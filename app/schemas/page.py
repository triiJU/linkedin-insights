from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class PageResponse(BaseModel):
    page_id: str
    page_name: str
    page_url: str
    linkedin_id: Optional[str] = None
    profile_picture_url: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    total_followers: int = 0
    head_count: Optional[int] = 0
    specialties: List[str] = []
    location: Optional[str] = None
    founded_year: Optional[str] = None
    company_type: Optional[str] = None
    scraped_at: datetime
    updated_at: datetime

class PageListResponse(BaseModel):
    pages: List[PageResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
