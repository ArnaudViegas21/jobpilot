@echo off
echo Setting up job-tracker project structure...

:: Create folders
mkdir data
mkdir scraper
mkdir tracker
mkdir applier
mkdir .vscode

:: Create data files
type nul > data\jobs.json
type nul > data\applications.csv
type nul > data\resume.json

:: Create scraper files
type nul > scraper\__init__.py
type nul > scraper\base.py
type nul > scraper\linkedin.py
type nul > scraper\indeed.py

:: Create tracker files
type nul > tracker\__init__.py
type nul > tracker\tracker.py
type nul > tracker\models.py

:: Create applier files
type nul > applier\__init__.py
type nul > applier\applier.py
type nul > applier\form_filler.py

:: Create root files
type nul > main.py
type nul > requirements.txt
type nul > config.yaml
type nul > .gitignore
type nul > README.md

:: Add basic .gitignore content
echo __pycache__/ >> .gitignore
echo *.pyc >> .gitignore
echo .env >> .gitignore
echo data/applications.csv >> .gitignore
echo data/resume.json >> .gitignore

:: Add basic requirements.txt content
echo playwright >> requirements.txt
echo beautifulsoup4 >> requirements.txt
echo httpx >> requirements.txt
echo pandas >> requirements.txt
echo pydantic >> requirements.txt
echo rich >> requirements.txt
echo typer >> requirements.txt
echo pyyaml >> requirements.txt

echo.
echo Project structure created successfully!
echo.
echo Next steps:
echo   1. cd into your project folder (if not already there)
echo   2. Run: pip install -r requirements.txt
echo   3. Run: playwright install
echo.
pause
