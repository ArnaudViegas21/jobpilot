from playwright.sync_api import sync_playwright, Page, Browser
from typing import Dict, Optional
import time


class FormFiller:
    """
    Handles auto-filling job application forms using Playwright.
    """
    
    def __init__(self, headless: bool = False):
        """
        Initialize the form filler.
        
        Args:
            headless: Run browser in headless mode (no visible window)
        """
        self.headless = headless
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
    
    def start(self):
        """Start the browser."""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.page = self.browser.new_page()
        print("[form_filler] Browser started")
    
    def stop(self):
        """Close the browser."""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        print("[form_filler] Browser closed")
    
    def fill_form(self, url: str, form_data: Dict[str, str]) -> bool:
        """
        Navigate to a URL and attempt to fill a form.
        
        Args:
            url: The job application URL
            form_data: Dictionary of form field values
                Example: {
                    "name": "John Doe",
                    "email": "john@example.com",
                    "phone": "555-0100",
                    "resume": "/path/to/resume.pdf"
                }
        
        Returns:
            True if successful, False otherwise
        """
        if not self.page:
            print("[form_filler] Browser not started. Call start() first.")
            return False
        
        try:
            print(f"[form_filler] Navigating to {url}")
            self.page.goto(url, wait_until="networkidle")
            time.sleep(2)  # Wait for page to fully load
            
            # Common form field selectors (these vary by site)
            field_patterns = {
                "name": ["input[name*='name']", "input[id*='name']", "input[placeholder*='name']"],
                "email": ["input[type='email']", "input[name*='email']", "input[id*='email']"],
                "phone": ["input[type='tel']", "input[name*='phone']", "input[id*='phone']"],
                "resume": ["input[type='file'][name*='resume']", "input[type='file'][accept*='pdf']"],
                "cover_letter": ["textarea[name*='cover']", "textarea[id*='cover']"],
                "linkedin": ["input[name*='linkedin']", "input[placeholder*='linkedin']"]
            }
            
            filled_fields = 0
            
            for field_name, value in form_data.items():
                if field_name not in field_patterns:
                    continue
                
                for selector in field_patterns[field_name]:
                    try:
                        element = self.page.query_selector(selector)
                        if element:
                            if field_name == "resume":
                                # File upload
                                element.set_input_files(value)
                            else:
                                # Text input
                                element.fill(value)
                            filled_fields += 1
                            print(f"[form_filler] Filled '{field_name}' field")
                            break
                    except Exception as e:
                        continue
            
            print(f"[form_filler] Filled {filled_fields}/{len(form_data)} fields")
            
            # Don't auto-submit - let user review
            print("[form_filler] Form filled. Review and submit manually.")
            print("[form_filler] Press Enter when done...")
            input()
            
            return filled_fields > 0
            
        except Exception as e:
            print(f"[form_filler] Error: {e}")
            return False
    
    def click_easy_apply(self, job_url: str) -> bool:
        """
        Attempt to find and click an "Easy Apply" or "Quick Apply" button.
        
        Args:
            job_url: URL of the job posting
        
        Returns:
            True if button found and clicked, False otherwise
        """
        if not self.page:
            print("[form_filler] Browser not started. Call start() first.")
            return False
        
        try:
            print(f"[form_filler] Looking for Easy Apply button on {job_url}")
            self.page.goto(job_url, wait_until="networkidle")
            time.sleep(2)
            
            # Common "Easy Apply" button selectors
            easy_apply_selectors = [
                "button:has-text('Easy Apply')",
                "button:has-text('Quick Apply')",
                "button:has-text('Apply Now')",
                "a:has-text('Easy Apply')",
                ".easy-apply-button",
                "[data-job-apply]"
            ]
            
            for selector in easy_apply_selectors:
                try:
                    button = self.page.query_selector(selector)
                    if button:
                        button.click()
                        print(f"[form_filler] Clicked Easy Apply button")
                        time.sleep(1)
                        return True
                except:
                    continue
            
            print("[form_filler] No Easy Apply button found")
            return False
            
        except Exception as e:
            print(f"[form_filler] Error: {e}")
            return False
    
    def take_screenshot(self, filename: str = "screenshot.png"):
        """Take a screenshot of the current page."""
        if self.page:
            self.page.screenshot(path=filename)
            print(f"[form_filler] Screenshot saved to {filename}")


# Example usage
if __name__ == "__main__":
    filler = FormFiller(headless=False)
    filler.start()
    
    # Example: Fill a form
    form_data = {
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "555-0100"
    }
    
    # Replace with actual job URL
    filler.fill_form("https://example.com/apply", form_data)
    
    filler.stop()