import sys
import os
import functools
import asyncio
import inspect
from colorama import Fore, init

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Milvus.MilvusRepository import MilvusRepository
from Milvus.MilvusField import *
from Milvus.MilvusIndex import *

# colorama 초기화
init(autoreset=True)
test_result = []

def Test(description):
    global test_result
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Before test execution
            print(Fore.YELLOW + "=" * 50)
            print(Fore.YELLOW + "[Test Information]")
            print(Fore.YELLOW + "Test Start: " + description)
            print(Fore.YELLOW + "Function Name: " + func.__name__ + "\n")

            # Execute the test function
            result = await func(*args, **kwargs)

            # After test execution
            print(Fore.YELLOW + "[Test Results]")
            print(Fore.YELLOW + "Expected Result:", result["expected"])
            print(Fore.YELLOW + "Actual Result  :", result["actual"])
            r = result["expected"] == result["actual"]

            test_result.append({
                "test_name": description,
                "test_result": r
            })

            print(Fore.YELLOW + "Final Result   : " + (Fore.GREEN + "Succeed" if r else Fore.RED + "Failed"))
            print(Fore.YELLOW + "=" * 50)

            return result

        return wrapper
    return decorator

class MilvusTest:
    milvus_repository = MilvusRepository(
        embedding_dimension=768
    )

    async def clear_database(self):
        await self.milvus_repository.clear_collections("test_collection")
    
    async def do_test(self):
        global test_result

        await self.clear_database()

        self.milvus_repository.add_collection(
            collection_name="test_collection",
            collection_fields=[
                StringField("user_id"),
                StringField("group_id"),
                VectorField("embedding")
            ],
            indexes=[
                Index("user_id"),
                Index("group_id")
            ]
        )

        tests = [
            self.test_1(),
            self.test_2(),
            self.test_3(),
            self.test_4(),
            self.test_5(),
            self.test_6(),
            self.test_7(),
            self.test_8(),
            self.test_9(),
            self.test_10(),
        ]
        for test in tests:
            await test
        
        print(Fore.YELLOW + "=" * 50)
        print(Fore.YELLOW + "[Test Summary]")
        cnt, s = 1, 0
        for test in test_result:
            print(Fore.YELLOW + f"[Test {cnt}] " + test["test_name"] + " -> " + (Fore.GREEN + "Succeed" if test["test_result"] else Fore.RED + "Failed"))
            cnt += 1
            if test["test_result"]:
                s += 1
        cnt -= 1
        print(Fore.YELLOW + "=" * 50)
        print(Fore.BLUE + f"{s} Tests Succeed over Total {cnt} Tests.\n")
        
    @Test("Test #1. Insert Single Data")
    async def test_1(self):
        result = await self.milvus_repository.insert(
            collection="test_collection",
            text="This is test data",
            data={
                "user_id": "dalmeng",
                "group_id": "dalmeng"
            },
            insert_one=True
        )
        return {
            "expected": {"user_id": "dalmeng", "group_id": "dalmeng"},
            "actual": result
        }
    
    @Test("Test #2. Insert Single Data with List")
    async def test_2(self):
        try:
            result = await self.milvus_repository.insert(
                collection="test_collection",
                text="Milvus Repository",
                data=[{
                    "user_id": "dalmeng",
                    "group_id": "dalmeng"
                }],
                insert_one=True
            )
        except Exception:
            return {
                "expected": Exception,
                "actual": Exception
            }
    
    @Test("Test #3. Insert Multiple Data")
    async def test_3(self):
        result = await self.milvus_repository.insert(
            collection="test_collection",
            text=["My name is Dalmeng.", "I am developer."],
            data=[
                {
                    "user_id": "dalmengs",
                    "group_id": "dalmeng"
                },
                {
                    "user_id": "dalmengs",
                    "group_id": "dalmeng"
                },
            ],
            insert_one=False
        )
        return {
            "expected": [
                {
                    "user_id": "dalmengs",
                    "group_id": "dalmeng"
                },
                {
                    "user_id": "dalmengs",
                    "group_id": "dalmeng"
                },
            ],
            "actual": result
        }
    
    @Test("Test #4. Insert Multiple Data with Dictionary")
    async def test_4(self):
        try:
            result = await self.milvus_repository.insert(
                collection="test_collection",
                text="Test Data",
                data={
                    "user_id": "dalmeng",
                    "group_id": "dalmeng"
                },
                insert_one=False
            )
        except Exception:
            return {
                "expected": Exception,
                "actual": Exception
            }
    
    @Test("Test #5. Find All Data")
    async def test_5(self):
        result = await self.milvus_repository.find(
            collection="test_collection"
        )
        return {
            "expected": sorted(
                [
                    {
                        "user_id": "dalmeng",
                        "group_id": "dalmeng"
                    },
                    {
                        "user_id": "dalmengs",
                        "group_id": "dalmeng"
                    },
                    {
                        "user_id": "dalmengs",
                        "group_id": "dalmeng"
                    },
                ]
            , key=lambda x: (x["user_id"], x["group_id"])),
            "actual": sorted(result, key=lambda x: (x["user_id"], x["group_id"]))
        }
    
    @Test("Test #6. Find Data using Filter")
    async def test_6(self):
        result = await self.milvus_repository.find(
            collection="test_collection",
            filter="user_id == 'dalmengs'"
        )
        return {
            "expected": sorted(
                [
                    {
                        "user_id": "dalmengs",
                        "group_id": "dalmeng"
                    },
                    {
                        "user_id": "dalmengs",
                        "group_id": "dalmeng"
                    },
                ]
            , key=lambda x: (x["user_id"], x["group_id"])),
            "actual": sorted(result, key=lambda x: (x["user_id"], x["group_id"]))
        }
    
    @Test("Test #7. Find Single Data using Filter")
    async def test_7(self):
        result = await self.milvus_repository.find(
            collection="test_collection",
            filter="user_id == 'dalmeng'",
            find_one=True
        )
        return {
            "expected": {
                "user_id": "dalmeng",
                "group_id": "dalmeng"
            },
            "actual": result
        }
    
    @Test("Test #8. Delete Data using Filter")
    async def test_8(self):
        result = await self.milvus_repository.delete(
            collection="test_collection",
            filter="user_id == 'dalmeng'"
        )
        return {
            "expected": [{
                "user_id": "dalmeng",
                "group_id": "dalmeng"
            }],
            "actual": result
        }
    
    @Test("Test #9. Retrieval Data")
    async def test_9(self):
        await self.milvus_repository.insert(
            collection="test_collection",
            text=["AWS", "Solutions", "Architect", "DevOps"],
            data=[
                {
                    "user_id": "testdata",
                    "group_id": "dalmeng"
                },
                {
                    "user_id": "testuser",
                    "group_id": "dalmeng"
                },
                {
                    "user_id": "testdalmeng",
                    "group_id": "dalmengs"
                },
                {
                    "user_id": "testdalmenguser",
                    "group_id": "dalmengs"
                }
            ],
            insert_one=False
        )
        result = await self.milvus_repository.retrieval(
            collection="test_collection",
            text="This is test retrieval sentence.",
            limit=3
        )
        print(result, end="\n\n")
        return {
            "expected": "Length : 3",
            "actual": "Length : {}".format(len(result))
        }
    
    @Test("Test #10. Retrieval Data using Filter")
    async def test_10(self):
        result = await self.milvus_repository.retrieval(
            collection="test_collection",
            text="This is test retrieval sentence.",
            filter="group_id == 'dalmeng'",
            limit=2
        )
        print(result, end="\n\n")
        return {
            "expected": "Length : 2",
            "actual": "Length : {}".format(len(result))
        }
    
async def main():
    t = MilvusTest()
    await t.do_test()

asyncio.run(main())