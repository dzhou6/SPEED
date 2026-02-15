from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure
import certifi
import logging
import os

from .config import MONGO_URI, MONGO_DB

logger = logging.getLogger(__name__)

# Dev-only escape hatch if your network/VPN/AV is breaking Atlas TLS.
# Put this in backend/.env ONLY if needed:
#   MONGO_TLS_ALLOW_INVALID=true
ALLOW_INVALID_TLS = os.getenv("MONGO_TLS_ALLOW_INVALID", "false").lower() in ("1", "true", "yes")


def _parse_bool(v: str | None) -> bool | None:
    if v is None:
        return None
    s = v.strip().lower()
    if s in ("1", "true", "yes", "y", "on"):
        return True
    if s in ("0", "false", "no", "n", "off"):
        return False
    return None


def _should_use_tls(uri: str) -> bool:
    # Explicit override (useful for local Mongo or weird corp proxies)
    override = _parse_bool(os.getenv("MONGO_TLS"))
    if override is not None:
        return override

    u = (uri or "").lower()

    # If someone explicitly turned it off in the URI, respect it.
    if "tls=false" in u or "ssl=false" in u:
        return False

    # Atlas / SRV almost always wants TLS.
    if u.startswith("mongodb+srv://"):
        return True
    if "mongodb.net" in u:
        return True

    # If it’s explicitly enabled in the URI, do it.
    if "tls=true" in u or "ssl=true" in u:
        return True

    return False


USE_TLS = _should_use_tls(MONGO_URI)

try:
    kwargs = dict(
        serverSelectionTimeoutMS=8000,
        connectTimeoutMS=8000,
        socketTimeoutMS=8000,
    )

    if USE_TLS:
        kwargs.update(
            tls=True,
            tlsCAFile=certifi.where(),
            tlsAllowInvalidCertificates=ALLOW_INVALID_TLS,
        )

    client = AsyncIOMotorClient(MONGO_URI, **kwargs)
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
