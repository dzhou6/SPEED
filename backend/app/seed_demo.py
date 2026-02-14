from __future__ import annotations
from datetime import datetime, timezone, timedelta
import asyncio
import logging
from .db import col, check_connection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEMO_COURSE = "CS471"

# 12 users across all 4 roles with varied skills and availability
USERS = [
    # Frontend role users
    ("Alex", ["Frontend"], ["React", "JavaScript", "UI/UX", "CSS", "TypeScript"], ["Mon evening", "Wed evening", "Fri evening"]),
    ("Casey", ["Frontend"], ["React", "TypeScript", "UI/UX", "Testing", "Design"], ["Mon evening", "Wed evening"]),
    ("Jordan", ["Frontend", "Backend"], ["React", "Python", "APIs", "Full-stack"], ["Tue evening", "Thu evening", "Sat afternoon"]),
    
    # Backend role users
    ("Ava", ["Backend"], ["Python", "APIs", "FastAPI", "MongoDB", "REST"], ["Mon evening", "Wed evening"]),
    ("Sam", ["Backend"], ["Python", "APIs", "MongoDB", "Security", "Testing"], ["Tue evening", "Thu evening", "Sat afternoon"]),
    ("Morgan", ["Backend", "Platform"], ["Python", "Docker", "AWS", "APIs", "DevOps"], ["Tue evening", "Thu evening"]),
    
    # Matching role users
    ("Noah", ["Matching"], ["ML", "Python", "Data", "Algorithms"], ["Tue evening", "Thu evening"]),
    ("Riley", ["Matching"], ["ML", "Python", "Data", "Statistics", "Optimization"], ["Fri evening", "Sat afternoon"]),
    ("Cameron", ["Matching", "Platform"], ["ML", "Python", "Docker", "Data", "Infrastructure"], ["Mon evening", "Wed evening", "Fri evening"]),
    
    # Platform role users
    ("Mia", ["Platform"], ["Docker", "Git", "AWS", "CI/CD", "DevOps"], ["Fri evening", "Sat afternoon"]),
    ("Taylor", ["Platform"], ["Docker", "Git", "Azure", "CI/CD", "Kubernetes"], ["Mon evening", "Wed evening", "Fri evening"]),
    ("Avery", ["Platform", "Backend"], ["Docker", "Python", "AWS", "APIs", "Infrastructure"], ["Tue evening", "Thu evening"]),
]

# 12 materials with keywords for Layer 2 AI pointer system
MATERIALS = [
    {"title": "Lecture 1: Introduction to Software Engineering", "keywords": ["introduction", "overview", "software engineering", "basics", "fundamentals"], "url": "https://docs.google.com/presentation/d/lecture1"},
    {"title": "Lecture 2: Requirements Engineering", "keywords": ["requirements", "specifications", "gathering", "analysis", "user stories"], "url": "https://docs.google.com/presentation/d/lecture2"},
    {"title": "Lecture 3: System Design and Architecture", "keywords": ["design", "architecture", "system design", "patterns", "structure"], "url": "https://docs.google.com/presentation/d/lecture3"},
    {"title": "Lecture 4: Testing and Quality Assurance", "keywords": ["testing", "QA", "quality", "test cases", "unit tests", "integration"], "url": "https://docs.google.com/presentation/d/lecture4"},
    {"title": "Lecture 5: Version Control and Git", "keywords": ["git", "version control", "collaboration", "github", "branching", "merge"], "url": "https://docs.google.com/presentation/d/lecture5"},
    {"title": "Lecture 6: APIs and Microservices", "keywords": ["API", "REST", "microservices", "backend", "endpoints", "HTTP"], "url": "https://docs.google.com/presentation/d/lecture6"},
    {"title": "Lecture 7: Frontend Development", "keywords": ["frontend", "React", "UI", "UX", "web development", "components"], "url": "https://docs.google.com/presentation/d/lecture7"},
    {"title": "Lecture 8: Database Design", "keywords": ["database", "SQL", "MongoDB", "data modeling", "schema", "queries"], "url": "https://docs.google.com/presentation/d/lecture8"},
    {"title": "Midterm Study Guide", "keywords": ["midterm", "exam", "study", "review", "preparation", "practice"], "url": "https://docs.google.com/document/d/midterm-guide"},
    {"title": "Final Exam Information", "keywords": ["final", "exam", "deadline", "date", "time", "location"], "url": "https://docs.google.com/document/d/final-exam"},
    {"title": "Project Guidelines", "keywords": ["project", "guidelines", "requirements", "submission", "deadline", "grading"], "url": "https://docs.google.com/document/d/project-guidelines"},
    {"title": "Office Hours Schedule", "keywords": ["office hours", "TA", "help", "questions", "schedule", "availability"], "url": "https://docs.google.com/document/d/office-hours"},
]

SYLLABUS_TEXT = (
    "CS471 - Software Engineering\n\n"
    "Course Information:\n"
    "- Lectures: Monday/Wednesday 2:00-3:15 PM, Room 1201\n"
    "- Office Hours: Tuesday 3:00-5:00 PM, Room 2105\n"
    "- Final Exam: December 15, 2024, 2:00-5:00 PM\n\n"
    "Assignment Schedule:\n"
    "- Homework 1: Due September 15, 11:59 PM\n"
    "- Homework 2: Due September 29, 11:59 PM\n"
    "- Project Proposal: Due October 10, 11:59 PM\n"
    "- Midterm: October 20, in-class\n"
    "- Final Project: Due December 10, 11:59 PM\n\n"
    "Grading:\n"
    "- Homeworks: 30%\n"
    "- Midterm: 20%\n"
    "- Final Project: 40%\n"
    "- Participation: 10%"
)

async def main():
    logger.info("Starting seed process...")
    
    # Check connection first
    try:
        await check_connection()
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise
    
    users = col("users")
    presence = col("presence")
    courses = col("courses")

    logger.info(f"Clearing existing data for {DEMO_COURSE}...")
    await courses.delete_many({"courseCode": DEMO_COURSE})
    await users.delete_many({"courseCodes": DEMO_COURSE})
    await presence.delete_many({"courseCode": DEMO_COURSE})

    logger.info(f"Creating course: {DEMO_COURSE}...")
    await courses.insert_one({
        "courseCode": DEMO_COURSE,
        "courseName": "Software Engineering (Demo)",
        "syllabusText": SYLLABUS_TEXT,
        "materials": MATERIALS,
        "createdAt": datetime.now(timezone.utc),
    })
    logger.info(f"✅ Created course with {len(MATERIALS)} materials")

    now = datetime.now(timezone.utc)
    # Vary last active times (some active today, some inactive)
    active_times = [
        now - timedelta(hours=2),   # Very active
        now - timedelta(hours=5),   # Active today
        now - timedelta(hours=12),  # Active today
        now - timedelta(days=1),    # Active yesterday
        now - timedelta(days=1, hours=5),  # Active yesterday
        now - timedelta(days=2),    # Active 2 days ago
        now - timedelta(days=2, hours=8),  # Active 2 days ago
        now - timedelta(days=3),   # Less active
        now - timedelta(days=4),   # Less active
        now - timedelta(days=5),   # Inactive
        now - timedelta(days=6),   # Inactive
        now - timedelta(days=7),   # Very inactive
    ]
    
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
        # Use varied activity times
        last_active = active_times[i % len(active_times)]
        await presence.insert_one({
            "userId": res.inserted_id, 
            "courseCode": DEMO_COURSE, 
            "lastActiveAt": last_active
        })
        logger.info(f"✅ Seeded user: {name} ({', '.join(roles)})")

    logger.info(f"\n🎉 Demo data seeded successfully!")
    logger.info(f"Course: {DEMO_COURSE}")
    logger.info(f"Users: {len(USERS)}")
    logger.info(f"Materials: {len(MATERIALS)}")
    print(f"\n✅ Seed complete! {len(USERS)} users and {len(MATERIALS)} materials ready for demo.")

if __name__ == "__main__":
    asyncio.run(main())
