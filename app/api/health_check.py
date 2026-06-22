from fastapi import APIRouter, Request, Response, status

from app.core._logging import logger
from app.core.interface import BaseResponse
from app.core.limiter import limiter

router = APIRouter(tags=["Health Check"])


@router.get("/", response_model=BaseResponse[None], status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def health_check(request: Request, response: Response) -> BaseResponse[None]:
    logger.info("Health check endpoint hit")

    status_code = status.HTTP_200_OK
    response.status_code = status_code
    return BaseResponse(
        message="Health check passed!", status_code=status_code, data=None
    )
