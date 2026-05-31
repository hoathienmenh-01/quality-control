"""JWT authentication utilities."""

from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import bcrypt
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.dependencies import get_db
from config import settings
from models.user import User

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# ── Pydantic schemas ──────────────────────────────────────────────────────────

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: int | None = None
    email: str | None = None
    role: str | None = None


class LoginRequest(BaseModel):
    """Schema cho login — chỉ cần email + password."""
    email: str
    password: str


class UserCreate(BaseModel):
    email: str
    name: str
    password: str
    role: str = "operator"


class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    role: str

    model_config = {"from_attributes": True}


# ── Helpers ───────────────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    """Hash password using bcrypt directly (avoids passlib warning on Python 3.12+)"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(plain: str, hashed: str) -> bool:
    """Verify password against bcrypt hash"""
    return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ── Dependencies ──────────────────────────────────────────────────────────────

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Decode JWT and return the authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int | None = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    return user


def require_role(*roles: str):
    """Dependency factory: require the current user to have one of the given roles."""

    def _check(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{current_user.role}' not in {roles}",
            )
        return current_user

    return _check
