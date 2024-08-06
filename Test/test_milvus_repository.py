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
    milvus_repository.add_collection(
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

    async def clear_database(self):
        await self.milvus_repository.clear_collections("test_collection")
    
    async def do_test(self):
        global test_result

        await self.clear_database()

        tests = [

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
        
    @Test("Test #1. ...")
    async def test_1(self):
        pass
    
async def main():
    t = MilvusTest()
    await t.do_test()

asyncio.run(main())