import logging
import os
import random
import threading
import time
import xml.etree.ElementTree as ET
from typing import Dict, Optional
from xml.dom import minidom

import queue

# Configuration constants
CONFIG = {
    'BUFFER_SIZE': 10,
    'XML_DIR': './xml_files',
    'PRODUCER_DELAY_MIN': 0.3,
    'PRODUCER_DELAY_MAX': 1.0,
    'CONSUMER_DELAY_MIN': 0.5,
    'CONSUMER_DELAY_MAX': 1.5,
    'MAX_STUDENTS': 10,
    'SEMAPHORE_TIMEOUT': 5.0,  # Timeout for semaphore acquires
}

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ITStudent class definition
class ITStudent:
    """Represents an IT student with personal and academic information."""

    def __init__(self, name: str = "", student_id: str = "", programme: str = "", courses: Dict[str, float] = None):
        """Initialize ITStudent with name, ID, programme, and courses."""
        self.name = name
        self.student_id = student_id
        self.programme = programme
        self.courses = courses if courses else {}

    def calculate_average(self) -> float:
        """Calculate the average mark across all courses."""
        if not self.courses:
            return 0.0
        return sum(self.courses.values()) / len(self.courses)

    def passed(self) -> bool:
        """Check if student passed (average >= 50)."""
        return self.calculate_average() >= 50.0

    def to_dict(self) -> dict:
        """Convert student to dictionary representation."""
        return {
            'name': self.name,
            'student_id': self.student_id,
            'programme': self.programme,
            'courses': self.courses
        }

    @staticmethod
    def from_dict(data: dict) -> 'ITStudent':
        """Create ITStudent from dictionary, with validation."""
        required_keys = ['name', 'student_id', 'programme', 'courses']
        if not all(key in data for key in required_keys):
            raise ValueError("Missing required fields in student data")

        if not isinstance(data['courses'], dict):
            raise ValueError("Courses must be a dictionary")

        return ITStudent(
            name=str(data['name']),
            student_id=str(data['student_id']),
            programme=str(data['programme']),
            courses=data['courses']
        )

    def __str__(self) -> str:
        """String representation of the student."""
        avg = self.calculate_average()
        status = "PASS" if self.passed() else "FAIL"

        course_info = "\n    ".join([f"{course}: {mark:.2f}" for course, mark in self.courses.items()])

        return f"""Student Name: {self.name}
Student ID: {self.student_id}
Programme: {self.programme}
Courses and Marks:
    {course_info}
Average: {avg:.2f}%
Status: {status}
{'-'*50}"""


# XML Handler class
class XMLHandler:
    """Handles XML serialization and deserialization of ITStudent objects."""

    @staticmethod
    def generate_xml_filename(student_num: int) -> str:
        """Generate XML filename for a student number."""
        return f"student{student_num}.xml"

    @staticmethod
    def save_student_to_xml(student: ITStudent, filename: str):
        """Save student data to XML file with error handling."""
        try:
            root = ET.Element("ITStudent")

            name_elem = ET.SubElement(root, "Name")
            name_elem.text = student.name

            id_elem = ET.SubElement(root, "StudentID")
            id_elem.text = student.student_id

            programme_elem = ET.SubElement(root, "Programme")
            programme_elem.text = student.programme

            courses_elem = ET.SubElement(root, "Courses")
            for course, mark in student.courses.items():
                course_elem = ET.SubElement(courses_elem, "Course")
                course_elem.set("name", course)
                course_elem.set("mark", str(mark))

            # Pretty print XML
            xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")

            with open(filename, 'w', encoding='utf-8') as f:
                f.write(xml_str)
        except Exception as e:
            logger.error(f"Failed to save student to XML {filename}: {e}")
            raise

    @staticmethod
    def load_student_from_xml(filename: str) -> ITStudent:
        """Load student data from XML file with error handling."""
        try:
            tree = ET.parse(filename)
            root = tree.getroot()

            name_elem = root.find("Name")
            if name_elem is None or name_elem.text is None:
                raise ValueError("Missing or empty Name element")

            student_id_elem = root.find("StudentID")
            if student_id_elem is None or student_id_elem.text is None:
                raise ValueError("Missing or empty StudentID element")

            programme_elem = root.find("Programme")
            if programme_elem is None or programme_elem.text is None:
                raise ValueError("Missing or empty Programme element")

            name = name_elem.text
            student_id = student_id_elem.text
            programme = programme_elem.text

            courses = {}
            courses_elem = root.find("Courses")
            if courses_elem is None:
                raise ValueError("Missing Courses element")

            for course_elem in courses_elem.findall("Course"):
                course_name = course_elem.get("name")
                mark_str = course_elem.get("mark")
                if course_name is None or mark_str is None:
                    raise ValueError("Missing course name or mark")
                try:
                    mark = float(mark_str)
                except ValueError:
                    raise ValueError(f"Invalid mark value: {mark_str}")
                courses[course_name] = mark

            return ITStudent(name, student_id, programme, courses)
        except ET.ParseError as e:
            logger.error(f"XML parsing error in {filename}: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to load student from XML {filename}: {e}")
            raise

    @staticmethod
    def clear_xml_file(filename: str):
        """Clear or delete the XML file."""
        try:
            # Option 1: Clear content (set empty)
            with open(filename, 'w') as f:
                f.write('')
            # Option 2: Or delete the file completely
            # os.remove(filename)
        except FileNotFoundError:
            logger.warning(f"File {filename} not found for clearing")
        except Exception as e:
            logger.error(f"Failed to clear XML file {filename}: {e}")


# Random Student Generator
class StudentGenerator:
    """Generates random ITStudent objects for testing."""

    FIRST_NAMES = ["John", "Jane", "Michael", "Sarah", "David", "Emma", "James", "Olivia", "Robert", "Sophia",
                   "William", "Ava", "Joseph", "Isabella", "Thomas", "Mia", "Charles", "Abigail", "Christopher", "Emily"]
    LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
                  "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"]
    PROGRAMMES = ["Computer Science", "Software Engineering", "Information Technology",
                  "Cybersecurity", "Data Science", "AI & Machine Learning", "Computer Engineering"]
    COURSES = ["Programming", "Database", "Networking", "Web Development", "Algorithms",
               "OS", "Security", "Data Structures", "Cloud Computing", "Mobile Development"]

    @staticmethod
    def generate_random_name() -> str:
        """Generate a random full name."""
        return f"{random.choice(StudentGenerator.FIRST_NAMES)} {random.choice(StudentGenerator.LAST_NAMES)}"

    @staticmethod
    def generate_random_id() -> str:
        """Generate a random 8-digit student ID."""
        return str(random.randint(10000000, 99999999))

    @staticmethod
    def generate_random_courses() -> Dict[str, float]:
        """Generate random courses with marks."""
        num_courses = random.randint(4, 7)
        selected_courses = random.sample(StudentGenerator.COURSES, num_courses)
        return {course: round(random.uniform(30, 100), 2) for course in selected_courses}

    @staticmethod
    def generate_random_student() -> ITStudent:
        """Generate a complete random student."""
        return ITStudent(
            name=StudentGenerator.generate_random_name(),
            student_id=StudentGenerator.generate_random_id(),
            programme=random.choice(StudentGenerator.PROGRAMMES),
            courses=StudentGenerator.generate_random_courses()
        )


# Shared Buffer class with semaphores
class SharedBuffer:
    """Shared buffer for producer-consumer problem using semaphores."""

    def __init__(self, size: int):
        """Initialize the shared buffer with given size."""
        self.buffer = queue.Queue(maxsize=size)
        self.mutex = threading.Semaphore(1)  # Binary semaphore for mutual exclusion
        self.empty = threading.Semaphore(size)  # Counts empty slots
        self.full = threading.Semaphore(0)  # Counts filled slots
        self.produced_count = 0
        self.consumed_count = 0
        self._lock = threading.Lock()  # For protecting counters
        self._stop_event = threading.Event()  # For clean shutdown

    def insert(self, item: int, producer_name: str = "Producer") -> bool:
        """Producer inserts item into buffer using semaphores with timeouts."""
        logger.info(f"{producer_name}: Attempting to insert {item}...")

        # Wait for empty slot (Rule 1: Producer waits if buffer is full)
        logger.debug(f"{producer_name}: Checking for empty slots (empty={self.empty._value})...")
        if not self.empty.acquire(timeout=CONFIG['SEMAPHORE_TIMEOUT']):
            logger.error(f"{producer_name}: Timeout waiting for empty slot")
            return False

        # Acquire mutex for exclusive access (Rule 3: Mutual exclusion)
        logger.debug(f"{producer_name}: Acquiring mutex for buffer access...")
        if not self.mutex.acquire(timeout=CONFIG['SEMAPHORE_TIMEOUT']):
            logger.error(f"{producer_name}: Timeout acquiring mutex")
            self.empty.release()  # Release the empty slot we acquired
            return False

        try:
            # Critical Section: Insert item into buffer
            self.buffer.put(item)
            with self._lock:
                self.produced_count += 1
            current_size = self.buffer.qsize()
            logger.info(f"{producer_name}: ✓ Inserted {item} (Buffer size: {current_size}/{CONFIG['BUFFER_SIZE']})")
            return True
        finally:
            # Release mutex
            self.mutex.release()
            logger.debug(f"{producer_name}: Released mutex")

            # Signal that a slot is now full
            self.full.release()
            logger.debug(f"{producer_name}: Signaled full slot (full={self.full._value})")

    def remove(self, consumer_name: str = "Consumer") -> Optional[int]:
        """Consumer removes item from buffer using semaphores with timeouts."""
        logger.info(f"{consumer_name}: Attempting to remove item...")

        # Wait for filled slot (Rule 2: Consumer waits if buffer is empty)
        logger.debug(f"{consumer_name}: Checking for filled slots (full={self.full._value})...")
        if not self.full.acquire(timeout=CONFIG['SEMAPHORE_TIMEOUT']):
            logger.error(f"{consumer_name}: Timeout waiting for filled slot")
            return None

        # Acquire mutex for exclusive access (Rule 3: Mutual exclusion)
        logger.debug(f"{consumer_name}: Acquiring mutex for buffer access...")
        if not self.mutex.acquire(timeout=CONFIG['SEMAPHORE_TIMEOUT']):
            logger.error(f"{consumer_name}: Timeout acquiring mutex")
            self.full.release()  # Release the full slot we acquired
            return None

        try:
            # Critical Section: Remove item from buffer
            item = self.buffer.get()
            with self._lock:
                self.consumed_count += 1
            current_size = self.buffer.qsize()
            logger.info(f"{consumer_name}: ✓ Removed {item} (Buffer size: {current_size}/{CONFIG['BUFFER_SIZE']})")
            return item
        finally:
            # Release mutex
            self.mutex.release()
            logger.debug(f"{consumer_name}: Released mutex")

            # Signal that a slot is now empty
            self.empty.release()
            logger.debug(f"{consumer_name}: Signaled empty slot (empty={self.empty._value})")

    def get_size(self) -> int:
        """Get current buffer size."""
        return self.buffer.qsize()

    def is_full(self) -> bool:
        """Check if buffer is full."""
        return self.buffer.full()

    def is_empty(self) -> bool:
        """Check if buffer is empty."""
        return self.buffer.empty()

    def stop(self):
        """Signal all operations to stop."""
        self._stop_event.set()


# Producer class using semaphores
class Producer(threading.Thread):
    """Producer thread that generates students and inserts them into buffer."""

    def __init__(self, buffer: SharedBuffer, xml_dir: str = CONFIG['XML_DIR'], name: str = "Producer"):
        """Initialize producer with buffer and XML directory."""
        super().__init__()
        self.buffer = buffer
        self.xml_dir = xml_dir
        self.name = name
        self.running = True

        # Create XML directory if it doesn't exist
        if not os.path.exists(self.xml_dir):
            os.makedirs(self.xml_dir)

    def _generate_and_save_student(self, student_num: int) -> bool:
        """Generate a student and save to XML. Return success status."""
        try:
            # Generate random student
            student = StudentGenerator.generate_random_student()

            # Create XML filename
            xml_filename = os.path.join(self.xml_dir, XMLHandler.generate_xml_filename(student_num))

            # Save to XML
            XMLHandler.save_student_to_xml(student, xml_filename)
            logger.info(f"{self.name}: Created {xml_filename}")

            # Insert corresponding integer to buffer
            return self.buffer.insert(student_num, self.name)
        except Exception as e:
            logger.error(f"{self.name}: Failed to generate/save student {student_num}: {e}")
            return False

    def run(self):
        """Main producer loop."""
        logger.info(f"{self.name} started...")
        student_num = 1

        while self.running and student_num <= CONFIG['MAX_STUDENTS']:
            if self._generate_and_save_student(student_num):
                student_num += 1
            else:
                logger.warning(f"{self.name}: Failed to process student {student_num}")
                break

            # Random delay between productions
            delay = random.uniform(CONFIG['PRODUCER_DELAY_MIN'], CONFIG['PRODUCER_DELAY_MAX'])
            logger.debug(f"{self.name}: Waiting {delay:.2f}s before next production...")
            time.sleep(delay)

        logger.info(f"{self.name} finished. Produced {student_num-1} students.")


# Consumer class using semaphores
class Consumer(threading.Thread):
    """Consumer thread that processes students from buffer."""

    def __init__(self, buffer: SharedBuffer, xml_dir: str = CONFIG['XML_DIR'], name: str = "Consumer"):
        """Initialize consumer with buffer and XML directory."""
        super().__init__()
        self.buffer = buffer
        self.xml_dir = xml_dir
        self.name = name
        self.running = True

    def _process_student(self, student_num: int) -> bool:
        """Process a student by loading from XML and displaying info. Return success."""
        try:
            # Create XML filename
            xml_filename = os.path.join(self.xml_dir, XMLHandler.generate_xml_filename(student_num))

            # Load student from XML
            student = XMLHandler.load_student_from_xml(xml_filename)

            # Clear the XML file
            XMLHandler.clear_xml_file(xml_filename)
            logger.info(f"{self.name}: Cleared {xml_filename}")

            # Process and display student information
            logger.info(f"\n{self.name} PROCESSED STUDENT:\n{student}\n")

            return True
        except Exception as e:
            logger.error(f"{self.name}: Failed to process student {student_num}: {e}")
            return False

    def run(self):
        """Main consumer loop."""
        logger.info(f"{self.name} started...")

        while self.running:
            # Remove integer from buffer
            student_num = self.buffer.remove(self.name)

            if student_num is not None:
                if not self._process_student(student_num):
                    logger.warning(f"{self.name}: Failed to process student {student_num}")
            else:
                logger.warning(f"{self.name}: No item to remove from buffer")
                break

            # Random delay between consumptions
            delay = random.uniform(CONFIG['CONSUMER_DELAY_MIN'], CONFIG['CONSUMER_DELAY_MAX'])
            logger.debug(f"{self.name}: Waiting {delay:.2f}s before next consumption...")
            time.sleep(delay)

            # Stop if all students have been processed
            with self.buffer._lock:
                if self.buffer.consumed_count >= CONFIG['MAX_STUDENTS']:
                    logger.info(f"{self.name}: All {CONFIG['MAX_STUDENTS']} students processed, stopping...")
                    break

        logger.info(f"{self.name} finished. Consumed {self.buffer.consumed_count} students.")


# Main function to run the Producer-Consumer problem with semaphores
def main():
    """Run the main producer-consumer simulation."""
    print("="*70)
    print("PRODUCER-CONSUMER PROBLEM WITH SEMAPHORES")
    print("="*70)
    print("Rules enforced by semaphores:")
    print("1. Producer waits when buffer is full")
    print("2. Consumer waits when buffer is empty")
    print("3. Mutual exclusion for buffer access")
    print("="*70)

    # Create shared buffer with semaphores
    buffer = SharedBuffer(CONFIG['BUFFER_SIZE'])

    # Create producer and consumer threads
    producer = Producer(buffer, name="Producer-1")
    consumer = Consumer(buffer, name="Consumer-1")

    # Start threads
    producer.start()
    time.sleep(0.5)  # Give producer a small head start
    consumer.start()

    # Wait for threads to complete
    producer.join()
    consumer.join()

    # Display summary
    print("\n" + "="*70)
    print("SIMULATION SUMMARY")
    print("="*70)
    print(f"Total produced: {buffer.produced_count}")
    print(f"Total consumed: {buffer.consumed_count}")
    print(f"Final buffer size: {buffer.get_size()}")
    print("="*70)


# Alternative: Multiple producers and consumers
def run_multiple_producers_consumers():
    """Demonstrate with multiple producers and consumers."""
    print("="*70)
    print("MULTIPLE PRODUCERS AND CONSUMERS WITH SEMAPHORES")
    print("="*70)

    buffer = SharedBuffer(CONFIG['BUFFER_SIZE'])

    # Create multiple producers and consumers
    producers = [Producer(buffer, name=f"Producer-{i+1}") for i in range(2)]
    consumers = [Consumer(buffer, name=f"Consumer-{i+1}") for i in range(2)]

    # Start all threads
    for p in producers:
        p.start()
        time.sleep(0.2)

    for c in consumers:
        c.start()
        time.sleep(0.2)

    # Let them run for a while
    time.sleep(8)

    # Signal producers to stop
    for p in producers:
        p.running = False

    # Wait for all to complete
    for p in producers:
        p.join()

    # Let consumers finish processing remaining items
    time.sleep(5)

    for c in consumers:
        c.running = False
        c.join()

    print("\nMulti-threaded simulation completed!")


# Simple demonstration with step-by-step execution
def demonstrate_semaphore_workflow():
    """Demonstrate the semaphore workflow step by step."""
    print("="*70)
    print("DEMONSTRATING SEMAPHORE WORKFLOW")
    print("="*70)

    buffer = SharedBuffer(3)  # Small buffer for demonstration

    print("\nInitial state:")
    print(f"  empty semaphore = {buffer.empty._value}")
    print(f"  full semaphore = {buffer.full._value}")
    print(f"  buffer size = {buffer.get_size()}")

    print("\n--- Step 1: Producer inserts item 1 ---")
    buffer.insert(1, "Demo-Producer")

    print("\n--- Step 2: Producer inserts item 2 ---")
    buffer.insert(2, "Demo-Producer")

    print("\n--- Step 3: Consumer removes item ---")
    item = buffer.remove("Demo-Consumer")
    print(f"Consumer removed: {item}")

    print("\n--- Step 4: Producer inserts item 3 ---")
    buffer.insert(3, "Demo-Producer")

    print("\n--- Step 5: Consumer removes item ---")
    item = buffer.remove("Demo-Consumer")
    print(f"Consumer removed: {item}")

    print("\n--- Step 6: Consumer removes item ---")
    item = buffer.remove("Demo-Consumer")
    print(f"Consumer removed: {item}")

    print("\n--- Step 7: Try to remove from empty buffer ---")
    print("(This will block until a producer adds something)")

    print("\nFinal state:")
    print(f"  empty semaphore = {buffer.empty._value}")
    print(f"  full semaphore = {buffer.full._value}")
    print(f"  buffer size = {buffer.get_size()}")
    print("="*70)


if __name__ == "__main__":
    # Run the main simulation
    # main()

    # Uncomment to see additional demonstrations
    # print("\n\n")
    # demonstrate_semaphore_workflow()

    # print("\n\n")
    run_multiple_producers_consumers()
