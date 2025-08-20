#!/usr/bin/env python3
"""
Simple System Monitor - Phase 1 Implementation
Essential metrics collection with <5% CPU overhead, <50MB RAM
"""
import psutil
import time
import json
import sqlite3
import subprocess
import asyncio
import logging
from pathlib import Path

class SimpleSystemMonitor:
    def __init__(self):
        self.db_path = '.claude/monitoring/monitoring.db'
        self.dashboard_data_path = '.claude/monitoring/dashboard_data.json'
        self.init_database()
        
        # Alert thresholds (from spec)
        self.thresholds = {
            'cpu_critical': 85.0,
            'memory_critical': 90.0,
            'disk_critical': 95.0,
            'mcp_servers_min': 7
        }
        
        # Configure logging
        logging.basicConfig(
            filename='.claude/monitoring/system_monitor.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def init_database(self):
        """Initialize monitoring database"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        
        # System metrics table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS system_metrics (
                timestamp REAL,
                cpu_percent REAL,
                memory_percent REAL,
                disk_percent REAL,
                active_processes INTEGER,
                mcp_server_count INTEGER
            )
        ''')
        
        # Alerts table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                timestamp REAL,
                alert_type TEXT,
                value REAL,
                action_taken TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def collect_metrics(self):
        """Collect essential system metrics"""
        try:
            metrics = {
                'timestamp': time.time(),
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
                'active_processes': len(psutil.pids()),
                'mcp_server_count': self.count_mcp_servers()
            }
            return metrics
        except Exception as e:
            self.logger.error(f"Failed to collect metrics: {e}")
            return {
                'timestamp': time.time(),
                'cpu_percent': 0,
                'memory_percent': 0,
                'disk_percent': 0,
                'active_processes': 0,
                'mcp_server_count': 0
            }
    
    def count_mcp_servers(self):
        """Count active MCP servers"""
        try:
            # Simple process count for MCP servers
            result = subprocess.run(
                ['pgrep', '-f', 'mcp'],
                capture_output=True,
                timeout=5,
                text=True
            )
            if result.returncode == 0:
                return len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
            return 0
        except Exception:
            return 0
    
    def store_metrics(self, metrics):
        """Store metrics in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute('''
                INSERT INTO system_metrics VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                metrics['timestamp'],
                metrics['cpu_percent'],
                metrics['memory_percent'],
                metrics['disk_percent'],
                metrics['active_processes'],
                metrics['mcp_server_count']
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            self.logger.error(f"Failed to store metrics: {e}")
    
    def check_alerts(self, metrics):
        """Check for alert conditions"""
        alerts = []
        
        if metrics['cpu_percent'] > self.thresholds['cpu_critical']:
            alerts.append({
                'type': 'cpu_critical',
                'value': metrics['cpu_percent'],
                'action': 'log_alert'
            })
        
        if metrics['memory_percent'] > self.thresholds['memory_critical']:
            alerts.append({
                'type': 'memory_critical',
                'value': metrics['memory_percent'],
                'action': 'clear_caches'
            })
        
        if metrics['disk_percent'] > self.thresholds['disk_critical']:
            alerts.append({
                'type': 'disk_critical',
                'value': metrics['disk_percent'],
                'action': 'cleanup_disk'
            })
        
        if metrics['mcp_server_count'] < self.thresholds['mcp_servers_min']:
            alerts.append({
                'type': 'mcp_servers_low',
                'value': metrics['mcp_server_count'],
                'action': 'check_mcp_health'
            })
        
        return alerts
    
    async def handle_alert(self, alert):
        """Handle alerts with safe autonomous actions"""
        try:
            action_taken = "none"
            
            if alert['type'] == 'memory_critical':
                action_taken = await self.clear_caches()
            elif alert['type'] == 'disk_critical':
                action_taken = await self.cleanup_disk()
            elif alert['type'] == 'cpu_critical':
                action_taken = f"logged CPU critical: {alert['value']:.1f}%"
                self.logger.warning(f"CPU critical: {alert['value']:.1f}% - manual review recommended")
            elif alert['type'] == 'mcp_servers_low':
                action_taken = f"logged MCP servers low: {alert['value']}"
                self.logger.warning(f"MCP servers low: {alert['value']} - coordination may be affected")
            
            # Log alert to database
            self.log_alert(alert, action_taken)
            
        except Exception as e:
            self.logger.error(f"Alert handling failed: {e}")
    
    async def clear_caches(self):
        """Safe cache clearing"""
        try:
            cache_dirs = [
                '.claude/cache',
                '.claude/logs/old',
                '/tmp/claude-*'
            ]
            
            cleared = []
            for cache_dir in cache_dirs:
                cache_path = Path(cache_dir)
                if cache_path.exists():
                    subprocess.run(['rm', '-rf', str(cache_path)], timeout=30)
                    cleared.append(cache_dir)
            
            action_msg = f"Cleared caches: {', '.join(cleared)}" if cleared else "No caches to clear"
            self.logger.info(action_msg)
            return action_msg
            
        except Exception as e:
            self.logger.error(f"Cache clear failed: {e}")
            return f"Cache clear failed: {e}"
    
    async def cleanup_disk(self):
        """Safe log cleanup (files older than 7 days)"""
        try:
            log_dirs = ['.claude/logs', '.claude/monitoring']
            cleaned = []
            
            for log_dir in log_dirs:
                if Path(log_dir).exists():
                    # Clean old log files
                    result = subprocess.run([
                        'find', log_dir, '-name', '*.log',
                        '-mtime', '+7', '-delete'
                    ], timeout=60, capture_output=True)
                    
                    if result.returncode == 0:
                        cleaned.append(log_dir)
            
            action_msg = f"Cleaned old logs in: {', '.join(cleaned)}" if cleaned else "No old logs to clean"
            self.logger.info(action_msg)
            return action_msg
            
        except Exception as e:
            self.logger.error(f"Disk cleanup failed: {e}")
            return f"Disk cleanup failed: {e}"
    
    def log_alert(self, alert, action_taken):
        """Log alert to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute('''
                INSERT INTO alerts VALUES (?, ?, ?, ?)
            ''', (
                time.time(),
                alert['type'],
                alert['value'],
                action_taken
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            self.logger.error(f"Failed to log alert: {e}")
    
    def update_dashboard_data(self, metrics):
        """Update dashboard data file"""
        try:
            # Get recent alerts
            conn = sqlite3.connect(self.db_path)
            recent_alerts = conn.execute('''
                SELECT alert_type, value, action_taken, timestamp 
                FROM alerts 
                WHERE timestamp > ? 
                ORDER BY timestamp DESC LIMIT 5
            ''', (time.time() - 3600,)).fetchall()
            conn.close()
            
            dashboard_data = {
                'timestamp': metrics['timestamp'],
                'system_health': {
                    'cpu_percent': round(metrics['cpu_percent'], 1),
                    'memory_percent': round(metrics['memory_percent'], 1),
                    'disk_percent': round(metrics['disk_percent'], 1),
                    'mcp_servers': metrics['mcp_server_count'],
                    'processes': metrics['active_processes']
                },
                'status': self.determine_overall_status(metrics),
                'recent_alerts': [
                    {
                        'type': alert[0],
                        'value': alert[1],
                        'action': alert[2],
                        'time': alert[3]
                    } for alert in recent_alerts
                ]
            }
            
            # Write dashboard data
            with open(self.dashboard_data_path, 'w') as f:
                json.dump(dashboard_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to update dashboard data: {e}")
    
    def determine_overall_status(self, metrics):
        """Determine overall system status"""
        if (metrics['cpu_percent'] > 85 or 
            metrics['memory_percent'] > 90 or 
            metrics['disk_percent'] > 95 or 
            metrics['mcp_server_count'] < 7):
            return 'critical'
        elif (metrics['cpu_percent'] > 70 or 
              metrics['memory_percent'] > 75 or 
              metrics['disk_percent'] > 80):
            return 'warning'
        else:
            return 'healthy'
    
    async def monitoring_loop(self):
        """Main monitoring loop"""
        self.logger.info("Starting system monitoring")
        
        while True:
            try:
                # Collect metrics
                metrics = self.collect_metrics()
                
                # Store in database
                self.store_metrics(metrics)
                
                # Check for alerts
                alerts = self.check_alerts(metrics)
                
                # Handle alerts
                for alert in alerts:
                    await self.handle_alert(alert)
                
                # Update dashboard data
                self.update_dashboard_data(metrics)
                
                # Log status
                if metrics['cpu_percent'] > 70 or metrics['memory_percent'] > 75:
                    self.logger.info(f"System status: CPU {metrics['cpu_percent']:.1f}%, Memory {metrics['memory_percent']:.1f}%")
                
                # Sleep for 30 seconds
                await asyncio.sleep(30)
                
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(60)  # Longer sleep on error

async def main():
    """Main function for running the monitor"""
    monitor = SimpleSystemMonitor()
    await monitor.monitoring_loop()

if __name__ == '__main__':
    asyncio.run(main())