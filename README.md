# LinkedIn Insights Microservice

Backend microservice for scraping and managing LinkedIn company page data.

## Features

### Core Requirements
- LinkedIn company page scraper (requests + BeautifulSoup)
- MongoDB storage with proper schema relationships
- RESTful API with filtering and pagination
- Follower count range filter (e.g., 20k-40k)
- Industry and name search filters
- Employee and post retrieval endpoints

### Additional Features
- Redis caching (5-minute TTL) - optional, can be disabled
- Async operations for better performance
- Docker support for easy deployment

## Tech Stack

- **Framework**: FastAPI
- **Database**: MongoDB (Motor for async)
- **Cache**: Redis (optional)
- **Scraping**: httpx + BeautifulSoup4
- **Testing**: pytest

## Setup

### Prerequisites
- Python 3.11+
- MongoDB
- Redis (optional)

### Installation

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your MongoDB URL
```

4. Start services:
```bash
# MongoDB
docker run -d -p 27017:27017 mongo:7.0

# Redis (optional)
docker run -d -p 6379:6379 redis:7-alpine
```

5. Run application:
```bash
uvicorn app.main:app --reload
```

Access at: http://localhost:8000

### Docker Setup

```bash
docker-compose up --build
```

## API Endpoints

### Pages
- `GET /api/v1/pages/{page_id}` - Get page (scrapes if not in DB)
- `GET /api/v1/pages` - List all pages
- `GET /api/v1/pages/{page_id}/employees` - Get employees
- `GET /api/v1/pages/{page_id}/posts` - Get posts
- `POST /api/v1/pages/{page_id}/refresh` - Re-scrape page
- `DELETE /api/v1/pages/{page_id}` - Delete page

### Filter Examples

```bash
# Follower range filter
GET /api/v1/pages?min_followers=20000&max_followers=40000

# Search by name
GET /api/v1/pages?search=technology

# Filter by industry
GET /api/v1/pages?industry=Software

# Pagination
GET /api/v1/pages?page=1&page_size=20
```

## Testing

Import `postman_collection.json` into Postman and run the requests.

API documentation available at:
- Swagger: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
app/
├── main.py              # FastAPI app
├── config.py            # Settings
├── models/              # MongoDB models
├── schemas/             # API schemas
├── services/            # Business logic
├── api/routes/          # API endpoints
└── database/            # DB connection
```

## Implementation Notes

### Scraping Limitations
- LinkedIn has anti-scraping measures that limit public data access
- Some data requires authentication (not implemented here)
- Follower lists are not publicly available - employee data is used as a proxy
- Post data may be limited without authentication

### Database Schema
- **Pages**: Company information with follower counts, industry, etc.
- **Posts**: Company posts with engagement metrics
- **Users**: Employee/people data linked to companies

### Design Patterns
- Repository pattern for data access
- Service layer for business logic
- Dependency injection via FastAPI
- Async/await for I/O operations

## Configuration

Edit `.env` file:

```env
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=linkedin_insights
REDIS_HOST=localhost
ENABLE_CACHE=true
```

## Troubleshooting

**MongoDB connection issues:**
```bash
docker ps | grep mongo
docker logs mongodb
```

**Cache issues:**
```bash
# Disable cache in .env
ENABLE_CACHE=false
```

**Scraping errors:**
- LinkedIn may block requests
- Try adjusting timeout in config
- Some data requires authentication

## License

Educational/Assignment project.
