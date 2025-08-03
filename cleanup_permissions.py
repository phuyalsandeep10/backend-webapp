import asyncio
from src.db.config import async_session
from sqlmodel import text

async def cleanup_permission_tables():
    async with async_session() as session:
        # Check if permission groups table exists
        result = await session.execute(text(
            "SELECT table_name FROM information_schema.tables WHERE table_name = 'sys_permission_groups'"
        ))
        if result.fetchone():
            print("Dropping sys_permission_groups table...")
            await session.execute(text("DROP TABLE IF EXISTS sys_permission_groups CASCADE"))
            await session.commit()
            print("✅ sys_permission_groups table dropped")
        else:
            print("sys_permission_groups table does not exist")

if __name__ == "__main__":
    asyncio.run(cleanup_permission_tables())
