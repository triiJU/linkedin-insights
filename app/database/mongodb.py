from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

class MongoDB:
    client: AsyncIOMotorClient = None
    
mongodb = MongoDB()

async def connect_to_mongo():
    mongodb.client = AsyncIOMotorClient(settings.MONGODB_URL)
    await mongodb.client.admin.command('ping')
    print("Connected to MongoDB!")
    
    # Create indexes
    db = mongodb.client[settings.DATABASE_NAME]
    
    # Pages collection indexes
    await db.pages.create_index("page_id", unique=True)
    await db.pages.create_index("total_followers")
    await db.pages.create_index("industry")
    await db.pages.create_index("page_name", name="page_name_text")
    
    # Posts collection indexes
    await db.posts.create_index("post_id", unique=True)
    await db.posts.create_index("page_id")
    await db.posts.create_index("posted_at")
    
    # Users collection indexes
    await db.users.create_index("user_id", unique=True)
    await db.users.create_index("company_page_id")

async def close_mongo_connection():
    mongodb.client.close()
    print("Closed MongoDB connection!")

def get_database():
    return mongodb.client[settings.DATABASE_NAME]
