import os
import logging
import re
import time
import agentql
from agentql.ext.playwright.sync_api import Page
from playwright.sync_api import sync_playwright, TimeoutError
from dotenv import load_dotenv
from airtable_integration import AirtableManager

# Set up logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
os.environ["AGENTQL_API_KEY"] = os.getenv("AGENTQL_API_KEY")

# Set the URL to the desired website
URL = "https://act.ucsd.edu/scheduleOfClasses/scheduleOfClassesStudent.htm"

def extract_course_data(page: Page):
    try:
        # Add debug logging for HTML content
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
        
        courses = page.evaluate("""() => {
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
        }""")
        
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

def select_subject_and_search(page: Page, subject_value: str, subject_text: str):
    try:
        # Ensure we're on the search page
        if not page.url.endswith(URL):
            page.goto(URL)
            time.sleep(1)  # Give the page a moment to load
        
        # Wait for the select element and its options to be available
        select = page.wait_for_selector('select[name="selectedSubjects"]')
        
        # Select the subject using JavaScript
        page.evaluate(f"""() => {{
            const select = document.querySelector('select[name="selectedSubjects"]');
            select.value = '{subject_value}';
            select.dispatchEvent(new Event('change'));
        }}""")
        
        log.info(f"Selected subject: {subject_text}")
        
        # Wait for and click the search button
        search_button = page.wait_for_selector('#socFacSubmit')
        if search_button:
            search_button.click()
            log.info("Clicked search button")
        else:
            log.error("Search button not found")
            return
        
        # Wait for navigation
        try:
            page.wait_for_load_state('networkidle', timeout=20000)
            log.info(f"Current URL: {page.url}")
            log.info(f"Page title: {page.title()}")
            
            # Handle pagination after successful search
            courses = handle_pagination(page)
            return courses
        except TimeoutError:
            log.error("Navigation timeout - skipping to next subject")
        except Exception as e:
            log.error(f"Error during search: {e}")
    except Exception as e:
        log.error(f"Error in select_subject_and_search: {e}")
    return []

def main():
    try:
        # Initialize Airtable manager
        airtable = AirtableManager()
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            
            # Navigate to the initial page
            page.goto(URL)
            page.wait_for_load_state('networkidle')
            log.info("Navigated to initial page")
            
            # Get all subjects
            subjects = get_all_subjects(page)
            log.info(f"Found {len(subjects)} subjects")
            
            # For testing, just process AAS
            test_subject = next(s for s in subjects if s['text'].startswith('AAS'))
            log.info(f"Testing with subject: {test_subject['text']}")
            
            # Select subject and search
            select_subject_and_search(page, test_subject['value'], test_subject['text'])
            
            # Wait for page to load after search
            page.wait_for_load_state('networkidle')
            
            # Extract course data
            courses = extract_course_data(page)
            
            # Print summary of extracted data
            log.info("\nExtracted Course Data Summary:")
            log.info(f"Found {len(courses)} courses")
            for course in courses:
                log.info(f"Course: {course['number']} - {course['name']} ({len(course['sections'])} sections)")
            
            # Upload courses to Airtable
            if courses:
                log.info("\nUploading courses to Airtable...")
                airtable.upload_courses(courses)
                log.info("Successfully uploaded all courses to Airtable")
            else:
                log.warning("No courses found to upload")
            
            browser.close()
            
    except Exception as e:
        log.error(f"Error in main: {e}")
        log.exception("Stack trace:")
        raise e  # Re-raise to see full traceback

if __name__ == "__main__":
    main()
