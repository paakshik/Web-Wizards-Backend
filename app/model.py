from sqlmodel import SQLModel, Field
from typing import Optional
from pydantic import EmailStr

# ── Students ──────────────────────────────────────────────
class Student(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    college_email: str = Field(unique=True)
    sch_id: str
    password: str
    profile_pic: Optional[str] = None

# ── Admins ────────────────────────────────────────────────
class Admin(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True)
    admin_id: str
    password: str
    profile_pic: Optional[str] = None
    department: str

# ── Complaints ────────────────────────────────────────────
class Complaint(SQLModel, table=True):
    id: str = Field(primary_key=True)        # UUID string
    student_username: str = Field(index=True)
    title: str
    description: str
    complaint_document: Optional[str] = None
    status: str = Field(default="open")
    created_at: str
    department: str
    phone_number: str
    closing_description: Optional[str] = None
    closing_documents: Optional[str] = None

# ── Request schemas (not tables, just for API input) ──────
class StudentAuthRequest(SQLModel):
    username: str
    college_email: EmailStr
    password: str

class AdminAuthRequest(SQLModel):
    username: str
    email: EmailStr
    password: str

class ComplaintRequest(SQLModel):
    title: str
    description: str
    department: str
    phone_number: str
