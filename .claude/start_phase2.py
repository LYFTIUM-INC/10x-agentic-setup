#!/usr/bin/env python3
"""
Phase 2 System Launcher
Starts Phase 1 + Phase 2 background monitoring and enhanced dashboard
"""
import subprocess
import asyncio
import signal
import sys
import time
from pathlib import Path

class Phase2Launcher:
    def __init__(self):
        self.processes = []
        self.running = True
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print("\nShutting down Phase 2 systems...")
        self.running = False
        
        # Terminate all processes
        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
        
        sys.exit(0)
    
    async def start_phase1_systems(self):
        """Start Phase 1 monitoring systems"""
        try:
            # System Monitor
            system_monitor = subprocess.Popen([
                sys.executable, 
                '.claude/monitoring/system_monitor.py'
            ])
            self.processes.append(system_monitor)
            print("✅ Phase 1 System Monitor started")
            
            # MCP Health Monitor
            mcp_monitor = subprocess.Popen([
                sys.executable, 
                '.claude/coordination/mcp_health_monitor.py'
            ])
            self.processes.append(mcp_monitor)
            print("✅ Phase 1 MCP Health Monitor started")
            
            return True
        except Exception as e:
            print(f"❌ Failed to start Phase 1 systems: {e}")
            return False
    
    async def start_background_agent(self):
        """Start the Phase 2 background monitoring agent"""
        try:
            process = subprocess.Popen([
                sys.executable, 
                '.claude/background/background_monitor.py'
            ])
            self.processes.append(process)
            print("✅ Phase 2 Background Agent started")
            return True
        except Exception as e:
            print(f"❌ Failed to start Background Agent: {e}")
            return False
    
    async def start_dashboard_aggregator(self):
        """Start the enhanced dashboard data aggregator"""
        try:
            process = subprocess.Popen([
                sys.executable, 
                '.claude/dashboard/data_aggregator.py'
            ])
            self.processes.append(process)
            print("✅ Phase 2 Dashboard Data Aggregator started")
            return True
        except Exception as e:
            print(f"❌ Failed to start Dashboard Aggregator: {e}")
            return False
    
    def check_prerequisites(self):
        """Check if all required components exist"""
        required_files = [
            # Phase 1 files
            '.claude/hooks/simple_pre_tool_use.py',
            '.claude/hooks/simple_post_tool_use.py',
            '.claude/hooks/simple_stop.py',
            '.claude/monitoring/system_monitor.py',
            '.claude/coordination/mcp_health_monitor.py',
            '.claude/monitoring/dashboard.html',
            # Phase 2 files
            '.claude/background/background_monitor.py',
            '.claude/dashboard/enhanced_dashboard.html',
            '.claude/dashboard/data_aggregator.py'
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
                dead_processes = []
                for i, process in enumerate(self.processes):
                    if process.poll() is not None:
                        dead_processes.append((i, process))
                
                # Restart dead processes
                for i, process in dead_processes:
                    print(f"⚠️  Process {i} died, restarting...")
                    self.processes.remove(process)
                    
                    # Restart based on original order
                    if i == 0:  # System monitor
                        subprocess.Popen([sys.executable, '.claude/monitoring/system_monitor.py'])
                    elif i == 1:  # MCP coordinator
                        subprocess.Popen([sys.executable, '.claude/coordination/mcp_health_monitor.py'])
                    elif i == 2:  # Background agent
                        subprocess.Popen([sys.executable, '.claude/background/background_monitor.py'])
                    elif i == 3:  # Dashboard aggregator
                        subprocess.Popen([sys.executable, '.claude/dashboard/data_aggregator.py'])
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                print(f"Error in process monitoring: {e}")
                await asyncio.sleep(60)
    
    def display_status(self):
        """Display current system status"""
        print("\n" + "="*60)
        print("🚀 10X AGENTIC SETUP - PHASE 2 ACTIVE")
        print("="*60)
        print("📊 PHASE 1 SYSTEMS:")
        print("   • System Monitor: Collecting metrics every 30s")
        print("   • MCP Coordinator: Health checking servers")
        print("   • Hook System: Capturing tool usage patterns")
        print("")
        print("🤖 PHASE 2 ENHANCEMENTS:")
        print("   • Background Agent: Autonomous 24/7 monitoring")
        print("   • Enhanced Dashboard: Real-time intelligence")
        print("   • Pattern Learning: Adaptive optimization")
        print("")
        print("📈 DASHBOARDS:")
        print("   • Phase 1: .claude/monitoring/dashboard.html")
        print("   • Phase 2: .claude/dashboard/enhanced_dashboard.html")
        print("")
        print("🎯 CAPABILITIES:")
        print("   • Predictive resource management")
        print("   • Automatic cache clearing")
        print("   • Proactive MCP server restarts")
        print("   • Usage pattern recognition")
        print("   • Intelligent recommendations")
        print("="*60)
        print("Press Ctrl+C to shutdown all services\n")
    
    async def generate_test_data(self):
        """Generate initial test data to populate dashboards"""
        try:
            print("🔄 Generating initial dashboard data...")
            
            # Let systems run for a moment to collect data
            await asyncio.sleep(10)
            
            # Force data aggregation once
            from pathlib import Path
            if Path('.claude/dashboard/data_aggregator.py').exists():
                subprocess.run([
                    sys.executable, '-c',
                    'from data_aggregator import DashboardDataAggregator; '
                    'agg = DashboardDataAggregator(); '
                    'agg.generate_enhanced_dashboard_data()'
                ], cwd='.claude/dashboard', timeout=30)
                print("✅ Initial dashboard data generated")
            
        except Exception as e:
            print(f"⚠️  Failed to generate test data: {e}")
    
    async def run(self):
        """Main run function"""
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        print("🚀 Starting 10X Agentic Setup - Phase 2")
        
        # Check prerequisites
        if not self.check_prerequisites():
            print("❌ Prerequisites not met. Run Phase 1 setup first.")
            return False
        
        # Start all systems
        phase1_ok = await self.start_phase1_systems()
        agent_ok = await self.start_background_agent()
        dashboard_ok = await self.start_dashboard_aggregator()
        
        if not (phase1_ok and agent_ok and dashboard_ok):
            print("❌ Failed to start some services")
            return False
        
        # Generate initial test data
        await self.generate_test_data()
        
        # Display status
        self.display_status()
        
        # Monitor processes
        await self.monitor_processes()
        
        return True

async def main():
    launcher = Phase2Launcher()
    await launcher.run()

if __name__ == '__main__':
    asyncio.run(main())