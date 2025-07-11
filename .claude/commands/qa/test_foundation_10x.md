## 🧪 TEST FOUNDATION 10X
*Shared Testing Infrastructure and Common Patterns for All Test Commands*

**Claude, execute TEST FOUNDATION SETUP with SHARED INFRASTRUCTURE, COMMON PATTERNS, and REUSABLE COMPONENTS for all testing commands.**

### 🎯 **FOUNDATION SERVICES** (Modular Testing Infrastructure)

**Test Environment Setup**:
```bash
/qa:test_foundation_10x --setup "[project_type]"
```
- Environment configuration
- Dependency installation
- Test data preparation
- Mock service setup

**Test Pattern Library**:
```bash
/qa:test_foundation_10x --patterns "[test_type]"
```
- Unit test patterns
- Integration test patterns
- Performance test patterns
- Security test patterns

**CI/CD Integration**:
```bash
/qa:test_foundation_10x --ci-setup "[platform]"
```
- GitHub Actions configuration
- GitLab CI setup
- Jenkins pipeline
- Docker test containers

**Test Data Management**:
```bash
/qa:test_foundation_10x --test-data "[scenario]"
```
- Test data generation
- Fixture management
- Database seeding
- API mock data

### 🔥 **CORE TESTING MODULES**

### **Module 1: Environment Setup**
```yaml
Test Environment:
  Python Projects:
    - Create virtual environment
    - Install pytest, coverage, pytest-mock
    - Configure test paths and imports
    - Set environment variables
    
  JavaScript/TypeScript:
    - Setup Jest/Vitest configuration
    - Install testing-library packages
    - Configure test runners
    - Setup coverage reporters
    
  ML Projects:
    - Install pytest-ml, mlflow
    - Configure GPU test allocation
    - Setup model test fixtures
    - Create test datasets
```

### **Module 2: Common Test Patterns**
```python
# Base test class pattern
class BaseTestCase:
    """Shared test functionality for all tests"""
    
    @classmethod
    def setup_class(cls):
        """Common setup for test class"""
        cls.test_data = load_test_fixtures()
        cls.mock_services = setup_mock_services()
        
    def setup_method(self):
        """Setup for each test method"""
        self.reset_database()
        self.clear_caches()
        
    def teardown_method(self):
        """Cleanup after each test"""
        self.cleanup_resources()
        
    # Shared assertion helpers
    def assert_api_response(self, response, expected_status=200):
        assert response.status_code == expected_status
        assert response.json() is not None
        
    def assert_model_performance(self, model, min_accuracy=0.9):
        metrics = evaluate_model(model, self.test_data)
        assert metrics['accuracy'] >= min_accuracy
```

### **Module 3: CI/CD Templates**
```yaml
# GitHub Actions template
name: Test Pipeline
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11]
        
    steps:
      - uses: actions/checkout@v3
      
      - name: Test Foundation Setup
        run: |
          /qa:test_foundation_10x --setup python
          
      - name: Run Tests
        run: |
          /qa:test_foundation_10x --run-tests \
            --coverage \
            --parallel \
            --fail-fast
            
      - name: Upload Results
        uses: actions/upload-artifact@v3
        with:
          name: test-results
          path: reports/
```

### **Module 4: Test Data Generators**
```python
# Test data generation patterns
class TestDataFactory:
    """Generate consistent test data"""
    
    @staticmethod
    def create_user(overrides=None):
        base_user = {
            'id': str(uuid.uuid4()),
            'name': fake.name(),
            'email': fake.email(),
            'created_at': datetime.now()
        }
        return {**base_user, **(overrides or {})}
    
    @staticmethod
    def create_ml_dataset(size=1000, features=10):
        """Generate synthetic ML test data"""
        X = np.random.randn(size, features)
        y = (X.sum(axis=1) > 0).astype(int)
        return X, y
    
    @staticmethod
    def create_api_mock_response(status=200, data=None):
        """Generate consistent API mock responses"""
        return {
            'status': status,
            'data': data or {},
            'timestamp': datetime.now().isoformat()
        }
```

### 🚀 **SHARED TESTING UTILITIES**

**3.1 Test Execution Framework**
```bash
# Unified test runner
function run_tests() {
    local test_type=${1:-"all"}
    local options=${2:-""}
    
    echo "🧪 Running $test_type tests..."
    
    case $test_type in
        unit)
            pytest tests/unit $options
            ;;
        integration)
            pytest tests/integration $options
            ;;
        ml)
            pytest tests/ml --ml-metrics $options
            ;;
        all)
            pytest tests/ --cov=src $options
            ;;
    esac
}

# Performance test wrapper
function run_performance_tests() {
    echo "⚡ Running performance benchmarks..."
    pytest tests/performance \
        --benchmark-only \
        --benchmark-autosave \
        --benchmark-compare
}
```

**3.2 Coverage Analysis**
```yaml
Coverage Configuration:
  targets:
    unit: 80%
    integration: 70%
    overall: 75%
    
  reporting:
    - terminal
    - html
    - xml (for CI)
    - json (for badges)
    
  exclusions:
    - "*/tests/*"
    - "*/migrations/*"
    - "*/__pycache__/*"
```

### 📊 **INTEGRATION WITH TEST COMMANDS**

**Commands Using This Foundation:**
```yaml
/qa:test_strategy_10x:
  - Calls: test_foundation_10x --setup --patterns
  - Adds: Strategic test planning
  
/testing:ml_pipeline_test_10x:
  - Calls: test_foundation_10x --setup ml --test-data
  - Adds: ML-specific testing
  
/qa:smart_test_generator_10x:
  - Calls: test_foundation_10x --patterns
  - Adds: AI-powered test generation
```

### 🔧 **SHARED CONFIGURATION**

```yaml
# test_config.yaml
test_foundation:
  environments:
    development:
      parallel: true
      fail_fast: false
      verbose: true
      
    ci:
      parallel: true
      fail_fast: true
      coverage_required: true
      
    production:
      smoke_tests_only: true
      monitoring_enabled: true
      
  timeouts:
    unit: 10s
    integration: 60s
    ml: 300s
    
  resources:
    max_workers: 4
    memory_limit: 4GB
    gpu_tests: optional
```

### 📈 **PERFORMANCE OPTIMIZATION**

**Test Parallelization**:
```python
# Parallel test execution
import pytest
from multiprocessing import cpu_count

pytest.main([
    '-n', str(cpu_count()),  # Use all CPUs
    '--dist=loadscope',      # Distribute by test scope
    '--maxfail=5',           # Stop after 5 failures
    'tests/'
])
```

**Smart Test Selection**:
```bash
# Run only affected tests
git diff --name-only | \
    grep -E '\.(py|js|ts)$' | \
    xargs pytest --testmon
```

### 🎯 **SUCCESS METRICS**

- **Setup Time**: < 2 minutes for any project type
- **Test Execution**: 50% faster with parallelization
- **Coverage**: Consistent 80%+ across projects
- **CI Integration**: < 5 minutes to add CI/CD
- **Reusability**: 90% of test patterns reused

**EXECUTE IMMEDIATELY**: Initialize shared test foundation for consistent, efficient testing across all test commands!