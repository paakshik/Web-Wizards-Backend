from fastapi import APIRouter, HTTPException
from pathlib import Path as FilePath
from app.config import  ADMIN_FILE
from app.dependencies import read_json_file
from fastapi import Depends
from fastapi.security import HTTPBearer
from app.api.auth import verify_token

security = HTTPBearer()

UPLOAD_DIR = FilePath("user_data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/me")
async def get_admin_profile(token_payload: dict = Depends(verify_token)):
    """
    Fetches the profile data of the currently logged-in admin based on their JWT token.
    """
    # 1. Security Check: Make sure it's an admin, not a student
    if token_payload.get("role") != "admin":
        raise HTTPException(status_code=403,
                            detail="Only admins can access this endpoint")
    username = token_payload.get("sub")
    admins = read_json_file(ADMIN_FILE)
    for admin in admins:
        if admin.get("username") == username:
            admin_data = admin.copy()

            admin_data.pop("password", None)

            return admin_data

    # 5. If the admin somehow has a valid token but was deleted from the database
    raise HTTPException(status_code=404, detail="Admin not found")