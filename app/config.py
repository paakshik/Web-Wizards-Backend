"""
Application entry point.
Responsible only for:
- FastAPI app instantiation
- Middleware registration
- Router mounting

No business logic must exist here.
"""

import os,sys
from pathlib import Path as FilePath
from dotenv import load_dotenv
import sentry_sdk
import logging


load_dotenv()
def setup_logging(log_dir_name: str = "logs") -> logging.Logger:
    """
    Configure and return a production-ready application logger.

    This function sets up a comprehensive logging system that:
    1. Creates a dedicated log directory in the project root
    2. Configures dual output (console + file) with rotation
    3. Sets appropriate log levels and formats for different environments
    4. Returns a named logger instance for application-wide use

    Args:
        log_dir_name: Name of the directory to store log files.
                     Defaults to "logs". The directory will be created
                     at the project root level.

    Returns:
        logging.Logger: A configured logger instance named "dashboard"
                       that can be imported and used throughout the application.

    Raises:
        PermissionError: If the log directory cannot be created due to
                        insufficient permissions.
        OSError: For other filesystem-related errors during directory creation.

    """
    project_root = FilePath(__file__).resolve().parent.parent
    log_dir = project_root / log_dir_name
    log_dir.mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_dir / "app.log")
        ]
    )
    logger_main = logging.getLogger("Personal Dashboard")
    logger_main.info("Logging system initialized from config")
    logger_main.debug(f"Log directory: {log_dir}")
    return logger_main

logger = setup_logging()

def require_env(key: str) -> str:
    """
    Fetch a required environment variable.

    This function ensures critical environment variables are present.
    If the variable is missing, it raises an immediate error with clear
    messaging, preventing the application from starting in an invalid state.

    Args:
        key: The name of the environment variable to fetch.

    Returns:
        str: The value of the environment variable.

    Raises:
        RuntimeError: If the environment variable is not set or is empty.
    """
    value = os.getenv(key)

    if not value:
        error_msg: str = f"Missing required environment variable: {key}"
        logger.critical(error_msg)
        sentry_sdk.capture_message(error_msg, level="fatal")
        raise RuntimeError(error_msg)

    logger.debug(f"Loaded required environment variable: {key}")
    return value


def optional_env(key: str, default=None):
    """
    Fetch an optional environment variable.

    This function retrieves environment variables that have sensible defaults
    or are not required for basic operation. It logs warnings for missing
    optional variables to aid debugging without breaking the application.

    Args:
        key: The name of the environment variable to fetch.
        default: The default value to return if the variable is not set.
                 Defaults to None.

    Returns:
        The value of the environment variable if set, otherwise the default.
    """
    value = os.getenv(key, default)
    if value is None:
        warning_msg: str = f"Optional environment variable '{key}' is not set, using default: {default}"
        logger.warning(warning_msg)
        return default
    logger.debug(f"Loaded required environment variable: {key}")
    return value


SECRET_KEY = require_env("SECRET_KEY")
ALGORITHM = require_env("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(optional_env("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
AUTHLIB_INSECURE_TRANSPORT = optional_env("AUTHLIB_INSECURE_TRANSPORT", "0")
DATABASE_URL = require_env("DATABASE_URL")
CLOUDINARY_CLOUD_NAME = require_env("CLOUDINARY_CLOUD_NAME")
CLOUDINARY_API_KEY = require_env("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = require_env("CLOUDINARY_API_SECRET")
SENTRY_DSN = optional_env("SENTRY_DSN")
RESEND_API_KEY = require_env("RESEND_API_KEY")
RESEND_FROM_EMAIL = require_env("RESEND_FROM_EMAIL")
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        environment=optional_env("ENVIRONMENT", "production"),
        traces_sample_rate=0.1,
        send_default_pii=False,
    )
logger.info("Sentry monitoring initialized")

