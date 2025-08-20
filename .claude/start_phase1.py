#!/usr/bin/env python3
"""
Phase 1 System Launcher
Starts all Phase 1 monitoring and coordination systems
"""
import subprocess
import asyncio
import signal
import sys
import time
from pathlib import Path

class Phase1Launcher:
    def __init__(self):
        self.processes = []
        self.running = True
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print("\nShutting down Phase 1 systems...")
        self.running = False
        
        # Terminate all processes
        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
        
        sys.exit(0)
    
    async def start_system_monitor(self):
        """Start the system monitoring service"""
        try:
            process = subprocess.Popen([
                sys.executable, 
                '.claude/monitoring/system_monitor.py'
            ])
            self.processes.append(process)
            print("✅ System Monitor started")
            return True
        except Exception as e:
            print(f"❌ Failed to start System Monitor: {e}")
            return False
    
    async def start_mcp_coordinator(self):
        """Start the MCP coordination service"""
        try:
            process = subprocess.Popen([
                sys.executable, 
                '.claude/coordination/mcp_health_monitor.py'
            ])
            self.processes.append(process)
            print("✅ MCP Health Monitor started")
            return True
        except Exception as e:
            print(f"❌ Failed to start MCP Health Monitor: {e}")
            return False
    
    def check_prerequisites(self):
        """Check if all required components exist"""
        required_files = [
            '.claude/hooks/simple_pre_tool_use.py',
            '.claude/hooks/simple_post_tool_use.py',
            '.claude/hooks/simple_stop.py',
            '.claude/monitoring/system_monitor.py',
            '.claude/coordination/mcp_health_monitor.py',
            '.claude/monitoring/dashboard.html'
        ]
        
        missing_files = []
        for file_path in required_files:
            if not Path(file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            print("❌ Missing required files:")
            for file_path in missing_files:
                print(f"   - {file_path}")
            return False
        
        print("✅ All required components found")
        return True
    
    async def monitor_processes(self):
        """Monitor running processes and restart if needed"""
        while self.running:
            try:
                # Check process health
                for i, process in enumerate(self.processes):
                    if process.poll() is not None:
                        print(f"⚠️  Process {i} died, restarting...")
                        # Remove dead process
                        self.processes.pop(i)
                        
                        # Restart based on index
                        if i == 0:  # System monitor
                            await self.start_system_monitor()
                        elif i == 1:  # MCP coordinator
                            await self.start_mcp_coordinator()
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                print(f"Error in process monitoring: {e}")
                await asyncio.sleep(60)
    
    def display_status(self):
        """Display current system status"""
        print("\n" + "="*50)
        print("🚀 10X AGENTIC SETUP - PHASE 1 ACTIVE")
        print("="*50)
        print("📊 System Monitor: Collecting metrics every 30s")
        print("🔗 MCP Coordinator: Health checking servers")
        print("🎣 Hook System: Capturing tool usage patterns")
        print("📈 Dashboard: http://localhost:8080 (if served)")
        print("📁 Dashboard File: .claude/monitoring/dashboard.html")
        print("="*50)
        print("Press Ctrl+C to shutdown all services\n")
    
    async def run(self):
        """Main run function"""
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        print("🚀 Starting 10X Agentic Setup - Phase 1")
        
        # Check prerequisites
        if not self.check_prerequisites():
            print("❌ Prerequisites not met. Run setup first.")
            return False
        
        # Start services
        system_monitor_ok = await self.start_system_monitor()
        mcp_coordinator_ok = await self.start_mcp_coordinator()
        
        if not (system_monitor_ok and mcp_coordinator_ok):
            print("❌ Failed to start some services")
            return False
        
        # Display status
        self.display_status()
        
        # Monitor processes
        await self.monitor_processes()
        
        return True

async def main():
    launcher = Phase1Launcher()
    await launcher.run()

if __name__ == '__main__':
    asyncio.run(main())