from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, List
import asyncio
from datetime import datetime
import math

from app.database. mongodb import get_database
from app.services.scraper import LinkedInScraper
from app.services.cache import cache_service
from app.schemas. page import PageResponse, PageListResponse
from app.schemas.post import PostResponse, PostListResponse
from app.schemas.user import UserResponse, UserListResponse
from app. models.page import PageModel
from app.models.post import PostModel
from app.models.user import SocialMediaUserModel
from app.config import settings
from app.services.ai_summary import ai_summary_service

router = APIRouter(prefix="/pages", tags=["Pages"])

@router.get("/{page_id}", response_model=PageResponse)
async def get_page(page_id: str, db=Depends(get_database)):
    """
    Retrieve LinkedIn page details by page ID.
    Scrapes data in real-time if not present in database.
    """
    cache_key = f"page:{page_id}"
    
    # Check cache
    if settings.ENABLE_CACHE: 
        cached = await cache_service.get(cache_key)
        if cached:
            return cached
    
    # Check database
    page_data = await db.pages.find_one({"page_id": page_id})
    
    if not page_data: 
        # Scrape if not found
        scraper = LinkedInScraper()
        try:
            scraped_data = await scraper. scrape_page(page_id)
            page_model = PageModel(**scraped_data)
            
            await db.pages.insert_one(
                page_model.model_dump(by_alias=True, exclude=['id'])
            )
            
            # Scrape posts and employees asynchronously
            posts_data = await scraper.scrape_posts(page_id, settings.MAX_POSTS_PER_PAGE)
            employees_data = await scraper.scrape_employees(page_id)
            
            # Store posts
            for post in posts_data:
                post_model = PostModel(**post)
                await db.posts. update_one(
                    {"post_id": post['post_id']},
                    {"$set": post_model. model_dump(by_alias=True, exclude=['id'])},
                    upsert=True
                )
            
            # Store employees
            for employee in employees_data:
                user_model = SocialMediaUserModel(**employee)
                await db. users.update_one(
                    {"user_id": employee['user_id']},
                    {"$set": user_model. model_dump(by_alias=True, exclude=['id'])},
                    upsert=True
                )
            
            page_data = await db.pages.find_one({"page_id": page_id})
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")
    
    response_data = PageResponse(**page_data).model_dump()
    
    # Cache the result
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
    
    # Follower range filter
    if min_followers is not None or max_followers is not None: 
        query['total_followers'] = {}
        if min_followers is not None:
            query['total_followers']['$gte'] = min_followers
        if max_followers is not None:
            query['total_followers']['$lte'] = max_followers
    
    # Industry filter
    if industry:
        query['industry'] = {"$regex": industry, "$options": "i"}
    
    # Name search filter
    if search:
        query['page_name'] = {"$regex": search, "$options":  "i"}
    
    # Get total count
    total = await db.pages.count_documents(query)
    
    # Calculate pagination
    skip = (page - 1) * page_size
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    
    # Fetch pages
    cursor = db.pages. find(query).skip(skip).limit(page_size)
    pages_data = await cursor.to_list(length=page_size)
    
    pages = [PageResponse(**page_data) for page_data in pages_data]
    
    return PageListResponse(
        pages=pages,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )

@router.get("/{page_id}/employees", response_model=UserListResponse)
async def get_page_employees(
    page_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db=Depends(get_database)
):
    """
    Get list of employees/people working at a company.
    """
    # Check if page exists
    page_data = await db.pages.find_one({"page_id": page_id})
    if not page_data: 
        raise HTTPException(status_code=404, detail="Page not found")
    
    query = {"company_page_id": page_id}
    
    # Get total count
    total = await db.users.count_documents(query)
    
    # Calculate pagination
    skip = (page - 1) * page_size
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    
    # Fetch users
    cursor = db.users. find(query).skip(skip).limit(page_size)
    users_data = await cursor.to_list(length=page_size)
    
    users = [UserResponse(**user_data) for user_data in users_data]
    
    return UserListResponse(
        users=users,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )

@router.get("/{page_id}/posts", response_model=PostListResponse)
async def get_page_posts(
    page_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(15, ge=1, le=100),
    db=Depends(get_database)
):
    """
    Get recent posts from a company page.
    Returns top 10-15 posts.
    """
    # Check if page exists
    page_data = await db.pages.find_one({"page_id": page_id})
    if not page_data: 
        raise HTTPException(status_code=404, detail="Page not found")
    
    query = {"page_id": page_id}
    
    # Get total count
    total = await db.posts. count_documents(query)
    
    # Calculate pagination
    skip = (page - 1) * page_size
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    
    # Fetch posts (sorted by posted_at descending)
    cursor = db.posts.find(query).sort("posted_at", -1).skip(skip).limit(page_size)
    posts_data = await cursor.to_list(length=page_size)
    
    posts = [PostResponse(**post_data) for post_data in posts_data]
    
    return PostListResponse(
        posts=posts,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )

@router.post("/{page_id}/refresh", response_model=PageResponse)
async def refresh_page(page_id: str, db=Depends(get_database)):
    """
    Force re-scrape a page and update database.
    Clears cache and fetches fresh data.
    """
    scraper = LinkedInScraper()
    
    try:
        # Scrape fresh data
        scraped_data = await scraper.scrape_page(page_id)
        scraped_data['updated_at'] = datetime.utcnow()
        
        # Update or insert page
        page_model = PageModel(**scraped_data)
        await db.pages.update_one(
            {"page_id": page_id},
            {"$set": page_model. model_dump(by_alias=True, exclude=['id'])},
            upsert=True
        )
        
        # Re-scrape posts and employees
        posts_data = await scraper. scrape_posts(page_id, settings.MAX_POSTS_PER_PAGE)
        employees_data = await scraper.scrape_employees(page_id)
        
        # Update posts
        for post in posts_data:
            post_model = PostModel(**post)
            await db.posts.update_one(
                {"post_id": post['post_id']},
                {"$set": post_model. model_dump(by_alias=True, exclude=['id'])},
                upsert=True
            )
        
        # Update employees
        for employee in employees_data:
            user_model = SocialMediaUserModel(**employee)
            await db.users.update_one(
                {"user_id": employee['user_id']},
                {"$set": user_model.model_dump(by_alias=True, exclude=['id'])},
                upsert=True
            )
        
        # Clear cache
        if settings.ENABLE_CACHE: 
            await cache_service.delete(f"page:{page_id}")
        
        page_data = await db.pages. find_one({"page_id": page_id})
        return PageResponse(**page_data)
        
    except Exception as e: 
        raise HTTPException(status_code=500, detail=f"Refresh failed: {str(e)}")

@router.delete("/{page_id}")
async def delete_page(page_id:  str, db=Depends(get_database)):
    """
    Delete a page and all associated data (posts, employees).
    """
    # Delete page
    result = await db.pages.delete_one({"page_id": page_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Page not found")
    
    # Delete associated posts
    await db.posts.delete_many({"page_id": page_id})
    
    # Delete associated employees
    await db.users. delete_many({"company_page_id": page_id})
    
    # Clear cache
    if settings.ENABLE_CACHE:
        await cache_service.delete(f"page:{page_id}")
    
    return {"message": f"Page {page_id} and associated data deleted successfully"}

@router.get("/{page_id}/summary")
async def get_page_ai_summary(page_id: str, db=Depends(get_database)):
    """
    Get AI-generated summary for a LinkedIn page.
    Uses ChatGPT to analyze followers, engagement, and company profile.
    """
    # Get page data
    page_data = await db.pages.find_one({"page_id": page_id})
    if not page_data:
        raise HTTPException(status_code=404, detail="Page not found")
    
    # Get counts
    posts_count = await db.posts. count_documents({"page_id": page_id})
    employees_count = await db.users. count_documents({"company_page_id": page_id})
    
    # Generate AI summary
    summary = await ai_summary_service.generate_page_summary(
        page_data,
        posts_count,
        employees_count
    )
    
    return {
        "page_id": page_id,
        "page_name": page_data.get('page_name'),
        "ai_summary": summary,
        "stats": {
            "followers": page_data.get('total_followers', 0),
            "posts": posts_count,
            "employees": employees_count
        }
    }
