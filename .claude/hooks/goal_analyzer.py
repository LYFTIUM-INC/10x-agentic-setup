#!/usr/bin/env python3
"""
Claude Sub-Agent: Goal Analysis & Intent Recognition
Triggered on UserPromptSubmit to deeply understand user intentions
"""

import sys
import json
import os
import hashlib
from datetime import datetime, timezone
from pathlib import Path

def create_task_signature(prompt):
    """Create a unique signature for similar tasks"""
    # Normalize prompt for similarity detection
    normalized = prompt.lower().strip()
    # Remove common variations but keep core intent
    normalized = normalized.replace("please", "").replace("can you", "").replace("could you", "")
    normalized = " ".join(normalized.split())  # Normalize whitespace
    return hashlib.md5(normalized.encode()).hexdigest()[:12]

def analyze_user_intent(prompt, session_id, context=None):
    """
    Use Claude's reasoning to deeply understand what the user actually wants
    """
    
    # Check for previous similar tasks
    task_signature = create_task_signature(prompt)
    history_file = Path(f".claude/data/task_history_{task_signature}.json")
    previous_attempts = []
    
    if history_file.exists():
        with open(history_file, 'r') as f:
            previous_attempts = json.load(f)
    
    # Prepare analysis context
    analysis_context = {
        "current_prompt": prompt,
        "session_id": session_id,
        "task_signature": task_signature,
        "previous_attempts": len(previous_attempts),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "context": context or {}
    }
    
    # Save initial analysis
    analysis = {
        "task_signature": task_signature,
        "session_id": session_id,
        "timestamp": analysis_context["timestamp"],
        "original_prompt": prompt,
        "analysis": {
            # These will be filled by Claude's analysis
            "primary_objective": None,
            "success_criteria": [],
            "task_type": None,
            "complexity": None,
            "deliverables": [],
            "quality_standards": [],
            "potential_pitfalls": [],
            "testing_approach": None
        },
        "previous_attempts": previous_attempts,
        "confidence": 0.0
    }
    
    # Save to session-specific file
    session_dir = Path(".claude/data/sessions")
    session_dir.mkdir(parents=True, exist_ok=True)
    
    with open(session_dir / f"{session_id}_goal_analysis.json", 'w') as f:
        json.dump(analysis, f, indent=2)
    
    # Update task history
    previous_attempts.append({
        "session_id": session_id,
        "timestamp": analysis_context["timestamp"],
        "prompt": prompt
    })
    
    history_file.parent.mkdir(parents=True, exist_ok=True)
    with open(history_file, 'w') as f:
        json.dump(previous_attempts, f, indent=2)
    
    print(f"📋 Goal analysis initialized for session {session_id}")
    print(f"🔍 Task signature: {task_signature}")
    if len(previous_attempts) > 1:
        print(f"⚠️  Warning: Similar task attempted {len(previous_attempts)} times")
    
    return analysis

def main():
    if len(sys.argv) < 2:
        print("Usage: goal_analyzer.py <event_json>")
        sys.exit(1)
    
    try:
        event_data = json.loads(sys.argv[1])
        payload = event_data.get('payload', {})
        prompt = payload.get('input', '')
        session_id = event_data.get('session_id', 'unknown')
        
        if not prompt:
            print("No prompt found in event data")
            sys.exit(1)
        
        analysis = analyze_user_intent(prompt, session_id, payload)
        
        # Output for Claude Code to process
        print(json.dumps({
            "status": "goal_analysis_complete",
            "session_id": session_id,
            "task_signature": analysis["task_signature"],
            "repeat_attempt": len(analysis["previous_attempts"]) > 1
        }))
        
    except Exception as e:
        print(f"Error in goal analysis: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()