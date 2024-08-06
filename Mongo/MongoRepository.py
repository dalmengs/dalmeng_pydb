import asyncio
import motor.motor_asyncio
from sqlalchemy.exc import DataError
from typing import Optional, Union

class MongoRepository:
    def __init__(self, username: str, password: str, table: str, host: str = "127.0.0.1", port: int = 27017, authentication_database: str = "admin"):
        self.__client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://{username}:{password}@{host}:{port}/?authSource={authSource}".format(
            username   = username,
            password   = password,
            host       = host,
            port       = port,
            authSource = authentication_database
        ))
        self.__table = self.__client[table]
    
    async def clear_collections(self, collection_names: Optional[Union[str | list]] = None):
        if not collection_names:
            collection_names = await self.__table.list_collection_names()
            for collection_name in collection_names:
                await self.__table[collection_name].delete_many({})
            return
        
        if isinstance(collection_names, str):
            collection_names = [collection_names]
        for collection_name in collection_names:
            await self.__table[collection_name].delete_many({})
    
    async def find(self, collection: str, filter: dict = {}, find_one=False):
        ret = []
        async for o in self.__table[collection].find(filter):
            if "_id" in o:
                del o["_id"]
                if "dalmeng_pydb_data_id" in o:
                    del o["dalmeng_pydb_data_id"]
                if find_one: return o
                ret.append(o)
        return None if find_one else ret

    async def upsert(self, collection: str, filter: dict, data: dict):
        result = await self.__table[collection].find_one(filter)
        if result:
            data["dalmeng_pydb_data_id"] = result["dalmeng_pydb_data_id"]
            await self.__table[collection].replace_one(
                filter={"dalmeng_pydb_data_id": result["dalmeng_pydb_data_id"]},
                replacement=data
            )
            if "_id" in data:
                del data["_id"]
            if "dalmeng_pydb_data_id" in data:
                del data["dalmeng_pydb_data_id"]
            return data
        return await self.insert(
            collection=collection,
            data=data,
            insert_one=True
        )
    
    async def update(self, collection: str, filter: dict, data: dict):
        result = await self.__table[collection].find_one(filter)
        if not result: raise DataError
        data["dalmeng_pydb_data_id"] = result["dalmeng_pydb_data_id"]
        await self.__table[collection].replace_one(
            filter={"dalmeng_pydb_data_id": result["dalmeng_pydb_data_id"]},
            replacement=data
        )
        if "_id" in data:
            del data["_id"]
        if "dalmeng_pydb_data_id" in data:
            del data["dalmeng_pydb_data_id"]
        return data
        

    async def insert(self, collection: str, data: dict | list[dict], insert_one=True):
        if insert_one:
            if not isinstance(data, dict):
                raise ValueError("To insert single data, data type must be dictionary.")
            data["dalmeng_pydb_data_id"] = random_id()
            await self.__table[collection].insert_one(data)
            inserted_data = data
        else:
            if not isinstance(data, list) or not all(isinstance(d, dict) for d in data):
                raise ValueError("To insert multiple data, data type must be list containing dictionary.")
            for d in data:
                d["dalmeng_pydb_data_id"] = random_id()
            await self.__table[collection].insert_many(data)
            inserted_data = data

        if inserted_data and isinstance(inserted_data, dict):
            if "_id" in inserted_data:
                del inserted_data["_id"]
            if "dalmeng_pydb_data_id" in inserted_data:
                del inserted_data["dalmeng_pydb_data_id"]
        elif isinstance(inserted_data, list):
            for d in inserted_data:
                if "_id" in d:
                    del d["_id"]
                if "dalmeng_pydb_data_id" in d:
                    del d["dalmeng_pydb_data_id"]
        return inserted_data

    async def delete(self, collection: str, filter: dict = {}):
        data = await self.find(collection, filter)
        await self.__table[collection].delete_many(filter)
        return data

import random
c = "1234567890qwertyuiopasdfghjklzxcvbnm"
def random_id():
    return ''.join(random.choices(c, k=50))