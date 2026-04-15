import json
from app.config import (STUDENTS_FILE, ADMIN_FILE,logger,sentry_sdk)
from pathlib import Path
from typing import Any, Union, List, Dict
def read_json_file(file_path: Union[str, Path]) -> Union[
    List[Any], Dict[str, Any], None]:
    """
    Read JSON file and return its content.

    Args:
        file_path: Path to JSON file (string or Path object)

    Returns:
        - List for user/project/command/chat files
        - Dict for tokens file
        - None for other files if they don't exist

    Behavior:
        - Returns empty list [] for user/project/command/chat files if file doesn't exist
        - Returns empty dict {} for tokens file if file doesn't exist
        - Returns None for other files if they don't exist
        - Returns default on JSON decode errors
    """
    """Read JSON file, return default if file doesn't exist or is invalid"""
    path_obj = Path(file_path)

    # 1. LAZY INIT: Check if file exists
    if not path_obj.exists():
        default_data = None

        if path_obj in [STUDENTS_FILE,ADMIN_FILE]:
            default_data = []

        # If it's a known file type, create it physically now
        if default_data is not None:
            try:
                # Ensure the folder exists (e.g., dashboard_data/)
                path_obj.parent.mkdir(parents=True, exist_ok=True)

                # Create the actual file with empty JSON
                with open(path_obj, 'w',encoding='utf-8') as f:
                    json.dump(default_data, f)

                logger.info(f"Lazy Initialized new data file: {path_obj}")
                return default_data
            except OSError as e:
                logger.error(f"Failed to lazy create {path_obj}: {e}")
                return default_data  # Return in-memory empty data as fallback

        return None

    # 2. Normal Read
    try:
        with open(path_obj, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Error reading {path_obj}: {e}")
        return []

def write_json_file(file_path, data, verbose=False) -> bool :
    """
        Write data to JSON file with error handling.

        Args:
            file_path: Path to write to (string or Path object)
            data: Data to serialize as JSON (dict, list, etc.)
            verbose: If True, print success message

        Returns:
            True if successful, False otherwise
        """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        if verbose:
            logger.info(f"Successfully wrote {type(data).__name__} to {file_path}")

        return True

    except IOError as e:
        logger.error(f"File I/O error writing to {file_path}: {e}", exc_info=True)
        sentry_sdk.capture_exception(e, extra={
            "file_path": str(file_path),
            "data_type": type(data).__name__
        })
        return False

    except (TypeError, ValueError) as e:
        logger.error(f"JSON serialization error for {file_path}: {e}", exc_info=True)
        sentry_sdk.capture_exception(e, extra={
            "file_path": str(file_path),
            "data_preview": str(data)[:200]
        })
        return False