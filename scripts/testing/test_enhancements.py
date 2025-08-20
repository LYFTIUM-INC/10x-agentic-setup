#!/usr/bin/env python3
"""
Test all enhancements and generate comprehensive report.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
import psutil
import sqlite3

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_mcp_servers():
    """Test MCP server availability."""
    print("\n1. MCP SERVER VERIFICATION")
    print("-" * 50)
    
    result = subprocess.run(
        ["python3", ".claude/scripts/verify_mcp_servers.py", "--json"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        try:
            data = json.loads(result.stdout)
            summary = data.get("summary", {})
            print(f"✓ Total Servers: {summary.get('total', 0)}")
            print(f"✓ Available: {summary.get('available', 0)}")
            print(f"✓ Missing: {summary.get('missing', 0)}")
            
            # Check each server
            for server, info in data.get("servers", {}).items():
                status = "✅" if info["status"] == "available" else "❌"
                print(f"  {status} {server}: {info['status']}")
            
            return summary.get('available', 0) == summary.get('total', 0)
        except:
            print("✗ Failed to parse MCP verification results")
            return False
    else:
        print("✗ MCP verification script failed")
        return False

def test_agents():
    """Test agent availability."""
    print("\n2. AGENT VERIFICATION")
    print("-" * 50)
    
    agents_dir = Path(".claude/agents")
    if not agents_dir.exists():
        print("✗ Agents directory not found")
        return False
        
    agent_files = list(agents_dir.glob("*.md"))
    print(f"✓ Total agents found: {len(agent_files)}")
    
    # Check key agents
    key_agents = [
        "project-architect.md",
        "performance-engineer.md", 
        "security-auditor.md",
        "agent-orchestrator.md",
        "mcp-orchestration-master.md"
    ]
    
    all_found = True
    for agent in key_agents:
        if (agents_dir / agent).exists():
            print(f"  ✅ {agent}")
        else:
            print(f"  ❌ {agent}")
            all_found = False
            
    return all_found and len(agent_files) >= 18

def test_hooks():
    """Test hook system."""
    print("\n3. HOOK SYSTEM VERIFICATION")
    print("-" * 50)
    
    hooks_dir = Path(".claude/hooks")
    if not hooks_dir.exists():
        print("✗ Hooks directory not found")
        return False
        
    hook_files = list(hooks_dir.glob("**/*.py"))
    print(f"✓ Total hook files: {len(hook_files)}")
    
    # Count by category
    categories = ["security", "performance", "coordination", "qa", "implementation"]
    for category in categories:
        count = len([f for f in hook_files if category in str(f)])
        print(f"  • {category}: {count} files")
        
    return len(hook_files) >= 50

def test_performance_db():
    """Test performance database."""
    print("\n4. PERFORMANCE DATABASE")
    print("-" * 50)
    
    db_path = Path(".claude/hooks/performance/performance_metrics.db")
    if not db_path.exists():
        print("✗ Performance database not found")
        return False
        
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get metrics count
        cursor.execute("SELECT COUNT(*) FROM performance_metrics")
        count = cursor.fetchone()[0]
        print(f"✓ Performance metrics collected: {count}")
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [t[0] for t in cursor.fetchall()]
        print(f"✓ Database tables: {len(tables)}")
        for table in tables[:5]:  # Show first 5
            print(f"  • {table}")
            
        conn.close()
        return count > 0
    except Exception as e:
        print(f"✗ Database error: {e}")
        return False

def test_parallel_optimizer():
    """Test parallel execution optimizer."""
    print("\n5. PARALLEL EXECUTION OPTIMIZER")
    print("-" * 50)
    
    try:
        # Import and test
        sys.path.insert(0, ".claude/hooks/performance")
        from parallel_execution_optimizer import get_optimizer
        
        optimizer = get_optimizer()
        print(f"✓ Optimizer initialized")
        print(f"✓ Optimal workers: {optimizer.optimal_workers}")
        print(f"✓ CPU count: {optimizer.cpu_count}")
        
        # Get performance stats
        stats = optimizer.get_performance_stats()
        if stats:
            print(f"✓ Average parallel efficiency: {stats.get('avg_parallel_efficiency', 0):.1f}x")
            print(f"✓ Success rate: {stats.get('success_rate', 0):.1f}%")
        
        return True
    except Exception as e:
        print(f"✗ Failed to test parallel optimizer: {e}")
        return False

def test_memory_optimizer():
    """Test memory optimizer."""
    print("\n6. MEMORY OPTIMIZER")
    print("-" * 50)
    
    try:
        from memory_optimizer import get_memory_optimizer
        
        optimizer = get_memory_optimizer()
        stats = optimizer.get_memory_stats()
        
        print(f"✓ Memory optimizer initialized")
        print(f"✓ System memory: {stats['system']['used_gb']:.1f}/{stats['system']['total_gb']:.1f} GB")
        print(f"✓ Memory usage: {stats['system']['percent']:.1f}%")
        print(f"✓ Process memory: {stats['process']['rss_gb']:.2f} GB")
        
        return True
    except Exception as e:
        print(f"✗ Failed to test memory optimizer: {e}")
        return False

def test_system_health():
    """Test system health."""
    print("\n7. SYSTEM HEALTH CHECK")
    print("-" * 50)
    
    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    print(f"✓ CPU Usage: {cpu}%")
    print(f"✓ Memory Usage: {memory.percent}% ({memory.used / (1024**3):.1f} GB)")
    print(f"✓ Disk Usage: {disk.percent}%")
    
    health_ok = cpu < 80 and memory.percent < 85 and disk.percent < 90
    
    if health_ok:
        print("✓ System health: GOOD")
    else:
        print("⚠️  System health: WARNING (high resource usage)")
        
    return health_ok

def main():
    """Run all tests."""
    print("="*60)
    print("10X AGENTIC SETUP - ENHANCEMENT VALIDATION")
    print("="*60)
    print(f"Timestamp: {datetime.now()}")
    
    results = {
        "mcp_servers": test_mcp_servers(),
        "agents": test_agents(),
        "hooks": test_hooks(),
        "performance_db": test_performance_db(),
        "parallel_optimizer": test_parallel_optimizer(),
        "memory_optimizer": test_memory_optimizer(),
        "system_health": test_system_health()
    }
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test}: {status}")
        
    print(f"\nTotal: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    
    # Overall status
    if passed == total:
        print("\n✅ ALL ENHANCEMENTS VALIDATED SUCCESSFULLY")
        return 0
    elif passed >= total * 0.7:
        print("\n⚠️  MOST ENHANCEMENTS WORKING (some issues)")
        return 1
    else:
        print("\n❌ ENHANCEMENTS NEED ATTENTION")
        return 2

if __name__ == "__main__":
    sys.exit(main())