from fastapi import APIRouter, Depends, HTTPException,Form,File,UploadFile
from app.config import logger,sentry_sdk
from datetime import date
from app.cloudinary_helper import upload_file
import uuid
from typing import Dict
from sqlmodel import Session, select
from app.api.auth import verify_token
from app.model import Complaint, ComplaintRequest
from app.database import get_session
from  typing import Optional
router = APIRouter(prefix="/complaints", tags=["Complaints"])


@router.post("/complaint/raise", status_code=201)
async def raise_complaint(
        title: str = Form(...),
        description: str = Form(...),
        department: str = Form(...),
        phone_number: str = Form(...),
        document: UploadFile = File(...),
        token_payload: dict = Depends(verify_token),
        session: Session = Depends(get_session)
) -> Dict[str, str]:

    """Only authenticated students can raise a complaint."""
    if token_payload.get("role") != "student":
        raise HTTPException(status_code=403, detail="Only students can raise complaints")

    username = token_payload.get("sub")
    logger.info(f"Student {username} raising complaint: {title}")
    unique_id = str(uuid.uuid4())

    doc_url = await upload_file(
        file=document,
        folder="campusresolve/complaints",
        public_id=f"{unique_id}_document"
    )

    new_complaint = Complaint(
        id=unique_id,
        student_username=username,
        title=title,
        description=description,
        complaint_document=doc_url,  # permanent Cloudinary URL
        status="open",
        created_at=str(date.today()),
        department=department,
        phone_number=phone_number,
    )
    session.add(new_complaint)
    session.commit()

    return {"message": "Complaint raised successfully", "complaint_id": unique_id}


@router.get("/student/my-complaints")
async def get_student_complaints(
    token_payload: dict = Depends(verify_token),
    session: Session = Depends(get_session)
):
    if token_payload.get("role") != "student":
        raise HTTPException(status_code=403, detail="Unauthorized")
    username = token_payload.get("sub")
    complaints = session.exec(
        select(Complaint).where(Complaint.student_username == username)
    ).all()
    return complaints

@router.get("/admin/my-complaints")
async def get_admin_complaints(
    department: Optional[str] = None,
    token_payload: dict = Depends(verify_token),
    session: Session = Depends(get_session)
):
    if token_payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Unauthorized")
    query = select(Complaint)
    if department:
        query = query.where(Complaint.department == department)

    return session.exec(query).all()


@router.get("/complaint/admin/stats")
async def get_admin_complaints(
    department: Optional[str] = None,
    token_payload: dict = Depends(verify_token),
    session: Session = Depends(get_session)
):
    """
    Returns counts of complaints at each stage.
    Filterable by department using a query parameter.
    """
    if token_payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Unauthorized")

    try:
        query = select(Complaint)
        if department:
            query = query.where(Complaint.department == department)
        complaints = session.exec(query).all()

        return {
            "total": len(complaints),
            "open": len([c for c in complaints if c.status == "open"]),
            "in_progress": len([c for c in complaints if c.status == "in_progress"]),
            "resolved": len([c for c in complaints if c.status == "resolved"]),
            "closed": len([c for c in complaints if c.status == "closed"]),
            "filtered_by_department": department or "All"
        }

    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=500, detail="Error calculating statistics")


@router.get("/complaint/student/stats")
async def get_student_stats(
    token_payload: dict = Depends(verify_token),
    session: Session = Depends(get_session)
):
    """
    Returns counts of complaints at each stage.
    """
    # Only Admins should see the full dashboard stats
    if token_payload.get("role") != "student":
        raise HTTPException(status_code=403, detail="Unauthorized")

    try:
        username = token_payload.get("sub")
        complaints = session.exec(
            select(Complaint).where(Complaint.student_username == username)
        ).all()

        return {
            "total": len(complaints),
            "open": len([c for c in complaints if c.status == "open"]),
            "in_progress": len([c for c in complaints if c.status == "in_progress"]),
            "resolved": len([c for c in complaints if c.status == "resolved"]),
            "closed": len([c for c in complaints if c.status == "closed"]),
        }
    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=500, detail="Error calculating statistics")


@router.patch("/complaint/{complaint_id}/status")
async def update_complaint_status(
    complaint_id: str,
    status_data: str,
    token_payload: dict = Depends(verify_token),
    session: Session = Depends(get_session)
):
    """
    Updates the status of a specific complaint.
    Only accessible by administrators.
    """
    if token_payload.get("role") != "admin":
        logger.warning(
            f"Unauthorized status update attempt by {token_payload.get('sub')}")
        raise HTTPException(status_code=403,
                            detail="Unauthorized: Only admins can update status")

    valid_statuses = ["open", "in_progress", "resolved"]
    if status_data not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Allowed values are: {valid_statuses}"
        )

    complaint = session.get(Complaint, complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    complaint.status = status_data
    session.commit()

    logger.info(
        f"Admin {token_payload.get('sub')} updated complaint {complaint_id} to '{status_data}'")

    return {
        "message": f"Complaint status successfully updated to '{status_data}'",
        "complaint_id": complaint_id
    }


@router.post("/complaint/{complaint_id}/close")
async def close_complaint(
    complaint_id: str,
    closing_description: str = Form(...),
    document: UploadFile = File(...),
    token_payload: dict = Depends(verify_token),
    session: Session = Depends(get_session)
) -> Dict[str, str]:
    """
    Closes a complaint.
    Requires an admin token, a text description, and at least one document.
    """
    if token_payload.get("role") != "admin":
        logger.warning(f"Unauthorized close attempt by {token_payload.get('sub')}")
        raise HTTPException(status_code=403, detail="Only admins can close complaints")

    complaint = session.get(Complaint, complaint_id)

    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    if complaint.status == "closed":
        raise HTTPException(status_code=400, detail="Complaint is already closed")

    doc_url = await upload_file(
        file=document,
        folder="campusresolve/resolutions",
        public_id=f"{complaint_id}_resolution"
    )

    complaint.status = "closed"
    complaint.closing_description = closing_description
    complaint.closing_documents = doc_url  # permanent Cloudinary URL
    session.commit()

    logger.info(f"Admin {token_payload.get('sub')} closed complaint {complaint_id}")

    return {
        "message": "Complaint successfully closed",
        "complaint_id": complaint_id,
        "document_saved": doc_url
    }

