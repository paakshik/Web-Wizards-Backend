from fastapi import APIRouter, Depends, HTTPException
from app.api.auth import verify_token  # the function above
from app.model import ComplaintRequest  # define a Pydantic model
from app.config import logger, COMPLAINT_FILE,sentry_sdk
from app.dependencies import read_json_file, write_json_file
from datetime import date
import uuid

router = APIRouter(prefix="/complaints", tags=["Complaints"])

@router.post("/complaint/raise", status_code=201)
async def raise_complaint(
    complaint: ComplaintRequest,
    token_payload: dict = Depends(verify_token)
):
    """Only authenticated students can raise a complaint."""
    # Ensure the logged-in user is a student
    if token_payload.get("role") != "student":
        raise HTTPException(status_code=403, detail="Only students can raise complaints")

    username = token_payload.get("sub")
    logger.info(f"Student {username} raising complaint: {complaint.title}")
    unique_id = str(uuid.uuid4())
    complaints = read_json_file(COMPLAINT_FILE)
    new_complaint = {
        "id": unique_id,
        "student_username": username,
        "title": complaint.title,
        "description": complaint.description,
        "status": "open",
        "created_at": str(date.today()),
        "department": complaint.department,
        "phone_number": complaint.phone_number,
    }
    complaints.append(new_complaint)
    write_json_file(COMPLAINT_FILE, complaints)

    return {"message": "Complaint raised successfully", "complaint_id": new_complaint["id"]}


@router.get("/student/my-complaints")
async def get_my_complaints(token_payload: dict = Depends(verify_token)):
    if token_payload.get("role") != "student":
        raise HTTPException(status_code=403, detail="Unauthorized")
    username = token_payload.get("sub")
    all_complaints = read_json_file(COMPLAINT_FILE)
    return [c for c in all_complaints if c.get("student_username") == username]

@router.get("/admin/my-complaints")
async def get_my_complaints(department:str,token_payload: dict = Depends(verify_token)):
    if token_payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Unauthorized")
    username = token_payload.get("sub")
    all_complaints = read_json_file(COMPLAINT_FILE)
    if department:
        all_complaints = [c for c in all_complaints if c.get("department") == department]
    return [c for c in all_complaints if c.get("student_username") == username]


@router.get("/complaint/admin/stats")
async def get_complaint_stats(
    department:str,
    token_payload: dict = Depends(verify_token)
):
    """
    Returns counts of complaints at each stage.
    Filterable by department using a query parameter.
    """
    # Only Admins should see the full dashboard stats
    if token_payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Unauthorized")

    try:
        complaints = read_json_file(COMPLAINT_FILE)

        if department:
            complaints = [c for c in complaints if c.get("department") == department]


        stats = {
            "total": len(complaints),
            "open": len([c for c in complaints if c["status"] == "open"]),
            "in_progress": len([c for c in complaints if c["status"] == "in_progress"]),
            "resolved": len([c for c in complaints if c["status"] == "resolved"]),
            "closed": len([c for c in complaints if c["status"] == "closed"]),
            "filtered_by_department": department or "All"
        }

        return stats

    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=500, detail="Error calculating statistics")


@router.get("/complaint/student/stats")
async def get_complaint_stats(
    token_payload: dict = Depends(verify_token)
):
    """
    Returns counts of complaints at each stage.
    """
    # Only Admins should see the full dashboard stats
    if token_payload.get("role") != "student":
        raise HTTPException(status_code=403, detail="Unauthorized")

    try:
        complaints = read_json_file(COMPLAINT_FILE)


        stats = {
            "total": len(complaints),
            "open": len([c for c in complaints if c["status"] == "open"]),
            "in_progress": len([c for c in complaints if c["status"] == "in_progress"]),
            "resolved": len([c for c in complaints if c["status"] == "resolved"]),
            "closed": len([c for c in complaints if c["status"] == "closed"]),
            "filtered_by_department": "All"
        }

        return stats

    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=500, detail="Error calculating statistics")


@router.patch("/complaint/{complaint_id}/status")
async def update_complaint_status(
        complaint_id: str,
        status_data: str,
        token_payload: dict = Depends(verify_token)
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

    # 3. Read the database
    complaints = read_json_file(COMPLAINT_FILE)

    # 4. Find the complaint and update it
    complaint_found = False
    for complaint in complaints:
        if complaint.get("id") == complaint_id:
            complaint["status"] = status_data
            complaint_found = True
            break

    if not complaint_found:
        raise HTTPException(status_code=404, detail="Complaint ID not found")

    # 6. Save the updated list back to the JSON file
    write_json_file(COMPLAINT_FILE, complaints)

    logger.info(
        f"Admin {token_payload.get('sub')} updated complaint {complaint_id} to '{status_data}'")

    return {
        "message": f"Complaint status successfully updated to '{status_data}'",
        "complaint_id": complaint_id
    }

