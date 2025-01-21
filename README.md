# 🎓 UCSD Schedule Scraper

An automated data extraction tool that efficiently scrapes and parses course information from UCSD's Schedule of Classes. Built with modern web automation technologies, it transforms raw HTML data into structured records in Airtable for seamless analysis and integration.

## 🔄 Automation Pipeline

The scraper implements a robust data pipeline:

- 🤖 **Automated Navigation**: Efficiently traverses the Schedule of Classes interface
- 📊 **Intelligent Parsing**: Extracts structured data from complex HTML patterns
- 🔍 **Data Validation**: Ensures accuracy of scraped information
- 📥 **Automated Storage**: Direct integration with Airtable's API

## 🚀 Setup

1. **Clone Repository**
```bash
git clone [your-repo-url]
cd tritonscraper
```

2. **Environment Setup**
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Airtable Configuration**
Configure environment variables in `.env`:
```
AIRTABLE_API_KEY=your_api_key
AIRTABLE_BASE_ID=your_base_id
AIRTABLE_TABLE_NAME_COURSES=your_courses_table_id
AIRTABLE_TABLE_NAME_SECTIONS=your_sections_table_id
```

4. **Data Schema Setup**

📊 **Courses Schema**
- Course Number (identifier)
- Course Name
- Units

📋 **Sections Schema**
- Section ID (unique identifier)
- Meeting Type
- Schedule (Days/Time)
- Location
- Instructor
- Enrollment Data
- Course Reference

## ⚡ Execution

Initialize the scraper:
```bash
python tritonscraper.py
```

The automation pipeline will execute, extracting course data and populating your Airtable base with structured records.

## 🛠 Technology Stack

- **Python**: Core automation and data processing
- **Playwright**: Headless browser automation
- **PyAirtable**: Data storage and API integration
