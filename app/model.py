from pydantic import BaseModel,EmailStr,Field
from typing import Optional, List
from datetime import date

class StudentAuthRequest(BaseModel):
    username: str
    college_email: EmailStr
    password: str


class AdminAuthRequest(BaseModel):
    username: str
    college_email: EmailStr
    password: str

class ComplaintRequest(BaseModel):
    student_username: str
    title: str
    description: str
    department: str
    phone_number: str= Field(..., min_length=10, max_length=15)
