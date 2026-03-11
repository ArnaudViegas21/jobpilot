import requests
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
from tracker.models import Job
from typing import List
import time
import random


class BaseScraper(ABC):
    """Abstract base class for job scrapers."""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    @abstractmethod
    def search_jobs(self, keywords: str, location: str = "", limit: int = 10) -> List[Job]:
        """Search for jobs. Must be implemented by each scraper."""
        pass
    
    def random_delay(self, min_seconds: float = 1.0, max_seconds: float = 3.0):
        """Add random delay to avoid rate limiting."""
        time.sleep(random.uniform(min_seconds, max_seconds))
    
    def safe_get(self, url: str, params: dict = None, max_retries: int = 3) -> requests.Response:
        """Make a request with retry logic."""
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, params=params, timeout=10)
                response.raise_for_status()
                return response
            except requests.RequestException as e:
                if attempt == max_retries - 1:
                    raise e
                self.random_delay(2, 5)
        raise Exception(f"Failed to fetch {url} after {max_retries} attempts")