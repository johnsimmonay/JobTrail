# app/schemas.py
from datetime import datetime, date
from enum import Enum
from pydantic import BaseModel, EmailStr, HttpUrl, Field, ConfigDict, field_validator

class ApplicationStatus(str, Enum):
    APPLIED = "applied"
    INTERVIEW = "interview"
    OFFER = "offer"
    REJECTED = "rejected"

class JobPlatform(str, Enum):
    LINKEDIN = "linkedin"
    JOBSTREET = "jobstreet"
    INDEED = "indeed"
    KALIBRR = "kalibrr"
    COMPANY_WEBSITE = "company_website"
    OTHER = "other"

class ApplicationCreate(BaseModel):
    company_name: str = Field(min_length=1, max_length=100)
    job_title: str = Field(min_length=1, max_length=100)
    applied_date: date = Field(default_factory=date.today)
    status: ApplicationStatus = ApplicationStatus.APPLIED
    source: JobPlatform | None = None
    job_url: HttpUrl | None = None
    notes: str | None = None
    location: str | None = None

class ApplicationRead(ApplicationCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime

class ApplicationUpdate(BaseModel):
    company_name: str = Field(min_length=1, max_length=100, default=None)
    job_title: str = Field(min_length=1, max_length=100, default=None)
    applied_date: date = Field(default=None)
    status: ApplicationStatus = Field(default=None)
    source: JobPlatform | None = None
    job_url: HttpUrl | None = None
    notes: str | None = None
    location: str | None = None

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    @field_validator("email")
    @classmethod
    def lowercase_email(cls, v: str) -> str:
        return v.lower()

class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: EmailStr
    created_at: datetime