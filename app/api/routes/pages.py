# Add this import at the top
from app.services.ai_summary import ai_summary_service

# Add this endpoint at the end of the file
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
    posts_count = await db.posts.count_documents({"page_id": page_id})
    employees_count = await db.users.count_documents({"company_page_id": page_id})
    
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
