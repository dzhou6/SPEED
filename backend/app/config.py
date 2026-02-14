import os
from dotenv import load_dotenv

load_dotenv()

def get_env(name: str, default: str | None = None) -> str:
    v = os.getenv(name, default)
    if v is None or v.strip() == "":
        raise RuntimeError(f"Missing required env var: {name}")
    return v

MONGO_URI = get_env("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB", "coursecupid")


