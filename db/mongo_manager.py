from motor.motor_asyncio import AsyncIOMotorClient

from config import MongoConfig


class AsyncMongoManager:

    def __init__(self, config: MongoConfig) -> None:
        self.client = AsyncIOMotorClient(config.url)
        self.db = self.client[config.db]
        self.collection = self.db[config.collection]

    async def close(self):
        if self.client:
            self.client.close()

    async def aggregate(self, pipeline) -> list:
        data = await self.collection.aggregate(pipeline).to_list(length=None)
        await self.close()
        return data

    # Add find option for extra case
    async def find(self, query):
        data = await self.collection.find(query).to_list(length=None)
        await self.close()
        return data
