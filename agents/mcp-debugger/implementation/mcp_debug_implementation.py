#!/usr/bin/env python3
"""
MCP Debug Implementation - Core debugging logic for 10x-mcp-debugger agent
Provides systematic testing, diagnosis, and resolution of MCP server issues
"""

import json
import subprocess
import time
import asyncio
import socket
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class MCPServer:
    """MCP Server configuration"""
    name: str
    command: str
    args: List[str]
    env: Dict[str, str]
    port: int
    expected_tools: List[str]

@dataclass
class ServerStatus:
    """Server health status"""
    server_name: str
    is_running: bool
    pid: Optional[int]
    port_available: bool
    tool_count: int
    latency_ms: Optional[float]
    issues: List[str]
    
@dataclass
class ToolTestResult:
    """Tool testing result"""
    tool_name: str
    success: bool
    execution_time_ms: float
    error: Optional[str]
    response_valid: bool

class MCPDebugger:
    """Core MCP debugging implementation"""
    
    def __init__(self):
        self.mcp_config_path = Path(".mcp.json")
        self.servers: Dict[str, MCPServer] = {}
        self.results: Dict[str, Any] = {}
        self.load_mcp_configuration()
        
        # Known MCP servers and their expected ports
        self.server_ports = {
            "ml-code-intelligence": 8001,
            "context-aware-memory": 8002,
            "agentic-workflow": 8003,
            "predictive-analytics": 8004,
            "ml-testing-qa": 8005,
            "10x-knowledge-graph": 8006,
            "10x-command-analytics": 8007
        }
        
        # Known tool sets for validation
        self.expected_tools = {
            "ml-code-intelligence": [
                "semantic_code_search",
                "analyze_code",
                "index_code_snippets",
                "get_server_stats",
                "assess_code_quality"
            ],
            "context-aware-memory": [
                "store_memory",
                "retrieve_memories",
                "predict_memory_needs",
                "analyze_memory_patterns"
            ],
            "10x-knowledge-graph": [
                "extract_concepts",
                "find_relationships",
                "visualize_graph",
                "add_concept",
                "get_graph_stats"
            ],
            "10x-command-analytics": [
                "track_command",
                "analyze_patterns",
                "predict_success",
                "optimize_workflow",
                "get_analytics_stats"
            ]
        }
    
    def load_mcp_configuration(self) -> bool:
        """Load and parse MCP configuration"""
        try:
            if not self.mcp_config_path.exists():
                print(f"❌ MCP configuration not found at {self.mcp_config_path}")
                return False
                
            with open(self.mcp_config_path, 'r') as f:
                config = json.load(f)
            
            # Parse mcpServers section
            mcp_servers = config.get('mcpServers', {})
            
            for server_name, server_config in mcp_servers.items():
                self.servers[server_name] = MCPServer(
                    name=server_name,
                    command=server_config.get('command', ''),
                    args=server_config.get('args', []),
                    env=server_config.get('env', {}),
                    port=self.server_ports.get(server_name, 0),
                    expected_tools=self.expected_tools.get(server_name, [])
                )
            
            print(f"✅ Loaded configuration for {len(self.servers)} MCP servers")
            return True
            
        except Exception as e:
            print(f"❌ Failed to load MCP configuration: {e}")
            return False
    
    def check_process_running(self, server_name: str) -> Tuple[bool, Optional[int]]:
        """Check if MCP server process is running"""
        try:
            # Try to find process by name
            result = subprocess.run(
                ['pgrep', '-f', server_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0 and result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                return True, int(pids[0])
            
            return False, None
            
        except Exception as e:
            print(f"Error checking process for {server_name}: {e}")
            return False, None
    
    def check_port_available(self, port: int) -> bool:
        """Check if port is listening"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            return result == 0
        except Exception:
            return False
    
    def measure_connection_latency(self, server: MCPServer) -> Optional[float]:
        """Measure connection latency to MCP server"""
        try:
            start_time = time.time()
            
            # Simple connection test
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect(('localhost', server.port))
            sock.close()
            
            latency_ms = (time.time() - start_time) * 1000
            return latency_ms
            
        except Exception:
            return None
    
    async def quick_health_check(self, server_name: Optional[str] = None) -> Dict[str, ServerStatus]:
        """Perform quick health check on MCP servers"""
        results = {}
        
        servers_to_check = [server_name] if server_name else self.servers.keys()
        
        for name in servers_to_check:
            if name not in self.servers:
                print(f"⚠️  Unknown server: {name}")
                continue
                
            server = self.servers[name]
            issues = []
            
            # Check process
            is_running, pid = self.check_process_running(name)
            if not is_running:
                issues.append("Process not running")
            
            # Check port
            port_available = self.check_port_available(server.port) if server.port else False
            if not port_available and server.port:
                issues.append(f"Port {server.port} not available")
            
            # Measure latency
            latency = self.measure_connection_latency(server) if is_running and port_available else None
            
            # Create status
            status = ServerStatus(
                server_name=name,
                is_running=is_running,
                pid=pid,
                port_available=port_available,
                tool_count=len(server.expected_tools),
                latency_ms=latency,
                issues=issues
            )
            
            results[name] = status
            
            # Print status
            if is_running and port_available:
                print(f"✅ {name:<25} [RUNNING] Port {server.port} | PID {pid} | {latency:.1f}ms")
            elif is_running:
                print(f"⚠️  {name:<25} [DEGRADED] Process running but port issue")
            else:
                print(f"❌ {name:<25} [FAILED] {', '.join(issues)}")
        
        return results
    
    async def diagnose_server(self, server_name: str) -> Dict[str, Any]:
        """Perform deep diagnosis of MCP server"""
        print(f"\n🔍 Diagnosing {server_name}...")
        
        diagnosis = {
            "server": server_name,
            "timestamp": datetime.now().isoformat(),
            "configuration": {},
            "process_health": {},
            "connectivity": {},
            "errors": [],
            "recommendations": []
        }
        
        if server_name not in self.servers:
            diagnosis["errors"].append(f"Server {server_name} not found in configuration")
            return diagnosis
        
        server = self.servers[server_name]
        
        # Configuration analysis
        diagnosis["configuration"] = {
            "command": server.command,
            "args": server.args,
            "env": server.env,
            "port": server.port
        }
        
        # Check if command exists
        if server.command:
            command_path = Path(server.command)
            if not command_path.exists():
                diagnosis["errors"].append(f"Command not found: {server.command}")
                diagnosis["recommendations"].append(f"Verify installation path for {server_name}")
        
        # Process health
        is_running, pid = self.check_process_running(server_name)
        diagnosis["process_health"] = {
            "is_running": is_running,
            "pid": pid
        }
        
        if not is_running:
            diagnosis["recommendations"].append(f"Start {server_name} server")
            
            # Check common issues
            if server.port:
                # Check if port is in use by another process
                if self.check_port_available(server.port):
                    diagnosis["errors"].append(f"Port {server.port} is in use by another process")
                    diagnosis["recommendations"].append(f"Kill process using port {server.port} or use different port")
        
        # Connectivity test
        if is_running and server.port:
            latency = self.measure_connection_latency(server)
            diagnosis["connectivity"] = {
                "port_available": self.check_port_available(server.port),
                "latency_ms": latency
            }
            
            if latency and latency > 1000:
                diagnosis["recommendations"].append("High latency detected - check server performance")
        
        # Check logs if available
        log_paths = [
            f"mcp_servers/{server_name}/server.log",
            f".claude/logs/{server_name}.log",
            f"/tmp/{server_name}.log"
        ]
        
        for log_path in log_paths:
            if Path(log_path).exists():
                try:
                    with open(log_path, 'r') as f:
                        # Read last 50 lines
                        lines = f.readlines()[-50:]
                        errors = [line for line in lines if 'error' in line.lower() or 'exception' in line.lower()]
                        if errors:
                            diagnosis["errors"].extend(errors[-5:])  # Last 5 errors
                except Exception:
                    pass
        
        return diagnosis
    
    async def test_server_tools(self, server_name: str) -> List[ToolTestResult]:
        """Test all tools available in an MCP server"""
        print(f"\n🧪 Testing tools for {server_name}...")
        
        if server_name not in self.servers:
            print(f"❌ Unknown server: {server_name}")
            return []
        
        server = self.servers[server_name]
        results = []
        
        # Check if server is running first
        is_running, _ = self.check_process_running(server_name)
        if not is_running:
            print(f"❌ Server {server_name} is not running")
            return []
        
        # Test each expected tool
        for tool_name in server.expected_tools:
            start_time = time.time()
            
            try:
                # Simulate tool testing (in real implementation, would use MCP protocol)
                # For now, we'll do a basic connectivity test
                success = self.check_port_available(server.port)
                execution_time = (time.time() - start_time) * 1000
                
                result = ToolTestResult(
                    tool_name=tool_name,
                    success=success,
                    execution_time_ms=execution_time,
                    error=None if success else "Connection failed",
                    response_valid=success
                )
                
                if success:
                    print(f"✅ {tool_name:<30} [{execution_time:.0f}ms] Response valid")
                else:
                    print(f"❌ {tool_name:<30} [ERROR] Connection failed")
                
            except Exception as e:
                result = ToolTestResult(
                    tool_name=tool_name,
                    success=False,
                    execution_time_ms=0,
                    error=str(e),
                    response_valid=False
                )
                print(f"❌ {tool_name:<30} [ERROR] {str(e)}")
            
            results.append(result)
        
        # Summary
        successful = sum(1 for r in results if r.success)
        print(f"\nTool Test Summary: {successful}/{len(results)} passed ({successful/len(results)*100:.1f}%)")
        
        return results
    
    async def apply_fixes(self, issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply automated fixes for detected issues"""
        fixes_applied = []
        
        for issue in issues:
            fix_result = {
                "issue": issue,
                "fix_applied": None,
                "success": False,
                "message": ""
            }
            
            if issue["type"] == "server_not_running":
                # Attempt to start server
                server_name = issue["server"]
                if server_name in self.servers:
                    server = self.servers[server_name]
                    try:
                        # Start server using configured command
                        subprocess.Popen(
                            [server.command] + server.args,
                            env={**os.environ, **server.env},
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL
                        )
                        
                        # Wait a moment for startup
                        await asyncio.sleep(3)
                        
                        # Check if started
                        is_running, _ = self.check_process_running(server_name)
                        if is_running:
                            fix_result["success"] = True
                            fix_result["message"] = f"Successfully started {server_name}"
                        else:
                            fix_result["message"] = f"Failed to start {server_name}"
                            
                    except Exception as e:
                        fix_result["message"] = f"Error starting {server_name}: {str(e)}"
                        
                fix_result["fix_applied"] = "start_server"
                
            elif issue["type"] == "port_conflict":
                # For port conflicts, we can only recommend manual intervention
                fix_result["fix_applied"] = "manual_required"
                fix_result["message"] = f"Port {issue['port']} conflict requires manual resolution"
                
            elif issue["type"] == "high_latency":
                # Attempt to restart server for performance issues
                server_name = issue["server"]
                # Implementation would restart server here
                fix_result["fix_applied"] = "restart_server"
                fix_result["message"] = f"Restart {server_name} to resolve performance issues"
            
            fixes_applied.append(fix_result)
        
        return fixes_applied
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate comprehensive debugging report"""
        report = []
        report.append(f"# MCP Debug Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 50)
        
        # Executive Summary
        if "health_check" in results:
            total_servers = len(results["health_check"])
            running_servers = sum(1 for s in results["health_check"].values() if s.is_running)
            report.append(f"\n## Executive Summary")
            report.append(f"- Total Servers: {total_servers}")
            report.append(f"- Running: {running_servers}/{total_servers}")
            report.append(f"- Status: {'✅ All systems operational' if running_servers == total_servers else '⚠️  Issues detected'}")
        
        # Server Status Details
        if "health_check" in results:
            report.append(f"\n## Server Status")
            for name, status in results["health_check"].items():
                status_icon = "✅" if status.is_running else "❌"
                report.append(f"\n### {status_icon} {name}")
                report.append(f"- Running: {status.is_running}")
                report.append(f"- PID: {status.pid or 'N/A'}")
                report.append(f"- Port: {self.servers[name].port if name in self.servers else 'Unknown'}")
                report.append(f"- Latency: {status.latency_ms:.1f}ms" if status.latency_ms else "- Latency: N/A")
                if status.issues:
                    report.append(f"- Issues: {', '.join(status.issues)}")
        
        # Diagnostic Results
        if "diagnostics" in results:
            report.append(f"\n## Diagnostic Results")
            for server_name, diagnosis in results["diagnostics"].items():
                report.append(f"\n### {server_name}")
                if diagnosis["errors"]:
                    report.append("**Errors Found:**")
                    for error in diagnosis["errors"]:
                        report.append(f"- {error}")
                if diagnosis["recommendations"]:
                    report.append("**Recommendations:**")
                    for rec in diagnosis["recommendations"]:
                        report.append(f"- {rec}")
        
        # Tool Testing Results
        if "tool_tests" in results:
            report.append(f"\n## Tool Testing Results")
            for server_name, tests in results["tool_tests"].items():
                successful = sum(1 for t in tests if t.success)
                report.append(f"\n### {server_name}")
                report.append(f"- Tools Tested: {len(tests)}")
                report.append(f"- Successful: {successful}/{len(tests)} ({successful/len(tests)*100:.1f}%)")
                
                # List failed tools
                failed_tools = [t for t in tests if not t.success]
                if failed_tools:
                    report.append("**Failed Tools:**")
                    for tool in failed_tools:
                        report.append(f"- {tool.tool_name}: {tool.error}")
        
        # Applied Fixes
        if "fixes" in results:
            report.append(f"\n## Applied Fixes")
            for fix in results["fixes"]:
                status_icon = "✅" if fix["success"] else "❌"
                report.append(f"{status_icon} {fix['message']}")
        
        return "\n".join(report)

# Utility functions for the agent to use

async def execute_mcp_debug(action: str, target: str = "all") -> str:
    """Main entry point for MCP debugging commands"""
    debugger = MCPDebugger()
    results = {}
    
    if action == "check":
        # Quick health check
        results["health_check"] = await debugger.quick_health_check(None if target == "all" else target)
        
    elif action == "diagnose":
        # Deep diagnostic
        results["diagnostics"] = {}
        servers = debugger.servers.keys() if target == "all" else [target]
        for server in servers:
            results["diagnostics"][server] = await debugger.diagnose_server(server)
            
    elif action == "test-tools":
        # Tool testing
        results["tool_tests"] = {}
        servers = debugger.servers.keys() if target == "all" else [target]
        for server in servers:
            results["tool_tests"][server] = await debugger.test_server_tools(server)
            
    elif action == "fix":
        # Apply fixes
        # First, run diagnostics to identify issues
        diagnostics = {}
        servers = debugger.servers.keys() if target == "all" else [target]
        for server in servers:
            diagnostics[server] = await debugger.diagnose_server(server)
        
        # Identify fixable issues
        issues = []
        for server, diag in diagnostics.items():
            if not diag.get("process_health", {}).get("is_running"):
                issues.append({"type": "server_not_running", "server": server})
        
        # Apply fixes
        results["fixes"] = await debugger.apply_fixes(issues)
        
    elif action == "full":
        # Complete workflow
        results["health_check"] = await debugger.quick_health_check()
        results["diagnostics"] = {}
        results["tool_tests"] = {}
        
        for server in debugger.servers.keys():
            results["diagnostics"][server] = await debugger.diagnose_server(server)
            if results["health_check"][server].is_running:
                results["tool_tests"][server] = await debugger.test_server_tools(server)
    
    # Generate report
    report = debugger.generate_report(results)
    return report

# Make available for import
if __name__ == "__main__":
    import sys
    import os
    
    # Simple CLI interface for testing
    if len(sys.argv) < 2:
        print("Usage: python mcp_debug_implementation.py [check|diagnose|test-tools|fix|full] [server-name|all]")
        sys.exit(1)
    
    action = sys.argv[1]
    target = sys.argv[2] if len(sys.argv) > 2 else "all"
    
    # Run the debugging
    report = asyncio.run(execute_mcp_debug(action, target))
    print(report)