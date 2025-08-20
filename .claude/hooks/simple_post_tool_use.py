#!/usr/bin/env python3
"""
Simple Post-Tool-Use Hook - Phase 1 Implementation  
Measures duration and extracts patterns with <2ms overhead
"""
import json
import sys
import time
import sqlite3
from pathlib import Path

def main():
    try:
        processing_start = time.time()
        
        # Read input data
        input_data = json.load(sys.stdin)
        
        # Extract metrics
        tool_name = input_data.get('tool_name', 'unknown')
        session_id = input_data.get('session_id', 'unknown')
        success = input_data.get('success', True)
        start_time = input_data.get('start_time', time.time())
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Store in database
        db_path = '.claude/hooks/hooks.db'
        conn = sqlite3.connect(db_path)
        
        # Update the event with duration and success
        conn.execute('''
            UPDATE events 
            SET duration = ?, success = ? 
            WHERE tool_name = ? AND session_id = ? AND timestamp = ?
        ''', (duration, success, tool_name, session_id, start_time))
        
        # Create patterns table if not exists
        conn.execute('''
            CREATE TABLE IF NOT EXISTS patterns (
                tool_name TEXT PRIMARY KEY,
                avg_duration REAL,
                success_rate REAL,
                count INTEGER
            )
        ''')
        
        # Update patterns (simple aggregation)
        conn.execute('''
            INSERT OR REPLACE INTO patterns (tool_name, avg_duration, success_rate, count)
            SELECT 
                tool_name,
                AVG(duration) as avg_duration,
                AVG(CAST(success AS FLOAT)) as success_rate,
                COUNT(*) as count
            FROM events 
            WHERE tool_name = ?
            GROUP BY tool_name
        ''', (tool_name,))
        
        conn.commit()
        conn.close()
        
        # Trigger coordination if needed (simple check)
        if should_trigger_coordination(tool_name, duration):
            trigger_mcp_task(tool_name, duration)
        
        processing_time = time.time() - processing_start
        
        # Target: <2ms processing time
        if processing_time > 0.002:
            # Log slow processing (but don't block)
            pass
            
    except Exception:
        # Silent fail - hooks should never block
        pass

def should_trigger_coordination(tool_name, duration):
    """Simple coordination trigger logic"""
    # Trigger on slow operations or specific tools
    if duration > 10:  # Slow operation
        return True
    if tool_name in ['Edit', 'Write', 'MultiEdit']:  # Code changes
        return True
    return False

def trigger_mcp_task(tool_name, duration):
    """Trigger MCP coordination task"""
    try:
        coordination_data = {
            'tool_name': tool_name,
            'duration': duration,
            'timestamp': time.time(),
            'suggested_action': 'analyze_code' if tool_name in ['Edit', 'Write'] else 'monitor'
        }
        
        # Store coordination trigger
        conn = sqlite3.connect('.claude/hooks/hooks.db')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS coordination_triggers (
                timestamp REAL,
                tool_name TEXT,
                action TEXT,
                data TEXT
            )
        ''')
        conn.execute(
            "INSERT INTO coordination_triggers VALUES (?, ?, ?, ?)",
            (time.time(), tool_name, coordination_data['suggested_action'], json.dumps(coordination_data))
        )
        conn.commit()
        conn.close()
        
    except Exception:
        pass  # Silent fail

if __name__ == '__main__':
    main()