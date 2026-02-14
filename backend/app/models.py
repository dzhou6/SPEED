from pydantic import BaseModel, Field
from typing import List, Optional, Literal

Role = Literal["Frontend", "Backend", "Matching", "Platform"]

from pydantic import BaseModel, HttpUrl
from typing import Optional

class ContactInfo(BaseModel):
    discord: Optional[str] = None
    linkedin: Optional[HttpUrl] = None  # validates URL format

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
