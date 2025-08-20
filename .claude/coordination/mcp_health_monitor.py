#!/usr/bin/env python3
"""
Basic MCP Health Monitor - Phase 1 Implementation
Simple health checks and autonomous restart with safety limits
"""
import subprocess
import time
import sqlite3
import asyncio
import logging
from pathlib import Path

# MCP server configuration
SERVERS = {
    "ml-code-intelligence": {"port": 8001, "wrapper": "ml-code-intelligence.sh"},
    "context-aware-memory": {"port": 8002, "wrapper": "context-aware-memory.sh"},
    "predictive-analytics": {"port": 8003, "wrapper": "predictive-analytics.sh"},
    "ml-testing-qa": {"port": 8004, "wrapper": "ml-testing-qa.sh"},
    "agentic-workflow": {"port": 8005, "wrapper": "agentic-workflow.sh"},
    "10x-knowledge-graph": {"port": 8006, "wrapper": "10x-knowledge-graph.sh"},
    "10x-command-analytics": {"port": 8007, "wrapper": "10x-command-analytics.sh"},
}

class MCPHealthMonitor:
    def __init__(self):
        self.db_path = '.claude/coordination/coordination.db'
        self.init_database()
        
        # Configure logging
        logging.basicConfig(
            filename='.claude/coordination/health_check.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def init_database(self):
        """Initialize coordination database"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        
        # Server health table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS server_health (
                timestamp REAL,
                server_name TEXT,
                status TEXT,
                restart_count INTEGER DEFAULT 0
            )
        ''')
        
        # Restart log table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS restart_log (
                timestamp REAL,
                server_name TEXT,
                action TEXT,
                details TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def check_server_health(self, server_name, config):
        """Simple health check - process and port"""
        try:
            # Check if process exists
            result = subprocess.run(
                ['pgrep', '-f', config['wrapper']], 
                capture_output=True, 
                timeout=5,
                text=True
            )
            process_running = result.returncode == 0
            
            # Check if port is listening
            result = subprocess.run(
                ['netstat', '-ln'], 
                capture_output=True, 
                timeout=5,
                text=True
            )
            port_listening = f":{config['port']}" in result.stdout
            
            # Determine status
            if process_running and port_listening:
                return "active"
            elif process_running:
                return "degraded"
            else:
                return "failed"
                
        except Exception as e:
            self.logger.error(f"Health check failed for {server_name}: {e}")
            return "failed"
    
    def store_health_status(self, server_name, status):
        """Store health status in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute(
                "INSERT INTO server_health (timestamp, server_name, status) VALUES (?, ?, ?)",
                (time.time(), server_name, status)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            self.logger.error(f"Failed to store health status: {e}")
    
    def count_recent_restarts(self, server_name, hours=1):
        """Count recent restarts for safety limit"""
        try:
            conn = sqlite3.connect(self.db_path)
            cutoff_time = time.time() - (hours * 3600)
            
            result = conn.execute('''
                SELECT COUNT(*) FROM restart_log 
                WHERE server_name = ? AND timestamp > ? AND action = 'restart_attempted'
            ''', (server_name, cutoff_time)).fetchone()
            
            conn.close()
            return result[0] if result else 0
        except Exception as e:
            self.logger.error(f"Failed to count restarts: {e}")
            return 999  # Assume limit exceeded on error
    
    async def attempt_restart(self, server_name, config):
        """Safe server restart with limits"""
        try:
            # Check restart limit (max 3 per hour)
            recent_restarts = self.count_recent_restarts(server_name, hours=1)
            if recent_restarts >= 3:
                self.log_restart_error(server_name, "Restart limit exceeded")
                return False
            
            self.log_restart_attempt(server_name)
            
            # Step 1: Kill existing process
            subprocess.run(['pkill', '-f', config['wrapper']], timeout=10)
            await asyncio.sleep(5)  # Grace period
            
            # Step 2: Start new process
            wrapper_path = f"/home/dell/.local/bin/mcp-servers/{config['wrapper']}"
            
            # Check if wrapper exists
            if not Path(wrapper_path).exists():
                wrapper_path = f"./mcp_servers/{config['wrapper']}"
                if not Path(wrapper_path).exists():
                    self.log_restart_error(server_name, f"Wrapper script not found: {config['wrapper']}")
                    return False
            
            process = subprocess.Popen(
                [wrapper_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # Step 3: Verify startup (30 second timeout)
            for i in range(30):
                await asyncio.sleep(1)
                if self.check_server_health(server_name, config) == "active":
                    self.log_restart_success(server_name)
                    return True
            
            self.log_restart_timeout(server_name)
            return False
            
        except Exception as e:
            self.log_restart_error(server_name, str(e))
            return False
    
    def log_restart_attempt(self, server_name):
        """Log restart attempt"""
        self.log_restart_action(server_name, "restart_attempted", "Attempting server restart")
        self.logger.info(f"Attempting restart of {server_name}")
    
    def log_restart_success(self, server_name):
        """Log successful restart"""
        self.log_restart_action(server_name, "restart_success", "Server successfully restarted")
        self.logger.info(f"Successfully restarted {server_name}")
    
    def log_restart_timeout(self, server_name):
        """Log restart timeout"""
        self.log_restart_action(server_name, "restart_timeout", "Server failed to start within timeout")
        self.logger.warning(f"Restart timeout for {server_name}")
    
    def log_restart_error(self, server_name, error):
        """Log restart error"""
        self.log_restart_action(server_name, "restart_failed", error)
        self.logger.error(f"Restart failed for {server_name}: {error}")
    
    def log_restart_action(self, server_name, action, details):
        """Log restart action to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute(
                "INSERT INTO restart_log VALUES (?, ?, ?, ?)",
                (time.time(), server_name, action, details)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            self.logger.error(f"Failed to log restart action: {e}")
    
    async def monitoring_loop(self):
        """Main monitoring loop"""
        self.logger.info("Starting MCP health monitoring")
        
        while True:
            try:
                for server_name, config in SERVERS.items():
                    status = self.check_server_health(server_name, config)
                    self.store_health_status(server_name, status)
                    
                    if status == "failed":
                        self.logger.warning(f"Server {server_name} failed, attempting restart")
                        await self.attempt_restart(server_name, config)
                
                # Wait 30 seconds before next check
                await asyncio.sleep(30)
                
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(60)  # Longer sleep on error
    
    def get_server_status_summary(self):
        """Get current server status summary"""
        try:
            summary = {}
            for server_name, config in SERVERS.items():
                status = self.check_server_health(server_name, config)
                summary[server_name] = {
                    'status': status,
                    'port': config['port']
                }
            return summary
        except Exception as e:
            self.logger.error(f"Failed to get status summary: {e}")
            return {}

async def main():
    """Main function for running the health monitor"""
    monitor = MCPHealthMonitor()
    await monitor.monitoring_loop()

if __name__ == '__main__':
    asyncio.run(main())