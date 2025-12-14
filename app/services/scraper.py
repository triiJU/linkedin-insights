import asyncio
import httpx
from typing import Dict, List, Optional
from datetime import datetime
from bs4 import BeautifulSoup
import re

class LinkedInScraper:
    """
    Simple LinkedIn scraper using requests + BeautifulSoup.
    Note: LinkedIn's anti-scraping measures may limit data availability.
    This is a basic implementation for demonstration purposes.
    """
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
    def _extract_number(self, text: str) -> int:
        """Extract numeric value from text like '25,000 followers'"""
        try: 
            numbers = re.findall(r'[\d,]+', text)
            if numbers: 
                return int(numbers[0]. replace(',', ''))
        except:
            pass
        return 0
    
    async def scrape_page(self, page_id: str) -> Dict:
        """
        Scrape basic LinkedIn company page information.
        Limited by LinkedIn's public data availability. 
        """
        url = f"https://www.linkedin.com/company/{page_id}/"
        
        try:
            async with httpx.AsyncClient(timeout=30.0, headers=self.headers, follow_redirects=True) as client:
                response = await client.get(url)
                
                if response.status_code != 200:
                    raise Exception(f"Failed to fetch page:  {response.status_code}")
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                page_data = {
                    "page_id": page_id,
                    "page_url": url,
                    "page_name": self._extract_page_name(soup),
                    "profile_picture_url":  self._extract_profile_picture(soup),
                    "description":  self._extract_description(soup),
                    "website": self._extract_website(soup),
                    "industry": self._extract_industry(soup),
                    "total_followers": self._extract_followers(soup),
                    "head_count": self._extract_headcount(soup),
                    "specialties": self._extract_specialties(soup),
                    "location": self._extract_location(soup),
                    "founded_year": None,
                    "company_type": None,
                }
                
                return page_data
                
        except Exception as e:
            print(f"Scraping error for {page_id}: {str(e)}")
            raise
    
    def _extract_page_name(self, soup: BeautifulSoup) -> str:
        """Extract company name from page"""
        try:
            name_tag = soup.find('h1', class_='top-card-layout__title')
            if name_tag:
                return name_tag. text.strip()
        except:
            pass
        return "Unknown"
    
    def _extract_profile_picture(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract profile picture URL"""
        try: 
            img_tag = soup. find('img', class_='top-card-layout__entity-image')
            if img_tag and img_tag.get('src'):
                return img_tag['src']
        except:
            pass
        return None
    
    def _extract_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract company description"""
        try: 
            desc_tag = soup. find('p', class_='break-words')
            if desc_tag:
                return desc_tag.text.strip()
        except:
            pass
        return None
    
    def _extract_website(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract company website"""
        try:
            link_tag = soup.find('a', href=re.compile(r'http'))
            if link_tag and 'linkedin.com' not in link_tag.get('href', ''):
                return link_tag.get('href')
        except:
            pass
        return None
    
    def _extract_industry(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract company industry"""
        try:
            industry_text = soup.find(string=re.compile('Industry', re.I))
            if industry_text:
                parent = industry_text.find_parent()
                if parent: 
                    return parent.text. replace('Industry', '').strip()
        except:
            pass
        return None
    
    def _extract_followers(self, soup:  BeautifulSoup) -> int:
        """Extract follower count"""
        try:
            followers_text = soup.find(string=re.compile('followers', re.I))
            if followers_text:
                return self._extract_number(followers_text)
        except:
            pass
        return 0
    
    def _extract_headcount(self, soup: BeautifulSoup) -> Optional[int]:
        """Extract employee headcount"""
        try:
            headcount_text = soup.find(string=re.compile('employees', re.I))
            if headcount_text:
                return self._extract_number(headcount_text)
        except:
            pass
        return None
    
    def _extract_specialties(self, soup: BeautifulSoup) -> List[str]:
        """Extract company specialties"""
        try: 
            specialties_text = soup. find(string=re.compile('Specialties', re.I))
            if specialties_text: 
                parent = specialties_text.find_parent()
                if parent: 
                    text = parent.text.replace('Specialties', '').strip()
                    return [s.strip() for s in text.split(',')]
        except:
            pass
        return []
    
    def _extract_location(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract company location"""
        try:
            location_tag = soup.find('div', class_=re.compile('location'))
            if location_tag: 
                return location_tag.text. strip()
        except:
            pass
        return None
    
    async def scrape_posts(self, page_id: str, max_posts: int = 20) -> List[Dict]:
        """
        Scrape recent posts from a company page.
        Note: Limited access without authentication.
        """
        posts = []
        
        try: 
            url = f"https://www.linkedin.com/company/{page_id}/posts/"
            
            async with httpx.AsyncClient(timeout=30.0, headers=self.headers, follow_redirects=True) as client:
                response = await client.get(url)
                
                if response.status_code != 200:
                    print(f"Failed to fetch posts:  {response.status_code}")
                    return posts
                
                soup = BeautifulSoup(response.text, 'html. parser')
                
                # This is a simplified approach - LinkedIn requires auth for full post data
                post_elements = soup.find_all('div', class_=re.compile('feed-shared-update'))[: max_posts]
                
                for idx, post_elem in enumerate(post_elements):
                    try:
                        post_data = {
                            "post_id": f"{page_id}_post_{idx}_{int(datetime.now().timestamp())}",
                            "page_id": page_id,
                            "content": self._extract_post_content(post_elem),
                            "post_url": f"https://www.linkedin.com/company/{page_id}/posts/",
                            "media_urls": [],
                            "likes": self._extract_post_likes(post_elem),
                            "comments_count": self._extract_post_comments(post_elem),
                            "reposts":  0,
                            "posted_at": datetime.now(),
                            "comments": []
                        }
                        posts.append(post_data)
                    except Exception as e: 
                        print(f"Error parsing post:  {e}")
                        continue
                        
        except Exception as e: 
            print(f"Error scraping posts for {page_id}: {str(e)}")
        
        return posts
    
    def _extract_post_content(self, post_elem) -> str:
        """Extract post content text"""
        try:
            content_tag = post_elem.find('div', class_=re. compile('feed-shared-text'))
            if content_tag: 
                return content_tag.text.strip()
        except:
            pass
        return "Post content unavailable"
    
    def _extract_post_likes(self, post_elem) -> int:
        """Extract post like count"""
        try:
            likes_text = post_elem.find(string=re.compile('reaction', re.I))
            if likes_text:
                return self._extract_number(likes_text)
        except:
            pass
        return 0
    
    def _extract_post_comments(self, post_elem) -> int:
        """Extract post comment count"""
        try:
            comments_text = post_elem.find(string=re.compile('comment', re.I))
            if comments_text:
                return self._extract_number(comments_text)
        except:
            pass
        return 0
    
    async def scrape_employees(self, page_id: str, max_employees: int = 50) -> List[Dict]:
        """
        Scrape employees from a company page.
        Note: LinkedIn limits public access to employee data.
        """
        employees = []
        
        try: 
            url = f"https://www.linkedin.com/company/{page_id}/people/"
            
            async with httpx.AsyncClient(timeout=30.0, headers=self.headers, follow_redirects=True) as client:
                response = await client.get(url)
                
                if response.status_code != 200:
                    print(f"Failed to fetch employees:  {response.status_code}")
                    return employees
                
                soup = BeautifulSoup(response.text, 'html. parser')
                
                # This is simplified - full employee list requires authentication
                employee_elements = soup. find_all('div', class_=re.compile('org-people'))[: max_employees]
                
                for idx, emp_elem in enumerate(employee_elements):
                    try:
                        employee_data = {
                            "user_id": f"{page_id}_employee_{idx}",
                            "name": self._extract_employee_name(emp_elem),
                            "profile_url": self._extract_employee_profile(emp_elem),
                            "profile_picture_url": self._extract_employee_picture(emp_elem),
                            "headline": self._extract_employee_headline(emp_elem),
                            "position": self._extract_employee_position(emp_elem),
                            "company_page_id": page_id
                        }
                        employees. append(employee_data)
                    except Exception as e:
                        print(f"Error parsing employee: {e}")
                        continue
                        
        except Exception as e:
            print(f"Error scraping employees for {page_id}: {str(e)}")
        
        return employees
    
    def _extract_employee_name(self, emp_elem) -> str:
        """Extract employee name"""
        try:
            name_tag = emp_elem. find('div', class_=re.compile('name'))
            if name_tag: 
                return name_tag.text. strip()
        except:
            pass
        return "Unknown Employee"
    
    def _extract_employee_profile(self, emp_elem) -> str:
        """Extract employee profile URL"""
        try:
            link_tag = emp_elem.find('a', href=re.compile('/in/'))
            if link_tag:
                return f"https://www.linkedin.com{link_tag.get('href')}"
        except:
            pass
        return ""
    
    def _extract_employee_picture(self, emp_elem) -> Optional[str]:
        """Extract employee profile picture"""
        try:
            img_tag = emp_elem.find('img')
            if img_tag: 
                return img_tag.get('src')
        except:
            pass
        return None
    
    def _extract_employee_headline(self, emp_elem) -> Optional[str]:
        """Extract employee headline"""
        try: 
            headline_tag = emp_elem.find('div', class_=re.compile('headline'))
            if headline_tag:
                return headline_tag. text.strip()
        except:
            pass
        return None
    
    def _extract_employee_position(self, emp_elem) -> Optional[str]:
        """Extract employee position/title"""
        try:
            position_tag = emp_elem.find('div', class_=re. compile('position'))
            if position_tag: 
                return position_tag.text.strip()
        except:
            pass
        return None
