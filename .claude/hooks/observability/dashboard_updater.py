#!/usr/bin/env python3
"""
Claude Code Hooks - Real-Time Observability Dashboard
Updates real-time dashboard with hook events and system metrics
"""

import os
import json
import time
import psutil
import sqlite3
import logging
import asyncio
import websockets
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('dashboard_updater')

@dataclass
class SystemMetrics:
    timestamp: str
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    disk_usage_percent: float
    network_sent_mb: float
    network_recv_mb: float
    active_processes: int

@dataclass
class HookEvent:
    session_id: str
    timestamp: str
    hook_event: str
    tool_name: str
    execution_time: Optional[float]
    success: bool
    metadata: Dict[str, Any]

class DashboardUpdater:
    """Real-time observability dashboard updater"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.session_id = os.environ.get('CLAUDE_SESSION_ID', 'unknown')
        self.dashboard_db = self.project_root / '.claude' / 'dashboard.db'
        self.websocket_port = int(os.environ.get('DASHBOARD_WS_PORT', '8080'))
        self.websocket_url = f"ws://localhost:{self.websocket_port}/ws"
        
        # Performance tracking
        self.start_time = time.time()
        self.event_count = 0
        self.last_metrics_time = time.time()
        
        self.init_database()
    
    def init_database(self):
        """Initialize dashboard database"""
        
        self.dashboard_db.parent.mkdir(exist_ok=True)
        
        with sqlite3.connect(self.dashboard_db) as conn:
            # Hook events table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS hook_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    timestamp TEXT,
                    hook_event TEXT,
                    tool_name TEXT,
                    execution_time REAL,
                    success BOOLEAN,
                    metadata TEXT,
                    displayed BOOLEAN DEFAULT FALSE
                )
            """)
            
            # System metrics table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS system_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    cpu_percent REAL,
                    memory_percent REAL,
                    memory_used_mb REAL,
                    disk_usage_percent REAL,
                    network_sent_mb REAL,
                    network_recv_mb REAL,
                    active_processes INTEGER
                )
            """)
            
            # Session state table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS session_state (
                    session_id TEXT PRIMARY KEY,
                    start_time TEXT,
                    last_activity TEXT,
                    total_events INTEGER,
                    active_hooks TEXT,
                    mcp_servers_status TEXT,
                    current_operations TEXT,
                    performance_summary TEXT
                )
            """)
            
            # MCP server status table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS mcp_server_status (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    server_name TEXT,
                    status TEXT,
                    response_time REAL,
                    last_operation TEXT,
                    error_count INTEGER
                )
            """)
    
    def update_dashboard(self):
        """Update dashboard with current hook event and system state"""
        
        try:
            # Collect current event data
            event_data = self._collect_event_data()
            
            # Collect system metrics
            system_metrics = self._collect_system_metrics()
            
            # Update database
            self._store_event_data(event_data)
            self._store_system_metrics(system_metrics)
            self._update_session_state(event_data)
            
            # Send to real-time dashboard
            self._send_to_dashboard(event_data, system_metrics)
            
            # Generate dashboard HTML if needed
            self._update_dashboard_html()
            
            # Performance tracking
            self.event_count += 1
            
            logger.info(f"Dashboard updated: {event_data['hook_event']} - {event_data['tool_name']}")
            
        except Exception as e:
            logger.error(f"Dashboard update failed: {e}")
    
    def _collect_event_data(self) -> HookEvent:
        """Collect current hook event data"""
        
        hook_event = os.environ.get('CLAUDE_HOOK_EVENT_NAME', 'Unknown')
        tool_name = os.environ.get('CLAUDE_TOOL_NAME', 'Unknown')
        execution_time = self._calculate_execution_time()
        
        # Extract metadata from environment
        metadata = {
            'file_paths': os.environ.get('CLAUDE_FILE_PATHS', '').split(',') if os.environ.get('CLAUDE_FILE_PATHS') else [],
            'tool_arguments': os.environ.get('CLAUDE_TOOL_ARGUMENTS', '{}'),
            'tool_response': os.environ.get('CLAUDE_TOOL_RESPONSE', ''),
            'session_duration': time.time() - self.start_time,
            'event_sequence': self.event_count + 1
        }
        
        # Determine success based on hook event and environment
        success = self._determine_operation_success(hook_event, metadata)
        
        return HookEvent(
            session_id=self.session_id,
            timestamp=datetime.now().isoformat(),
            hook_event=hook_event,
            tool_name=tool_name,
            execution_time=execution_time,
            success=success,
            metadata=metadata
        )
    
    def _collect_system_metrics(self) -> SystemMetrics:
        """Collect current system performance metrics"""
        
        # CPU and Memory
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_used_mb = memory.used / (1024 * 1024)
        
        # Disk usage for project directory
        disk_usage = psutil.disk_usage(str(self.project_root))
        disk_usage_percent = (disk_usage.used / disk_usage.total) * 100
        
        # Network I/O
        network = psutil.net_io_counters()
        network_sent_mb = network.bytes_sent / (1024 * 1024)
        network_recv_mb = network.bytes_recv / (1024 * 1024)
        
        # Active processes
        active_processes = len(psutil.pids())
        
        return SystemMetrics(
            timestamp=datetime.now().isoformat(),
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            memory_used_mb=memory_used_mb,
            disk_usage_percent=disk_usage_percent,
            network_sent_mb=network_sent_mb,
            network_recv_mb=network_recv_mb,
            active_processes=active_processes
        )
    
    def _calculate_execution_time(self) -> Optional[float]:
        """Calculate execution time for tool operations"""
        
        hook_event = os.environ.get('CLAUDE_HOOK_EVENT_NAME', '')
        
        if hook_event == 'PreToolUse':
            # Store start time
            start_time_file = self.project_root / '.claude' / f'start_time_{self.session_id}.tmp'
            with open(start_time_file, 'w') as f:
                f.write(str(time.time()))
            return None
        
        elif hook_event == 'PostToolUse':
            # Calculate execution time
            start_time_file = self.project_root / '.claude' / f'start_time_{self.session_id}.tmp'
            
            if start_time_file.exists():
                try:
                    with open(start_time_file, 'r') as f:
                        start_time = float(f.read().strip())
                    
                    execution_time = time.time() - start_time
                    start_time_file.unlink()  # Clean up
                    return execution_time
                    
                except (ValueError, FileNotFoundError):
                    return None
        
        return None
    
    def _determine_operation_success(self, hook_event: str, metadata: Dict[str, Any]) -> bool:
        """Determine if operation was successful"""
        
        # For PostToolUse events, check for errors in response
        if hook_event == 'PostToolUse':
            tool_response = metadata.get('tool_response', '')
            
            # Check for error indicators
            error_indicators = [
                'error', 'failed', 'exception', 'traceback',
                'could not', 'unable to', 'permission denied'
            ]
            
            tool_response_lower = tool_response.lower()
            for indicator in error_indicators:
                if indicator in tool_response_lower:
                    return False
        
        # For other events, assume success unless explicitly failed
        return True
    
    def _store_event_data(self, event: HookEvent):
        """Store event data in database"""
        
        with sqlite3.connect(self.dashboard_db) as conn:
            conn.execute("""
                INSERT INTO hook_events 
                (session_id, timestamp, hook_event, tool_name, execution_time, success, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                event.session_id,
                event.timestamp,
                event.hook_event,
                event.tool_name,
                event.execution_time,
                event.success,
                json.dumps(event.metadata)
            ))
    
    def _store_system_metrics(self, metrics: SystemMetrics):
        """Store system metrics in database"""
        
        with sqlite3.connect(self.dashboard_db) as conn:
            conn.execute("""
                INSERT INTO system_metrics 
                (timestamp, cpu_percent, memory_percent, memory_used_mb, 
                 disk_usage_percent, network_sent_mb, network_recv_mb, active_processes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metrics.timestamp,
                metrics.cpu_percent,
                metrics.memory_percent,
                metrics.memory_used_mb,
                metrics.disk_usage_percent,
                metrics.network_sent_mb,
                metrics.network_recv_mb,
                metrics.active_processes
            ))
    
    def _update_session_state(self, event: HookEvent):
        """Update session state information"""
        
        with sqlite3.connect(self.dashboard_db) as conn:
            # Get current session state
            current_state = conn.execute(
                "SELECT * FROM session_state WHERE session_id = ?",
                (self.session_id,)
            ).fetchone()
            
            # Prepare updated state
            now = datetime.now().isoformat()
            total_events = self.event_count + 1
            
            # Get active hooks
            active_hooks = self._get_active_hooks()
            
            # Get MCP server status
            mcp_status = self._get_mcp_server_status()
            
            # Get current operations
            current_operations = self._get_current_operations(event)
            
            # Performance summary
            performance_summary = self._generate_performance_summary()
            
            if current_state:
                # Update existing session
                conn.execute("""
                    UPDATE session_state 
                    SET last_activity = ?, total_events = ?, active_hooks = ?,
                        mcp_servers_status = ?, current_operations = ?, performance_summary = ?
                    WHERE session_id = ?
                """, (
                    now, total_events, json.dumps(active_hooks),
                    json.dumps(mcp_status), json.dumps(current_operations),
                    json.dumps(performance_summary), self.session_id
                ))
            else:
                # Create new session
                conn.execute("""
                    INSERT INTO session_state 
                    (session_id, start_time, last_activity, total_events, active_hooks,
                     mcp_servers_status, current_operations, performance_summary)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    self.session_id, now, now, total_events, json.dumps(active_hooks),
                    json.dumps(mcp_status), json.dumps(current_operations),
                    json.dumps(performance_summary)
                ))
    
    def _get_active_hooks(self) -> List[str]:
        """Get list of currently active hooks"""
        
        active_hooks = []
        
        hook_event = os.environ.get('CLAUDE_HOOK_EVENT_NAME', '')
        if hook_event:
            active_hooks.append(hook_event)
        
        # Check for running hook processes
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = ' '.join(proc.info['cmdline'] or [])
                if '.claude/hooks/' in cmdline and proc.info['name'] == 'python3':
                    hook_name = self._extract_hook_name(cmdline)
                    if hook_name and hook_name not in active_hooks:
                        active_hooks.append(hook_name)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return active_hooks
    
    def _extract_hook_name(self, cmdline: str) -> Optional[str]:
        """Extract hook name from command line"""
        
        if '.claude/hooks/' in cmdline:
            parts = cmdline.split('.claude/hooks/')
            if len(parts) > 1:
                hook_path = parts[1].split()[0]
                return hook_path.replace('/', '_').replace('.py', '')
        
        return None
    
    def _get_mcp_server_status(self) -> Dict[str, str]:
        """Get current MCP server status"""
        
        # This would normally check actual MCP servers
        # For now, return mock status
        servers = [
            'context-aware-memory', 'ml-code-intelligence', 'agentic-workflow',
            'predictive-analytics', 'ml-testing-qa', '10x-knowledge-graph', '10x-command-analytics'
        ]
        
        status = {}
        for server in servers:
            # Check if server process is running
            status[server] = self._check_server_process(server)
        
        return status
    
    def _check_server_process(self, server_name: str) -> str:
        """Check if MCP server process is running"""
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = ' '.join(proc.info['cmdline'] or [])
                if server_name in cmdline and 'server.py' in cmdline:
                    return 'online'
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return 'offline'
    
    def _get_current_operations(self, event: HookEvent) -> List[Dict[str, Any]]:
        """Get current operations in progress"""
        
        operations = []
        
        # Current hook operation
        if event.hook_event and event.tool_name:
            operations.append({
                'type': 'hook_operation',
                'name': f"{event.hook_event}: {event.tool_name}",
                'status': 'active',
                'start_time': event.timestamp,
                'progress': self._estimate_progress(event)
            })
        
        # Check for other active operations
        operations.extend(self._get_file_operations())
        operations.extend(self._get_network_operations())
        
        return operations
    
    def _estimate_progress(self, event: HookEvent) -> float:
        """Estimate operation progress"""
        
        if event.hook_event == 'PreToolUse':
            return 0.1  # Just started
        elif event.hook_event == 'PostToolUse':
            return 1.0  # Completed
        elif event.hook_event in ['Notification', 'SubagentStop']:
            return 0.5  # In progress
        
        return 0.3  # Default progress
    
    def _get_file_operations(self) -> List[Dict[str, Any]]:
        """Get active file operations"""
        
        operations = []
        
        # Check for active file I/O
        for proc in psutil.process_iter(['pid', 'name', 'open_files']):
            try:
                if proc.info['name'] in ['python3', 'uv', 'git']:
                    open_files = proc.info['open_files'] or []
                    
                    for file_info in open_files:
                        if str(self.project_root) in file_info.path:
                            operations.append({
                                'type': 'file_operation',
                                'name': f"File I/O: {Path(file_info.path).name}",
                                'status': 'active',
                                'details': file_info.path
                            })
                            break  # Only add one per process
                            
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return operations[:5]  # Limit to 5 operations
    
    def _get_network_operations(self) -> List[Dict[str, Any]]:
        """Get active network operations"""
        
        operations = []
        
        # Check for active network connections
        for conn in psutil.net_connections(kind='inet'):
            if conn.status == psutil.CONN_ESTABLISHED:
                # Check if it's related to our MCP servers
                if conn.laddr.port in [8001, 8002, 8003, 8004, 8005, 8006, 8007]:
                    operations.append({
                        'type': 'network_operation',
                        'name': f"MCP Connection: {conn.laddr.port}",
                        'status': 'connected',
                        'details': f"{conn.laddr.ip}:{conn.laddr.port}"
                    })
        
        return operations[:3]  # Limit to 3 operations
    
    def _generate_performance_summary(self) -> Dict[str, Any]:
        """Generate performance summary for current session"""
        
        current_time = time.time()
        session_duration = current_time - self.start_time
        
        return {
            'session_duration': session_duration,
            'total_events': self.event_count,
            'events_per_minute': (self.event_count / session_duration) * 60 if session_duration > 0 else 0,
            'avg_cpu_usage': self._get_avg_cpu_usage(),
            'avg_memory_usage': self._get_avg_memory_usage(),
            'last_update': datetime.now().isoformat()
        }
    
    def _get_avg_cpu_usage(self) -> float:
        """Get average CPU usage for session"""
        
        with sqlite3.connect(self.dashboard_db) as conn:
            result = conn.execute("""
                SELECT AVG(cpu_percent) 
                FROM system_metrics 
                WHERE timestamp >= ?
            """, (
                (datetime.now() - timedelta(minutes=10)).isoformat(),
            )).fetchone()
            
            return result[0] if result and result[0] else 0.0
    
    def _get_avg_memory_usage(self) -> float:
        """Get average memory usage for session"""
        
        with sqlite3.connect(self.dashboard_db) as conn:
            result = conn.execute("""
                SELECT AVG(memory_percent) 
                FROM system_metrics 
                WHERE timestamp >= ?
            """, (
                (datetime.now() - timedelta(minutes=10)).isoformat(),
            )).fetchone()
            
            return result[0] if result and result[0] else 0.0
    
    def _send_to_dashboard(self, event: HookEvent, metrics: SystemMetrics):
        """Send data to real-time dashboard via WebSocket"""
        
        try:
            # Prepare dashboard update message
            dashboard_message = {
                'type': 'dashboard_update',
                'timestamp': datetime.now().isoformat(),
                'session_id': self.session_id,
                'event': asdict(event),
                'metrics': asdict(metrics),
                'summary': self._generate_performance_summary()
            }
            
            # Send via WebSocket (non-blocking)
            asyncio.create_task(self._send_websocket_message(dashboard_message))
            
        except Exception as e:
            logger.warning(f"Failed to send to dashboard: {e}")
    
    async def _send_websocket_message(self, message: Dict[str, Any]):
        """Send message via WebSocket"""
        
        try:
            async with websockets.connect(self.websocket_url, timeout=2) as websocket:
                await websocket.send(json.dumps(message))
                
        except Exception as e:
            # WebSocket connection failed - dashboard might not be running
            logger.debug(f"WebSocket send failed: {e}")
    
    def _update_dashboard_html(self):
        """Update static dashboard HTML file"""
        
        dashboard_file = self.project_root / '.claude' / 'dashboard.html'
        
        try:
            # Generate current dashboard HTML
            html_content = self._generate_dashboard_html()
            
            with open(dashboard_file, 'w') as f:
                f.write(html_content)
                
        except Exception as e:
            logger.warning(f"Failed to update dashboard HTML: {e}")
    
    def _generate_dashboard_html(self) -> str:
        """Generate dashboard HTML content"""
        
        # Get recent events and metrics
        recent_events = self._get_recent_events(10)
        current_metrics = self._collect_system_metrics()
        session_summary = self._generate_performance_summary()
        
        html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <title>10X Agentic Setup - Real-Time Dashboard</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #1a1a1a; color: #fff; }}
        .dashboard {{ max-width: 1400px; margin: 0 auto; }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .header h1 {{ color: #00ff88; margin: 0; font-size: 2.5em; }}
        .header p {{ color: #ccc; margin: 5px 0; }}
        .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .metric-card {{ background: #2a2a2a; border-radius: 10px; padding: 20px; border-left: 4px solid #00ff88; }}
        .metric-title {{ font-size: 1.2em; margin-bottom: 10px; color: #00ff88; }}
        .metric-value {{ font-size: 2em; font-weight: bold; margin-bottom: 5px; }}
        .metric-unit {{ color: #ccc; font-size: 0.8em; }}
        .events-section {{ background: #2a2a2a; border-radius: 10px; padding: 20px; }}
        .events-title {{ font-size: 1.5em; margin-bottom: 20px; color: #00ff88; }}
        .event-item {{ background: #333; border-radius: 5px; padding: 15px; margin-bottom: 10px; }}
        .event-header {{ display: flex; justify-content: between; align-items: center; margin-bottom: 10px; }}
        .event-type {{ color: #00ff88; font-weight: bold; }}
        .event-time {{ color: #ccc; font-size: 0.9em; }}
        .event-tool {{ color: #fff; }}
        .event-meta {{ color: #aaa; font-size: 0.9em; }}
        .status-online {{ color: #00ff88; }}
        .status-offline {{ color: #ff4444; }}
        .update-time {{ text-align: center; margin-top: 20px; color: #ccc; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="header">
            <h1>🚀 10X Agentic Setup Dashboard</h1>
            <p>Session: {self.session_id}</p>
            <p>Real-time observability and performance monitoring</p>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-title">CPU Usage</div>
                <div class="metric-value">{current_metrics.cpu_percent:.1f}</div>
                <div class="metric-unit">%</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-title">Memory Usage</div>
                <div class="metric-value">{current_metrics.memory_percent:.1f}</div>
                <div class="metric-unit">%</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-title">Session Duration</div>
                <div class="metric-value">{session_summary['session_duration'] / 60:.1f}</div>
                <div class="metric-unit">minutes</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-title">Total Events</div>
                <div class="metric-value">{session_summary['total_events']}</div>
                <div class="metric-unit">events</div>
            </div>
        </div>
        
        <div class="events-section">
            <div class="events-title">Recent Hook Events</div>
            {self._format_events_html(recent_events)}
        </div>
        
        <div class="update-time">
            Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
</body>
</html>
        """
        
        return html_template
    
    def _get_recent_events(self, limit: int) -> List[Dict[str, Any]]:
        """Get recent hook events from database"""
        
        with sqlite3.connect(self.dashboard_db) as conn:
            cursor = conn.execute("""
                SELECT hook_event, tool_name, timestamp, execution_time, success, metadata
                FROM hook_events 
                WHERE session_id = ?
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (self.session_id, limit))
            
            events = []
            for row in cursor.fetchall():
                events.append({
                    'hook_event': row[0],
                    'tool_name': row[1],
                    'timestamp': row[2],
                    'execution_time': row[3],
                    'success': row[4],
                    'metadata': json.loads(row[5]) if row[5] else {}
                })
            
            return events
    
    def _format_events_html(self, events: List[Dict[str, Any]]) -> str:
        """Format events as HTML"""
        
        if not events:
            return '<div class="event-item">No events recorded yet</div>'
        
        html_events = []
        for event in events:
            success_indicator = '✓' if event['success'] else '✗'
            execution_time = f"{event['execution_time']:.3f}s" if event['execution_time'] else "N/A"
            
            event_html = f"""
            <div class="event-item">
                <div class="event-header">
                    <span class="event-type">{event['hook_event']}</span>
                    <span class="event-time">{event['timestamp'][-8:]}</span>
                </div>
                <div class="event-tool">{event['tool_name']} {success_indicator}</div>
                <div class="event-meta">Execution time: {execution_time}</div>
            </div>
            """
            html_events.append(event_html)
        
        return '\n'.join(html_events)

def main():
    """Main dashboard updater entry point"""
    
    updater = DashboardUpdater()
    updater.update_dashboard()
    
    print("Dashboard updated successfully")

if __name__ == "__main__":
    main()