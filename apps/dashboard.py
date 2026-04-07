"""
Web Dashboard for JobPilot using Flask.

Run with: python apps/dashboard.py
Access at: http://localhost:5000
"""

from flask import Flask, render_template, jsonify, request, redirect, url_for
from tracker.tracker import load_applications, update_status, summary
from tracker.models import JobStatus
import json
from pathlib import Path
from datetime import datetime

app = Flask(__name__)


@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('dashboard.html')


@app.route('/api/applications')
def get_applications():
    """API endpoint to get all applications."""
    try:
        applications = load_applications()
        apps_data = [app.model_dump(mode='json') for app in applications]
        return jsonify({
            'success': True,
            'applications': apps_data,
            'count': len(apps_data)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/jobs')
def get_jobs():
    """API endpoint to get all scraped jobs."""
    try:
        jobs_file = Path('data/jobs.json')
        if not jobs_file.exists():
            return jsonify({
                'success': True,
                'jobs': [],
                'count': 0
            })
        
        with open(jobs_file, 'r') as f:
            jobs = json.load(f)
        
        return jsonify({
            'success': True,
            'jobs': jobs,
            'count': len(jobs)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/summary')
def get_summary():
    """API endpoint to get application statistics."""
    try:
        stats = summary()
        return jsonify({
            'success': True,
            'summary': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/applications/<job_id>/status', methods=['POST'])
def update_application_status(job_id):
    """API endpoint to update application status."""
    try:
        data = request.get_json()
        new_status = JobStatus(data.get('status'))
        notes = data.get('notes')
        
        success = update_status(job_id, new_status, notes)
        
        return jsonify({
            'success': success,
            'message': f'Updated status to {new_status.value}' if success else 'Update failed'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/stats')
def get_detailed_stats():
    """API endpoint for detailed statistics."""
    try:
        applications = load_applications()
        
        # Calculate various stats
        total = len(applications)
        
        if total == 0:
            return jsonify({
                'success': True,
                'stats': {
                    'total': 0,
                    'interview_rate': 0,
                    'offer_rate': 0,
                    'response_rate': 0
                }
            })
        
        stats_data = summary()
        
        interview_rate = (stats_data.get('interview', 0) / total) * 100
        offer_rate = (stats_data.get('offer', 0) / total) * 100
        response_rate = ((stats_data.get('interview', 0) + stats_data.get('offer', 0) + stats_data.get('rejected', 0)) / total) * 100
        
        # Applications over time
        apps_by_date = {}
        for app in applications:
            date_str = str(app.date_applied)
            apps_by_date[date_str] = apps_by_date.get(date_str, 0) + 1
        
        return jsonify({
            'success': True,
            'stats': {
                'total': total,
                'interview_rate': round(interview_rate, 1),
                'offer_rate': round(offer_rate, 1),
                'response_rate': round(response_rate, 1),
                'by_status': stats_data,
                'timeline': apps_by_date
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# HTML template as string (we'll create a templates folder structure)
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JobPilot Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        header {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }
        
        h1 {
            color: #667eea;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .subtitle {
            color: #666;
            font-size: 1.1em;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
        }
        
        .stat-value {
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            margin: 10px 0;
        }
        
        .stat-label {
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        
        .tab {
            background: white;
            border: none;
            padding: 15px 30px;
            border-radius: 10px;
            cursor: pointer;
            font-size: 1em;
            transition: all 0.3s ease;
            color: #666;
        }
        
        .tab.active {
            background: #667eea;
            color: white;
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        .content-section {
            display: none;
        }
        
        .content-section.active {
            display: block;
        }
        
        .table-container {
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            padding: 30px;
            overflow-x: auto;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
        }
        
        th {
            background: #f8f9fa;
            padding: 15px;
            text-align: left;
            font-weight: 600;
            color: #333;
            border-bottom: 2px solid #e9ecef;
        }
        
        td {
            padding: 15px;
            border-bottom: 1px solid #e9ecef;
        }
        
        tr:hover {
            background: #f8f9fa;
        }
        
        .status-badge {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
        }
        
        .status-applied { background: #e3f2fd; color: #1976d2; }
        .status-interview { background: #fff3e0; color: #f57c00; }
        .status-offer { background: #e8f5e9; color: #388e3c; }
        .status-rejected { background: #ffebee; color: #d32f2f; }
        .status-withdrawn { background: #f5f5f5; color: #757575; }
        
        .job-link {
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
        }
        
        .job-link:hover {
            text-decoration: underline;
        }
        
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #666;
        }
        
        .empty-state-icon {
            font-size: 4em;
            margin-bottom: 20px;
            opacity: 0.3;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            color: #666;
        }
        
        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🚀 JobPilot Dashboard</h1>
            <p class="subtitle">Track your job applications and opportunities</p>
        </header>
        
        <div class="stats-grid" id="stats">
            <div class="loading">
                <div class="spinner"></div>
                <p>Loading statistics...</p>
            </div>
        </div>
        
        <div class="tabs">
            <button class="tab active" onclick="switchTab('applications')">Applications</button>
            <button class="tab" onclick="switchTab('jobs')">Available Jobs</button>
        </div>
        
        <div id="applications" class="content-section active">
            <div class="table-container">
                <h2 style="margin-bottom: 20px;">Your Applications</h2>
                <div id="applications-content" class="loading">
                    <div class="spinner"></div>
                    <p>Loading applications...</p>
                </div>
            </div>
        </div>
        
        <div id="jobs" class="content-section">
            <div class="table-container">
                <h2 style="margin-bottom: 20px;">Available Jobs</h2>
                <div id="jobs-content" class="loading">
                    <div class="spinner"></div>
                    <p>Loading jobs...</p>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Tab switching
        function switchTab(tabName) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.content-section').forEach(s => s.classList.remove('active'));
            
            event.target.classList.add('active');
            document.getElementById(tabName).classList.add('active');
        }
        
        // Load statistics
        async function loadStats() {
            try {
                const response = await fetch('/api/stats');
                const data = await response.json();
                
                if (data.success) {
                    const stats = data.stats;
                    document.getElementById('stats').innerHTML = `
                        <div class="stat-card">
                            <div class="stat-label">Total Applications</div>
                            <div class="stat-value">${stats.total}</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-label">Interview Rate</div>
                            <div class="stat-value">${stats.interview_rate}%</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-label">Offer Rate</div>
                            <div class="stat-value">${stats.offer_rate}%</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-label">Response Rate</div>
                            <div class="stat-value">${stats.response_rate}%</div>
                        </div>
                    `;
                }
            } catch (error) {
                console.error('Error loading stats:', error);
            }
        }
        
        // Load applications
        async function loadApplications() {
            try {
                const response = await fetch('/api/applications');
                const data = await response.json();
                
                if (data.success && data.applications.length > 0) {
                    const tableHTML = `
                        <table>
                            <thead>
                                <tr>
                                    <th>Title</th>
                                    <th>Company</th>
                                    <th>Status</th>
                                    <th>Applied</th>
                                    <th>Source</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${data.applications.map(app => `
                                    <tr>
                                        <td><a href="${app.url}" target="_blank" class="job-link">${app.title}</a></td>
                                        <td>${app.company}</td>
                                        <td><span class="status-badge status-${app.status}">${app.status}</span></td>
                                        <td>${app.date_applied}</td>
                                        <td>${app.source}</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    `;
                    document.getElementById('applications-content').innerHTML = tableHTML;
                } else {
                    document.getElementById('applications-content').innerHTML = `
                        <div class="empty-state">
                            <div class="empty-state-icon">📭</div>
                            <h3>No applications yet</h3>
                            <p>Start applying to jobs to see them here!</p>
                        </div>
                    `;
                }
            } catch (error) {
                console.error('Error loading applications:', error);
            }
        }
        
        // Load jobs
        async function loadJobs() {
            try {
                const response = await fetch('/api/jobs');
                const data = await response.json();
                
                if (data.success && data.jobs.length > 0) {
                    const tableHTML = `
                        <table>
                            <thead>
                                <tr>
                                    <th>Title</th>
                                    <th>Company</th>
                                    <th>Location</th>
                                    <th>Source</th>
                                    <th>Scraped</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${data.jobs.map(job => `
                                    <tr>
                                        <td><a href="${job.url}" target="_blank" class="job-link">${job.title}</a></td>
                                        <td>${job.company}</td>
                                        <td>${job.location}</td>
                                        <td>${job.source}</td>
                                        <td>${job.date_scraped}</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    `;
                    document.getElementById('jobs-content').innerHTML = tableHTML;
                } else {
                    document.getElementById('jobs-content').innerHTML = `
                        <div class="empty-state">
                            <div class="empty-state-icon">🔍</div>
                            <h3>No jobs scraped yet</h3>
                            <p>Run the scraper to find jobs!</p>
                        </div>
                    `;
                }
            } catch (error) {
                console.error('Error loading jobs:', error);
            }
        }
        
        // Initialize
        loadStats();
        loadApplications();
        loadJobs();
        
        // Refresh every 30 seconds
        setInterval(() => {
            loadStats();
            loadApplications();
            loadJobs();
        }, 30000);
    </script>
</body>
</html>
"""

# Create templates directory and save HTML
def setup_templates():
    """Create templates directory and save the dashboard HTML."""
    templates_dir = Path('apps/templates')
    templates_dir.mkdir(parents=True, exist_ok=True)
    
    with open(templates_dir / 'dashboard.html', 'w') as f:
        f.write(DASHBOARD_HTML)


if __name__ == '__main__':
    setup_templates()
    print("🚀 Starting JobPilot Dashboard...")
    print("📊 Access dashboard at: http://localhost:5000")
    print("Press Ctrl+C to stop")
    app.run(debug=True, host='0.0.0.0', port=5000)