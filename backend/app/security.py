import re
import time
from fastapi import HTTPException, status

MAX_LOGIN_ATTEMPTS = 5
WINDOW_SECONDS = 60

_login_attempts: dict[str, list[float]] = {}

BANNED_CODE_PATTERNS = ["import os", "import sys", "subprocess", "eval(", "exec(", "open(", "__"]


def validate_username(username: str) -> None:
    if not 3 <= len(username) <= 20:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid username or password")
    if not re.match(r"^[A-Za-z0-9_]+$", username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid username or password")


def validate_password_strength(password: str) -> None:
    if len(password) < 8:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid username or password")
    if not re.search(r"[a-z]", password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid username or password")
    if not re.search(r"[A-Z]", password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid username or password")
    if not re.search(r"\d", password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid username or password")
    if not re.search(r"[^A-Za-z0-9]", password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid username or password")


def rate_limit_login(ip: str) -> None:
    now = time.time()
    attempts = _login_attempts.get(ip, [])
    attempts = [ts for ts in attempts if now - ts < WINDOW_SECONDS]
    if len(attempts) >= MAX_LOGIN_ATTEMPTS:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                            detail="Invalid username or password")
    attempts.append(now)
    _login_attempts[ip] = attempts


def validate_action_code(code: str) -> None:
    for pattern in BANNED_CODE_PATTERNS:
        if pattern in code:
            raise ValueError("Insecure code detected")
