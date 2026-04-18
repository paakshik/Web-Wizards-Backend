import resend
from app.config import RESEND_API_KEY, RESEND_FROM_EMAIL, logger

resend.api_key = RESEND_API_KEY
def send_complaint_raised_email(admin_email: str, admin_username: str,
                                complaint_title: str, complaint_id: str,
                                department: str, student_username: str, ) -> None:
    """
    Sends email to dept admin when a new complaint is raised.
    """
    try:
        resend.Emails.send({
            "from": RESEND_FROM_EMAIL,
            "to": "paakshik862@gmail.com",
            "subject": f"[CampusResolve] New Complaint: {complaint_title}",
            "html": f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #e53e3e;">New Complaint Filed</h2>
                    <p>Hello <strong>{admin_username}</strong>,</p>
                    <p>A new complaint has been raised in your department that requires your attention.</p>

                    <div style="background: #f7f7f7; padding: 16px; border-radius: 8px; margin: 16px 0;">
                        <p><strong>Complaint ID:</strong> {complaint_id}</p>
                        <p><strong>Title:</strong> {complaint_title}</p>
                        <p><strong>Department:</strong> {department}</p>
                        <p><strong>Raised by:</strong> {student_username}</p>
                        <p><strong>Status:</strong> Open</p>
                    </div>

                    <p>Please log in to CampusResolve to review and take action.</p>
                    <p style="color: #888; font-size: 12px;">This is an automated message from CampusResolve.</p>
                </div>
            """
        })
        logger.info(f"Complaint notification email sent to admin: {admin_email}")
    except Exception as e:
        # Don't crash the request if email fails — just log it
        logger.error(f"Failed to send complaint email to admin {admin_email}: {str(e)}")


def send_status_update_email(student_email: str, student_username: str,
                             complaint_title: str, complaint_id: str, new_status: str):
    """
    Sends email to student when their complaint status is updated.
    """
    # Human readable status labels
    status_labels = {
        "open": "Open",
        "in_progress": "In Progress",
        "resolved": "Resolved",
        "closed": "Closed"
    }

    status_colors = {
        "open": "#e53e3e",
        "in_progress": "#d69e2e",
        "resolved": "#38a169",
        "closed": "#718096"
    }

    label = status_labels.get(new_status, new_status)
    color = status_colors.get(new_status, "#718096")

    try:
        resend.Emails.send({
            "from": RESEND_FROM_EMAIL,
            "to": "paakshik862@gmail.com",
            "subject": f"[CampusResolve] Complaint Update: {complaint_title}",
            "html": f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #3182ce;">Complaint Status Updated</h2>
                    <p>Hello <strong>{student_username}</strong>,</p>
                    <p>Your complaint status has been updated.</p>

                    <div style="background: #f7f7f7; padding: 16px; border-radius: 8px; margin: 16px 0;">
                        <p><strong>Complaint ID:</strong> {complaint_id}</p>
                        <p><strong>Title:</strong> {complaint_title}</p>
                        <p><strong>New Status:</strong> 
                            <span style="color: {color}; font-weight: bold;">{label}</span>
                        </p>
                    </div>

                    <p>Log in to CampusResolve to view full details.</p>
                    <p style="color: #888; font-size: 12px;">This is an automated message from CampusResolve.</p>
                </div>
            """
        })
        logger.info(f"Status update email sent to student: {student_email}")
    except Exception as e:
        logger.error(
            f"Failed to send status email to student {student_email}: {str(e)}")


def send_complaint_closed_email(student_email: str, student_username: str,
                                complaint_title: str, complaint_id: str,
                                closing_description: str):
    """
    Sends email to student when their complaint is officially closed.
    """
    try:
        resend.Emails.send({
            "from": RESEND_FROM_EMAIL,
            "to": "paakshik862@gmail.com",
            "subject": f"[CampusResolve] Complaint Closed: {complaint_title}",
            "html": f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #38a169;">Complaint Closed</h2>
                    <p>Hello <strong>{student_username}</strong>,</p>
                    <p>Your complaint has been officially closed by the admin.</p>

                    <div style="background: #f7f7f7; padding: 16px; border-radius: 8px; margin: 16px 0;">
                        <p><strong>Complaint ID:</strong> {complaint_id}</p>
                        <p><strong>Title:</strong> {complaint_title}</p>
                        <p><strong>Resolution Note:</strong> {closing_description}</p>
                        <p><strong>Status:</strong> <span style="color: #718096; font-weight: bold;">Closed</span></p>
                    </div>

                    <p>If you feel the issue was not resolved, please raise a new complaint.</p>
                    <p style="color: #888; font-size: 12px;">This is an automated message from CampusResolve.</p>
                </div>
            """
        })
        logger.info(f"Complaint closed email sent to student: {student_email}")
    except Exception as e:
        logger.error(
            f"Failed to send closed email to student {student_email}: {str(e)}")