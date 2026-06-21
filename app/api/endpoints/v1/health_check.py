from fastapi import APIRouter, status, Request, Response
from app.core.interface import BaseResponse
from app.core.limiter import limiter
from app.core._logging import logger

router = APIRouter(prefix="/v1")


@router.get("/", response_model=BaseResponse[None], status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def health_check(request: Request, response: Response) -> BaseResponse[None]:
    logger.info("Health check endpoint hit")

    response.status_code = status.HTTP_200_OK
    return BaseResponse(message="Health check passed!", data=None)
