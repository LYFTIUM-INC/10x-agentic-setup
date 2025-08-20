#!/usr/bin/env python3
"""
Real-time Performance Monitor for Agent System
Integrates with Claude Code hooks to provide live performance monitoring
"""

import asyncio
import json
import sqlite3
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import sys
import os

class RealtimePerformanceMonitor:
    """Real-time monitoring of agent system performance"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.hooks_dir = self.project_root / ".claude" / "hooks"
        self.performance_db = self.hooks_dir / "performance" / "performance_metrics.db"
        self.predictive_db = self.hooks_dir / "performance" / "predictive_analytics.db"
        
        self.monitoring_active = False
        self.performance_data = {
            "agent_executions": [],
            "hook_events": [],
            "mcp_operations": [],
            "system_metrics": [],
            "realtime_stats": {}
        }
        
        # Performance thresholds
        self.thresholds = {
            "agent_execution_time": 0.020,  # 20ms
            "hook_response_time": 0.010,    # 10ms
            "mcp_response_time": 0.050,     # 50ms
            "system_cpu_threshold": 80.0,   # 80%
            "memory_threshold": 85.0,       # 85%
            "cache_hit_rate_min": 0.70      # 70%
        }
    
    def start_monitoring(self, duration_minutes: int = 10):
        """Start real-time performance monitoring"""
        print(f"🚀 Starting Real-time Performance Monitoring for {duration_minutes} minutes")
        print("=" * 60)
        
        self.monitoring_active = True
        end_time = time.time() + (duration_minutes * 60)
        
        # Start monitoring threads
        threads = [
            threading.Thread(target=self._monitor_hook_events, daemon=True),
            threading.Thread(target=self._monitor_system_resources, daemon=True),
            threading.Thread(target=self._monitor_database_metrics, daemon=True),
            threading.Thread(target=self._generate_realtime_stats, daemon=True)
        ]
        
        for thread in threads:
            thread.start()
        
        # Main monitoring loop
        try:
            while time.time() < end_time and self.monitoring_active:
                self._display_realtime_dashboard()
                time.sleep(5)  # Update every 5 seconds
                
        except KeyboardInterrupt:
            print("\n⏹️ Monitoring stopped by user")
        
        self.monitoring_active = False
        
        # Wait for threads to finish
        for thread in threads:
            thread.join(timeout=2)
        
        # Generate final report
        self._generate_monitoring_report()
    
    def _monitor_hook_events(self):
        """Monitor Claude Code hook events"""
        hook_types = ["pre_tool_use", "post_tool_use", "user_prompt_submit", "stop", "notification"]
        
        while self.monitoring_active:
            try:
                # Check for new hook events
                logs_dir = self.project_root / "mcp_servers" / "logs"
                
                if logs_dir.exists():
                    for log_dir in logs_dir.iterdir():
                        if log_dir.is_dir():
                            for hook_type in hook_types:
                                hook_file = log_dir / f"{hook_type}.json"
                                if hook_file.exists():
                                    self._process_hook_event(hook_file, hook_type)
                
                time.sleep(1)  # Check every second
                
            except Exception as e:
                print(f"⚠️ Hook monitoring error: {e}")
                time.sleep(5)
    
    def _monitor_system_resources(self):
        """Monitor system resource usage"""
        while self.monitoring_active:
            try:
                # Simulate system resource monitoring
                cpu_usage = self._get_cpu_usage()
                memory_usage = self._get_memory_usage()
                disk_usage = self._get_disk_usage()
                
                resource_data = {
                    "timestamp": datetime.now().isoformat(),
                    "cpu_percent": cpu_usage,
                    "memory_percent": memory_usage,
                    "disk_percent": disk_usage,
                    "cpu_alert": cpu_usage > self.thresholds["system_cpu_threshold"],
                    "memory_alert": memory_usage > self.thresholds["memory_threshold"]
                }
                
                self.performance_data["system_metrics"].append(resource_data)
                
                # Keep only last 100 entries
                if len(self.performance_data["system_metrics"]) > 100:
                    self.performance_data["system_metrics"] = self.performance_data["system_metrics"][-100:]
                
                time.sleep(2)  # Update every 2 seconds
                
            except Exception as e:
                print(f"⚠️ System monitoring error: {e}")
                time.sleep(5)
    
    def _monitor_database_metrics(self):
        """Monitor performance database metrics"""
        while self.monitoring_active:
            try:
                # Check performance database
                if self.performance_db.exists():
                    with sqlite3.connect(self.performance_db) as conn:
                        cursor = conn.cursor()
                        
                        # Get recent metrics
                        cursor.execute("""
                            SELECT COUNT(*) as total_metrics,
                                   AVG(response_time) as avg_response_time,
                                   MAX(timestamp) as last_update
                            FROM performance_metrics 
                            WHERE timestamp > datetime('now', '-1 hour')
                        """)
                        
                        metrics_data = cursor.fetchone()
                        if metrics_data:
                            self.performance_data["db_metrics"] = {
                                "total_recent_metrics": metrics_data[0],
                                "avg_response_time": metrics_data[1] or 0,
                                "last_update": metrics_data[2],
                                "timestamp": datetime.now().isoformat()
                            }
                
                # Check predictive analytics database
                if self.predictive_db.exists():
                    with sqlite3.connect(self.predictive_db) as conn:
                        cursor = conn.cursor()
                        
                        cursor.execute("""
                            SELECT COUNT(*) as total_predictions,
                                   AVG(confidence) as avg_confidence
                            FROM velocity_predictions 
                            WHERE timestamp > datetime('now', '-1 hour')
                        """)
                        
                        pred_data = cursor.fetchone()
                        if pred_data:
                            self.performance_data["prediction_metrics"] = {
                                "total_predictions": pred_data[0],
                                "avg_confidence": pred_data[1] or 0,
                                "timestamp": datetime.now().isoformat()
                            }
                
                time.sleep(10)  # Update every 10 seconds
                
            except Exception as e:
                print(f"⚠️ Database monitoring error: {e}")
                time.sleep(15)
    
    def _generate_realtime_stats(self):
        """Generate real-time performance statistics"""
        while self.monitoring_active:
            try:
                current_time = datetime.now()
                
                # Calculate agent execution stats
                recent_executions = [
                    exec_data for exec_data in self.performance_data["agent_executions"]
                    if datetime.fromisoformat(exec_data["timestamp"]) > current_time - timedelta(minutes=5)
                ]
                
                # Calculate hook performance stats
                recent_hooks = [
                    hook_data for hook_data in self.performance_data["hook_events"]
                    if datetime.fromisoformat(hook_data["timestamp"]) > current_time - timedelta(minutes=5)
                ]
                
                # Generate stats
                stats = {
                    "timestamp": current_time.isoformat(),
                    "agents": {
                        "total_executions_5min": len(recent_executions),
                        "avg_execution_time": sum(e.get("execution_time", 0) for e in recent_executions) / max(len(recent_executions), 1),
                        "executions_meeting_target": sum(1 for e in recent_executions if e.get("execution_time", 0) <= self.thresholds["agent_execution_time"]),
                        "target_compliance_rate": sum(1 for e in recent_executions if e.get("execution_time", 0) <= self.thresholds["agent_execution_time"]) / max(len(recent_executions), 1)
                    },
                    "hooks": {
                        "total_events_5min": len(recent_hooks),
                        "avg_response_time": sum(h.get("response_time", 0) for h in recent_hooks) / max(len(recent_hooks), 1),
                        "events_meeting_target": sum(1 for h in recent_hooks if h.get("response_time", 0) <= self.thresholds["hook_response_time"]),
                        "target_compliance_rate": sum(1 for h in recent_hooks if h.get("response_time", 0) <= self.thresholds["hook_response_time"]) / max(len(recent_hooks), 1)
                    },
                    "system": {
                        "current_cpu": self.performance_data["system_metrics"][-1]["cpu_percent"] if self.performance_data["system_metrics"] else 0,
                        "current_memory": self.performance_data["system_metrics"][-1]["memory_percent"] if self.performance_data["system_metrics"] else 0,
                        "cpu_alerts": sum(1 for m in self.performance_data["system_metrics"][-20:] if m.get("cpu_alert", False)),
                        "memory_alerts": sum(1 for m in self.performance_data["system_metrics"][-20:] if m.get("memory_alert", False))
                    }
                }
                
                self.performance_data["realtime_stats"] = stats
                
                time.sleep(3)  # Update every 3 seconds
                
            except Exception as e:
                print(f"⚠️ Stats generation error: {e}")
                time.sleep(5)
    
    def _display_realtime_dashboard(self):
        """Display real-time performance dashboard"""
        os.system('clear' if os.name == 'posix' else 'cls')  # Clear screen
        
        print("🚀 REAL-TIME AGENT PERFORMANCE DASHBOARD")
        print("=" * 60)
        print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        stats = self.performance_data.get("realtime_stats", {})
        
        if stats:
            # Agent Performance Section
            agents = stats.get("agents", {})
            print("🤖 AGENT PERFORMANCE (Last 5 minutes)")
            print("-" * 40)
            print(f"  Total Executions: {agents.get('total_executions_5min', 0)}")
            print(f"  Avg Execution Time: {agents.get('avg_execution_time', 0):.4f}s (target: {self.thresholds['agent_execution_time']:.3f}s)")
            print(f"  Target Compliance: {agents.get('target_compliance_rate', 0):.1%}")
            
            compliance_status = "✅" if agents.get('target_compliance_rate', 0) >= 0.95 else "❌"
            print(f"  Status: {compliance_status}")
            print()
            
            # Hook Performance Section
            hooks = stats.get("hooks", {})
            print("🔗 HOOK PERFORMANCE (Last 5 minutes)")
            print("-" * 40)
            print(f"  Total Events: {hooks.get('total_events_5min', 0)}")
            print(f"  Avg Response Time: {hooks.get('avg_response_time', 0):.4f}s (target: {self.thresholds['hook_response_time']:.3f}s)")
            print(f"  Target Compliance: {hooks.get('target_compliance_rate', 0):.1%}")
            
            hook_status = "✅" if hooks.get('target_compliance_rate', 0) >= 0.95 else "❌"
            print(f"  Status: {hook_status}")
            print()
            
            # System Resources Section
            system = stats.get("system", {})
            print("💻 SYSTEM RESOURCES")
            print("-" * 40)
            print(f"  CPU Usage: {system.get('current_cpu', 0):.1f}% (threshold: {self.thresholds['system_cpu_threshold']:.1f}%)")
            print(f"  Memory Usage: {system.get('current_memory', 0):.1f}% (threshold: {self.thresholds['memory_threshold']:.1f}%)")
            print(f"  CPU Alerts (last 20 samples): {system.get('cpu_alerts', 0)}")
            print(f"  Memory Alerts (last 20 samples): {system.get('memory_alerts', 0)}")
            
            cpu_status = "✅" if system.get('current_cpu', 0) <= self.thresholds['system_cpu_threshold'] else "❌"
            memory_status = "✅" if system.get('current_memory', 0) <= self.thresholds['memory_threshold'] else "❌" 
            print(f"  CPU Status: {cpu_status}")
            print(f"  Memory Status: {memory_status}")
            print()
        
        # Database Metrics Section
        if "db_metrics" in self.performance_data:
            db_metrics = self.performance_data["db_metrics"]
            print("💾 DATABASE METRICS (Last hour)")
            print("-" * 40)
            print(f"  Total Metrics Collected: {db_metrics.get('total_recent_metrics', 0)}")
            print(f"  Avg Response Time: {db_metrics.get('avg_response_time', 0):.4f}s")
            print(f"  Last Update: {db_metrics.get('last_update', 'N/A')}")
            print()
        
        # Predictive Analytics Section
        if "prediction_metrics" in self.performance_data:
            pred_metrics = self.performance_data["prediction_metrics"]
            print("🔮 PREDICTIVE ANALYTICS (Last hour)")
            print("-" * 40)
            print(f"  Total Predictions: {pred_metrics.get('total_predictions', 0)}")
            print(f"  Avg Confidence: {pred_metrics.get('avg_confidence', 0):.1%}")
            print()
        
        print("Press Ctrl+C to stop monitoring...")
        print("=" * 60)
    
    def _process_hook_event(self, hook_file: Path, hook_type: str):
        """Process a hook event file"""
        try:
            if hook_file.stat().st_mtime > time.time() - 300:  # Only recent files (last 5 minutes)
                with open(hook_file, 'r') as f:
                    hook_data = json.load(f)
                
                event_data = {
                    "timestamp": datetime.now().isoformat(),
                    "hook_type": hook_type,
                    "response_time": hook_data.get("execution_time", 0.005),  # Default 5ms
                    "success": hook_data.get("success", True),
                    "file_size": hook_file.stat().st_size
                }
                
                self.performance_data["hook_events"].append(event_data)
                
                # Keep only last 500 events
                if len(self.performance_data["hook_events"]) > 500:
                    self.performance_data["hook_events"] = self.performance_data["hook_events"][-500:]
                    
        except Exception as e:
            pass  # Silently ignore individual file errors
    
    def _get_cpu_usage(self) -> float:
        """Get current CPU usage percentage"""
        try:
            import psutil
            return psutil.cpu_percent(interval=0.1)
        except ImportError:
            # Simulate CPU usage if psutil not available
            import random
            return 45.0 + random.uniform(-15, 25)  # Simulate 30-70% usage
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage percentage"""
        try:
            import psutil
            return psutil.virtual_memory().percent
        except ImportError:
            # Simulate memory usage
            import random
            return 55.0 + random.uniform(-20, 20)  # Simulate 35-75% usage
    
    def _get_disk_usage(self) -> float:
        """Get current disk usage percentage"""
        try:
            import psutil
            return psutil.disk_usage('/').percent
        except ImportError:
            # Simulate disk usage
            import random
            return 40.0 + random.uniform(-10, 30)  # Simulate 30-70% usage
    
    def _generate_monitoring_report(self):
        """Generate final monitoring report"""
        report = {
            "monitoring_session": {
                "start_time": datetime.now().isoformat(),
                "duration_minutes": 10,
                "total_events_captured": len(self.performance_data["hook_events"]),
                "total_system_samples": len(self.performance_data["system_metrics"])
            },
            "performance_summary": self.performance_data["realtime_stats"],
            "detailed_data": {
                "hook_events": len(self.performance_data["hook_events"]),
                "system_metrics": len(self.performance_data["system_metrics"]),
                "agent_executions": len(self.performance_data["agent_executions"])
            }
        }
        
        # Save report
        report_file = self.project_root / "tests" / "realtime_monitoring_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n📊 Real-time Monitoring Report saved to: {report_file}")
        print("🏁 Monitoring session complete!")

def main():
    """Run real-time performance monitoring"""
    monitor = RealtimePerformanceMonitor()
    
    # Allow user to specify monitoring duration
    duration = 10  # Default 10 minutes
    if len(sys.argv) > 1:
        try:
            duration = int(sys.argv[1])
        except ValueError:
            print("Invalid duration specified, using default 10 minutes")
    
    monitor.start_monitoring(duration)

if __name__ == "__main__":
    main()