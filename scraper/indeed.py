from scraper.base import BaseScraper
from tracker.models import Job
from bs4 import BeautifulSoup
from typing import List
from datetime import date
import hashlib


class IndeedScraper(BaseScraper):
    """Scraper for Indeed.com job listings."""
    
    BASE_URL = "https://www.indeed.com"
    
    def search_jobs(self, keywords: str, location: str = "", limit: int = 10) -> List[Job]:
        """
        Search Indeed for jobs.
        
        NOTE: Indeed actively blocks scrapers. This may not work reliably.
        Consider using the Adzuna API scraper instead (scraper/adzuna.py).
        
        Args:
            keywords: Job search keywords (e.g., "Python Developer")
            location: Location filter (e.g., "New York, NY")
            limit: Maximum number of jobs to return
        
        Returns:
            List of Job objects
        """
        jobs = []
        
        # Add more realistic headers to avoid detection
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.indeed.com/',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        search_url = f"{self.BASE_URL}/jobs"
        params = {
            'q': keywords,
            'l': location,
            'limit': limit
        }
        
        print(f"[indeed] Searching for '{keywords}' in '{location}'...")
        print(f"[indeed] WARNING: Indeed blocks scrapers. If this fails, use Adzuna API instead.")
        
        try:
            self.random_delay(1, 3)  # Add delay before request
            response = self.safe_get(search_url, params=params)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Indeed's job cards - structure may vary, this is a simplified version
            job_cards = soup.find_all('div', class_='job_seen_beacon')
            
            for card in job_cards[:limit]:
                try:
                    # Extract job details
                    title_elem = card.find('h2', class_='jobTitle')
                    company_elem = card.find('span', class_='companyName')
                    location_elem = card.find('div', class_='companyLocation')
                    
                    if not title_elem or not company_elem:
                        continue
                    
                    # Get job link
                    link_elem = title_elem.find('a')
                    job_url = f"{self.BASE_URL}{link_elem['href']}" if link_elem and 'href' in link_elem.attrs else ""
                    
                    # Create unique ID from URL or title+company
                    job_id = hashlib.md5(job_url.encode()).hexdigest()[:12] if job_url else hashlib.md5(f"{title_elem.text}{company_elem.text}".encode()).hexdigest()[:12]
                    
                    job = Job(
                        id=f"indeed_{job_id}",
                        title=title_elem.text.strip(),
                        company=company_elem.text.strip(),
                        location=location_elem.text.strip() if location_elem else location,
                        url=job_url,
                        source="indeed",
                        date_scraped=date.today()
                    )
                    
                    jobs.append(job)
                    print(f"[indeed] Found: {job.title} @ {job.company}")
                    
                except Exception as e:
                    print(f"[indeed] Error parsing job card: {e}")
                    continue
                
                self.random_delay(0.5, 1.5)
            
            print(f"[indeed] Scraped {len(jobs)} jobs")
            
        except Exception as e:
            print(f"[indeed] Error during search: {e}")
        
        return jobs


# Quick test function
if __name__ == "__main__":
    scraper = IndeedScraper()
    jobs = scraper.search_jobs("Python Developer", "Remote", limit=5)
    for job in jobs:
        print(f"{job.title} at {job.company} - {job.url}")