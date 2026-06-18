from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response

from app.core._logging import logger


class ExceptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response | JSONResponse:
        """
        This middleware will catch any exceptions that occur in the application
        and return a JSON response with the error message.
        """
        try:
            return await call_next(request)
        except Exception as e:
            logger.error("An internal server error occurred", error=str(object=e))

            return JSONResponse(
                status_code=500,
                content={
                    "message": "An internal server error occurred.",
                },
            )
