from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from bson import ObjectId
from app.models.page import PyObjectId

class SocialMediaUserModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    user_id: str = Field(..., description="LinkedIn user ID")
    name: str
    profile_url: str
    profile_picture_url: Optional[str] = None
    headline: Optional[str] = None
    position: Optional[str] = None
    company_page_id: Optional[str] = None
    
  
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "user_id": "john-doe",
                "name": "John Doe",
                "profile_url": "https://www.linkedin.com/in/john-doe/",
                "headline": "Software Engineer at DeepSolv",
                "company_page_id": "deepsolv"
            }
        }
