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
        
        Args:
            keywords: Job search keywords (e.g., "Python Developer")
            location: Location filter (e.g., "New York, NY")
            limit: Maximum number of jobs to return
        
        Returns:
            List of Job objects
        """
        jobs = []
        search_url = f"{self.BASE_URL}/jobs"
        params = {
            'q': keywords,
            'l': location,
            'limit': limit
        }
        
        print(f"[indeed] Searching for '{keywords}' in '{location}'...")
        
        try:
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