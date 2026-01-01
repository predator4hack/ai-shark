from pydantic import BaseModel
from typing import Optional


class BaseResponse(BaseModel):
    """Base response model"""
    success: bool = True
    message: Optional[str] = None
