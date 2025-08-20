#!/usr/bin/env python3
"""
Test script for Technical Pattern Discovery Agent
Verifies agent creation and technical pattern research capabilities
"""

import json
import yaml
from pathlib import Path
from datetime import datetime

class TechnicalPatternDiscoveryAgentTest:
    """Test suite for the Technical Pattern Discovery Agent"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.agent_path = self.project_root / ".claude" / "agents" / "10x-technical-pattern-discovery.md"
        self.test_results = []
        
    def run_all_tests(self):
        """Run all test scenarios"""
        print("🧪 Testing Technical Pattern Discovery Agent")
        print("=" * 60)
        
        # Test 1: Verify agent file exists
        self.test_agent_file_exists()
        
        # Test 2: Validate agent metadata
        self.test_agent_metadata()
        
        # Test 3: Verify capabilities
        self.test_agent_capabilities()
        
        # Test 4: Check MCP integration
        self.test_mcp_integration()
        
        # Test 5: Validate knowledge integration
        self.test_knowledge_integration()
        
        # Print test summary
        self.print_test_summary()
        
    def test_agent_file_exists(self):
        """Test that agent file was created"""
        test_name = "Agent File Exists"
        if self.agent_path.exists():
            self.test_results.append((test_name, "✅ PASS", "Agent file created successfully"))
        else:
            self.test_results.append((test_name, "❌ FAIL", f"Agent file not found at {self.agent_path}"))
            
    def test_agent_metadata(self):
        """Test agent metadata structure"""
        test_name = "Agent Metadata Validation"
        
        if not self.agent_path.exists():
            self.test_results.append((test_name, "⚠️ SKIP", "Agent file not found"))
            return
            
        try:
            content = self.agent_path.read_text()
            
            # Check for required metadata fields
            required_fields = [
                "Type: researcher",
                "Domain: 10x-technical-pattern-discovery",
                "Created: 2025-07-28"
            ]
            
            missing_fields = []
            for field in required_fields:
                if field not in content:
                    missing_fields.append(field)
                    
            if not missing_fields:
                self.test_results.append((test_name, "✅ PASS", "All metadata fields present"))
            else:
                self.test_results.append((test_name, "❌ FAIL", f"Missing fields: {missing_fields}"))
                
        except Exception as e:
            self.test_results.append((test_name, "❌ FAIL", f"Error reading agent file: {e}"))
            
    def test_agent_capabilities(self):
        """Test agent capabilities definition"""
        test_name = "Agent Capabilities"
        
        if not self.agent_path.exists():
            self.test_results.append((test_name, "⚠️ SKIP", "Agent file not found"))
            return
            
        try:
            content = self.agent_path.read_text()
            
            # Check for key capabilities
            required_capabilities = [
                "pattern_discovery",
                "technical_analysis",
                "optimization_intelligence",
                "knowledge_integration"
            ]
            
            capabilities_section = content.split("## Capabilities")[1].split("##")[0] if "## Capabilities" in content else ""
            
            missing_capabilities = []
            for capability in required_capabilities:
                if capability not in capabilities_section:
                    missing_capabilities.append(capability)
                    
            if not missing_capabilities:
                self.test_results.append((test_name, "✅ PASS", "All core capabilities defined"))
            else:
                self.test_results.append((test_name, "❌ FAIL", f"Missing capabilities: {missing_capabilities}"))
                
        except Exception as e:
            self.test_results.append((test_name, "❌ FAIL", f"Error parsing capabilities: {e}"))
            
    def test_mcp_integration(self):
        """Test MCP server integration configuration"""
        test_name = "MCP Integration"
        
        if not self.agent_path.exists():
            self.test_results.append((test_name, "⚠️ SKIP", "Agent file not found"))
            return
            
        try:
            content = self.agent_path.read_text()
            
            # Check for MCP servers
            required_mcps = [
                "ml-code-intelligence",
                "agentic-workflow",
                "10x-knowledge-graph"
            ]
            
            integration_section = content.split("**MCP Servers**:")[1].split("\n")[0] if "**MCP Servers**:" in content else ""
            
            missing_mcps = []
            for mcp in required_mcps:
                if mcp not in integration_section:
                    missing_mcps.append(mcp)
                    
            if not missing_mcps:
                self.test_results.append((test_name, "✅ PASS", "All required MCPs integrated"))
            else:
                self.test_results.append((test_name, "❌ FAIL", f"Missing MCPs: {missing_mcps}"))
                
        except Exception as e:
            self.test_results.append((test_name, "❌ FAIL", f"Error checking MCP integration: {e}"))
            
    def test_knowledge_integration(self):
        """Test knowledge asset integration"""
        test_name = "Knowledge Integration"
        
        if not self.agent_path.exists():
            self.test_results.append((test_name, "⚠️ SKIP", "Agent file not found"))
            return
            
        try:
            content = self.agent_path.read_text()
            
            # Check for knowledge assets
            required_assets = [
                "technical_patterns",
                "performance_data",
                "architecture_assets",
                "knowledge_graph"
            ]
            
            knowledge_section = content.split("## Knowledge Integration")[1].split("##")[0] if "## Knowledge Integration" in content else ""
            
            missing_assets = []
            for asset in required_assets:
                if asset not in knowledge_section:
                    missing_assets.append(asset)
                    
            if not missing_assets:
                self.test_results.append((test_name, "✅ PASS", "All knowledge assets integrated"))
            else:
                self.test_results.append((test_name, "❌ FAIL", f"Missing assets: {missing_assets}"))
                
        except Exception as e:
            self.test_results.append((test_name, "❌ FAIL", f"Error checking knowledge integration: {e}"))
            
    def print_test_summary(self):
        """Print test execution summary"""
        print("\n📊 Test Results Summary")
        print("=" * 60)
        
        for test_name, status, message in self.test_results:
            print(f"{status} {test_name}: {message}")
            
        # Calculate pass rate
        passed = sum(1 for _, status, _ in self.test_results if "PASS" in status)
        total = len(self.test_results)
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        print("\n" + "=" * 60)
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Pass Rate: {pass_rate:.1f}%")
        
        # Generate detailed report
        self.generate_detailed_report()
        
    def generate_detailed_report(self):
        """Generate detailed test report"""
        report_path = self.project_root / "tests" / "technical_pattern_discovery_agent_report.md"
        
        report_content = f"""# Technical Pattern Discovery Agent Test Report

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Agent Path**: `{self.agent_path}`

## Test Results

| Test | Status | Details |
|------|--------|---------|
"""
        
        for test_name, status, message in self.test_results:
            report_content += f"| {test_name} | {status} | {message} |\n"
            
        report_content += f"""

## Agent Overview

The Technical Pattern Discovery Agent is a specialized researcher focusing on:

1. **Technical Pattern Discovery**
   - ML-powered code intelligence
   - Semantic pattern analysis
   - Architecture evaluation
   - Integration optimization

2. **Key Capabilities**
   - Pattern discovery using ML code intelligence
   - Technical analysis with quality assessment
   - Optimization intelligence for 5-10x gains
   - Knowledge integration with graph correlation

3. **MCP Integration**
   - ml-code-intelligence
   - agentic-workflow
   - 10x-knowledge-graph
   - predictive-analytics
   - context-aware-memory

4. **Performance Profile**
   - Pattern Discovery Rate: > 10 patterns per analysis
   - Optimization Identification: 5-10x improvement opportunities
   - Integration Success: 95% pattern compatibility
   - Analysis Speed: < 0.020s pattern correlation

## Usage Example

```bash
# Use the agent for technical pattern discovery
/subagents/orchestrate_subagents_10x \\
  --task "Analyze codebase for performance optimization patterns" \\
  --agents "10x-technical-pattern-discovery" \\
  --mode optimal
```

## Integration Points

- **Knowledge Assets**: Access to ML MCP integration blueprints, performance patterns
- **Tools**: ml_code_analysis, pattern_discovery, knowledge_graph, semantic_search
- **Performance**: Optimized for parallel pattern analysis
- **Security**: Enhanced level for code analysis operations
"""
        
        report_path.write_text(report_content)
        print(f"\n📄 Detailed report saved to: {report_path}")


if __name__ == "__main__":
    # Run the tests
    tester = TechnicalPatternDiscoveryAgentTest()
    tester.run_all_tests()