import certifi
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import AsyncGenerator
from .core.config import settings
from .schemas import EmissionRecord

client: AsyncIOMotorClient = None
database: AsyncIOMotorDatabase = None

async def init_db():
    global client, database
    try:
        client = AsyncIOMotorClient(
            settings.MONGO_URI,
            tlsCAFile=certifi.where()
        )
        
        db_name = settings.MONGO_URI.split('/')[-1].split('?')[0]
        
        if not db_name:
            db_name = getattr(settings, 'DB_NAME', 'carbon_tracker_db')
            print(f"⚠️  No DB name found in URI, using: '{db_name}'")
        
        database = client[db_name]
        
        await database.command('ping') 
        print(f"✅ MongoDB connection successful. Database: '{db_name}'")

    except Exception as e:
        print(f"❌ Error connecting to MongoDB: {e}")

async def get_db() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    if database is None:
        raise ConnectionError("Database connection is not initialized or failed to connect.")
    yield database