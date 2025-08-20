#!/usr/bin/env python3
"""
Simple Pre-Tool-Use Hook - Phase 1 Implementation
Captures start time with <1ms overhead
"""
import json
import sys
import time
import sqlite3
from pathlib import Path

def main():
    try:
        start_time = time.time()
        
        # Read input data
        input_data = json.load(sys.stdin)
        
        # Extract basic info
        tool_name = input_data.get('tool_name', 'unknown')
        session_id = input_data.get('session_id', 'unknown')
        
        # Initialize database
        db_path = '.claude/hooks/hooks.db'
        conn = sqlite3.connect(db_path)
        
        # Create table if not exists
        conn.execute('''
            CREATE TABLE IF NOT EXISTS events (
                timestamp REAL,
                tool_name TEXT,
                duration REAL,
                success BOOLEAN,
                session_id TEXT
            )
        ''')
        
        # Store start event (duration will be updated by post hook)
        conn.execute(
            "INSERT INTO events VALUES (?, ?, ?, ?, ?)",
            (start_time, tool_name, 0, True, session_id)
        )
        conn.commit()
        conn.close()
        
        # Output for next hook
        output = {
            'start_time': start_time,
            'tool_name': tool_name,
            'session_id': session_id
        }
        print(json.dumps(output))
        
    except Exception:
        # Silent fail - hooks should never block
        pass

if __name__ == '__main__':
    main()