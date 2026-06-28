from fastapi import APIRouter, Body, Request, Response, status

from app.core._logging import logger
from app.core.interface import AuthResponse, BaseResponse
from app.core.limiter import limiter
from app.services.auth import generate_token as generate_token_service

router = APIRouter(tags=["Auth"])


@router.post(
    path="/generate-token",
    response_model=BaseResponse[AuthResponse],
    status_code=status.HTTP_200_OK,
)
@limiter.limit(limit_value="10/minute")
async def generate_token(
    request: Request,
    response: Response,
    user_name: str = Body(...),
    password: str = Body(...),
) -> BaseResponse[AuthResponse]:
    """Generate a JWT access token for the given user credentials."""
    logger.info("Generate token endpoint hit")

    if not password or not password.strip():
        logger.warning("Generate token failed: password is empty")
        status_code = status.HTTP_400_BAD_REQUEST
        response.status_code = status_code
        return BaseResponse(
            message="Password is required",
            status_code=status_code,
            data=None,
        )

    token_data = generate_token_service(user_name=user_name, password=password)

    status_code = status.HTTP_200_OK
    response.status_code = status_code
    return BaseResponse(
        message="Token generated successfully!",
        status_code=status_code,
        data=token_data,
    )
