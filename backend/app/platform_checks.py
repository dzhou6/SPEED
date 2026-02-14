from __future__ import annotations
import os

def require_env(name: str) -> str:
    v = os.getenv(name)
    if not v or not v.strip():
        raise RuntimeError(f"Missing required environment variable: {name}")
    return v

def validate_mongo_uri(uri: str) -> None:
    if not (uri.startswith("mongodb://") or uri.startswith("mongodb+srv://")):
        raise RuntimeError("MONGO_URI must start with mongodb:// or mongodb+srv://")
    if uri.strip().startswith(("'", '"')) or uri.strip().endswith(("'", '"')):
        raise RuntimeError("MONGO_URI looks quoted. Remove surrounding quotes in .env")

def run_platform_checks() -> None:
    mongo_uri = require_env("MONGO_URI")
    validate_mongo_uri(mongo_uri)
