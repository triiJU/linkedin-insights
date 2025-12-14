from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database.mongodb import connect_to_mongo, close_mongo_connection
from app.services.cache import cache_service
from app.api.routes import pages

@asynccontextmanager
async def lifespan(app: FastAPI):
 
    await connect_to_mongo()
    if settings.ENABLE_CACHE:
        await cache_service.connect()
    yield
  
    await close_mongo_connection()
    if settings.ENABLE_CACHE:
        await cache_service.disconnect()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
    description="LinkedIn company page scraper and insights API"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pages.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": "LinkedIn Insights Microservice",
        "version": settings.VERSION,
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
