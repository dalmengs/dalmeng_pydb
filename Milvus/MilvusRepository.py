import asyncio
from sqlalchemy.exc import DataError
from typing import Optional, Union, List, Dict, Any
from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility
from Milvus.Embedder import Embedder

class MilvusRepository:
    def __init__(self, embedding_dimension: int, milvus_host: str = "127.0.0.1", milvus_port: int = 19530, metric_type: str = "COSINE", index_type: str = "IVF_FLAT", limit: int = 3, embedding_server_host: str = "127.0.0.1", embedding_server_port: int = 7777):
        connections.connect(host=milvus_host, port=milvus_port)
        self.__param = {
            'metric_type': metric_type,
            'index_type': index_type,
            'params': {
                "nlist": int(embedding_dimension)
            }
        }
        self.__limit = int(limit)
        self.__embedding_dimension = int(embedding_dimension)
        self.__metric_type = metric_type
        self.__collections = {}
        self.__collections_metadata = {}
        self.__embedder: Embedder = Embedder(
            embedding_ip=embedding_server_host,
            embedding_port=embedding_server_port
        )

    def add_collection(self, collection_name: str, collection_fields: List[Dict[str, Any]], indexes: List[Dict[str, str]]):
        vector_field_name = None

        self.__collections_metadata[collection_name] = {
            "vector_field": None,
            "fields": []
        }

        fields = [FieldSchema(name="dalmeng_pydb_data_id", dtype=DataType.VARCHAR, is_primary=True, max_length=64)]
        for field in collection_fields:
            if field["type"] == "string":
                fields.append(
                    FieldSchema(name=field["name"], dtype=DataType.VARCHAR, max_length=field["max_length"])
                )
                self.__collections_metadata[collection_name]["fields"].append(field["name"])
            elif field["type"] == "vector":
                fields.append(
                    FieldSchema(name=field["name"], dtype=DataType.FLOAT_VECTOR, dim=self.__embedding_dimension)
                )
                vector_field_name = field["name"]
                self.__collections_metadata[collection_name]["vector_field"] = field["name"]

        if not vector_field_name:
            raise ValueError("Vector Field must exist.")

        collection = Collection(
            name=collection_name,
            schema=CollectionSchema(
                fields=fields
            ),
        )

        if collection_name not in self.__collections:
            self.__collections[collection_name] = collection
        
        for index in indexes:
            index_params = {"index_type": index["index_type"]}
            if index["name"] == vector_field_name:
                index_params["metric_type"] = self.__metric_type
                vector_field_name = None
            
            self.__collections[collection_name].create_index(
                field_name=index["name"],
                index_params=index_params
            )

        if vector_field_name:
            self.__collections[collection_name].create_index(
                field_name=vector_field_name,
                index_params=self.__param
            )
        self.__collections[collection_name].load()

    async def clear_collections(self, collection_names: Optional[Union[str | list]] = None):
        if not collection_names:
            collection_names = utility.list_collections()
            for collection_name in collection_names:
                utility.drop_collection(collection_name)
            return
        
        if isinstance(collection_names, str):
            collection_names = [collection_names]
        for collection_name in collection_names:
            if utility.has_collection(collection_name): utility.drop_collection(collection_name)
    
    async def retrieval(self, collection: str, text: str, filter: str = "dalmeng_pydb_data_id != ''", limit: int = None):
        embedded_vector = await self.__embedder.encode(message=text)
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self.__retrieval, collection, embedded_vector, filter, limit
        )

    def __retrieval(self, collection: str, embedded_vector, filter: str, limit: int):
        limit = limit if limit else self.__limit
        retrieval_result = self.__collections[collection].search(
            data=[embedded_vector],
            anns_field=self.__collections_metadata[collection]["vector_field"],
            param=self.__param,
            limit=limit,
            output_fields=self.__collections_metadata[collection]["fields"],
            expr=filter
        )

        result = []
        for hits in retrieval_result:
            for hit in hits:
                result.append(hit.to_dict()["entity"])
        
        return result

    async def find(self, collection: str, filter: str = "dalmeng_pydb_data_id != ''", find_one=False):
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, self.__find, collection, filter
        )
        
        if find_one:
            if not len(result): 
                return None
            if "dalmeng_pydb_data_id" in result[0]:
                del result[0]["dalmeng_pydb_data_id"]
            return result[0]
        
        ret = []
        for i in result:
            if "dalmeng_pydb_data_id" in i:
                del i["dalmeng_pydb_data_id"]
            ret.append(i)
        
        return ret

    def __find(self, collection: str, filter: str):
        result = self.__collections[collection].query(
            expr=filter, 
            output_fields=self.__collections_metadata[collection]["fields"]
        )
        return result

    async def insert(self, collection: str, text: str | list, data: list | dict, insert_one=True):
        if insert_one:
            if not isinstance(data, dict):
                raise ValueError("To insert single data, data type must be dictionary.")
            if not isinstance(text, str):
                raise ValueError("To insert single data, text type must be string.")
            
            embedded_vector = await self.__embedder.encode(text)
            data["dalmeng_pydb_data_id"] = random_id()
            data[self.__collections_metadata[collection]["vector_field"]] = embedded_vector
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self.__insert, collection, data)
            
            if "dalmeng_pydb_data_id" in data:
                del data["dalmeng_pydb_data_id"]
            if self.__collections_metadata[collection]["vector_field"] in data:
                del data[self.__collections_metadata[collection]["vector_field"]]
            return data
        
        if not isinstance(data, list) or not all(isinstance(d, dict) for d in data):
            raise ValueError("To insert multiple data, data type must be list containing dictionary.")
        if not isinstance(text, list) or not all(isinstance(d, str) for d in text) or len(data) != len(text):
            raise ValueError("To insert multiple data, text type must be list containing string, and its length must be equal to data list.")
        
        embedded_vectors = await self.__embedder.encode(text)

        for i in range(len(embedded_vectors)):
            data[i]["dalmeng_pydb_data_id"] = random_id()
            data[i][self.__collections_metadata[collection]["vector_field"]] = embedded_vectors[i]

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.__insert, collection, data)

        for i in range(len(embedded_vectors)):
            if "dalmeng_pydb_data_id" in data[i]:
                del data[i]["dalmeng_pydb_data_id"]
            if self.__collections_metadata[collection]["vector_field"] in data[i]:
                del data[i][self.__collections_metadata[collection]["vector_field"]]

        return data

    def __insert(self, collection: str, data: dict | list):
        self.__collections[collection].insert(data)
        self.__collections[collection].flush()

    async def delete(self, collection: str, filter: str = "dalmeng_pydb_data_id != ''"):
        result = await self.find(collection=collection, filter=filter)
        
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.__delete, collection, filter)
        
        return result

    def __delete(self, collection: str, filter: str):
        self.__collections[collection].delete(expr=filter)

import random
c = "1234567890qwertyuiopasdfghjklzxcvbnm"
def random_id():
    return ''.join(random.choices(c, k=50))