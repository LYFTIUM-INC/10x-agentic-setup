"""
Tests for Advanced Code Analysis (Phase 2)
"""

import pytest
import asyncio
import sys
from pathlib import Path

# Add paths
sys.path.append(str(Path(__file__).parent.parent / "src"))
sys.path.append(str(Path(__file__).parent.parent.parent / "shared" / "src"))

from server import MLCodeIntelligenceServer, CodeAnalysisRequest
from tools.advanced_analysis import AdvancedPythonAnalyzer, enhance_code_analysis
from utils.config_utils import create_development_config


@pytest.mark.asyncio
async def test_advanced_code_analysis():
    """Test advanced code analysis with refactoring suggestions"""
    config = create_development_config("ml-code-intelligence-test")
    server = MLCodeIntelligenceServer(config)
    await server._startup()
    
    try:
        # Complex Python code with various issues
        complex_code = '''
class UserManager:
    def __init__(self, db, cache, logger, email_service, notification_service, sms_service):
        self.db = db
        self.cache = cache
        self.logger = logger
        self.email_service = email_service
        self.notification_service = notification_service
        self.sms_service = sms_service
    
    def create_user_with_full_profile(self, name, email, password, address, phone, age, gender, preferences, settings):
        """Create user with extensive validation and setup"""
        if not name or not email:
            return None
        
        if len(name) < 2:
            return None
            
        if '@' not in email:
            return None
            
        if len(password) < 8:
            return None
            
        if self.db.user_exists(email):
            self.logger.warning(f"User already exists: {email}")
            return None
        
        try:
            # Nested validation
            if age:
                if age < 13:
                    self.logger.error("User too young")
                    return None
                elif age > 120:
                    self.logger.error("Invalid age")
                    return None
                else:
                    if age < 18:
                        # More nested logic
                        if not preferences.get('parental_consent'):
                            self.logger.error("Parental consent required")
                            return None
                        else:
                            # Even more nesting
                            if not preferences.get('guardian_email'):
                                self.logger.error("Guardian email required")
                                return None
            
            # Create user
            user = self.db.create_user(name, email, password)
            user.address = address
            user.phone = phone
            user.age = age
            user.gender = gender
            user.preferences = preferences
            user.settings = settings
            
            # Cache user
            self.cache.set(f"user_{user.id}", user)
            
            # Send notifications
            self.email_service.send_welcome_email(email)
            if phone:
                self.sms_service.send_welcome_sms(phone)
            
            # Log creation
            self.logger.info(f"Created user {user.id} with email {email}")
            
            return user
            
        except Exception as e:
            self.logger.error(f"Failed to create user: {e}")
            return None
    
    def duplicate_user_logic(self, name, email, password):
        """This function duplicates logic from create_user_with_full_profile"""
        if not name or not email:
            return None
        
        if len(name) < 2:
            return None
            
        if '@' not in email:
            return None
            
        if len(password) < 8:
            return None
            
        return True

def unused_helper_function():
    """This function is never called"""
    return "helper result"

class AnotherUserManager:
    """This class duplicates UserManager functionality"""
    def __init__(self, database, cache_service):
        self.database = database
        self.cache_service = cache_service
    
    def create_user(self, name, email):
        user = self.database.create_user(name, email)
        self.cache_service.set(f"user_{user.id}", user)
        return user
'''
        
        # Test basic analysis with advanced features
        request = CodeAnalysisRequest(
            code=complex_code,
            language="python",
            include_metrics=True,
            include_issues=True,
            include_advanced=True,
            include_suggestions=True
        )
        
        response = await server._analyze_code(request)
        
        # Verify response structure
        assert response.language == "python"
        assert response.summary is not None
        assert response.metrics is not None
        assert response.advanced_analysis is not None
        assert response.refactoring_suggestions is not None
        
        # Check advanced analysis components
        advanced = response.advanced_analysis
        assert 'refactoring_suggestions' in advanced
        assert 'detected_patterns' in advanced
        assert 'architectural_insights' in advanced
        assert 'function_metrics' in advanced
        assert 'class_metrics' in advanced
        
        # Verify we have meaningful suggestions
        suggestions = advanced['refactoring_suggestions']
        assert len(suggestions) > 0
        
        # Check for expected suggestion types
        suggestion_types = [s['type'] for s in suggestions]
        assert any('parameter' in s_type for s_type in suggestion_types)  # Too many parameters
        assert any('complexity' in s_type or 'nesting' in s_type for s_type in suggestion_types)  # High complexity/nesting
        
        # Verify function metrics
        function_metrics = advanced['function_metrics']
        assert 'create_user_with_full_profile' in function_metrics
        func_metrics = function_metrics['create_user_with_full_profile']
        assert func_metrics['cyclomatic_complexity'] > 5  # Should be high due to nested conditions
        assert func_metrics['parameter_count'] > 5  # Should detect many parameters
        
        # Verify class metrics
        class_metrics = advanced['class_metrics']
        assert 'UserManager' in class_metrics
        
        print(f"✅ Advanced analysis found {len(suggestions)} refactoring suggestions")
        print(f"✅ Detected patterns: {len(advanced['detected_patterns'])}")
        print(f"✅ Architectural insights: {len(advanced['architectural_insights'])}")
        
    finally:
        await server._shutdown()


@pytest.mark.asyncio
async def test_pattern_detection():
    """Test specific pattern detection capabilities"""
    # Test Singleton pattern detection
    singleton_code = '''
class DatabaseConnection:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def connect(self):
        return "connected"
'''
    
    analyzer = AdvancedPythonAnalyzer()
    result = analyzer.analyze_advanced(singleton_code)
    
    patterns = result['detected_patterns']
    pattern_names = [p['name'] for p in patterns]
    
    assert any('Singleton' in name for name in pattern_names)
    print("✅ Singleton pattern detection working")


@pytest.mark.asyncio
async def test_refactoring_suggestions():
    """Test refactoring suggestion generation"""
    config = create_development_config("ml-code-intelligence-test")
    server = MLCodeIntelligenceServer(config)
    
    try:
        # Code with clear refactoring opportunities
        refactor_code = '''
def process_data(data, option1, option2, option3, option4, option5, option6, option7):
    if option1:
        if option2:
            if option3:
                if option4:
                    return data * 2
                else:
                    return data * 3
            else:
                return data * 4
        else:
            return data * 5
    else:
        return data
'''
        
        # Get suggestions through the internal method
        result = await server._advanced_analysis(refactor_code, "python")
        suggestions = result.get('advanced_analysis', {}).get('refactoring_suggestions', [])
        
        assert len(suggestions) > 0
        
        print(f"✅ Generated {len(suggestions)} refactoring suggestions")
        for suggestion in suggestions[:5]:  # Show first 5
            print(f"   - {suggestion['type']}: {suggestion['description']}")
        
        # Should suggest parameter object for too many parameters
        suggestion_types = [s['type'].lower() for s in suggestions]
        assert any('parameter' in s_type for s_type in suggestion_types)
        
        # Check that we have meaningful suggestions
        assert all('description' in s for s in suggestions)
        assert all('priority' in s for s in suggestions)
        
    finally:
        pass  # No startup required for this test


@pytest.mark.asyncio
async def test_advanced_tool_endpoints():
    """Test the new advanced analysis tool endpoints"""
    config = create_development_config("ml-code-intelligence-test")
    server = MLCodeIntelligenceServer(config)
    await server._startup()
    
    try:
        test_code = '''
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

class Calculator:
    def add(self, a, b):
        return a + b
    
    def multiply(self, a, b):
        return a * b
'''
        
        # Test advanced analysis endpoint
        advanced_result = await server._advanced_analysis(test_code, "python")
        assert 'advanced_analysis' in advanced_result
        assert advanced_result['status'] == 'success'
        
        # Test refactoring suggestions through internal method
        result = await server._advanced_analysis(test_code, "python")
        suggestions = result.get('advanced_analysis', {}).get('refactoring_suggestions', [])
        assert isinstance(suggestions, list)
        
        # Test pattern detection through internal method
        patterns = result.get('advanced_analysis', {}).get('detected_patterns', [])
        assert isinstance(patterns, list)
        
        print("✅ All advanced tool endpoints working")
        
    finally:
        await server._shutdown()


if __name__ == "__main__":
    async def run_tests():
        print("🧪 Running Advanced Code Analysis Tests...")
        
        await test_advanced_code_analysis()
        await test_pattern_detection()
        await test_refactoring_suggestions()
        await test_advanced_tool_endpoints()
        
        print("✅ All advanced analysis tests passed!")
    
    asyncio.run(run_tests())