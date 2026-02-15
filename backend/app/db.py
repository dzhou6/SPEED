from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure
import certifi
import logging
import os
from .config import MONGO_URI, MONGO_DB

logger = logging.getLogger(__name__)

def _env_flag(name: str, default: bool = False) -> bool:
    v = os.getenv(name)
    if v is None:
        return default
    return v.strip().lower() in ("1", "true", "yes", "y", "on")

# Dev-only escape hatch if your network/VPN/AV is breaking Atlas TLS.
# Put this in backend/.env ONLY if needed:
#   MONGO_TLS_ALLOW_INVALID=true
ALLOW_INVALID_TLS = _env_flag("MONGO_TLS_ALLOW_INVALID", False)

# Optional override:
#   MONGO_TLS=true/false
MONGO_TLS_OVERRIDE = os.getenv("MONGO_TLS")

def _should_use_tls(uri: str) -> bool:
    if MONGO_TLS_OVERRIDE is not None:
        return _env_flag("MONGO_TLS", False)
    u = uri.lower()
    if u.startswith("mongodb+srv://"):
        return True
    return ("tls=true" in u) or ("ssl=true" in u)

mongo_kwargs = dict(
    serverSelectionTimeoutMS=8000,
    connectTimeoutMS=8000,
    socketTimeoutMS=8000,
)

try:
    if _should_use_tls(MONGO_URI):
        mongo_kwargs.update(
            tls=True,
            tlsCAFile=certifi.where(),
            tlsAllowInvalidCertificates=ALLOW_INVALID_TLS,
        )

    client = AsyncIOMotorClient(MONGO_URI, **mongo_kwargs)
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
