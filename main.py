#!/usr/bin/env python3
"""
JobPilot - Job Application Tracker and Auto-Applier

A comprehensive tool to scrape job listings, track applications, 
and automate the application process.
"""

import typer
from rich.console import Console
from rich.table import Table
from rich.progress import track
import json
import yaml
from pathlib import Path

from scraper.indeed import IndeedScraper
from scraper.linkedin import LinkedInScraper
from scraper.adzuna import AdzunaScraper
from applier.applier import JobApplier
from tracker.tracker import (
    save_application, 
    load_applications, 
    update_status, 
    get_by_status,
    summary
)
from tracker.models import Job, Application, JobStatus

app = typer.Typer(help="JobPilot - Job Application Tracker & Auto-Applier")
console = Console()


@app.command()
def scrape(
    keywords: str = typer.Option(..., "--keywords", "-k", help="Job search keywords"),
    location: str = typer.Option("", "--location", "-l", help="Location filter"),
    source: str = typer.Option("adzuna", "--source", "-s", help="Job board (adzuna/indeed/linkedin)"),
    limit: int = typer.Option(10, "--limit", "-n", help="Max number of jobs to scrape"),
    save: bool = typer.Option(True, "--save/--no-save", help="Save results to jobs.json")
):
    """Scrape job listings from job boards."""
    console.print(f"\n[bold blue]Scraping {source.upper()}...[/bold blue]")
    
    # Initialize scraper
    if source.lower() == "adzuna":
        # Load API credentials from config
        config_file = Path("config.yaml")
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f) or {}
        else:
            config = {}
        
        api_keys = config.get('api_keys', {}).get('adzuna', {})
        app_id = api_keys.get('app_id')
        app_key = api_keys.get('app_key')
        
        if not app_id or not app_key or app_id == "YOUR_ADZUNA_APP_ID":
            console.print("[red]Adzuna API credentials not found![/red]")
            console.print("[yellow]Get free API key at: https://developer.adzuna.com/[/yellow]")
            console.print("[yellow]Add to config.yaml under 'api_keys.adzuna'[/yellow]")
            return
        
        scraper = AdzunaScraper(app_id, app_key)
    elif source.lower() == "indeed":
        scraper = IndeedScraper()
    elif source.lower() == "linkedin":
        scraper = LinkedInScraper()
    else:
        console.print(f"[red]Unknown source: {source}[/red]")
        return
    
    # Scrape jobs
    jobs = scraper.search_jobs(keywords, location, limit)
    
    if not jobs:
        console.print("[yellow]No jobs found[/yellow]")
        return
    
    # Display results
    table = Table(title=f"Found {len(jobs)} Jobs")
    table.add_column("Title", style="cyan")
    table.add_column("Company", style="magenta")
    table.add_column("Location", style="green")
    
    for job in jobs:
        table.add_row(job.title, job.company, job.location)
    
    console.print(table)
    
    # Save to file
    if save:
        jobs_file = Path("data/jobs.json")
        
        # Load existing jobs
        existing_jobs = []
        if jobs_file.exists():
            with open(jobs_file, 'r') as f:
                existing_jobs = [Job(**j) for j in json.load(f)]
        
        # Add new jobs (avoid duplicates by ID)
        existing_ids = {j.id for j in existing_jobs}
        new_jobs = [j for j in jobs if j.id not in existing_ids]
        
        all_jobs = existing_jobs + new_jobs
        
        # Save
        with open(jobs_file, 'w') as f:
            json.dump([j.model_dump(mode='json') for j in all_jobs], f, indent=2, default=str)
        
        console.print(f"\n[green]✓ Saved {len(new_jobs)} new jobs to {jobs_file}[/green]")


@app.command()
def apply(
    job_id: str = typer.Option(None, "--job-id", "-j", help="Job ID to apply to"),
    batch: bool = typer.Option(False, "--batch", "-b", help="Apply to multiple jobs from jobs.json"),
    limit: int = typer.Option(5, "--limit", "-n", help="Max applications in batch mode")
):
    """Apply to jobs using browser automation."""
    applier = JobApplier()
    
    if job_id:
        # Apply to specific job
        jobs_file = Path("data/jobs.json")
        if not jobs_file.exists():
            console.print("[red]No jobs.json found. Run 'scrape' first.[/red]")
            return
        
        with open(jobs_file, 'r') as f:
            jobs_data = json.load(f)
        
        job = next((Job(**j) for j in jobs_data if j['id'] == job_id), None)
        
        if not job:
            console.print(f"[red]Job {job_id} not found[/red]")
            return
        
        applier.apply_to_job(job)
    
    elif batch:
        # Batch apply
        jobs_file = Path("data/jobs.json")
        if not jobs_file.exists():
            console.print("[red]No jobs.json found. Run 'scrape' first.[/red]")
            return
        
        with open(jobs_file, 'r') as f:
            jobs_data = json.load(f)
        
        jobs = [Job(**j) for j in jobs_data]
        console.print(f"\n[bold]Batch applying to {min(len(jobs), limit)} jobs[/bold]")
        
        applier.batch_apply(jobs, max_applications=limit)
    
    else:
        console.print("[yellow]Specify --job-id or --batch[/yellow]")


@app.command()
def track(
    action: str = typer.Argument("list", help="Action: list/add/update/summary"),
    job_id: str = typer.Option(None, "--job-id", "-j", help="Job ID"),
    status: str = typer.Option(None, "--status", "-s", help="New status"),
    notes: str = typer.Option(None, "--notes", "-n", help="Notes to add")
):
    """Manage your application tracker."""
    
    if action == "list":
        # List all applications
        apps = load_applications()
        
        if not apps:
            console.print("[yellow]No applications tracked yet[/yellow]")
            return
        
        table = Table(title=f"Your Applications ({len(apps)} total)")
        table.add_column("Job ID", style="dim")
        table.add_column("Title", style="cyan")
        table.add_column("Company", style="magenta")
        table.add_column("Status", style="bold")
        table.add_column("Applied", style="green")
        
        for app in apps:
            # Color code status
            status_colors = {
                "applied": "blue",
                "interview": "yellow",
                "offer": "green",
                "rejected": "red",
                "withdrawn": "dim"
            }
            color = status_colors.get(app.status.value, "white")
            
            table.add_row(
                app.job_id,
                app.title,
                app.company,
                f"[{color}]{app.status.value}[/{color}]",
                str(app.date_applied)
            )
        
        console.print(table)
    
    elif action == "summary":
        # Show status summary
        stats = summary()
        
        table = Table(title="Application Statistics")
        table.add_column("Status", style="bold")
        table.add_column("Count", style="cyan", justify="right")
        
        for status, count in stats.items():
            if status == "total":
                table.add_row("─" * 20, "─" * 5)
                table.add_row("[bold]TOTAL[/bold]", f"[bold]{count}[/bold]")
            else:
                table.add_row(status.upper(), str(count))
        
        console.print(table)
    
    elif action == "update":
        if not job_id or not status:
            console.print("[red]--job-id and --status are required for update[/red]")
            return
        
        try:
            new_status = JobStatus(status.lower())
            success = update_status(job_id, new_status, notes)
            
            if success:
                console.print(f"[green]✓ Updated {job_id} to {status}[/green]")
            else:
                console.print(f"[red]Failed to update {job_id}[/red]")
        except ValueError:
            console.print(f"[red]Invalid status: {status}[/red]")
            console.print(f"Valid statuses: {', '.join([s.value for s in JobStatus])}")
    
    elif action == "add":
        console.print("[yellow]Use 'apply' command to add applications, or manually add to applications.csv[/yellow]")
    
    else:
        console.print(f"[red]Unknown action: {action}[/red]")


@app.command()
def config():
    """Open config.yaml for editing."""
    import subprocess
    import sys
    import os
    
    config_file = Path("config.yaml")
    
    if not config_file.exists():
        # Create default config
        default_config = """# JobPilot Configuration

# API Keys for job boards (get free keys at these URLs)
api_keys:
  adzuna:
    # Get free API key at: https://developer.adzuna.com/
    app_id: "YOUR_ADZUNA_APP_ID"
    app_key: "YOUR_ADZUNA_APP_KEY"

# Your personal information (used for auto-filling forms)
personal_info:
  name: "Your Full Name"
  email: "your.email@example.com"
  phone: "555-0100"
  linkedin: "https://linkedin.com/in/yourprofile"
  resume_path: "data/resume.pdf"

# Job search preferences
search:
  keywords:
    - "Python Developer"
    - "Software Engineer"
  locations:
    - "Remote"
    - "New York, NY"
  
# Application settings
apply:
  auto_submit: false  # DANGEROUS: Auto-submit without review
  max_per_day: 10
  
# Scraper settings
scraper:
  rate_limit_delay: 2  # seconds between requests
  max_retries: 3
"""
        with open(config_file, 'w') as f:
            f.write(default_config)
        console.print(f"[green]✓ Created default config at {config_file}[/green]")
    
    # Open in default editor
    if sys.platform == "win32":
        subprocess.run(["notepad", str(config_file)])
    else:
        subprocess.run([os.environ.get("EDITOR", "nano"), str(config_file)])


@app.command()
def stats():
    """Show detailed statistics."""
    apps = load_applications()
    
    if not apps:
        console.print("[yellow]No applications yet[/yellow]")
        return
    
    console.print("\n[bold]📊 Application Statistics[/bold]\n")
    
    # Status breakdown
    stats = summary()
    console.print(f"Total Applications: [bold cyan]{stats['total']}[/bold cyan]")
    console.print(f"Applied: [blue]{stats['applied']}[/blue]")
    console.print(f"Interviews: [yellow]{stats['interview']}[/yellow]")
    console.print(f"Offers: [green]{stats['offer']}[/green]")
    console.print(f"Rejected: [red]{stats['rejected']}[/red]")
    
    # Success rate
    if stats['total'] > 0:
        interview_rate = (stats['interview'] / stats['total']) * 100
        offer_rate = (stats['offer'] / stats['total']) * 100
        console.print(f"\nInterview Rate: [yellow]{interview_rate:.1f}%[/yellow]")
        console.print(f"Offer Rate: [green]{offer_rate:.1f}%[/green]")


@app.command()
def export(
    summary_report: bool = typer.Option(False, "--summary", "-s", help="Export detailed summary report"),
    output: str = typer.Option(None, "--output", "-o", help="Output file path")
):
    """Export applications to Excel."""
    from tracker.excel_export import export_to_excel, export_summary_to_excel
    
    try:
        if summary_report:
            filepath = export_summary_to_excel(output)
            console.print(f"[green]✓ Exported summary report to {filepath}[/green]")
        else:
            filepath = export_to_excel(output)
            console.print(f"[green]✓ Exported applications to {filepath}[/green]")
        
        # Open the file
        import subprocess
        import sys
        if sys.platform == "win32":
            subprocess.run(["start", filepath], shell=True)
        elif sys.platform == "darwin":
            subprocess.run(["open", filepath])
        else:
            subprocess.run(["xdg-open", filepath])
    except ValueError as e:
        console.print(f"[red]{e}[/red]")
    except Exception as e:
        console.print(f"[red]Error exporting: {e}[/red]")


@app.command()
def dashboard():
    """Launch the web dashboard."""
    console.print("\n[bold blue]🚀 Starting JobPilot Dashboard...[/bold blue]")
    console.print("[green]📊 Access at: http://localhost:5000[/green]")
    console.print("[yellow]Press Ctrl+C to stop[/yellow]\n")
    
    import subprocess
    import sys
    
    # Run the dashboard
    dashboard_path = Path("apps/dashboard.py")
    if not dashboard_path.exists():
        console.print("[red]Dashboard not found! Make sure apps/dashboard.py exists.[/red]")
        return
    
    try:
        subprocess.run([sys.executable, str(dashboard_path)])
    except KeyboardInterrupt:
        console.print("\n[yellow]Dashboard stopped[/yellow]")


if __name__ == "__main__":
    app()