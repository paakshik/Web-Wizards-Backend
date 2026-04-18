from fastapi import APIRouter, HTTPException
from fastapi import Depends
from fastapi.security import HTTPBearer
from app.api.auth import verify_token
from sqlmodel import Session, select
from app.model import Admin
from app.database import get_session

security = HTTPBearer()

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/me")
async def get_admin_profile(
    token_payload: dict = Depends(verify_token),
    session: Session = Depends(get_session)
):
    """
    It does fetch the profile data of the currently logged-in admin based on their JWT
    token.
    """
    # 1. Security Check: Make sure it's an admin, not a student
    if token_payload.get("role") != "admin":
        raise HTTPException(status_code=403,
                            detail="Only admins can access this endpoint")
    username = token_payload.get("sub")
    admin = session.exec(
        select(Admin).where(Admin.username == username)
    ).first()

    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    # Return everything except the password
    return {
        "username": admin.username,
        "email": admin.email,
        "admin_id": admin.admin_id,
        "department": admin.department,
        "profile_pic": admin.profile_pic
    }