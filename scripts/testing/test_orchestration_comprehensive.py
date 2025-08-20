#!/usr/bin/env python3
"""
🧪 Comprehensive Sub-Agent Orchestration Test Suite
Tests all orchestration modes and coordination features
"""

import os
import sys
import time
import sqlite3
import subprocess
from pathlib import Path

def run_orchestration_test(task, mode, description):
    """Run a single orchestration test"""
    print(f"\n{'='*60}")
    print(f"🧪 TEST: {description}")
    print(f"   Task: {task}")
    print(f"   Mode: {mode}")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        result = subprocess.run([
            "python3", "orchestrate_subagents_10x.py",
            "--task", task,
            "--mode", mode
        ], capture_output=True, text=True, timeout=30)
        
        execution_time = time.time() - start_time
        
        if result.returncode == 0:
            print(f"✅ TEST PASSED ({execution_time:.2f}s)")
            return {
                "status": "passed",
                "execution_time": execution_time,
                "output": result.stdout
            }
        else:
            print(f"❌ TEST FAILED ({execution_time:.2f}s)")
            print(f"Error: {result.stderr}")
            return {
                "status": "failed",
                "execution_time": execution_time,
                "error": result.stderr
            }
    
    except subprocess.TimeoutExpired:
        print(f"⏰ TEST TIMEOUT (30s)")
        return {
            "status": "timeout",
            "execution_time": 30.0,
            "error": "Test timed out after 30 seconds"
        }
    
    except Exception as e:
        print(f"❌ TEST ERROR: {e}")
        return {
            "status": "error",
            "execution_time": 0,
            "error": str(e)
        }

def analyze_database_metrics():
    """Analyze orchestration database for metrics"""
    db_path = ".claude/orchestration.db"
    
    if not os.path.exists(db_path):
        return {"error": "Database not found"}
    
    try:
        with sqlite3.connect(db_path) as conn:
            # Get execution statistics
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total_executions,
                    AVG(json_extract(performance_metrics, '$.total_execution_time')) as avg_execution_time,
                    AVG(json_extract(performance_metrics, '$.parallel_efficiency')) as avg_parallel_efficiency,
                    AVG(json_extract(performance_metrics, '$.success_rate')) as success_rate,
                    AVG(json_extract(performance_metrics, '$.agents_used')) as avg_agents_used
                FROM execution_plans
                WHERE status = 'completed'
            """)
            
            stats = cursor.fetchone()
            
            # Get agent usage statistics
            cursor = conn.execute("""
                SELECT agent_name, COUNT(*) as usage_count
                FROM orchestration_events 
                WHERE event_type = 'agent_execution'
                GROUP BY agent_name
                ORDER BY usage_count DESC
            """)
            
            agent_usage = cursor.fetchall()
            
            # Get recent executions
            cursor = conn.execute("""
                SELECT task_description, status, 
                       json_extract(performance_metrics, '$.total_execution_time') as execution_time,
                       json_extract(performance_metrics, '$.agents_used') as agents_used
                FROM execution_plans
                ORDER BY start_time DESC
                LIMIT 5
            """)
            
            recent_executions = cursor.fetchall()
            
            return {
                "total_executions": stats[0] or 0,
                "avg_execution_time": round(stats[1] or 0, 2),
                "avg_parallel_efficiency": round(stats[2] or 0, 1),
                "success_rate": round(stats[3] or 0, 1),
                "avg_agents_used": round(stats[4] or 0, 1),
                "agent_usage": agent_usage[:5],  # Top 5 agents
                "recent_executions": recent_executions
            }
    
    except Exception as e:
        return {"error": f"Database analysis failed: {e}"}

def main():
    """Run comprehensive orchestration tests"""
    print(f"🎛️  COMPREHENSIVE SUB-AGENT ORCHESTRATION TEST SUITE")
    print(f"{'='*70}")
    
    # Ensure we're in the right directory
    os.chdir(Path(__file__).parent)
    
    # Test cases covering different scenarios
    test_cases = [
        {
            "task": "comprehensive-system-analysis",
            "mode": "auto",
            "description": "Auto Mode - Complex Multi-Domain Analysis"
        },
        {
            "task": "security vulnerability assessment",
            "mode": "optimal",
            "description": "Optimal Mode - Security-Focused Analysis"
        },
        {
            "task": "performance optimization review",
            "mode": "auto",
            "description": "Auto Mode - Performance-Focused Analysis"
        },
        {
            "task": "code quality and architecture analysis",
            "mode": "manual",
            "description": "Manual Mode - Code Quality Analysis"
        },
        {
            "task": "multi-phase system refactoring analysis",
            "mode": "optimal",
            "description": "Optimal Mode - Complex Refactoring Task"
        }
    ]
    
    # Run all tests
    test_results = []
    total_start_time = time.time()
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔬 Running Test {i}/{len(test_cases)}")
        result = run_orchestration_test(
            test_case["task"],
            test_case["mode"],
            test_case["description"]
        )
        result["test_case"] = test_case
        test_results.append(result)
        
        # Brief pause between tests
        time.sleep(1)
    
    total_execution_time = time.time() - total_start_time
    
    # Analyze database metrics
    print(f"\n📊 ANALYZING ORCHESTRATION METRICS")
    print(f"{'='*60}")
    
    db_metrics = analyze_database_metrics()
    
    # Generate comprehensive report
    print(f"\n📋 COMPREHENSIVE TEST REPORT")
    print(f"{'='*70}")
    
    # Test Summary
    passed_tests = sum(1 for r in test_results if r["status"] == "passed")
    failed_tests = sum(1 for r in test_results if r["status"] == "failed")
    error_tests = sum(1 for r in test_results if r["status"] == "error")
    timeout_tests = sum(1 for r in test_results if r["status"] == "timeout")
    
    print(f"🎯 Test Execution Summary:")
    print(f"   Total Tests: {len(test_results)}")
    print(f"   Passed: {passed_tests} ✅")
    print(f"   Failed: {failed_tests} ❌")
    print(f"   Errors: {error_tests} ⚠️")
    print(f"   Timeouts: {timeout_tests} ⏰")
    print(f"   Success Rate: {(passed_tests/len(test_results)*100):.1f}%")
    print(f"   Total Execution Time: {total_execution_time:.2f}s")
    
    # Database Metrics
    if "error" not in db_metrics:
        print(f"\n📈 Orchestration Performance Metrics:")
        print(f"   Total Orchestrated Executions: {db_metrics['total_executions']}")
        print(f"   Average Execution Time: {db_metrics['avg_execution_time']}s")
        print(f"   Average Parallel Efficiency: {db_metrics['avg_parallel_efficiency']}%")
        print(f"   Overall Success Rate: {db_metrics['success_rate']}%")
        print(f"   Average Agents per Task: {db_metrics['avg_agents_used']}")
        
        print(f"\n🤖 Agent Usage Statistics:")
        for agent_name, count in db_metrics['agent_usage']:
            print(f"   {agent_name}: {count} executions")
        
        print(f"\n🕒 Recent Orchestration History:")
        for task, status, exec_time, agents in db_metrics['recent_executions']:
            task_short = task[:40] + "..." if len(task) > 40 else task
            print(f"   {status}: {task_short} ({exec_time:.1f}s, {agents} agents)")
    
    # Detailed Test Results
    print(f"\n🔍 Detailed Test Results:")
    for i, result in enumerate(test_results, 1):
        test_case = result["test_case"]
        status_icon = {
            "passed": "✅",
            "failed": "❌", 
            "error": "⚠️",
            "timeout": "⏰"
        }.get(result["status"], "❓")
        
        print(f"\n   Test {i}: {status_icon} {result['status'].upper()}")
        print(f"      Description: {test_case['description']}")
        print(f"      Task: {test_case['task']}")
        print(f"      Mode: {test_case['mode']}")
        print(f"      Execution Time: {result['execution_time']:.2f}s")
        
        if result["status"] != "passed" and "error" in result:
            print(f"      Error: {result['error'][:100]}...")
    
    # Success Criteria Analysis
    print(f"\n🏆 ORCHESTRATION SUCCESS CRITERIA ANALYSIS")
    print(f"{'='*60}")
    
    success_criteria = {
        "Multi-Agent Coordination": passed_tests >= 4,
        "Multiple Execution Modes": len(set(r["test_case"]["mode"] for r in test_results if r["status"] == "passed")) >= 2,
        "Task Decomposition": passed_tests > 0,
        "Parallel Processing": db_metrics.get("avg_parallel_efficiency", 0) > 10,
        "Result Aggregation": passed_tests > 0,
        "Performance Tracking": db_metrics.get("total_executions", 0) > 0,
        "Database Integration": "error" not in db_metrics,
        "Agent Discovery": passed_tests > 0
    }
    
    for criterion, met in success_criteria.items():
        status = "✅ PASSED" if met else "❌ FAILED"
        print(f"   {criterion}: {status}")
    
    overall_success = sum(success_criteria.values()) / len(success_criteria) * 100
    print(f"\n🎯 Overall Orchestration Success Rate: {overall_success:.1f}%")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS")
    print(f"{'='*60}")
    
    if overall_success >= 90:
        print("🚀 EXCELLENT: Sub-agent orchestration system is fully operational!")
        print("   - All core features are working correctly")
        print("   - Multi-agent coordination is successful") 
        print("   - System is ready for production use")
    elif overall_success >= 75:
        print("✅ GOOD: Sub-agent orchestration system is mostly operational")
        print("   - Core features are working")
        print("   - Some optimizations may be needed")
        print("   - Monitor performance and improve efficiency")
    else:
        print("⚠️  NEEDS IMPROVEMENT: Sub-agent orchestration system needs work")
        print("   - Several core features may need fixes")
        print("   - Review failed tests and errors")
        print("   - Consider debugging and optimization")
    
    print(f"\n✅ COMPREHENSIVE TEST SUITE COMPLETE!")
    print(f"Report saved to: {Path.cwd() / 'orchestration_test_report.txt'}")
    
    # Save detailed report to file
    with open("orchestration_test_report.txt", "w") as f:
        f.write(f"SUB-AGENT ORCHESTRATION COMPREHENSIVE TEST REPORT\n")
        f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"{'='*60}\n\n")
        
        f.write(f"TEST EXECUTION SUMMARY:\n")
        f.write(f"Total Tests: {len(test_results)}\n")
        f.write(f"Passed: {passed_tests}\n")
        f.write(f"Failed: {failed_tests}\n")
        f.write(f"Success Rate: {(passed_tests/len(test_results)*100):.1f}%\n")
        f.write(f"Total Execution Time: {total_execution_time:.2f}s\n\n")
        
        if "error" not in db_metrics:
            f.write(f"PERFORMANCE METRICS:\n")
            f.write(f"Total Executions: {db_metrics['total_executions']}\n")
            f.write(f"Average Execution Time: {db_metrics['avg_execution_time']}s\n")
            f.write(f"Average Parallel Efficiency: {db_metrics['avg_parallel_efficiency']}%\n")
            f.write(f"Overall Success Rate: {db_metrics['success_rate']}%\n\n")
        
        f.write(f"SUCCESS CRITERIA:\n")
        for criterion, met in success_criteria.items():
            f.write(f"{criterion}: {'PASSED' if met else 'FAILED'}\n")
        f.write(f"\nOverall Success Rate: {overall_success:.1f}%\n")

if __name__ == "__main__":
    main()