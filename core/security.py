"""Security utilities — Rate limiting, password validation, audit logging."""

import hashlib
import logging
import re
import time
from collections import defaultdict
from datetime import datetime, timezone
from functools import wraps
from typing import Any

from fastapi import HTTPException, Request, status

logger = logging.getLogger("security")
audit_logger = logging.getLogger("audit")

# ── Rate Limiting (in-memory, per-IP) ────────────────────────────────────────

class RateLimiter:
    """Simple in-memory rate limiter theo IP."""

    def __init__(self):
        self._attempts: dict[str, list[float]] = defaultdict(list)

    def is_rate_limited(self, key: str, max_attempts: int = 5, window_seconds: int = 300) -> bool:
        """Kiểm tra có bị rate limit không.

        Args:
            key: Rate limit key (thường là IP address)
            max_attempts: Số lần thử tối đa trong window
            window_seconds: Kích thước cửa sổ thời gian (giây)

        Returns:
            True nếu bị rate limited
        """
        now = time.time()
        # Xóa các attempts cũ
        self._attempts[key] = [
            t for t in self._attempts[key] if now - t < window_seconds
        ]
        return len(self._attempts[key]) >= max_attempts

    def record_attempt(self, key: str):
        """Ghi nhận 1 lần thử."""
        self._attempts[key].append(time.time())

    def get_remaining_attempts(self, key: str, max_attempts: int = 5, window_seconds: int = 300) -> int:
        """Số lần thử còn lại."""
        now = time.time()
        self._attempts[key] = [
            t for t in self._attempts[key] if now - t < window_seconds
        ]
        return max(0, max_attempts - len(self._attempts[key]))

    def reset(self, key: str):
        """Reset attempts cho 1 key."""
        self._attempts.pop(key, None)


# Singleton
rate_limiter = RateLimiter()


# ── Password Validation ──────────────────────────────────────────────────────

class PasswordValidationError(Exception):
    pass


def validate_password(password: str) -> str:
    """Validate password strength. Trả về password nếu hợp lệ, raise nếu không.

    Rules:
    - Tối thiểu 8 ký tự
    - Ít nhất 1 chữ hoa
    - Ít nhất 1 chữ thường
    - Ít nhất 1 chữ số
    - Ít nhất 1 ký tự đặc biệt (!@#$%^&*()_+-=)
    """
    errors = []

    if len(password) < 8:
        errors.append("Mật khẩu phải có ít nhất 8 ký tự")
    if not re.search(r'[A-Z]', password):
        errors.append("Mật khẩu phải có ít nhất 1 chữ hoa")
    if not re.search(r'[a-z]', password):
        errors.append("Mật khẩu phải có ít nhất 1 chữ thường")
    if not re.search(r'\d', password):
        errors.append("Mật khẩu phải có ít nhất 1 chữ số")
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password):
        errors.append("Mật khẩu phải có ít nhất 1 ký tự đặc biệt")

    if errors:
        raise PasswordValidationError("; ".join(errors))

    return password


# ── Audit Logging ────────────────────────────────────────────────────────────

def log_audit(
    action: str,
    user_id: int | str | None = None,
    user_email: str | None = None,
    details: dict[str, Any] | None = None,
    ip_address: str | None = None,
    success: bool = True,
):
    """Ghi audit log cho hành động quan trọng.

    Args:
        action: Tên hành động (login, create_inspection, resolve_alert, ...)
        user_id: ID người thực hiện
        user_email: Email người thực hiện
        details: Chi tiết bổ sung
        ip_address: IP address
        success: Hành động có thành công không
    """
    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "user_id": user_id,
        "user_email": user_email,
        "ip_address": ip_address,
        "success": success,
        "details": details or {},
    }

    if success:
        audit_logger.info("AUDIT: %s", log_entry)
    else:
        audit_logger.warning("AUDIT_FAIL: %s", log_entry)


def get_client_ip(request: Request) -> str:
    """Lấy IP client từ request, hỗ trợ reverse proxy."""
    # Kiểm tra X-Forwarded-For header (reverse proxy)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    # Kiểm tra X-Real-IP header
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()
    # Fallback to direct connection
    return request.client.host if request.client else "unknown"


# ── Input Sanitization ───────────────────────────────────────────────────────

def sanitize_string(value: str, max_length: int = 500) -> str:
    """Sanitize string input — strip, limit length, remove control chars."""
    if not value:
        return value
    # Strip whitespace
    value = value.strip()
    # Remove control characters (except newline/tab)
    value = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', value)
    # Limit length
    if len(value) > max_length:
        value = value[:max_length]
    return value


def validate_serial_number(serial: str) -> bool:
    """Validate serial number format — chỉ cho phép alphanumeric + dash/underscore."""
    return bool(re.match(r'^[A-Za-z0-9\-_]{1,100}$', serial))


def validate_station_id(station_id: str) -> bool:
    """Validate station ID format."""
    return bool(re.match(r'^[A-Za-z0-9\-_]{1,50}$', station_id))
