"""Snowflake database connection and utilities."""
import logging
from .config import (
    SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER, SNOWFLAKE_PASSWORD,
    SNOWFLAKE_WAREHOUSE, SNOWFLAKE_DATABASE, SNOWFLAKE_SCHEMA
)

logger = logging.getLogger(__name__)

_snowflake_conn = None

def get_snowflake_connection():
    """Get or create Snowflake connection."""
    global _snowflake_conn
    
    # Check if Snowflake is configured
    if not all([SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER, SNOWFLAKE_PASSWORD, 
                SNOWFLAKE_WAREHOUSE, SNOWFLAKE_DATABASE]):
        return None
    
    # Return existing connection if valid
    if _snowflake_conn is not None:
        try:
            # Test connection
            _snowflake_conn.cursor().execute("SELECT 1")
            return _snowflake_conn
        except Exception:
            # Connection is stale, create new one
            _snowflake_conn = None
    
    # Create new connection
    try:
        import snowflake.connector
        # Log connection attempt (without password)
        logger.info(f"Attempting Snowflake connection: account={SNOWFLAKE_ACCOUNT}, user={SNOWFLAKE_USER}, warehouse={SNOWFLAKE_WAREHOUSE}, database={SNOWFLAKE_DATABASE}, schema={SNOWFLAKE_SCHEMA}")
        _snowflake_conn = snowflake.connector.connect(
            account=SNOWFLAKE_ACCOUNT,
            user=SNOWFLAKE_USER,
            password=SNOWFLAKE_PASSWORD,
            warehouse=SNOWFLAKE_WAREHOUSE,
            database=SNOWFLAKE_DATABASE,
            schema=SNOWFLAKE_SCHEMA
        )
        logger.info(f"Connected to Snowflake: {SNOWFLAKE_DATABASE}.{SNOWFLAKE_SCHEMA}")
        return _snowflake_conn
    except Exception as e:
        logger.warning(f"Failed to connect to Snowflake: {e}")
        logger.warning(f"Connection details: account={SNOWFLAKE_ACCOUNT}, user={SNOWFLAKE_USER}, warehouse={SNOWFLAKE_WAREHOUSE}, database={SNOWFLAKE_DATABASE}")
        return None

def is_snowflake_available():
    """Check if Snowflake is configured and available."""
    return get_snowflake_connection() is not None
