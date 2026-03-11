"""
Adzuna API Scraper - Free job search API
Sign up for free API key at: https://developer.adzuna.com/
"""

import requests
from tracker.models import Job
from typing import List
from datetime import date
import hashlib


class AdzunaScraper:
    """
    Scraper using Adzuna's free job search API.
    
    Setup:
    1. Go to https://developer.adzuna.com/
    2. Sign up for free account
    3. Get your API ID and API Key
    4. Add them to config.yaml under 'api_keys.adzuna'
    """
    
    BASE_URL = "https://api.adzuna.com/v1/api/jobs/us/search"
    
    def __init__(self, app_id: str, app_key: str):
        """
        Initialize scraper with API credentials.
        
        Args:
            app_id: Your Adzuna Application ID
            app_key: Your Adzuna API Key
        """
        self.app_id = app_id
        self.app_key = app_key
    
    def search_jobs(self, keywords: str, location: str = "", limit: int = 10) -> List[Job]:
        """
        Search for jobs using Adzuna API.
        
        Args:
            keywords: Job search keywords
            location: Location filter
            limit: Maximum number of jobs to return
        
        Returns:
            List of Job objects
        """
        jobs = []
        
        # API endpoint: /v1/api/jobs/{country}/search/{page}
        url = f"{self.BASE_URL}/1"
        
        params = {
            'app_id': self.app_id,
            'app_key': self.app_key,
            'results_per_page': limit,
            'what': keywords,
            'where': location,
            'content-type': 'application/json'
        }
        
        print(f"[adzuna] Searching for '{keywords}' in '{location}'...")
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            for result in data.get('results', []):
                # Create unique ID
                job_id = hashlib.md5(result['id'].encode()).hexdigest()[:12]
                
                # Extract salary if available
                salary = None
                if result.get('salary_min') and result.get('salary_max'):
                    salary = f"${result['salary_min']:,.0f} - ${result['salary_max']:,.0f}"
                elif result.get('salary_min'):
                    salary = f"${result['salary_min']:,.0f}+"
                
                job = Job(
                    id=f"adzuna_{job_id}",
                    title=result['title'],
                    company=result['company']['display_name'],
                    location=result['location']['display_name'],
                    url=result['redirect_url'],
                    source="adzuna",
                    description=result.get('description', ''),
                    salary=salary,
                    date_scraped=date.today()
                )
                
                jobs.append(job)
                print(f"[adzuna] Found: {job.title} @ {job.company}")
            
            print(f"[adzuna] Scraped {len(jobs)} jobs")
            
        except requests.RequestException as e:
            print(f"[adzuna] API Error: {e}")
            print("[adzuna] Make sure your API credentials are correct")
        except Exception as e:
            print(f"[adzuna] Error: {e}")
        
        return jobs


# Quick test
if __name__ == "__main__":
    import os
    
    # Get credentials from environment or hardcode for testing
    app_id = os.getenv('ADZUNA_APP_ID', 'YOUR_APP_ID_HERE')
    app_key = os.getenv('ADZUNA_APP_KEY', 'YOUR_APP_KEY_HERE')
    
    if app_id == 'YOUR_APP_ID_HERE':
        print("Please set your Adzuna API credentials!")
        print("Get them at: https://developer.adzuna.com/")
    else:
        scraper = AdzunaScraper(app_id, app_key)
        jobs = scraper.search_jobs("Python Developer", "Remote", limit=5)
        for job in jobs:
            print(f"{job.title} at {job.company} - {job.url}")