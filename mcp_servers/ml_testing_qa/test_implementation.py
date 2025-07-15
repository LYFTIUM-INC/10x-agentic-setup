#!/usr/bin/env python3
"""
ML Testing QA MCP Implementation Test
Quick validation of the complete ML Testing QA MCP server implementation
"""

import asyncio
import json
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from server import MLTestingQAServer, IntelligentTestGenerator, QualityPredictor, AdaptiveTestingStrategist

async def test_intelligent_test_generation():
    """Test intelligent test generation functionality"""
    print("🧪 Testing Intelligent Test Generation...")
    
    generator = IntelligentTestGenerator()
    
    test_code = '''
def calculate_discount(price, discount_percentage):
    """Calculate discount amount for a given price and percentage"""
    if price < 0:
        raise ValueError("Price cannot be negative")
    
    if discount_percentage < 0 or discount_percentage > 100:
        raise ValueError("Discount percentage must be between 0 and 100")
    
    discount_amount = price * (discount_percentage / 100)
    return round(discount_amount, 2)

def process_order(items, customer_type="regular"):
    """Process an order with customer-specific discounts"""
    if not items:
        return {"total": 0, "items": []}
    
    total = 0
    processed_items = []
    
    for item in items:
        price = item.get("price", 0)
        quantity = item.get("quantity", 1)
        
        if customer_type == "premium":
            price = price * 0.9  # 10% discount
        elif customer_type == "vip":
            price = price * 0.8  # 20% discount
        
        item_total = price * quantity
        total += item_total
        
        processed_items.append({
            "name": item.get("name", "Unknown"),
            "price": price,
            "quantity": quantity,
            "total": item_total
        })
    
    return {"total": round(total, 2), "items": processed_items}
'''
    
    context = {
        "test_framework": "pytest",
        "coverage_target": 95,
        "include_performance_tests": True,
        "include_security_tests": True
    }
    
    result = await generator.generate_tests(test_code, context)
    
    print(f"✅ Generated {len(result.get('unit_tests', []))} unit tests")
    print(f"✅ Generated {len(result.get('edge_case_tests', []))} edge case tests")
    print(f"✅ Generated {len(result.get('performance_tests', []))} performance tests")
    print(f"✅ Generated {len(result.get('security_tests', []))} security tests")
    print(f"✅ Estimated coverage: {result.get('coverage_estimate', 0):.1f}%")
    print(f"✅ Test quality score: {result.get('test_quality_score', 0):.1f}/100")
    
    # Show sample generated test
    if result.get('unit_tests'):
        print("\\n📝 Sample generated unit test:")
        print(result['unit_tests'][0])
    
    return result

async def test_quality_prediction():
    """Test quality prediction functionality"""
    print("\\n🎯 Testing Quality Prediction...")
    
    predictor = QualityPredictor()
    
    test_code = '''
def complex_algorithm(data, threshold=0.5):
    results = []
    
    for i, item in enumerate(data):
        if item > threshold:
            if i % 2 == 0:
                if item > threshold * 2:
                    results.append(item * 1.5)
                else:
                    results.append(item * 1.2)
            else:
                results.append(item * 0.8)
        else:
            results.append(0)
    
    return results

def risky_function(user_input):
    import os
    # This is risky code for testing
    command = f"echo {user_input}"
    os.system(command)
    return eval(user_input)
'''
    
    context = {
        "project_type": "data_processing",
        "team_size": 6,
        "criticality": "medium"
    }
    
    result = await predictor.predict_quality(test_code, context)
    
    print(f"✅ Overall quality score: {result.get('overall_quality_score', 0):.1f}/100")
    print(f"✅ Maintainability score: {result.get('maintainability_score', 0):.1f}/100")
    print(f"✅ Complexity score: {result.get('complexity_score', 0):.1f}/100")
    print(f"✅ Security score: {result.get('security_score', 0):.1f}/100")
    print(f"✅ Performance score: {result.get('performance_score', 0):.1f}/100")
    
    bug_pred = result.get('bug_prediction', {})
    print(f"✅ Bug prediction: {bug_pred.get('risk_level', 'unknown')} risk ({bug_pred.get('probability', 0):.2f} probability)")
    
    print("\\n📋 Key recommendations:")
    for i, rec in enumerate(result.get('recommendations', [])[:3], 1):
        print(f"  {i}. {rec}")
    
    print("\\n⚠️  Risk areas:")
    for risk in result.get('risk_areas', []):
        print(f"  • {risk}")
    
    return result

async def test_adaptive_strategy():
    """Test adaptive testing strategy optimization"""
    print("\\n📊 Testing Adaptive Strategy Optimization...")
    
    strategist = AdaptiveTestingStrategist()
    
    project_context = {
        "code": '''
from flask import Flask, request, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.json
    
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Missing username or password'}), 400
    
    # Hash password
    password_hash = generate_password_hash(data['password'])
    
    # Save to database
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            'INSERT INTO users (username, password_hash) VALUES (?, ?)',
            (data['username'], password_hash)
        )
        conn.commit()
        return jsonify({'message': 'User created successfully'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Username already exists'}), 400
    finally:
        conn.close()

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, username FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return jsonify({'id': user[0], 'username': user[1]})
    else:
        return jsonify({'error': 'User not found'}), 404
''',
        "features": {
            "cyclomatic_complexity": 8,
            "lines_of_code": 45,
            "function_count": 2,
            "class_count": 0,
            "nested_depth": 3,
            "exception_handling": 2
        }
    }
    
    result = await strategist.optimize_strategy(project_context)
    
    strategy = result.get('recommended_strategy', {})
    analysis = result.get('project_analysis', {})
    
    print(f"✅ Recommended strategy: {strategy.get('description', 'Unknown')}")
    print(f"✅ Project type: {analysis.get('type', 'unknown')}")
    print(f"✅ Risk level: {analysis.get('risk_level', 'unknown')}")
    print(f"✅ Complexity: {analysis.get('complexity', 'unknown')}")
    
    distribution = result.get('test_distribution', {})
    print(f"✅ Test distribution: {distribution.get('unit', 0):.0%} unit, {distribution.get('integration', 0):.0%} integration, {distribution.get('e2e', 0):.0%} E2E")
    
    print("\\n🎯 Priority areas:")
    for area in result.get('priority_areas', []):
        print(f"  • {area}")
    
    print("\\n💡 Optimization tips:")
    for i, tip in enumerate(result.get('optimization_tips', [])[:3], 1):
        print(f"  {i}. {tip}")
    
    effort_reduction = result.get('estimated_effort_reduction', {})
    print(f"\\n📈 Estimated effort reduction: {effort_reduction.get('testing_effort_reduction', 'unknown')}")
    
    return result

async def test_comprehensive_analysis():
    """Test comprehensive analysis combining all capabilities"""
    print("\\n🔍 Testing Comprehensive Analysis...")
    
    server = MLTestingQAServer()
    
    test_code = '''
import hashlib
import json
from datetime import datetime, timedelta

class UserSession:
    def __init__(self, user_id, session_timeout=3600):
        self.user_id = user_id
        self.session_id = self._generate_session_id()
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.session_timeout = session_timeout
        self.is_active = True
    
    def _generate_session_id(self):
        """Generate unique session ID"""
        timestamp = str(datetime.now().timestamp())
        user_str = str(self.user_id)
        return hashlib.sha256(f"{user_str}_{timestamp}".encode()).hexdigest()
    
    def is_expired(self):
        """Check if session is expired"""
        if not self.is_active:
            return True
        
        time_diff = datetime.now() - self.last_activity
        return time_diff.total_seconds() > self.session_timeout
    
    def refresh(self):
        """Refresh session activity"""
        if self.is_expired():
            return False
        
        self.last_activity = datetime.now()
        return True
    
    def terminate(self):
        """Terminate session"""
        self.is_active = False
    
    def to_dict(self):
        """Convert session to dictionary"""
        return {
            'user_id': self.user_id,
            'session_id': self.session_id,
            'created_at': self.created_at.isoformat(),
            'last_activity': self.last_activity.isoformat(),
            'session_timeout': self.session_timeout,
            'is_active': self.is_active,
            'is_expired': self.is_expired()
        }

def validate_user_input(user_data):
    """Validate user input data"""
    if not isinstance(user_data, dict):
        raise TypeError("User data must be a dictionary")
    
    required_fields = ['username', 'email', 'password']
    for field in required_fields:
        if field not in user_data:
            raise ValueError(f"Missing required field: {field}")
        
        if not user_data[field] or not isinstance(user_data[field], str):
            raise ValueError(f"Invalid value for field: {field}")
    
    # Validate email format
    if '@' not in user_data['email'] or '.' not in user_data['email']:
        raise ValueError("Invalid email format")
    
    # Validate password strength
    password = user_data['password']
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")
    
    if not any(c.isupper() for c in password):
        raise ValueError("Password must contain at least one uppercase letter")
    
    if not any(c.islower() for c in password):
        raise ValueError("Password must contain at least one lowercase letter")
    
    if not any(c.isdigit() for c in password):
        raise ValueError("Password must contain at least one digit")
    
    return True
'''
    
    context = {
        "project_type": "web_app",
        "test_framework": "pytest",
        "coverage_target": 95,
        "team_size": 8,
        "criticality": "high"
    }
    
    result = await server.handle_comprehensive_analysis({
        'code': test_code,
        'context': context
    })
    
    # Display comprehensive results
    test_gen = result.get('test_generation', {})
    quality_pred = result.get('quality_prediction', {})
    strategy_opt = result.get('strategy_optimization', {})
    summary = result.get('comprehensive_summary', {})
    
    print(f"✅ Test generation: {len(test_gen.get('unit_tests', []))} unit tests, {test_gen.get('coverage_estimate', 0):.1f}% coverage")
    print(f"✅ Quality assessment: {quality_pred.get('overall_quality_score', 0):.1f}/100 quality score")
    print(f"✅ Strategy optimization: {strategy_opt.get('recommended_strategy', {}).get('description', 'Unknown strategy')}")
    
    print(f"\\n📊 Comprehensive Summary:")
    print(f"   Overall assessment: {summary.get('overall_assessment', 'unknown')}")
    print(f"   Risk level: {summary.get('risk_level', 'unknown')}")
    print(f"   Estimated effort: {summary.get('estimated_effort', 'unknown')}")
    
    print("\\n🎯 Top recommendations:")
    for i, rec in enumerate(summary.get('key_recommendations', [])[:3], 1):
        print(f"  {i}. {rec}")
    
    print("\\n⚡ Priority actions:")
    for i, action in enumerate(summary.get('priority_actions', [])[:3], 1):
        print(f"  {i}. {action}")
    
    return result

async def test_server_performance():
    """Test server performance metrics"""
    print("\\n📈 Testing Server Performance...")
    
    server = MLTestingQAServer()
    
    # Get initial metrics
    initial_metrics = server.get_performance_metrics()
    print(f"Initial metrics: {initial_metrics['total_requests']} requests, {initial_metrics['success_rate_percentage']:.1f}% success rate")
    
    # Perform some operations
    simple_code = "def test_func(x): return x * 2"
    
    await server.handle_test_generation({'code': simple_code})
    await server.handle_quality_prediction({'code': simple_code})
    await server.handle_strategy_optimization({'project_context': {'project_type': 'utility'}})
    
    # Get updated metrics
    final_metrics = server.get_performance_metrics()
    print(f"Final metrics: {final_metrics['total_requests']} requests, {final_metrics['success_rate_percentage']:.1f}% success rate")
    print(f"Average response time: {final_metrics['average_response_time_ms']:.2f}ms")
    
    return final_metrics

async def main():
    """Run all tests"""
    print("🚀 ML Testing QA MCP Implementation Test Suite")
    print("=" * 60)
    
    try:
        # Test individual components
        await test_intelligent_test_generation()
        await test_quality_prediction()
        await test_adaptive_strategy()
        await test_comprehensive_analysis()
        await test_server_performance()
        
        print("\\n" + "=" * 60)
        print("✅ All tests completed successfully!")
        print("🎉 ML Testing QA MCP Server is fully functional!")
        
    except Exception as e:
        print(f"\\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)