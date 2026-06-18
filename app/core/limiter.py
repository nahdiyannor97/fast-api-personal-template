from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings


def get_rate_limit_key(request: Request) -> str:
    """
    Get the client IP address from the request to use as a rate limit key.
    """
    client_ip = get_remote_address(request=request)
    return client_ip


limiter = Limiter(
    key_func=get_rate_limit_key,
    default_limits=[
        f"{settings.rate_limit_per_minute}/minute",
        f"{settings.rate_limit_hour}/hour",
        f"{settings.rate_limit_seconds}/second",
    ],
    strategy=settings.rate_limit_strategy,
)
