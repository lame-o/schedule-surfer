# 🌊 Schedule Surfer - UCSD Course Scraper

A powerful data automation tool that surfs through UCSD's Schedule of Classes, efficiently extracting and parsing course information. Built with modern web automation technologies, Schedule Surfer transforms raw HTML data into structured records in Airtable for seamless analysis and integration.

## 🎯 Current Capabilities

The surfer currently navigates through:
- AIP (Academic Internship Program)
- AAS (African American Studies)
- AWP (Analytical Writing Program)
- ANES (Anesthesiology)
- ANBI (Anthro/Biological Anthropology)

Successfully handling:
- 🔄 Multiple pages of results
- 🚫 "No classes found" scenarios
- 📊 Various enrollment states (FULL/Available)
- 📝 Different meeting types (Lecture, Discussion, Seminar)

## 🔄 Automation Pipeline

The surfer implements a robust data pipeline:

- 🤖 **Automated Navigation**: Efficiently traverses the Schedule of Classes interface
- 📊 **Intelligent Parsing**: Extracts structured data from complex HTML patterns
- 🔍 **Data Validation**: Ensures accuracy of scraped information
- 📥 **Automated Storage**: Direct integration with Airtable's API

## 🚀 Setup

1. **Clone Repository**
```bash
git clone [your-repo-url]
cd schedule-surfer
```

2. **Environment Setup**
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
playwright install
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
- Subject Code (e.g., AAS, AWP, ANBI)

📋 **Sections Schema**
- Section ID (unique identifier)
- Meeting Type
- Schedule (Days/Time)
- Location
- Instructor
- Enrollment Data (Available/Total seats)
- Course Reference

## ⚡ Execution

Start surfing:
```bash
python tritonscraper.py
```

The automation pipeline will execute, surfing through course data and populating your Airtable base with structured records.

## 🛠 Technology Stack

- **Python**: Core automation and data processing
- **Playwright**: Headless browser automation
- **PyAirtable**: Data storage and API integration

## Contributing

Feel free to open issues or submit pull requests with improvements.

## License

[Your chosen license]
