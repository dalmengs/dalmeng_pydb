
#! How to Use Milvus Repository
#! ================================================================================

#& Imports
from Milvus.MilvusRepository import MilvusRepository
from Milvus.MilvusField import *
from Milvus.MilvusIndex import *

#& Repository Instance
milvus_repository: MilvusRepository = MilvusRepository(
    embedding_dimension=756,           # Required
    milvus_host="127.0.0.1",           # Optional (Default="127.0.0.1")
    milvus_port=19530,                 # Optional (Default=19530)
    metric_type="COSINE",              # Optional (Default="COSINE")
    index_type="IVF_FLAT",             # Optional (Default="IVF_FLAT")
    limit=3,                           # Optional (Default=3)
    embedding_server_host="127.0.0.1", # Optional (Default="127.0.0.1")
    embedding_server_port=7777         # Optional (Default=7777)
)

#& Delete Collection
milvus_repository.clear_collections()                   # Delete All Collections
milvus_repository.clear_collections("test_collection")  # Delete Collection with Name
milvus_repository.clear_collections(["test1", "test2"]) # Delete Collection with Collection Name List

#& Collection Field
"""
    <StringField> - String Type Field
    name        [string, required]
    max_length  [integer, optional(default=256)]
"""
StringField("user_id")
StringField(name="user_id", max_length=256)
StringField("user_id", 256)

"""
    <VectorField> - Float Vector Field
    name        [string, required]
"""
VectorField("embedding")
VectorField(name="embedding")

#& Collection Index
"""
    <Index> - Collection Index
    name        [string, required]
    index_type  [string, optional(default="Trie")]
"""
Index("user_id")
Index(name="user_id", index_type="Trie")
Index("user_id", "Trie")

#& Add Collection
milvus_repository.add_collection(
    collection_name="test_collection", # Collection Name
    collection_fields=[                # Collection Field (must contain one vector field)
        StringField(name="user_id", max_length=256),
        StringField("group_id"),
        VectorField("embedding")
    ],
    indexes=[                         # Indexes
        Index(name="user_id", index_type="Trie"),
        Index("group_id")
    ]
)

#& Retrieval Function
async def retrieval():
    """
        #* [Request]
        collection        Collection Name                  [string, required]
        text              Similarity Search Sentence       [string, optional(default="Trie")]
        filter            Condition Filter                 [string, optional(default=None)]
        limit             Retrieval Limit                  [integer, optional(default=3)]

        #* [Response]
        Return type is list[dict].
    """
    result = await milvus_repository.retrieval(
        collection="test_collection",
        text="This is Test Retrieval Sentence.",
        filter="user_id == 'dalmeng'",
        limit=3
    )

#& Find Function
async def find():
    """
        #* [Request]
        collection        Collection Name                  [string, required]
        filter            Condition Filter                 [string, optional(default=None)]
        find_one          Retrieval Type                   [boolean, optional(default=False)]

        #* [Response]
        if `find_one` is True,  return type is dict.
        if `find_one` is False, return type is list[dict].
    """
    result = await milvus_repository.find(
        collection="test_collection",
        filter="user_id == 'dalmeng'",
        find_one=True
    )

#& Insert Function
async def insert():
    """
        #* [Request]
        collection        Collection Name             [string, required]
        text              Embedding Sentences         [string | list[string], required]
        data              Corresponding Data          [dict   | list[dict],   required]
        insert_one        Insert Type                 [boolean, optional(default=True)]

        * If type of `text` is string, type of `data` must be dict.
        * If type of `text` is list[string], type of `data` must be list[string] whose length is equal to length of `text`

        #* [Response]
        if `insert_one` is True,  return type is dict.
        if `insert_one` is False, return type is list[dict].
    """
    #^ If `insert_one` is True,
    result = await milvus_repository.insert(
        collection="test_collection",
        text="I like soccer.",
        data={ "user_id": 'dalmeng' },
        insert_one=True
    )
    #^ If `insert_one` is False,
    result = await milvus_repository.insert(
        collection="test_collection",
        text=["I like soccer.", "I love pizza."],
        data=[
            { "user_id": 'dalmeng' },
            { "user_id": 'dalmeng' },
        ],
        insert_one=False
    )

#& Delete Function
async def insert():
    """
        #* [Request]
        collection        Collection Name             [string, required]
        filter            Condition Filter            [string, optional(default=None)]

        #* [Response]
        Return type is list.
    """
    result = await milvus_repository.delete(
        collection="test_collection",
        filter="user_id == 'dalmeng'"
    )

#! ================================================================================


#! How to Use Mongo Repository
#! ================================================================================
    
#& Imports
from Mongo.MongoRepository import MongoRepository

#& Repository Instance
mongo_repository: MongoRepository = MongoRepository(
    username="testuser",                # Required
    password="1234",                    # Required
    table="test_table",                 # Required
    host="127.0.0.1",                   # Optional (Default="127.0.0.1")
    port=27017,                         # Optional (Default=27017)
    authentication_database="admin"     # Optional (Default="admin")
)

#& Delete Collection
mongo_repository.clear_collections()                   # Delete All Collections
mongo_repository.clear_collections("test_collection")  # Delete Collection with Name
mongo_repository.clear_collections(["test1", "test2"]) # Delete Collection with Collection Name List

#& Find Function
async def find():
    """
        #* [Request]
        collection        Collection Name             [string, required]
        filter            Condition Filter            [dict, optional(default={})]
        find_one          Find Type                   [boolean, optional(default=False)]

        #* [Response]
        if `find_one` is True,  return type is dict.
        if `find_one` is False, return type is list[dict].
    """
    result = await mongo_repository.find(
        collection="test_collection",
        filter={"username": "dalmeng"},
        find_one=True
    )
    
#& Update / Insert Function
async def upsert():
    """
        #* [Request]
        collection        Collection Name             [string, required]
        filter            Condition Filter            [dict, required]
        data              Upsert Data                 [dict, required]

        #* [Response]
        Return type is dict.
    """
    result = await mongo_repository.upsert(
        collection="test_collection",
        filter={"username": "dalmeng"},
        data={"username": "dalmengs"}
    )

#& Update Function
async def update():
    """
        #* [Request]
        collection        Collection Name             [string, required]
        filter            Condition Filter            [dict, required]
        data              Update Data                 [dict, required]

        #* [Response]
        Return type is dict.
    """
    result = await mongo_repository.update(
        collection="test_collection",
        filter={"username": "dalmeng"},
        data={"username": "dalmengs"}
    )

#& Insert Function
async def insert():
    """
        #* [Request]
        collection        Collection Name             [string, required]
        data              Update Data                 [dict, required]
        insert_one        Insert Type                 [boolean, optional(default=True)]

        #* [Response]
        if `insert_one` is True,  return type is dict.
        if `insert_one` is False, return type is list[dict].
    """
    #^ If `insert_one` is True,
    result = await mongo_repository.insert(
        collection="test_collection",
        data=[{"username": "dalmeng"}, {"username": "dalmenglee"}],
        insert_one=True
    )
    #^ If `insert_one` is False,
    result = await mongo_repository.insert(
        collection="test_collection",
        data={"username": "dalmeng"},
        insert_one=False
    )

#& Delete Function
async def delete():
    """
        #* [Request]
        collection        Collection Name             [string, required]
        filter            Condition Filter            [dict, optional(default={})]

        #* [Response]
        Return type is list[dict].
    """
    result = await mongo_repository.delete(
        collection="test_collection",
        filter={"username": "dalmeng"}
    )
    