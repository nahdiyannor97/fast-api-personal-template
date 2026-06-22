from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlmodel import SQLModel

from app.api.health_check import router as health_check_router
from app.core._logging import logger
from app.core.config import environment, settings
from app.core.limiter import limiter
from app.db.engine import engine
from app.db.mongo import init_mongo


@asynccontextmanager
async def lifespan(_: FastAPI):
    """
    Handle the lifespan events of the FastAPI application.
    """
    if settings.use_mock_db:
        logger.info("Using mock databases")
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        await init_mongo()
    else:
        logger.info("Using real databases")
        await init_mongo()
    yield


def configure_middlewares(app: FastAPI) -> None:
    """
    Configure CORS and other middlewares for the application.
    """
    if settings.environment == environment.DEVELOPMENT:
        app.add_middleware(
            middleware_class=CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )


def configure_documentation(app: FastAPI) -> None:
    """
    Configure static documentation (Swagger UI, ReDoc) for the application.
    """
    if settings.use_static_document:
        app.mount("/static", StaticFiles(directory="app/static"), name="static")

        @app.get("/docs", include_in_schema=False)
        async def custom_swagger_ui_html():
            """
            Serve the custom Swagger UI HTML.
            """
            return get_swagger_ui_html(
                openapi_url=app.openapi_url,
                title=f"{app.title} - Swagger UI",
                oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
                swagger_js_url="/static/swagger-ui-bundle.js",
                swagger_css_url="/static/swagger-ui.css",
                swagger_favicon_url="/static/favicon.png",
            )

        @app.get("/redoc", include_in_schema=False)
        async def redoc_html():
            """
            Serve the custom ReDoc HTML.
            """
            return get_redoc_html(
                openapi_url=app.openapi_url,
                title=f"{app.title} - ReDoc",
                redoc_js_url="/static/redoc.standalone.js",
                redoc_favicon_url="/static/favicon.png",
            )


def configure_rate_limit(app: FastAPI) -> None:
    """
    Configure the rate limiter for the application.
    """
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


def configure_routers(app: FastAPI) -> None:
    """
    Include all API routers in the application.
    """
    app.include_router(router=health_check_router)


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application instance.
    """
    app = FastAPI(
        title=settings.project_name,
        version=settings.project_version,
        lifespan=lifespan,
        docs_url=None if settings.use_static_document else "/docs",
        redoc_url=None if settings.use_static_document else "/redoc",
    )

    configure_rate_limit(app=app)
    configure_middlewares(app=app)
    configure_documentation(app=app)
    configure_routers(app=app)

    return app


create_app()
