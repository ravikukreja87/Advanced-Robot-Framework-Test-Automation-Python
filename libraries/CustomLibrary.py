"""
Custom utility library with common helper functions
"""

import json
import random
import string
from datetime import datetime, timedelta
from typing import Dict, List, Any
from robot.api.deco import keyword, library
from robot.api import logger
from faker import Faker


@library(scope='GLOBAL')
class CustomLibrary:
    """Custom utility keywords for test automation"""
    
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    
    def __init__(self):
        self.faker = Faker()
        self.test_data_cache = {}
    
    @keyword("Generate Random Email")
    def generate_random_email(self, domain: str = "test.com") -> str:
        """Generate random email address"""
        username = self.faker.user_name()
        email = f"{username}@{domain}"
        logger.info(f"Generated email: {email}")
        return email
    
    @keyword("Generate Random Phone")
    def generate_random_phone(self, country_code: str = "+1") -> str:
        """Generate random phone number"""
        phone = f"{country_code}{random.randint(1000000000, 9999999999)}"
        return phone
    
    @keyword("Generate Test User")
    def generate_test_user(self) -> Dict:
        """Generate complete test user with all details"""
        user = {
            'first_name': self.faker.first_name(),
            'last_name': self.faker.last_name(),
            'email': self.faker.email(),
            'phone': self.faker.phone_number(),
            'address': self.faker.address(),
            'city': self.faker.city(),
            'state': self.faker.state(),
            'zip': self.faker.zipcode(),
            'dob': self.faker.date_of_birth(minimum_age=18, maximum_age=80).strftime('%Y-%m-%d'),
            'ssn': self.faker.ssn(),
            'username': self.faker.user_name(),
            'password': self.generate_secure_password()
        }
        logger.info(f"Generated test user: {user['email']}")
        return user
    
    @keyword("Generate Secure Password")
    def generate_secure_password(self, length: int = 12) -> str:
        """Generate secure random password"""
        chars = string.ascii_letters + string.digits + "!@#$%^&*()"
        password = ''.join(random.choice(chars) for _ in range(length))
        return password
    
    @keyword("Get Current Timestamp")
    def get_current_timestamp(self, format: str = "%Y-%m-%d %H:%M:%S") -> str:
        """Get current timestamp"""
        return datetime.now().strftime(format)
    
    @keyword("Calculate Future Date")
    def calculate_future_date(self, days: int = 1, format: str = "%Y-%m-%d") -> str:
        """Calculate future date"""
        future = datetime.now() + timedelta(days=int(days))
        return future.strftime(format)
    
    @keyword("Wait For Condition")
    def wait_for_condition(self, condition_func, timeout: int = 30, poll_interval: float = 0.5) -> bool:
        """
        Smart wait that polls a condition until it's true or timeout.
        
        Args:
            condition_func: Function that returns bool
            timeout: Maximum seconds to wait
            poll_interval: Seconds between checks
            
        Returns:
            True if condition met, False if timeout
        """
        end_time = time.time() + timeout
        
        while time.time() < end_time:
            try:
                if condition_func():
                    return True
            except:
                pass
            time.sleep(poll_interval)
        
        return False
    
    @keyword("Retry On Failure")
    def retry_on_failure(self, keyword_name: str, max_attempts: int = 3, delay: int = 2):
        """
        Retry a keyword if it fails.
        
        Args:
            keyword_name: Name of keyword to retry
            max_attempts: Maximum retry attempts
            delay: Seconds to wait between retries
        """
        from robot.libraries.BuiltIn import BuiltIn
        bi = BuiltIn()
        
        for attempt in range(1, max_attempts + 1):
            try:
                logger.info(f"Attempt {attempt}/{max_attempts}: {keyword_name}")
                bi.run_keyword(keyword_name)
                logger.info(f"✅ Success on attempt {attempt}")
                return
            except Exception as e:
                if attempt == max_attempts:
                    logger.error(f"❌ All {max_attempts} attempts failed")
                    raise
                logger.warn(f"Attempt {attempt} failed: {e}. Retrying in {delay}s...")
                time.sleep(delay)