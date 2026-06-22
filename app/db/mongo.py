import mongomock.database
from beanie import init_beanie
from mongomock_motor import AsyncMongoMockClient
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings


async def init_mongo():
    """
    Initialize MongoDB connection and Beanie ODM.
    """
    if settings.use_mock_db:
        orig_list_collection_names = mongomock.database.Database.list_collection_names

        def patched_list_collection_names(self, *args, **kwargs):
            kwargs.pop("authorizedCollections", None)
            kwargs.pop("nameOnly", None)

            return orig_list_collection_names(self, *args, **kwargs)

        mongomock.database.Database.list_collection_names = (
            patched_list_collection_names
        )
        client = AsyncMongoMockClient()
    else:
        client = AsyncIOMotorClient(host=settings.mongodb_url)

    await init_beanie(
        database=client.get_database(name=settings.database_name),
        document_models=[],
    )
