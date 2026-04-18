from typing import Dict
from fastapi import APIRouter, HTTPException,status,Form,UploadFile,File
from app.model import StudentAuthRequest, AdminAuthRequest
from pathlib import Path as FilePath
from app.config import logger, sentry_sdk, STUDENTS_FILE, ADMIN_FILE
from app.dependencies import read_json_file, write_json_file
import bcrypt
import os,shutil
import jwt
from datetime import datetime, timedelta
from fastapi import Depends, Header
from app.config import SECRET_KEY,ALGORITHM,ACCESS_TOKEN_EXPIRE_MINUTES
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


security = HTTPBearer()

UPLOAD_DIR = FilePath("user_data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
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
async def signup_student(username: str = Form(...),
    college_email: str = Form(...),
    password: str = Form(...),
    sch_id: str = Form(...),
    avatar: UploadFile = File(...)) -> Dict[str, str]:
    """
    Registers a new student account in the system.

    This endpoint reads the existing student database, checks for username
    uniqueness, and appends the new student credentials to the JSON storage.
    If the username exists, a warning is logged to Sentry.

    Args:
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
        users = read_json_file(STUDENTS_FILE)

        if any(user.get("username") == username and user.get("sch_id") ==
               sch_id and user.get("college_email") ==
               college_email for user in users):
            msg = f"Signup failed: Username '{username}' already exists."
            logger.warning(msg)
            raise HTTPException(status_code=400, detail="Username already exists")

        file_ext = os.path.splitext(avatar.filename)[1]
        file_name = f"{username}_avatar{file_ext}"
        file_path = UPLOAD_DIR / file_name


        with file_path.open("wb") as buffer:
            shutil.copyfileobj(avatar.file, buffer)

        hashed_pwd = get_password_hash(password)
        new_user = {
            "username": username,
            "college_email": college_email,
            "sch_id": sch_id,
            "password": hashed_pwd,
            "profile_pic": f"/uploads/{file_name}"
        }
        users.append(new_user)
        write_json_file(STUDENTS_FILE, users)

        logger.info(f"Successfully registered new user: {username}")
        return {"message": "User created successfully",
                "username": username}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Critical error during student signup: {str(e)}", exc_info=True)
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/signup/admin", status_code=status.HTTP_201_CREATED)
async def signup_admin(username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    id: str = Form(...),
    department: str = Form(...),
    avatar: UploadFile = File(...)) -> Dict[str, str]:
    """
    Registers a new admin account in the system.

    This endpoint reads the existing admin database, checks for username
    uniqueness, and appends the new admin credentials to the JSON storage.
    If the admin exists, a warning is logged to logger.

    Args:
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
        users = read_json_file(ADMIN_FILE)

        if any(user.get("username") == username and user.get("id") ==
               id and user.get("email") ==
               email for user in users):
            msg = f"Signup failed: Username '{username}' already exists."
            logger.warning(msg)
            raise HTTPException(status_code=400, detail="Username already exists")

        file_ext = os.path.splitext(avatar.filename)[1]
        file_name = f"{username}_avatar{file_ext}"
        file_path = UPLOAD_DIR / file_name


        with file_path.open("wb") as buffer:
            shutil.copyfileobj(avatar.file, buffer)

        hashed_pwd = get_password_hash(password)
        new_user = {
            "username": username,
            "email": email,
            "id": id,
            "password": hashed_pwd,
            "profile_pic": f"/uploads/{file_name}",
            "department": department,
        }
        users.append(new_user)
        write_json_file(ADMIN_FILE, users)

        logger.info(f"Successfully registered new admin: {username}")
        return {"message": "User created successfully",
                "username": username}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Critical error during admin signup: {str(e)}", exc_info=True)
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=500, detail="Internal server error")

# ============================================================================
# LOGIN ENDPOINTS
# ============================================================================

@router.post("/login/student")
async def login_user(student_data: StudentAuthRequest) -> Dict[str, str]:
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
    """
    logger.info(f"Login attempt for user: {student_data.username}")

    try:
        users = read_json_file(STUDENTS_FILE)

        for user in users:
            if user.get("username") == student_data.username and verify_password(student_data.password, user.get("password")) and user.get("college_email") == student_data.college_email:
                logger.info(f"User login successful: {student_data.username}")
                token = create_access_token(
                    data={"sub": student_data.username, "role": "student"})
                return {
                    "message": "User login successful",
                    "role": "student",
                    "token": token,
                }

        msg = f"Failed login attempt for user: {student_data.username} (Invalid credentials)"
        logger.warning(msg)
        sentry_sdk.capture_message(msg, level="warning")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    except HTTPException:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=500, detail="Login processing error")


@router.post("/login/admin")
async def login_admin(admin_data: AdminAuthRequest) -> Dict[str, str]:
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
        admins = read_json_file(ADMIN_FILE)

        for admin in admins:
            if admin.get("email") == admin_data.college_email and verify_password(admin_data.password, admin.get("password")):
                logger.info(f"Admin login successful: {admin_data.username}")
                token = create_access_token(
                    data={"sub": admin_data.username, "role": "admin"})
                return {
                    "message": "Admin login successful",
                    "role": "admin",
                    "token": token
                }

        msg = f"Failed admin login attempt: {admin_data.username} (Invalid credentials)"
        logger.warning(msg)
        sentry_sdk.capture_message(msg, level="warning")

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    except HTTPException:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=500, detail="Admin login processing error")