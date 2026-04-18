from typing import Dict
from fastapi import APIRouter, HTTPException,status,Form,UploadFile,File
from app.cloudinary_helper import upload_file
from app.config import logger, sentry_sdk
import bcrypt
from sqlmodel import Session, select
from app.model import Student, Admin, StudentAuthRequest, AdminAuthRequest
import os,shutil
import jwt
from datetime import datetime, timedelta
from fastapi import Depends
from app.config import SECRET_KEY,ALGORITHM,ACCESS_TOKEN_EXPIRE_MINUTES
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.database import get_session

security = HTTPBearer()

router = APIRouter(prefix="/auth", tags=["Authentication"])

def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(
        plain.encode("utf-8"),
        hashed.encode("utf-8")
    )

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)



def verify_token(auth: HTTPAuthorizationCredentials = Depends(security)):
    """Extract and validate JWT token from the Authorization header."""
    # HTTPBearer automatically handles the "Bearer " prefix for you!
    token = auth.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
# ============================================================================
# SIGNUP ENDPOINTS
# ============================================================================
@router.post("/signup/student", status_code=status.HTTP_201_CREATED)
async def signup_student(
    username: str = Form(...),
    college_email: str = Form(...),
    password: str = Form(...),
    sch_id: str = Form(...),
    avatar: UploadFile = File(...),
    session: Session = Depends(get_session)
) -> Dict[str, str]:

    """
    Registers a new student account in the system.

    This endpoint reads the existing student database, checks for username
    uniqueness, and appends the new student credentials to the JSON storage.
    If the username exists, a warning is logged to Sentry.

    Args:
        :param session:
        :param sch_id:
        :param avatar:
        :param password:
        :param college_email:
        :param username:
    Returns:
        Dict[str, str]: A dictionary containing a success message and the
            created username.

    Raises:
        HTTPException:
            - 400 (Bad Request): If the username is already taken.
            - 500 (Internal Server Error): If a filesystem error occurs.
    """
    logger.info(f"Attempting to register new user: {username}")

    try:
        existing = session.exec(
            select(Student).where(Student.username == username)
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Username already exists")

        existing_email = session.exec(
            select(Student).where(Student.college_email == college_email)
        ).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already registered")

        avatar_url = await upload_file(
            file=avatar,
            folder="campusresolve/avatars/students",
            public_id=f"{username}_avatar"
        )


        hashed_pwd = get_password_hash(password)
        new_student = Student(
            username=username,
            college_email=college_email,
            sch_id=sch_id,
            password=hashed_pwd,
            profile_pic=avatar_url
        )
        session.add(new_student)
        session.commit()

        logger.info(f"Successfully registered new student: {username}")
        return {"message": "Student created successfully", "username": username}

    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Critical error during student signup: {str(e)}", exc_info=True)
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/signup/admin", status_code=status.HTTP_201_CREATED)
async def signup_admin(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    id: str = Form(...),
    department: str = Form(...),
    avatar: UploadFile = File(...),
    session: Session = Depends(get_session)
) -> Dict[str, str]:
    """
    Registers a new admin account in the system.

    This endpoint reads the existing admin database, checks for username
    uniqueness, and appends the new admin credentials to the JSON storage.
    If the admin exists, a warning is logged to logger.

    Args:
        :param session:
        :param email:
        :param id:
        :param department:
        :param avatar:
        :param password:
        :param username:
    Returns:
        Dict[str, str]: A dictionary containing a success message and the
            created username.

    Raises:
        HTTPException:
            - 400 (Bad Request): If the username is already taken.
            - 500 (Internal Server Error): If a filesystem error occurs.
    """
    logger.info(f"Attempting to register new user: {username}")

    try:
        existing = session.exec(
            select(Admin).where(Admin.username == username)
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Username already exists")

        existing_email = session.exec(
            select(Admin).where(Admin.email == email)
        ).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already registered")

        avatar_url = await upload_file(
            file=avatar,
            folder="campusresolve/avatars/admins",
            public_id=f"{username}_avatar"
        )
        hashed_pwd = get_password_hash(password)
        new_admin = Admin(
            username=username,
            email=email,
            admin_id=id,
            password=hashed_pwd,
            profile_pic=avatar_url,
            department=department
        )

        session.add(new_admin)
        session.commit()

        logger.info(f"Successfully registered new admin: {username}")
        return {"message": "Admin created successfully", "username": username}

    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Critical error during admin signup: {str(e)}", exc_info=True)
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=500, detail="Internal server error")

# ============================================================================
# LOGIN ENDPOINTS
# ============================================================================

@router.post("/login/student")
async def login_user(student_data: StudentAuthRequest,
                     session: Session = Depends(get_session)) -> Dict[str, str]:
    """
    Authenticates a student against the student database.

    Iterates through the student JSON records to find a matching username, email
    and password. Unauthorized attempts are logged and sent to Sentry
    as warnings for security monitoring.

    Args:
        student_data (StudentAuthRequest): The login credentials containing
            'username', 'email'  and 'password'.

    Returns:
        Dict[str, str]: A success message, the assigned role ('student'),
            and a temporary authentication token.

    Raises:
        HTTPException:
            - 401 (Unauthorized): If credentials do not match any record.
            - 500 (Internal Server Error): If the database is unreachable.
            :param student_data:
            :param session:
    """
    logger.info(f"Login attempt for user: {student_data.username}")

    try:
        student = session.exec(
            select(Student).where(Student.username == student_data.username)
        ).first()

        if not student or not verify_password(student_data.password, student.password):
            msg = f"Failed login attempt for student: {student_data.username}"
            logger.warning(msg)
            sentry_sdk.capture_message(msg, level="warning")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Invalid credentials")

        if student.college_email != student_data.college_email:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Invalid email")

        token = create_access_token(data={"sub": student.username, "role": "student"})
        logger.info(f"Student login successful: {student_data.username}")
        return {"message": "Login successful", "role": "student", "token": token}

    except HTTPException:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=500, detail="Login processing error")


@router.post("/login/admin")
async def login_admin(
    admin_data: AdminAuthRequest,
    session: Session = Depends(get_session)
) -> Dict[str, str]:
    """
    Authenticates an administrator against the admin database.

    Verifies the admin credentials. Successful logins are logged for audit
    trails, while failed attempts are sent to Sentry as warnings to track
    potential brute-force activity.

    Args:
        admin_data (AdminAuthRequest): The admin credentials containing
            'email' and 'password'.

    Returns:
        Dict[str, str]: A success message, the assigned role ('admin'),
            and a temporary administrative token.

    Raises:
        HTTPException:
            - 401 (Unauthorized): If admin credentials are invalid.
            - 500 (Internal Server Error): If the admin database is corrupted or missing.
    """
    logger.info(f"Admin login attempt for username: {admin_data.username}")

    try:
        admin = session.exec(
            select(Admin).where(Admin.username == admin_data.username)
        ).first()

        if not admin or not verify_password(admin_data.password, admin.password):
            msg = f"Failed admin login attempt: {admin_data.username}"
            logger.warning(msg)
            sentry_sdk.capture_message(msg, level="warning")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Invalid username or password")

        if admin.email != admin_data.college_email:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Invalid username or password")

        token = create_access_token(data={"sub": admin.username, "role": "admin"})
        logger.info(f"Admin login successful: {admin_data.username}")
        return {"message": "Admin login successful", "role": "admin", "token": token}

    except HTTPException:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=500, detail="Admin login processing error")