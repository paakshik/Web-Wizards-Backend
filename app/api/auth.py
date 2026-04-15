from typing import  Dict
from fastapi import APIRouter, HTTPException, status
from app.model import AuthRequest
from app.config import logger, sentry_sdk, STUDENTS_FILE, ADMIN_FILE
from app.dependencies import read_json_file,write_json_file
router = APIRouter(prefix="/auth", tags=["Authentication"])



# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


# ============================================================================
# SIGNUP ENDPOINTS
# ============================================================================

@router.post("/signup/user", status_code=status.HTTP_201_CREATED)
async def signup_user(user_data: AuthRequest) -> Dict[str, str]:
    """
    Registers a new student/user into the students.json file.

    Args:
        user_data (AuthRequest): The username and password payload.

    Returns:
        Dict[str, str]: A success message and the registered username.
    """
    logger.info(f"Attempting to register new user: {user_data.username}")
    users = read_json_file(STUDENTS_FILE)

    if any(user.get("username") == user_data.username for user in users):
        logger.warning(
            f"Signup failed: Username '{user_data.username}' already exists.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )

    users.append(user_data.model_dump())
    write_json_file(STUDENTS_FILE, users)

    logger.info(f"Successfully registered new user: {user_data.username}")
    return {"message": "User created successfully", "username": user_data.username}


@router.post("/signup/admin", status_code=status.HTTP_201_CREATED)
async def signup_admin(admin_data: AuthRequest) -> Dict[str, str]:
    """
    Registers a new admin into the admin.json file.

    Args:
        admin_data (AuthRequest): The admin username and password payload.

    Returns:
        Dict[str, str]: A success message and the registered admin username.
    """
    logger.info(f"Attempting to register new admin: {admin_data.username}")
    admins = read_json_file(ADMIN_FILE)

    if any(admin.get("username") == admin_data.username for admin in admins):
        logger.warning(
            f"Admin signup failed: Username '{admin_data.username}' already exists.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin username already exists"
        )

    admins.append(admin_data.model_dump())
    write_json_file(ADMIN_FILE, admins)

    logger.info(f"Successfully registered new admin: {admin_data.username}")
    return {"message": "Admin created successfully", "username": admin_data.username}


# ============================================================================
# LOGIN ENDPOINTS
# ============================================================================

@router.post("/login/user")
async def login_user(user_data: AuthRequest) -> Dict[str, str]:
    """
    Authenticates a standard user/student from the students.json file.

    Args:
        user_data (AuthRequest): The login credentials.

    Returns:
        Dict[str, str]: A success message, the user role, and a dummy token.
    """
    logger.info(f"Login attempt for user: {user_data.username}")
    users = read_json_file(STUDENTS_FILE)

    for user in users:
        if user.get("username") == user_data.username and user.get(
                "password") == user_data.password:
            logger.info(f"User login successful: {user_data.username}")
            return {
                "message": "User login successful",
                "role": "student",
                "token": "dummy-user-token"
            }

    logger.warning(
        f"Failed login attempt for user: {user_data.username} (Invalid credentials)")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password"
    )


@router.post("/login/admin")
async def login_admin(admin_data: AuthRequest) -> Dict[str, str]:
    """
    Authenticates an admin from the admin.json file.

    Args:
        admin_data (AuthRequest): The admin login credentials.

    Returns:
        Dict[str, str]: A success message, the admin role, and a dummy token.
    """
    logger.info(f"Admin login attempt for username: {admin_data.username}")
    admins = read_json_file(ADMIN_FILE)

    for admin in admins:
        if admin.get("username") == admin_data.username and admin.get(
                "password") == admin_data.password:
            logger.info(f"Admin login successful: {admin_data.username}")
            return {
                "message": "Admin login successful",
                "role": "admin",
                "token": "dummy-admin-token"
            }

    logger.warning(
        f"Failed admin login attempt: {admin_data.username} (Invalid credentials)")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password"
    )


# ============================================================================
# LOGOUT ENDPOINT
# ============================================================================

@router.post("/logout")
async def logout() -> Dict[str, str]:
    """
    Handles user and admin logout.

    In a stateless architecture, this primarily acts as a confirmation endpoint.
    The client application should delete the stored token.

    Returns:
        Dict[str, str]: A confirmation message.
    """
    logger.info("Logout endpoint accessed")
    return {
        "message": "Logged out successfully. Please clear your token on the client side."}