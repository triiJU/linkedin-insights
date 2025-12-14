from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")

class PageModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    page_id: str = Field(..., description="LinkedIn page ID")
    page_name: str
    page_url: str
    linkedin_id: Optional[str] = None
    profile_picture_url: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    total_followers: Optional[int] = 0
    head_count: Optional[int] = 0
    specialties: Optional[List[str]] = []
    location: Optional[str] = None
    founded_year: Optional[str] = None
    company_type: Optional[str] = None
    phone: Optional[str] = None
    
    # Metadata
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "page_id": "deepsolv",
                "page_name": "DeepSolv",
                "page_url": "https://www.linkedin.com/company/deepsolv/",
                "total_followers": 25000,
                "industry": "Technology"
            }
        }
