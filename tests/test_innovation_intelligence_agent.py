#!/usr/bin/env python3
"""
Test script for Innovation Intelligence Analyst specialist agent
Verifies proper configuration and integration with project infrastructure
"""

import os
import sys
import json
import yaml
from pathlib import Path
from datetime import datetime

# Add project paths
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class InnovationIntelligenceAgentTester:
    def __init__(self):
        self.project_root = project_root
        self.agent_path = self.project_root / ".claude" / "agents" / "10x-innovation-intelligence-analyst.md"
        self.knowledge_path = self.project_root / "Knowledge" / "intelligence"
        self.test_results = []
        
    def run_all_tests(self):
        """Run comprehensive tests for the Innovation Intelligence Analyst agent"""
        print("🧪 Testing Innovation Intelligence Analyst Agent Configuration...\n")
        
        # Test 1: Agent file exists and is properly formatted
        self.test_agent_configuration()
        
        # Test 2: Verify MCP integrations
        self.test_mcp_integrations()
        
        # Test 3: Check knowledge asset availability
        self.test_knowledge_assets()
        
        # Test 4: Verify performance profile
        self.test_performance_profile()
        
        # Test 5: Validate security configuration
        self.test_security_configuration()
        
        # Test 6: Check hook integrations
        self.test_hook_integrations()
        
        # Print test results
        self.print_test_results()
        
    def test_agent_configuration(self):
        """Test agent file exists and has proper configuration"""
        print("📋 Test 1: Agent Configuration")
        
        if not self.agent_path.exists():
            self.test_results.append({
                "test": "Agent Configuration",
                "status": "FAIL",
                "reason": "Agent file not found"
            })
            return
            
        try:
            with open(self.agent_path, 'r') as f:
                content = f.read()
                
            # Check for required sections
            required_sections = [
                "name: 10x-innovation-intelligence-analyst",
                "Market and competitive intelligence specialist",
                "integration_mcps:",
                "70%-cache-hit-rate",
                "knowledge_assets:"
            ]
            
            missing_sections = []
            for section in required_sections:
                if section not in content:
                    missing_sections.append(section)
                    
            if missing_sections:
                self.test_results.append({
                    "test": "Agent Configuration",
                    "status": "FAIL",
                    "reason": f"Missing sections: {missing_sections}"
                })
            else:
                self.test_results.append({
                    "test": "Agent Configuration",
                    "status": "PASS",
                    "details": "All required sections present"
                })
                
        except Exception as e:
            self.test_results.append({
                "test": "Agent Configuration",
                "status": "ERROR",
                "reason": str(e)
            })
            
    def test_mcp_integrations(self):
        """Test MCP server integrations are properly configured"""
        print("🔗 Test 2: MCP Integrations")
        
        expected_mcps = [
            "chroma-rag",
            "websearch",
            "competitive-intelligence",
            "pattern-analysis",
            "context-aware-memory",
            "10x-knowledge-graph"
        ]
        
        try:
            with open(self.agent_path, 'r') as f:
                content = f.read()
                
            # Extract MCP integration list
            if "integration_mcps:" in content:
                mcp_line = [line for line in content.split('\n') if "integration_mcps:" in line][0]
                configured_mcps = eval(mcp_line.split(":", 1)[1].strip())
                
                missing_mcps = set(expected_mcps) - set(configured_mcps)
                extra_mcps = set(configured_mcps) - set(expected_mcps)
                
                if missing_mcps:
                    self.test_results.append({
                        "test": "MCP Integrations",
                        "status": "FAIL",
                        "reason": f"Missing MCPs: {missing_mcps}"
                    })
                else:
                    self.test_results.append({
                        "test": "MCP Integrations",
                        "status": "PASS",
                        "details": f"All {len(expected_mcps)} MCPs configured correctly"
                    })
            else:
                self.test_results.append({
                    "test": "MCP Integrations",
                    "status": "FAIL",
                    "reason": "MCP integration section not found"
                })
                
        except Exception as e:
            self.test_results.append({
                "test": "MCP Integrations",
                "status": "ERROR",
                "reason": str(e)
            })
            
    def test_knowledge_assets(self):
        """Test availability of knowledge assets"""
        print("📚 Test 3: Knowledge Assets")
        
        # Check for competitive analysis reports
        competitive_reports = list(self.knowledge_path.glob("*competitive*"))
        market_reports = list(self.knowledge_path.glob("*market*"))
        
        available_assets = {
            "competitive_analysis": len(competitive_reports),
            "market_analysis": len(market_reports),
            "total_intelligence_docs": len(list(self.knowledge_path.glob("*.md")))
        }
        
        if competitive_reports or market_reports:
            self.test_results.append({
                "test": "Knowledge Assets",
                "status": "PASS",
                "details": f"Found {available_assets['competitive_analysis']} competitive reports, "
                          f"{available_assets['market_analysis']} market reports, "
                          f"{available_assets['total_intelligence_docs']} total intelligence documents"
            })
        else:
            self.test_results.append({
                "test": "Knowledge Assets",
                "status": "WARN",
                "reason": "Limited knowledge assets available",
                "details": available_assets
            })
            
    def test_performance_profile(self):
        """Test performance profile configuration"""
        print("⚡ Test 4: Performance Profile")
        
        expected_profile = "70%-cache-hit-rate, 5-10x-research-efficiency, parallel-intelligence-gathering"
        
        try:
            with open(self.agent_path, 'r') as f:
                content = f.read()
                
            if f'performance_profile: "{expected_profile}"' in content:
                self.test_results.append({
                    "test": "Performance Profile",
                    "status": "PASS",
                    "details": "Correct performance profile configured"
                })
            else:
                self.test_results.append({
                    "test": "Performance Profile",
                    "status": "FAIL",
                    "reason": "Performance profile mismatch"
                })
                
        except Exception as e:
            self.test_results.append({
                "test": "Performance Profile",
                "status": "ERROR",
                "reason": str(e)
            })
            
    def test_security_configuration(self):
        """Test security level configuration"""
        print("🛡️ Test 5: Security Configuration")
        
        try:
            with open(self.agent_path, 'r') as f:
                content = f.read()
                
            if 'security_level: "read-write-validated"' in content:
                self.test_results.append({
                    "test": "Security Configuration",
                    "status": "PASS",
                    "details": "Proper security level configured"
                })
            else:
                self.test_results.append({
                    "test": "Security Configuration",
                    "status": "FAIL",
                    "reason": "Security level not properly configured"
                })
                
        except Exception as e:
            self.test_results.append({
                "test": "Security Configuration",
                "status": "ERROR",
                "reason": str(e)
            })
            
    def test_hook_integrations(self):
        """Test hook system integrations"""
        print("🔌 Test 6: Hook Integrations")
        
        expected_hooks = ["PreToolUse", "PostToolUse", "SubagentStop"]
        
        try:
            with open(self.agent_path, 'r') as f:
                content = f.read()
                
            if "hook_integration:" in content:
                hook_line = [line for line in content.split('\n') if "hook_integration:" in line][0]
                configured_hooks = eval(hook_line.split(":", 1)[1].strip())
                
                if set(configured_hooks) == set(expected_hooks):
                    self.test_results.append({
                        "test": "Hook Integrations",
                        "status": "PASS",
                        "details": "All required hooks configured"
                    })
                else:
                    self.test_results.append({
                        "test": "Hook Integrations",
                        "status": "FAIL",
                        "reason": f"Hook mismatch. Expected: {expected_hooks}, Got: {configured_hooks}"
                    })
            else:
                self.test_results.append({
                    "test": "Hook Integrations",
                    "status": "FAIL",
                    "reason": "Hook integration section not found"
                })
                
        except Exception as e:
            self.test_results.append({
                "test": "Hook Integrations",
                "status": "ERROR",
                "reason": str(e)
            })
            
    def print_test_results(self):
        """Print formatted test results"""
        print("\n" + "="*60)
        print("📊 TEST RESULTS SUMMARY")
        print("="*60)
        
        passed = sum(1 for r in self.test_results if r["status"] == "PASS")
        failed = sum(1 for r in self.test_results if r["status"] == "FAIL")
        warnings = sum(1 for r in self.test_results if r["status"] == "WARN")
        errors = sum(1 for r in self.test_results if r["status"] == "ERROR")
        
        for result in self.test_results:
            status_icon = {
                "PASS": "✅",
                "FAIL": "❌",
                "WARN": "⚠️",
                "ERROR": "🔥"
            }.get(result["status"], "❓")
            
            print(f"\n{status_icon} {result['test']}: {result['status']}")
            if "reason" in result:
                print(f"   Reason: {result['reason']}")
            if "details" in result:
                print(f"   Details: {result['details']}")
                
        print("\n" + "="*60)
        print(f"Total Tests: {len(self.test_results)}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️ Warnings: {warnings}")
        print(f"🔥 Errors: {errors}")
        print("="*60)
        
        # Overall status
        if failed == 0 and errors == 0:
            print("\n🎉 All tests passed! Innovation Intelligence Analyst is properly configured.")
        else:
            print("\n⚠️ Some tests failed. Please review the configuration.")
            
        # Save results to JSON
        results_file = self.project_root / "tests" / "innovation_intelligence_agent_test_results.json"
        with open(results_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "agent": "10x-innovation-intelligence-analyst",
                "results": self.test_results,
                "summary": {
                    "total": len(self.test_results),
                    "passed": passed,
                    "failed": failed,
                    "warnings": warnings,
                    "errors": errors
                }
            }, f, indent=2)
            
        print(f"\n📄 Test results saved to: {results_file}")

if __name__ == "__main__":
    tester = InnovationIntelligenceAgentTester()
    tester.run_all_tests()