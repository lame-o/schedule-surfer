# UCSD Schedule of Classes Scraper

A Python-based web scraper that extracts course data from UCSD's Schedule of Classes and stores it in Airtable for better organization and readability.

## Features

- Scrapes course data from UCSD's Schedule of Classes using Playwright
- Stores data in Airtable with a clean, organized structure
- Captures detailed information for both courses and sections:
  - Course level: number, name, units
  - Section level: section ID, meeting type, days, time, location, instructor, seat availability

## Setup

1. Clone the repository:
```bash
git clone [your-repo-url]
cd tritonscraper
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up your environment variables in a `.env` file:
```
AIRTABLE_API_KEY=your_api_key
AIRTABLE_BASE_ID=your_base_id
AIRTABLE_TABLE_NAME_COURSES=your_courses_table_id
AIRTABLE_TABLE_NAME_SECTIONS=your_sections_table_id
```

5. Set up your Airtable base with two tables:

Courses table with fields:
- Course Number (Single line text)
- Course Name (Single line text)
- Units (Single line text)

Sections table with fields:
- Section ID (Single line text)
- Meeting Type (Single line text)
- Days (Single line text)
- Time (Single line text)
- Building (Single line text)
- Room (Single line text)
- Instructor (Single line text)
- Available Seats (Number)
- Seat Limit (Number)
- Course Link (Link to Courses table)

## Usage

Run the scraper:
```bash
python tritonscraper.py
```

The script will:
1. Navigate to UCSD's Schedule of Classes
2. Extract course data for the specified subject
3. Upload the data to your Airtable base

## Dependencies

- Playwright: Web scraping and browser automation
- PyAirtable: Airtable API integration
- python-dotenv: Environment variable management

## Contributing

Feel free to open issues or submit pull requests with improvements.

## License

[Your chosen license]
