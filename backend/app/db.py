from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure
import certifi
import logging
import os
from .config import MONGO_URI, MONGO_DB

logger = logging.getLogger(__name__)

# Dev-only escape hatch if your network/VPN/AV is breaking Atlas TLS.
# Put this in backend/.env ONLY if needed:
# MONGO_TLS_ALLOW_INVALID=true
ALLOW_INVALID_TLS = os.getenv("MONGO_TLS_ALLOW_INVALID", "false").lower() in ("1", "true", "yes")

try:
    client = AsyncIOMotorClient(
        MONGO_URI,
        tls=True,
        tlsCAFile=certifi.where(),
        tlsAllowInvalidCertificates=ALLOW_INVALID_TLS,  # dev-only toggle
        serverSelectionTimeoutMS=8000,
        connectTimeoutMS=8000,
        socketTimeoutMS=8000,
    )
    db = client[MONGO_DB]
except Exception as e:
    logger.error(f"Failed to initialize MongoDB client: {e}")
    raise


async def check_connection():
    """Check if MongoDB connection is working"""
    try:
        await client.admin.command("ping")
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
