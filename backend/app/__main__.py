import sys
import asyncio
from app.seed_demo import main as seed_main

if __name__ == "__main__":
    cmd = sys.argv[1:] if len(sys.argv) > 1 else []
    if not cmd:
        print("Usage: python -m app seed")
        raise SystemExit(2)

    if cmd[0] == "seed":
        asyncio.run(seed_main())
    else:
        print(f"Unknown command: {cmd[0]}")
        raise SystemExit(2)
