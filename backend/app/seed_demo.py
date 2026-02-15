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
            "CS471 - Software Engineering\n"
            "Fall 2024\n"
            "3 Credit Hours\n\n"
            
            "INSTRUCTOR INFORMATION\n"
            "Professor: Dr. Sarah Chen\n"
            "Email: schen@gmu.edu\n"
            "Office: Room 2105, Engineering Building\n"
            "Office Hours: Tuesday 3:00-5:00 PM (or by appointment)\n"
            "Phone: (703) 993-1234\n\n"
            
            "COURSE INFORMATION\n"
            "Course Code: CS471\n"
            "Course Name: Software Engineering\n"
            "Prerequisites: CS310 (Data Structures) and CS321 (Software Design)\n"
            "Lecture Time: Monday/Wednesday 2:00-3:15 PM\n"
            "Lecture Location: Room 1201, Engineering Building\n"
            "Course Website: https://cs471.gmu.edu (Blackboard)\n"
            "Textbook: 'Software Engineering: A Practitioner's Approach' by Roger Pressman, 9th Edition\n"
            "ISBN: 978-0078022128\n\n"
            
            "COURSE DESCRIPTION\n"
            "This course provides a comprehensive introduction to software engineering principles and practices. "
            "Students will learn the fundamental concepts of software development lifecycle, including requirements analysis, "
            "system design, implementation, testing, and maintenance. The course covers both traditional and agile methodologies, "
            "with emphasis on practical application through team-based projects. Topics include software process models, "
            "requirements engineering, system architecture, design patterns, testing strategies, version control, "
            "project management, and software quality assurance. Students will work in teams to develop a complete software "
            "application, applying the concepts learned throughout the semester.\n\n"
            
            "LEARNING OBJECTIVES\n"
            "Upon successful completion of this course, students will be able to:\n"
            "1. Understand and apply software engineering principles and methodologies\n"
            "2. Analyze and document software requirements using various techniques\n"
            "3. Design software systems using appropriate architectural patterns and design principles\n"
            "4. Implement software solutions following best practices and coding standards\n"
            "5. Apply testing strategies including unit, integration, and system testing\n"
            "6. Use version control systems effectively for collaborative development\n"
            "7. Work effectively in teams to develop software projects\n"
            "8. Understand project management concepts and apply them to software development\n"
            "9. Evaluate software quality and apply quality assurance techniques\n"
            "10. Communicate technical information effectively through documentation and presentations\n\n"
            
            "COURSE SCHEDULE\n"
            "Week 1 (Aug 26-30): Introduction to Software Engineering\n"
            "  - Course overview and expectations\n"
            "  - Software engineering fundamentals\n"
            "  - Software process models (Waterfall, Agile, DevOps)\n"
            "  - Reading: Chapter 1-2\n\n"
            
            "Week 2 (Sep 2-6): Requirements Engineering\n"
            "  - Requirements gathering and analysis\n"
            "  - Use cases and user stories\n"
            "  - Requirements documentation (SRS)\n"
            "  - Homework 1 assigned (Due Sep 15)\n"
            "  - Reading: Chapter 3-4\n\n"
            
            "Week 3 (Sep 9-13): System Design and Architecture\n"
            "  - Architectural design principles\n"
            "  - Design patterns (Singleton, Factory, Observer, MVC)\n"
            "  - UML diagrams (Class, Sequence, Activity)\n"
            "  - Reading: Chapter 5-6\n\n"
            
            "Week 4 (Sep 16-20): Object-Oriented Design\n"
            "  - OOP principles (Encapsulation, Inheritance, Polymorphism)\n"
            "  - Design patterns continued\n"
            "  - Code organization and structure\n"
            "  - Homework 1 due Sep 15, 11:59 PM\n"
            "  - Reading: Chapter 7\n\n"
            
            "Week 5 (Sep 23-27): Implementation and Coding Standards\n"
            "  - Coding best practices\n"
            "  - Code reviews and pair programming\n"
            "  - Documentation standards\n"
            "  - Homework 2 assigned (Due Sep 29)\n"
            "  - Reading: Chapter 8\n\n"
            
            "Week 6 (Sep 30 - Oct 4): Version Control and Collaboration\n"
            "  - Git fundamentals\n"
            "  - Branching strategies (Git Flow, GitHub Flow)\n"
            "  - Code collaboration workflows\n"
            "  - Pull requests and code review\n"
            "  - Homework 2 due Sep 29, 11:59 PM\n"
            "  - Project Proposal assigned (Due Oct 10)\n"
            "  - Reading: Chapter 9\n\n"
            
            "Week 7 (Oct 7-11): Testing and Quality Assurance\n"
            "  - Testing fundamentals\n"
            "  - Unit testing (JUnit, pytest)\n"
            "  - Integration and system testing\n"
            "  - Test-driven development (TDD)\n"
            "  - Project Proposal due Oct 10, 11:59 PM\n"
            "  - Reading: Chapter 10-11\n\n"
            
            "Week 8 (Oct 14-18): Midterm Review and Exam\n"
            "  - Review session: Oct 16\n"
            "  - Midterm Exam: Oct 20, in-class (2:00-3:15 PM)\n"
            "  - Covers Weeks 1-7 material\n"
            "  - Format: Multiple choice, short answer, design problems\n\n"
            
            "Week 9 (Oct 21-25): APIs and Web Services\n"
            "  - RESTful API design\n"
            "  - API documentation (OpenAPI/Swagger)\n"
            "  - Microservices architecture\n"
            "  - Reading: Chapter 12\n\n"
            
            "Week 10 (Oct 28 - Nov 1): Database Design and Integration\n"
            "  - Database design principles\n"
            "  - SQL and NoSQL databases\n"
            "  - ORM frameworks\n"
            "  - Data modeling\n"
            "  - Reading: Chapter 13\n\n"
            
            "Week 11 (Nov 4-8): Frontend Development\n"
            "  - Modern frontend frameworks (React, Vue)\n"
            "  - UI/UX principles\n"
            "  - State management\n"
            "  - Responsive design\n"
            "  - Reading: Chapter 14\n\n"
            
            "Week 12 (Nov 11-15): DevOps and Deployment\n"
            "  - Continuous Integration/Continuous Deployment (CI/CD)\n"
            "  - Containerization (Docker)\n"
            "  - Cloud deployment (AWS, Azure, GCP)\n"
            "  - Monitoring and logging\n"
            "  - Reading: Chapter 15\n\n"
            
            "Week 13 (Nov 18-22): Project Management\n"
            "  - Agile methodologies (Scrum, Kanban)\n"
            "  - Sprint planning and retrospectives\n"
            "  - Risk management\n"
            "  - Team communication and collaboration\n"
            "  - Reading: Chapter 16\n\n"
            
            "Week 14 (Nov 25-29): Thanksgiving Break - No Classes\n\n"
            
            "Week 15 (Dec 2-6): Software Maintenance and Evolution\n"
            "  - Maintenance types (Corrective, Adaptive, Perfective)\n"
            "  - Refactoring techniques\n"
            "  - Technical debt\n"
            "  - Final Project presentations begin\n"
            "  - Reading: Chapter 17\n\n"
            
            "Week 16 (Dec 9-13): Final Project Presentations\n"
            "  - Team presentations (Dec 9-11)\n"
            "  - Final Project submission: Dec 10, 11:59 PM\n"
            "  - Course wrap-up and review\n\n"
            
            "FINAL EXAM\n"
            "Date: December 15, 2024\n"
            "Time: 2:00-5:00 PM\n"
            "Location: Room 1201, Engineering Building\n"
            "Format: Comprehensive exam covering all course material\n"
            "Duration: 3 hours\n"
            "Allowed materials: One 8.5x11 inch double-sided cheat sheet\n\n"
            
            "ASSIGNMENTS AND GRADING\n"
            "Homework Assignments (30%)\n"
            "  - Homework 1: Requirements Analysis (10%)\n"
            "    Due: September 15, 11:59 PM\n"
            "    Submit via Blackboard\n"
            "  - Homework 2: System Design (10%)\n"
            "    Due: September 29, 11:59 PM\n"
            "    Submit via Blackboard\n"
            "  - Homework 3: Testing and QA (10%)\n"
            "    Due: November 5, 11:59 PM\n"
            "    Submit via Blackboard\n\n"
            
            "Project Proposal (5%)\n"
            "  - Due: October 10, 11:59 PM\n"
            "  - 3-5 page document describing your team's final project\n"
            "  - Include: problem statement, requirements, design overview, timeline\n"
            "  - Submit via Blackboard\n\n"
            
            "Midterm Exam (20%)\n"
            "  - Date: October 20, in-class\n"
            "  - Covers: Weeks 1-7 material\n"
            "  - Format: Multiple choice, short answer, design problems\n\n"
            
            "Final Project (40%)\n"
            "  - Team-based software development project\n"
            "  - Proposal due: October 10\n"
            "  - Progress reports: October 25, November 15\n"
            "  - Final submission: December 10, 11:59 PM\n"
            "  - Presentation: December 9-11 (during class)\n"
            "  - Deliverables:\n"
            "    * Working software application\n"
            "    * Source code repository (GitHub/GitLab)\n"
            "    * Technical documentation\n"
            "    * User manual\n"
            "    * Team presentation (15 minutes)\n"
            "  - Grading breakdown:\n"
            "    * Functionality: 40%\n"
            "    * Code quality: 20%\n"
            "    * Documentation: 20%\n"
            "    * Presentation: 10%\n"
            "    * Team collaboration: 10%\n\n"
            
            "Participation (10%)\n"
            "  - Class attendance and engagement\n"
            "  - In-class exercises and discussions\n"
            "  - Peer code reviews\n"
            "  - Office hours attendance (optional but encouraged)\n\n"
            
            "GRADING SCALE\n"
            "A: 93-100%\n"
            "A-: 90-92%\n"
            "B+: 87-89%\n"
            "B: 83-86%\n"
            "B-: 80-82%\n"
            "C+: 77-79%\n"
            "C: 73-76%\n"
            "C-: 70-72%\n"
            "D: 60-69%\n"
            "F: Below 60%\n\n"
            
            "COURSE POLICIES\n"
            "Attendance:\n"
            "  - Regular attendance is required and expected\n"
            "  - More than 3 unexcused absences may result in grade reduction\n"
            "  - Absences due to illness, family emergency, or university-sanctioned activities are excused with documentation\n"
            "  - If you miss a class, you are responsible for obtaining notes and assignments from classmates\n\n"
            
            "Assignment Submission:\n"
            "  - All assignments must be submitted through Blackboard by 11:59 PM on the due date\n"
            "  - Late submissions are subject to the late policy (see below)\n"
            "  - Technical difficulties are not an excuse for late submission - submit early to avoid issues\n"
            "  - Keep backups of all your work\n\n"
            
            "Collaboration:\n"
            "  - Homework: Collaboration on concepts and discussion is allowed, but all written work must be your own\n"
            "  - Final Project: Team collaboration is required and expected\n"
            "  - Sharing code or solutions is strictly prohibited and will result in academic dishonesty charges\n"
            "  - When in doubt, ask the instructor\n\n"
            
            "Academic Integrity:\n"
            "  - Academic integrity is strictly enforced\n"
            "  - Plagiarism, cheating, or any form of academic dishonesty will result in:\n"
            "    * Zero on the assignment/exam\n"
            "    * Course failure (F grade)\n"
            "    * Reporting to the Office of Academic Integrity\n"
            "  - All work must be original or properly cited\n"
            "  - Use of AI tools (ChatGPT, Copilot, etc.) is allowed for learning and assistance, but:\n"
            "    * You must understand and be able to explain all code you submit\n"
            "    * You must cite any AI-generated code or content\n"
            "    * Copy-pasting AI-generated code without understanding is considered plagiarism\n\n"
            
            "Classroom Conduct:\n"
            "  - Laptops/phones are allowed for note-taking and in-class exercises only\n"
            "  - No social media, games, or unrelated activities during class\n"
            "  - Respectful behavior is required at all times\n"
            "  - Questions and participation are encouraged\n"
            "  - Arrive on time and stay for the entire class period\n\n"
            
            "LATE SUBMISSION POLICY\n"
            "Homework and Assignments:\n"
            "  - Assignments submitted within 24 hours of deadline: 10% penalty\n"
            "  - Assignments submitted within 48 hours: 25% penalty\n"
            "  - No submissions accepted after 48 hours without prior approval\n"
            "  - Extensions must be requested at least 24 hours before deadline via email\n"
            "  - Extensions are granted only for valid reasons (illness, family emergency, etc.) with documentation\n"
            "  - Technical difficulties are not grounds for extension - submit early\n\n"
            
            "Final Project:\n"
            "  - Late submissions are not accepted without prior approval\n"
            "  - Extensions must be requested at least 1 week before deadline\n"
            "  - Medical emergencies require documentation\n"
            "  - Each team member is responsible for ensuring timely submission\n\n"
            
            "RESOURCES\n"
            "Required Textbook:\n"
            "  - 'Software Engineering: A Practitioner's Approach' by Roger Pressman, 9th Edition\n"
            "  - Available at the campus bookstore and online retailers\n"
            "  - Older editions are acceptable but may have different page numbers\n\n"
            
            "Course Materials:\n"
            "  - All lecture slides, assignments, and resources available on Blackboard\n"
            "  - Code examples and templates provided on course GitHub repository\n"
            "  - Additional readings and resources posted weekly\n\n"
            
            "Software and Tools:\n"
            "  - Git (version control)\n"
            "  - Python 3.9+ or Java 11+ (depending on project choice)\n"
            "  - IDE: VS Code, IntelliJ IDEA, or PyCharm (your choice)\n"
            "  - Testing frameworks: JUnit (Java) or pytest (Python)\n"
            "  - Docker (for containerization)\n"
            "  - All software is available for free download\n\n"
            
            "Office Hours and Help:\n"
            "  - Professor office hours: Tuesday 3:00-5:00 PM, Room 2105\n"
            "  - TA office hours: Thursday 2:00-4:00 PM, Room 2106\n"
            "  - Email: schen@gmu.edu (allow 24-48 hours for response)\n"
            "  - Piazza: For questions and discussions (check daily)\n"
            "  - Tutoring center: Available for additional help\n\n"
            
            "ACCOMMODATIONS\n"
            "Students with disabilities who need academic accommodations should:\n"
            "  1. Contact the Office of Disability Services (ODS) at (703) 993-2474\n"
            "  2. Provide documentation to ODS\n"
            "  3. Meet with the instructor to discuss accommodations\n"
            "  4. Request accommodations at least 2 weeks before needed\n"
            "  - All accommodations must be approved by ODS\n"
            "  - Accommodations are not retroactive\n\n"
            
            "IMPORTANT DATES\n"
            "September 15: Homework 1 due\n"
            "September 29: Homework 2 due\n"
            "October 10: Project Proposal due\n"
            "October 20: Midterm Exam\n"
            "November 5: Homework 3 due\n"
            "November 15: Final Project progress report due\n"
            "December 9-11: Final Project presentations\n"
            "December 10: Final Project submission due\n"
            "December 15: Final Exam (2:00-5:00 PM)\n\n"
            
            "CONTACT INFORMATION\n"
            "For questions about:\n"
            "  - Course content: Attend office hours or email professor\n"
            "  - Assignments: Check Blackboard first, then email\n"
            "  - Technical issues: Contact IT support or post on Piazza\n"
            "  - Personal issues: Email professor to schedule appointment\n\n"
            
            "Good luck and I look forward to working with you this semester!\n"
            "Dr. Sarah Chen\n\n"
            
            "ADDITIONAL POLICY DETAILS AND PROCEDURES\n"
            "Assignment Submission Procedures:\n"
            "  - All assignments must be submitted through the Blackboard course portal\n"
            "  - Assignments must be submitted in the format specified in the assignment instructions\n"
            "  - File naming convention: LastName_FirstName_AssignmentNumber.ext (e.g., Smith_John_HW1.pdf)\n"
            "  - Late submissions are automatically penalized according to the late policy\n"
            "  - Technical difficulties with Blackboard are not grounds for late submission - submit early\n"
            "  - Keep backup copies of all submitted work\n"
            "  - You will receive email confirmation upon successful submission\n"
            "  - If you do not receive confirmation within 24 hours, contact the instructor immediately\n"
            "  - Resubmissions are not allowed after the deadline without prior approval\n"
            "  - All submissions are timestamped automatically by Blackboard\n"
            "  - Submissions after 11:59 PM on the due date are considered late\n"
            "  - Group assignments require all group members' names in the submission\n\n"
            
            "Grading and Feedback Procedures:\n"
            "  - Grades will be posted on Blackboard within 2 weeks of submission deadline\n"
            "  - Grade disputes must be submitted in writing within 1 week of grade posting\n"
            "  - Grade disputes must include specific justification for the requested change\n"
            "  - All grade changes require instructor approval and documentation\n"
            "  - Final grades are calculated automatically based on the grading breakdown\n"
            "  - Extra credit opportunities may be announced during the semester\n"
            "  - Grades are not negotiable - focus on improving future assignments\n"
            "  - Rubrics for all assignments are available on Blackboard\n"
            "  - Feedback will be provided through Blackboard comments and annotations\n"
            "  - Office hours are available for grade discussions\n\n"
            
            "Communication Policies:\n"
            "  - All course-related communication must use official GMU email addresses\n"
            "  - Include course code (CS471) in the subject line of all emails\n"
            "  - Allow 24-48 hours for email responses during weekdays\n"
            "  - Emails sent on weekends may not be answered until Monday\n"
            "  - Use Piazza for general questions that may benefit other students\n"
            "  - Private questions should be sent via email to the instructor\n"
            "  - Check email and Piazza daily for course announcements\n"
            "  - Important announcements will also be posted on Blackboard\n"
            "  - Do not use social media or messaging apps for course communication\n"
            "  - Professional communication is expected in all interactions\n\n"
            
            "Technology Requirements and Policies:\n"
            "  - Students must have reliable internet access for online components\n"
            "  - Laptops are required for in-class coding exercises\n"
            "  - All required software must be installed and tested before assignments\n"
            "  - Technical support is available through GMU IT services\n"
            "  - Software licenses are available through GMU's software portal\n"
            "  - Cloud storage (Google Drive, OneDrive) is recommended for backups\n"
            "  - Version control (Git) is required for all programming assignments\n"
            "  - Students are responsible for maintaining their development environment\n"
            "  - Technical issues do not excuse late submissions\n"
            "  - Test your code on multiple systems before submission\n\n"
            
            "Detailed Weekly Schedule with Reading Assignments:\n"
            "Week 1 (Aug 26-30): Introduction to Software Engineering\n"
            "  - Monday Aug 26: Course introduction, syllabus review, expectations\n"
            "  - Wednesday Aug 28: Software engineering fundamentals, history, importance\n"
            "  - Reading: Pressman Chapter 1 (Introduction), Chapter 2 (Process Models)\n"
            "  - Assignment: Read syllabus thoroughly, set up development environment\n"
            "  - Due: Environment setup verification by Aug 30, 11:59 PM\n\n"
            
            "Week 2 (Sep 2-6): Requirements Engineering\n"
            "  - Monday Sep 2: Labor Day - No class (university holiday)\n"
            "  - Wednesday Sep 4: Requirements gathering techniques, stakeholder analysis\n"
            "  - Reading: Pressman Chapter 3 (Requirements Engineering), Chapter 4 (Requirements Analysis)\n"
            "  - Assignment: Homework 1 assigned - Requirements document for sample project\n"
            "  - Due: Homework 1 - September 15, 11:59 PM\n\n"
            
            "Week 3 (Sep 9-13): System Design and Architecture\n"
            "  - Monday Sep 9: Architectural design principles, system decomposition\n"
            "  - Wednesday Sep 11: Design patterns introduction, UML basics\n"
            "  - Reading: Pressman Chapter 5 (System Design), Chapter 6 (Architectural Design)\n"
            "  - Assignment: Continue working on Homework 1\n"
            "  - Lab: UML diagramming exercise (in-class, not graded)\n\n"
            
            "Week 4 (Sep 16-20): Object-Oriented Design\n"
            "  - Monday Sep 16: OOP principles deep dive, encapsulation, inheritance\n"
            "  - Wednesday Sep 18: Polymorphism, abstraction, design patterns continued\n"
            "  - Reading: Pressman Chapter 7 (Object-Oriented Design)\n"
            "  - Assignment: Homework 1 due September 15, 11:59 PM\n"
            "  - Assignment: Homework 2 assigned - System design document\n"
            "  - Due: Homework 2 - September 29, 11:59 PM\n\n"
            
            "Week 5 (Sep 23-27): Implementation and Coding Standards\n"
            "  - Monday Sep 23: Coding best practices, code organization, naming conventions\n"
            "  - Wednesday Sep 25: Code reviews, pair programming, documentation standards\n"
            "  - Reading: Pressman Chapter 8 (Implementation)\n"
            "  - Assignment: Continue working on Homework 2\n"
            "  - Lab: Code review exercise with peer feedback\n\n"
            
            "Week 6 (Sep 30 - Oct 4): Version Control and Collaboration\n"
            "  - Monday Sep 30: Git fundamentals, repository management, branching\n"
            "  - Wednesday Oct 2: Collaborative workflows, pull requests, code merging\n"
            "  - Reading: Pressman Chapter 9 (Version Control and Configuration Management)\n"
            "  - Assignment: Homework 2 due September 29, 11:59 PM\n"
            "  - Assignment: Project Proposal assigned - teams must submit by Oct 10\n"
            "  - Lab: Git workshop - create repository, practice branching and merging\n"
            "  - Due: Project Proposal - October 10, 11:59 PM\n\n"
            
            "Week 7 (Oct 7-11): Testing and Quality Assurance\n"
            "  - Monday Oct 7: Testing fundamentals, test types, test planning\n"
            "  - Wednesday Oct 9: Unit testing frameworks, integration testing strategies\n"
            "  - Reading: Pressman Chapter 10 (Testing), Chapter 11 (Quality Assurance)\n"
            "  - Assignment: Project Proposal due October 10, 11:59 PM\n"
            "  - Lab: Write unit tests for sample code, achieve 80%+ coverage\n\n"
            
            "Week 8 (Oct 14-18): Midterm Review and Exam\n"
            "  - Monday Oct 14: Comprehensive review session - all topics from Weeks 1-7\n"
            "  - Wednesday Oct 16: Practice problems, Q&A session, exam format review\n"
            "  - Midterm Exam: Friday October 20, 2:00-3:15 PM (regular class time)\n"
            "  - Exam Location: Room 1201, Engineering Building\n"
            "  - Exam Format: Multiple choice (40%), short answer (30%), design problems (30%)\n"
            "  - Exam Coverage: All material from Weeks 1-7, including readings\n"
            "  - Allowed Materials: One 8.5x11 inch double-sided cheat sheet (handwritten only)\n"
            "  - No electronic devices allowed during exam\n"
            "  - Arrive 10 minutes early for seating assignments\n\n"
            
            "Week 9 (Oct 21-25): APIs and Web Services\n"
            "  - Monday Oct 21: RESTful API design principles, HTTP methods, status codes\n"
            "  - Wednesday Oct 23: API documentation, OpenAPI/Swagger, microservices introduction\n"
            "  - Reading: Pressman Chapter 12 (Web Services and APIs)\n"
            "  - Assignment: Midterm exam returned, review solutions in class\n"
            "  - Lab: Design and document a REST API for a sample application\n\n"
            
            "Week 10 (Oct 28 - Nov 1): Database Design and Integration\n"
            "  - Monday Oct 28: Database design principles, normalization, ER diagrams\n"
            "  - Wednesday Oct 30: SQL vs NoSQL, ORM frameworks, data modeling\n"
            "  - Reading: Pressman Chapter 13 (Database Design)\n"
            "  - Assignment: Homework 3 assigned - Database design and API integration\n"
            "  - Lab: Create database schema, write queries, integrate with API\n"
            "  - Due: Homework 3 - November 5, 11:59 PM\n\n"
            
            "Week 11 (Nov 4-8): Frontend Development\n"
            "  - Monday Nov 4: Modern frontend frameworks, React/Vue introduction\n"
            "  - Wednesday Nov 6: UI/UX principles, state management, component design\n"
            "  - Reading: Pressman Chapter 14 (Frontend Development)\n"
            "  - Assignment: Homework 3 due November 5, 11:59 PM\n"
            "  - Lab: Build a simple React component, implement state management\n\n"
            
            "Week 12 (Nov 11-15): DevOps and Deployment\n"
            "  - Monday Nov 11: CI/CD pipelines, automated testing, build processes\n"
            "  - Wednesday Nov 13: Containerization with Docker, cloud deployment strategies\n"
            "  - Reading: Pressman Chapter 15 (DevOps and Deployment)\n"
            "  - Assignment: Final Project progress report due November 15, 11:59 PM\n"
            "  - Progress report must include: current status, completed features, remaining work, timeline\n"
            "  - Lab: Set up CI/CD pipeline, containerize application, deploy to cloud\n\n"
            
            "Week 13 (Nov 18-22): Project Management\n"
            "  - Monday Nov 18: Agile methodologies, Scrum framework, sprint planning\n"
            "  - Wednesday Nov 20: Kanban boards, retrospectives, risk management\n"
            "  - Reading: Pressman Chapter 16 (Project Management)\n"
            "  - Assignment: Continue working on Final Project\n"
            "  - Lab: Create project plan, set up project management tools\n\n"
            
            "Week 14 (Nov 25-29): Thanksgiving Break - No Classes\n"
            "  - Monday Nov 25: University holiday - no classes\n"
            "  - Wednesday Nov 27: University holiday - no classes\n"
            "  - Friday Nov 29: University holiday - no classes\n"
            "  - Use this time to work on Final Project\n"
            "  - Office hours will be available by appointment only\n"
            "  - Email responses may be delayed during break\n\n"
            
            "Week 15 (Dec 2-6): Software Maintenance and Evolution\n"
            "  - Monday Dec 2: Maintenance types, refactoring techniques, technical debt\n"
            "  - Wednesday Dec 4: Code quality metrics, legacy system management\n"
            "  - Reading: Pressman Chapter 17 (Software Maintenance)\n"
            "  - Assignment: Final Project presentations begin December 9\n"
            "  - Presentation schedule will be posted on Blackboard\n"
            "  - Each team has 15 minutes: 10 minutes presentation + 5 minutes Q&A\n"
            "  - Final Project submission due: December 10, 11:59 PM\n"
            "  - All deliverables must be submitted: code, documentation, presentation slides\n\n"
            
            "Week 16 (Dec 9-13): Final Project Presentations\n"
            "  - Monday Dec 9: Final Project presentations (Teams 1-4)\n"
            "  - Wednesday Dec 11: Final Project presentations (Teams 5-8)\n"
            "  - Friday Dec 13: Course wrap-up, final exam review, Q&A\n"
            "  - Final Project submission deadline: December 10, 11:59 PM (hard deadline)\n"
            "  - Late project submissions are not accepted - plan accordingly\n"
            "  - All team members must attend all presentation sessions\n"
            "  - Presentation attendance is part of participation grade\n\n"
            
            "FINAL EXAM DETAILED INFORMATION\n"
            "Date: Monday, December 15, 2024\n"
            "Time: 2:00-5:00 PM (3 hours)\n"
            "Location: Room 1201, Engineering Building (regular classroom)\n"
            "Format: Comprehensive exam covering all course material\n"
            "  - Part 1: Multiple Choice (30 questions, 45 minutes)\n"
            "  - Part 2: Short Answer (5 questions, 60 minutes)\n"
            "  - Part 3: Design Problems (2 problems, 75 minutes)\n"
            "Allowed Materials:\n"
            "  - One 8.5x11 inch double-sided cheat sheet (handwritten only)\n"
            "  - No printed materials, no electronic devices\n"
            "  - Calculator not needed and not allowed\n"
            "  - Scratch paper will be provided\n"
            "Exam Coverage:\n"
            "  - All topics from Weeks 1-16\n"
            "  - All assigned readings from Pressman textbook\n"
            "  - All lecture material and in-class discussions\n"
            "  - All homework assignments and solutions\n"
            "  - All lab exercises and code examples\n"
            "  - Final project concepts and methodologies\n"
            "Preparation Tips:\n"
            "  - Review all homework assignments and solutions\n"
            "  - Study all lecture slides and notes\n"
            "  - Review textbook chapters and key concepts\n"
            "  - Practice with sample exam questions (available on Blackboard)\n"
            "  - Create comprehensive cheat sheet with formulas and key concepts\n"
            "  - Get adequate sleep the night before\n"
            "  - Arrive 15 minutes early for seating\n"
            "  - Bring multiple pens/pencils and erasers\n"
            "  - No bathroom breaks during exam (plan accordingly)\n"
            "  - Cell phones must be turned off and stored away\n"
            "  - Academic integrity is strictly enforced - no cheating\n\n"
            
            "DETAILED GRADING BREAKDOWN AND POLICIES\n"
            "Homework Assignments (30% of total grade):\n"
            "  - Homework 1: Requirements Analysis (10% of course grade, 33.3% of homework grade)\n"
            "    * Due: September 15, 11:59 PM\n"
            "    * Weight: 3.33% of final grade\n"
            "    * Grading: Based on completeness, accuracy, clarity, formatting\n"
            "    * Late penalty: 10% per day, maximum 25% penalty\n"
            "  - Homework 2: System Design (10% of course grade, 33.3% of homework grade)\n"
            "    * Due: September 29, 11:59 PM\n"
            "    * Weight: 3.33% of final grade\n"
            "    * Grading: Based on design quality, UML diagrams, documentation\n"
            "    * Late penalty: 10% per day, maximum 25% penalty\n"
            "  - Homework 3: Testing and QA (10% of course grade, 33.3% of homework grade)\n"
            "    * Due: November 5, 11:59 PM\n"
            "    * Weight: 3.33% of final grade\n"
            "    * Grading: Based on test coverage, test quality, QA processes\n"
            "    * Late penalty: 10% per day, maximum 25% penalty\n"
            "  - All homeworks must be submitted individually unless otherwise specified\n"
            "  - Collaboration on concepts is allowed, but written work must be your own\n"
            "  - Plagiarism will result in zero on assignment and possible course failure\n\n"
            
            "Project Proposal (5% of total grade):\n"
            "  - Due: October 10, 11:59 PM\n"
            "  - Weight: 5% of final grade\n"
            "  - Format: 3-5 page document (PDF format required)\n"
            "  - Must include: Problem statement, requirements overview, design approach, timeline\n"
            "  - Grading: Based on clarity, feasibility, completeness, professionalism\n"
            "  - Late submissions not accepted - proposal is required for project approval\n"
            "  - Teams must submit one proposal per team\n"
            "  - Individual proposals required if working alone (with instructor approval)\n\n"
            
            "Midterm Exam (20% of total grade):\n"
            "  - Date: October 20, in-class (2:00-3:15 PM)\n"
            "  - Weight: 20% of final grade\n"
            "  - Format: Multiple choice, short answer, design problems\n"
            "  - Coverage: Weeks 1-7 material, Chapters 1-9 of textbook\n"
            "  - Duration: 75 minutes\n"
            "  - Allowed materials: One handwritten cheat sheet (8.5x11, double-sided)\n"
            "  - No make-up exams except for documented emergencies\n"
            "  - Exam grades posted within 1 week on Blackboard\n"
            "  - Grade disputes must be submitted within 1 week of posting\n\n"
            
            "Final Project (40% of total grade):\n"
            "  - Proposal due: October 10, 11:59 PM (5% of course grade)\n"
            "  - Progress report due: November 15, 11:59 PM (required, not graded separately)\n"
            "  - Final submission due: December 10, 11:59 PM (35% of course grade)\n"
            "  - Presentation: December 9-11 (during class, 5% of course grade)\n"
            "  - Total weight: 40% of final grade\n"
            "  - Grading breakdown:\n"
            "    * Functionality (40% of project grade): Does it work? Are features complete?\n"
            "    * Code quality (20% of project grade): Clean code, proper structure, documentation\n"
            "    * Documentation (20% of project grade): User manual, technical docs, API docs\n"
            "    * Presentation (10% of project grade): Clarity, professionalism, Q&A performance\n"
            "    * Team collaboration (10% of project grade): Peer evaluation, contribution\n"
            "  - Deliverables required:\n"
            "    * Working software application (deployed or runnable)\n"
            "    * Source code repository (GitHub/GitLab link)\n"
            "    * Technical documentation (architecture, design decisions)\n"
            "    * User manual (how to use the application)\n"
            "    * Presentation slides (PDF format)\n"
            "    * Team member contribution statement\n"
            "  - Late submissions: Not accepted without prior approval (request 1 week in advance)\n"
            "  - All team members receive the same project grade unless peer evaluation indicates otherwise\n\n"
            
            "Participation (10% of total grade):\n"
            "  - Class attendance and engagement (40% of participation grade)\n"
            "  - In-class exercises and discussions (30% of participation grade)\n"
            "  - Peer code reviews and feedback (20% of participation grade)\n"
            "  - Office hours attendance (optional but encouraged, 10% of participation grade)\n"
            "  - Participation is assessed throughout the semester\n"
            "  - More than 3 unexcused absences will result in participation grade reduction\n"
            "  - Active participation in discussions is expected and rewarded\n"
            "  - Constructive feedback to peers is valued\n\n"
            
            "GRADE CALCULATION EXAMPLE\n"
            "Example student performance:\n"
            "  - Homework 1: 85/100 (8.5% of homework grade)\n"
            "  - Homework 2: 90/100 (9.0% of homework grade)\n"
            "  - Homework 3: 88/100 (8.8% of homework grade)\n"
            "  - Homework average: (85+90+88)/3 = 87.67%\n"
            "  - Homework contribution to final: 87.67% × 30% = 26.30 points\n"
            "  - Project Proposal: 92/100\n"
            "  - Project Proposal contribution: 92% × 5% = 4.60 points\n"
            "  - Midterm Exam: 78/100\n"
            "  - Midterm contribution: 78% × 20% = 15.60 points\n"
            "  - Final Project: 88/100\n"
            "  - Final Project contribution: 88% × 40% = 35.20 points\n"
            "  - Participation: 90/100\n"
            "  - Participation contribution: 90% × 10% = 9.00 points\n"
            "  - Total: 26.30 + 4.60 + 15.60 + 35.20 + 9.00 = 90.70 points\n"
            "  - Final Grade: A- (90-92% range)\n\n"
            
            "ADDITIONAL IMPORTANT POLICIES AND PROCEDURES\n"
            "Academic Integrity Policy (Detailed):\n"
            "  - Academic integrity is the foundation of university learning\n"
            "  - All work submitted must be your own original work\n"
            "  - Plagiarism includes but is not limited to:\n"
            "    * Copying code from online sources without citation\n"
            "    * Copying assignments from other students\n"
            "    * Using AI tools to generate code without understanding and citation\n"
            "    * Submitting work done by someone else\n"
            "    * Allowing others to copy your work\n"
            "  - Consequences of academic dishonesty:\n"
            "    * First offense: Zero on assignment, mandatory meeting with instructor\n"
            "    * Second offense: Course failure (F grade), report to Office of Academic Integrity\n"
            "    * Severe cases: Immediate course failure, possible university-level sanctions\n"
            "  - When in doubt, ask the instructor before submitting\n"
            "  - Proper citation is required for all external sources\n"
            "  - Collaboration boundaries: Discuss concepts, but write code independently\n\n"
            
            "Accommodation Procedures (Detailed):\n"
            "  - Students with documented disabilities must register with ODS\n"
            "  - ODS contact: (703) 993-2474, ods@gmu.edu\n"
            "  - Accommodation letters must be provided to instructor within first 2 weeks\n"
            "  - Accommodations are not retroactive - request early\n"
            "  - Common accommodations include:\n"
            "    * Extended time on exams\n"
            "    * Alternative testing locations\n"
            "    * Note-taking assistance\n"
            "    * Accessible course materials\n"
            "  - All accommodations must be approved by ODS\n"
            "  - Instructor will work with ODS to implement approved accommodations\n"
            "  - Confidentiality of disability information is maintained\n\n"
            
            "Emergency Procedures:\n"
            "  - In case of fire alarm: Exit building immediately, meet at designated area\n"
            "  - In case of medical emergency: Call 911, then notify instructor\n"
            "  - In case of severe weather: Follow university closure procedures\n"
            "  - Check GMU website and email for class cancellation notices\n"
            "  - Make-up work will be arranged for excused absences due to emergencies\n"
            "  - Documentation required for emergency-related absences\n\n"
            
            "Technology Failure Procedures:\n"
            "  - If Blackboard is down: Contact instructor via email immediately\n"
            "  - If your computer fails: Use university computer labs or library computers\n"
            "  - Always keep backups of your work (cloud storage recommended)\n"
            "  - Technical failures do not excuse late submissions\n"
            "  - Plan ahead and submit assignments early to avoid last-minute issues\n"
            "  - IT support: (703) 993-8870, itsupport@gmu.edu\n\n"
            
            "This syllabus is subject to change with notice. All changes will be announced in class and on Blackboard.\n"
            "Last updated: August 15, 2024\n"
            "For the most current version, always check Blackboard.\n"
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
            "CS101 - Introduction to Computer Science\n"
            "Fall 2024\n"
            "3 Credit Hours\n\n"
            
            "INSTRUCTOR INFORMATION\n"
            "Professor: Dr. Michael Johnson\n"
            "Email: mjohnson@gmu.edu\n"
            "Office: Room 2105, Science Building\n"
            "Office Hours: Monday 2:00-4:00 PM (or by appointment)\n"
            "Phone: (703) 993-2345\n\n"
            
            "COURSE INFORMATION\n"
            "Course Code: CS101\n"
            "Course Name: Introduction to Computer Science\n"
            "Prerequisites: None (open to all majors)\n"
            "Lecture Time: Tuesday/Thursday 10:00-11:15 AM\n"
            "Lecture Location: Room 2101, Science Building\n"
            "Course Website: https://cs101.gmu.edu (Blackboard)\n"
            "Textbook: 'Python Programming: An Introduction to Computer Science' by John Zelle, 3rd Edition\n"
            "ISBN: 978-1590282755\n\n"
            
            "COURSE DESCRIPTION\n"
            "This course provides a comprehensive introduction to computer science and programming. "
            "Students will learn fundamental programming concepts using Python, including variables, "
            "data types, control structures, functions, and basic data structures. The course covers "
            "problem-solving techniques, algorithm design, and software development practices. "
            "Topics include programming fundamentals, conditionals and loops, functions and modules, "
            "file I/O, lists and dictionaries, object-oriented programming basics, and debugging techniques. "
            "Students will complete hands-on programming labs and a final project to demonstrate their understanding.\n\n"
            
            "LEARNING OBJECTIVES\n"
            "Upon successful completion of this course, students will be able to:\n"
            "1. Write, test, and debug Python programs\n"
            "2. Understand and use fundamental programming constructs (variables, conditionals, loops)\n"
            "3. Design and implement functions and modules\n"
            "4. Work with basic data structures (lists, dictionaries, strings)\n"
            "5. Read from and write to files\n"
            "6. Apply problem-solving strategies to programming challenges\n"
            "7. Understand basic algorithm design and complexity\n"
            "8. Use debugging tools and techniques effectively\n"
            "9. Write well-documented, readable code\n"
            "10. Work independently on programming assignments\n\n"
            
            "COURSE SCHEDULE\n"
            "Week 1 (Aug 27-31): Introduction to Programming\n"
            "  - Course overview and expectations\n"
            "  - Introduction to Python and programming environments\n"
            "  - First program: Hello World\n"
            "  - Reading: Chapter 1-2\n"
            "  - Lab 0: Environment setup (ungraded)\n\n"
            
            "Week 2 (Sep 3-7): Variables and Data Types\n"
            "  - Variables, assignment, and naming conventions\n"
            "  - Numeric data types (int, float)\n"
            "  - Strings and string operations\n"
            "  - Input and output functions\n"
            "  - Reading: Chapter 3\n"
            "  - Lab 1 assigned (Due Sep 20)\n\n"
            
            "Week 3 (Sep 10-14): Control Structures - Conditionals\n"
            "  - Boolean expressions and logical operators\n"
            "  - If, elif, else statements\n"
            "  - Nested conditionals\n"
            "  - Reading: Chapter 4\n"
            "  - Continue working on Lab 1\n\n"
            
            "Week 4 (Sep 17-21): Control Structures - Loops\n"
            "  - While loops and for loops\n"
            "  - Loop control (break, continue)\n"
            "  - Nested loops\n"
            "  - Reading: Chapter 5\n"
            "  - Lab 1 due September 20, 11:59 PM\n"
            "  - Lab 2 assigned (Due Oct 4)\n\n"
            
            "Week 5 (Sep 24-28): Functions\n"
            "  - Function definition and calling\n"
            "  - Parameters and arguments\n"
            "  - Return values\n"
            "  - Scope and local vs global variables\n"
            "  - Reading: Chapter 6\n"
            "  - Continue working on Lab 2\n\n"
            
            "Week 6 (Oct 1-5): Lists and Sequences\n"
            "  - Lists, tuples, and sequences\n"
            "  - List operations and methods\n"
            "  - List comprehensions\n"
            "  - Reading: Chapter 7\n"
            "  - Lab 2 due October 4, 11:59 PM\n"
            "  - Lab 3 assigned (Due Oct 18)\n\n"
            
            "Week 7 (Oct 8-12): Dictionaries and Sets\n"
            "  - Dictionary creation and manipulation\n"
            "  - Dictionary methods\n"
            "  - Sets and set operations\n"
            "  - Reading: Chapter 8\n"
            "  - Continue working on Lab 3\n\n"
            
            "Week 8 (Oct 15-19): Midterm Review and Exam\n"
            "  - Comprehensive review session: October 17\n"
            "  - Midterm Exam: October 25, in-class (10:00-11:15 AM)\n"
            "  - Covers Weeks 1-7 material\n"
            "  - Format: Multiple choice, short answer, programming problems\n"
            "  - Lab 3 due October 18, 11:59 PM\n\n"
            
            "Week 9 (Oct 22-26): File I/O and Exception Handling\n"
            "  - Reading from files\n"
            "  - Writing to files\n"
            "  - Exception handling (try, except, finally)\n"
            "  - Reading: Chapter 9\n"
            "  - Midterm returned, review solutions\n\n"
            
            "Week 10 (Oct 29 - Nov 2): Object-Oriented Programming Basics\n"
            "  - Classes and objects\n"
            "  - Attributes and methods\n"
            "  - Constructors (__init__)\n"
            "  - Reading: Chapter 10\n"
            "  - Final Project assigned (Due Dec 12)\n\n"
            
            "Week 11 (Nov 5-9): Advanced Topics\n"
            "  - Modules and packages\n"
            "  - Standard library overview\n"
            "  - Working with dates and times\n"
            "  - Reading: Chapter 11\n"
            "  - Continue working on Final Project\n\n"
            
            "Week 12 (Nov 12-16): Algorithm Design and Complexity\n"
            "  - Algorithm design strategies\n"
            "  - Time and space complexity basics\n"
            "  - Sorting and searching algorithms\n"
            "  - Reading: Chapter 12\n"
            "  - Final Project progress check\n\n"
            
            "Week 13 (Nov 19-23): Thanksgiving Break - No Classes\n"
            "  - Monday Nov 19: University holiday\n"
            "  - Wednesday Nov 21: University holiday\n"
            "  - Friday Nov 23: University holiday\n"
            "  - Use this time to work on Final Project\n\n"
            
            "Week 14 (Nov 26-30): Debugging and Testing\n"
            "  - Debugging techniques and tools\n"
            "  - Unit testing basics\n"
            "  - Code review and best practices\n"
            "  - Reading: Chapter 13\n"
            "  - Final Project due: December 12, 11:59 PM\n\n"
            
            "Week 15 (Dec 3-7): Final Project Presentations\n"
            "  - Project presentations: December 5-7\n"
            "  - Each student presents for 5 minutes\n"
            "  - Course wrap-up and review\n\n"
            
            "FINAL EXAM\n"
            "Date: December 18, 2024\n"
            "Time: 10:00 AM-12:00 PM\n"
            "Location: Room 2101, Science Building\n"
            "Format: Comprehensive exam covering all course material\n"
            "Duration: 2 hours\n"
            "Allowed materials: One 8.5x11 inch double-sided cheat sheet (handwritten only)\n\n"
            
            "ASSIGNMENTS AND GRADING\n"
            "Lab Assignments (40%)\n"
            "  - Lab 1: Basic Programming (10% of course grade)\n"
            "    Due: September 20, 11:59 PM\n"
            "    Submit via Blackboard\n"
            "  - Lab 2: Control Structures (10% of course grade)\n"
            "    Due: October 4, 11:59 PM\n"
            "    Submit via Blackboard\n"
            "  - Lab 3: Functions and Data Structures (10% of course grade)\n"
            "    Due: October 18, 11:59 PM\n"
            "    Submit via Blackboard\n"
            "  - Lab 4: File I/O and OOP (10% of course grade)\n"
            "    Due: November 8, 11:59 PM\n"
            "    Submit via Blackboard\n"
            "  - All labs must be completed individually\n"
            "  - Code must be well-commented and follow style guidelines\n"
            "  - Late submissions: 15% penalty per day, maximum 2 days late\n\n"
            
            "Midterm Exam (25%)\n"
            "  - Date: October 25, in-class\n"
            "  - Covers: Weeks 1-7 material\n"
            "  - Format: Multiple choice, short answer, programming problems\n"
            "  - Duration: 75 minutes\n"
            "  - Allowed materials: One handwritten cheat sheet (8.5x11, double-sided)\n\n"
            
            "Final Project (25%)\n"
            "  - Individual programming project\n"
            "  - Proposal due: November 1, 11:59 PM\n"
            "  - Final submission due: December 12, 11:59 PM\n"
            "  - Presentation: December 5-7 (during class)\n"
            "  - Deliverables:\n"
            "    * Working Python program\n"
            "    * Source code with comments\n"
            "    * User documentation\n"
            "    * 5-minute presentation\n"
            "  - Grading breakdown:\n"
            "    * Functionality: 50%\n"
            "    * Code quality: 25%\n"
            "    * Documentation: 15%\n"
            "    * Presentation: 10%\n\n"
            
            "Participation (10%)\n"
            "  - Class attendance and engagement\n"
            "  - In-class exercises\n"
            "  - Peer code reviews\n"
            "  - Office hours attendance (optional but encouraged)\n\n"
            
            "GRADING SCALE\n"
            "A: 93-100%\n"
            "A-: 90-92%\n"
            "B+: 87-89%\n"
            "B: 83-86%\n"
            "B-: 80-82%\n"
            "C+: 77-79%\n"
            "C: 73-76%\n"
            "C-: 70-72%\n"
            "D: 60-69%\n"
            "F: Below 60%\n\n"
            
            "COURSE POLICIES\n"
            "Attendance:\n"
            "  - Regular attendance is expected\n"
            "  - Missing more than 4 classes may affect your grade\n"
            "  - Absences due to illness or emergencies are excused with documentation\n"
            "  - If you miss a class, you are responsible for obtaining notes from classmates\n\n"
            
            "Assignment Submission:\n"
            "  - All assignments must be submitted through Blackboard by 11:59 PM on the due date\n"
            "  - File naming: LastName_FirstName_LabX.py\n"
            "  - Late submissions: 15% penalty per day, maximum 2 days late\n"
            "  - Technical difficulties are not an excuse - submit early\n"
            "  - Keep backups of all your work\n\n"
            
            "Academic Integrity:\n"
            "  - All work must be your own original work\n"
            "  - Copying code from online sources without citation is plagiarism\n"
            "  - Copying assignments from other students is cheating\n"
            "  - Consequences: Zero on assignment, possible course failure, report to Office of Academic Integrity\n"
            "  - When in doubt, ask the instructor\n"
            "  - Collaboration on concepts is allowed, but code must be written independently\n\n"
            
            "LATE SUBMISSION POLICY\n"
            "Labs:\n"
            "  - Labs submitted up to 1 day late: 15% penalty\n"
            "  - Labs submitted 1-2 days late: 30% penalty\n"
            "  - No credit after 2 days without approved extension\n"
            "  - Extensions require email request 48 hours before deadline\n"
            "  - Medical emergencies require documentation\n\n"
            
            "Final Project:\n"
            "  - Late submissions not accepted without prior approval\n"
            "  - Extensions must be requested at least 1 week before deadline\n"
            "  - Each day late results in 10% penalty\n\n"
            
            "RESOURCES\n"
            "Required Textbook:\n"
            "  - 'Python Programming: An Introduction to Computer Science' by John Zelle, 3rd Edition\n"
            "  - Available at campus bookstore and online retailers\n\n"
            
            "Software and Tools:\n"
            "  - Python 3.9+ (free download from python.org)\n"
            "  - IDE: VS Code, PyCharm, or IDLE (your choice)\n"
            "  - All software is available for free\n\n"
            
            "Office Hours and Help:\n"
            "  - Professor office hours: Monday 2:00-4:00 PM, Room 2105\n"
            "  - TA office hours: Wednesday 1:00-3:00 PM, Room 2106\n"
            "  - Email: mjohnson@gmu.edu (allow 24-48 hours for response)\n"
            "  - Tutoring center: Available for additional help\n\n"
            
            "IMPORTANT DATES\n"
            "September 20: Lab 1 due\n"
            "October 4: Lab 2 due\n"
            "October 18: Lab 3 due\n"
            "October 25: Midterm Exam\n"
            "November 1: Final Project proposal due\n"
            "November 8: Lab 4 due\n"
            "December 5-7: Final Project presentations\n"
            "December 12: Final Project submission due\n"
            "December 18: Final Exam (10:00 AM-12:00 PM)\n\n"
            
            "This syllabus is subject to change with notice. All changes will be announced in class and on Blackboard.\n"
            "Last updated: August 15, 2024\n"
            "For the most current version, always check Blackboard.\n"
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
            "MATH200 - Calculus II\n"
            "Fall 2024\n"
            "4 Credit Hours\n\n"
            
            "INSTRUCTOR INFORMATION\n"
            "Professor: Dr. Emily Rodriguez\n"
            "Email: erodriguez@gmu.edu\n"
            "Office: Room 3105, Math Building\n"
            "Office Hours: Thursday 1:00-3:00 PM (or by appointment)\n"
            "Phone: (703) 993-3456\n\n"
            
            "COURSE INFORMATION\n"
            "Course Code: MATH200\n"
            "Course Name: Calculus II\n"
            "Prerequisites: MATH113 (Calculus I) with grade of C or better\n"
            "Lecture Time: Monday/Wednesday/Friday 9:00-9:50 AM\n"
            "Lecture Location: Room 3101, Math Building\n"
            "Course Website: https://math200.gmu.edu (Blackboard)\n"
            "Textbook: 'Calculus: Early Transcendentals' by James Stewart, 8th Edition\n"
            "ISBN: 978-1285741550\n\n"
            
            "COURSE DESCRIPTION\n"
            "This course is a continuation of Calculus I, covering advanced integration techniques, "
            "applications of integration, sequences and series, and parametric equations. Students will "
            "develop deeper understanding of calculus concepts and their applications to real-world problems. "
            "Topics include integration by parts, trigonometric substitution, partial fractions, improper "
            "integrals, applications of integration (area, volume, arc length), sequences and series, "
            "power series, Taylor series, and parametric equations. Emphasis is placed on problem-solving "
            "skills and mathematical reasoning.\n\n"
            
            "LEARNING OBJECTIVES\n"
            "Upon successful completion of this course, students will be able to:\n"
            "1. Apply various integration techniques to solve complex integrals\n"
            "2. Evaluate improper integrals and understand their convergence\n"
            "3. Use integration to find areas, volumes, and arc lengths\n"
            "4. Understand and work with sequences and series\n"
            "5. Determine convergence or divergence of series using various tests\n"
            "6. Represent functions as power series and Taylor series\n"
            "7. Work with parametric equations and polar coordinates\n"
            "8. Apply calculus concepts to solve real-world problems\n"
            "9. Communicate mathematical reasoning clearly\n"
            "10. Use technology appropriately to support mathematical understanding\n\n"
            
            "COURSE SCHEDULE\n"
            "Week 1 (Aug 26-30): Review of Integration Basics\n"
            "  - Review of fundamental integration techniques\n"
            "  - Substitution method review\n"
            "  - Reading: Chapter 5 review\n"
            "  - Homework 1 assigned (Due Sep 18)\n\n"
            
            "Week 2 (Sep 2-6): Integration Techniques - Part 1\n"
            "  - Integration by parts\n"
            "  - Trigonometric integrals\n"
            "  - Reading: Chapter 7.1-7.2\n"
            "  - Continue working on Homework 1\n\n"
            
            "Week 3 (Sep 9-13): Integration Techniques - Part 2\n"
            "  - Trigonometric substitution\n"
            "  - Partial fractions\n"
            "  - Reading: Chapter 7.3-7.4\n"
            "  - Homework 1 due September 18, 11:59 PM\n"
            "  - Homework 2 assigned (Due Sep 25)\n\n"
            
            "Week 4 (Sep 16-20): Improper Integrals\n"
            "  - Type 1 and Type 2 improper integrals\n"
            "  - Comparison test for improper integrals\n"
            "  - Reading: Chapter 7.8\n"
            "  - Continue working on Homework 2\n\n"
            
            "Week 5 (Sep 23-27): Applications of Integration\n"
            "  - Area between curves\n"
            "  - Volumes of solids of revolution\n"
            "  - Reading: Chapter 6.1-6.2\n"
            "  - Homework 2 due September 25, 11:59 PM\n"
            "  - Homework 3 assigned (Due Oct 2)\n\n"
            
            "Week 6 (Sep 30 - Oct 4): More Applications\n"
            "  - Arc length and surface area\n"
            "  - Work and force applications\n"
            "  - Reading: Chapter 6.3-6.4\n"
            "  - Continue working on Homework 3\n"
            "  - Midterm 1 review session: October 7\n\n"
            
            "Week 7 (Oct 7-11): Midterm 1\n"
            "  - Review session: October 7\n"
            "  - Midterm 1: October 9, in-class (9:00-9:50 AM)\n"
            "  - Covers: Integration techniques and applications\n"
            "  - Format: Problems requiring full solutions\n"
            "  - Homework 3 due October 2, 11:59 PM\n\n"
            
            "Week 8 (Oct 14-18): Sequences\n"
            "  - Introduction to sequences\n"
            "  - Limit of a sequence\n"
            "  - Convergence and divergence\n"
            "  - Reading: Chapter 11.1\n"
            "  - Homework 4 assigned (Due Oct 23)\n\n"
            
            "Week 9 (Oct 21-25): Series - Part 1\n"
            "  - Introduction to series\n"
            "  - Geometric series\n"
            "  - Telescoping series\n"
            "  - Reading: Chapter 11.2\n"
            "  - Homework 4 due October 23, 11:59 PM\n"
            "  - Homework 5 assigned (Due Oct 30)\n\n"
            
            "Week 10 (Oct 28 - Nov 1): Series - Part 2\n"
            "  - Integral test\n"
            "  - Comparison tests\n"
            "  - Alternating series test\n"
            "  - Reading: Chapter 11.3-11.5\n"
            "  - Continue working on Homework 5\n\n"
            
            "Week 11 (Nov 4-8): Series - Part 3\n"
            "  - Ratio test and root test\n"
            "  - Absolute and conditional convergence\n"
            "  - Reading: Chapter 11.6-11.7\n"
            "  - Homework 5 due October 30, 11:59 PM\n"
            "  - Homework 6 assigned (Due Nov 6)\n"
            "  - Midterm 2 review session: November 11\n\n"
            
            "Week 12 (Nov 11-15): Midterm 2 and Power Series\n"
            "  - Midterm 2: November 13, in-class (9:00-9:50 AM)\n"
            "  - Power series and interval of convergence\n"
            "  - Reading: Chapter 11.8\n"
            "  - Homework 6 due November 6, 11:59 PM\n"
            "  - Homework 7 assigned (Due Nov 20)\n\n"
            
            "Week 13 (Nov 18-22): Taylor Series\n"
            "  - Taylor and Maclaurin series\n"
            "  - Applications of Taylor series\n"
            "  - Reading: Chapter 11.10-11.11\n"
            "  - Homework 7 due November 20, 11:59 PM\n"
            "  - Thanksgiving break begins November 25\n\n"
            
            "Week 14 (Nov 25-29): Thanksgiving Break - No Classes\n"
            "  - Monday Nov 25: University holiday\n"
            "  - Wednesday Nov 27: University holiday\n"
            "  - Friday Nov 29: University holiday\n"
            "  - Use this time to review for final exam\n\n"
            
            "Week 15 (Dec 2-6): Parametric Equations and Review\n"
            "  - Parametric equations and curves\n"
            "  - Polar coordinates\n"
            "  - Comprehensive review for final exam\n"
            "  - Reading: Chapter 10.1-10.3\n\n"
            
            "FINAL EXAM\n"
            "Date: December 20, 2024\n"
            "Time: 8:00-10:00 AM\n"
            "Location: Room 3101, Math Building\n"
            "Format: Comprehensive exam covering all course material\n"
            "Duration: 2 hours\n"
            "Allowed materials: One 8.5x11 inch double-sided cheat sheet (handwritten only)\n"
            "Calculator: Not allowed on exams\n\n"
            
            "ASSIGNMENTS AND GRADING\n"
            "Homework Assignments (20%)\n"
            "  - 7 homework assignments throughout the semester\n"
            "  - Each homework worth approximately 2.86% of course grade\n"
            "  - Due dates: See schedule above\n"
            "  - Submit via Blackboard or in-class (as specified)\n"
            "  - Show all work for full credit\n"
            "  - Late policy: 20% penalty per day, maximum 2 days late\n"
            "  - Collaboration on homework is allowed, but work must be written independently\n\n"
            
            "Midterm 1 (25%)\n"
            "  - Date: October 9, in-class\n"
            "  - Covers: Integration techniques and applications\n"
            "  - Format: Problems requiring full solutions\n"
            "  - Duration: 50 minutes\n"
            "  - Allowed materials: One handwritten cheat sheet (8.5x11, double-sided)\n"
            "  - No calculator allowed\n\n"
            
            "Midterm 2 (25%)\n"
            "  - Date: November 13, in-class\n"
            "  - Covers: Sequences and series (Chapters 11.1-11.7)\n"
            "  - Format: Problems requiring full solutions\n"
            "  - Duration: 50 minutes\n"
            "  - Allowed materials: One handwritten cheat sheet (8.5x11, double-sided)\n"
            "  - No calculator allowed\n\n"
            
            "Final Exam (30%)\n"
            "  - Date: December 20, 8:00-10:00 AM\n"
            "  - Comprehensive exam covering all course material\n"
            "  - Format: Problems requiring full solutions\n"
            "  - Duration: 2 hours\n"
            "  - Allowed materials: One handwritten cheat sheet (8.5x11, double-sided)\n"
            "  - No calculator allowed\n"
            "  - Must pass final exam (60% or higher) to pass the course\n\n"
            
            "GRADING SCALE\n"
            "A: 93-100%\n"
            "A-: 90-92%\n"
            "B+: 87-89%\n"
            "B: 83-86%\n"
            "B-: 80-82%\n"
            "C+: 77-79%\n"
            "C: 73-76%\n"
            "C-: 70-72%\n"
            "D: 60-69%\n"
            "F: Below 60%\n\n"
            
            "COURSE POLICIES\n"
            "Attendance:\n"
            "  - Attendance is strongly recommended\n"
            "  - Material builds on previous lectures - missing class makes it difficult to catch up\n"
            "  - More than 6 unexcused absences may result in grade reduction\n"
            "  - Absences due to illness or emergencies are excused with documentation\n"
            "  - If you miss a class, you are responsible for obtaining notes from classmates\n\n"
            
            "Assignment Submission:\n"
            "  - All homework must be submitted by 11:59 PM on the due date\n"
            "  - Submit via Blackboard or bring to class (as specified)\n"
            "  - Show all work clearly for full credit\n"
            "  - Late homework: 20% penalty per day, maximum 2 days late\n"
            "  - No credit after 2 days without prior arrangement\n"
            "  - Extensions must be requested via email before the deadline\n\n"
            
            "Academic Integrity:\n"
            "  - All work must be your own original work\n"
            "  - Copying homework or exam answers is cheating\n"
            "  - Consequences: Zero on assignment/exam, possible course failure, report to Office of Academic Integrity\n"
            "  - Study groups are encouraged, but homework must be written independently\n"
            "  - When in doubt, ask the instructor\n\n"
            
            "Calculator Policy:\n"
            "  - Calculators are allowed for homework assignments\n"
            "  - Calculators are NOT allowed on midterms or final exam\n"
            "  - Show all work - answers without work will receive no credit\n"
            "  - Graphing calculators may be helpful for homework but are not required\n\n"
            
            "LATE SUBMISSION POLICY\n"
            "Homework:\n"
            "  - Homework accepted up to 2 days late with 20% penalty per day\n"
            "  - No credit after 2 days without prior arrangement\n"
            "  - Extensions must be requested via email before the deadline\n"
            "  - Medical emergencies require documentation\n"
            "  - Technical difficulties are not grounds for extension - submit early\n\n"
            
            "RESOURCES\n"
            "Required Textbook:\n"
            "  - 'Calculus: Early Transcendentals' by James Stewart, 8th Edition\n"
            "  - Available at campus bookstore and online retailers\n"
            "  - Older editions are acceptable but page numbers may differ\n\n"
            
            "Software and Tools:\n"
            "  - Graphing calculator (for homework only)\n"
            "  - Online resources: Wolfram Alpha, Desmos (for homework help)\n"
            "  - All course materials available on Blackboard\n\n"
            
            "Office Hours and Help:\n"
            "  - Professor office hours: Thursday 1:00-3:00 PM, Room 3105\n"
            "  - TA office hours: Tuesday 2:00-4:00 PM, Room 3106\n"
            "  - Email: erodriguez@gmu.edu (allow 24-48 hours for response)\n"
            "  - Math tutoring center: Available for additional help\n"
            "  - Study groups: Encouraged and can be arranged\n\n"
            
            "IMPORTANT DATES\n"
            "September 18: Homework 1 due\n"
            "September 25: Homework 2 due\n"
            "October 2: Homework 3 due\n"
            "October 9: Midterm 1\n"
            "October 23: Homework 4 due\n"
            "October 30: Homework 5 due\n"
            "November 6: Homework 6 due\n"
            "November 13: Midterm 2\n"
            "November 20: Homework 7 due\n"
            "December 20: Final Exam (8:00-10:00 AM)\n\n"
            
            "This syllabus is subject to change with notice. All changes will be announced in class and on Blackboard.\n"
            "Last updated: August 15, 2024\n"
            "For the most current version, always check Blackboard.\n"
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
            "CS330 - Data Structures and Algorithms\n"
            "Fall 2024\n"
            "3 Credit Hours\n\n"
            
            "INSTRUCTOR INFORMATION\n"
            "Professor: Dr. James Park\n"
            "Email: jpark@gmu.edu\n"
            "Office: Room 2205, Engineering Building\n"
            "Office Hours: Wednesday 4:00-6:00 PM (or by appointment)\n"
            "Phone: (703) 993-4567\n\n"
            
            "COURSE INFORMATION\n"
            "Course Code: CS330\n"
            "Course Name: Data Structures and Algorithms\n"
            "Prerequisites: CS211 (Object-Oriented Programming) and CS310 (Data Structures) with grade of C or better\n"
            "Lecture Time: Tuesday/Thursday 2:00-3:15 PM\n"
            "Lecture Location: Room 2201, Engineering Building\n"
            "Course Website: https://cs330.gmu.edu (Blackboard)\n"
            "Textbook: 'Introduction to Algorithms' by Cormen, Leiserson, Rivest, and Stein, 4th Edition\n"
            "ISBN: 978-0262046305\n\n"
            
            "COURSE DESCRIPTION\n"
            "This course provides an in-depth study of fundamental data structures and algorithms. "
            "Students will learn to analyze algorithm efficiency, implement various data structures, "
            "and apply algorithmic design techniques to solve complex problems. Topics include algorithm "
            "analysis and complexity, arrays and linked lists, stacks and queues, trees and binary search "
            "trees, hash tables, heaps and priority queues, graphs and graph algorithms, sorting and "
            "searching algorithms, dynamic programming, and greedy algorithms. Emphasis is placed on "
            "understanding time and space complexity, choosing appropriate data structures for problems, "
            "and implementing efficient algorithms.\n\n"
            
            "LEARNING OBJECTIVES\n"
            "Upon successful completion of this course, students will be able to:\n"
            "1. Analyze algorithm time and space complexity using Big-O notation\n"
            "2. Implement and use fundamental data structures (arrays, lists, stacks, queues, trees, hash tables)\n"
            "3. Design and implement efficient algorithms for common problems\n"
            "4. Apply algorithmic design techniques (divide-and-conquer, dynamic programming, greedy)\n"
            "5. Understand and implement graph algorithms (BFS, DFS, shortest paths)\n"
            "6. Compare and contrast different sorting and searching algorithms\n"
            "7. Choose appropriate data structures for specific problem requirements\n"
            "8. Write well-documented, efficient code\n"
            "9. Solve complex algorithmic problems\n"
            "10. Communicate algorithmic solutions clearly\n\n"
            
            "COURSE SCHEDULE\n"
            "Week 1 (Aug 27-31): Introduction and Algorithm Analysis\n"
            "  - Course overview and expectations\n"
            "  - Algorithm analysis and Big-O notation\n"
            "  - Time and space complexity\n"
            "  - Reading: Chapter 1-2\n"
            "  - Programming Assignment 1 assigned (Due Sep 22)\n\n"
            
            "Week 2 (Sep 3-7): Arrays and Linked Lists\n"
            "  - Dynamic arrays and resizing\n"
            "  - Singly and doubly linked lists\n"
            "  - Comparison of array vs linked list operations\n"
            "  - Reading: Chapter 3\n"
            "  - Continue working on Assignment 1\n\n"
            
            "Week 3 (Sep 10-14): Stacks and Queues\n"
            "  - Stack ADT and implementations\n"
            "  - Queue ADT and implementations\n"
            "  - Applications (expression evaluation, BFS/DFS)\n"
            "  - Reading: Chapter 4\n"
            "  - Continue working on Assignment 1\n\n"
            
            "Week 4 (Sep 17-21): Trees and Binary Search Trees\n"
            "  - Tree terminology and properties\n"
            "  - Binary trees and tree traversals\n"
            "  - Binary search trees (BST)\n"
            "  - Reading: Chapter 5\n"
            "  - Assignment 1 due September 22, 11:59 PM\n"
            "  - Assignment 2 assigned (Due Oct 6)\n\n"
            
            "Week 5 (Sep 24-28): Balanced Trees\n"
            "  - AVL trees and rotations\n"
            "  - Red-black trees (overview)\n"
            "  - Tree balancing strategies\n"
            "  - Reading: Chapter 6\n"
            "  - Continue working on Assignment 2\n\n"
            
            "Week 6 (Oct 1-5): Hash Tables\n"
            "  - Hash functions and collision resolution\n"
            "  - Chaining vs open addressing\n"
            "  - Hash table operations and analysis\n"
            "  - Reading: Chapter 7\n"
            "  - Assignment 2 due October 6, 11:59 PM\n"
            "  - Assignment 3 assigned (Due Oct 20)\n\n"
            
            "Week 7 (Oct 8-12): Heaps and Priority Queues\n"
            "  - Binary heaps (min-heap, max-heap)\n"
            "  - Heap operations (insert, delete, heapify)\n"
            "  - Priority queue implementations\n"
            "  - Reading: Chapter 8\n"
            "  - Continue working on Assignment 3\n"
            "  - Midterm review session: October 24\n\n"
            
            "Week 8 (Oct 15-19): Midterm Review and Exam\n"
            "  - Comprehensive review session: October 24\n"
            "  - Midterm Exam: October 27, in-class (2:00-3:15 PM)\n"
            "  - Covers: Weeks 1-7 material\n"
            "  - Format: Algorithm analysis, data structure questions, coding problems\n"
            "  - Assignment 3 due October 20, 11:59 PM\n\n"
            
            "Week 9 (Oct 22-26): Sorting Algorithms\n"
            "  - Comparison-based sorts (bubble, insertion, selection, merge, quick, heap)\n"
            "  - Non-comparison sorts (counting, radix, bucket)\n"
            "  - Analysis and comparison of sorting algorithms\n"
            "  - Reading: Chapter 9\n"
            "  - Final Project assigned (Due Dec 15)\n\n"
            
            "Week 10 (Oct 29 - Nov 2): Graphs - Part 1\n"
            "  - Graph representation (adjacency list, adjacency matrix)\n"
            "  - Graph traversals (BFS, DFS)\n"
            "  - Topological sort\n"
            "  - Reading: Chapter 10.1-10.3\n"
            "  - Continue working on Final Project\n\n"
            
            "Week 11 (Nov 5-9): Graphs - Part 2\n"
            "  - Shortest path algorithms (Dijkstra's, Bellman-Ford)\n"
            "  - Minimum spanning trees (Kruskal's, Prim's)\n"
            "  - Graph applications\n"
            "  - Reading: Chapter 10.4-10.5\n"
            "  - Continue working on Final Project\n\n"
            
            "Week 12 (Nov 12-16): Dynamic Programming\n"
            "  - Principles of dynamic programming\n"
            "  - Memoization vs tabulation\n"
            "  - Classic DP problems (knapsack, longest common subsequence, etc.)\n"
            "  - Reading: Chapter 11\n"
            "  - Final Project progress report due: November 15\n\n"
            
            "Week 13 (Nov 19-23): Greedy Algorithms\n"
            "  - Greedy algorithm design\n"
            "  - Activity selection, fractional knapsack\n"
            "  - Huffman coding\n"
            "  - Reading: Chapter 12\n"
            "  - Continue working on Final Project\n"
            "  - Thanksgiving break begins November 25\n\n"
            
            "Week 14 (Nov 26-30): Thanksgiving Break - No Classes\n"
            "  - Monday Nov 26: University holiday\n"
            "  - Wednesday Nov 28: University holiday\n"
            "  - Friday Nov 30: University holiday\n"
            "  - Use this time to work on Final Project\n\n"
            
            "Week 15 (Dec 3-7): Advanced Topics and Review\n"
            "  - String algorithms (KMP, Rabin-Karp)\n"
            "  - Advanced data structures overview\n"
            "  - Comprehensive review for final exam\n"
            "  - Final Project due: December 15, 11:59 PM\n\n"
            
            "FINAL EXAM\n"
            "Date: December 17, 2024\n"
            "Time: 2:00-5:00 PM\n"
            "Location: Room 2201, Engineering Building\n"
            "Format: Comprehensive exam covering all course material\n"
            "Duration: 3 hours\n"
            "Allowed materials: One 8.5x11 inch double-sided cheat sheet (handwritten only)\n"
            "No electronic devices allowed\n\n"
            
            "ASSIGNMENTS AND GRADING\n"
            "Programming Assignments (35%)\n"
            "  - Assignment 1: Linked List Implementation (11.67% of course grade)\n"
            "    Due: September 22, 11:59 PM\n"
            "    Submit via Blackboard\n"
            "  - Assignment 2: Binary Search Tree (11.67% of course grade)\n"
            "    Due: October 6, 11:59 PM\n"
            "    Submit via Blackboard\n"
            "  - Assignment 3: Hash Table Implementation (11.67% of course grade)\n"
            "    Due: October 20, 11:59 PM\n"
            "    Submit via Blackboard\n"
            "  - All assignments must be completed individually\n"
            "  - Code must be well-documented and follow style guidelines\n"
            "  - Late policy: 5% penalty per 12 hours, maximum 48 hours late\n"
            "  - No credit after 48 hours without prior approval\n\n"
            
            "Midterm Exam (25%)\n"
            "  - Date: October 27, in-class\n"
            "  - Covers: Weeks 1-7 material (data structures, algorithm analysis)\n"
            "  - Format: Algorithm analysis, data structure questions, coding problems\n"
            "  - Duration: 75 minutes\n"
            "  - Allowed materials: One handwritten cheat sheet (8.5x11, double-sided)\n"
            "  - No electronic devices allowed\n\n"
            
            "Final Project (30%)\n"
            "  - Individual or team project (teams of 2-3, with instructor approval)\n"
            "  - Proposal due: November 1, 11:59 PM\n"
            "  - Progress report due: November 15, 11:59 PM\n"
            "  - Final submission due: December 15, 11:59 PM\n"
            "  - Deliverables:\n"
            "    * Working implementation of chosen algorithm/data structure\n"
            "    * Source code with comprehensive documentation\n"
            "    * Performance analysis and comparison\n"
            "    * Written report (5-8 pages)\n"
            "  - Grading breakdown:\n"
            "    * Implementation and correctness: 40%\n"
            "    * Code quality and documentation: 25%\n"
            "    * Performance analysis: 20%\n"
            "    * Written report: 15%\n\n"
            
            "Participation (10%)\n"
            "  - Class attendance and engagement\n"
            "  - In-class exercises and discussions\n"
            "  - Peer code reviews\n"
            "  - Office hours attendance (optional but encouraged)\n\n"
            
            "GRADING SCALE\n"
            "A: 93-100%\n"
            "A-: 90-92%\n"
            "B+: 87-89%\n"
            "B: 83-86%\n"
            "B-: 80-82%\n"
            "C+: 77-79%\n"
            "C: 73-76%\n"
            "C-: 70-72%\n"
            "D: 60-69%\n"
            "F: Below 60%\n\n"
            
            "COURSE POLICIES\n"
            "Attendance:\n"
            "  - Attendance is required\n"
            "  - Participation in discussions is part of your grade\n"
            "  - More than 3 unexcused absences may result in grade reduction\n"
            "  - Absences due to illness or emergencies are excused with documentation\n"
            "  - If you miss a class, you are responsible for obtaining notes from classmates\n\n"
            
            "Assignment Submission:\n"
            "  - All code must be submitted through the course portal by 11:59 PM on the due date\n"
            "  - File naming: LastName_FirstName_AssignmentX.zip\n"
            "  - Include all source files, documentation, and test cases\n"
            "  - Late submissions: 5% penalty per 12 hours, maximum 48 hours late\n"
            "  - No credit after 48 hours without prior approval\n"
            "  - Extensions require 48-hour advance notice and valid reason\n"
            "  - Technical difficulties are not grounds for extension - submit early\n\n"
            
            "Academic Integrity:\n"
            "  - All work must be your own original work\n"
            "  - Copying code from online sources without citation is plagiarism\n"
            "  - Copying assignments from other students is cheating\n"
            "  - Consequences: Zero on assignment, course failure, report to Office of Academic Integrity\n"
            "  - Collaboration on concepts is encouraged, but code must be written independently\n"
            "  - When in doubt, ask the instructor\n"
            "  - Use of AI coding assistants (ChatGPT, Copilot) must be disclosed and cited\n\n"
            
            "Code Quality:\n"
            "  - Code must be well-commented and follow style guidelines\n"
            "  - Proper variable naming and code organization required\n"
            "  - Code that doesn't compile will receive significant penalty\n"
            "  - Test cases should be included with submissions\n"
            "  - Documentation must explain algorithm choices and complexity analysis\n\n"
            
            "LATE SUBMISSION POLICY\n"
            "Programming Assignments:\n"
            "  - Assignments submitted within 12 hours: 5% penalty\n"
            "  - Assignments submitted within 24 hours: 15% penalty\n"
            "  - Assignments submitted within 48 hours: 30% penalty\n"
            "  - No submissions accepted after 48 hours\n"
            "  - Extensions require 48-hour advance notice and valid reason\n"
            "  - Medical emergencies require documentation\n\n"
            
            "Final Project:\n"
            "  - Late submissions not accepted without prior approval\n"
            "  - Extensions must be requested at least 1 week before deadline\n"
            "  - Each day late results in 10% penalty\n"
            "  - No credit after 3 days late\n\n"
            
            "RESOURCES\n"
            "Required Textbook:\n"
            "  - 'Introduction to Algorithms' by Cormen, Leiserson, Rivest, and Stein, 4th Edition\n"
            "  - Available at campus bookstore and online retailers\n"
            "  - Older editions are acceptable but page numbers may differ\n\n"
            
            "Software and Tools:\n"
            "  - Programming language: Java, C++, or Python (your choice)\n"
            "  - IDE: IntelliJ IDEA, Eclipse, VS Code, or PyCharm (your choice)\n"
            "  - Version control: Git (required for final project)\n"
            "  - All software is available for free\n\n"
            
            "Office Hours and Help:\n"
            "  - Professor office hours: Wednesday 4:00-6:00 PM, Room 2205\n"
            "  - TA office hours: Friday 2:00-4:00 PM, Room 2206\n"
            "  - Email: jpark@gmu.edu (allow 24-48 hours for response)\n"
            "  - Piazza: For questions and discussions (check daily)\n"
            "  - Tutoring center: Available for additional help\n\n"
            
            "IMPORTANT DATES\n"
            "September 22: Programming Assignment 1 due\n"
            "October 6: Programming Assignment 2 due\n"
            "October 20: Programming Assignment 3 due\n"
            "October 27: Midterm Exam\n"
            "November 1: Final Project proposal due\n"
            "November 15: Final Project progress report due\n"
            "December 15: Final Project submission due\n"
            "December 17: Final Exam (2:00-5:00 PM)\n\n"
            
            "This syllabus is subject to change with notice. All changes will be announced in class and on Blackboard.\n"
            "Last updated: August 15, 2024\n"
            "For the most current version, always check Blackboard.\n"
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
