# 📚 UCSD Schedule Scraper

Say goodbye to endless clicking through UCSD's Schedule of Classes! This smart scraper automatically gathers course data and presents it beautifully in Airtable, making course planning a breeze.

## ✨ What It Does

This tool transforms messy course data into organized, easy-to-read information in Airtable:

- 🎯 **Course Details**: Numbers, names, and unit counts
- 📅 **Section Info**: Meeting times, locations, and instructors
- 💺 **Real-time Availability**: Track open seats and enrollment limits
- 🔄 **Automated Updates**: Just run and watch your Airtable fill up

## 🚀 Quick Start

1. **Get the code**
```bash
git clone [your-repo-url]
cd tritonscraper
```

2. **Set up your environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure Airtable**
Create a `.env` file with your Airtable credentials:
```
AIRTABLE_API_KEY=your_api_key
AIRTABLE_BASE_ID=your_base_id
AIRTABLE_TABLE_NAME_COURSES=your_courses_table_id
AIRTABLE_TABLE_NAME_SECTIONS=your_sections_table_id
```

4. **Set up your Airtable tables**

📘 **Courses Table**
- Course Number
- Course Name
- Units

📗 **Sections Table**
- Section ID
- Meeting Type
- Days & Time
- Location (Building + Room)
- Instructor
- Seat Availability
- Course Link (connects to Courses table)

## 🎮 Usage

Just run:
```bash
python tritonscraper.py
```

Then sit back and watch as your Airtable fills up with neatly organized course data! 

## 🛠 Tech Stack

- **Playwright**: Handles the web scraping magic
- **PyAirtable**: Keeps your data organized
- **python-dotenv**: Manages your secrets
