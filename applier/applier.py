from applier.form_filler import FormFiller
from tracker.models import Job, Application, JobStatus
from tracker.tracker import save_application
from datetime import date
from typing import Dict, Optional
import yaml
import os


class JobApplier:
    """
    Orchestrates the job application process using the FormFiller.
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize the applier.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.form_filler = FormFiller(headless=False)
        self.resume_data = self._load_resume_data()
    
    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file."""
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return yaml.safe_load(f) or {}
        return {}
    
    def _load_resume_data(self) -> Dict[str, str]:
        """
        Load resume data for auto-filling forms.
        This reads from config.yaml or returns defaults.
        """
        return self.config.get('personal_info', {
            'name': 'Your Name',
            'email': 'your.email@example.com',
            'phone': '555-0100',
            'linkedin': 'https://linkedin.com/in/yourprofile',
            'resume_path': 'data/resume.pdf'
        })
    
    def apply_to_job(self, job: Job, auto_submit: bool = False) -> bool:
        """
        Apply to a single job.
        
        Args:
            job: The Job object to apply to
            auto_submit: If True, attempt to auto-submit (risky!)
        
        Returns:
            True if application was successful, False otherwise
        """
        print(f"\n[applier] Applying to: {job.title} @ {job.company}")
        print(f"[applier] URL: {job.url}")
        
        try:
            self.form_filler.start()
            
            # Try Easy Apply if available
            if job.easy_apply:
                if self.form_filler.click_easy_apply(job.url):
                    # Fill the Easy Apply form
                    success = self.form_filler.fill_form(job.url, self.resume_data)
                else:
                    # Fallback to regular form
                    success = self.form_filler.fill_form(job.url, self.resume_data)
            else:
                # Regular application
                success = self.form_filler.fill_form(job.url, self.resume_data)
            
            if success:
                # Create Application record
                app = Application(
                    job_id=job.id,
                    title=job.title,
                    company=job.company,
                    url=job.url,
                    source=job.source,
                    status=JobStatus.APPLIED,
                    date_applied=date.today(),
                    resume_used=self.resume_data.get('resume_path', 'default.pdf')
                )
                
                # Save to tracker
                save_application(app)
                print(f"[applier] ✓ Application saved to tracker")
                
                self.form_filler.stop()
                return True
            else:
                print(f"[applier] ✗ Failed to fill form")
                self.form_filler.stop()
                return False
                
        except Exception as e:
            print(f"[applier] Error: {e}")
            self.form_filler.stop()
            return False
    
    def batch_apply(self, jobs: list[Job], max_applications: int = 5) -> int:
        """
        Apply to multiple jobs in batch.
        
        Args:
            jobs: List of Job objects
            max_applications: Maximum number of applications to submit
        
        Returns:
            Number of successful applications
        """
        successful = 0
        
        for i, job in enumerate(jobs[:max_applications]):
            print(f"\n[applier] Job {i+1}/{min(len(jobs), max_applications)}")
            
            if self.apply_to_job(job):
                successful += 1
            
            # Ask user if they want to continue
            if i < len(jobs) - 1:
                response = input("\nContinue to next job? (y/n): ").lower()
                if response != 'y':
                    break
        
        print(f"\n[applier] Applied to {successful}/{len(jobs)} jobs")
        return successful


# Example usage
if __name__ == "__main__":
    from tracker.models import Job
    
    # Example job
    test_job = Job(
        id="test_001",
        title="Python Developer",
        company="Tech Company",
        location="Remote",
        url="https://example.com/jobs/python-dev",
        source="manual",
        easy_apply=False
    )
    
    applier = JobApplier()
    applier.apply_to_job(test_job)