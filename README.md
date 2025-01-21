# Schedule Surfer

A web scraper for UCSD's Schedule of Classes using AgentQL and Playwright.

## Features
- Navigates through all subjects in UCSD's course schedule
- Handles pagination for each subject
- Skips subjects with no results
- Ensures each page is fully loaded before proceeding

## Requirements
- Python 3.x
- AgentQL
- Playwright
- python-dotenv

## Setup
1. Clone the repository
2. Install dependencies:
```bash
pip install agentql playwright python-dotenv
```
3. Create a `.env` file with your AgentQL API key:
```
AGENTQL_API_KEY=your_api_key_here
```

## Usage
Run the script:
```bash
python tritonscraper.py
```

## Note
This is a work in progress. The script currently navigates through subjects and handles pagination, with data scraping functionality to be added.
