import os
from typing import Any, Dict, List, Optional

from pydantic import BaseModel
from pydantic_settings import BaseSettings
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase


class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "appdb")


settings = Settings()
_client: Optional[AsyncIOMotorClient] = None
_db: Optional[AsyncIOMotorDatabase] = None


def get_db() -> Optional[AsyncIOMotorDatabase]:
    global _client, _db
    if _db is not None:
        return _db
    if not settings.DATABASE_URL:
        return None
    _client = AsyncIOMotorClient(settings.DATABASE_URL)
    _db = _client[settings.DATABASE_NAME]
    return _db


async def create_document(collection_name: str, data: Dict[str, Any]) -> Any:
    db = get_db()
    if db is None:
        return None
    doc = {**data}
    res = await db[collection_name].insert_one(doc)
    return res.inserted_id


async def get_documents(collection_name: str, filter_dict: Optional[Dict[str, Any]] = None, limit: int = 50) -> List[Dict[str, Any]]:
    db = get_db()
    if db is None:
        return []
    cursor = db[collection_name].find(filter_dict or {}).limit(limit)
    return [doc async for doc in cursor]
