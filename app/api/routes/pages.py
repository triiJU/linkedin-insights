from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, List
import asyncio
from datetime import datetime

from app.database.mongodb import get_database
from app.services.scraper import LinkedInScraper
from app.services.cache import cache_service
from app.schemas.page import PageResponse, PageListResponse
from app.models.page import PageModel
from app.models.post import PostModel
from app.models.user import SocialMediaUserModel
from app.config import settings

router = APIRouter(prefix="/pages", tags=["Pages"])

@router.get("/{page_id}", response_model=PageResponse)
async def get_page(page_id: str, db=Depends(get_database)):
    """
    Retrieve LinkedIn page details by page ID.
    Scrapes data in real-time if not present in database.
    """
    cache_key = f"page:{page_id}"
    
  
    if settings.ENABLE_CACHE:
        cached = await cache_service.get(cache_key)
        if cached:
            return cached
  
    page_data = await db.pages.find_one({"page_id": page_id})
    
    if not page_data:
        
        scraper = LinkedInScraper()
        try:
            scraped_data = await scraper.scrape_page(page_id)
            page_model = PageModel(**scraped_data)
            
            await db.pages.insert_one(
                page_model.model_dump(by_alias=True, exclude=['id'])
            )
            
            
            posts_data = await scraper.scrape_posts(page_id, settings.MAX_POSTS_PER_PAGE)
            employees_data = await scraper.scrape_employees(page_id)
            
            
            for post in posts_data:
                post_model = PostModel(**post)
                await db.posts.update_one(
                    {"post_id": post['post_id']},
                    {"$set": post_model.model_dump(by_alias=True, exclude=['id'])},
                    upsert=True
                )
            
            
            for employee in employees_data:
                user_model = SocialMediaUserModel(**employee)
                await db.users.update_one(
                    {"user_id": employee['user_id']},
                    {"$set": user_model.model_dump(by_alias=True, exclude=['id'])},
                    upsert=True
                )
            
            page_data = await db.pages.find_one({"page_id": page_id})
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")
    
    response_data = PageResponse(**page_data).model_dump()
    
    
    if settings.ENABLE_CACHE:
        await cache_service.set(cache_key, response_data)
    
    return response_data

@router.get("/", response_model=PageListResponse)
async def list_pages(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    min_followers: Optional[int] = Query(None, description="Minimum followers"),
    max_followers: Optional[int] = Query(None, description="Maximum followers"),
    industry: Optional[str] = Query(None, description="Filter by industry"),
    search: Optional[str] = Query(None, description="Search by name"),
    db=Depends(get_database)
):
    """
    List pages with optional filters:
    - Follower count range (e.g., 20k-40k)
    - Industry filter
    - Name search (case-insensitive)
    - Pagination support
    """
    query = {}
    
    if min_followers is not None or max_followers is not None:
        query['total_followers'] = {}
        if min_followers is not None:
            query['total_followers']['$gte'] = min_followers
        if max_followers is not None:
            query['total_followers']['$lte'] = max_followers
    
   
    if industry:
        query['industry'] = {"$regex": industry, "$options": "i"}
    
    
    if search:
        query['page_name'] = {"$regex": search, "$options": "i"}
    
    total = await db.pages.count_documents(query)
    
    skip = (page - 1) * page_size
    cursor = db.pages.find(query).skip(skip).limit(page_size).sort("total_followers", -1)
    pages = await cursor.to_list(page_size)
    
    pages_response = [PageResponse(**p) for p in pages]
    
    return PageListResponse(
        pages=pages_response,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )

@router.get("/{page_id}/employees", response_model=List[dict])
async def get_page_employees(
    page_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db=Depends(get_database)
):
    """
    Get employees/people associated with the company.
    Note: LinkedIn does not publicly expose follower identities.
    This endpoint returns employees as a proxy.
    """
    skip = (page - 1) * page_size
    cursor = db.users.find({"company_page_id": page_id}).skip(skip).limit(page_size)
    users = await cursor.to_list(page_size)
    return users

@router.get("/{page_id}/posts", response_model=List[dict])
async def get_page_posts(
    page_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(15, ge=1, le=50),
    db=Depends(get_database)
):
    """Get recent 10-15 posts from the page"""
    skip = (page - 1) * page_size
    cursor = db.posts.find({"page_id": page_id}).sort("posted_at", -1).skip(skip).limit(page_size)
    posts = await cursor.to_list(page_size)
    return posts

@router.delete("/{page_id}")
async def delete_page(page_id: str, db=Depends(get_database)):
    """Delete page and all associated data"""
    page_result = await db.pages.delete_one({"page_id": page_id})
    await db.posts.delete_many({"page_id": page_id})
    await db.users.delete_many({"company_page_id": page_id})
    
    if settings.ENABLE_CACHE:
        await cache_service.delete(f"page:{page_id}")
    
    if page_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Page not found")
    
    return {"message": "Page deleted successfully"}

@router.post("/{page_id}/refresh")
async def refresh_page(page_id: str, db=Depends(get_database)):
    """Re-scrape page to update data"""
    scraper = LinkedInScraper()
    
    try:
        scraped_data = await scraper.scrape_page(page_id)
        scraped_data['updated_at'] = datetime.utcnow()
        
        page_model = PageModel(**scraped_data)
        await db.pages.update_one(
            {"page_id": page_id},
            {"$set": page_model.model_dump(by_alias=True, exclude=['id'])},
            upsert=True
        )
        
        if settings.ENABLE_CACHE:
            await cache_service.delete(f"page:{page_id}")
        
        return {"message": "Page refreshed successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Refresh failed: {str(e)}")
