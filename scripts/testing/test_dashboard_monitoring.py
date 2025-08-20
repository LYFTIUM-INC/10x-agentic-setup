#!/usr/bin/env python3
"""
Test Dashboard and Monitoring Integration
Simulates real agent activity to verify dashboard functionality
"""

import time
import sqlite3
import random
import json
import psutil
from pathlib import Path
from datetime import datetime
import sys
import os

# Add project path to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Performance metrics database
PERF_DB = "databases/performance/metrics.db"
SECURITY_DB = "databases/security/audit.db"
ANALYTICS_DB = "databases/analytics/predictive.db"

def insert_performance_metrics():
    """Insert test performance metrics"""
    print("📊 Inserting performance metrics...")
    
    conn = sqlite3.connect(PERF_DB)
    cursor = conn.cursor()
    
    # Insert system metrics
    for i in range(10):
        timestamp = time.time() - (i * 60)  # Spread over last 10 minutes
        cpu = random.uniform(30, 80)
        memory = random.uniform(40, 70)
        disk = random.uniform(60, 85)
        
        cursor.execute('''
            INSERT INTO system_metrics (timestamp, cpu_usage, memory_usage, disk_usage, network_io)
            VALUES (?, ?, ?, ?, ?)
        ''', (timestamp, cpu, memory, disk, random.randint(1000, 50000)))
    
    # Insert tool executions
    tools = ['Read', 'Write', 'Edit', 'Bash', 'Grep', 'WebSearch']
    for i in range(20):
        tool = random.choice(tools)
        timestamp = time.time() - random.randint(0, 3600)
        exec_time = random.uniform(0.1, 5.0)
        success = random.random() > 0.1  # 90% success rate
        
        cursor.execute('''
            INSERT INTO tool_executions (timestamp, tool_name, execution_time, success, arguments, result_size)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (timestamp, tool, exec_time, success, '{"test": true}', random.randint(100, 10000)))
    
    # Insert performance metrics
    metrics = ['response_time', 'throughput', 'latency', 'error_rate']
    for i in range(30):
        metric = random.choice(metrics)
        timestamp = time.time() - random.randint(0, 7200)
        value = random.uniform(0, 100)
        
        cursor.execute('''
            INSERT INTO performance_metrics (timestamp, metric_name, metric_value, context, session_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (timestamp, metric, value, '{"source": "test"}', 'test-session'))
    
    conn.commit()
    conn.close()
    print("  ✅ Inserted system metrics, tool executions, and performance data")

def insert_security_events():
    """Insert test security events"""
    print("🛡️ Inserting security events...")
    
    conn = sqlite3.connect(SECURITY_DB)
    cursor = conn.cursor()
    
    # Insert security events
    event_types = ['path_validation', 'command_injection', 'file_access', 'auth_attempt']
    severities = ['low', 'medium', 'high', 'critical']
    statuses = ['allowed', 'blocked', 'warning']
    
    for i in range(15):
        timestamp = time.time() - random.randint(0, 86400)
        event_type = random.choice(event_types)
        severity = random.choice(severities)
        status = random.choice(statuses)
        
        cursor.execute('''
            INSERT INTO security_events (timestamp, event_type, severity, details, file_path, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (timestamp, event_type, severity, f'Test {event_type} event', f'/test/path/{i}', status))
    
    conn.commit()
    conn.close()
    print("  ✅ Inserted security events")

def insert_predictive_analytics():
    """Insert test predictive analytics data"""
    print("🔮 Inserting predictive analytics...")
    
    conn = sqlite3.connect(ANALYTICS_DB)
    cursor = conn.cursor()
    
    # Insert velocity predictions
    task_types = ['feature_implementation', 'bug_fix', 'refactoring', 'testing']
    for i in range(10):
        timestamp = time.time() - random.randint(0, 3600)
        task_type = random.choice(task_types)
        predicted_time = random.uniform(300, 7200)  # 5 min to 2 hours
        confidence = random.uniform(0.5, 0.95)
        
        cursor.execute('''
            INSERT INTO velocity_predictions (timestamp, task_type, predicted_time, confidence, context)
            VALUES (?, ?, ?, ?, ?)
        ''', (timestamp, task_type, predicted_time, confidence, '{"model": "test"}'))
    
    # Insert trend analysis
    metrics = ['cpu_usage', 'memory_usage', 'error_rate', 'response_time']
    directions = ['increasing', 'decreasing', 'stable']
    for i in range(8):
        timestamp = time.time() - random.randint(0, 7200)
        metric = random.choice(metrics)
        direction = random.choice(directions)
        slope = random.uniform(-0.5, 0.5)
        confidence = random.uniform(0.6, 0.9)
        
        cursor.execute('''
            INSERT INTO trend_analysis (timestamp, metric_name, trend_direction, slope, confidence)
            VALUES (?, ?, ?, ?, ?)
        ''', (timestamp, metric, direction, slope, confidence))
    
    conn.commit()
    conn.close()
    print("  ✅ Inserted velocity predictions and trend analysis")

def update_dashboard_data():
    """Update the dashboard data file with simulated metrics"""
    print("📈 Updating dashboard data...")
    
    dashboard_data = {
        'timestamp': time.time(),
        'system_metrics': {
            'avg_cpu_usage': psutil.cpu_percent(interval=1),
            'avg_memory_usage': psutil.virtual_memory().percent,
            'avg_disk_usage': psutil.disk_usage('/').percent,
            'max_cpu_usage': psutil.cpu_percent(interval=0.1),
            'max_memory_usage': psutil.virtual_memory().percent + 5,
            'max_disk_usage': psutil.disk_usage('/').percent + 2,
            'sample_count': 10
        },
        'tool_performance': {
            'avg_execution_time': 1.25,
            'total_executions': 156,
            'success_rate': 94.2,
            'top_tools': [
                {'name': 'Read', 'avg_time': 0.85, 'executions': 45},
                {'name': 'Write', 'avg_time': 1.2, 'executions': 32},
                {'name': 'Edit', 'avg_time': 0.95, 'executions': 28},
                {'name': 'Bash', 'avg_time': 2.5, 'executions': 25},
                {'name': 'Grep', 'avg_time': 0.45, 'executions': 26}
            ]
        },
        'security_summary': {
            'blocked_threats': 8,
            'total_events': 127,
            'recent_violations': 3,
            'backups_created': 5
        },
        'recent_alerts': [
            {
                'message': 'High CPU usage detected (85%)',
                'severity': 'warning',
                'timestamp': time.time() - 300,
                'type': 'performance'
            },
            {
                'message': 'Security scan completed successfully',
                'severity': 'info',
                'timestamp': time.time() - 600,
                'type': 'security'
            }
        ],
        'hook_performance': {
            'avg_execution_time': 0.045,
            'total_executions': 412,
            'success_rate': 99.8
        },
        'mcp_coordination': {
            'active_servers': 7,
            'parallel_tasks': 8,
            'efficiency': 96.5,
            'total_requests': 2156,
            'avg_response_time': 0.72
        },
        'time_series': {
            'timestamps': [datetime.fromtimestamp(time.time() - i*60).strftime('%H:%M') for i in range(20, 0, -1)],
            'cpu_usage': [random.uniform(30, 70) for _ in range(20)],
            'memory_usage': [random.uniform(40, 65) for _ in range(20)],
            'disk_usage': [random.uniform(70, 75) for _ in range(20)]
        },
        'security_breakdown': {
            'allowed': 108,
            'blocked': 15,
            'warnings': 4
        },
        'hook_breakdown': {
            'PreToolUse': {'avg_time': 0.025, 'count': 156},
            'PostToolUse': {'avg_time': 0.035, 'count': 156},
            'UserPromptSubmit': {'avg_time': 0.055, 'count': 45},
            'Stop': {'avg_time': 0.065, 'count': 12}
        },
        'mcp_server_health': {
            'ml-code-intelligence': 98,
            'context-aware-memory': 96,
            'predictive-analytics': 93,
            'ml-testing-qa': 91,
            'agentic-workflow': 95,
            '10x-knowledge-graph': 92,
            '10x-command-analytics': 97
        }
    }
    
    # Save to dashboard data file
    dashboard_path = Path.home() / ".claude" / "dashboard_data.json"
    with open(dashboard_path, 'w') as f:
        json.dump(dashboard_data, f, indent=2)
    
    print("  ✅ Dashboard data updated")

def main():
    """Run all test data insertions"""
    print("🚀 Testing Dashboard and Monitoring Integration")
    print("=" * 50)
    
    # Create databases if they don't exist
    os.makedirs("databases/performance", exist_ok=True)
    os.makedirs("databases/security", exist_ok=True)
    os.makedirs("databases/analytics", exist_ok=True)
    
    # Insert test data
    insert_performance_metrics()
    insert_security_events()
    insert_predictive_analytics()
    update_dashboard_data()
    
    print("\n✅ Test data inserted successfully!")
    print("📊 Dashboard should now show:")
    print("  - System resource metrics")
    print("  - Tool performance statistics")
    print("  - Security events and alerts")
    print("  - Predictive analytics data")
    print("  - Real-time charts and visualizations")
    print("\n💡 Open /home/dell/.claude/dashboard.html in your browser to view the dashboard")

if __name__ == "__main__":
    main()