#!/usr/bin/env python3
"""
Claude Sub-Agent: Real-time Execution Tracking
Triggered on PostToolUse to track what's actually happening
"""

import sys
import json
import os
from datetime import datetime, timezone
from pathlib import Path

def track_execution_step(event_data):
    """Track each tool use and build execution context"""
    
    session_id = event_data.get('session_id', 'unknown')
    tool_name = event_data.get('payload', {}).get('tool', 'unknown')
    tool_result = event_data.get('payload', {}).get('result', '')
    
    # Load existing execution log
    session_dir = Path(".claude/data/sessions")
    execution_log_file = session_dir / f"{session_id}_execution_log.json"
    
    execution_log = {
        "session_id": session_id,
        "start_time": datetime.now(timezone.utc).isoformat(),
        "tools_used": [],
        "files_modified": [],
        "commands_executed": [],
        "errors_encountered": [],
        "outputs_generated": [],
        "code_created": False,
        "tests_run": False,
        "documentation_updated": False,
        "dependencies_installed": False
    }
    
    if execution_log_file.exists():
        with open(execution_log_file, 'r') as f:
            execution_log = json.load(f)
    
    # Process this tool use
    step = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tool": tool_name,
        "success": "error" not in tool_result.lower(),
        "details": tool_result[:500] if tool_result else ""  # Limit size
    }
    
    execution_log["tools_used"].append(step)
    
    # Analyze what happened
    if tool_name == "Write" or tool_name == "Edit" or tool_name == "MultiEdit":
        file_path = event_data.get('payload', {}).get('file_path', '')
        if file_path and file_path not in execution_log["files_modified"]:
            execution_log["files_modified"].append(file_path)
        execution_log["code_created"] = True
    
    elif tool_name == "Bash":
        command = event_data.get('payload', {}).get('command', '')
        if command:
            execution_log["commands_executed"].append(command)
            
            # Detect specific activities
            if any(test_cmd in command.lower() for test_cmd in ['test', 'jest', 'pytest', 'npm test', 'bun test']):
                execution_log["tests_run"] = True
            
            if any(install_cmd in command.lower() for install_cmd in ['install', 'add', 'pip install', 'npm install', 'bun install']):
                execution_log["dependencies_installed"] = True
    
    elif tool_name == "Read":
        # Track what's being read for context
        file_path = event_data.get('payload', {}).get('file_path', '')
        if file_path and file_path.endswith('.md'):
            execution_log["documentation_updated"] = True
    
    # Track errors
    if "error" in tool_result.lower() or step["success"] == False:
        execution_log["errors_encountered"].append({
            "tool": tool_name,
            "error": tool_result[:200],
            "timestamp": step["timestamp"]
        })
    
    # Track meaningful outputs
    if tool_result and len(tool_result) > 50:
        execution_log["outputs_generated"].append({
            "tool": tool_name,
            "output_length": len(tool_result),
            "timestamp": step["timestamp"]
        })
    
    # Save updated log
    with open(execution_log_file, 'w') as f:
        json.dump(execution_log, f, indent=2)
    
    return execution_log

def main():
    if len(sys.argv) < 2:
        print("Usage: execution_tracker.py <event_json>")
        sys.exit(1)
    
    try:
        event_data = json.loads(sys.argv[1])
        execution_log = track_execution_step(event_data)
        
        # Output progress indicators
        session_id = event_data.get('session_id', 'unknown')
        tools_count = len(execution_log["tools_used"])
        files_count = len(execution_log["files_modified"])
        errors_count = len(execution_log["errors_encountered"])
        
        print(f"📊 Execution tracking - Session: {session_id}")
        print(f"🔧 Tools used: {tools_count}, Files modified: {files_count}")
        if errors_count > 0:
            print(f"⚠️  Errors encountered: {errors_count}")
        
        # Check for concerning patterns
        if errors_count > 3:
            print("🚨 High error rate detected - task may be struggling")
        
        if tools_count > 20:
            print("🔄 Complex task detected - many tools being used")
        
    except Exception as e:
        print(f"Error in execution tracking: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()