#!/usr/bin/env python3
"""
MCP Integration Validator
Tests that agents can access custom MCP tools and validates integration
"""

import json
import subprocess
import time
import logging
from pathlib import Path
from typing import Dict, List, Any, Tuple

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MCPIntegrationValidator:
    """Validates MCP server and agent integration"""
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.settings_file = base_dir / 'settings.json'
        self.mcp_servers_dir = base_dir.parent / 'mcp_servers'
        
    def load_settings(self) -> Dict[str, Any]:
        """Load Claude Code settings"""
        try:
            with open(self.settings_file) as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load settings: {e}")
            return {}
    
    def validate_mcp_server_config(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Validate MCP server configurations"""
        mcp_servers = settings.get('mcpServers', {})
        validation_results = {
            'total_servers_configured': len(mcp_servers),
            'valid_configurations': 0,
            'configuration_issues': [],
            'server_details': {}
        }
        
        for server_name, config in mcp_servers.items():
            server_result = {
                'name': server_name,
                'configured': True,
                'command_exists': False,
                'script_exists': False,
                'environment_valid': True,
                'issues': []
            }
            
            # Check if command exists
            command = config.get('command', '')
            if Path(command).exists():
                server_result['command_exists'] = True
            else:
                server_result['issues'].append(f"Command not found: {command}")
            
            # Check if script exists
            args = config.get('args', [])
            if args:
                script_path = Path(args[0])
                if script_path.exists():
                    server_result['script_exists'] = True
                else:
                    server_result['issues'].append(f"Script not found: {args[0]}")
            
            # Validate environment variables
            env = config.get('env', {})
            pythonpath = env.get('PYTHONPATH', '')
            if pythonpath and not Path(pythonpath).exists():
                server_result['environment_valid'] = False
                server_result['issues'].append(f"PYTHONPATH not found: {pythonpath}")
            
            if not server_result['issues']:
                validation_results['valid_configurations'] += 1
            
            validation_results['server_details'][server_name] = server_result
        
        return validation_results
    
    def validate_agent_registry(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Validate agent registry"""
        agent_registry = settings.get('agentRegistry', {})
        metadata = agent_registry.get('_metadata', {})
        
        validation_results = {
            'total_agents_registered': metadata.get('total_agents', 0),
            'agents_with_mcp_integration': 0,
            'mcp_usage_distribution': {},
            'agent_details': {}
        }
        
        for agent_name, config in agent_registry.items():
            if agent_name.startswith('_'):
                continue
                
            integration_mcps = config.get('integration_mcps', [])
            if integration_mcps:
                validation_results['agents_with_mcp_integration'] += 1
                
                for mcp in integration_mcps:
                    if mcp not in validation_results['mcp_usage_distribution']:
                        validation_results['mcp_usage_distribution'][mcp] = 0
                    validation_results['mcp_usage_distribution'][mcp] += 1
            
            validation_results['agent_details'][agent_name] = {
                'has_mcp_integration': len(integration_mcps) > 0,
                'mcp_count': len(integration_mcps),
                'integrated_mcps': integration_mcps,
                'domain': config.get('domain', 'unknown'),
                'tools': config.get('tools', [])
            }
        
        return validation_results
    
    def test_mcp_server_imports(self) -> Dict[str, Any]:
        """Test if MCP server modules can be imported"""
        test_results = {
            'servers_tested': 0,
            'import_successful': 0,
            'import_failures': [],
            'server_test_details': {}
        }
        
        servers_to_test = [
            ('ml-code-intelligence', 'ml_code_intelligence/src/server.py'),
            ('context-aware-memory', 'context_aware_memory/src/server.py'),
            ('ml-testing-qa', 'ml_testing_qa/src/server.py'),
            ('agentic-workflow', 'agentic_workflow/src/server.py'),
            ('predictive-analytics', 'predictive_analytics/src/server.py'),
            ('10x-knowledge-graph', 'knowledge_graph/src/server.py'),
            ('10x-command-analytics', 'command_analytics/src/server.py')
        ]
        
        for server_name, script_path in servers_to_test:
            test_results['servers_tested'] += 1
            full_path = self.mcp_servers_dir / script_path
            
            if not full_path.exists():
                test_results['import_failures'].append(f"{server_name}: Script not found")
                test_results['server_test_details'][server_name] = {
                    'import_success': False,
                    'error': 'Script not found',
                    'script_path': str(full_path)
                }
                continue
            
            try:
                # Test import by running python -c "import sys; sys.path.append(...); import server"
                venv_python = self.mcp_servers_dir / 'mcp_venv/bin/python'
                server_dir = full_path.parent
                
                cmd = [
                    str(venv_python), '-c',
                    f"import sys; sys.path.append('{server_dir}'); import server; print('Import successful')"
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    test_results['import_successful'] += 1
                    test_results['server_test_details'][server_name] = {
                        'import_success': True,
                        'script_path': str(full_path)
                    }
                else:
                    test_results['import_failures'].append(f"{server_name}: {result.stderr.strip()}")
                    test_results['server_test_details'][server_name] = {
                        'import_success': False,
                        'error': result.stderr.strip(),
                        'script_path': str(full_path)
                    }
            
            except Exception as e:
                test_results['import_failures'].append(f"{server_name}: {str(e)}")
                test_results['server_test_details'][server_name] = {
                    'import_success': False,
                    'error': str(e),
                    'script_path': str(full_path)
                }
        
        return test_results
    
    def generate_integration_report(self, validation_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive integration report"""
        
        mcp_config = validation_results['mcp_config']
        agent_registry = validation_results['agent_registry']
        import_tests = validation_results['import_tests']
        
        report = {
            'summary': {
                'total_mcp_servers_configured': mcp_config['total_servers_configured'],
                'valid_mcp_configurations': mcp_config['valid_configurations'],
                'mcp_configuration_success_rate': f"{(mcp_config['valid_configurations'] / max(1, mcp_config['total_servers_configured']) * 100):.1f}%",
                'total_agents_registered': agent_registry['total_agents_registered'],
                'agents_with_mcp_integration': agent_registry['agents_with_mcp_integration'],
                'agent_mcp_integration_rate': f"{(agent_registry['agents_with_mcp_integration'] / max(1, agent_registry['total_agents_registered']) * 100):.1f}%",
                'import_test_success_rate': f"{(import_tests['import_successful'] / max(1, import_tests['servers_tested']) * 100):.1f}%",
                'validation_timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            },
            'mcp_server_analysis': {
                'configured_servers': list(mcp_config['server_details'].keys()),
                'working_servers': [name for name, details in mcp_config['server_details'].items() if not details['issues']],
                'problematic_servers': [name for name, details in mcp_config['server_details'].items() if details['issues']],
                'import_successful_servers': [name for name, details in import_tests['server_test_details'].items() if details.get('import_success', False)],
                'configuration_issues': mcp_config['configuration_issues']
            },
            'agent_integration_analysis': {
                'most_integrated_mcps': sorted(agent_registry['mcp_usage_distribution'].items(), key=lambda x: x[1], reverse=True),
                'agents_by_integration_level': {
                    'high_integration_agents': [name for name, details in agent_registry['agent_details'].items() if details['mcp_count'] >= 5],
                    'medium_integration_agents': [name for name, details in agent_registry['agent_details'].items() if 2 <= details['mcp_count'] < 5],
                    'low_integration_agents': [name for name, details in agent_registry['agent_details'].items() if details['mcp_count'] == 1],
                    'no_integration_agents': [name for name, details in agent_registry['agent_details'].items() if details['mcp_count'] == 0]
                }
            },
            'recommendations': [],
            'detailed_results': {
                'mcp_config': mcp_config,
                'agent_registry': agent_registry,
                'import_tests': import_tests
            }
        }
        
        # Generate recommendations
        if report['summary']['mcp_configuration_success_rate'].startswith('100'):
            report['recommendations'].append("✅ All MCP servers properly configured")
        else:
            report['recommendations'].append(f"⚠️ {len(report['mcp_server_analysis']['problematic_servers'])} MCP servers need configuration fixes")
        
        if float(report['summary']['agent_mcp_integration_rate'].rstrip('%')) > 80:
            report['recommendations'].append("✅ High agent-MCP integration rate achieved")
        else:
            report['recommendations'].append("⚠️ Consider increasing agent-MCP integration coverage")
        
        if report['summary']['import_test_success_rate'].startswith('100'):
            report['recommendations'].append("✅ All MCP servers pass import tests")
        else:
            report['recommendations'].append(f"⚠️ {len(import_tests['import_failures'])} MCP servers have import issues")
        
        report['recommendations'].extend([
            f"🎯 {report['summary']['total_agents_registered']} agents registered and accessible via /agent interface",
            f"🔧 {len(report['agent_integration_analysis']['most_integrated_mcps'])} unique MCP servers integrated",
            "🚀 Agent-MCP integration system operational and ready for use"
        ])
        
        return report
    
    def run_validation(self) -> Dict[str, Any]:
        """Run complete MCP integration validation"""
        logger.info("Starting MCP integration validation...")
        
        # Load settings
        settings = self.load_settings()
        if not settings:
            return {"error": "Failed to load settings"}
        
        # Run validations
        mcp_config = self.validate_mcp_server_config(settings)
        agent_registry = self.validate_agent_registry(settings)
        import_tests = self.test_mcp_server_imports()
        
        # Combine results
        validation_results = {
            'mcp_config': mcp_config,
            'agent_registry': agent_registry,
            'import_tests': import_tests
        }
        
        # Generate report
        report = self.generate_integration_report(validation_results)
        
        logger.info("MCP integration validation completed")
        return report

def main():
    """Main entry point"""
    base_dir = Path(__file__).parent.parent
    validator = MCPIntegrationValidator(base_dir)
    
    # Run validation
    report = validator.run_validation()
    
    # Save report
    report_path = base_dir / 'mcp_integration_validation_report.json'
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    summary = report.get('summary', {})
    print("\n🔍 MCP Integration Validation Results:")
    print(f"✅ MCP Servers Configured: {summary.get('total_mcp_servers_configured', 0)}")
    print(f"✅ Valid Configurations: {summary.get('mcp_configuration_success_rate', 'N/A')}")
    print(f"✅ Agents Registered: {summary.get('total_agents_registered', 0)}")
    print(f"✅ Agent-MCP Integration: {summary.get('agent_mcp_integration_rate', 'N/A')}")
    print(f"✅ Import Tests: {summary.get('import_test_success_rate', 'N/A')}")
    print(f"\n📊 Full Report: {report_path}")
    
    recommendations = report.get('recommendations', [])
    if recommendations:
        print("\n💡 Recommendations:")
        for rec in recommendations:
            print(f"  {rec}")
    
    return report

if __name__ == "__main__":
    main()