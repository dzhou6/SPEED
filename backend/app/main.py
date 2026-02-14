from __future__ import annotations
from .platform_checks import run_platform_checks
@app.on_event("startup")
async def _startup():
    run_platform_checks()

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone
from bson import ObjectId

from .db import col
from .models import DemoAuthIn, DemoAuthOut, ProfileIn, SwipeIn, HubIn, AskIn, AskOut
from .matching import rank_candidates

app = FastAPI(title="CourseCupid MVP")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

def require_user(x_user_id: str | None) -> ObjectId:
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Missing X-User-Id")
    try:
        return ObjectId(x_user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid X-User-Id")

from .db import db

@app.get("/health")
async def health():
    try:
        await db.command("ping")
        return {"ok": True, "db": "ok"}
    except Exception as e:
        return {"ok": False, "db": "down", "error": str(e)}


@app.post("/auth/demo", response_model=DemoAuthOut)
async def auth_demo(body: DemoAuthIn):
    users = col("users")
    doc = {
        "displayName": body.displayName or f"User{str(ObjectId())[-4:]}",
        "courseCodes": [body.courseCode],
        "rolePrefs": [],
        "skills": [],
        "availability": [],
        "goals": None,
        "createdAt": datetime.now(timezone.utc),
    }
    res = await users.insert_one(doc)
    return DemoAuthOut(userId=str(res.inserted_id), displayName=doc["displayName"])

@app.post("/profile")
async def upsert_profile(body: ProfileIn, x_user_id: str | None = Header(default=None, alias="X-User-Id")):
    uid = require_user(x_user_id)
    users = col("users")
    await users.update_one(
        {"_id": uid},
        {
            "$addToSet": {"courseCodes": body.courseCode},
            "$set": {
                "displayName": body.displayName,
                "rolePrefs": body.rolePrefs,
                "skills": body.skills,
                "availability": body.availability,
                "goals": body.goals,
            },
        },
        upsert=False,
    )
    return {"ok": True}

@app.post("/heartbeat")
async def heartbeat(courseCode: str, x_user_id: str | None = Header(default=None, alias="X-User-Id")):
    uid = require_user(x_user_id)
    presence = col("presence")
    await presence.update_one(
        {"userId": uid, "courseCode": courseCode},
        {"$set": {"lastActiveAt": datetime.now(timezone.utc)}},
        upsert=True,
    )
    return {"ok": True}

async def get_last_active_map(courseCode: str):
    presence = col("presence")
    cur = presence.find({"courseCode": courseCode})
    m = {}
    async for p in cur:
        m[str(p["userId"])] = p.get("lastActiveAt")
    return m

@app.get("/recommendations")
async def recommendations(courseCode: str, x_user_id: str | None = Header(default=None, alias="X-User-Id")):
    uid = require_user(x_user_id)
    users = col("users")
    swipes = col("swipes")
    pods = col("pods")

    me = await users.find_one({"_id": uid})
    if not me:
        raise HTTPException(404, "User not found")

    already = set()
    async for s in swipes.find({"fromUserId": uid, "courseCode": courseCode}):
        already.add(str(s["toUserId"]))

    my_pod = await pods.find_one({"courseCode": courseCode, "memberIds": uid})
    my_pod_roles = []
    if my_pod:
        async for member in users.find({"_id": {"$in": my_pod["memberIds"]}}):
            if member.get("rolePrefs"):
                my_pod_roles.extend(member["rolePrefs"])

    last_active = await get_last_active_map(courseCode)

    cand = []
    async for u in users.find({"_id": {"$ne": uid}, "courseCodes": courseCode}):
        if str(u["_id"]) in already:
            continue
        u["lastActiveAt"] = last_active.get(str(u["_id"]))
        cand.append(u)

    ranked = rank_candidates(me, cand, my_pod_roles)

    out = []
    for r in ranked:
        u = next((x for x in cand if str(x["_id"]) == r["userId"]), None)
        if not u:
            continue
        out.append({
            "userId": r["userId"],
            "displayName": u.get("displayName", "Student"),
            "rolePrefs": u.get("rolePrefs", []),
            "skills": u.get("skills", [])[:6],
            "availability": u.get("availability", [])[:3],
            "lastActiveAt": u.get("lastActiveAt"),
            "score": r["score"],
            "reasons": r["reasons"],
        })
    return {"candidates": out}

async def has_mutual_accept(courseCode: str, a: ObjectId, b: ObjectId) -> bool:
    swipes = col("swipes")
    ab = await swipes.find_one({"courseCode": courseCode, "fromUserId": a, "toUserId": b, "decision": "accept"})
    ba = await swipes.find_one({"courseCode": courseCode, "fromUserId": b, "toUserId": a, "decision": "accept"})
    return bool(ab and ba)

async def get_user_pod(courseCode: str, uid: ObjectId):
    pods = col("pods")
    return await pods.find_one({"courseCode": courseCode, "memberIds": uid})

@app.post("/swipe")
async def swipe(body: SwipeIn, x_user_id: str | None = Header(default=None, alias="X-User-Id")):
    uid = require_user(x_user_id)
    users = col("users")
    swipes = col("swipes")

    target = ObjectId(body.targetUserId)
    if uid == target:
        raise HTTPException(400, "Cannot swipe self")

    me = await users.find_one({"_id": uid, "courseCodes": body.courseCode})
    other = await users.find_one({"_id": target, "courseCodes": body.courseCode})
    if not me or not other:
        raise HTTPException(400, "Both users must be in the course")

    await swipes.update_one(
        {"fromUserId": uid, "toUserId": target, "courseCode": body.courseCode},
        {"$set": {"decision": body.decision, "createdAt": datetime.now(timezone.utc)}},
        upsert=True,
    )

    mutual = False
    pod_updated = False
    pod_id = None

    if body.decision == "accept":
        mutual = await has_mutual_accept(body.courseCode, uid, target)
        if mutual:
            pods = col("pods")
            pod_me = await get_user_pod(body.courseCode, uid)
            pod_other = await get_user_pod(body.courseCode, target)

            if pod_me and pod_other and pod_me["_id"] != pod_other["_id"]:
                raise HTTPException(409, "Both users already in different pods")
            if pod_me and len(pod_me["memberIds"]) >= 4 and target not in pod_me["memberIds"]:
                raise HTTPException(409, "Pod is full")

            if not pod_me and not pod_other:
                doc = {
                    "courseCode": body.courseCode,
                    "memberIds": [uid, target],
                    "leaderId": uid,
                    "hubLink": None,
                    "createdAt": datetime.now(timezone.utc),
                }
                res = await pods.insert_one(doc)
                pod_id = str(res.inserted_id)
                pod_updated = True
            else:
                existing = pod_me or pod_other
                if target not in existing["memberIds"]:
                    if len(existing["memberIds"]) >= 4:
                        raise HTTPException(409, "Pod is full")
                    await pods.update_one({"_id": existing["_id"]}, {"$addToSet": {"memberIds": target}})
                    pod_updated = True
                pod_id = str(existing["_id"])

    return {"ok": True, "mutual": mutual, "podUpdated": pod_updated, "podId": pod_id}

@app.get("/pod")
async def pod(courseCode: str, x_user_id: str | None = Header(default=None, alias="X-User-Id")):
    uid = require_user(x_user_id)
    pods = col("pods")
    users = col("users")

    p = await pods.find_one({"courseCode": courseCode, "memberIds": uid})
    if not p:
        return {"hasPod": False}

    members = []
    last_active = await get_last_active_map(courseCode)

    async for u in users.find({"_id": {"$in": p["memberIds"]}}):
        members.append({
            "userId": str(u["_id"]),
            "displayName": u.get("displayName", "Student"),
            "rolePrefs": u.get("rolePrefs", []),
            "skills": u.get("skills", [])[:6],
            "availability": u.get("availability", [])[:3],
            "lastActiveAt": last_active.get(str(u["_id"])),
        })

    unlocked = []
    for m in members:
        mid = ObjectId(m["userId"])
        if mid == uid:
            continue
        if await has_mutual_accept(courseCode, uid, mid):
            unlocked.append(m["userId"])

    return {
        "hasPod": True,
        "podId": str(p["_id"]),
        "courseCode": courseCode,
        "leaderId": str(p["leaderId"]),
        "memberIds": [str(x) for x in p["memberIds"]],
        "members": members,
        "unlockedContactIds": unlocked,
        "hubLink": p.get("hubLink"),
    }

@app.post("/pod/hub")
async def set_hub(body: HubIn, x_user_id: str | None = Header(default=None, alias="X-User-Id")):
    uid = require_user(x_user_id)
    pods = col("pods")
    p = await pods.find_one({"courseCode": body.courseCode, "memberIds": uid})
    if not p:
        raise HTTPException(404, "No pod")
    if p["leaderId"] != uid:
        raise HTTPException(403, "Only leader can set hub link")
    if not body.hubLink.startswith("https://docs.google.com/"):
        raise HTTPException(400, "Hub link must be a Google Docs/Sheets link")
    await pods.update_one({"_id": p["_id"]}, {"$set": {"hubLink": body.hubLink}})
    return {"ok": True}

def route_question(q: str) -> int:
    ql = q.lower()
    logistics_words = ["when", "due", "deadline", "final", "midterm", "exam", "where", "room", "office hour", "syllabus"]
    pointer_words = ["explain", "concept", "lecture", "slides", "topic", "reading", "understand", "confused"]
    if any(w in ql for w in logistics_words):
        return 1
    if any(w in ql for w in pointer_words):
        return 2
    return 3

@app.post("/ask", response_model=AskOut)
async def ask(body: AskIn, x_user_id: str | None = Header(default=None, alias="X-User-Id")):
    _ = require_user(x_user_id)

    courses = col("courses")
    c = await courses.find_one({"courseCode": body.courseCode})
    if not c:
        raise HTTPException(404, "Course not found (seed demo data first)")

    layer = route_question(body.question)

    if layer == 1:
        return AskOut(layer=1, answer=f"(Layer 1 Logistics)\n\n“{c['syllabusText'][:220]}...”", links=[])

    if layer == 2:
        mats = c.get("materials", [])[:10]
        if not mats:
            return AskOut(layer=2, answer="(Layer 2 Pointer) No materials available.", links=[])
        ql = body.question.lower()
        picks = []
        for m in mats:
            kws = [k.lower() for k in m.get("keywords", [])]
            if any(k in ql for k in kws):
                picks.append(m)
        if not picks:
            picks = mats[:2]
        links = [p["url"] for p in picks[:2]]
        titles = [p["title"] for p in picks[:2]]
        return AskOut(layer=2, answer=f"(Layer 2 Pointer) Check: {', '.join(titles)}", links=links)

    tickets = col("tickets")
    res = await tickets.insert_one({
        "courseCode": body.courseCode,
        "question": body.question,
        "status": "open",
        "createdAt": datetime.now(timezone.utc),
    })
    return AskOut(layer=3, answer=f"(Layer 3 Escalation) Ticket created: {str(res.inserted_id)}", links=[])
