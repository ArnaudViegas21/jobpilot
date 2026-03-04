import csv
import os
from datetime import date
from typing import Optional
from tracker.models import Application, JobStatus

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
CSV_PATH = os.path.join(DATA_DIR, "applications.csv")

# All fields we store in the CSV (must match Application model)
FIELDS = [
    "job_id", "title", "company", "url", "source", "status",
    "date_applied", "date_updated", "resume_used", "cover_letter",
    "notes", "contact_name", "contact_email", "interview_date", "offer_amount"
]


def _ensure_csv():
    """Create the CSV file with headers if it doesn't exist yet."""
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(CSV_PATH):
        with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader()


def save_application(app: Application) -> None:
    """Add a new application to the CSV."""
    _ensure_csv()

    # Check for duplicates by job_id
    existing = load_applications()
    for a in existing:
        if a.job_id == app.job_id:
            print(f"[tracker] Already tracking application for job_id '{app.job_id}'. Skipping.")
            return

    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writerow(app.model_dump())
    print(f"[tracker] Saved application: {app.title} @ {app.company}")


def load_applications() -> list[Application]:
    """Load all applications from the CSV."""
    _ensure_csv()
    applications = []
    with open(CSV_PATH, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert empty strings back to None for optional fields
            cleaned = {k: (v if v != "" else None) for k, v in row.items()}
            applications.append(Application(**cleaned))
    return applications


def update_status(job_id: str, new_status: JobStatus, notes: Optional[str] = None) -> bool:
    """Update the status (and optionally notes) of an existing application."""
    applications = load_applications()
    updated = False

    for app in applications:
        if app.job_id == job_id:
            app.status = new_status
            app.date_updated = date.today()
            if notes:
                app.notes = notes
            updated = True
            break

    if not updated:
        print(f"[tracker] No application found with job_id '{job_id}'.")
        return False

    # Rewrite the entire CSV with the updated data
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        for app in applications:
            writer.writerow(app.model_dump())

    print(f"[tracker] Updated job_id '{job_id}' to status '{new_status}'.")
    return True


def get_by_status(status: JobStatus) -> list[Application]:
    """Return all applications matching a given status."""
    return [app for app in load_applications() if app.status == status]


def summary() -> dict:
    """Return a count of applications grouped by status."""
    applications = load_applications()
    counts = {status.value: 0 for status in JobStatus}
    for app in applications:
        counts[app.status.value] += 1
    counts["total"] = len(applications)
    return counts