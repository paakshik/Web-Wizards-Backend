from fastapi import APIRouter, HTTPException
from fastapi import Depends
from fastapi.security import HTTPBearer
from app.api.auth import verify_token
from sqlmodel import Session, select
from app.model import Student
from app.database import get_session

security = HTTPBearer()

router = APIRouter(prefix="/student", tags=["Student"])

@router.get("/me")
async def get_student_profile(
    token_payload: dict = Depends(verify_token),
    session: Session = Depends(get_session)
):
    """
    Fetches the profile data of the currently logged-in student based on their JWT token.
    """
    # 1. Security Check: Make sure it's a student, not an admin
    if token_payload.get("role") != "student":
        raise HTTPException(status_code=403,
                            detail="Only students can access this endpoint")

    # 2. Extract the username from the token payload (which we saved as 'sub' during login)
    username = token_payload.get("sub")

    # 3. Read the students database
    student = session.exec(
        select(Student).where(Student.username == username)
    ).first()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    return {
        "username": student.username,
        "college_email": student.college_email,
        "sch_id": student.sch_id,
        "profile_pic": student.profile_pic
    }