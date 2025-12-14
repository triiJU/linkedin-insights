from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class CommentResponse(BaseModel):
    comment_id: str
    author_name: str
    author_profile_url: Optional[str] = None
    content: str
    posted_at: Optional[datetime] = None
    likes: Optional[int] = 0

class PostResponse(BaseModel):
    post_id: str
    page_id: str
    content: str
    post_url: str
    media_urls: List[str] = []
    likes: int = 0
    comments_count: int = 0
    reposts:  int = 0
    posted_at: Optional[datetime] = None
    comments: List[CommentResponse] = []
    scraped_at: datetime

class PostListResponse(BaseModel):
    posts: List[PostResponse]
    total: int
    page: int
    page_size: int
    total_pages:  int
