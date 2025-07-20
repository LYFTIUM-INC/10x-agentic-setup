"""
CI/CD Integration Module for ML Testing QA MCP Server
Provides integration with popular CI/CD platforms and test frameworks
"""

import asyncio
import json
import logging
import os
import subprocess
import tempfile
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class TestExecution:
    """Represents a test execution result"""
    test_name: str
    status: str  # passed, failed, skipped
    duration: float
    output: str
    error_message: Optional[str] = None
    coverage_data: Optional[Dict[str, Any]] = None

@dataclass
class CIResult:
    """Represents CI/CD integration result"""
    success: bool
    total_tests: int
    passed_tests: int
    failed_tests: int
    skipped_tests: int
    coverage_percentage: float
    duration: float
    test_executions: List[TestExecution]
    artifacts: List[str]
    recommendations: List[str]

class TestFrameworkIntegrator:
    """Integrates with popular test frameworks"""
    
    def __init__(self):
        self.supported_frameworks = {
            'pytest': self._handle_pytest,
            'unittest': self._handle_unittest,
            'nose2': self._handle_nose2,
            'jest': self._handle_jest,
            'mocha': self._handle_mocha,
            'junit': self._handle_junit
        }
        self.coverage_tools = {
            'coverage.py': self._handle_coverage_py,
            'pytest-cov': self._handle_pytest_cov,
            'istanbul': self._handle_istanbul,
            'jacoco': self._handle_jacoco
        }
    
    async def detect_framework(self, project_path: str) -> List[str]:
        """Detect test frameworks used in the project"""
        detected_frameworks = []
        
        try:
            # Check for Python frameworks
            if os.path.exists(os.path.join(project_path, 'pytest.ini')) or \
               os.path.exists(os.path.join(project_path, 'pyproject.toml')):
                detected_frameworks.append('pytest')
            
            # Check for package.json (JavaScript frameworks)
            package_json_path = os.path.join(project_path, 'package.json')
            if os.path.exists(package_json_path):
                with open(package_json_path, 'r') as f:
                    package_data = json.load(f)
                    
                dependencies = {**package_data.get('dependencies', {}), 
                              **package_data.get('devDependencies', {})}
                
                if 'jest' in dependencies:
                    detected_frameworks.append('jest')
                if 'mocha' in dependencies:
                    detected_frameworks.append('mocha')
            
            # Check for Java frameworks
            if os.path.exists(os.path.join(project_path, 'pom.xml')) or \
               os.path.exists(os.path.join(project_path, 'build.gradle')):
                detected_frameworks.append('junit')
            
            # Fallback to unittest for Python projects
            if any(f.endswith('.py') for f in os.listdir(project_path)) and not detected_frameworks:
                detected_frameworks.append('unittest')
                
        except Exception as e:
            logger.error(f"Framework detection failed: {e}")
        
        return detected_frameworks
    
    async def execute_tests(self, project_path: str, framework: str, 
                          test_files: List[str] = None) -> CIResult:
        """Execute tests using specified framework"""
        
        if framework not in self.supported_frameworks:
            raise ValueError(f"Unsupported framework: {framework}")
        
        try:
            return await self.supported_frameworks[framework](project_path, test_files)
        except Exception as e:
            logger.error(f"Test execution failed for {framework}: {e}")
            return CIResult(
                success=False,
                total_tests=0,
                passed_tests=0,
                failed_tests=0,
                skipped_tests=0,
                coverage_percentage=0.0,
                duration=0.0,
                test_executions=[],
                artifacts=[],
                recommendations=[f"Test execution failed: {str(e)}"]
            )
    
    async def _handle_pytest(self, project_path: str, test_files: List[str] = None) -> CIResult:
        """Handle pytest execution"""
        
        cmd = ['python', '-m', 'pytest', '--tb=short', '--json-report', 
               '--json-report-file=test_results.json']
        
        if test_files:
            cmd.extend(test_files)
        else:
            cmd.append('tests/')
        
        # Add coverage if available
        if os.system('python -c "import pytest_cov"') == 0:
            cmd.extend(['--cov=src', '--cov-report=json:coverage.json'])
        
        start_time = datetime.now()
        
        try:
            result = subprocess.run(
                cmd,
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            
            # Parse JSON report if available
            json_report_path = os.path.join(project_path, 'test_results.json')
            test_executions = []
            total_tests = passed_tests = failed_tests = skipped_tests = 0
            
            if os.path.exists(json_report_path):
                with open(json_report_path, 'r') as f:
                    report_data = json.load(f)
                
                total_tests = report_data.get('summary', {}).get('total', 0)
                passed_tests = report_data.get('summary', {}).get('passed', 0)
                failed_tests = report_data.get('summary', {}).get('failed', 0)
                skipped_tests = report_data.get('summary', {}).get('skipped', 0)
                
                for test in report_data.get('tests', []):
                    test_executions.append(TestExecution(
                        test_name=test.get('nodeid', 'unknown'),
                        status=test.get('outcome', 'unknown'),
                        duration=test.get('duration', 0.0),
                        output=test.get('stdout', ''),
                        error_message=test.get('stderr') if test.get('outcome') == 'failed' else None
                    ))
            
            # Parse coverage if available
            coverage_percentage = 0.0
            coverage_path = os.path.join(project_path, 'coverage.json')
            if os.path.exists(coverage_path):
                with open(coverage_path, 'r') as f:
                    coverage_data = json.load(f)
                    coverage_percentage = coverage_data.get('totals', {}).get('percent_covered', 0.0)
            
            success = result.returncode == 0
            artifacts = ['test_results.json', 'coverage.json'] if os.path.exists(coverage_path) else ['test_results.json']
            
            recommendations = []
            if coverage_percentage < 80:
                recommendations.append(f"Coverage is {coverage_percentage:.1f}% - consider adding more tests")
            if failed_tests > 0:
                recommendations.append(f"{failed_tests} tests failed - review and fix failing tests")
            
            return CIResult(
                success=success,
                total_tests=total_tests,
                passed_tests=passed_tests,
                failed_tests=failed_tests,
                skipped_tests=skipped_tests,
                coverage_percentage=coverage_percentage,
                duration=duration,
                test_executions=test_executions,
                artifacts=artifacts,
                recommendations=recommendations
            )
            
        except subprocess.TimeoutExpired:
            return CIResult(
                success=False,
                total_tests=0,
                passed_tests=0,
                failed_tests=0,
                skipped_tests=0,
                coverage_percentage=0.0,
                duration=300.0,
                test_executions=[],
                artifacts=[],
                recommendations=["Tests timed out after 5 minutes - consider optimizing test performance"]
            )
    
    async def _handle_unittest(self, project_path: str, test_files: List[str] = None) -> CIResult:
        """Handle unittest execution"""
        
        cmd = ['python', '-m', 'unittest', 'discover', '-v']
        
        if test_files:
            # For unittest, we need to convert file paths to module paths
            cmd = ['python', '-m', 'unittest', '-v'] + [
                f.replace('/', '.').replace('.py', '') for f in test_files
            ]
        
        start_time = datetime.now()
        
        try:
            result = subprocess.run(
                cmd,
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            
            # Parse unittest output
            output_lines = result.stderr.split('\n')
            test_executions = []
            total_tests = passed_tests = failed_tests = skipped_tests = 0
            
            for line in output_lines:
                if ' ... ok' in line:
                    test_name = line.split(' ... ok')[0].strip()
                    test_executions.append(TestExecution(
                        test_name=test_name,
                        status='passed',
                        duration=0.0,
                        output=line
                    ))
                    passed_tests += 1
                elif ' ... FAIL' in line or ' ... ERROR' in line:
                    test_name = line.split(' ... ')[0].strip()
                    status = 'failed'
                    test_executions.append(TestExecution(
                        test_name=test_name,
                        status=status,
                        duration=0.0,
                        output=line,
                        error_message=line
                    ))
                    failed_tests += 1
                elif ' ... skipped' in line:
                    test_name = line.split(' ... skipped')[0].strip()
                    test_executions.append(TestExecution(
                        test_name=test_name,
                        status='skipped',
                        duration=0.0,
                        output=line
                    ))
                    skipped_tests += 1
            
            total_tests = passed_tests + failed_tests + skipped_tests
            success = result.returncode == 0
            
            recommendations = []
            if failed_tests > 0:
                recommendations.append(f"{failed_tests} tests failed - review unittest output")
            if total_tests == 0:
                recommendations.append("No tests found - ensure test files are properly named (test_*.py)")
            
            return CIResult(
                success=success,
                total_tests=total_tests,
                passed_tests=passed_tests,
                failed_tests=failed_tests,
                skipped_tests=skipped_tests,
                coverage_percentage=0.0,  # unittest doesn't provide coverage by default
                duration=duration,
                test_executions=test_executions,
                artifacts=[],
                recommendations=recommendations
            )
            
        except subprocess.TimeoutExpired:
            return CIResult(
                success=False,
                total_tests=0,
                passed_tests=0,
                failed_tests=0,
                skipped_tests=0,
                coverage_percentage=0.0,
                duration=300.0,
                test_executions=[],
                artifacts=[],
                recommendations=["Tests timed out after 5 minutes"]
            )
    
    async def _handle_nose2(self, project_path: str, test_files: List[str] = None) -> CIResult:
        """Handle nose2 execution"""
        # Similar implementation to unittest but using nose2
        return await self._handle_unittest(project_path, test_files)
    
    async def _handle_jest(self, project_path: str, test_files: List[str] = None) -> CIResult:
        """Handle Jest execution"""
        
        cmd = ['npm', 'test', '--', '--json', '--coverage']
        
        if test_files:
            cmd.extend(test_files)
        
        start_time = datetime.now()
        
        try:
            result = subprocess.run(
                cmd,
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            
            # Parse Jest JSON output
            test_executions = []
            total_tests = passed_tests = failed_tests = skipped_tests = 0
            coverage_percentage = 0.0
            
            try:
                # Jest outputs JSON to stdout
                jest_output = json.loads(result.stdout)
                
                for test_result in jest_output.get('testResults', []):
                    for assertion in test_result.get('assertionResults', []):
                        test_executions.append(TestExecution(
                            test_name=assertion.get('title', 'unknown'),
                            status=assertion.get('status', 'unknown'),
                            duration=assertion.get('duration', 0.0) / 1000.0,  # Convert ms to seconds
                            output=assertion.get('fullName', ''),
                            error_message=assertion.get('failureMessages', [None])[0]
                        ))
                        
                        if assertion.get('status') == 'passed':
                            passed_tests += 1
                        elif assertion.get('status') == 'failed':
                            failed_tests += 1
                        else:
                            skipped_tests += 1
                
                total_tests = passed_tests + failed_tests + skipped_tests
                
                # Extract coverage if available
                coverage_summary = jest_output.get('coverageMap', {}).get('summary', {})
                if coverage_summary:
                    lines_coverage = coverage_summary.get('lines', {})
                    coverage_percentage = lines_coverage.get('pct', 0.0)
                    
            except json.JSONDecodeError:
                # Fallback to parsing text output
                logger.warning("Could not parse Jest JSON output, using text parsing")
            
            success = result.returncode == 0
            artifacts = ['coverage/lcov-report/index.html'] if coverage_percentage > 0 else []
            
            recommendations = []
            if coverage_percentage < 80:
                recommendations.append(f"Coverage is {coverage_percentage:.1f}% - add more tests")
            if failed_tests > 0:
                recommendations.append(f"{failed_tests} tests failed - check Jest output")
            
            return CIResult(
                success=success,
                total_tests=total_tests,
                passed_tests=passed_tests,
                failed_tests=failed_tests,
                skipped_tests=skipped_tests,
                coverage_percentage=coverage_percentage,
                duration=duration,
                test_executions=test_executions,
                artifacts=artifacts,
                recommendations=recommendations
            )
            
        except subprocess.TimeoutExpired:
            return CIResult(
                success=False,
                total_tests=0,
                passed_tests=0,
                failed_tests=0,
                skipped_tests=0,
                coverage_percentage=0.0,
                duration=300.0,
                test_executions=[],
                artifacts=[],
                recommendations=["Jest tests timed out after 5 minutes"]
            )
    
    async def _handle_mocha(self, project_path: str, test_files: List[str] = None) -> CIResult:
        """Handle Mocha execution"""
        # Similar to Jest but for Mocha
        cmd = ['npx', 'mocha', '--reporter', 'json']
        
        if test_files:
            cmd.extend(test_files)
        
        # Implementation similar to Jest
        return await self._handle_jest(project_path, test_files)
    
    async def _handle_junit(self, project_path: str, test_files: List[str] = None) -> CIResult:
        """Handle JUnit execution"""
        
        # Check for Maven or Gradle
        if os.path.exists(os.path.join(project_path, 'pom.xml')):
            cmd = ['mvn', 'test']
        elif os.path.exists(os.path.join(project_path, 'build.gradle')):
            cmd = ['./gradlew', 'test']
        else:
            cmd = ['java', '-cp', 'junit-platform-console-standalone.jar', 
                   'org.junit.platform.console.ConsoleLauncher', '--scan-classpath']
        
        start_time = datetime.now()
        
        try:
            result = subprocess.run(
                cmd,
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=600  # Java builds can take longer
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            
            # Parse Maven/Gradle output
            output_lines = result.stdout.split('\n')
            test_executions = []
            total_tests = passed_tests = failed_tests = skipped_tests = 0
            
            # Look for test summary in output
            for line in output_lines:
                if 'Tests run:' in line:
                    # Parse line like "Tests run: 5, Failures: 0, Errors: 0, Skipped: 1"
                    parts = line.split(',')
                    for part in parts:
                        part = part.strip()
                        if part.startswith('Tests run:'):
                            total_tests = int(part.split(':')[1].strip())
                        elif part.startswith('Failures:'):
                            failed_tests += int(part.split(':')[1].strip())
                        elif part.startswith('Errors:'):
                            failed_tests += int(part.split(':')[1].strip())
                        elif part.startswith('Skipped:'):
                            skipped_tests = int(part.split(':')[1].strip())
            
            passed_tests = total_tests - failed_tests - skipped_tests
            success = result.returncode == 0
            
            # Look for JaCoCo coverage reports
            coverage_percentage = 0.0
            jacoco_xml = os.path.join(project_path, 'target/site/jacoco/jacoco.xml')
            if os.path.exists(jacoco_xml):
                # Parse JaCoCo XML for coverage percentage
                try:
                    import xml.etree.ElementTree as ET
                    tree = ET.parse(jacoco_xml)
                    root = tree.getroot()
                    
                    # Find line coverage
                    for counter in root.findall('.//counter[@type="LINE"]'):
                        covered = int(counter.get('covered', 0))
                        missed = int(counter.get('missed', 0))
                        total = covered + missed
                        if total > 0:
                            coverage_percentage = (covered / total) * 100.0
                            break
                except Exception as e:
                    logger.warning(f"Could not parse JaCoCo coverage: {e}")
            
            artifacts = ['target/surefire-reports/', 'target/site/jacoco/'] if os.path.exists(jacoco_xml) else ['target/surefire-reports/']
            
            recommendations = []
            if coverage_percentage < 80:
                recommendations.append(f"Coverage is {coverage_percentage:.1f}% - add more unit tests")
            if failed_tests > 0:
                recommendations.append(f"{failed_tests} tests failed - check surefire reports")
            
            return CIResult(
                success=success,
                total_tests=total_tests,
                passed_tests=passed_tests,
                failed_tests=failed_tests,
                skipped_tests=skipped_tests,
                coverage_percentage=coverage_percentage,
                duration=duration,
                test_executions=test_executions,
                artifacts=artifacts,
                recommendations=recommendations
            )
            
        except subprocess.TimeoutExpired:
            return CIResult(
                success=False,
                total_tests=0,
                passed_tests=0,
                failed_tests=0,
                skipped_tests=0,
                coverage_percentage=0.0,
                duration=600.0,
                test_executions=[],
                artifacts=[],
                recommendations=["Java tests timed out after 10 minutes"]
            )
    
    async def _handle_coverage_py(self, project_path: str) -> Dict[str, Any]:
        """Handle coverage.py integration"""
        # This would be called separately to get coverage data
        pass
    
    async def _handle_pytest_cov(self, project_path: str) -> Dict[str, Any]:
        """Handle pytest-cov integration"""
        # Already integrated in pytest handler
        pass
    
    async def _handle_istanbul(self, project_path: str) -> Dict[str, Any]:
        """Handle Istanbul coverage integration"""
        # For JavaScript projects
        pass
    
    async def _handle_jacoco(self, project_path: str) -> Dict[str, Any]:
        """Handle JaCoCo coverage integration"""
        # Already integrated in JUnit handler
        pass

class CICDPlatformIntegrator:
    """Integrates with CI/CD platforms"""
    
    def __init__(self):
        self.platforms = {
            'github-actions': self._handle_github_actions,
            'gitlab-ci': self._handle_gitlab_ci,
            'jenkins': self._handle_jenkins,
            'azure-devops': self._handle_azure_devops,
            'travis-ci': self._handle_travis_ci,
            'circle-ci': self._handle_circle_ci
        }
    
    async def detect_platform(self, project_path: str) -> List[str]:
        """Detect CI/CD platforms used in project"""
        detected_platforms = []
        
        # GitHub Actions
        if os.path.exists(os.path.join(project_path, '.github/workflows')):
            detected_platforms.append('github-actions')
        
        # GitLab CI
        if os.path.exists(os.path.join(project_path, '.gitlab-ci.yml')):
            detected_platforms.append('gitlab-ci')
        
        # Jenkins
        if os.path.exists(os.path.join(project_path, 'Jenkinsfile')):
            detected_platforms.append('jenkins')
        
        # Azure DevOps
        if os.path.exists(os.path.join(project_path, 'azure-pipelines.yml')):
            detected_platforms.append('azure-devops')
        
        # Travis CI
        if os.path.exists(os.path.join(project_path, '.travis.yml')):
            detected_platforms.append('travis-ci')
        
        # Circle CI
        if os.path.exists(os.path.join(project_path, '.circleci/config.yml')):
            detected_platforms.append('circle-ci')
        
        return detected_platforms
    
    async def generate_config(self, platform: str, test_config: Dict[str, Any]) -> str:
        """Generate CI/CD configuration for specified platform"""
        
        if platform not in self.platforms:
            raise ValueError(f"Unsupported platform: {platform}")
        
        return await self.platforms[platform](test_config)
    
    async def _handle_github_actions(self, test_config: Dict[str, Any]) -> str:
        """Generate GitHub Actions workflow"""
        
        framework = test_config.get('framework', 'pytest')
        python_version = test_config.get('python_version', '3.9')
        node_version = test_config.get('node_version', '16')
        
        if framework in ['pytest', 'unittest']:
            workflow = f"""
name: Test Suite

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        python-version: ['{python_version}']
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{{{ matrix.python-version }}}}
      uses: actions/setup-python@v4
      with:
        python-version: ${{{{ matrix.python-version }}}}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests with {framework}
      run: |
        {framework} tests/ --cov=src --cov-report=xml --cov-report=html
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella
        fail_ci_if_error: true
    
    - name: Archive test results
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: test-results
        path: |
          htmlcov/
          coverage.xml
"""
        
        elif framework in ['jest', 'mocha']:
            workflow = f"""
name: Test Suite

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        node-version: ['{node_version}']
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Use Node.js ${{{{ matrix.node-version }}}}
      uses: actions/setup-node@v3
      with:
        node-version: ${{{{ matrix.node-version }}}}
        cache: 'npm'
    
    - name: Install dependencies
      run: npm ci
    
    - name: Run tests with {framework}
      run: npm test -- --coverage
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage/lcov.info
        flags: unittests
        name: codecov-umbrella
        fail_ci_if_error: true
    
    - name: Archive test results
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: test-results
        path: |
          coverage/
          test-results.xml
"""
        
        else:
            workflow = f"""
name: Test Suite

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up JDK 11
      uses: actions/setup-java@v3
      with:
        java-version: '11'
        distribution: 'temurin'
    
    - name: Cache Maven dependencies
      uses: actions/cache@v3
      with:
        path: ~/.m2
        key: ${{{{ runner.os }}}}-m2-${{{{ hashFiles('**/pom.xml') }}}}
        restore-keys: ${{{{ runner.os }}}}-m2
    
    - name: Run tests
      run: mvn clean test
    
    - name: Generate test report
      uses: dorny/test-reporter@v1
      if: success() || failure()
      with:
        name: Maven Tests
        path: target/surefire-reports/*.xml
        reporter: java-junit
"""
        
        return workflow.strip()
    
    async def _handle_gitlab_ci(self, test_config: Dict[str, Any]) -> str:
        """Generate GitLab CI configuration"""
        
        framework = test_config.get('framework', 'pytest')
        
        if framework in ['pytest', 'unittest']:
            config = f"""
stages:
  - test
  - coverage

variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"

cache:
  paths:
    - .cache/pip/
    - venv/

test:
  stage: test
  image: python:3.9
  before_script:
    - python -m venv venv
    - source venv/bin/activate
    - pip install --upgrade pip
    - pip install -r requirements.txt
    - pip install pytest pytest-cov
  script:
    - {framework} tests/ --cov=src --cov-report=xml --cov-report=html --junitxml=report.xml
  artifacts:
    reports:
      junit: report.xml
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
    paths:
      - htmlcov/
    expire_in: 1 week
  coverage: '/TOTAL.+?(\\d+%)/'

pages:
  stage: coverage
  dependencies:
    - test
  script:
    - mv htmlcov/ public/
  artifacts:
    paths:
      - public
  only:
    - main
"""
        
        elif framework in ['jest', 'mocha']:
            config = f"""
stages:
  - test
  - coverage

variables:
  NPM_CONFIG_CACHE: "$CI_PROJECT_DIR/.npm"

cache:
  paths:
    - .npm/
    - node_modules/

test:
  stage: test
  image: node:16
  before_script:
    - npm ci
  script:
    - npm test -- --coverage --watchAll=false
  artifacts:
    reports:
      junit: junit.xml
      coverage_report:
        coverage_format: cobertura
        path: coverage/cobertura-coverage.xml
    paths:
      - coverage/
    expire_in: 1 week
  coverage: '/Lines\\s*:\\s*(\\d+\\.?\\d*)%/'

pages:
  stage: coverage
  dependencies:
    - test
  script:
    - mv coverage/lcov-report/ public/
  artifacts:
    paths:
      - public
  only:
    - main
"""
        
        return config.strip()
    
    async def _handle_jenkins(self, test_config: Dict[str, Any]) -> str:
        """Generate Jenkinsfile"""
        
        framework = test_config.get('framework', 'pytest')
        
        if framework in ['pytest', 'unittest']:
            jenkinsfile = f"""
pipeline {{
    agent any
    
    environment {{
        PYTHONPATH = "${{WORKSPACE}}"
    }}
    
    stages {{
        stage('Setup') {{
            steps {{
                sh 'python -m venv venv'
                sh 'source venv/bin/activate && pip install --upgrade pip'
                sh 'source venv/bin/activate && pip install -r requirements.txt'
                sh 'source venv/bin/activate && pip install pytest pytest-cov'
            }}
        }}
        
        stage('Test') {{
            steps {{
                sh 'source venv/bin/activate && {framework} tests/ --cov=src --cov-report=xml --junitxml=test-results.xml'
            }}
            post {{
                always {{
                    junit 'test-results.xml'
                    publishCoverage adapters: [coberturaAdapter('coverage.xml')], sourceFileResolver: sourceFiles('STORE_LAST_BUILD')
                }}
            }}
        }}
        
        stage('Archive') {{
            steps {{
                archiveArtifacts artifacts: 'coverage.xml,test-results.xml', fingerprint: true
            }}
        }}
    }}
    
    post {{
        always {{
            cleanWs()
        }}
    }}
}}
"""
        
        return jenkinsfile.strip()
    
    async def _handle_azure_devops(self, test_config: Dict[str, Any]) -> str:
        """Generate Azure DevOps pipeline"""
        
        framework = test_config.get('framework', 'pytest')
        
        config = f"""
trigger:
- main
- develop

pool:
  vmImage: 'ubuntu-latest'

variables:
  pythonVersion: '3.9'

steps:
- task: UsePythonVersion@0
  inputs:
    versionSpec: '$(pythonVersion)'
  displayName: 'Use Python $(pythonVersion)'

- script: |
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    pip install pytest pytest-cov
  displayName: 'Install dependencies'

- script: |
    {framework} tests/ --cov=src --cov-report=xml --junitxml=test-results.xml
  displayName: 'Run tests'

- task: PublishTestResults@2
  condition: succeededOrFailed()
  inputs:
    testResultsFiles: 'test-results.xml'
    testRunTitle: 'Publish test results'

- task: PublishCodeCoverageResults@1
  inputs:
    codeCoverageTool: Cobertura
    summaryFileLocation: 'coverage.xml'
"""
        
        return config.strip()
    
    async def _handle_travis_ci(self, test_config: Dict[str, Any]) -> str:
        """Generate Travis CI configuration"""
        
        framework = test_config.get('framework', 'pytest')
        python_version = test_config.get('python_version', '3.9')
        
        config = f"""
language: python
python:
  - "{python_version}"

install:
  - pip install -r requirements.txt
  - pip install pytest pytest-cov codecov

script:
  - {framework} tests/ --cov=src

after_success:
  - codecov

cache: pip

branches:
  only:
    - main
    - develop
"""
        
        return config.strip()
    
    async def _handle_circle_ci(self, test_config: Dict[str, Any]) -> str:
        """Generate Circle CI configuration"""
        
        framework = test_config.get('framework', 'pytest')
        
        config = f"""
version: 2.1

orbs:
  python: circleci/python@2.0.3

workflows:
  test-workflow:
    jobs:
      - test

jobs:
  test:
    docker:
      - image: cimg/python:3.9
    steps:
      - checkout
      - python/install-packages:
          pkg-manager: pip
      - run:
          name: Install test dependencies
          command: pip install pytest pytest-cov
      - run:
          name: Run tests
          command: {framework} tests/ --cov=src --cov-report=xml --junitxml=test-results.xml
      - store_test_results:
          path: test-results.xml
      - store_artifacts:
          path: coverage.xml
"""
        
        return config.strip()

class TestOptimizer:
    """Optimizes test execution and selection"""
    
    def __init__(self):
        self.optimization_strategies = {
            'parallel': self._optimize_parallel_execution,
            'selective': self._optimize_test_selection,
            'incremental': self._optimize_incremental_testing,
            'cache': self._optimize_test_caching
        }
    
    async def optimize_test_suite(self, project_path: str, optimization_type: str = 'parallel') -> Dict[str, Any]:
        """Optimize test suite execution"""
        
        if optimization_type not in self.optimization_strategies:
            raise ValueError(f"Unknown optimization type: {optimization_type}")
        
        return await self.optimization_strategies[optimization_type](project_path)
    
    async def _optimize_parallel_execution(self, project_path: str) -> Dict[str, Any]:
        """Optimize for parallel test execution"""
        
        recommendations = []
        
        # Analyze test files for parallelization opportunities
        test_files = []
        for root, dirs, files in os.walk(os.path.join(project_path, 'tests')):
            for file in files:
                if file.startswith('test_') and file.endswith('.py'):
                    test_files.append(os.path.join(root, file))
        
        # Estimate parallel execution benefits
        total_tests = len(test_files)
        estimated_speedup = min(total_tests / 4, 8)  # Assume 4 tests per core, max 8x speedup
        
        recommendations.append(f"Use pytest-xdist for parallel execution: pytest -n auto")
        recommendations.append(f"Estimated speedup: {estimated_speedup:.1f}x with parallel execution")
        
        if total_tests > 100:
            recommendations.append("Consider splitting large test files for better parallelization")
        
        return {
            'optimization_type': 'parallel',
            'estimated_speedup': estimated_speedup,
            'recommendations': recommendations,
            'configuration': {
                'pytest_args': ['-n', 'auto'],
                'max_workers': 8
            }
        }
    
    async def _optimize_test_selection(self, project_path: str) -> Dict[str, Any]:
        """Optimize test selection based on code changes"""
        
        recommendations = []
        
        # Analyze git history for test-to-code mappings
        try:
            result = subprocess.run(
                ['git', 'log', '--name-only', '--pretty=format:', '-10'],
                cwd=project_path,
                capture_output=True,
                text=True
            )
            
            changed_files = [f for f in result.stdout.split('\n') if f.strip()]
            
            # Map source files to test files
            test_mappings = {}
            for file in changed_files:
                if file.endswith('.py') and not file.startswith('test_'):
                    # Find corresponding test file
                    test_file = f"test_{os.path.basename(file)}"
                    test_path = os.path.join(project_path, 'tests', test_file)
                    if os.path.exists(test_path):
                        test_mappings[file] = test_file
            
            recommendations.append("Run only tests related to changed files")
            recommendations.append(f"Found {len(test_mappings)} file-to-test mappings")
            
            if len(test_mappings) > 0:
                recommendations.append("Use pytest --lf to run only failed tests")
                recommendations.append("Use pytest --ff to run failed tests first")
            
        except Exception as e:
            recommendations.append(f"Could not analyze git history: {e}")
        
        return {
            'optimization_type': 'selective',
            'test_mappings': test_mappings if 'test_mappings' in locals() else {},
            'recommendations': recommendations,
            'configuration': {
                'pytest_args': ['--lf', '--ff'],
                'selective_testing': True
            }
        }
    
    async def _optimize_incremental_testing(self, project_path: str) -> Dict[str, Any]:
        """Optimize for incremental testing"""
        
        recommendations = []
        
        # Check for pytest-watch or similar tools
        recommendations.append("Use pytest-watch for continuous testing: ptw")
        recommendations.append("Use pytest --cache-show to see test cache")
        recommendations.append("Use pytest --co to collect tests without running")
        
        # Analyze test duration for prioritization
        cache_dir = os.path.join(project_path, '.pytest_cache')
        if os.path.exists(cache_dir):
            recommendations.append("Leverage pytest cache for faster test discovery")
        
        return {
            'optimization_type': 'incremental',
            'recommendations': recommendations,
            'configuration': {
                'pytest_args': ['--cache-show'],
                'watch_mode': True
            }
        }
    
    async def _optimize_test_caching(self, project_path: str) -> Dict[str, Any]:
        """Optimize test result caching"""
        
        recommendations = []
        
        # Check current cache usage
        cache_dir = os.path.join(project_path, '.pytest_cache')
        if os.path.exists(cache_dir):
            cache_size = sum(os.path.getsize(os.path.join(dirpath, filename))
                           for dirpath, dirnames, filenames in os.walk(cache_dir)
                           for filename in filenames)
            cache_size_mb = cache_size / (1024 * 1024)
            recommendations.append(f"Current cache size: {cache_size_mb:.1f} MB")
        
        recommendations.append("Enable pytest result caching with --cache-clear")
        recommendations.append("Use pytest --stepwise to stop at first failure")
        recommendations.append("Cache test data and fixtures for faster setup")
        
        return {
            'optimization_type': 'cache',
            'cache_size': cache_size_mb if 'cache_size_mb' in locals() else 0,
            'recommendations': recommendations,
            'configuration': {
                'pytest_args': ['--cache-clear', '--stepwise'],
                'fixture_caching': True
            }
        }

# Main integration class
class MLTestingCICDIntegrator:
    """Main class for CI/CD integration with ML Testing QA"""
    
    def __init__(self):
        self.framework_integrator = TestFrameworkIntegrator()
        self.platform_integrator = CICDPlatformIntegrator()
        self.test_optimizer = TestOptimizer()
    
    async def setup_project_testing(self, project_path: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Complete CI/CD setup for a project"""
        
        if config is None:
            config = {}
        
        try:
            # Detect frameworks and platforms
            frameworks = await self.framework_integrator.detect_framework(project_path)
            platforms = await self.platform_integrator.detect_platform(project_path)
            
            # Execute tests with detected framework
            test_results = []
            for framework in frameworks:
                result = await self.framework_integrator.execute_tests(project_path, framework)
                test_results.append(result)
            
            # Generate CI/CD configurations if requested
            ci_configs = {}
            if config.get('generate_configs', False):
                for platform in platforms or ['github-actions']:  # Default to GitHub Actions
                    for framework in frameworks:
                        ci_config = await self.platform_integrator.generate_config(
                            platform, {'framework': framework}
                        )
                        ci_configs[f"{platform}_{framework}"] = ci_config
            
            # Optimize test execution
            optimization = await self.test_optimizer.optimize_test_suite(
                project_path, config.get('optimization_type', 'parallel')
            )
            
            return {
                'success': True,
                'detected_frameworks': frameworks,
                'detected_platforms': platforms,
                'test_results': test_results,
                'ci_configurations': ci_configs,
                'optimization': optimization,
                'recommendations': self._generate_integration_recommendations(
                    frameworks, platforms, test_results, optimization
                )
            }
            
        except Exception as e:
            logger.error(f"CI/CD integration setup failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'recommendations': ["Check project structure and dependencies"]
            }
    
    def _generate_integration_recommendations(self, frameworks: List[str], platforms: List[str], 
                                            test_results: List[CIResult], optimization: Dict[str, Any]) -> List[str]:
        """Generate comprehensive integration recommendations"""
        
        recommendations = []
        
        # Framework recommendations
        if not frameworks:
            recommendations.append("No test framework detected - add pytest or unittest")
        elif len(frameworks) > 1:
            recommendations.append(f"Multiple frameworks detected ({', '.join(frameworks)}) - consider standardizing")
        
        # Platform recommendations
        if not platforms:
            recommendations.append("No CI/CD platform detected - add GitHub Actions workflow")
        
        # Test result recommendations
        for result in test_results:
            if result.coverage_percentage < 80:
                recommendations.append(f"Test coverage is {result.coverage_percentage:.1f}% - aim for 80%+")
            if result.failed_tests > 0:
                recommendations.append(f"{result.failed_tests} tests failing - fix before CI/CD setup")
        
        # Optimization recommendations
        recommendations.extend(optimization.get('recommendations', []))
        
        # General best practices
        recommendations.extend([
            "Use branch protection rules to require passing tests",
            "Set up automated dependency updates with Dependabot",
            "Configure code quality gates with coverage thresholds",
            "Add pre-commit hooks for code formatting and linting"
        ])
        
        return recommendations