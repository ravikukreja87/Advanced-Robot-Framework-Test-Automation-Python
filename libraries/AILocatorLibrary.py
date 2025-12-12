"""
AI-Powered Smart Locator Library
Uses machine learning to generate optimal locators
"""

import re
from typing import List, Dict
from robot.api.deco import keyword, library
from robot.api import logger


@library(scope='GLOBAL')
class AILocatorLibrary:
    """Generate smart, resilient locators using AI strategies"""
    
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    
    @keyword("Generate Smart Locator")
    def generate_smart_locator(self, element_info: Dict) -> List[str]:
        """
        Generate multiple fallback locators for an element.
        Returns list of locators in order of reliability.
        
        Args:
            element_info: Dict with element attributes
            
        Returns:
            List of locator strategies
            
        Example:
            | ${locators}= | Generate Smart Locator | {'id': 'btn', 'class': 'submit'} |
        """
        locators = []
        
        # Priority 1: Unique identifiers
        if 'id' in element_info and element_info['id']:
            locators.append(f"id={element_info['id']}")
        
        if 'data-testid' in element_info:
            locators.append(f"css=[data-testid='{element_info['data-testid']}']")
        
        # Priority 2: Name attribute
        if 'name' in element_info and element_info['name']:
            locators.append(f"name={element_info['name']}")
        
        # Priority 3: Composite selectors
        if 'class' in element_info and 'type' in element_info:
            locators.append(f"css={element_info.get('tag', 'button')}.{element_info['class']}[type='{element_info['type']}']")
        
        # Priority 4: Text-based
        if 'text' in element_info:
            locators.append(f"xpath=//*[contains(text(), '{element_info['text']}')]")
        
        # Priority 5: Aria labels
        if 'aria-label' in element_info:
            locators.append(f"css=[aria-label='{element_info['aria-label']}']")
        
        logger.info(f"Generated {len(locators)} smart locators")
        return locators
    
    @keyword("Validate Locator Strength")
    def validate_locator_strength(self, locator: str) -> Dict:
        """
        Analyze locator and provide strength score and recommendations.
        
        Returns:
            Dict with score (0-100) and recommendations
        """
        score = 50  # Base score
        issues = []
        recommendations = []
        
        # Check for best practices
        if 'data-testid' in locator or 'data-test' in locator:
            score += 30
        elif locator.startswith('id='):
            score += 25
        elif locator.startswith('name='):
            score += 15
        
        # Penalize fragile patterns
        if '//*' in locator and '[' in locator and '@' not in locator:
            score -= 20
            issues.append("Absolute XPath detected - very fragile")
            recommendations.append("Use relative XPath or CSS selectors")
        
        if 'contains(@class' in locator:
            score -= 10
            issues.append("Class-based locator may be unstable")
            recommendations.append("Consider using data-testid or ID")
        
        # Check for index-based selectors
        if re.search(r'\[\d+\]', locator):
            score -= 15
            issues.append("Index-based selector detected")
            recommendations.append("Use unique attributes instead")
        
        score = max(0, min(100, score))  # Clamp between 0-100
        
        result = {
            'score': score,
            'strength': 'Strong' if score >= 75 else 'Medium' if score >= 50 else 'Weak',
            'issues': issues,
            'recommendations': recommendations
        }
        
        logger.info(f"Locator Strength Analysis: {result}")
        return result