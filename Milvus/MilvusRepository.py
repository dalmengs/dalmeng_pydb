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
    
    async def retrieval(self, collection: str, text: str, filter: str = None, limit: int = None):
        embedded_vector = self.__embedder.encode(message=text)

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
                result.append(hit.entity)
        
        return result

    async def find(self, collection: str, filter: str, find_one=False):
        result = self.__collections[collection].query(
            expr = filter, 
            output_fields = self.__collections_metadata[collection]["fields"]
        )
        if find_one: return result[0] if len(result) else None
        return [o for o in result]

    async def insert(self, collection: str, text: str | list, data: list | dict, insert_one=True):
        if insert_one:
            if not isinstance(data, dict):
                raise ValueError("To insert single data, data type must be dictionary.")
            if not isinstance(text, str):
                raise ValueError("To insert single data, text type must be string.")
            
            embedded_vector = await Embedder.encode(text)

            data["dalmeng_pydb_data_id"] = random_id()
            data[self.__collections_metadata[collection]["vector_field"]] = embedded_vector

            self.__collections[collection].insert(data)
            self.__collections[collection].flush()

            if "dalmeng_pydb_data_id" in data:
                del data["dalmeng_pydb_data_id"]
            if self.__collections_metadata[collection]["vector_field"] in data:
                del data[self.__collections_metadata[collection]["vector_field"]]
            return data
        
        if not isinstance(data, list) or not all(isinstance(d, dict) for d in data):
            raise ValueError("To insert multiple data, data type must be list containing dictionary.")
        if not isinstance(text, list) or not all(isinstance(d, str) for d in text) or len(data) != len(text):
            raise ValueError("To insert multiple data, text type must be list containing string, and its length must be equal to data list.")
        
        embedded_vectors = await Embedder.encode(text)

        for i in range(len(embedded_vectors)):
            data[i]["dalmeng_pydb_data_id"] = random_id()
            data[i][self.__collections_metadata[collection]["vector_field"]] = embedded_vectors[i]

        self.__collections[collection].insert(data)
        self.__collections[collection].flush()

        for i in range(len(embedded_vectors)):
            if "dalmeng_pydb_data_id" in data[i]:
                del data[i]["dalmeng_pydb_data_id"]
            if self.__collections_metadata[collection]["vector_field"] in data[i]:
                del data[i][self.__collections_metadata[collection]["vector_field"]]

        return data

    async def delete(self, collection: str, filter: dict = {}):
        self.__collections[collection].delete(
            expr=filter
        )

import random
c = "1234567890qwertyuiopasdfghjklzxcvbnm"
def random_id():
    return ''.join(random.choices(c, k=50))