import asyncio
import asyncpg
from src.core.config import settings
from data import test_data
import asyncio
import asyncpg


async def main():
    conn = await asyncpg.connect(
        f"postgresql://{settings.postgres_user}:"
        f"{settings.postgres_password}@{settings.postgres_host}:"
        f"{settings.postgres_port}/{settings.postgres_db}"
    )

    for table in test_data.keys():
        await conn.execute(f"TRUNCATE TABLE {table} CASCADE")
        table_data = test_data[table]
        columns = table_data[0].keys()

        query = f"""INSERT INTO {table} ({','.join(columns)})
                VALUES ({','.join(['$'+str(n+1) for n in range(len(columns))])});"""
        print(query)
        values = [[value for value in table_data.values()] for table_data in test_data[table]]
        await conn.executemany(query, values)
    await conn.close()


asyncio.get_event_loop().run_until_complete(main())
