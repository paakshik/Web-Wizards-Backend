from fastapi import APIRouter, HTTPException
from pathlib import Path as FilePath
from app.config import  STUDENTS_FILE
from app.dependencies import read_json_file
from fastapi import Depends
from fastapi.security import HTTPBearer
from app.api.auth import verify_token

security = HTTPBearer()

UPLOAD_DIR = FilePath("user_data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
router = APIRouter(prefix="/student", tags=["Student"])

@router.get("/me")
async def get_student_profile(token_payload: dict = Depends(verify_token)):
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
    users = read_json_file(STUDENTS_FILE)

    # 4. Find the specific student
    for user in users:
        if user.get("username") == username:
            user_data = user.copy()

            user_data.pop("password", None)

            # Return the safe user data
            return user_data
    raise HTTPException(status_code=404, detail="Student not found")