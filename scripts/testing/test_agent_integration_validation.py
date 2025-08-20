#!/usr/bin/env python3
"""
Agent Integration Validation Test
Tests all newly created agents for proper integration with SubagentStop hooks and MCP coordination
"""

import os
import sys
import json
import sqlite3
import subprocess
import time
from pathlib import Path

def main():
    """Run comprehensive agent integration validation"""
    print("🧪 Starting Agent Integration Validation Test")
    
    project_root = Path.cwd()
    coordinator_path = project_root / ".claude/hooks/coordination/subagent_coordinator.py"
    db_path = project_root / ".claude/subagent_coordination.db"
    
    # Test data for different agents
    test_agents = [
        {
            "name": "performance-engineer",
            "tool_name": "performance_analysis",
            "result": {
                "status": "success",
                "analysis_type": "bottleneck_detection",
                "execution_time": 4.5,
                "bottlenecks_found": 3,
                "optimization_recommendations": 5
            }
        },
        {
            "name": "security-auditor", 
            "tool_name": "security_scan",
            "result": {
                "status": "success",
                "vulnerabilities_found": 2,
                "security_score": 87,
                "critical_issues": 0,
                "recommendations": ["Update dependencies", "Implement input validation"]
            }
        },
        {
            "name": "project-architect",
            "tool_name": "architecture_analysis", 
            "result": {
                "status": "success",
                "design_patterns_analyzed": 15,
                "architecture_score": 92,
                "improvement_suggestions": 4
            }
        },
        {
            "name": "10x-enterprise-coordination-director",
            "tool_name": "enterprise_coordination",
            "result": {
                "status": "success",
                "agents_coordinated": 8,
                "workflow_efficiency": 95,
                "resource_optimization": 78
            }
        }
    ]
    
    print(f"📊 Testing {len(test_agents)} agents for integration...")
    
    # Test each agent
    results = []
    for i, agent in enumerate(test_agents, 1):
        print(f"\n🤖 Testing Agent {i}/{len(test_agents)}: {agent['name']}")
        
        try:
            # Set environment variables
            env = os.environ.copy()
            env['CLAUDE_TOOL_NAME'] = agent['tool_name']
            env['CLAUDE_SUBAGENT_NAME'] = agent['name']
            env['CLAUDE_SUBAGENT_RESULT'] = json.dumps(agent['result'])
            
            # Run coordinator
            result = subprocess.run(
                [sys.executable, str(coordinator_path)],
                env=env,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            success = result.returncode == 0
            results.append({
                "agent": agent['name'],
                "success": success,
                "output": result.stdout if success else result.stderr
            })
            
            if success:
                print(f"   ✅ Integration successful")
            else:
                print(f"   ❌ Integration failed: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print(f"   ⏰ Timeout - taking too long")
            results.append({
                "agent": agent['name'],
                "success": False,
                "output": "Timeout"
            })
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results.append({
                "agent": agent['name'],
                "success": False,
                "output": str(e)
            })
    
    # Check database state
    print(f"\n📊 Checking Database Integration...")
    
    if db_path.exists():
        with sqlite3.connect(db_path) as conn:
            # Check agent registry
            registry_count = conn.execute("SELECT COUNT(*) FROM subagent_registry").fetchone()[0]
            print(f"   📋 Registered Agents: {registry_count}")
            
            # Check coordination events
            events_count = conn.execute("SELECT COUNT(*) FROM coordination_events").fetchone()[0]
            print(f"   📝 Coordination Events: {events_count}")
            
            # Check recent executions
            recent_executions = conn.execute("""
                SELECT agent_name, COUNT(*) as execution_count 
                FROM coordination_events 
                WHERE event_type = 'subagent_coordination' 
                AND timestamp > ? 
                GROUP BY agent_name
            """, (time.time() - 300,)).fetchall()  # Last 5 minutes
            
            print(f"   ⚡ Recent Executions: {len(recent_executions)}")
            for agent_name, count in recent_executions:
                print(f"      • {agent_name}: {count} executions")
    else:
        print(f"   ❌ Database not found at {db_path}")
    
    # Check MCP server availability
    print(f"\n🔗 Checking MCP Server Integration...")
    
    mcp_servers = ["agentic_workflow", "ml_code_intelligence", "predictive_analytics"]
    mcp_available = []
    
    for server in mcp_servers:
        server_path = project_root / "mcp_servers" / server
        if server_path.exists():
            mcp_available.append(server)
            print(f"   ✅ {server}: Available")
        else:
            print(f"   ❌ {server}: Not found")
    
    print(f"   📊 MCP Integration: {len(mcp_available)}/{len(mcp_servers)} servers available")
    
    # Performance tracking check
    print(f"\n📈 Checking Performance Tracking...")
    
    perf_db = project_root / "databases" / "performance" / "metrics.db"
    if perf_db.exists():
        print(f"   ✅ Performance database exists")
        try:
            with sqlite3.connect(perf_db) as conn:
                tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
                print(f"   📊 Performance tables: {len(tables)}")
        except Exception as e:
            print(f"   ⚠️  Performance database error: {e}")
    else:
        print(f"   ❌ Performance database not found")
    
    # Dashboard integration check
    print(f"\n📊 Checking Dashboard Integration...")
    
    dashboard_path = project_root / "dashboard.html"
    if dashboard_path.exists():
        print(f"   ✅ Dashboard HTML exists")
        dashboard_size = dashboard_path.stat().st_size
        print(f"   📏 Dashboard size: {dashboard_size:,} bytes")
    else:
        print(f"   ❌ Dashboard not found")
    
    # Generate summary
    print(f"\n🎯 Integration Validation Summary")
    print(f"=" * 50)
    
    successful_agents = sum(1 for r in results if r['success'])
    print(f"Agents Tested: {len(results)}")
    print(f"Successful Integrations: {successful_agents}")
    print(f"Success Rate: {(successful_agents/len(results)*100):.1f}%")
    
    if successful_agents == len(results):
        print(f"🎉 All agents successfully integrated!")
    else:
        print(f"⚠️  Some agents need attention:")
        for result in results:
            if not result['success']:
                print(f"   • {result['agent']}: {result['output']}")
    
    # System health check
    print(f"\n🔍 System Health Check")
    print(f"📋 Agent Registry: {'✅' if registry_count > 0 else '❌'}")
    print(f"📝 Event Logging: {'✅' if events_count > 0 else '❌'}")
    print(f"🔗 MCP Integration: {'✅' if len(mcp_available) >= 2 else '❌'}")
    print(f"📈 Performance Tracking: {'✅' if perf_db.exists() else '❌'}")
    print(f"📊 Dashboard: {'✅' if dashboard_path.exists() else '❌'}")
    
    overall_health = (
        (registry_count > 0) + 
        (events_count > 0) + 
        (len(mcp_available) >= 2) + 
        perf_db.exists() + 
        dashboard_path.exists()
    )
    
    print(f"\n🎯 Overall System Health: {overall_health}/5 components operational")
    
    if overall_health >= 4:
        print("🎉 System is healthy and ready for production!")
    elif overall_health >= 3:
        print("⚠️  System is mostly operational with minor issues")
    else:
        print("❌ System needs attention - multiple components not working")
    
    return successful_agents == len(results) and overall_health >= 4

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)