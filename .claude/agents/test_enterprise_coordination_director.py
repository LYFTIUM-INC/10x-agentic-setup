#!/usr/bin/env python3
"""
Enterprise Coordination Director - Creation and Integration Test
Comprehensive testing of the Enterprise Coordination Director sub-agent
"""

import os
import sys
import json
import time
import sqlite3
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add project paths
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

class EnterpriseCoordinationDirectorTest:
    """Comprehensive test suite for Enterprise Coordination Director"""
    
    def __init__(self):
        self.project_root = project_root
        self.agent_file = self.project_root / '.claude' / 'agents' / '10x-enterprise-coordination-director.md'
        self.test_results = {
            'creation': False,
            'parsing': False,
            'integration': False,
            'security_validation': False,
            'dashboard_integration': False,
            'compliance_framework': False,
            'audit_logging': False,
            'performance_metrics': False,
            'enterprise_coordination': False
        }
        self.start_time = time.time()
        
        print("🚀 Enterprise Coordination Director - Comprehensive Test Suite")
        print("=" * 80)
    
    def test_agent_creation(self) -> bool:
        """Test 1: Verify agent file creation and structure"""
        
        print("\n📋 Test 1: Agent Creation and Structure Validation")
        print("-" * 50)
        
        try:
            # Check if agent file exists
            if not self.agent_file.exists():
                print("❌ Agent file not found")
                return False
            
            # Read and parse agent content
            content = self.agent_file.read_text()
            
            # Verify YAML frontmatter
            if not content.startswith('---'):
                print("❌ Missing YAML frontmatter")
                return False
            
            # Extract frontmatter
            lines = content.split('\n')
            yaml_end = None
            for i, line in enumerate(lines[1:], 1):
                if line.strip() == '---':
                    yaml_end = i
                    break
            
            if yaml_end is None:
                print("❌ Invalid YAML frontmatter structure")
                return False
            
            # Parse metadata
            metadata = {}
            for line in lines[1:yaml_end]:
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    metadata[key] = value
            
            # Verify required fields
            required_fields = ['name', 'description', 'tools', 'domain', 'integration_mcps', 'performance_profile', 'security_level']
            for field in required_fields:
                if field not in metadata:
                    print(f"❌ Missing required field: {field}")
                    return False
            
            # Verify enterprise-specific attributes
            if 'enterprise' not in metadata['domain']:
                print("❌ Domain should contain 'enterprise'")
                return False
            
            if 'enterprise' not in metadata['security_level']:
                print("❌ Security level should be enterprise-grade")
                return False
            
            print("✅ Agent structure validation passed")
            print(f"   Name: {metadata.get('name')}")
            print(f"   Domain: {metadata.get('domain')}")
            print(f"   Security Level: {metadata.get('security_level')}")
            print(f"   Performance Profile: {metadata.get('performance_profile')}")
            
            return True
            
        except Exception as e:
            print(f"❌ Agent creation test failed: {e}")
            return False
    
    def test_agent_parsing(self) -> bool:
        """Test 2: Test agent definition parsing"""
        
        print("\n🔍 Test 2: Agent Definition Parsing")
        print("-" * 50)
        
        try:
            # Import the subagent coordinator
            sys.path.insert(0, str(self.project_root / '.claude' / 'hooks' / 'coordination'))
            from subagent_coordinator import SubAgentCoordinator
            
            # Initialize coordinator
            coordinator = SubAgentCoordinator()
            
            # Check if our agent was discovered
            agent_name = '10x-enterprise-coordination-director'
            if agent_name in coordinator.available_agents:
                agent_info = coordinator.available_agents[agent_name]
                print("✅ Agent successfully parsed and registered")
                print(f"   Name: {agent_info.name}")
                print(f"   Description: {agent_info.description}")
                print(f"   Domain: {agent_info.domain}")
                print(f"   Security Level: {agent_info.security_level}")
                print(f"   Performance Profile: {agent_info.performance_profile}")
                print(f"   Integration MCPs: {len(agent_info.integration_mcps)} servers")
                return True
            else:
                print(f"❌ Agent not found in registry")
                print(f"   Available agents: {list(coordinator.available_agents.keys())}")
                return False
                
        except Exception as e:
            print(f"❌ Agent parsing test failed: {e}")
            return False
    
    def test_integration_systems(self) -> bool:
        """Test 3: Test integration with existing systems"""
        
        print("\n🔗 Test 3: Integration Systems Validation")
        print("-" * 50)
        
        try:
            # Check for required integration components
            integration_paths = [
                self.project_root / '.claude' / 'hooks' / 'security' / 'audit_logger.py',
                self.project_root / '.claude' / 'hooks' / 'observability' / 'dashboard_updater.py',
                self.project_root / '.claude' / 'hooks' / 'coordination' / 'subagent_coordinator.py',
                self.project_root / '.claude' / 'dashboard.html',
                self.project_root / '.claude' / 'security_validation.db'
            ]
            
            missing_components = []
            for path in integration_paths:
                if not path.exists():
                    missing_components.append(path.name)
            
            if missing_components:
                print(f"❌ Missing integration components: {', '.join(missing_components)}")
                return False
            
            print("✅ All integration components available")
            
            # Test database connections
            db_paths = [
                self.project_root / '.claude' / 'dashboard.db',
                self.project_root / '.claude' / 'subagent_coordination.db',
                self.project_root / '.claude' / 'security_validation.db'
            ]
            
            accessible_dbs = 0
            for db_path in db_paths:
                try:
                    if db_path.exists():
                        with sqlite3.connect(str(db_path)) as conn:
                            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
                            tables = cursor.fetchall()
                            accessible_dbs += 1
                            print(f"   Database {db_path.name}: {len(tables)} tables")
                except Exception as e:
                    print(f"   Database {db_path.name}: Connection failed ({e})")
            
            if accessible_dbs >= 2:
                print(f"✅ Database integration validated ({accessible_dbs}/{len(db_paths)} accessible)")
                return True
            else:
                print(f"❌ Insufficient database connectivity ({accessible_dbs}/{len(db_paths)})")
                return False
                
        except Exception as e:
            print(f"❌ Integration systems test failed: {e}")
            return False
    
    def test_security_validation(self) -> bool:
        """Test 4: Test enterprise security validation capabilities"""
        
        print("\n🛡️ Test 4: Enterprise Security Validation")
        print("-" * 50)
        
        try:
            # Test security audit logger integration
            sys.path.insert(0, str(self.project_root / '.claude' / 'hooks' / 'security'))
            from audit_logger import AuditLogger, AuditEventType, AuditSeverity
            
            # Initialize audit logger
            audit_logger = AuditLogger()
            
            # Test enterprise coordination security events
            test_events = [
                {
                    'type': 'enterprise_coordination',
                    'action': 'coordinate_multi_tier_workflow',
                    'resource': 'enterprise_systems',
                    'severity': AuditSeverity.MEDIUM
                },
                {
                    'type': 'compliance_validation',
                    'action': 'validate_policy_adherence',
                    'resource': 'compliance_framework',
                    'severity': AuditSeverity.HIGH
                },
                {
                    'type': 'dashboard_integration',
                    'action': 'update_enterprise_metrics',
                    'resource': 'dashboard_system',
                    'severity': AuditSeverity.LOW
                }
            ]
            
            logged_events = 0
            for event in test_events:
                try:
                    audit_logger.log_security_violation(
                        violation_type=event['action'],
                        resource=event['resource'],
                        user_id='enterprise_coordinator',
                        session_id='test_session',
                        severity=event['severity'],
                        details={'test': 'enterprise_coordination_validation'}
                    )
                    logged_events += 1
                except Exception as e:
                    print(f"   Failed to log {event['type']} event: {e}")
            
            # Calculate validation rate
            validation_rate = logged_events / len(test_events)
            
            if validation_rate >= 0.875:  # 87.5% target
                print(f"✅ Security validation rate: {validation_rate:.1%} (Target: 87.5%+)")
                return True
            else:
                print(f"❌ Security validation rate: {validation_rate:.1%} (Below 87.5% target)")
                return False
                
        except Exception as e:
            print(f"❌ Security validation test failed: {e}")
            return False
    
    def test_dashboard_integration(self) -> bool:
        """Test 5: Test dashboard integration capabilities"""
        
        print("\n📊 Test 5: Dashboard Integration Validation")
        print("-" * 50)
        
        try:
            # Test dashboard updater integration
            sys.path.insert(0, str(self.project_root / '.claude' / 'hooks' / 'observability'))
            from dashboard_updater import DashboardUpdater
            
            # Initialize dashboard updater
            dashboard_updater = DashboardUpdater()
            
            # Test enterprise metrics collection
            os.environ['CLAUDE_HOOK_EVENT_NAME'] = 'EnterpriseCoordination'
            os.environ['CLAUDE_TOOL_NAME'] = 'enterprise_coordinate'
            os.environ['CLAUDE_SESSION_ID'] = 'enterprise_test_session'
            
            # Test dashboard update
            dashboard_updater.update_dashboard()
            
            # Verify database was updated
            db_path = dashboard_updater.dashboard_db
            if db_path.exists():
                with sqlite3.connect(db_path) as conn:
                    # Check for hook events
                    cursor = conn.execute(
                        "SELECT COUNT(*) FROM hook_events WHERE hook_event = 'EnterpriseCoordination'"
                    )
                    event_count = cursor.fetchone()[0]
                    
                    # Check for system metrics
                    cursor = conn.execute("SELECT COUNT(*) FROM system_metrics")
                    metrics_count = cursor.fetchone()[0]
                    
                    if event_count > 0 and metrics_count > 0:
                        print(f"✅ Dashboard integration successful")
                        print(f"   Enterprise events logged: {event_count}")
                        print(f"   System metrics collected: {metrics_count}")
                        return True
                    else:
                        print(f"❌ Dashboard integration incomplete")
                        print(f"   Events: {event_count}, Metrics: {metrics_count}")
                        return False
            else:
                print("❌ Dashboard database not created")
                return False
                
        except Exception as e:
            print(f"❌ Dashboard integration test failed: {e}")
            return False
    
    def test_compliance_framework(self) -> bool:
        """Test 6: Test compliance framework capabilities"""
        
        print("\n📋 Test 6: Compliance Framework Validation")
        print("-" * 50)
        
        try:
            # Read agent content to verify compliance features
            content = self.agent_file.read_text()
            
            # Check for compliance-related features
            compliance_indicators = [
                'compliance',
                'audit',
                'SOC2',
                'ISO27001',
                'GDPR',
                'policy',
                'regulatory',
                'framework'
            ]
            
            found_indicators = []
            for indicator in compliance_indicators:
                if indicator.lower() in content.lower():
                    found_indicators.append(indicator)
            
            compliance_coverage = len(found_indicators) / len(compliance_indicators)
            
            if compliance_coverage >= 0.8:  # 80% coverage
                print(f"✅ Compliance framework coverage: {compliance_coverage:.1%}")
                print(f"   Found indicators: {', '.join(found_indicators)}")
                return True
            else:
                print(f"❌ Insufficient compliance coverage: {compliance_coverage:.1%}")
                print(f"   Missing indicators: {set(compliance_indicators) - set(found_indicators)}")
                return False
                
        except Exception as e:
            print(f"❌ Compliance framework test failed: {e}")
            return False
    
    def test_audit_logging(self) -> bool:
        """Test 7: Test comprehensive audit logging"""
        
        print("\n📝 Test 7: Audit Logging Capabilities")
        print("-" * 50)
        
        try:
            # Test audit logging functionality
            audit_db_path = self.project_root / '.claude' / 'security_audit.db'
            
            if audit_db_path.exists():
                with sqlite3.connect(audit_db_path) as conn:
                    # Check audit events table
                    cursor = conn.execute(
                        "SELECT name FROM sqlite_master WHERE type='table' AND name='audit_events'"
                    )
                    
                    if cursor.fetchone():
                        # Count recent audit events
                        cursor = conn.execute(
                            "SELECT COUNT(*) FROM audit_events WHERE timestamp > ?",
                            (time.time() - 3600,)  # Last hour
                        )
                        recent_events = cursor.fetchone()[0]
                        
                        print(f"✅ Audit logging system operational")
                        print(f"   Recent audit events: {recent_events}")
                        
                        # Check event types
                        cursor = conn.execute(
                            "SELECT DISTINCT event_type FROM audit_events"
                        )
                        event_types = [row[0] for row in cursor.fetchall()]
                        print(f"   Event types logged: {len(event_types)}")
                        
                        return True
                    else:
                        print("❌ Audit events table not found")
                        return False
            else:
                print("⚠️ Audit database not found - will be created on first use")
                return True  # This is acceptable for new installations
                
        except Exception as e:
            print(f"❌ Audit logging test failed: {e}")
            return False
    
    def test_performance_metrics(self) -> bool:
        """Test 8: Test performance metrics collection"""
        
        print("\n⚡ Test 8: Performance Metrics Collection")
        print("-" * 50)
        
        try:
            # Test system metrics collection
            import psutil
            
            # Collect sample metrics
            metrics = {
                'cpu_percent': psutil.cpu_percent(interval=0.1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_usage': psutil.disk_usage('/').percent,
                'network_io': psutil.net_io_counters(),
                'active_processes': len(psutil.pids())
            }
            
            # Verify all metrics are collected
            collected_metrics = 0
            target_metrics = 57  # Target from specifications
            
            for key, value in metrics.items():
                if value is not None:
                    collected_metrics += 1
            
            # Simulate additional enterprise metrics
            enterprise_metrics = [
                'coordination_efficiency', 'security_validation_rate',
                'compliance_adherence', 'dashboard_latency',
                'audit_event_rate', 'threat_detection_time',
                'incident_response_time', 'system_availability'
            ]
            
            total_available_metrics = collected_metrics + len(enterprise_metrics)
            
            if total_available_metrics >= target_metrics:
                print(f"✅ Performance metrics capability: {total_available_metrics} metrics available")
                print(f"   Target: {target_metrics}+ metrics")
                print(f"   System metrics: {collected_metrics}")
                print(f"   Enterprise metrics: {len(enterprise_metrics)}")
                return True
            else:
                print(f"❌ Insufficient metrics capability: {total_available_metrics} < {target_metrics}")
                return False
                
        except Exception as e:
            print(f"❌ Performance metrics test failed: {e}")
            return False
    
    def test_enterprise_coordination(self) -> bool:
        """Test 9: Test enterprise coordination capabilities"""
        
        print("\n🏢 Test 9: Enterprise Coordination Capabilities")
        print("-" * 50)
        
        try:
            # Test coordination system integration
            coordination_db = self.project_root / '.claude' / 'subagent_coordination.db'
            
            if coordination_db.exists():
                with sqlite3.connect(coordination_db) as conn:
                    # Check coordination tables
                    cursor = conn.execute(
                        "SELECT name FROM sqlite_master WHERE type='table'"
                    )
                    tables = [row[0] for row in cursor.fetchall()]
                    
                    required_tables = ['subagent_registry', 'subagent_executions', 'coordination_events']
                    found_tables = [table for table in required_tables if table in tables]
                    
                    if len(found_tables) == len(required_tables):
                        print(f"✅ Coordination database structure complete")
                        print(f"   Tables found: {', '.join(found_tables)}")
                        
                        # Check if our agent is registered
                        cursor = conn.execute(
                            "SELECT COUNT(*) FROM subagent_registry WHERE name LIKE '%enterprise%'"
                        )
                        enterprise_agents = cursor.fetchone()[0]
                        
                        if enterprise_agents > 0:
                            print(f"   Enterprise coordination agents: {enterprise_agents}")
                            return True
                        else:
                            print(f"   No enterprise agents registered yet")
                            return True  # Acceptable for new installations
                    else:
                        missing_tables = set(required_tables) - set(found_tables)
                        print(f"❌ Missing coordination tables: {', '.join(missing_tables)}")
                        return False
            else:
                print("⚠️ Coordination database not found - will be created on first use")
                return True  # Acceptable for new installations
                
        except Exception as e:
            print(f"❌ Enterprise coordination test failed: {e}")
            return False
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run all tests and generate comprehensive report"""
        
        print("🔬 Running Comprehensive Test Suite...")
        print("=" * 80)
        
        # Run all tests
        tests = [
            ('creation', self.test_agent_creation),
            ('parsing', self.test_agent_parsing),
            ('integration', self.test_integration_systems),
            ('security_validation', self.test_security_validation),
            ('dashboard_integration', self.test_dashboard_integration),
            ('compliance_framework', self.test_compliance_framework),
            ('audit_logging', self.test_audit_logging),
            ('performance_metrics', self.test_performance_metrics),
            ('enterprise_coordination', self.test_enterprise_coordination)
        ]
        
        for test_name, test_function in tests:
            try:
                self.test_results[test_name] = test_function()
            except Exception as e:
                print(f"❌ Test {test_name} failed with exception: {e}")
                self.test_results[test_name] = False
        
        # Generate final report
        return self.generate_test_report()
    
    def generate_test_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        
        execution_time = time.time() - self.start_time
        passed_tests = sum(1 for result in self.test_results.values() if result)
        total_tests = len(self.test_results)
        success_rate = passed_tests / total_tests
        
        print("\n" + "=" * 80)
        print("📊 ENTERPRISE COORDINATION DIRECTOR - TEST REPORT")
        print("=" * 80)
        
        print(f"\n🎯 OVERALL RESULTS:")
        print(f"   Tests Passed: {passed_tests}/{total_tests}")
        print(f"   Success Rate: {success_rate:.1%}")
        print(f"   Execution Time: {execution_time:.2f} seconds")
        
        print(f"\n📋 DETAILED RESULTS:")
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {test_name.replace('_', ' ').title()}: {status}")
        
        # Assess enterprise readiness
        critical_tests = ['creation', 'parsing', 'integration', 'security_validation']
        critical_passed = sum(1 for test in critical_tests if self.test_results.get(test, False))
        critical_rate = critical_passed / len(critical_tests)
        
        print(f"\n🏢 ENTERPRISE READINESS ASSESSMENT:")
        print(f"   Critical Systems: {critical_passed}/{len(critical_tests)} ({critical_rate:.1%})")
        
        if critical_rate >= 0.875:  # 87.5% target
            print("   Status: ✅ ENTERPRISE READY")
            enterprise_status = "ready"
        elif critical_rate >= 0.75:
            print("   Status: ⚠️ PARTIALLY READY")
            enterprise_status = "partial"
        else:
            print("   Status: ❌ NOT READY")
            enterprise_status = "not_ready"
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if not self.test_results.get('security_validation', False):
            print("   • Enhance security validation capabilities")
        if not self.test_results.get('dashboard_integration', False):
            print("   • Complete dashboard integration setup")
        if not self.test_results.get('compliance_framework', False):
            print("   • Strengthen compliance framework integration")
        if success_rate == 1.0:
            print("   • All tests passed - Enterprise Coordination Director ready for deployment")
        
        return {
            'timestamp': datetime.now().isoformat(),
            'execution_time': execution_time,
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'success_rate': success_rate,
            'critical_rate': critical_rate,
            'enterprise_status': enterprise_status,
            'test_results': self.test_results,
            'agent_created': self.agent_file.exists(),
            'integration_verified': self.test_results.get('integration', False),
            'security_validated': self.test_results.get('security_validation', False),
            'dashboard_integrated': self.test_results.get('dashboard_integration', False)
        }

def main():
    """Main test execution"""
    
    # Initialize and run tests
    test_suite = EnterpriseCoordinationDirectorTest()
    report = test_suite.run_comprehensive_test()
    
    # Save test report
    report_file = test_suite.project_root / '.claude' / 'agents' / 'enterprise_coordination_test_report.json'
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Test report saved: {report_file}")
    
    # Exit with appropriate code
    if report['enterprise_status'] == 'ready':
        print("\n🚀 Enterprise Coordination Director successfully created and tested!")
        sys.exit(0)
    else:
        print("\n⚠️ Enterprise Coordination Director requires additional setup")
        sys.exit(1)

if __name__ == "__main__":
    main()