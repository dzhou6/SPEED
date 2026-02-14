from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.patriot_ai import generate_match_explain, PROMPT_VERSION

router = APIRouter(prefix="/ai", tags=["ai"])

class ExplainReq(BaseModel):
    viewer_id: str
    candidate_id: str
    mode: str = "quick"     # "quick" or "skill"
    context: dict = {}

@router.post("/match_explain")
async def match_explain(req: ExplainReq):
    # --- Get DB handle (adjust this to your project’s DB pattern) ---
    # Common patterns:
    #   from app.db import get_db
    #   db = get_db()
    #
    # OR:
    #   from app.db import db
    #   db = db
    #
    # Replace the next 2 lines accordingly:
    from app.db import get_db
    db = get_db()

    cache_key = {
        "viewer_id": req.viewer_id,
        "candidate_id": req.candidate_id,
        "mode": req.mode,
        "prompt_version": PROMPT_VERSION,
    }

    cached = await db.ai_explanations.find_one(cache_key)
    if cached:
        return cached["result"]

    viewer = await db.profiles.find_one({"_id": req.viewer_id})
    candidate = await db.profiles.find_one({"_id": req.candidate_id})
    if not viewer or not candidate:
        raise HTTPException(status_code=404, detail="Profile not found")

    result = await generate_match_explain(
        viewer, candidate, {"mode": req.mode, **(req.context or {})}
    )

    await db.ai_explanations.insert_one({**cache_key, "result": result})
    return result
