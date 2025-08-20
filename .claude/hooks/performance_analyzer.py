#!/usr/bin/env python3
"""
Claude Sub-Agent: Performance Analysis & Verification
Triggered on Stop to analyze task completion and actually test results
"""

import sys
import json
import os
import subprocess
import hashlib
from datetime import datetime, timezone
from pathlib import Path

def run_verification_tests(execution_log, goal_analysis):
    """Actually test if the implementation works"""
    
    verification_results = {
        "code_compiles": False,
        "tests_pass": False,
        "functionality_works": False,
        "no_syntax_errors": True,
        "performance_acceptable": True,
        "verification_details": []
    }
    
    try:
        # Check if code was created
        if execution_log.get("code_created", False):
            modified_files = execution_log.get("files_modified", [])
            
            for file_path in modified_files:
                if not os.path.exists(file_path):
                    continue
                
                file_ext = Path(file_path).suffix.lower()
                
                # JavaScript/TypeScript verification
                if file_ext in ['.js', '.ts', '.jsx', '.tsx']:
                    try:
                        # Try to parse with Node.js
                        result = subprocess.run(
                            ['node', '-c', file_path], 
                            capture_output=True, 
                            text=True, 
                            timeout=10
                        )
                        if result.returncode == 0:
                            verification_results["code_compiles"] = True
                            verification_results["verification_details"].append(f"✅ {file_path} syntax valid")
                        else:
                            verification_results["no_syntax_errors"] = False
                            verification_results["verification_details"].append(f"❌ {file_path} syntax error: {result.stderr[:100]}")
                    except Exception as e:
                        verification_results["verification_details"].append(f"⚠️ Could not verify {file_path}: {str(e)}")
                
                # Python verification
                elif file_ext == '.py':
                    try:
                        result = subprocess.run(
                            ['python3', '-m', 'py_compile', file_path], 
                            capture_output=True, 
                            text=True, 
                            timeout=10
                        )
                        if result.returncode == 0:
                            verification_results["code_compiles"] = True
                            verification_results["verification_details"].append(f"✅ {file_path} compiles successfully")
                        else:
                            verification_results["no_syntax_errors"] = False
                            verification_results["verification_details"].append(f"❌ {file_path} compilation error")
                    except Exception as e:
                        verification_results["verification_details"].append(f"⚠️ Could not verify {file_path}: {str(e)}")
        
        # Check if tests were run and passed
        if execution_log.get("tests_run", False):
            # Look for test output in execution log
            for cmd in execution_log.get("commands_executed", []):
                if any(test_indicator in cmd.lower() for test_indicator in ['test', 'jest', 'pytest']):
                    # Assume tests passed if no errors were recorded after test command
                    recent_errors = [e for e in execution_log.get("errors_encountered", []) 
                                   if 'test' in e.get('tool', '').lower()]
                    if not recent_errors:
                        verification_results["tests_pass"] = True
                        verification_results["verification_details"].append("✅ Tests appear to have passed")
                    else:
                        verification_results["verification_details"].append("❌ Test failures detected")
        
        # Check for common success indicators
        outputs = execution_log.get("outputs_generated", [])
        if outputs:
            for output in outputs[-3:]:  # Check last 3 outputs
                output_content = output.get('output', '').lower()
                if any(success_word in output_content for success_word in ['success', 'completed', 'done', 'finished']):
                    verification_results["functionality_works"] = True
                    break
        
        # Performance check - if too many errors, mark as poor performance
        error_count = len(execution_log.get("errors_encountered", []))
        tool_count = len(execution_log.get("tools_used", []))
        
        if error_count > 5 or tool_count > 30:
            verification_results["performance_acceptable"] = False
            verification_results["verification_details"].append(f"⚠️ Performance concern: {error_count} errors, {tool_count} tools used")
    
    except Exception as e:
        verification_results["verification_details"].append(f"❌ Verification failed: {str(e)}")
    
    return verification_results

def calculate_completion_score(goal_analysis, execution_log, verification_results):
    """Calculate objective completion score"""
    
    score = 0.0
    max_score = 100.0
    details = []
    
    # Code quality (30 points)
    if verification_results["code_compiles"]:
        score += 15
        details.append("✅ Code compiles/parses correctly (+15)")
    
    if verification_results["no_syntax_errors"]:
        score += 15
        details.append("✅ No syntax errors (+15)")
    else:
        details.append("❌ Syntax errors detected (-15)")
    
    # Functionality (40 points)
    if verification_results["tests_pass"]:
        score += 20
        details.append("✅ Tests pass (+20)")
    elif execution_log.get("tests_run", False):
        details.append("⚠️ Tests run but may have failed")
    
    if verification_results["functionality_works"]:
        score += 20
        details.append("✅ Functionality appears to work (+20)")
    
    # Completeness (20 points)
    if execution_log.get("code_created", False):
        score += 10
        details.append("✅ Code was created (+10)")
    
    if execution_log.get("documentation_updated", False):
        score += 5
        details.append("✅ Documentation updated (+5)")
    
    if execution_log.get("dependencies_installed", False):
        score += 5
        details.append("✅ Dependencies handled (+5)")
    
    # Performance penalty (10 points)
    if verification_results["performance_acceptable"]:
        score += 10
        details.append("✅ Good performance (+10)")
    else:
        details.append("❌ Performance concerns (-10)")
    
    return min(score, max_score), details

def update_task_performance_history(task_signature, session_id, completion_score, verification_results):
    """Update performance tracking for repeated tasks"""
    
    history_file = Path(f".claude/data/performance_history_{task_signature}.json")
    
    performance_history = {
        "task_signature": task_signature,
        "attempts": [],
        "average_score": 0.0,
        "trend": "neutral",
        "user_satisfaction_pattern": "unknown"
    }
    
    if history_file.exists():
        with open(history_file, 'r') as f:
            performance_history = json.load(f)
    
    # Add this attempt
    attempt = {
        "session_id": session_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "completion_score": completion_score,
        "verification_results": verification_results,
        "attempt_number": len(performance_history["attempts"]) + 1
    }
    
    performance_history["attempts"].append(attempt)
    
    # Calculate trends
    if len(performance_history["attempts"]) >= 2:
        recent_scores = [a["completion_score"] for a in performance_history["attempts"][-3:]]
        performance_history["average_score"] = sum(recent_scores) / len(recent_scores)
        
        # Determine trend
        if len(performance_history["attempts"]) >= 3:
            if recent_scores[-1] > recent_scores[-2] > recent_scores[-3]:
                performance_history["trend"] = "improving"
            elif recent_scores[-1] < recent_scores[-2] < recent_scores[-3]:
                performance_history["trend"] = "declining"
            else:
                performance_history["trend"] = "stable"
        
        # Detect user dissatisfaction pattern
        if len(performance_history["attempts"]) > 2:
            performance_history["user_satisfaction_pattern"] = "user_repeating_task"
            
            if performance_history["average_score"] < 70:
                performance_history["user_satisfaction_pattern"] = "user_unsatisfied_low_quality"
            elif len(performance_history["attempts"]) > 3:
                performance_history["user_satisfaction_pattern"] = "user_unsatisfied_persistent"
    else:
        performance_history["average_score"] = completion_score
    
    # Save updated history
    with open(history_file, 'w') as f:
        json.dump(performance_history, f, indent=2)
    
    return performance_history

def main():
    if len(sys.argv) < 2:
        print("Usage: performance_analyzer.py <event_json>")
        sys.exit(1)
    
    try:
        event_data = json.loads(sys.argv[1])
        session_id = event_data.get('session_id', 'unknown')
        
        # Load goal analysis and execution log
        session_dir = Path(".claude/data/sessions")
        goal_file = session_dir / f"{session_id}_goal_analysis.json"
        execution_file = session_dir / f"{session_id}_execution_log.json"
        
        if not goal_file.exists() or not execution_file.exists():
            print(f"Missing analysis files for session {session_id}")
            sys.exit(1)
        
        with open(goal_file, 'r') as f:
            goal_analysis = json.load(f)
        
        with open(execution_file, 'r') as f:
            execution_log = json.load(f)
        
        print(f"🔍 Analyzing performance for session {session_id}")
        
        # Run verification tests
        verification_results = run_verification_tests(execution_log, goal_analysis)
        
        # Calculate completion score
        completion_score, score_details = calculate_completion_score(
            goal_analysis, execution_log, verification_results
        )
        
        # Update performance history
        task_signature = goal_analysis.get("task_signature", "unknown")
        performance_history = update_task_performance_history(
            task_signature, session_id, completion_score, verification_results
        )
        
        # Create final performance report
        performance_report = {
            "session_id": session_id,
            "task_signature": task_signature,
            "completion_score": completion_score,
            "verification_results": verification_results,
            "score_details": score_details,
            "performance_history": performance_history,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Save performance report
        report_file = session_dir / f"{session_id}_performance_report.json"
        with open(report_file, 'w') as f:
            json.dump(performance_report, f, indent=2)
        
        # Output summary
        print(f"📊 Completion Score: {completion_score:.1f}/100")
        print(f"🔧 Verification: {len([r for r in verification_results.values() if r == True])}/6 checks passed")
        
        if performance_history["user_satisfaction_pattern"] == "user_repeating_task":
            attempts = len(performance_history["attempts"])
            avg_score = performance_history["average_score"]
            print(f"⚠️  REPEATED TASK: Attempt #{attempts}, Avg Score: {avg_score:.1f}")
            
            if attempts > 2 and avg_score < 70:
                print("🚨 USER LIKELY UNSATISFIED - Consider alternative approach")
        
        print("📋 Score breakdown:")
        for detail in score_details:
            print(f"   {detail}")
        
    except Exception as e:
        print(f"Error in performance analysis: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()