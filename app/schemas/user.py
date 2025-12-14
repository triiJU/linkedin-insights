from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class UserResponse(BaseModel):
    user_id: str
    name: str
    profile_url: str
    profile_picture_url: Optional[str] = None
    headline: Optional[str] = None
    position: Optional[str] = None
    company_page_id: Optional[str] = None
    scraped_at: datetime

class UserListResponse(BaseModel):
    users: List[UserResponse]
    total: int
    page: int
    page_size: int
    total_pages:  int
