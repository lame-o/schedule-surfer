import os
from typing import Dict, List
from pyairtable import Table
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

log = logging.getLogger(__name__)

class AirtableManager:
    def __init__(self):
        # Get environment variables
        self.api_key = os.getenv('AIRTABLE_API_KEY')
        self.base_id = os.getenv('AIRTABLE_BASE_ID')
        
        # Extract table IDs from the full paths
        courses_table_path = os.getenv('AIRTABLE_TABLE_NAME_COURSES', '')
        sections_table_path = os.getenv('AIRTABLE_TABLE_NAME_SECTIONS', '')
        
        self.courses_table_id = courses_table_path.split('/')[0] if '/' in courses_table_path else courses_table_path
        self.sections_table_id = sections_table_path.split('/')[0] if '/' in sections_table_path else sections_table_path
        
        if not all([self.api_key, self.base_id, self.courses_table_id, self.sections_table_id]):
            raise ValueError("Missing required Airtable environment variables")
        
        # Initialize Airtable tables
        self.courses_table = Table(self.api_key, self.base_id, self.courses_table_id)
        self.sections_table = Table(self.api_key, self.base_id, self.sections_table_id)
        
        log.info(f"Initialized Airtable connection with base ID: {self.base_id}")
        log.info(f"Using courses table: {self.courses_table_id}")
        log.info(f"Using sections table: {self.sections_table_id}")
    
    def create_course(self, course: Dict) -> str:
        """Create a course record in Airtable and return its ID."""
        try:
            # Check if course has any Lecture or Discussion sections
            has_valid_sections = False
            for section in course.get('sections', []):
                meeting_type = section['meetingType'].upper()
                if meeting_type in ['LECTURE', 'DISCUSSION', 'LE', 'DI']:
                    has_valid_sections = True
                    break
            
            if not has_valid_sections:
                log.info(f"Skipping course {course['number']} - no Lecture or Discussion sections")
                return None
            
            # Clean up course data
            course_data = {
                'Course Number': course['number'],
                'Course Name': course['name'],
                'Units': course.get('units', 'N/A'),
                'Subject Code': course.get('subject_code', 'N/A'),
            }
            
            # Create course record
            record = self.courses_table.create(course_data)
            log.info(f"Created course: {course['number']} - {course['name']}")
            return record['id']
            
        except Exception as e:
            log.error(f"Error creating course {course.get('number', 'unknown')}: {e}")
            return None
    
    def create_section(self, section: Dict, course_id: str, course: Dict) -> str:
        """Create a section record in Airtable and return its ID."""
        try:
            # Only process Lecture and Discussion sections
            meeting_type = section['meetingType'].upper()
            if meeting_type not in ['LECTURE', 'DISCUSSION', 'LE', 'DI']:
                log.info(f"Skipping section {section['sectionId']} with meeting type {meeting_type}")
                return None
            
            # Clean up section data
            section_data = {
                'Section ID': section['sectionId'],
                'Meeting Type': section['meetingType'],
                'Days': section['days'],
                'Time': section['time'],
                'Building': section['building'],
                'Room': section['room'],
                'Instructor': section['instructor'],
                'Available Seats': section.get('available', 0),
                'Seat Limit': section.get('limit', 0),
                'Course Link': [course_id],  # Link to the parent course
                'Subject Code': course.get('subject_code', 'N/A'),  # Add subject code from course
            }
            
            # Create section record
            record = self.sections_table.create(section_data)
            log.info(f"Created section: {section['sectionId']}")
            return record['id']
            
        except Exception as e:
            log.error(f"Error creating section {section.get('sectionId', 'unknown')}: {e}")
            return None
    
    def upload_courses(self, courses: List[Dict]) -> None:
        """Upload a list of courses and their sections to Airtable."""
        try:
            log.info(f"Starting upload of {len(courses)} courses to Airtable")
            for course in courses:
                # Create course record
                course_id = self.create_course(course)
                if not course_id:
                    continue
                
                # Create section records
                for section in course['sections']:
                    self.create_section(section, course_id, course)
            log.info("Finished uploading courses to Airtable")
                    
        except Exception as e:
            log.error(f"Error uploading courses: {e}")
            log.exception("Stack trace:")
