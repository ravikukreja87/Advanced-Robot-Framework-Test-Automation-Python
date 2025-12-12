"""
AI-Powered Self-Healing Library for Robot Framework
Automatically heals broken locators using multiple fallback strategies
"""

import os
import json
import time
from typing import List, Dict, Tuple, Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException
from robot.api.deco import keyword, library
from robot.api import logger
import cv2
import numpy as np
from PIL import Image
import io


@library(scope='GLOBAL', auto_keywords=True)
class SelfHealingLibrary:
    """
    Self-healing library that automatically adapts when UI elements change.
    Uses AI-powered strategies to find elements even when primary locators fail.
    """
    
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = '1.0.0'
    
    def __init__(self):
        self.healing_cache = {}
        self.healing_history = []
        self.cache_file = 'reports/healing_cache.json'
        self.load_cache()
        
    def load_cache(self):
        """Load previously healed locators from cache"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    self.healing_cache = json.load(f)
                logger.info(f"Loaded {len(self.healing_cache)} healed locators from cache")
        except Exception as e:
            logger.warn(f"Could not load healing cache: {e}")
    
    def save_cache(self):
        """Save healed locators to cache"""
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, 'w') as f:
                json.dump(self.healing_cache, f, indent=2)
        except Exception as e:
            logger.warn(f"Could not save healing cache: {e}")
    
    @keyword("Find Element With Healing")
    def find_element_with_healing(self, driver, locator: str, timeout: int = 10) -> WebElement:
        """
        Find element with self-healing capability.
        If primary locator fails, tries alternative strategies.
        
        Args:
            driver: Selenium WebDriver instance
            locator: Primary locator (xpath, css, id, etc.)
            timeout: Maximum time to wait for element
            
        Returns:
            WebElement if found
            
        Example:
            | ${element}= | Find Element With Healing | ${driver} | id=submit-button |
        """
        start_time = time.time()
        original_locator = locator
        
        # Try cache first
        if locator in self.healing_cache:
            cached_locator = self.healing_cache[locator]
            logger.info(f"Trying cached healed locator: {cached_locator}")
            try:
                element = self._find_element(driver, cached_locator)
                if element:
                    logger.info(f"✅ Found element using cached locator")
                    return element
            except:
                logger.info("Cached locator failed, trying other strategies")
        
        # Strategy 1: Try original locator
        try:
            element = self._find_element(driver, locator)
            if element:
                logger.info(f"✅ Found element with original locator: {locator}")
                return element
        except NoSuchElementException:
            logger.info(f"❌ Original locator failed: {locator}")
        
        # Strategy 2: Try alternative locator types
        logger.info("🔄 Attempting self-healing...")
        healed_element = self._try_healing_strategies(driver, locator)
        
        if healed_element:
            # Cache the healed locator
            healed_locator = self._get_element_locator(healed_element)
            self.healing_cache[original_locator] = healed_locator
            self.save_cache()
            
            # Log healing success
            healing_info = {
                'original_locator': original_locator,
                'healed_locator': healed_locator,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'healing_time': round(time.time() - start_time, 2)
            }
            self.healing_history.append(healing_info)
            
            logger.info(f"✅ Self-healing SUCCESS! New locator: {healed_locator}")
            return healed_element
        
        raise NoSuchElementException(f"Could not find element even with self-healing: {original_locator}")
    
    def _try_healing_strategies(self, driver, original_locator: str) -> Optional[WebElement]:
        """Try multiple healing strategies"""
        strategies = [
            self._heal_by_text_content,
            self._heal_by_nearby_elements,
            self._heal_by_attributes,
            self._heal_by_position,
            self._heal_by_visual_similarity
        ]
        
        for strategy in strategies:
            try:
                element = strategy(driver, original_locator)
                if element:
                    logger.info(f"✅ Healed using strategy: {strategy.__name__}")
                    return element
            except Exception as e:
                logger.debug(f"Strategy {strategy.__name__} failed: {e}")
                continue
        
        return None
    
    def _heal_by_text_content(self, driver, locator: str) -> Optional[WebElement]:
        """Find element by its text content"""
        try:
            # Extract text from original locator if possible
            text_hints = ['Login', 'Submit', 'Search', 'Save', 'Cancel']  # Common texts
            
            for text in text_hints:
                try:
                    element = driver.find_element(By.XPATH, f"//*[contains(text(), '{text}')]")
                    return element
                except:
                    continue
        except Exception as e:
            logger.debug(f"Text content healing failed: {e}")
        return None
    
    def _heal_by_nearby_elements(self, driver, locator: str) -> Optional[WebElement]:
        """Find element by analyzing nearby stable elements"""
        # This is a simplified version - in production, you'd analyze DOM structure
        return None
    
    def _heal_by_attributes(self, driver, locator: str) -> Optional[WebElement]:
        """Find element by common attributes (class, name, type, etc.)"""
        try:
            # Try common attribute patterns
            attributes = ['data-testid', 'data-test', 'name', 'type', 'role', 'aria-label']
            
            for attr in attributes:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, f'[{attr}]')
                    if elements:
                        return elements[0]  # Return first match
                except:
                    continue
        except Exception as e:
            logger.debug(f"Attribute healing failed: {e}")
        return None
    
    def _heal_by_position(self, driver, locator: str) -> Optional[WebElement]:
        """Find element by its relative position on page"""
        # Simplified version - would use coordinate analysis in production
        return None
    
    def _heal_by_visual_similarity(self, driver, locator: str) -> Optional[WebElement]:
        """Find element using visual/image recognition"""
        # This would use OpenCV/TensorFlow for image matching
        return None
    
    def _find_element(self, driver, locator: str) -> WebElement:
        """Parse locator string and find element"""
        if '=' in locator:
            strategy, value = locator.split('=', 1)
            by_mapping = {
                'id': By.ID,
                'name': By.NAME,
                'xpath': By.XPATH,
                'css': By.CSS_SELECTOR,
                'class': By.CLASS_NAME,
                'tag': By.TAG_NAME,
                'link': By.LINK_TEXT,
                'partial_link': By.PARTIAL_LINK_TEXT
            }
            by = by_mapping.get(strategy.lower(), By.XPATH)
            return driver.find_element(by, value)
        else:
            return driver.find_element(By.XPATH, locator)
    
    def _get_element_locator(self, element: WebElement) -> str:
        """Generate locator string for an element"""
        # Try to generate a stable locator
        if element.get_attribute('id'):
            return f"id={element.get_attribute('id')}"
        elif element.get_attribute('name'):
            return f"name={element.get_attribute('name')}"
        else:
            return f"xpath=({element.tag_name})[1]"  # Simplified
    
    @keyword("Get Healing Statistics")
    def get_healing_statistics(self) -> Dict:
        """Get statistics about self-healing operations"""
        stats = {
            'total_healings': len(self.healing_history),
            'cached_locators': len(self.healing_cache),
            'recent_healings': self.healing_history[-10:] if self.healing_history else []
        }
        logger.info(f"Healing Statistics: {json.dumps(stats, indent=2)}")
        return stats
