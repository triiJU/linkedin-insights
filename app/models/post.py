from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from bson import ObjectId
from app.models.page import PyObjectId

class CommentModel(BaseModel):
    comment_id: str
    author_name: str
    author_profile_url: Optional[str] = None
    content: str
    posted_at: Optional[datetime] = None
    likes: Optional[int] = 0

class PostModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    post_id: str = Field(..., description="LinkedIn post ID")
    page_id: str = Field(..., description="Associated page ID")
    content: str
    post_url: str
    media_urls: Optional[List[str]] = []
    likes: Optional[int] = 0
    comments_count: Optional[int] = 0
    reposts: Optional[int] = 0
    posted_at: Optional[datetime] = None
    comments: Optional[List[CommentModel]] = []
    
    # Metadata
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "post_id": "12345678",
                "page_id": "deepsolv",
                "content": "Exciting news about our new product!",
                "likes": 150,
                "comments_count": 25,
                "reposts": 10
            }
        }
