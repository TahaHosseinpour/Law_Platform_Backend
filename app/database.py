from prisma import Prisma

# Global Prisma client instance
db = Prisma()


async def connect_db():
    """Connect to database"""
    await db.connect()
    print("✅ Connected to database")


async def disconnect_db():
    """Disconnect from database"""
    await db.disconnect()
    print("❌ Disconnected from database")
