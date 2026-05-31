"""Auth router — login, register, current user."""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from api.auth import (
    LoginRequest,
    Token,
    UserCreate,
    UserResponse,
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
    require_role,
)
from api.dependencies import get_db
from core.security import (
    PasswordValidationError,
    get_client_ip,
    log_audit,
    rate_limiter,
    validate_password,
)
from models.user import User

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Rate limit settings cho login
LOGIN_MAX_ATTEMPTS = 5
LOGIN_WINDOW_SECONDS = 300  # 5 phút


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    payload: UserCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),  # Chỉ admin mới tạo user
):
    """Register a new user. CHỈ ADMIN mới có quyền tạo tài khoản."""
    # Validate password strength
    try:
        validate_password(payload.password)
    except PasswordValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=payload.email,
        name=payload.name,
        password_hash=hash_password(payload.password),
        role=payload.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    log_audit(
        "create_user",
        user_id=current_user.id,
        user_email=current_user.email,
        details={"new_user_email": payload.email, "role": payload.role},
        ip_address=get_client_ip(request),
    )

    return user


@router.post("/login", response_model=Token)
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)):
    """Authenticate and return a JWT token. Có rate limiting chống brute force."""
    client_ip = get_client_ip(request)
    rate_key = f"login:{client_ip}"

    # Kiểm tra rate limit
    if rate_limiter.is_rate_limited(rate_key, LOGIN_MAX_ATTEMPTS, LOGIN_WINDOW_SECONDS):
        log_audit(
            "login_rate_limited",
            details={"email": payload.email, "ip": client_ip},
            ip_address=client_ip,
            success=False,
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Quá nhiều lần thử đăng nhập. Thử lại sau {LOGIN_WINDOW_SECONDS // 60} phút.",
        )

    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        # Ghi nhận lần thử thất bại
        rate_limiter.record_attempt(rate_key)
        remaining = rate_limiter.get_remaining_attempts(rate_key, LOGIN_MAX_ATTEMPTS, LOGIN_WINDOW_SECONDS)

        log_audit(
            "login_failed",
            details={"email": payload.email, "ip": client_ip, "remaining_attempts": remaining},
            ip_address=client_ip,
            success=False,
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sai email hoặc mật khẩu",
        )

    # Đăng nhập thành công → reset rate limit
    rate_limiter.reset(rate_key)

    token = create_access_token({"sub": str(user.id), "email": user.email, "role": user.role})

    log_audit(
        "login_success",
        user_id=user.id,
        user_email=user.email,
        details={"ip": client_ip},
        ip_address=client_ip,
    )

    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Return the authenticated user's profile."""
    return current_user
