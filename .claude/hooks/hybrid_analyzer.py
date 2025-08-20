#!/usr/bin/env python3
"""
Hybrid Hook: Combines system data collection with Claude reasoning
Collects system data, then triggers Claude analysis via Task tool
"""

import sys
import json
import os
import subprocess
from pathlib import Path
from datetime import datetime, timezone

def collect_system_data(event_data):
    """Collect objective system data that Claude cannot access"""
    
    session_id = event_data.get('session_id', 'unknown')
    hook_type = event_data.get('hook_type', 'unknown')
    
    system_data = {
        "session_id": session_id,
        "hook_type": hook_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "system_metrics": {}
    }
    
    try:
        # Git information
        if Path('.git').exists():
            branch = subprocess.check_output(['git', 'branch', '--show-current'], 
                                           text=True, timeout=5).strip()
            status = subprocess.check_output(['git', 'status', '--porcelain'], 
                                           text=True, timeout=5)
            uncommitted = len(status.strip().split('\n')) if status.strip() else 0
            
            system_data["system_metrics"]["git"] = {
                "current_branch": branch,
                "uncommitted_files": uncommitted,
                "has_changes": uncommitted > 0
            }
    except:
        system_data["system_metrics"]["git"] = {"error": "Git not available"}
    
    try:
        # File system metrics
        current_dir = Path('.')
        file_counts = {
            "total_files": len(list(current_dir.rglob('*'))),
            "js_files": len(list(current_dir.rglob('*.js'))),
            "ts_files": len(list(current_dir.rglob('*.ts'))),
            "py_files": len(list(current_dir.rglob('*.py'))),
            "md_files": len(list(current_dir.rglob('*.md')))
        }
        system_data["system_metrics"]["files"] = file_counts
    except:
        system_data["system_metrics"]["files"] = {"error": "File access failed"}
    
    try:
        # Project configuration
        config_files = {}
        for config_file in ['package.json', '.claude/claude.json', 'tsconfig.json']:
            if Path(config_file).exists():
                config_files[config_file] = {
                    "exists": True,
                    "size": Path(config_file).stat().st_size,
                    "modified": Path(config_file).stat().st_mtime
                }
            else:
                config_files[config_file] = {"exists": False}
        
        system_data["system_metrics"]["config"] = config_files
    except:
        system_data["system_metrics"]["config"] = {"error": "Config access failed"}
    
    # Save system data for Claude to analyze
    data_dir = Path(".claude/data/system")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    with open(data_dir / f"{session_id}_{hook_type}_system_data.json", 'w') as f:
        json.dump(system_data, f, indent=2)
    
    return system_data

def create_claude_analysis_prompt(system_data, event_data):
    """Create a prompt for Claude to analyze the system data"""
    
    prompt = f"""# Intelligent System Analysis

I have collected objective system data that requires your reasoning and analysis:

## System Data Collected:
```json
{json.dumps(system_data, indent=2)}
```

## Event Context:
- Session ID: {event_data.get('session_id', 'unknown')}
- Hook Type: {event_data.get('hook_type', 'unknown')}
- Payload: {json.dumps(event_data.get('payload', {}), indent=2)}

## Analysis Required:

### 1. System Health Assessment
Based on the git status, file metrics, and configuration:
- What is the current project health?
- Are there any concerning patterns?
- What risks do you identify?

### 2. Development Context Analysis  
Considering the hook type and event payload:
- What was the user trying to accomplish?
- How does this fit into the project's evolution?
- What patterns emerge from the activity?

### 3. Intelligent Recommendations
Using your reasoning about software development:
- What immediate actions would improve the situation?
- What long-term strategies should be considered?
- How can we prevent common pitfalls?

### 4. Quality Assessment
Evaluate the current state against best practices:
- Code organization quality
- Development workflow efficiency  
- Technical debt indicators
- Maintenance burden assessment

Please provide a structured analysis with specific, actionable insights."""

    return prompt

def trigger_claude_analysis(system_data, event_data):
    """Trigger Claude analysis of the system data"""
    
    # Create analysis prompt
    prompt = create_claude_analysis_prompt(system_data, event_data)
    
    # Save prompt for potential manual review
    prompt_file = Path(f".claude/data/system/{event_data.get('session_id', 'unknown')}_analysis_prompt.md")
    with open(prompt_file, 'w') as f:
        f.write(prompt)
    
    # In a real implementation, this would trigger Claude via the Task tool
    # For now, we log that analysis is ready
    analysis_trigger = {
        "type": "claude_analysis_ready",
        "session_id": event_data.get('session_id'),
        "system_data_file": f"{event_data.get('session_id')}_{event_data.get('hook_type')}_system_data.json",
        "analysis_prompt_file": str(prompt_file),
        "trigger_time": datetime.now(timezone.utc).isoformat()
    }
    
    # Save trigger info
    with open(Path(f".claude/data/system/analysis_trigger_{event_data.get('session_id')}.json"), 'w') as f:
        json.dump(analysis_trigger, f, indent=2)
    
    return analysis_trigger

def main():
    if len(sys.argv) < 2:
        print("Usage: hybrid_analyzer.py <event_json>")
        sys.exit(1)
    
    try:
        # Parse event data
        event_data = json.loads(sys.argv[1])
        
        # Collect system data that Claude cannot access
        print("🔍 Collecting system metrics...")
        system_data = collect_system_data(event_data)
        
        # Prepare for Claude analysis
        print("🧠 Preparing Claude analysis...")
        analysis_trigger = trigger_claude_analysis(system_data, event_data)
        
        # Output summary
        print(f"📊 System data collected: {len(system_data['system_metrics'])} categories")
        print(f"🎯 Analysis prompt ready: {analysis_trigger['analysis_prompt_file']}")
        print(f"💡 Claude can now provide intelligent insights on this data")
        
        # Suggest next steps
        print("\n🚀 Next Steps:")
        print("1. Review the system data in .claude/data/system/")
        print("2. Use the generated analysis prompt with Claude")
        print("3. Combine system metrics with Claude's reasoning")
        print("4. Generate actionable insights and recommendations")
        
    except Exception as e:
        print(f"Error in hybrid analysis: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()