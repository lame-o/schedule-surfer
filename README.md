# Schedule Surfer - UCSD Course Scraper

A Python-based web scraper for UCSD's Schedule of Classes that extracts detailed course information and stores it in Airtable for better organization and accessibility.

## Features

- Scrapes course data from UCSD's Schedule of Classes website
- Handles multiple subjects and pagination
- Extracts detailed course information including:
  - Course number and name
  - Subject code
  - Units
  - Multiple sections per course
  - Meeting times and locations
  - Instructor information
  - Enrollment numbers (available/total seats)
- Stores data in Airtable for easy access and organization
- Handles various edge cases:
  - Subjects with no courses
  - Multiple pages of results
  - Full sections
  - Various meeting types (Lecture, Discussion, Seminar, etc.)

## Requirements

- Python 3.7+
- Playwright
- PyAirtable
- python-dotenv

## Installation

1. Clone the repository:
```bash
git clone [your-repo-url]
cd tritonscraper
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install Playwright browsers:
```bash
playwright install
```

4. Create a `.env` file with your Airtable credentials:
```
AIRTABLE_API_KEY=your_api_key
AIRTABLE_BASE_ID=your_base_id
AIRTABLE_TABLE_NAME_COURSES=your_courses_table_id
AIRTABLE_TABLE_NAME_SECTIONS=your_sections_table_id
```

## Airtable Setup

1. Create a new Airtable base
2. Create two tables:
   - Courses table with fields:
     - Course Number (Single line text)
     - Course Name (Single line text)
     - Units (Single line text)
     - Subject Code (Single line text)
   - Sections table with fields:
     - Section ID (Single line text)
     - Meeting Type (Single line text)
     - Days (Single line text)
     - Time (Single line text)
     - Building (Single line text)
     - Room (Single line text)
     - Instructor (Single line text)
     - Available Seats (Number)
     - Total Seats (Number)
     - Course (Link to Courses table)

## Usage

Run the scraper:
```bash
python tritonscraper.py
```

The script will:
1. Navigate to UCSD's Schedule of Classes
2. Scrape data for multiple subjects
3. Upload the data to your Airtable base
4. Handle pagination automatically
5. Log progress and any errors

## Contributing

Feel free to open issues or submit pull requests with improvements.

## License

[Your chosen license]
