from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure
import logging
from .config import MONGO_URI, MONGO_DB

logger = logging.getLogger(__name__)

try:
    client = AsyncIOMotorClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client[MONGO_DB]
except Exception as e:
    logger.error(f"Failed to initialize MongoDB client: {e}")
    raise

async def check_connection():
    """Check if MongoDB connection is working"""
    try:
        await client.admin.command('ping')
        logger.info(f"Connected to MongoDB: {MONGO_DB}")
        return True
    except (ServerSelectionTimeoutError, ConnectionFailure) as e:
        logger.error(f"❌ MongoDB connection timeout: {e}")
        raise RuntimeError(
            "Cannot connect to MongoDB. Please check:\n"
            "1. MONGO_URI is correct in .env file\n"
            "2. MongoDB Atlas IP allowlist includes your IP (or 0.0.0.0/0 for dev)\n"
            "3. Database user has proper permissions\n"
            "4. Network connection is working"
        )
    except Exception as e:
        logger.error(f"❌ MongoDB connection error: {e}")
        raise RuntimeError(f"Cannot connect to MongoDB: {e}")

def col(name: str):
    return db[name]
