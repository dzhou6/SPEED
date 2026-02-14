from __future__ import annotations
from datetime import datetime, timezone, timedelta
import asyncio
from .db import col

DEMO_COURSE = "CS471"

USERS = [
    ("Ava", ["Backend"], ["Python", "APIs", "FastAPI", "MongoDB"], ["Mon evening", "Wed evening"]),
    ("Noah", ["Matching"], ["ML", "Python", "Data"], ["Tue evening", "Thu evening"]),
    ("Mia", ["Platform"], ["Docker", "Git", "AWS"], ["Fri evening", "Sat afternoon"]),
]

MATERIALS = [
    {"title":"Lecture 2: Processes", "keywords":["process","fork","exec"], "url":"https://example.com/lec2"},
    {"title":"Lecture 3: Threads", "keywords":["threads","synchronization"], "url":"https://example.com/lec3"},
    {"title":"Exam Info", "keywords":["midterm","final","exam"], "url":"https://example.com/exams"},
]

SYLLABUS_TEXT = (
    "CS471 Demo Syllabus: Midterm is March 12. Final is May 12 at 10:30AM. "
    "Homework is due Fridays at 11:59PM. Office hours: Tue 2–4PM, Thu 3–5PM."
)

async def main():
    users = col("users")
    presence = col("presence")
    courses = col("courses")

    await courses.delete_many({"courseCode": DEMO_COURSE})
    await users.delete_many({"courseCodes": DEMO_COURSE})
    await presence.delete_many({"courseCode": DEMO_COURSE})

    await courses.insert_one({
        "courseCode": DEMO_COURSE,
        "courseName": "Operating Systems (Demo)",
        "syllabusText": SYLLABUS_TEXT,
        "materials": MATERIALS,
        "createdAt": datetime.now(timezone.utc),
    })

    now = datetime.now(timezone.utc)
    for i, (name, roles, skills, avail) in enumerate(USERS):
        res = await users.insert_one({
            "displayName": name,
            "courseCodes": [DEMO_COURSE],
            "rolePrefs": roles,
            "skills": skills,
            "availability": avail,
            "goals": "Study + accountability",
            "createdAt": now,
        })
        last = now - timedelta(hours=(i * 6) % 48)
        await presence.insert_one({"userId": res.inserted_id, "courseCode": DEMO_COURSE, "lastActiveAt": last})

    print("Seeded demo.")

if __name__ == "__main__":
    asyncio.run(main())
