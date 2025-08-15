from abs_nosql_repository_core.repository.base_repository import BaseRepository
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.mongodb.integration import Integration


class IntegrationRepository(BaseRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection_name = "integrations"
        super().__init__(Integration, db)
