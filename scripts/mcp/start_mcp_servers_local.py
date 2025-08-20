#!/usr/bin/env python3
"""
Local MCP Server Startup Script
Starts all MCP servers with proper import paths and port management
"""

import os
import sys
import time
import signal
import subprocess
import multiprocessing
from pathlib import Path
import socket

def is_port_available(port):
    """Check if a port is available"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
            return True
    except OSError:
        return False

def start_server(server_info):
    """Start a single MCP server"""
    server_name, server_path, port = server_info
    
    print(f"🚀 Starting {server_name} on port {port}...")
    
    # Check if port is available
    if not is_port_available(port):
        print(f"⚠️  Port {port} is already in use for {server_name}")
        return None
    
    # Set up environment
    env = os.environ.copy()
    project_root = Path(__file__).parent
    shared_path = project_root / "mcp_servers" / "shared" / "src"
    
    env['PYTHONPATH'] = f"{server_path}:{shared_path}:{env.get('PYTHONPATH', '')}"
    env['MCP_SERVER_PORT'] = str(port)
    env['MCP_SERVER_HOST'] = 'localhost'
    
    # Start server process
    server_file = Path(server_path) / "server.py"
    
    try:
        # Create startup script for this server
        startup_script = f"""
import sys
import os

# Add paths
sys.path.insert(0, r'{server_path}')
sys.path.insert(0, r'{shared_path}')

# Set environment
os.environ['MCP_SERVER_PORT'] = '{port}'
os.environ['MCP_SERVER_HOST'] = 'localhost'

# Import and run server
try:
    import server
    print(f'✅ {{server.__name__}} server started on port {port}')
    
    # Keep server running
    if hasattr(server, 'main'):
        server.main()
    elif hasattr(server, 'app'):
        # Run the MCP app
        import asyncio
        if hasattr(server.app, 'run'):
            asyncio.run(server.app.run())
        else:
            print(f'Server {{server.__name__}} loaded but no run method found')
            # Keep alive
            import time
            while True:
                time.sleep(1)
    else:
        print(f'Server {{server.__name__}} loaded but no main function found')
        # Keep alive anyway
        import time
        while True:
            time.sleep(1)
            
except KeyboardInterrupt:
    print(f'Server {server_name} stopping...')
except Exception as e:
    print(f'Error in server {server_name}: {{e}}')
    import traceback
    traceback.print_exc()
"""
        
        # Write temporary startup script
        script_file = project_root / f"temp_start_{server_name.lower().replace(' ', '_')}.py"
        with open(script_file, 'w') as f:
            f.write(startup_script)
        
        # Start the server
        process = subprocess.Popen([
            sys.executable, str(script_file)
        ], env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        # Give it a moment to start
        time.sleep(2)
        
        # Check if it's still running
        if process.poll() is None:
            print(f"✅ {server_name} started successfully (PID: {process.pid})")
            return process, script_file
        else:
            print(f"❌ {server_name} failed to start")
            # Clean up
            try:
                script_file.unlink()
            except:
                pass
            return None
            
    except Exception as e:
        print(f"❌ Error starting {server_name}: {e}")
        return None

def main():
    """Main function to start all MCP servers"""
    
    print("🚀 Starting Local MCP Servers")
    print("=" * 50)
    
    project_root = Path(__file__).parent
    
    # Define servers with their paths and ports
    servers = [
        ("Context-Aware Memory", project_root / "mcp_servers" / "context_aware_memory" / "src", 8001),
        ("ML Code Intelligence", project_root / "mcp_servers" / "ml_code_intelligence" / "src", 8002),
        ("Agentic Workflow", project_root / "mcp_servers" / "agentic_workflow" / "src", 8003),
        ("Predictive Analytics", project_root / "mcp_servers" / "predictive_analytics" / "src", 8004),
        ("ML Testing QA", project_root / "mcp_servers" / "ml_testing_qa" / "src", 8005),
    ]
    
    # Start servers
    running_servers = []
    
    for server_info in servers:
        server_name, server_path, port = server_info
        
        if not server_path.exists():
            print(f"❌ {server_name}: Path not found - {server_path}")
            continue
            
        result = start_server(server_info)
        if result:
            running_servers.append(result)
    
    if not running_servers:
        print("❌ No servers started successfully")
        return 1
    
    print(f"\n✅ Started {len(running_servers)} MCP servers")
    print("\n📊 Server Status:")
    for i, (process, script_file) in enumerate(running_servers):
        port = 8001 + i
        print(f"  - Server {i+1}: PID {process.pid}, Port {port}")
    
    print(f"\n🌐 Test server connectivity:")
    for i, (process, script_file) in enumerate(running_servers):
        port = 8001 + i
        print(f"  curl http://localhost:{port}/health")
    
    print(f"\n⏹️  To stop servers: kill {' '.join(str(p[0].pid) for p in running_servers)}")
    print("   Or press Ctrl+C to stop all servers")
    
    # Handle shutdown
    def signal_handler(sig, frame):
        print("\n🛑 Shutting down servers...")
        for process, script_file in running_servers:
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                process.kill()
            
            # Clean up script files
            try:
                script_file.unlink()
            except:
                pass
        
        print("✅ All servers stopped")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Keep main process alive
    try:
        while True:
            # Check if any servers died
            for i, (process, script_file) in enumerate(running_servers[:]):
                if process.poll() is not None:
                    print(f"⚠️  Server {i+1} died (PID {process.pid})")
                    running_servers.remove((process, script_file))
            
            if not running_servers:
                print("❌ All servers have stopped")
                break
                
            time.sleep(5)
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())