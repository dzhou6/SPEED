from pydantic import BaseModel, Field, field_validator, HttpUrl
from typing import List, Optional, Literal

Role = Literal["Frontend", "Backend", "Matching", "Platform"]

class ContactInfo(BaseModel):
    discord: Optional[str] = None
    linkedin: Optional[str] = None  # Accept string, validate URL format if provided
    
    @field_validator('linkedin')
    @classmethod
    def validate_linkedin(cls, v):
        if v is None or v == "":
            return None
        # Validate URL format using HttpUrl
        try:
            # HttpUrl will raise ValueError if invalid
            validated = HttpUrl(v)
            return str(validated)
        except Exception:
            raise ValueError("LinkedIn must be a valid URL (e.g., https://linkedin.com/in/yourprofile)")

class UserProfileIn(BaseModel):
    displayName: str
    rolePrefs: list[str]
    skills: list[str]
    availability: list[str] = []
    contact: Optional[ContactInfo] = None

class DemoAuthIn(BaseModel):
    courseCode: str
    displayName: Optional[str] = None

class DemoAuthOut(BaseModel):
    userId: str
    displayName: Optional[str] = None

class ProfileIn(BaseModel):
    courseCode: str
    displayName: Optional[str] = None
    rolePrefs: List[Role] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    availability: List[str] = Field(default_factory=list)
    goals: Optional[str] = None
    contact: Optional[ContactInfo] = None

class SwipeIn(BaseModel):
    courseCode: str
    targetUserId: str
    decision: Literal["accept", "pass"]

class HubIn(BaseModel):
    courseCode: str
    hubLink: str

class AskIn(BaseModel):
    courseCode: str
    question: str

class AskOut(BaseModel):
    layer: int
    answer: str
    links: List[str] = Field(default_factory=list)

class CourseOut(BaseModel):
    courseCode: str
    courseName: Optional[str] = None
    syllabusText: Optional[str] = None
    professor: Optional[str] = None
    location: Optional[str] = None
    classPolicy: Optional[str] = None
    latePolicy: Optional[str] = None
    officeHours: Optional[str] = None

class TicketIn(BaseModel):
    courseCode: str
    question: str
    # Some older UI versions sent userId in the body; accept it but rely on X-User-Id.
    userId: Optional[str] = None


class TicketOut(BaseModel):
    ok: bool = True
    ticketId: Optional[str] = None
    message: Optional[str] = None
