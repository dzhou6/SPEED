from pydantic import BaseModel, Field, HttpUrl, field_validator
from typing import List, Optional, Literal

Role = Literal["Frontend", "Backend", "Matching", "Platform"]


class ContactInfo(BaseModel):
    discord: Optional[str] = None
    linkedin: Optional[HttpUrl] = None  # validates URL format (http/https)
    email: Optional[str] = None

    @field_validator("linkedin", mode="before")
    @classmethod
    def _normalize_linkedin(cls, v):
        if v is None:
            return v
        if isinstance(v, str):
            s = v.strip()
            if not s:
                return None
            # common user input: "linkedin.com/in/..." without scheme
            if "://" not in s:
                if s.startswith("www."):
                    s = "https://" + s
                elif s.startswith("linkedin.com") or s.startswith("lnkd.in"):
                    s = "https://" + s
            return s
        return v


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


class TicketIn(BaseModel):
    courseCode: str
    question: str
