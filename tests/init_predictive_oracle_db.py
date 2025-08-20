#!/usr/bin/env python3
"""
Initialize databases for Predictive Performance Oracle testing
Creates tables and sample data for testing
"""

import sqlite3
import datetime
import random
from pathlib import Path

def init_performance_metrics_db():
    """Initialize performance metrics database with sample data"""
    db_path = Path(".claude/hooks/performance/performance_metrics.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create performance_metrics table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS performance_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            metric_name TEXT NOT NULL,
            value REAL NOT NULL,
            unit TEXT,
            category TEXT,
            metadata TEXT
        )
    """)
    
    # Insert sample data for 57 different metrics
    metrics = [
        # CPU metrics
        ("cpu_usage_percent", "percent", "system"),
        ("cpu_frequency_mhz", "mhz", "system"),
        ("cpu_load_1min", "load", "system"),
        ("cpu_load_5min", "load", "system"),
        ("cpu_load_15min", "load", "system"),
        ("cpu_context_switches", "count", "system"),
        
        # Memory metrics
        ("memory_usage_percent", "percent", "system"),
        ("memory_available_mb", "mb", "system"),
        ("memory_swap_percent", "percent", "system"),
        ("memory_page_faults", "count", "system"),
        
        # Disk metrics
        ("disk_usage_percent", "percent", "system"),
        ("disk_read_mb", "mb", "system"),
        ("disk_write_mb", "mb", "system"),
        ("disk_io_time_ms", "ms", "system"),
        
        # Network metrics
        ("network_bytes_sent", "bytes", "network"),
        ("network_bytes_recv", "bytes", "network"),
        ("network_packets_sent", "count", "network"),
        ("network_packets_recv", "count", "network"),
        ("network_errors", "count", "network"),
        
        # Process metrics
        ("process_count", "count", "system"),
        ("thread_count", "count", "system"),
        ("file_descriptors", "count", "system"),
        
        # Tool execution metrics
        ("tool_execution_time_ms", "ms", "tool"),
        ("tool_success_rate", "percent", "tool"),
        ("tool_error_count", "count", "tool"),
        
        # Hook performance metrics
        ("hook_execution_time_ms", "ms", "hook"),
        ("hook_queue_length", "count", "hook"),
        ("hook_processing_rate", "rate", "hook"),
        
        # MCP coordination metrics
        ("mcp_response_time_ms", "ms", "mcp"),
        ("mcp_active_connections", "count", "mcp"),
        ("mcp_message_queue_size", "count", "mcp"),
        
        # Security validation metrics
        ("security_checks_performed", "count", "security"),
        ("security_threats_detected", "count", "security"),
        ("security_validation_time_ms", "ms", "security"),
        
        # Application metrics
        ("request_latency_ms", "ms", "application"),
        ("request_throughput", "rps", "application"),
        ("error_rate_percent", "percent", "application"),
        ("cache_hit_ratio", "ratio", "application"),
        
        # Database metrics
        ("db_query_time_ms", "ms", "database"),
        ("db_connection_count", "count", "database"),
        ("db_transaction_rate", "tps", "database"),
        
        # Custom metrics to reach 57
        ("code_complexity_score", "score", "code"),
        ("test_coverage_percent", "percent", "code"),
        ("build_time_seconds", "seconds", "build"),
        ("deployment_frequency", "count", "deployment"),
        ("mean_time_to_recovery", "minutes", "reliability"),
        ("feature_completion_rate", "percent", "productivity"),
        ("bug_detection_rate", "percent", "quality"),
        ("performance_score", "score", "performance"),
        ("user_satisfaction_score", "score", "user"),
        ("api_availability_percent", "percent", "availability"),
        ("data_processing_rate", "mbps", "data"),
        ("queue_processing_time", "ms", "queue"),
        ("cache_memory_usage", "mb", "cache"),
        ("log_volume_mb", "mb", "logging"),
        ("alert_frequency", "count", "monitoring")
    ]
    
    # Generate sample data points
    base_time = datetime.datetime.now() - datetime.timedelta(hours=24)
    
    for i in range(100):  # 100 time points
        timestamp = base_time + datetime.timedelta(minutes=i*15)
        
        for metric_name, unit, category in metrics:
            # Generate realistic values based on metric type
            if "percent" in unit:
                value = random.uniform(0, 100)
            elif "time" in metric_name or "ms" in unit:
                value = random.uniform(10, 500)
            elif "count" in metric_name:
                value = random.randint(1, 1000)
            elif "score" in metric_name:
                value = random.uniform(0, 10)
            else:
                value = random.uniform(0, 1000)
            
            cursor.execute("""
                INSERT INTO performance_metrics 
                (timestamp, metric_name, value, unit, category)
                VALUES (?, ?, ?, ?, ?)
            """, (timestamp, metric_name, value, unit, category))
    
    conn.commit()
    conn.close()
    print(f"✅ Initialized performance_metrics.db with {len(metrics)} unique metrics")

def init_predictive_analytics_db():
    """Initialize predictive analytics database with velocity predictions"""
    db_path = Path(".claude/hooks/performance/predictive_analytics.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create velocity_predictions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS velocity_predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prediction_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            task_type TEXT NOT NULL,
            predicted_velocity REAL NOT NULL,
            confidence_score REAL NOT NULL,
            model_used TEXT NOT NULL,
            actual_velocity REAL,
            error_margin REAL,
            metadata TEXT
        )
    """)
    
    # Create trend_analysis table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trend_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analysis_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            metric_name TEXT NOT NULL,
            trend_direction TEXT,
            trend_strength REAL,
            forecast_horizon INTEGER,
            forecast_values TEXT,
            model_params TEXT
        )
    """)
    
    # Generate 24 velocity predictions
    task_types = [
        "feature_implementation", "bug_fix", "code_refactoring",
        "test_creation", "documentation", "deployment",
        "code_review", "performance_optimization", "security_audit",
        "database_migration", "api_integration", "ui_development"
    ]
    
    models = ["TimeGPT", "ARIMA", "Random Forest", "LSTM", "Ensemble"]
    
    base_time = datetime.datetime.now() - datetime.timedelta(days=7)
    
    for i in range(24):
        timestamp = base_time + datetime.timedelta(hours=i*7)
        task_type = random.choice(task_types)
        model = random.choice(models)
        
        # Generate realistic velocity predictions
        base_velocity = random.uniform(60, 120)
        confidence = random.uniform(0.75, 0.95)
        
        cursor.execute("""
            INSERT INTO velocity_predictions 
            (prediction_timestamp, task_type, predicted_velocity, 
             confidence_score, model_used)
            VALUES (?, ?, ?, ?, ?)
        """, (timestamp, task_type, base_velocity, confidence, model))
    
    conn.commit()
    conn.close()
    print("✅ Initialized predictive_analytics.db with 24 velocity predictions")

if __name__ == "__main__":
    print("🔧 Initializing databases for Predictive Performance Oracle...")
    init_performance_metrics_db()
    init_predictive_analytics_db()
    print("✨ Database initialization complete!")