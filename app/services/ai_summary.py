import httpx
from typing import Dict, Optional
from app.config import settings

class AISummaryService:
    """
    AI-powered summary generation for LinkedIn pages.
    Uses OpenAI GPT or compatible APIs.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or getattr(settings, 'OPENAI_API_KEY', None)
        self.api_url = "https://api.openai.com/v1/chat/completions"
    
    async def generate_page_summary(
        self,
        page_data: Dict,
        posts_count: int = 0,
        employees_count: int = 0
    ) -> str:
        """
        Generate AI summary for a LinkedIn page.
        """
        if not self.api_key:
            return "AI summary unavailable - API key not configured"
        
        prompt = self._build_prompt(page_data, posts_count, employees_count)
        
        try: 
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client. post(
                    self.api_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "gpt-3.5-turbo",
                        "messages": [
                            {"role": "system", "content": "You are a LinkedIn insights analyst. "},
                            {"role": "user", "content": prompt}
                        ],
                        "max_tokens": 300,
                        "temperature": 0.7
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result['choices'][0]['message']['content']
                else:
                    return f"AI summary generation failed: {response.status_code}"
                    
        except Exception as e:
            return f"AI summary error: {str(e)}"
    
    def _build_prompt(self, page_data: Dict, posts_count: int, employees_count: int) -> str:
        """Build prompt for AI summary generation"""
        return f"""
        Analyze this LinkedIn company page and provide a concise summary: 
        
        Company: {page_data. get('page_name', 'Unknown')}
        Industry: {page_data.get('industry', 'Unknown')}
        Followers: {page_data.get('total_followers', 0):,}
        Employees: {employees_count}
        Description: {page_data.get('description', 'Not available')}
        Recent Posts: {posts_count}
        
        Provide a 2-3 sentence summary covering:
        1. Company profile and market position
        2. Follower engagement level
        3. Employee count and company size assessment
        """

# Singleton instance
ai_summary_service = AISummaryService()
