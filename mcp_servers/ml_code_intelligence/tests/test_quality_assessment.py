"""
Tests for Code Quality Assessment (Phase 3)
"""

import pytest
import asyncio
import sys
from pathlib import Path

# Add paths
sys.path.append(str(Path(__file__).parent.parent / "src"))
sys.path.append(str(Path(__file__).parent.parent.parent / "shared" / "src"))

from server import MLCodeIntelligenceServer
from tools.quality_assessment import assess_code_quality, CodeQualityAnalyzer, QualityCategory
from utils.config_utils import create_development_config


@pytest.mark.asyncio
async def test_comprehensive_quality_assessment():
    """Test comprehensive quality assessment functionality"""
    config = create_development_config("ml-code-intelligence-test")
    server = MLCodeIntelligenceServer(config)
    await server._startup()
    
    try:
        # Complex code with various quality issues
        test_code = '''
import os
import sys

class UserManager:
    def __init__(self, db, cache, logger, email_service, notification_service, sms_service, analytics, auth_service):
        self.db = db
        self.cache = cache
        self.logger = logger
        self.email_service = email_service
        self.notification_service = notification_service
        self.sms_service = sms_service
        self.analytics = analytics
        self.auth_service = auth_service
    
    def create_user_with_full_validation_and_setup_including_notifications_and_analytics_tracking(self, name, email, password, address, phone, age, gender, preferences, settings, metadata, tracking_data):
        if not name or not email or not password:
            return None
        
        if len(name) < 2:
            return None
            
        if '@' not in email:
            return None
            
        if len(password) < 8:
            return None
        
        # No null checks
        user_data = {'name': name, 'email': email}
        
        if age:
            if age < 13:
                self.logger.error("User too young")
                return None
            elif age > 120:
                self.logger.error("Invalid age")
                return None
            else:
                if age < 18:
                    if not preferences.get('parental_consent'):
                        self.logger.error("Parental consent required")
                        return None
                    else:
                        if not preferences.get('guardian_email'):
                            self.logger.error("Guardian email required")
                            return None
                        else:
                            if not preferences.get('guardian_phone'):
                                self.logger.error("Guardian phone required")
                                return None
                            else:
                                if not self.validate_guardian_info(preferences):
                                    self.logger.error("Invalid guardian info")
                                    return None
        
        # Dangerous function usage
        eval_result = eval(f"'{name}'.upper()")
        
        try:
            user = self.db.create_user(name, email, password)
            user.address = address
            user.phone = phone
            user.age = age
            user.gender = gender
            user.preferences = preferences
            user.settings = settings
            
            self.cache.set(f"user_{user.id}", user)
            
            # SQL injection vulnerability
            query = f"SELECT * FROM users WHERE email = '{email}'"
            self.db.execute(query)
            
            # Hardcoded credentials
            api_key = "sk-1234567890abcdef"
            password_check = "admin123"
            
            # Send notifications
            self.email_service.send_welcome_email(email)
            if phone:
                self.sms_service.send_welcome_sms(phone)
            
            self.analytics.track_user_creation(user.id)
            self.logger.info(f"Created user {user.id} with email {email}")
            
            return user
            
        except:
            # Poor error handling - catching all exceptions
            self.logger.error("Something went wrong")
            return None
    
    def validate_guardian_info(self, preferences):
        # Missing docstring
        guardian_email = preferences.get('guardian_email')
        guardian_phone = preferences.get('guardian_phone')
        
        # Nested loops (inefficient)
        for i in range(len(guardian_email)):
            for j in range(len(guardian_phone)):
                if guardian_email[i] == guardian_phone[j]:
                    return False
        
        return True
    
    def duplicate_validation_logic(self, name, email, password):
        # Duplicate code
        if not name or not email or not password:
            return False
        
        if len(name) < 2:
            return False
            
        if '@' not in email:
            return False
            
        if len(password) < 8:
            return False
            
        return True

def unused_global_function():
    # Dead code
    return "This is never called"

# God object class
class MegaProcessor:
    def __init__(self):
        pass
    
    def method1(self): pass
    def method2(self): pass
    def method3(self): pass
    def method4(self): pass
    def method5(self): pass
    def method6(self): pass
    def method7(self): pass
    def method8(self): pass
    def method9(self): pass
    def method10(self): pass
    def method11(self): pass
    def method12(self): pass
    def method13(self): pass
    def method14(self): pass
    def method15(self): pass
    def method16(self): pass
    def method17(self): pass
    def method18(self): pass
    def method19(self): pass
    def method20(self): pass
    def method21(self): pass
'''
        
        # Test quality assessment through server
        result = await server._assess_quality(test_code, "python", include_trends=True)
        
        # Verify response structure
        assert result['status'] == 'success'
        assert 'overall_score' in result
        assert 'category_scores' in result
        assert 'technical_debt_ratio' in result
        assert 'maintainability_index' in result
        assert 'metrics' in result
        assert 'improvement_priorities' in result
        
        # Check that quality score is low due to many issues
        assert result['overall_score'] < 70  # Should be low quality
        
        # Check category scores exist
        category_scores = result['category_scores']
        expected_categories = ['maintainability', 'reliability', 'security', 'performance', 'readability', 'testability']
        for category in expected_categories:
            assert category in category_scores
        
        # Security should be very low due to dangerous functions and hardcoded secrets
        assert category_scores['security'] < 50
        
        # Maintainability should be low due to complexity and long function names
        assert category_scores['maintainability'] < 60
        
        # Check technical debt is high
        assert result['technical_debt_ratio'] > 0.3
        
        # Check we have improvement priorities
        priorities = result['improvement_priorities']
        assert len(priorities) > 0
        assert all('metric' in p for p in priorities)
        assert all('priority' in p for p in priorities)
        assert all('suggestions' in p for p in priorities)
        
        print(f"✅ Quality assessment: {result['overall_score']:.1f}/100")
        print(f"✅ Technical debt ratio: {result['technical_debt_ratio']:.2f}")
        print(f"✅ Found {len(priorities)} improvement priorities")
        
    finally:
        await server._shutdown()


@pytest.mark.asyncio
async def test_quality_assessment_tools():
    """Test quality assessment tool endpoints"""
    config = create_development_config("ml-code-intelligence-test")
    server = MLCodeIntelligenceServer(config)
    await server._startup()
    
    try:
        # Good quality code
        good_code = '''
from typing import List, Optional

class Calculator:
    """A simple calculator with basic operations."""
    
    def __init__(self) -> None:
        """Initialize the calculator."""
        self.history: List[str] = []
    
    def add(self, a: float, b: float) -> float:
        """Add two numbers and return the result."""
        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            raise TypeError("Arguments must be numbers")
        
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result
    
    def subtract(self, a: float, b: float) -> float:
        """Subtract second number from first and return the result."""
        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            raise TypeError("Arguments must be numbers")
        
        result = a - b
        self.history.append(f"{a} - {b} = {result}")
        return result
    
    def get_history(self) -> List[str]:
        """Get calculation history."""
        return self.history.copy()
    
    def clear_history(self) -> None:
        """Clear calculation history."""
        self.history.clear()
'''
        
        # Test assess_code_quality tool
        quality_result = await server._assess_quality(good_code, "python", False)
        assert quality_result['status'] == 'success'
        assert quality_result['overall_score'] > 80  # Should be high quality
        
        # Test get_quality_metrics tool
        metrics_result = await server._assess_quality(good_code, "python", False)
        metrics = {
            'overall_score': metrics_result.get('overall_score', 0),
            'category_scores': metrics_result.get('category_scores', {}),
            'technical_debt_ratio': metrics_result.get('technical_debt_ratio', 0),
            'maintainability_index': metrics_result.get('maintainability_index', 0)
        }
        
        assert metrics['overall_score'] > 80
        assert metrics['technical_debt_ratio'] < 0.2
        assert metrics['maintainability_index'] > 70
        
        # Test get_improvement_priorities tool  
        priorities = metrics_result.get('improvement_priorities', [])
        # Good code should have few or no priorities
        assert len(priorities) <= 2
        
        print(f"✅ Good code quality: {quality_result['overall_score']:.1f}/100")
        print(f"✅ Good code priorities: {len(priorities)}")
        
    finally:
        await server._shutdown()


@pytest.mark.asyncio
async def test_quality_categories():
    """Test individual quality category assessments"""
    analyzer = CodeQualityAnalyzer()
    
    # Test code with specific issues for each category
    test_cases = {
        'maintainability': '''
def very_complex_function(a, b, c, d, e, f, g, h):
    if a > 0:
        if b > 0:
            if c > 0:
                if d > 0:
                    if e > 0:
                        if f > 0:
                            return g + h
                        else:
                            return g - h
                    else:
                        return c * d
                else:
                    return b * c
            else:
                return a * b
        else:
            return a
    else:
        return 0
''',
        'security': '''
def dangerous_function(user_input):
    # Dangerous eval usage
    result = eval(user_input)
    
    # Hardcoded credentials
    password = "admin123"
    api_key = "sk-1234567890"
    
    # SQL injection vulnerability
    query = f"SELECT * FROM users WHERE name = '{user_input}'"
    
    return result
''',
        'performance': '''
def inefficient_function(data):
    result = []
    
    # Nested loops - O(n²) complexity
    for i in range(len(data)):
        for j in range(len(data)):
            if i != j:
                result.append(data[i] + data[j])
    
    # No caching, repeated calculations
    expensive_calc = []
    for item in data:
        expensive_calc.append(sum(range(1000)) * item)
    
    return result + expensive_calc
''',
        'reliability': '''
def unreliable_function(data):
    # No error handling
    result = data[0] / data[1]
    
    # No null checks
    name = data.name.upper()
    
    # No type checking
    return result + name
''',
        'readability': '''
def r(d,x,y,z):    # Poor naming
#no docstring
    if d>0:r=x+y*z;return r    # Multiple statements, poor formatting
    else:return x-y/z if z!=0 else 0    # Complex one-liner
''',
        'testability': '''
import random
import datetime

def hard_to_test_function():
    # Uses global state
    current_time = datetime.datetime.now()
    random_value = random.random()
    
    # Hard to mock external dependencies
    with open('/tmp/data.txt', 'r') as f:
        data = f.read()
    
    # Complex logic mixed with I/O
    if current_time.hour > 12 and random_value > 0.5:
        return data.upper()
    else:
        return data.lower()
'''
    }
    
    for category, code in test_cases.items():
        report = analyzer.assess_quality(code, "python")
        
        # All categories should have some issues
        assert report.overall_score < 90
        
        # The specific category being tested should have a lower score
        category_score = report.category_scores.get(category, 100)
        
        if category == 'security':
            assert category_score < 50  # Security issues should be severe
        elif category == 'maintainability':
            assert category_score < 60  # Complex code should score low
        elif category == 'performance':
            assert category_score < 70  # Inefficient code should score low
        
        print(f"✅ {category} test: overall={report.overall_score:.1f}, {category}={category_score:.1f}")


@pytest.mark.asyncio
async def test_quality_trends_and_priorities():
    """Test quality trend analysis and improvement priorities"""
    analyzer = CodeQualityAnalyzer()
    
    # Code with clear improvement opportunities
    code_with_issues = '''
def process_users(users):
    # Multiple issues for testing priorities
    results = []
    
    for user in users:
        # No null checking (reliability issue)
        name = user.name.upper()
        
        # SQL injection (security issue)  
        query = f"SELECT * FROM accounts WHERE user_id = {user.id}"
        
        # Inefficient nested operation (performance issue)
        for i in range(100):
            for j in range(100):
                if i * j == user.score:
                    results.append(name)
    
    return results
'''
    
    report = analyzer.assess_quality(code_with_issues, "python", include_trends=True)
    
    # Should have improvement priorities
    assert len(report.improvement_priorities) > 0
    
    # Check priority structure
    for priority in report.improvement_priorities:
        assert 'metric' in priority
        assert 'category' in priority
        assert 'current_score' in priority
        assert 'priority' in priority
        assert 'suggestions' in priority
        
        # Priority should be high/medium for low scores
        if priority['current_score'] < 50:
            assert priority['priority'] in ['high', 'critical']
    
    # Should have quality trends
    assert 'quality_trends' in report.__dict__
    
    print(f"✅ Found {len(report.improvement_priorities)} improvement priorities")
    print(f"✅ Quality trends available: {bool(report.quality_trends)}")


@pytest.mark.asyncio
async def test_quality_assessment_edge_cases():
    """Test quality assessment edge cases"""
    analyzer = CodeQualityAnalyzer()
    
    # Empty code
    empty_report = analyzer.assess_quality("", "python")
    assert empty_report.overall_score >= 0
    
    # Syntax error
    syntax_error_report = analyzer.assess_quality("def invalid syntax", "python")
    assert syntax_error_report.overall_score == 0
    
    # Very simple code
    simple_code = "print('hello')"
    simple_report = analyzer.assess_quality(simple_code, "python")
    assert simple_report.overall_score > 50  # Should be reasonable
    
    # Non-Python language
    js_code = "function test() { return 42; }"
    js_report = analyzer.assess_quality(js_code, "javascript")
    assert js_report.overall_score >= 0
    
    print("✅ Edge cases handled correctly")


@pytest.mark.asyncio
async def test_server_quality_integration():
    """Test quality assessment integration with the main server"""
    config = create_development_config("ml-code-intelligence-test")
    server = MLCodeIntelligenceServer(config)
    await server._startup()
    
    try:
        test_code = '''
def factorial(n: int) -> int:
    """Calculate factorial of a number."""
    if not isinstance(n, int) or n < 0:
        raise ValueError("Input must be a non-negative integer")
    
    if n <= 1:
        return 1
    
    return n * factorial(n - 1)
'''
        
        # Test that server stats include quality assessment capabilities
        stats = await server.get_server_stats()
        stats.update({
            "indexed_code_count": server.indexed_code_count,
            "embedding_model": server.settings.embedding_model,
            "vector_db_type": server.settings.vector_db_type,
            "ml_device": server.settings.ml_device
        })
        
        assert 'ml_device' in stats
        assert 'embedding_model' in stats
        
        # Test quality assessment through server
        quality_result = await server._assess_quality(test_code, "python")
        assert quality_result['status'] == 'success'
        assert quality_result['overall_score'] > 90  # Clean code should score high
        
        print(f"✅ Server integration: quality score {quality_result['overall_score']:.1f}")
        
    finally:
        await server._shutdown()


if __name__ == "__main__":
    async def run_tests():
        print("🧪 Running Quality Assessment Tests (Phase 3)...")
        
        await test_comprehensive_quality_assessment()
        await test_quality_assessment_tools()
        await test_quality_categories()
        await test_quality_trends_and_priorities()
        await test_quality_assessment_edge_cases()
        await test_server_quality_integration()
        
        print("✅ All quality assessment tests passed!")
    
    asyncio.run(run_tests())