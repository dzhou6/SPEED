from __future__ import annotations
from datetime import datetime, timezone, timedelta
import asyncio
import logging
from .db import col, check_connection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEMO_COURSE = "CS471"

# Define multiple courses with detailed information
COURSES = [
    {
        "courseCode": "CS471",
        "courseName": "Software Engineering",
        "professor": "Dr. Sarah Chen",
        "location": "Room 1201, Engineering Building",
        "officeHours": "Tuesday 3:00-5:00 PM, Room 2105",
        "syllabusText": (
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
        ),
        "classPolicy": (
            "Class Policies:\n"
            "- Attendance is required. More than 3 unexcused absences may result in grade reduction.\n"
            "- All assignments must be submitted through the course portal.\n"
            "- Collaboration on homework is allowed, but all work must be your own.\n"
            "- Academic integrity is strictly enforced. Plagiarism will result in course failure.\n"
            "- Laptops/phones are allowed for note-taking only during lectures."
        ),
        "latePolicy": (
            "Late Submission Policy:\n"
            "- Assignments submitted within 24 hours of deadline: 10% penalty\n"
            "- Assignments submitted within 48 hours: 25% penalty\n"
            "- No submissions accepted after 48 hours without prior approval\n"
            "- Extensions must be requested at least 24 hours before deadline\n"
            "- Medical emergencies require documentation"
        ),
        "materials": [
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
    },
    {
        "courseCode": "CS101",
        "courseName": "Introduction to Computer Science",
        "professor": "Dr. Michael Johnson",
        "location": "Room 2101, Science Building",
        "officeHours": "Monday 2:00-4:00 PM, Room 2105",
        "syllabusText": (
            "CS101 - Introduction to Computer Science\n\n"
            "Course Information:\n"
            "- Lectures: Tuesday/Thursday 10:00-11:15 AM, Room 2101\n"
            "- Office Hours: Monday 2:00-4:00 PM, Room 2105\n"
            "- Final Exam: December 18, 2024, 10:00 AM-12:00 PM\n\n"
            "Assignment Schedule:\n"
            "- Lab 1: Due September 20, 11:59 PM\n"
            "- Lab 2: Due October 4, 11:59 PM\n"
            "- Lab 3: Due October 18, 11:59 PM\n"
            "- Midterm: October 25, in-class\n"
            "- Final Project: Due December 12, 11:59 PM\n\n"
            "Grading:\n"
            "- Labs: 40%\n"
            "- Midterm: 25%\n"
            "- Final Project: 25%\n"
            "- Participation: 10%"
        ),
        "classPolicy": (
            "Class Policies:\n"
            "- Regular attendance is expected. Missing more than 4 classes may affect your grade.\n"
            "- Labs must be completed individually unless otherwise specified.\n"
            "- Code must be well-commented and follow style guidelines.\n"
            "- Cheating or copying code will result in a zero and possible course failure.\n"
            "- Respectful behavior is required in all class interactions."
        ),
        "latePolicy": (
            "Late Submission Policy:\n"
            "- Labs submitted up to 1 day late: 15% penalty\n"
            "- Labs submitted 1-2 days late: 30% penalty\n"
            "- No credit after 2 days without approved extension\n"
            "- Extensions require email request 48 hours before deadline"
        ),
        "materials": [
            {"title": "Lecture 1: What is Computer Science?", "keywords": ["introduction", "computer science", "programming", "basics"], "url": "https://docs.google.com/presentation/d/cs101-lecture1"},
            {"title": "Lecture 2: Programming Basics", "keywords": ["programming", "variables", "data types", "syntax"], "url": "https://docs.google.com/presentation/d/cs101-lecture2"},
            {"title": "Lecture 3: Control Structures", "keywords": ["if", "loops", "conditionals", "control flow"], "url": "https://docs.google.com/presentation/d/cs101-lecture3"},
            {"title": "Lab 1 Instructions", "keywords": ["lab", "assignment", "instructions", "submission"], "url": "https://docs.google.com/document/d/cs101-lab1"},
            {"title": "Midterm Review", "keywords": ["midterm", "review", "study", "practice"], "url": "https://docs.google.com/document/d/cs101-midterm-review"},
        ]
    },
    {
        "courseCode": "MATH200",
        "courseName": "Calculus II",
        "professor": "Dr. Emily Rodriguez",
        "location": "Room 3101, Math Building",
        "officeHours": "Thursday 1:00-3:00 PM, Room 3105",
        "syllabusText": (
            "MATH200 - Calculus II\n\n"
            "Course Information:\n"
            "- Lectures: Monday/Wednesday/Friday 9:00-9:50 AM, Room 3101\n"
            "- Office Hours: Thursday 1:00-3:00 PM, Room 3105\n"
            "- Final Exam: December 20, 2024, 8:00-10:00 AM\n\n"
            "Assignment Schedule:\n"
            "- Homework 1: Due September 18, 11:59 PM\n"
            "- Homework 2: Due September 25, 11:59 PM\n"
            "- Homework 3: Due October 2, 11:59 PM\n"
            "- Midterm 1: October 9, in-class\n"
            "- Midterm 2: November 13, in-class\n"
            "- Final Exam: December 20, 8:00-10:00 AM\n\n"
            "Grading:\n"
            "- Homeworks: 20%\n"
            "- Midterm 1: 25%\n"
            "- Midterm 2: 25%\n"
            "- Final Exam: 30%"
        ),
        "classPolicy": (
            "Class Policies:\n"
            "- Attendance is strongly recommended. Material builds on previous lectures.\n"
            "- Calculators are allowed for homework but not exams.\n"
            "- Show all work for full credit on assignments and exams.\n"
            "- Study groups are encouraged, but homework must be written independently.\n"
            "- Questions are welcome during class and office hours."
        ),
        "latePolicy": (
            "Late Submission Policy:\n"
            "- Homework accepted up to 2 days late with 20% penalty per day\n"
            "- No credit after 2 days without prior arrangement\n"
            "- Extensions must be requested via email before the deadline\n"
            "- Medical emergencies require documentation"
        ),
        "materials": [
            {"title": "Chapter 1: Integration Techniques", "keywords": ["integration", "techniques", "substitution", "parts"], "url": "https://docs.google.com/presentation/d/math200-ch1"},
            {"title": "Chapter 2: Applications of Integration", "keywords": ["applications", "area", "volume", "integration"], "url": "https://docs.google.com/presentation/d/math200-ch2"},
            {"title": "Chapter 3: Sequences and Series", "keywords": ["sequences", "series", "convergence", "divergence"], "url": "https://docs.google.com/presentation/d/math200-ch3"},
            {"title": "Practice Problems Set 1", "keywords": ["practice", "problems", "homework", "exercises"], "url": "https://docs.google.com/document/d/math200-practice1"},
            {"title": "Midterm 1 Study Guide", "keywords": ["midterm", "study", "guide", "review"], "url": "https://docs.google.com/document/d/math200-midterm1"},
        ]
    },
    {
        "courseCode": "CS330",
        "courseName": "Data Structures and Algorithms",
        "professor": "Dr. James Park",
        "location": "Room 2201, Engineering Building",
        "officeHours": "Wednesday 4:00-6:00 PM, Room 2205",
        "syllabusText": (
            "CS330 - Data Structures and Algorithms\n\n"
            "Course Information:\n"
            "- Lectures: Tuesday/Thursday 2:00-3:15 PM, Room 2201\n"
            "- Office Hours: Wednesday 4:00-6:00 PM, Room 2205\n"
            "- Final Exam: December 17, 2024, 2:00-5:00 PM\n\n"
            "Assignment Schedule:\n"
            "- Programming Assignment 1: Due September 22, 11:59 PM\n"
            "- Programming Assignment 2: Due October 6, 11:59 PM\n"
            "- Programming Assignment 3: Due October 20, 11:59 PM\n"
            "- Midterm: October 27, in-class\n"
            "- Final Project: Due December 15, 11:59 PM\n\n"
            "Grading:\n"
            "- Programming Assignments: 35%\n"
            "- Midterm: 25%\n"
            "- Final Project: 30%\n"
            "- Participation: 10%"
        ),
        "classPolicy": (
            "Class Policies:\n"
            "- Attendance is required. Participation in discussions is part of your grade.\n"
            "- All code must be submitted through the course portal with proper documentation.\n"
            "- Collaboration on concepts is encouraged, but code must be written independently.\n"
            "- Academic dishonesty will result in course failure and reporting to the dean.\n"
            "- Laptops are required for in-class coding exercises."
        ),
        "latePolicy": (
            "Late Submission Policy:\n"
            "- Assignments submitted within 12 hours: 5% penalty\n"
            "- Assignments submitted within 24 hours: 15% penalty\n"
            "- Assignments submitted within 48 hours: 30% penalty\n"
            "- No submissions accepted after 48 hours\n"
            "- Extensions require 48-hour advance notice and valid reason"
        ),
        "materials": [
            {"title": "Lecture 1: Arrays and Linked Lists", "keywords": ["arrays", "linked lists", "data structures", "basics"], "url": "https://docs.google.com/presentation/d/cs330-lecture1"},
            {"title": "Lecture 2: Stacks and Queues", "keywords": ["stacks", "queues", "ADT", "abstract data types"], "url": "https://docs.google.com/presentation/d/cs330-lecture2"},
            {"title": "Lecture 3: Trees and Binary Search Trees", "keywords": ["trees", "BST", "binary search", "traversal"], "url": "https://docs.google.com/presentation/d/cs330-lecture3"},
            {"title": "Lecture 4: Hash Tables", "keywords": ["hash", "hash tables", "collision", "hashing"], "url": "https://docs.google.com/presentation/d/cs330-lecture4"},
            {"title": "Lecture 5: Sorting Algorithms", "keywords": ["sorting", "algorithms", "quicksort", "mergesort"], "url": "https://docs.google.com/presentation/d/cs330-lecture5"},
            {"title": "Programming Assignment 1: Linked List Implementation", "keywords": ["assignment", "linked list", "programming", "implementation"], "url": "https://docs.google.com/document/d/cs330-pa1"},
            {"title": "Midterm Review", "keywords": ["midterm", "review", "study", "algorithms"], "url": "https://docs.google.com/document/d/cs330-midterm-review"},
        ]
    },
]

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

    # Clear all demo data
    logger.info("Clearing existing demo data...")
    for course in COURSES:
        await courses.delete_many({"courseCode": course["courseCode"]})
        await users.delete_many({"courseCodes": course["courseCode"]})
        await presence.delete_many({"courseCode": course["courseCode"]})

    # Create all courses
    for course_data in COURSES:
        logger.info(f"Creating course: {course_data['courseCode']}...")
        await courses.insert_one({
            "courseCode": course_data["courseCode"],
            "courseName": course_data["courseName"],
            "professor": course_data.get("professor"),
            "location": course_data.get("location"),
            "officeHours": course_data.get("officeHours"),
            "syllabusText": course_data["syllabusText"],
            "classPolicy": course_data.get("classPolicy"),
            "latePolicy": course_data.get("latePolicy"),
            "materials": course_data["materials"],
            "createdAt": datetime.now(timezone.utc),
        })
        logger.info(f"Created course {course_data['courseCode']} with {len(course_data['materials'])} materials")

    # Create users for CS471 (the main demo course)
    now = datetime.now(timezone.utc)
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
            "courseCodes": [DEMO_COURSE],  # Users only in CS471 for now
            "rolePrefs": roles,
            "skills": skills,
            "availability": avail,
            "goals": "Study + accountability",
            "createdAt": now,
        })
        last_active = active_times[i % len(active_times)]
        await presence.insert_one({
            "userId": res.inserted_id, 
            "courseCode": DEMO_COURSE, 
            "lastActiveAt": last_active
        })
        logger.info(f"Seeded user: {name} ({', '.join(roles)})")

    logger.info(f"\nDemo data seeded successfully!")
    logger.info(f"Courses created: {', '.join([c['courseCode'] for c in COURSES])}")
    logger.info(f"Users: {len(USERS)} (in {DEMO_COURSE})")
    print(f"\nSeed complete! {len(COURSES)} courses created. {len(USERS)} users in {DEMO_COURSE}.")

if __name__ == "__main__":
    asyncio.run(main())
