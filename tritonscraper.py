import os
import logging
import re
import time
import agentql
from agentql.ext.playwright.sync_api import Page
from playwright.sync_api import sync_playwright, TimeoutError
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
os.environ["AGENTQL_API_KEY"] = os.getenv("AGENTQL_API_KEY")

# Set the URL to the desired website
URL = "https://act.ucsd.edu/scheduleOfClasses/scheduleOfClassesStudent.htm"

def handle_pagination(page: Page):
    try:
        # Wait for either the results table or "No classes found" message
        page.wait_for_selector('table.tbrdr, div.centeralign', timeout=5000)
        
        # Check for "No Result Found" message
        no_results = page.query_selector('div.centeralign')
        if no_results and "No Result Found" in no_results.inner_text():
            log.info("No results found for this subject")
            return
        
        # Check if there are any results
        if not page.query_selector('table.tbrdr'):
            log.info("No results table found for this subject")
            return
        
        while True:
            # Log current page info
            current_page = page.evaluate("""() => {
                const pageText = document.querySelector('td[align="right"]');
                return pageText ? pageText.textContent.trim() : null;
            }""")
            log.info(f"Current page info: {current_page}")
            
            # Extract current page number using regex
            match = re.search(r'Page\s*\((\d+)\s*of\s*(\d+)\)', current_page)
            if not match:
                log.error(f"Could not parse page numbers from: {current_page}")
                break
                
            current_page_number = int(match.group(1))
            total_pages = int(match.group(2))
            log.info(f"On page {current_page_number} of {total_pages}")
            
            # Wait for the page content to be fully loaded
            page.wait_for_selector('table.tbrdr')
            # Wait for all cells in the table to be loaded
            page.wait_for_selector('table.tbrdr td')
            # Wait for network to be idle to ensure all content is loaded
            page.wait_for_load_state('networkidle')
            
            if current_page_number >= total_pages:
                log.info("Reached last page")
                break
            
            # Click the next page number
            next_page_link = page.query_selector(f'a[href*="page={current_page_number + 1}"]')
            if not next_page_link:
                log.error(f"Could not find link to page {current_page_number + 1}")
                break
                
            # Click next page
            next_page_link.click()
            log.info(f"Clicked page {current_page_number + 1}")
            
            # Wait for navigation and table refresh
            page.wait_for_load_state('networkidle')
            page.wait_for_selector('table.tbrdr')
    except Exception as e:
        log.error(f"Error during pagination: {e}")

def get_all_subjects(page: Page):
    """Get list of all subject options"""
    try:
        # Wait for the select element and its options to be available
        select = page.wait_for_selector('select[name="selectedSubjects"]')
        
        # Wait for options to be loaded
        page.wait_for_function("""
            () => {
                const select = document.querySelector('select[name="selectedSubjects"]');
                return select && select.options && select.options.length > 0;
            }
        """)
        
        # Get all subject options
        subjects = page.evaluate("""() => {
            const select = document.querySelector('select[name="selectedSubjects"]');
            const options = Array.from(select.options);
            console.log('Found', options.length, 'subjects');
            return options.map(opt => ({
                value: opt.value,
                text: opt.text.trim()
            })).filter(opt => opt.text && opt.value);  // Filter out empty options
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
            page.wait_for_load_state('networkidle', timeout=10000)
            log.info(f"Current URL: {page.url}")
            log.info(f"Page title: {page.title()}")
            
            # Handle pagination after successful search
            handle_pagination(page)
        except TimeoutError:
            log.error("Navigation timeout - skipping to next subject")
        except Exception as e:
            log.error(f"Error during search: {e}")
        finally:
            # Always try to return to search page
            try:
                page.goto(URL)
                time.sleep(1)  # Give the page a moment to load
                log.info("Returned to search page")
            except Exception as e:
                log.error(f"Failed to return to search page: {e}")
    except Exception as e:
        log.error(f"Error in select_subject_and_search: {e}")

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})  # Set a large viewport
        page = agentql.wrap(context.new_page())
        
        try:
            # Navigate to the initial page
            page.goto(URL)
            log.info("Navigated to initial page")
            
            # Get all subjects
            subjects = get_all_subjects(page)
            log.info(f"Found {len(subjects)} subjects")
            
            # Process each subject
            for i, subject in enumerate(subjects, 1):
                log.info(f"Processing subject {i} of {len(subjects)}: {subject['text']}")
                select_subject_and_search(page, subject['value'], subject['text'])
            
            log.info("Finished processing all subjects")
            
        except Exception as e:
            log.error(f"An error occurred: {e}")
        finally:
            context.close()
            browser.close()

if __name__ == "__main__":
    main()
