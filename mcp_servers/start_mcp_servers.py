#!/usr/bin/env python3
"""
MCP Server Startup Script
Starts all MCP servers with proper configuration and virtual environment
"""

import os
import sys
import subprocess
import time
import signal
import logging
from pathlib import Path
from typing import Dict, List

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MCPServerManager:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.mcp_servers_dir = Path(__file__).parent
        self.venv_path = self.mcp_servers_dir / "mcp_venv"
        self.python_path = self.venv_path / "bin" / "python"
        
        # Server configurations
        self.servers = {
            "ml-code-intelligence": {
                "path": "ml_code_intelligence/src/server.py",
                "port": 8001,
                "env_vars": {"MCP_SERVER_PORT": "8001"}
            },
            "context-aware-memory": {
                "path": "context_aware_memory/src/server.py", 
                "port": 8002,
                "env_vars": {"MCP_SERVER_PORT": "8002"}
            },
            "agentic-workflow": {
                "path": "agentic_workflow/src/server.py",
                "port": 8003, 
                "env_vars": {"MCP_SERVER_PORT": "8003"}
            },
            "predictive-analytics": {
                "path": "predictive_analytics/src/server.py",
                "port": 8004,
                "env_vars": {"MCP_SERVER_PORT": "8004"}
            },
            "ml-testing-qa": {
                "path": "ml_testing_qa/src/server.py",
                "port": 8005,
                "env_vars": {"MCP_SERVER_PORT": "8005"}
            },
            "10x-knowledge-graph": {
                "path": "knowledge_graph/src/server.py",
                "port": 8006,
                "env_vars": {"MCP_SERVER_PORT": "8006"}
            },
            "10x-command-analytics": {
                "path": "command_analytics/src/server.py",
                "port": 8007,
                "env_vars": {"MCP_SERVER_PORT": "8007"}
            }
        }
        
        self.processes = {}
        
    def setup_environment(self):
        """Setup Python environment for MCP servers"""
        logger.info("Setting up MCP server environment...")
        
        # Check virtual environment
        if not self.venv_path.exists():
            logger.error(f"Virtual environment not found at {self.venv_path}")
            logger.info("Please run: python -m venv mcp_venv && source mcp_venv/bin/activate && pip install -r requirements.txt")
            return False
        
        if not self.python_path.exists():
            logger.error(f"Python executable not found at {self.python_path}")
            return False
            
        return True
        
    def kill_existing_processes(self):
        """Kill any existing MCP server processes"""
        logger.info("Stopping existing MCP server processes...")
        
        for server_name, config in self.servers.items():
            port = config["port"]
            try:
                # Kill processes using the port
                subprocess.run([
                    "bash", "-c", 
                    f"lsof -ti:{port} | xargs -r kill -9"
                ], capture_output=True, timeout=5)
                logger.info(f"Stopped existing processes on port {port}")
            except subprocess.TimeoutExpired:
                logger.warning(f"Timeout stopping processes on port {port}")
            except Exception as e:
                logger.warning(f"Error stopping processes on port {port}: {e}")
                
        # Wait for processes to terminate
        time.sleep(2)
        
    def start_server(self, server_name: str, config: Dict) -> bool:
        """Start a specific MCP server"""
        server_path = self.mcp_servers_dir / config["path"]
        
        if not server_path.exists():
            logger.error(f"Server file not found: {server_path}")
            return False
            
        # Setup environment variables
        env = os.environ.copy()
        env["PYTHONPATH"] = str(self.mcp_servers_dir / "shared" / "src")
        env.update(config.get("env_vars", {}))
        
        # Setup log files
        log_dir = self.mcp_servers_dir / "logs" / server_name
        log_dir.mkdir(parents=True, exist_ok=True)
        
        stdout_file = log_dir / "stdout.log"
        stderr_file = log_dir / "stderr.log"
        
        try:
            logger.info(f"Starting {server_name} on port {config['port']}...")
            
            with open(stdout_file, 'w') as stdout, open(stderr_file, 'w') as stderr:
                process = subprocess.Popen([
                    str(self.python_path), str(server_path)
                ], env=env, cwd=server_path.parent,
                   stdout=stdout, stderr=stderr)
            
            self.processes[server_name] = process
            
            # Give server time to start
            time.sleep(2)
            
            # Check if process is still running
            if process.poll() is None:
                logger.info(f"✅ {server_name} started successfully (PID: {process.pid})")
                return True
            else:
                logger.error(f"❌ {server_name} failed to start")
                # Read error logs
                if stderr_file.exists():
                    with open(stderr_file) as f:
                        error_log = f.read()
                        if error_log:
                            logger.error(f"Error log for {server_name}: {error_log[:500]}...")
                return False
                
        except Exception as e:
            logger.error(f"Exception starting {server_name}: {e}")
            return False
            
    def start_all_servers(self) -> bool:
        """Start all MCP servers"""
        if not self.setup_environment():
            return False
            
        self.kill_existing_processes()
        
        success_count = 0
        total_servers = len(self.servers)
        
        logger.info(f"Starting {total_servers} MCP servers...")
        
        for server_name, config in self.servers.items():
            if self.start_server(server_name, config):
                success_count += 1
            else:
                logger.error(f"Failed to start {server_name}")
                
        success_rate = (success_count / total_servers) * 100
        logger.info(f"Started {success_count}/{total_servers} servers ({success_rate:.1f}% success rate)")
        
        if success_rate >= 95:
            logger.info("🎉 MCP integration target achieved (95%+ success rate)")
            return True
        else:
            logger.warning(f"⚠️ MCP integration below target ({success_rate:.1f}% < 95%)")
            return False
            
    def health_check(self) -> Dict[str, bool]:
        """Perform health check on all servers"""
        logger.info("Performing health checks...")
        
        health_status = {}
        
        for server_name, config in self.servers.items():
            port = config["port"]
            try:
                import requests
                response = requests.get(f"http://localhost:{port}/health", timeout=5)
                health_status[server_name] = response.status_code == 200
                
                if health_status[server_name]:
                    logger.info(f"✅ {server_name} healthy")
                else:
                    logger.warning(f"❌ {server_name} unhealthy (status: {response.status_code})")
                    
            except Exception as e:
                health_status[server_name] = False
                logger.warning(f"❌ {server_name} not responding: {e}")
                
        healthy_count = sum(health_status.values())
        total_count = len(health_status)
        health_rate = (healthy_count / total_count) * 100
        
        logger.info(f"Health check: {healthy_count}/{total_count} servers healthy ({health_rate:.1f}%)")
        
        return health_status
        
    def stop_all_servers(self):
        """Stop all MCP servers gracefully"""
        logger.info("Stopping all MCP servers...")
        
        for server_name, process in self.processes.items():
            try:
                logger.info(f"Stopping {server_name}...")
                process.terminate()
                
                # Wait for graceful shutdown
                try:
                    process.wait(timeout=10)
                    logger.info(f"✅ {server_name} stopped gracefully")
                except subprocess.TimeoutExpired:
                    logger.warning(f"Force killing {server_name}...")
                    process.kill()
                    process.wait()
                    
            except Exception as e:
                logger.error(f"Error stopping {server_name}: {e}")
                
        self.processes.clear()
        
    def create_status_script(self):
        """Create a status checking script"""
        status_script = self.mcp_servers_dir / "check_mcp_status.py"
        
        script_content = f'''#!/usr/bin/env python3
"""MCP Server Status Checker"""

import requests
import sys

def check_status():
    servers = {dict(self.servers)}
    
    healthy = 0
    for name, config in servers.items():
        port = config["port"]
        try:
            response = requests.get(f"http://localhost:{{port}}/health", timeout=2)
            if response.status_code == 200:
                print(f"✅ {{name}} (port {{port}})")
                healthy += 1
            else:
                print(f"❌ {{name}} (port {{port}}) - HTTP {{response.status_code}}")
        except:
            print(f"❌ {{name}} (port {{port}}) - Not responding")
    
    total = len(servers)
    health_rate = (healthy / total) * 100
    print(f"\\n📊 Overall Health: {{health_rate:.1f}}% ({{healthy}}/{{total}})")
    
    if health_rate >= 95:
        print("🎉 Target achieved (95%+ health rate)")
        sys.exit(0)
    else:
        print("⚠️ Below target (95% health rate)")  
        sys.exit(1)

if __name__ == "__main__":
    check_status()
'''
        
        with open(status_script, 'w') as f:
            f.write(script_content)
        os.chmod(status_script, 0o755)
        
        logger.info(f"📝 Created status checker: {status_script}")

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info("Received shutdown signal")
    if 'manager' in globals():
        manager.stop_all_servers()
    sys.exit(0)

def main():
    global manager
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    manager = MCPServerManager()
    
    # Check command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "stop":
            manager.stop_all_servers()
            return
        elif command == "status":
            manager.health_check()
            return
        elif command == "restart":
            manager.stop_all_servers()
            time.sleep(3)
            # Fall through to start
        elif command != "start":
            print("Usage: python start_mcp_servers.py [start|stop|status|restart]")
            return
    
    # Start servers
    success = manager.start_all_servers()
    
    if success:
        logger.info("🎉 All MCP servers started successfully!")
        
        # Wait a bit then do health check
        time.sleep(5)
        health_status = manager.health_check()
        
        # Create status script
        manager.create_status_script()
        
        logger.info("MCP servers are running. Use Ctrl+C to stop.")
        
        # Keep the script running
        try:
            while True:
                time.sleep(60)
                # Periodic health check
                manager.health_check()
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            
    else:
        logger.error("❌ Failed to start all MCP servers")
        sys.exit(1)

if __name__ == "__main__":
    main()