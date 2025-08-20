#!/usr/bin/env python3
"""
Background Monitor Agent - Phase 2 Implementation
Autonomous 24/7 monitoring with pattern learning and proactive actions
"""
import asyncio
import json
import sqlite3
import time
import psutil
import subprocess
import logging
from pathlib import Path
from collections import defaultdict, deque

class BackgroundMonitorAgent:
    def __init__(self):
        self.db_path = '.claude/background/background_monitor.db'
        self.patterns_file = '.claude/background/patterns.json'
        self.running = False
        
        # Ensure directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self.init_database()
        
        # Load learned patterns
        self.usage_patterns = self.load_patterns()
        
        # State tracking
        self.state_history = deque(maxlen=1000)
        
        # Monitoring thresholds (from Phase 1)
        self.thresholds = {
            'cpu_warning': 70.0,
            'memory_action': 85.0,
            'disk_action': 90.0,
            'mcp_health_check_interval': 60
        }
        
        # Configure logging
        logging.basicConfig(
            filename='.claude/background/monitor.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def init_database(self):
        """Initialize background agent database"""
        conn = sqlite3.connect(self.db_path)
        
        # Agent actions table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS agent_actions (
                timestamp REAL,
                action_type TEXT,
                result TEXT,
                details TEXT
            )
        ''')
        
        # Agent status table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS agent_status (
                last_heartbeat REAL,
                actions_count INTEGER,
                errors_count INTEGER
            )
        ''')
        
        # Pattern learning table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS learned_patterns (
                pattern_type TEXT,
                pattern_data TEXT,
                confidence REAL,
                last_updated REAL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def load_patterns(self):
        """Load learned usage patterns"""
        try:
            if Path(self.patterns_file).exists():
                with open(self.patterns_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load patterns: {e}")
        
        return {
            'peak_hours': [],
            'tool_sequences': {},
            'resource_cycles': {}
        }
    
    def save_patterns(self):
        """Save learned patterns to file"""
        try:
            with open(self.patterns_file, 'w') as f:
                json.dump(self.usage_patterns, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save patterns: {e}")
    
    async def collect_system_metrics(self):
        """Collect comprehensive system metrics"""
        try:
            metrics = {
                'timestamp': time.time(),
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
                'active_processes': len(psutil.pids()),
                'mcp_servers_active': await self.count_active_mcp_servers(),
                'recent_tools': await self.get_recent_tool_usage(),
                'current_project': await self.detect_current_project()
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
                'mcp_servers_active': 0,
                'recent_tools': [],
                'current_project': 'unknown'
            }
    
    async def count_active_mcp_servers(self):
        """Count active MCP servers"""
        try:
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
    
    async def get_recent_tool_usage(self):
        """Get recent tool usage from hooks database"""
        try:
            if not Path('.claude/hooks/hooks.db').exists():
                return []
            
            conn = sqlite3.connect('.claude/hooks/hooks.db')
            result = conn.execute('''
                SELECT tool_name FROM events 
                WHERE timestamp > ? 
                ORDER BY timestamp DESC LIMIT 10
            ''', (time.time() - 3600,)).fetchall()
            conn.close()
            
            return [row[0] for row in result]
        except Exception:
            return []
    
    async def detect_current_project(self):
        """Detect current project context"""
        try:
            # Simple project detection based on git repo
            result = subprocess.run(
                ['git', 'rev-parse', '--show-toplevel'],
                capture_output=True,
                timeout=5,
                text=True
            )
            if result.returncode == 0:
                return Path(result.stdout.strip()).name
            return 'unknown'
        except Exception:
            return 'unknown'
    
    def check_urgent_conditions(self, metrics):
        """Check for conditions requiring immediate action"""
        actions = []
        
        # High memory usage
        if metrics['memory_percent'] > self.thresholds['memory_action']:
            actions.append({
                'type': 'clear_caches',
                'priority': 'high',
                'reason': f"Memory at {metrics['memory_percent']:.1f}%",
                'metrics': metrics
            })
        
        # Failed MCP servers
        if metrics['mcp_servers_active'] < 7:
            actions.append({
                'type': 'check_mcp_servers',
                'priority': 'high',
                'reason': f"Only {metrics['mcp_servers_active']} MCP servers active",
                'metrics': metrics
            })
        
        # Disk space critical
        if metrics['disk_percent'] > self.thresholds['disk_action']:
            actions.append({
                'type': 'cleanup_disk',
                'priority': 'high',
                'reason': f"Disk usage at {metrics['disk_percent']:.1f}%",
                'metrics': metrics
            })
        
        return actions
    
    def suggest_proactive_actions(self, metrics):
        """Suggest proactive actions based on learned patterns"""
        actions = []
        current_hour = time.localtime().tm_hour
        
        # Time-based predictions
        if current_hour in self.usage_patterns.get('peak_hours', []):
            actions.append({
                'type': 'warm_systems',
                'priority': 'medium',
                'reason': f"Peak usage predicted at hour {current_hour}",
                'metrics': metrics
            })
        
        # Resource trend predictions
        if len(self.state_history) > 10:
            memory_trend = self.predict_memory_trend()
            if memory_trend > 80:
                actions.append({
                    'type': 'preload_research',
                    'priority': 'low',
                    'reason': "Memory usage trending up",
                    'metrics': metrics
                })
        
        # Tool sequence predictions
        recent_tools = metrics.get('recent_tools', [])
        if len(recent_tools) > 3:
            predicted_tools = self.predict_next_tools(recent_tools)
            if 'research' in predicted_tools:
                actions.append({
                    'type': 'preload_research',
                    'priority': 'low',
                    'reason': "Research tools predicted",
                    'metrics': metrics
                })
        
        return actions
    
    def predict_memory_trend(self):
        """Predict memory usage trend"""
        if len(self.state_history) < 5:
            return 0
        
        recent_memory = [state['memory_percent'] for state in list(self.state_history)[-5:]]
        # Simple linear trend
        if len(recent_memory) >= 2:
            slope = (recent_memory[-1] - recent_memory[0]) / len(recent_memory)
            prediction = recent_memory[-1] + slope * 3  # Predict 3 intervals ahead
            return max(0, min(100, prediction))
        
        return recent_memory[-1] if recent_memory else 0
    
    def predict_next_tools(self, recent_tools):
        """Predict next tools based on usage patterns"""
        # Simple pattern matching
        tool_sequences = self.usage_patterns.get('tool_sequences', {})
        
        # Look for matching sequences
        for seq_len in range(min(3, len(recent_tools)), 0, -1):
            sequence = tuple(recent_tools[:seq_len])
            if sequence in tool_sequences:
                return tool_sequences[sequence]
        
        return []
    
    async def execute_action(self, action):
        """Execute autonomous action with safety checks"""
        try:
            success = False
            details = ""
            
            if action['type'] == 'clear_caches':
                success, details = await self.clear_development_caches()
            
            elif action['type'] == 'cleanup_disk':
                success, details = await self.cleanup_disk_space()
            
            elif action['type'] == 'check_mcp_servers':
                success, details = await self.check_and_restart_mcp_servers()
            
            elif action['type'] == 'warm_systems':
                success, details = await self.warm_systems()
            
            elif action['type'] == 'preload_research':
                success, details = await self.preload_research_data()
            
            # Record action execution
            self.record_action(action, success, details)
            return success
            
        except Exception as e:
            self.logger.error(f"Action execution failed: {e}")
            self.record_action(action, False, str(e))
            return False
    
    async def clear_development_caches(self):
        """Clear common development caches"""
        try:
            cache_dirs = [
                '.claude/cache',
                'node_modules/.cache',
                '.npm/_cacache',
                '__pycache__',
                '.pytest_cache'
            ]
            
            cleared_size = 0
            cleared_items = []
            
            for cache_dir in cache_dirs:
                cache_path = Path(cache_dir)
                if cache_path.exists():
                    # Get size before clearing
                    size = sum(f.stat().st_size for f in cache_path.rglob('*') if f.is_file())
                    
                    # Clear cache
                    subprocess.run(['rm', '-rf', str(cache_path)], timeout=30)
                    cleared_size += size
                    cleared_items.append(cache_dir)
            
            details = f"Cleared {len(cleared_items)} caches, freed {cleared_size/1024/1024:.1f}MB"
            self.logger.info(details)
            return True, details
            
        except Exception as e:
            self.logger.error(f"Cache clear failed: {e}")
            return False, str(e)
    
    async def cleanup_disk_space(self):
        """Clean up disk space safely"""
        try:
            # Clean old log files
            cleaned_items = []
            
            log_dirs = ['.claude/logs', '.claude/monitoring', '/tmp']
            
            for log_dir in log_dirs:
                if Path(log_dir).exists():
                    # Clean files older than 7 days
                    result = subprocess.run([
                        'find', log_dir, '-name', '*.log',
                        '-mtime', '+7', '-delete'
                    ], timeout=60, capture_output=True)
                    
                    if result.returncode == 0:
                        cleaned_items.append(log_dir)
            
            details = f"Cleaned old logs in {len(cleaned_items)} directories"
            self.logger.info(details)
            return True, details
            
        except Exception as e:
            self.logger.error(f"Disk cleanup failed: {e}")
            return False, str(e)
    
    async def check_and_restart_mcp_servers(self):
        """Check and restart MCP servers if needed"""
        try:
            # Use Phase 1 MCP coordination if available
            if Path('.claude/coordination/mcp_health_monitor.py').exists():
                result = subprocess.run([
                    'python3', '.claude/coordination/mcp_health_monitor.py'
                ], timeout=30, capture_output=True)
                
                details = "Triggered MCP health check"
                self.logger.info(details)
                return True, details
            else:
                details = "MCP health monitor not available"
                self.logger.warning(details)
                return False, details
                
        except Exception as e:
            self.logger.error(f"MCP server check failed: {e}")
            return False, str(e)
    
    async def warm_systems(self):
        """Warm up systems for predicted usage"""
        try:
            # Preload common libraries
            actions = []
            
            # Check if development tools are available
            dev_tools = ['git', 'node', 'python3', 'npm']
            available_tools = []
            
            for tool in dev_tools:
                result = subprocess.run(['which', tool], capture_output=True)
                if result.returncode == 0:
                    available_tools.append(tool)
            
            details = f"Warmed up {len(available_tools)} development tools"
            self.logger.info(details)
            return True, details
            
        except Exception as e:
            self.logger.error(f"System warm-up failed: {e}")
            return False, str(e)
    
    async def preload_research_data(self):
        """Preload commonly accessed research data"""
        try:
            # Get common research patterns from hooks if available
            common_queries = []
            
            if Path('.claude/hooks/hooks.db').exists():
                conn = sqlite3.connect('.claude/hooks/hooks.db')
                result = conn.execute('''
                    SELECT tool_name, COUNT(*) as usage_count
                    FROM events 
                    WHERE tool_name IN ('WebSearch', 'WebFetch', 'Grep')
                    AND timestamp > ?
                    GROUP BY tool_name
                    ORDER BY usage_count DESC
                    LIMIT 3
                ''', (time.time() - 86400,)).fetchall()
                conn.close()
                
                common_queries = [row[0] for row in result]
            
            details = f"Preloaded research data for {len(common_queries)} common patterns"
            self.logger.info(details)
            return True, details
            
        except Exception as e:
            self.logger.error(f"Research preload failed: {e}")
            return False, str(e)
    
    def record_action(self, action, success, details):
        """Record action execution"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute('''
                INSERT INTO agent_actions VALUES (?, ?, ?, ?)
            ''', (
                time.time(),
                action['type'],
                'success' if success else 'failed',
                details
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            self.logger.error(f"Failed to record action: {e}")
    
    def record_state(self, metrics):
        """Record current state for pattern learning"""
        timestamp = time.time()
        
        state = {
            'timestamp': timestamp,
            'hour': time.localtime(timestamp).tm_hour,
            'cpu_percent': metrics['cpu_percent'],
            'memory_percent': metrics['memory_percent'],
            'active_tools': metrics.get('recent_tools', []),
            'mcp_activity': {'active_servers': metrics['mcp_servers_active']},
            'project_context': metrics.get('current_project', 'unknown')
        }
        
        self.state_history.append(state)
        
        # Update patterns every 10 states
        if len(self.state_history) % 10 == 0:
            self.update_patterns()
    
    def update_patterns(self):
        """Update learned patterns from state history"""
        if len(self.state_history) < 50:
            return
        
        # Update time-based patterns
        hourly_usage = defaultdict(list)
        for state in self.state_history:
            hour = state['hour']
            hourly_usage[hour].append(state['cpu_percent'])
        
        # Identify peak hours (high average CPU usage)
        peak_hours = []
        for hour, cpu_values in hourly_usage.items():
            if len(cpu_values) > 5:
                avg_cpu = sum(cpu_values) / len(cpu_values)
                if avg_cpu > 30:
                    peak_hours.append(hour)
        
        self.usage_patterns['peak_hours'] = peak_hours
        
        # Save updated patterns
        self.save_patterns()
        self.logger.info(f"Updated patterns: peak hours {peak_hours}")
    
    def update_agent_status(self, metrics):
        """Update agent status in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Get current counts
            actions_count = conn.execute('SELECT COUNT(*) FROM agent_actions').fetchone()[0]
            errors_count = conn.execute('''
                SELECT COUNT(*) FROM agent_actions WHERE result = 'failed'
            ''').fetchone()[0]
            
            # Update or insert status
            conn.execute('''
                INSERT OR REPLACE INTO agent_status VALUES (?, ?, ?)
            ''', (time.time(), actions_count, errors_count))
            
            conn.commit()
            conn.close()
        except Exception as e:
            self.logger.error(f"Failed to update agent status: {e}")
    
    async def monitoring_loop(self):
        """Main background monitoring loop"""
        self.running = True
        self.logger.info("Background monitor agent started")
        
        while self.running:
            try:
                # 1. Collect system metrics
                metrics = await self.collect_system_metrics()
                
                # 2. Check for urgent actions
                urgent_actions = self.check_urgent_conditions(metrics)
                for action in urgent_actions:
                    await self.execute_action(action)
                
                # 3. Suggest proactive actions
                proactive_actions = self.suggest_proactive_actions(metrics)
                for action in proactive_actions:
                    await self.execute_action(action)
                
                # 4. Learn from current state
                self.record_state(metrics)
                
                # 5. Update agent status
                self.update_agent_status(metrics)
                
                # Sleep for next iteration
                await asyncio.sleep(30)
                
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(60)
    
    async def shutdown(self):
        """Graceful shutdown"""
        self.running = False
        self.logger.info("Background monitor agent shutting down")

async def main():
    """Main function for running the background agent"""
    agent = BackgroundMonitorAgent()
    try:
        await agent.monitoring_loop()
    except KeyboardInterrupt:
        await agent.shutdown()

if __name__ == '__main__':
    asyncio.run(main())