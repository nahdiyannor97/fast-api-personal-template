from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings

connect_args = {"check_same_thread": False} if "sqlite" in settings.database_url else {}
engine = create_async_engine(
    url=settings.database_url, connect_args=connect_args, echo=settings.database_echo
)
