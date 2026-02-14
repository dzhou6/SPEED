import os, json
import httpx

PROMPT_VERSION = "v1"

def _fallback(viewer, candidate):
    name = candidate.get("name") or candidate.get("displayName") or "This person"
    return {
        "headline": f"{name} looks like a solid match 💘",
        "reasons": [
            "Complementary roles/skills for a balanced pod",
            "Similar goals and workable availability",
        ],
        "risks": [],
        "icebreaker": "Hey! We look like a good match for roles + schedule. Want to team up and do a quick 10-min kickoff?",
        "pod_idea": "Build a pod/team matchmaking MVP with accept/pass and anti-ghosting.",
        "prompt_version": PROMPT_VERSION,
    }

async def generate_match_explain(viewer: dict, candidate: dict, context: dict) -> dict:
    if os.getenv("PATRIOTAI_ENABLED", "false").lower() != "true":
        return _fallback(viewer, candidate)

    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "").rstrip("/")
    key = os.getenv("AZURE_OPENAI_API_KEY", "")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")

    if not endpoint or not key or not deployment:
        return _fallback(viewer, candidate)

    url = f"{endpoint}/openai/deployments/{deployment}/chat/completions?api-version={api_version}"

    system = (
        "You are PatriotAI for team matchmaking. Output ONLY valid JSON with keys: "
        "headline (string), reasons (array of strings), risks (array of strings), "
        "icebreaker (string), pod_idea (string). Keep it concise, specific, and friendly."
    )

    user = {
        "viewer": viewer,
        "candidate": candidate,
        "context": context,
        "constraints": {"max_reasons": 5, "max_risks": 3, "valentine_flair": True},
    }

    payload = {
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(user)},
        ],
        "temperature": 0.4,
        "max_tokens": 350,
    }

    headers = {"api-key": key, "Content-Type": "application/json"}

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            text = resp.json()["choices"][0]["message"]["content"]
            data = json.loads(text)
            data["prompt_version"] = PROMPT_VERSION
            return data
    except Exception:
        return _fallback(viewer, candidate)
