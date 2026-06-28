from datetime import datetime, timedelta, timezone

from jose import jwt

from app.core.config import settings


def generate_token(user_name: str, password: str) -> dict:
    """Generate a JWT access token for the given user credentials."""
    expire = datetime.now(tz=timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    payload = {
        "sub": user_name,
        "iat": datetime.now(tz=timezone.utc),
        "exp": expire,
    }
    access_token = jwt.encode(
        claims=payload,
        key=settings.secret_key,
        algorithm=settings.algorithm,
    )
    return {"access_token": access_token, "token_type": "bearer"}
