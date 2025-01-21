import os
import logging
import re
import time
import agentql
from agentql.ext.playwright.sync_api import Page
from playwright.sync_api import sync_playwright, TimeoutError
from dotenv import load_dotenv
from airtable_integration import AirtableManager
from typing import List, Dict

# Set up logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
os.environ["AGENTQL_API_KEY"] = os.getenv("AGENTQL_API_KEY")

# Set the URL to the desired website
URL = "https://act.ucsd.edu/scheduleOfClasses/scheduleOfClassesStudent.htm"

def extract_course_data(page: Page, subject_code: str = '') -> List[Dict]:
    """Extract course data from the page."""
    try:
        # Get HTML content for debugging
        html_content = page.content()
        log.info("Page HTML content length: %d", len(html_content))
        log.info("Looking for table.tbrdr...")
        
        # Check if table exists
        table_exists = page.evaluate("""() => {
            const table = document.querySelector('table.tbrdr');
            return table !== null;
        }""")
        log.info("Table exists: %s", table_exists)
        
        if not table_exists:
            log.error("Could not find course table on page")
            return []
        
        # Get row count
        row_count = page.evaluate("""() => {
            const rows = document.querySelectorAll('table.tbrdr tr');
            return rows.length;
        }""")
        log.info("Found %d rows in table", row_count)
        
        courses = page.evaluate("""(subject_code) => {
            const courses = [];
            let currentCourse = null;
            
            // Get all rows from the table
            const rows = Array.from(document.querySelectorAll('table.tbrdr tr'));
            console.log('Processing ' + rows.length + ' rows');
            
            for (let row of rows) {
                // Skip header rows and empty rows
                if (!row.querySelector('td')) {
                    console.log('Skipping row without td');
                    continue;
                }
                
                // Check if this is a course header row (contains course name and number)
                const isCourseHeader = row.querySelector('td.crsheader');
                if (isCourseHeader) {
                    console.log('Found course header row');
                    
                    // If we have a previous course with sections, add it to our list
                    if (currentCourse && currentCourse.sections.length > 0) {
                        console.log('Adding course: ' + currentCourse.number);
                        courses.push(currentCourse);
                    }
                    
                    // Extract course name and number
                    const courseNumberCell = row.querySelector('td.crsheader:nth-child(2)');
                    const courseNameCell = row.querySelector('td.crsheader span.boldtxt');
                    const unitsText = row.textContent.match(/\\(\\s*(\\d+)\\s*Units\\)/);
                    
                    // Only create a new course if we have both a number and a name
                    if (courseNumberCell && courseNameCell) {
                        console.log('Creating new course: ' + courseNumberCell.textContent.trim());
                        currentCourse = {
                            name: courseNameCell.textContent.trim(),
                            number: courseNumberCell.textContent.trim(),
                            units: unitsText ? unitsText[1] : '',
                            subject_code: subject_code,
                            sections: []
                        };
                    } else {
                        console.log('Missing course number or name');
                    }
                    continue;
                }
                
                // Check if this is a section row (contains class details)
                const isSection = row.classList.contains('sectxt');
                if (isSection && currentCourse) {
                    console.log('Found section row for course: ' + currentCourse.number);
                    const cells = Array.from(row.querySelectorAll('td'));
                    if (cells.length >= 13) {  
                        // Extract meeting type
                        const meetingType = cells[3].querySelector('span')?.getAttribute('title') || cells[3].textContent.trim();
                        
                        // Parse fields in correct order
                        const sectionId = cells[4].textContent.trim(); // Section ID is in the "Days" column
                        const days = cells[5].textContent.trim(); // Days is in the "Time" column
                        const time = cells[6].textContent.trim(); // Time is in the "Building" column
                        const building = cells[7].textContent.trim(); // Building is in the "Room" column
                        const room = cells[8].textContent.trim(); // Room is in the "Instructor" column
                        const instructor = cells[9] ? cells[9].textContent.trim() : 'N/A'; // Instructor is in the next column
                        
                        // Extract seat counts from the enrollment cells
                        const availableCell = cells[10];
                        const limitCell = cells[11];
                        
                        let available = 0, limit = 0;
                        
                        // Check if section is full
                        const fullText = availableCell.querySelector('.ertext')?.textContent.trim();
                        if (fullText === 'FULL') {
                            available = 0;
                            limit = parseInt(limitCell.textContent.trim()) || 0;
                        } else {
                            // Try to get direct numbers
                            const availText = availableCell.textContent.trim();
                            const limitText = limitCell.textContent.trim();
                            available = parseInt(availText) || 0;
                            limit = parseInt(limitText) || 0;
                        }
                        
                        const section = {
                            sectionId,
                            meetingType,
                            days,
                            time,
                            building,
                            room,
                            instructor,
                            available,
                            limit
                        };
                        
                        // Clean up the data
                        for (const key in section) {
                            if (typeof section[key] === 'string') {
                                section[key] = section[key].replace(/\\s+/g, ' ').trim();
                                if (!section[key]) {
                                    section[key] = 'N/A';
                                }
                            }
                        }
                        
                        currentCourse.sections.push(section);
                        console.log('Added section: ' + section.sectionId);
                    } else {
                        console.log('Section row has insufficient cells: ' + cells.length);
                    }
                }
            }
            
            // Don't forget to add the last course if it has sections
            if (currentCourse && currentCourse.sections.length > 0) {
                console.log('Adding final course: ' + currentCourse.number);
                courses.push(currentCourse);
            }
            
            console.log('Returning ' + courses.length + ' courses');
            return courses;
        }""", subject_code)
        
        # Log the extracted data in a more structured way
        log.info(f"\nExtracted {len(courses)} courses:")
        for course in courses:
            log.info(f"\nCourse: {course['number']} - {course['name']}")
            log.info(f"  Units: {course.get('units', 'N/A')}")
            log.info(f"  Total Sections: {len(course['sections'])}")
            for section in course['sections']:
                log.info(f"    Section {section['sectionId']}:")
                log.info(f"      Type: {section['meetingType']}")
                log.info(f"      Days: {section['days']}")
                log.info(f"      Time: {section['time']}")
                log.info(f"      Location: {section['building']} {section['room']}")
                log.info(f"      Instructor: {section['instructor']}")
                log.info(f"      Seats: {section['available']}/{section['limit']} available")
        
        return courses
        
    except Exception as e:
        log.error(f"Error extracting course data: {e}")
        log.exception("Stack trace:")
        return []

def parse_enrollment(cell):
    """Parse enrollment information from a cell."""
    try:
        text = cell.text_content().strip()
        if 'FULL' in text:
            available = 0
            limit_cell = cell.locator('xpath=following-sibling::td[1]')
            limit = int(limit_cell.text_content().strip()) if limit_cell.count() > 0 else 0
        else:
            available = int(text) if text.isdigit() else 0
            limit_cell = cell.locator('xpath=following-sibling::td[1]')
            limit = int(limit_cell.text_content().strip()) if limit_cell.count() > 0 else 0
        return available, limit
    except Exception as e:
        log.error(f"Error parsing enrollment: {e}")
        return 0, 0

def handle_pagination(page: Page):
    try:
        # Wait for either the results table or "No Result Found" message
        page.wait_for_selector('table.tbrdr, div.centeralign', timeout=20000)
        
        # Check for "No Result Found" message
        no_results = page.query_selector('div.centeralign')
        if no_results and "No Result Found" in no_results.text_content():
            log.info("No results found")
            return []
            
        # Extract course data from current page
        courses = extract_course_data(page)
        
        return courses
        
    except Exception as e:
        log.error(f"Error during pagination: {e}")
        return []

def get_all_subjects(page: Page):
    try:
        # Wait for the select element and its options to be available
        page.wait_for_selector('select[name="selectedSubjects"]')
        
        # Wait for options to be loaded
        page.wait_for_function("""
            () => {
                const select = document.querySelector('select[name="selectedSubjects"]');
                return select && select.options && select.options.length > 0;
            }
        """, timeout=20000)
        
        subjects = page.evaluate("""() => {
            const select = document.querySelector('select[name="selectedSubjects"]');
            const options = Array.from(select.options);
            return options.map(opt => ({
                value: opt.value,
                text: opt.text.trim()
            })).filter(opt => opt.text && opt.value);
        }""")
        
        return subjects
    except Exception as e:
        log.error(f"Error getting subjects: {e}")
        return []

def select_subject_and_search(page: Page, subject_value: str, subject_text: str) -> List[Dict]:
    """Select a subject and click search."""
    try:
        # Go back to the main page
        page.goto(URL)
        page.wait_for_load_state('networkidle')
        
        # Log the HTML for debugging
        html_content = page.content()
        log.info("Page HTML:")
        log.info(html_content[:1000])  # First 1000 chars
        
        # Add a delay to see what's happening
        time.sleep(2)
        
        # Select the subject using the correct selector
        subject_selector = page.locator("select[name='selectedSubjects']")
        subject_selector.select_option(subject_value)
        log.info(f"Selected subject: {subject_text}")
        
        # Add another delay
        time.sleep(2)
        
        # Click search using the correct selector
        search_button = page.locator("#socFacSubmit")
        search_button.click()
        log.info("Clicked search button")
        
        # Wait for results to load
        page.wait_for_load_state('networkidle')
        
    except Exception as e:
        log.error(f"Error in select_subject_and_search: {e}")

def scrape_courses(page: Page, airtable: AirtableManager):
    try:
        # Navigate to initial page
        page.goto("https://act.ucsd.edu/scheduleOfClasses/scheduleOfClassesStudent.htm")
        logging.info("Navigated to initial page")

        # Get all subjects
        subjects = get_all_subjects(page)
        subject_count = len(subjects)
        logging.info(f"Found {subject_count} subjects")

        # Define the subjects to test (up to ANBI)
        test_subjects = []
        for subject in subjects:
            subject_text = subject['text']
            if subject_text.startswith("ANBI"):
                test_subjects.append(subject)
                break
            test_subjects.append(subject)
        
        logging.info(f"Testing {len(test_subjects)} subjects: {', '.join(s['text'] for s in test_subjects)}")

        # Process each subject
        for subject in test_subjects:
            try:
                logging.info(f"Processing subject: {subject['text']}")
                
                # Extract subject code from the text (e.g., "AAS - African American Studies" -> "AAS")
                subject_code = subject['text'].split(' - ')[0]
                
                # Select the subject and search
                select_subject_and_search(page, subject['value'], subject['text'])
                logging.info(f"Selected subject: {subject['text']}")
                
                # Wait for page load
                page.wait_for_load_state('networkidle')
                
                # Log current state
                current_url = page.url
                page_title = page.title()
                html_content = page.content()
                logging.info(f"Current URL: {current_url}")
                logging.info(f"Page title: {page_title}")
                logging.info(f"Page HTML content length: {len(html_content)}")
                
                # Check for "No classes found" message
                no_results = page.query_selector('td.NoClasses')
                if no_results and "No classes found" in no_results.text_content():
                    logging.info(f"No classes found for subject: {subject['text']}")
                    continue
                
                # Process all pages for this subject
                while True:
                    # Extract courses from current page
                    courses = extract_course_data(page, subject_code)
                    if courses:
                        logging.info(f"\nExtracted {len(courses)} courses from {subject['text']}:")
                        for course in courses:
                            logging.info(f"\nCourse: {course['number']} - {course['name']}")
                            logging.info(f"  Units: {course['units']}")
                            logging.info(f"  Total Sections: {len(course['sections'])}")
                            for section in course['sections']:
                                logging.info(f"    Section {section['sectionId']}:")
                                logging.info(f"      Type: {section['meetingType']}")
                                logging.info(f"      Days: {section['days']}")
                                logging.info(f"      Time: {section['time']}")
                                logging.info(f"      Location: {section['building']} {section['room']}")
                                logging.info(f"      Instructor: {section['instructor']}")
                                logging.info(f"      Seats: {section['available']}/{section['limit']} available")
                        
                        # Upload to Airtable
                        logging.info("\nUploading courses to Airtable...")
                        airtable.upload_courses(courses)
                    
                    # Check for next page
                    next_page = page.query_selector("input[value='Next']")
                    if next_page and not next_page.is_disabled():
                        next_page.click()
                        page.wait_for_load_state('networkidle')
                        logging.info("Moved to next page")
                    else:
                        break
                
            except Exception as e:
                logging.error(f"Error processing subject {subject['text']}: {e}")
                logging.exception("Stack trace:")
                continue

    except Exception as e:
        logging.error(f"Error in scrape_courses: {e}")
        logging.exception("Stack trace:")

def main():
    try:
        # Initialize Airtable manager
        airtable = AirtableManager()
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            
            # Scrape courses
            scrape_courses(page, airtable)
            
            browser.close()
            
    except Exception as e:
        log.error(f"Error in main: {e}")
        log.exception("Stack trace:")
        raise e  # Re-raise to see full traceback

if __name__ == "__main__":
    main()
