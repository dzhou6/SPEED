from __future__ import annotations

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone
from bson import ObjectId
import os

import logging
from .platform_checks import run_platform_checks
from .db import col, db, check_connection
from .models import DemoAuthIn, DemoAuthOut, ProfileIn, SwipeIn, HubIn, AskIn, AskOut, CourseOut
from .matching import rank_candidates

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="CourseCupid MVP")

# Optional AI routes (for match explanations)
try:
    from .ai_routes import router as ai_router
    app.include_router(ai_router)
except ImportError:
    logger.warning("ai_routes not available, skipping")



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def _startup():
    logger.info("Starting CourseCupid API...")
    run_platform_checks()
    await check_connection()
    logger.info("✅ Application startup complete")

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

@app.get("/course", response_model=CourseOut)
async def get_course(courseCode: str):
    """Get course information including name, description, professor, location, and policies"""
    courses = col("courses")
    c = await courses.find_one({"courseCode": courseCode})
    if not c:
        raise HTTPException(404, "Course not found")
    return CourseOut(
        courseCode=courseCode,
        courseName=c.get("courseName"),
        syllabusText=c.get("syllabusText"),
        professor=c.get("professor"),
        location=c.get("location"),
        classPolicy=c.get("classPolicy"),
        latePolicy=c.get("latePolicy"),
        officeHours=c.get("officeHours")
    )


@app.post("/auth/demo", response_model=DemoAuthOut)
async def auth_demo(body: DemoAuthIn):
    users = col("users")
    # Check if user already exists (by checking if they have any course)
    # For demo, we'll create new user each time, but in real app you'd check by email/auth
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

@app.get("/user/courses")
async def get_user_courses(x_user_id: str | None = Header(default=None, alias="X-User-Id")):
    """Get all courses the user is enrolled in"""
    try:
        uid = require_user(x_user_id)
        users = col("users")
        courses = col("courses")
        
        user = await users.find_one({"_id": uid})
        if not user:
            # Return empty list instead of 404 for better UX
            return {"courseCodes": [], "courses": []}
        
        user_course_codes = user.get("courseCodes", [])
        if not user_course_codes:
            return {"courseCodes": [], "courses": []}
        
        # Get course details for each course code
        course_list = []
        async for course in courses.find({"courseCode": {"$in": user_course_codes}}):
            course_list.append({
                "courseCode": course.get("courseCode"),
                "courseName": course.get("courseName")
            })
        
        logger.info(f"User {uid} has courses: {user_course_codes}, found details for: {[c['courseCode'] for c in course_list]}")
        return {"courseCodes": user_course_codes, "courses": course_list}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user courses: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get courses: {str(e)}")

@app.post("/user/add-course")
async def add_course_to_user(courseCode: str, x_user_id: str | None = Header(default=None, alias="X-User-Id")):
    """Add a course to user's enrolled courses"""
    try:
        uid = require_user(x_user_id)
        users = col("users")
        
        # Add course to user's courseCodes array
        result = await users.update_one(
            {"_id": uid},
            {"$addToSet": {"courseCodes": courseCode}},
            upsert=False
        )
        
        if result.matched_count == 0:
            raise HTTPException(404, "User not found")
        
        return {"ok": True, "courseCode": courseCode}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding course: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add course: {str(e)}")

@app.post("/profile")
async def upsert_profile(body: ProfileIn, x_user_id: str | None = Header(default=None, alias="X-User-Id")):
    try:
        uid = require_user(x_user_id)
        users = col("users")

        doc = body.model_dump(exclude_none=True)
    # we don't want these as normal fields if you're using courseCodes + header user id
        doc.pop("courseCode", None)
        doc.pop("userId", None)

        await users.update_one(
            {"_id": uid},
            {
                "$addToSet": {"courseCodes": body.courseCode},
                "$set": doc,
            },
            upsert=True,
        )
        return {"ok": True}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving profile: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save profile: {str(e)}")

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
async def recommendations(
    courseCode: str, 
    mode: str = "skillmatch",
    x_user_id: str | None = Header(default=None, alias="X-User-Id")
):
    try:
        uid = require_user(x_user_id)
        users = col("users")
        swipes = col("swipes")
        pods = col("pods")
    except Exception as e:
        logger.error(f"Error in recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    # Validate mode
    if mode not in ["quickmatch", "skillmatch"]:
        mode = "skillmatch"  # Default to skillmatch if invalid

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

    ranked = rank_candidates(me, cand, my_pod_roles, mode=mode)

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
    try:
        uid = require_user(x_user_id)
        pods = col("pods")
        users = col("users")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in pod endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

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

async def ask_ai_syllabus(question: str, syllabus_text: str) -> str:
    """Use OpenAI to answer questions about the syllabus intelligently."""
    try:
        from openai import OpenAI
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            # Fallback to simple text search if no API key
            return _fallback_syllabus_answer(question, syllabus_text)
        
        client = OpenAI(api_key=api_key)
        
        # More generic system prompt that works for all courses
        system_prompt = (
            "You are a helpful and friendly teaching assistant for a university course. "
            "Your job is to answer student questions about the course syllabus in a natural, conversational way. "
            "DO NOT just copy-paste text from the syllabus. Instead, read the syllabus carefully and provide "
            "a clear, helpful answer in your own words. Be concise but complete. "
            "When mentioning specific dates, times, percentages, or policies, be accurate and include the exact details. "
            "If the answer is not in the syllabus, say so clearly and suggest they contact the instructor. "
            "Format your answer in a friendly, easy-to-read way with proper structure."
        )
        
        user_prompt = (
            f"Student Question: {question}\n\n"
            f"Course Syllabus:\n{syllabus_text}\n\n"
            f"Please answer the student's question in a natural, conversational way. "
            f"Read the syllabus carefully and explain the answer clearly in your own words. "
            f"Do NOT just copy text from the syllabus - synthesize the information and explain it naturally. "
            f"Be accurate with dates, times, and specific details. "
            f"If the information is not in the syllabus, say 'I don't see that information in the syllabus. Please contact your instructor for clarification.'"
        )
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,  # Lower temperature for more accurate, consistent answers
            max_tokens=800  # Increased for more detailed responses
        )
        
        answer = response.choices[0].message.content.strip()
        return answer
        
    except Exception as e:
        logger.warning(f"OpenAI API error: {e}, falling back to simple search")
        return _fallback_syllabus_answer(question, syllabus_text)

def _fallback_syllabus_answer(question: str, syllabus_text: str) -> str:
    """Fallback method when OpenAI is not available - simple keyword matching."""
    ql = question.lower()
    syllabus_lower = syllabus_text.lower()
    
    # Extract relevant sections based on keywords
    keywords_map = {
        "due": ["due", "deadline", "submission"],
        "exam": ["exam", "midterm", "final"],
        "homework": ["homework", "assignment"],
        "office": ["office hours", "office"],
        "grade": ["grading", "grade", "percentage"],
        "policy": ["policy", "late", "attendance"],
        "project": ["project", "final project"],
        "when": ["when", "date", "time"],
        "where": ["where", "location", "room"]
    }
    
    # Find relevant sections
    lines = syllabus_text.split('\n')
    relevant_lines = []
    for keyword_group in keywords_map.values():
        if any(kw in ql for kw in keyword_group):
            for line in lines:
                if any(kw in line.lower() for kw in keyword_group):
                    if line.strip() and len(line.strip()) > 10:
                        relevant_lines.append(line.strip())
    
    if relevant_lines:
        return f"Based on the syllabus:\n\n" + "\n".join(relevant_lines[:5])
    else:
        # Return a snippet around the question keywords
        words = ql.split()
        for word in words:
            if len(word) > 3 and word in syllabus_lower:
                idx = syllabus_lower.find(word)
                start = max(0, idx - 200)
                end = min(len(syllabus_text), idx + 300)
                snippet = syllabus_text[start:end]
                return f"Found in syllabus:\n\n{snippet}..."
        
        return f"Here's a relevant section from the syllabus:\n\n{syllabus_text[:500]}..."

@app.post("/ask", response_model=AskOut)
async def ask(body: AskIn, x_user_id: str | None = Header(default=None, alias="X-User-Id")):
    """All questions are routed to Layer 1 (Syllabus AI) for now."""
    _ = require_user(x_user_id)

    courses = col("courses")
    c = await courses.find_one({"courseCode": body.courseCode})
    if not c:
        raise HTTPException(404, "Course not found (seed demo data first)")

    # Always use Layer 1 - Syllabus AI for all questions
    syllabus_text = c.get("syllabusText", "")
    if syllabus_text:
        ai_answer = await ask_ai_syllabus(body.question, syllabus_text)
        return AskOut(layer=1, answer=f"📋 Syllabus Assistant\n\n{ai_answer}", links=[])
    else:
        return AskOut(layer=1, answer="Syllabus information not available. Please contact your instructor.", links=[])
