from pydantic import BaseModel
from typing import Optional, List

class AuthRequest(BaseModel):
    username: str
    password: str