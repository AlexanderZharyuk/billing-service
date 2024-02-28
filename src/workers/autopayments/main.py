import asyncio

from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import text

from src.workers.helpers import session_injection


@session_injection
async def test(session: AsyncSession = None):
    sql = text("SELECT * FROM templates")
    result = await session.exec(sql)
    return list(result.scalars())

async def main():
    while True:
        #ToDo: examples for test
        first = await test()
        print(f"func test1 execute: {first}\nfunc test2 execute: {first}")
        #await asyncio.sleep(1) #ToDo: for future

if __name__ == "__main__":
    asyncio.run(main())