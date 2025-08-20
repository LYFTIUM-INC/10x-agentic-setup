#!/usr/bin/env python3
"""
Performance Metrics Collector
Real-time collection and analysis of system and tool performance metrics
"""

import os
import psutil
import time
import json
import sqlite3
import logging
import threading
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import statistics
import asyncio
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MetricType(Enum):
    SYSTEM = "system"
    TOOL_EXECUTION = "tool_execution"
    HOOK_PERFORMANCE = "hook_performance"
    MCP_COORDINATION = "mcp_coordination"
    SECURITY_VALIDATION = "security_validation"

class MetricSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

@dataclass
class SystemMetrics:
    timestamp: float
    cpu_usage: float
    memory_usage: float
    memory_available: int
    disk_usage: float
    disk_free: int
    network_sent: int
    network_recv: int
    load_average: List[float]
    process_count: int
    thread_count: int
    open_files: int

@dataclass
class ToolExecutionMetrics:
    tool_name: str
    start_time: float
    end_time: float
    execution_time: float
    cpu_time: float
    memory_peak: int
    input_size: int
    output_size: int
    success: bool
    error_type: Optional[str] = None
    thread_id: str = None
    session_id: str = None

@dataclass
class HookPerformanceMetrics:
    hook_name: str
    hook_type: str  # PreToolUse, PostToolUse, etc.
    execution_time: float
    memory_usage: int
    success: bool
    tool_name: str = None
    error_message: str = None
    timestamp: float = None

@dataclass
class PerformanceAlert:
    alert_id: str
    metric_type: MetricType
    severity: MetricSeverity
    message: str
    threshold_value: float
    current_value: float
    timestamp: float
    metadata: Dict[str, Any] = None

class MetricsCollector:
    """Real-time performance metrics collection and analysis"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or str(Path.home() / ".claude" / "performance_metrics.db")
        self.db_lock = threading.RLock()
        self.collection_active = False
        self.collection_thread = None
        
        # Performance thresholds
        self.thresholds = {
            'cpu_usage': 80.0,           # CPU usage percentage
            'memory_usage': 85.0,        # Memory usage percentage  
            'disk_usage': 90.0,          # Disk usage percentage
            'tool_execution_time': 30.0, # Tool execution time seconds
            'hook_execution_time': 5.0,  # Hook execution time seconds
            'memory_leak_threshold': 100 * 1024 * 1024,  # 100MB
            'response_time_threshold': 10.0  # Response time seconds
        }
        
        # Metric aggregation windows
        self.windows = {
            'short': 300,    # 5 minutes
            'medium': 1800,  # 30 minutes
            'long': 3600     # 1 hour
        }
        
        # Alert handlers
        self.alert_handlers = []
        
        # Baseline metrics for comparison
        self.baseline_metrics = {}
        self.baseline_established = False
        
        # Initialize database
        self.init_database()
        
        # Start background collection
        self.start_collection()
        
        logger.info(f"Performance metrics collector initialized with database: {self.db_path}")
    
    def init_database(self):
        """Initialize performance metrics database"""
        
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with self.db_lock:
            conn = sqlite3.connect(self.db_path)
            
            # System metrics table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS system_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    cpu_usage REAL NOT NULL,
                    memory_usage REAL NOT NULL,
                    memory_available INTEGER NOT NULL,
                    disk_usage REAL NOT NULL,
                    disk_free INTEGER NOT NULL,
                    network_sent INTEGER NOT NULL,
                    network_recv INTEGER NOT NULL,
                    load_average TEXT NOT NULL,
                    process_count INTEGER NOT NULL,
                    thread_count INTEGER NOT NULL,
                    open_files INTEGER NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tool execution metrics table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS tool_execution_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tool_name TEXT NOT NULL,
                    start_time REAL NOT NULL,
                    end_time REAL NOT NULL,
                    execution_time REAL NOT NULL,
                    cpu_time REAL NOT NULL,
                    memory_peak INTEGER NOT NULL,
                    input_size INTEGER NOT NULL,
                    output_size INTEGER NOT NULL,
                    success BOOLEAN NOT NULL,
                    error_type TEXT,
                    thread_id TEXT,
                    session_id TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Hook performance metrics table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS hook_performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    hook_name TEXT NOT NULL,
                    hook_type TEXT NOT NULL,
                    execution_time REAL NOT NULL,
                    memory_usage INTEGER NOT NULL,
                    success BOOLEAN NOT NULL,
                    tool_name TEXT,
                    error_message TEXT,
                    timestamp REAL NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Performance alerts table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS performance_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    alert_id TEXT UNIQUE NOT NULL,
                    metric_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT NOT NULL,
                    threshold_value REAL NOT NULL,
                    current_value REAL NOT NULL,
                    timestamp REAL NOT NULL,
                    metadata TEXT,
                    acknowledged BOOLEAN DEFAULT FALSE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for performance
            conn.execute('CREATE INDEX IF NOT EXISTS idx_system_timestamp ON system_metrics(timestamp)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_tool_execution_time ON tool_execution_metrics(start_time)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_hook_timestamp ON hook_performance_metrics(timestamp)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON performance_alerts(timestamp)')
            
            conn.commit()
            conn.close()
    
    def start_collection(self):
        """Start background metrics collection"""
        
        if not self.collection_active:
            self.collection_active = True
            self.collection_thread = threading.Thread(target=self._collection_loop, daemon=True)
            self.collection_thread.start()
            logger.info("Background metrics collection started")
    
    def stop_collection(self):
        """Stop background metrics collection"""
        
        if self.collection_active:
            self.collection_active = False
            if self.collection_thread:
                self.collection_thread.join(timeout=5.0)
            logger.info("Background metrics collection stopped")
    
    def _collection_loop(self):
        """Background collection loop"""
        
        while self.collection_active:
            try:
                # Collect system metrics every 10 seconds
                system_metrics = self.collect_system_metrics()
                self.store_system_metrics(system_metrics)
                
                # Check for performance alerts
                self.check_performance_alerts(system_metrics)
                
                # Update baseline if needed
                if not self.baseline_established:
                    self.update_baseline_metrics()
                
                time.sleep(10)  # Collect every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in metrics collection loop: {e}")
                time.sleep(30)  # Wait longer on error
    
    def collect_system_metrics(self) -> SystemMetrics:
        """Collect current system metrics"""
        
        # CPU usage
        cpu_usage = psutil.cpu_percent(interval=1)
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_usage = memory.percent
        memory_available = memory.available
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_usage = (disk.used / disk.total) * 100
        disk_free = disk.free
        
        # Network I/O
        network = psutil.net_io_counters()
        network_sent = network.bytes_sent
        network_recv = network.bytes_recv
        
        # Load average
        try:
            load_average = list(psutil.getloadavg())
        except AttributeError:
            # Windows doesn't have load average
            load_average = [0.0, 0.0, 0.0]
        
        # Process information
        process_count = len(psutil.pids())
        
        # Thread count (estimate from current process)
        current_process = psutil.Process()
        thread_count = current_process.num_threads()
        
        # Open files (for current process)
        try:
            open_files = len(current_process.open_files())
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            open_files = 0
        
        return SystemMetrics(
            timestamp=time.time(),
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            memory_available=memory_available,
            disk_usage=disk_usage,
            disk_free=disk_free,
            network_sent=network_sent,
            network_recv=network_recv,
            load_average=load_average,
            process_count=process_count,
            thread_count=thread_count,
            open_files=open_files
        )
    
    def track_tool_execution(self, tool_name: str, start_time: float = None) -> 'ToolExecutionTracker':
        """Create a tool execution tracker"""
        return ToolExecutionTracker(self, tool_name, start_time)
    
    def track_hook_execution(self, hook_name: str, hook_type: str, tool_name: str = None) -> 'HookExecutionTracker':
        """Create a hook execution tracker"""
        return HookExecutionTracker(self, hook_name, hook_type, tool_name)
    
    def store_system_metrics(self, metrics: SystemMetrics):
        """Store system metrics in database"""
        
        with self.db_lock:
            conn = sqlite3.connect(self.db_path)
            conn.execute('''
                INSERT INTO system_metrics
                (timestamp, cpu_usage, memory_usage, memory_available, disk_usage,
                 disk_free, network_sent, network_recv, load_average, process_count,
                 thread_count, open_files)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metrics.timestamp,
                metrics.cpu_usage,
                metrics.memory_usage,
                metrics.memory_available,
                metrics.disk_usage,
                metrics.disk_free,
                metrics.network_sent,
                metrics.network_recv,
                json.dumps(metrics.load_average),
                metrics.process_count,
                metrics.thread_count,
                metrics.open_files
            ))
            conn.commit()
            conn.close()
    
    def store_tool_execution_metrics(self, metrics: ToolExecutionMetrics):
        """Store tool execution metrics"""
        
        with self.db_lock:
            conn = sqlite3.connect(self.db_path)
            conn.execute('''
                INSERT INTO tool_execution_metrics
                (tool_name, start_time, end_time, execution_time, cpu_time,
                 memory_peak, input_size, output_size, success, error_type,
                 thread_id, session_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metrics.tool_name,
                metrics.start_time,
                metrics.end_time,
                metrics.execution_time,
                metrics.cpu_time,
                metrics.memory_peak,
                metrics.input_size,
                metrics.output_size,
                metrics.success,
                metrics.error_type,
                metrics.thread_id,
                metrics.session_id
            ))
            conn.commit()
            conn.close()
    
    def store_hook_performance_metrics(self, metrics: HookPerformanceMetrics):
        """Store hook performance metrics"""
        
        with self.db_lock:
            conn = sqlite3.connect(self.db_path)
            conn.execute('''
                INSERT INTO hook_performance_metrics
                (hook_name, hook_type, execution_time, memory_usage, success,
                 tool_name, error_message, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metrics.hook_name,
                metrics.hook_type,
                metrics.execution_time,
                metrics.memory_usage,
                metrics.success,
                metrics.tool_name,
                metrics.error_message,
                metrics.timestamp or time.time()
            ))
            conn.commit()
            conn.close()
    
    def check_performance_alerts(self, metrics: SystemMetrics):
        """Check for performance threshold violations"""
        
        alerts = []
        
        # CPU usage alert
        if metrics.cpu_usage > self.thresholds['cpu_usage']:
            alerts.append(PerformanceAlert(
                alert_id=self._generate_alert_id(),
                metric_type=MetricType.SYSTEM,
                severity=MetricSeverity.WARNING if metrics.cpu_usage < 95 else MetricSeverity.CRITICAL,
                message=f"High CPU usage detected: {metrics.cpu_usage:.1f}%",
                threshold_value=self.thresholds['cpu_usage'],
                current_value=metrics.cpu_usage,
                timestamp=metrics.timestamp,
                metadata={'metric': 'cpu_usage'}
            ))
        
        # Memory usage alert
        if metrics.memory_usage > self.thresholds['memory_usage']:
            alerts.append(PerformanceAlert(
                alert_id=self._generate_alert_id(),
                metric_type=MetricType.SYSTEM,
                severity=MetricSeverity.WARNING if metrics.memory_usage < 95 else MetricSeverity.CRITICAL,
                message=f"High memory usage detected: {metrics.memory_usage:.1f}%",
                threshold_value=self.thresholds['memory_usage'],
                current_value=metrics.memory_usage,
                timestamp=metrics.timestamp,
                metadata={'metric': 'memory_usage'}
            ))
        
        # Disk usage alert
        if metrics.disk_usage > self.thresholds['disk_usage']:
            alerts.append(PerformanceAlert(
                alert_id=self._generate_alert_id(),
                metric_type=MetricType.SYSTEM,
                severity=MetricSeverity.CRITICAL,
                message=f"High disk usage detected: {metrics.disk_usage:.1f}%",
                threshold_value=self.thresholds['disk_usage'],
                current_value=metrics.disk_usage,
                timestamp=metrics.timestamp,
                metadata={'metric': 'disk_usage'}
            ))
        
        # Store and trigger alerts
        for alert in alerts:
            self.store_alert(alert)
            self.trigger_alert(alert)
    
    def get_performance_summary(self, window_seconds: int = 3600) -> Dict[str, Any]:
        """Get performance summary for specified time window"""
        
        start_time = time.time() - window_seconds
        
        with self.db_lock:
            conn = sqlite3.connect(self.db_path)
            
            # System metrics summary
            cursor = conn.execute('''
                SELECT AVG(cpu_usage), AVG(memory_usage), AVG(disk_usage),
                       MIN(memory_available), MIN(disk_free),
                       MAX(cpu_usage), MAX(memory_usage), COUNT(*)
                FROM system_metrics
                WHERE timestamp >= ?
            ''', (start_time,))
            
            system_stats = cursor.fetchone()
            
            # Tool execution summary
            cursor = conn.execute('''
                SELECT AVG(execution_time), MAX(execution_time), MIN(execution_time),
                       COUNT(*), SUM(CASE WHEN success THEN 1 ELSE 0 END)
                FROM tool_execution_metrics
                WHERE start_time >= ?
            ''', (start_time,))
            
            tool_stats = cursor.fetchone()
            
            # Hook performance summary
            cursor = conn.execute('''
                SELECT AVG(execution_time), MAX(execution_time), COUNT(*),
                       SUM(CASE WHEN success THEN 1 ELSE 0 END)
                FROM hook_performance_metrics
                WHERE timestamp >= ?
            ''', (start_time,))
            
            hook_stats = cursor.fetchone()
            
            # Recent alerts
            cursor = conn.execute('''
                SELECT COUNT(*), severity
                FROM performance_alerts
                WHERE timestamp >= ?
                GROUP BY severity
            ''', (start_time,))
            
            alert_counts = {row[1]: row[0] for row in cursor.fetchall()}
            
            conn.close()
        
        return {
            'time_window_seconds': window_seconds,
            'system_metrics': {
                'avg_cpu_usage': system_stats[0] or 0,
                'avg_memory_usage': system_stats[1] or 0,
                'avg_disk_usage': system_stats[2] or 0,
                'min_memory_available': system_stats[3] or 0,
                'min_disk_free': system_stats[4] or 0,
                'max_cpu_usage': system_stats[5] or 0,
                'max_memory_usage': system_stats[6] or 0,
                'sample_count': system_stats[7] or 0
            },
            'tool_execution': {
                'avg_execution_time': tool_stats[0] or 0,
                'max_execution_time': tool_stats[1] or 0,
                'min_execution_time': tool_stats[2] or 0,
                'total_executions': tool_stats[3] or 0,
                'successful_executions': tool_stats[4] or 0,
                'success_rate': (tool_stats[4] / tool_stats[3] * 100) if tool_stats[3] else 0
            },
            'hook_performance': {
                'avg_execution_time': hook_stats[0] or 0,
                'max_execution_time': hook_stats[1] or 0,
                'total_executions': hook_stats[2] or 0,
                'successful_executions': hook_stats[3] or 0,
                'success_rate': (hook_stats[3] / hook_stats[2] * 100) if hook_stats[2] else 0
            },
            'alerts': alert_counts,
            'summary_generated_at': time.time()
        }
    
    def update_baseline_metrics(self):
        """Update baseline metrics for comparison"""
        
        # Get recent system metrics for baseline
        summary = self.get_performance_summary(window_seconds=300)  # 5 minute window
        
        if summary['system_metrics']['sample_count'] >= 10:  # Need at least 10 samples
            self.baseline_metrics = {
                'cpu_usage': summary['system_metrics']['avg_cpu_usage'],
                'memory_usage': summary['system_metrics']['avg_memory_usage'],
                'disk_usage': summary['system_metrics']['avg_disk_usage'],
                'tool_execution_time': summary['tool_execution']['avg_execution_time'],
                'hook_execution_time': summary['hook_performance']['avg_execution_time'],
                'established_at': time.time()
            }
            self.baseline_established = True
            logger.info("Performance baseline established")
    
    def store_alert(self, alert: PerformanceAlert):
        """Store performance alert"""
        
        with self.db_lock:
            conn = sqlite3.connect(self.db_path)
            conn.execute('''
                INSERT INTO performance_alerts
                (alert_id, metric_type, severity, message, threshold_value,
                 current_value, timestamp, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                alert.alert_id,
                alert.metric_type.value,
                alert.severity.value,
                alert.message,
                alert.threshold_value,
                alert.current_value,
                alert.timestamp,
                json.dumps(alert.metadata or {})
            ))
            conn.commit()
            conn.close()
    
    def trigger_alert(self, alert: PerformanceAlert):
        """Trigger alert to handlers"""
        
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                logger.error(f"Alert handler failed: {e}")
        
        # Log alert
        if alert.severity == MetricSeverity.CRITICAL:
            logger.critical(f"Performance Alert: {alert.message}")
        elif alert.severity == MetricSeverity.WARNING:
            logger.warning(f"Performance Alert: {alert.message}")
        else:
            logger.info(f"Performance Alert: {alert.message}")
    
    def add_alert_handler(self, handler):
        """Add alert handler function"""
        self.alert_handlers.append(handler)
    
    def cleanup_old_metrics(self, retention_days: int = 7):
        """Clean up old metrics beyond retention period"""
        
        cutoff_time = time.time() - (retention_days * 24 * 3600)
        
        with self.db_lock:
            conn = sqlite3.connect(self.db_path)
            
            # Clean up old metrics
            conn.execute('DELETE FROM system_metrics WHERE timestamp < ?', (cutoff_time,))
            conn.execute('DELETE FROM tool_execution_metrics WHERE start_time < ?', (cutoff_time,))
            conn.execute('DELETE FROM hook_performance_metrics WHERE timestamp < ?', (cutoff_time,))
            conn.execute('DELETE FROM performance_alerts WHERE timestamp < ?', (cutoff_time,))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Cleaned up metrics older than {retention_days} days")
    
    def _generate_alert_id(self) -> str:
        """Generate unique alert ID"""
        import uuid
        return f"perf_{int(time.time())}_{uuid.uuid4().hex[:8]}"

class ToolExecutionTracker:
    """Context manager for tracking tool execution performance"""
    
    def __init__(self, collector: MetricsCollector, tool_name: str, start_time: float = None):
        self.collector = collector
        self.tool_name = tool_name
        self.start_time = start_time or time.time()
        self.process = psutil.Process()
        self.initial_memory = self.process.memory_info().rss
        self.success = True
        self.error_type = None
        self.input_size = 0
        self.output_size = 0
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.success = False
            self.error_type = exc_type.__name__
        
        self.record_completion()
    
    def set_input_size(self, size: int):
        """Set input data size"""
        self.input_size = size
    
    def set_output_size(self, size: int):
        """Set output data size"""
        self.output_size = size
    
    def record_completion(self):
        """Record tool execution completion"""
        
        end_time = time.time()
        execution_time = end_time - self.start_time
        
        try:
            current_memory = self.process.memory_info().rss
            memory_peak = max(current_memory, self.initial_memory)
            cpu_time = sum(self.process.cpu_times()[:2])  # user + system time
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            memory_peak = self.initial_memory
            cpu_time = 0.0
        
        metrics = ToolExecutionMetrics(
            tool_name=self.tool_name,
            start_time=self.start_time,
            end_time=end_time,
            execution_time=execution_time,
            cpu_time=cpu_time,
            memory_peak=memory_peak,
            input_size=self.input_size,
            output_size=self.output_size,
            success=self.success,
            error_type=self.error_type,
            thread_id=str(threading.current_thread().ident),
            session_id=None  # Could be set from context
        )
        
        self.collector.store_tool_execution_metrics(metrics)
        
        # Check for performance alerts
        if execution_time > self.collector.thresholds['tool_execution_time']:
            alert = PerformanceAlert(
                alert_id=self.collector._generate_alert_id(),
                metric_type=MetricType.TOOL_EXECUTION,
                severity=MetricSeverity.WARNING,
                message=f"Slow tool execution: {self.tool_name} took {execution_time:.2f}s",
                threshold_value=self.collector.thresholds['tool_execution_time'],
                current_value=execution_time,
                timestamp=end_time,
                metadata={'tool_name': self.tool_name}
            )
            self.collector.store_alert(alert)
            self.collector.trigger_alert(alert)

class HookExecutionTracker:
    """Context manager for tracking hook execution performance"""
    
    def __init__(self, collector: MetricsCollector, hook_name: str, hook_type: str, tool_name: str = None):
        self.collector = collector
        self.hook_name = hook_name
        self.hook_type = hook_type
        self.tool_name = tool_name
        self.start_time = time.time()
        self.process = psutil.Process()
        self.initial_memory = self.process.memory_info().rss
        self.success = True
        self.error_message = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.success = False
            self.error_message = str(exc_val)
        
        self.record_completion()
    
    def record_completion(self):
        """Record hook execution completion"""
        
        end_time = time.time()
        execution_time = end_time - self.start_time
        
        try:
            current_memory = self.process.memory_info().rss
            memory_usage = current_memory - self.initial_memory
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            memory_usage = 0
        
        metrics = HookPerformanceMetrics(
            hook_name=self.hook_name,
            hook_type=self.hook_type,
            execution_time=execution_time,
            memory_usage=memory_usage,
            success=self.success,
            tool_name=self.tool_name,
            error_message=self.error_message,
            timestamp=end_time
        )
        
        self.collector.store_hook_performance_metrics(metrics)
        
        # Check for performance alerts
        if execution_time > self.collector.thresholds['hook_execution_time']:
            alert = PerformanceAlert(
                alert_id=self.collector._generate_alert_id(),
                metric_type=MetricType.HOOK_PERFORMANCE,
                severity=MetricSeverity.WARNING,
                message=f"Slow hook execution: {self.hook_name} took {execution_time:.2f}s",
                threshold_value=self.collector.thresholds['hook_execution_time'],
                current_value=execution_time,
                timestamp=end_time,
                metadata={'hook_name': self.hook_name, 'hook_type': self.hook_type}
            )
            self.collector.store_alert(alert)
            self.collector.trigger_alert(alert)

# Example usage and testing
def test_metrics_collector():
    """Test the metrics collector functionality"""
    
    import tempfile
    import os
    
    # Create temporary database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
        db_path = temp_db.name
    
    try:
        print("🧪 Testing Performance Metrics Collector...")
        
        collector = MetricsCollector(db_path)
        
        # Test system metrics collection
        print("📊 Collecting system metrics...")
        system_metrics = collector.collect_system_metrics()
        print(f"   CPU: {system_metrics.cpu_usage:.1f}%")
        print(f"   Memory: {system_metrics.memory_usage:.1f}%")
        print(f"   Disk: {system_metrics.disk_usage:.1f}%")
        
        # Test tool execution tracking
        print("🔧 Testing tool execution tracking...")
        with collector.track_tool_execution("test_tool") as tracker:
            tracker.set_input_size(1024)
            time.sleep(0.1)  # Simulate work
            tracker.set_output_size(2048)
        print("   ✅ Tool execution tracked")
        
        # Test hook execution tracking
        print("🪝 Testing hook execution tracking...")
        with collector.track_hook_execution("test_hook", "PreToolUse", "test_tool"):
            time.sleep(0.05)  # Simulate hook work
        print("   ✅ Hook execution tracked")
        
        # Get performance summary
        print("📈 Getting performance summary...")
        summary = collector.get_performance_summary(window_seconds=60)
        print(f"   Tool executions: {summary['tool_execution']['total_executions']}")
        print(f"   Hook executions: {summary['hook_performance']['total_executions']}")
        print(f"   Success rate: {summary['tool_execution']['success_rate']:.1f}%")
        
        # Stop collection
        collector.stop_collection()
        
        print("✅ Performance metrics collector test completed!")
        
    finally:
        # Cleanup
        if os.path.exists(db_path):
            os.unlink(db_path)

if __name__ == "__main__":
    test_metrics_collector()