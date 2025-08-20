#!/usr/bin/env python3
"""
Simple Stop Hook - Phase 1 Implementation
Aggregates session data and triggers learning with <3ms overhead
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
        session_id = input_data.get('session_id', 'unknown')
        
        # Connect to database
        db_path = '.claude/hooks/hooks.db'
        conn = sqlite3.connect(db_path)
        
        # Aggregate session data
        session_stats = conn.execute('''
            SELECT 
                COUNT(*) as tool_count,
                AVG(duration) as avg_duration,
                AVG(CAST(success AS FLOAT)) as success_rate,
                MIN(timestamp) as session_start,
                MAX(timestamp) as session_end
            FROM events 
            WHERE session_id = ?
        ''', (session_id,)).fetchone()
        
        if session_stats and session_stats[0] > 0:
            # Create session summary table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS session_summary (
                    session_id TEXT PRIMARY KEY,
                    tool_count INTEGER,
                    avg_duration REAL,
                    success_rate REAL,
                    session_start REAL,
                    session_end REAL,
                    session_duration REAL
                )
            ''')
            
            # Store session summary
            session_duration = session_stats[4] - session_stats[3] if session_stats[3] and session_stats[4] else 0
            conn.execute('''
                INSERT OR REPLACE INTO session_summary VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                session_id,
                session_stats[0],  # tool_count
                session_stats[1] or 0,  # avg_duration
                session_stats[2] or 0,  # success_rate
                session_stats[3] or 0,  # session_start
                session_stats[4] or 0,  # session_end
                session_duration
            ))
            
            # Trigger learning (simple pattern recognition)
            trigger_learning(conn, session_id, session_stats)
        
        conn.commit()
        conn.close()
        
        processing_time = time.time() - processing_start
        
        # Target: <3ms processing time
        if processing_time > 0.003:
            # Log slow processing (but don't block)
            pass
            
    except Exception:
        # Silent fail - hooks should never block
        pass

def trigger_learning(conn, session_id, session_stats):
    """Simple learning trigger"""
    try:
        tool_count, avg_duration, success_rate = session_stats[0], session_stats[1] or 0, session_stats[2] or 0
        
        # Create learning insights table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS learning_insights (
                timestamp REAL,
                session_id TEXT,
                insight_type TEXT,
                insight_data TEXT
            )
        ''')
        
        insights = []
        
        # Generate simple insights
        if success_rate < 0.8:
            insights.append({
                'type': 'low_success_rate',
                'message': f'Session success rate {success_rate:.1%} below optimal',
                'suggestion': 'Review failed operations and consider workflow optimization'
            })
        
        if avg_duration > 5:
            insights.append({
                'type': 'slow_operations',
                'message': f'Average operation time {avg_duration:.1f}s above optimal',
                'suggestion': 'Consider tool alternatives or system optimization'
            })
        
        if tool_count > 50:
            insights.append({
                'type': 'high_activity',
                'message': f'High activity session with {tool_count} operations',
                'suggestion': 'Consider workflow automation opportunities'
            })
        
        # Store insights
        for insight in insights:
            conn.execute(
                "INSERT INTO learning_insights VALUES (?, ?, ?, ?)",
                (time.time(), session_id, insight['type'], json.dumps(insight))
            )
        
    except Exception:
        pass  # Silent fail

if __name__ == '__main__':
    main()