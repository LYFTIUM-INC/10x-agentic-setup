#!/usr/bin/env python3
"""
Test script for Performance Intelligence Engineer specialist agent
Verifies proper configuration and integration capabilities
"""

import os
import sys
import json
import sqlite3
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / ".claude" / "hooks" / "coordination"))

from subagent_coordinator import SubAgentCoordinator

def test_agent_registration():
    """Test that the agent is properly registered"""
    print("🧪 Testing Performance Intelligence Agent Registration...")
    
    coordinator = SubAgentCoordinator()
    
    # Check if agent exists
    agent_name = "10x-performance-intelligence-specialist"
    assert agent_name in coordinator.available_agents, f"Agent {agent_name} not found in available agents"
    
    agent = coordinator.available_agents[agent_name]
    
    # Verify agent properties
    assert agent.domain == "10x-performance-intelligence", "Incorrect domain"
    assert agent.performance_profile == "high-performance", "Incorrect performance profile"
    assert agent.security_level == "read-write", "Incorrect security level"
    
    # Verify MCP integrations
    expected_mcps = ["predictive-analytics", "ml-code-intelligence", "performance-monitoring", "resource-optimization"]
    assert set(agent.integration_mcps) == set(expected_mcps), "Incorrect MCP integrations"
    
    # Verify tools
    expected_tools = ["Edit", "MultiEdit", "Read", "Write", "Bash", "WebSearch", "WebFetch", "TodoWrite"]
    assert set(agent.tools) == set(expected_tools), "Incorrect tools configuration"
    
    print("✅ Agent registration test passed!")
    return True

def test_database_integration():
    """Test database integration for the agent"""
    print("\n🧪 Testing Database Integration...")
    
    db_path = project_root / ".claude" / "subagent_coordination.db"
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute("""
            SELECT name, domain, performance_profile, security_level, total_executions, avg_execution_time
            FROM subagent_registry 
            WHERE name = '10x-performance-intelligence-specialist'
        """)
        
        result = cursor.fetchone()
        assert result is not None, "Agent not found in database"
        
        name, domain, perf_profile, sec_level, total_exec, avg_time = result
        
        assert name == "10x-performance-intelligence-specialist"
        assert domain == "10x-performance-intelligence"
        assert perf_profile == "high-performance"
        assert sec_level == "read-write"
        
        print(f"  • Agent: {name}")
        print(f"  • Domain: {domain}")
        print(f"  • Performance Profile: {perf_profile}")
        print(f"  • Security Level: {sec_level}")
        print(f"  • Total Executions: {total_exec}")
        print(f"  • Average Execution Time: {avg_time}s")
    
    print("✅ Database integration test passed!")
    return True

def test_performance_capabilities():
    """Test agent's performance-specific capabilities"""
    print("\n🧪 Testing Performance Capabilities...")
    
    # Read the agent definition
    agent_file = project_root / ".claude" / "agents" / "10x-performance-intelligence-specialist.md"
    content = agent_file.read_text()
    
    # Verify key performance capabilities are documented
    capabilities = [
        "57+ performance metrics",
        "24 velocity predictions",
        "5-10x performance gains",
        "70% cache hit rate",
        "85% resource utilization",
        "0.020s coordination",
        "Bottleneck detection",
        "Predictive analytics"
    ]
    
    for capability in capabilities:
        assert capability.lower() in content.lower(), f"Missing capability: {capability}"
        print(f"  ✓ {capability}")
    
    print("✅ Performance capabilities test passed!")
    return True

def test_mcp_integration():
    """Test MCP server integration configuration"""
    print("\n🧪 Testing MCP Integration...")
    
    coordinator = SubAgentCoordinator()
    
    # Check MCP availability
    print(f"  • Agentic Workflow Available: {coordinator.agentic_workflow_available}")
    print(f"  • ML Intelligence Available: {coordinator.ml_intelligence_available}")
    print(f"  • Predictive Analytics Available: {coordinator.predictive_analytics_available}")
    
    # Verify at least some MCPs are available
    mcp_count = sum([
        coordinator.agentic_workflow_available,
        coordinator.ml_intelligence_available,
        coordinator.predictive_analytics_available
    ])
    
    assert mcp_count > 0, "No MCP servers available"
    
    print(f"✅ MCP integration test passed! ({mcp_count}/3 servers available)")
    return True

def test_coordination_simulation():
    """Simulate agent coordination"""
    print("\n🧪 Testing Coordination Simulation...")
    
    # Set up environment variables for simulation
    os.environ['CLAUDE_TOOL_NAME'] = 'TodoWrite'
    os.environ['CLAUDE_SUBAGENT_NAME'] = '10x-performance-intelligence-specialist'
    os.environ['CLAUDE_SUBAGENT_RESULT'] = json.dumps({
        "task": "performance_analysis",
        "metrics_analyzed": 57,
        "bottlenecks_found": 3,
        "optimization_potential": "5-10x",
        "cache_hit_rate": 0.72
    })
    
    # Run coordination
    coordinator = SubAgentCoordinator()
    
    event_data = {
        "tool_name": os.environ.get('CLAUDE_TOOL_NAME'),
        "subagent_result": os.environ.get('CLAUDE_SUBAGENT_RESULT'),
        "subagent_name": os.environ.get('CLAUDE_SUBAGENT_NAME')
    }
    
    # This should complete without errors
    coordinator.coordinate_subagent_execution(event_data)
    
    print("✅ Coordination simulation test passed!")
    return True

def main():
    """Run all tests"""
    print("🔬 Performance Intelligence Agent Test Suite")
    print("=" * 50)
    
    tests = [
        test_agent_registration,
        test_database_integration,
        test_performance_capabilities,
        test_mcp_integration,
        test_coordination_simulation
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed: {test.__name__}")
            print(f"   Error: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Performance Intelligence Agent is properly configured.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the configuration.")
        return 1

if __name__ == "__main__":
    sys.exit(main())