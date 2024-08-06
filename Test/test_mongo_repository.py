import sys
import os
import functools
import asyncio
import inspect
from colorama import Fore, init

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Mongo.MongoRepository import MongoRepository

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

class MongoTest:
    mongo_repository = MongoRepository(
        username="test_username",
        password="test_password",
        table="test_table"
    )
    collection_name = "test_collection"

    async def clear_database(self):
        await self.mongo_repository.clear_collections("test_collection")
    
    async def do_test(self):
        global test_result

        await self.clear_database()

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
            self.test_11(),
            self.test_12(),
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
        
    @Test("Test #1. Insert Single Data with Dictionary")
    async def test_1(self):
        result = await self.mongo_repository.insert(
            collection=self.collection_name,
            data={"name": "dalmeng", "type": 1},
            insert_one=True
        )
        return {
            "expected": {"name": "dalmeng", "type": 1},
            "actual": result
        }
    
    @Test("Test #2. Insert Single Data with List")
    async def test_2(self):
        try:
            result = await self.mongo_repository.insert(
                collection=self.collection_name,
                data=[],
                insert_one=True
            )
        except Exception:
            return {
                "expected": Exception,
                "actual": Exception,
            }
    
    @Test("Test #3. Insert Multiple Data with List")
    async def test_3(self):
        result = await self.mongo_repository.insert(
            collection=self.collection_name,
            data=[{"name": "dalmeng1", "type": 3}, {"name": "dalmeng2", "type": 2}, {"name": "dalmeng3", "type": 2}],
            insert_one=False
        )
        return {
            "expected": [{"name": "dalmeng1", "type": 3}, {"name": "dalmeng2", "type": 2}, {"name": "dalmeng3", "type": 2}],
            "actual": result
        }
    
    @Test("Test #4. Insert Multiple Data with Dictionary")
    async def test_4(self):
        try:
            result = await self.mongo_repository.insert(
                collection=self.collection_name,
                data={"name": "dalmeng4", "type": 2},
                insert_one=False
            )
        except:
            return {
                "expected": Exception,
                "actual": Exception
            }
        
    @Test("Test #5. Delete Data")
    async def test_5(self):
        result = await self.mongo_repository.delete(
            collection=self.collection_name,
            filter={"name": "dalmeng3"}
        )
        return {
            "expected": [{"name": "dalmeng3", "type": 2}],
            "actual": result
        }
    
    @Test("Test #6. Find Single Data")
    async def test_6(self):
        result = await self.mongo_repository.find(
            collection=self.collection_name,
            filter={"name": "dalmeng1"},
            find_one=True
        )
        return {
            "expected": {"name": "dalmeng1", "type": 3},
            "actual": result
        }
    
    @Test("Test #7. Find All")
    async def test_7(self):
        result = await self.mongo_repository.find(
            collection=self.collection_name
        )
        return {
            "expected": [{"name": "dalmeng", "type": 1}, {"name": "dalmeng1", "type": 3}, {"name": "dalmeng2", "type": 2}],
            "actual": result
        }
    
    @Test("Test #8. Find Using Filter")
    async def test_8(self):
        result = await self.mongo_repository.find(
            collection=self.collection_name,
            filter={"type": 1}
        )
        return {
            "expected": [{"name": "dalmeng", "type": 1}],
            "actual": result
        }
    
    @Test("Test #9. Update Non-Exist Data")
    async def test_9(self):
        try:
            result = await self.mongo_repository.update(
                collection=self.collection_name,
                filter={"name": "dalmeng3"},
                data={"name": "dalmeng5"}
            )
        except Exception:
            return {
                "expected": Exception,
                "actual": Exception
            }
    
    @Test("Test #10. Update Data")
    async def test_10(self):
        result = await self.mongo_repository.update(
            collection=self.collection_name,
            filter={"name": "dalmeng1"},
            data={"name": "dalmeng1", "type": 1}
        )
        return {
            "expected": {"name": "dalmeng1", "type": 1},
            "actual": result
        }
    
    @Test("Test #11. Upsert Non-Exist Data")
    async def test_11(self):
        result = await self.mongo_repository.upsert(
            collection=self.collection_name,
            filter={"name": "dalmeng3"},
            data={"name": "dalmeng3", "type": 3}
        )
        return {
            "expected": {"name": "dalmeng3", "type": 3},
            "actual": result
        }
    
    @Test("Test #12. Upsert Exist Data")
    async def test_12(self):
        result = await self.mongo_repository.upsert(
            collection=self.collection_name,
            filter={"name": "dalmeng1"},
            data={"name": "dalmeng1", "type": 2}
        )
        return {
            "expected": {"name": "dalmeng1", "type": 2},
            "actual": result
        }

async def main():
    t = MongoTest()
    await t.do_test()

asyncio.run(main())