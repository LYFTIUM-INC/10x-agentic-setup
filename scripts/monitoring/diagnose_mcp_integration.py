#!/usr/bin/env python3
"""
Comprehensive MCP Integration Diagnostics
Diagnoses all MCP integration issues and provides detailed recommendations
"""

import os
import sys
import json
import subprocess
import socket
import time
import shutil
from pathlib import Path
from datetime import datetime

class MCPDiagnostics:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.mcp_servers_dir = self.project_root / "mcp_servers"
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "summary": {},
            "servers": {},
            "issues": [],
            "recommendations": []
        }
        
        # Expected MCP servers based on CLAUDE.md
        self.expected_servers = {
            "ml-code-intelligence": {"port": 8001, "dir": "ml_code_intelligence"},
            "context-aware-memory": {"port": 8002, "dir": "context_aware_memory"},
            "predictive-analytics": {"port": 8004, "dir": "predictive_analytics"},
            "ml-testing-qa": {"port": 8005, "dir": "ml_testing_qa"},
            "agentic-workflow": {"port": 8003, "dir": "agentic_workflow"},
            "10x-knowledge-graph": {"port": 8003, "dir": "knowledge_graph"},
            "10x-command-analytics": {"port": 8004, "dir": "command_analytics"},
            "chroma-rag": {"external": True, "process": "chroma-mcp"},
            "websearch": {"external": True, "process": "web-search-server"},
            "fetch": {"external": True, "process": "mcp_server_fetch"},
            "github": {"external": True, "process": "github"},
            "filesystem": {"built_in": True},
            "memory": {"external": True, "process": "mcp-server-memory"},
            "sqlite": {"built_in": True}
        }
    
    def check_docker_status(self):
        """Check Docker installation and status"""
        print("🐳 Checking Docker status...")
        
        # Check if docker is installed
        docker_installed = shutil.which('docker') is not None
        docker_compose_installed = shutil.which('docker-compose') is not None
        
        if not docker_installed:
            self.results["issues"].append({
                "severity": "HIGH",
                "component": "Docker",
                "issue": "Docker is not installed",
                "impact": "Cannot run containerized MCP servers"
            })
            self.results["recommendations"].append({
                "priority": "HIGH",
                "action": "Install Docker",
                "command": "sudo apt-get update && sudo apt-get install docker-ce docker-ce-cli containerd.io"
            })
        
        # Check if docker daemon is running
        try:
            result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
            docker_running = result.returncode == 0
            
            if not docker_running:
                self.results["issues"].append({
                    "severity": "HIGH",
                    "component": "Docker",
                    "issue": "Docker daemon is not running",
                    "impact": "Cannot start containerized MCP servers",
                    "details": result.stderr
                })
                self.results["recommendations"].append({
                    "priority": "HIGH",
                    "action": "Start Docker daemon",
                    "command": "sudo systemctl start docker"
                })
        except Exception as e:
            docker_running = False
            self.results["issues"].append({
                "severity": "HIGH",
                "component": "Docker",
                "issue": f"Cannot connect to Docker: {str(e)}",
                "impact": "MCP servers cannot be managed via Docker"
            })
        
        self.results["summary"]["docker_installed"] = docker_installed
        self.results["summary"]["docker_running"] = docker_running
        self.results["summary"]["docker_compose_installed"] = docker_compose_installed
        
        return docker_installed and docker_running
    
    def check_python_environment(self):
        """Check Python environment setup"""
        print("🐍 Checking Python environment...")
        
        # Check Python version
        python_version = sys.version
        self.results["summary"]["python_version"] = python_version
        
        # Check for virtual environment
        venv_path = self.project_root / ".venv"
        venv_exists = venv_path.exists()
        
        if not venv_exists:
            self.results["issues"].append({
                "severity": "MEDIUM",
                "component": "Python Environment",
                "issue": "No virtual environment found",
                "impact": "Dependencies may conflict with system packages"
            })
            self.results["recommendations"].append({
                "priority": "MEDIUM",
                "action": "Create virtual environment",
                "command": "python -m venv .venv && source .venv/bin/activate"
            })
        
        # Check required packages
        required_packages = ['mcp', 'httpx', 'pydantic', 'fastapi', 'uvicorn']
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            self.results["issues"].append({
                "severity": "HIGH",
                "component": "Python Dependencies",
                "issue": f"Missing packages: {', '.join(missing_packages)}",
                "impact": "MCP servers cannot run without required dependencies"
            })
            self.results["recommendations"].append({
                "priority": "HIGH",
                "action": "Install missing packages",
                "command": f"pip install {' '.join(missing_packages)}"
            })
        
        self.results["summary"]["venv_exists"] = venv_exists
        self.results["summary"]["missing_packages"] = missing_packages
        
        return len(missing_packages) == 0
    
    def check_server_files(self, server_name, server_config):
        """Check if server files exist and are valid"""
        if server_config.get('built_in') or server_config.get('external'):
            return True
            
        server_dir = self.mcp_servers_dir / server_config['dir']
        server_src = server_dir / "src"
        server_file = server_src / "server.py"
        
        issues = []
        
        if not server_dir.exists():
            issues.append(f"Server directory missing: {server_dir}")
        elif not server_src.exists():
            issues.append(f"Source directory missing: {server_src}")
        elif not server_file.exists():
            issues.append(f"Server file missing: {server_file}")
        else:
            # Check if server.py is valid Python
            try:
                with open(server_file, 'r') as f:
                    compile(f.read(), str(server_file), 'exec')
            except SyntaxError as e:
                issues.append(f"Syntax error in server.py: {e}")
        
        if issues:
            self.results["servers"][server_name] = {
                "status": "MISSING_FILES",
                "issues": issues
            }
            for issue in issues:
                self.results["issues"].append({
                    "severity": "HIGH",
                    "component": server_name,
                    "issue": issue,
                    "impact": f"{server_name} cannot start"
                })
        
        return len(issues) == 0
    
    def check_port_availability(self, server_name, port):
        """Check if a port is available or in use"""
        if not isinstance(port, int):
            return True
            
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return True
        except OSError:
            # Port is in use, check what's using it
            try:
                result = subprocess.run(
                    ['lsof', '-i', f':{port}', '-t'],
                    capture_output=True,
                    text=True
                )
                if result.stdout:
                    pid = result.stdout.strip()
                    # Get process info
                    proc_result = subprocess.run(
                        ['ps', '-p', pid, '-o', 'comm='],
                        capture_output=True,
                        text=True
                    )
                    process_name = proc_result.stdout.strip()
                    
                    self.results["servers"][server_name] = {
                        "status": "PORT_IN_USE",
                        "port": port,
                        "pid": pid,
                        "process": process_name
                    }
                    
                    if process_name and 'python' in process_name.lower():
                        # Likely an MCP server already running
                        return True
                    else:
                        self.results["issues"].append({
                            "severity": "MEDIUM",
                            "component": server_name,
                            "issue": f"Port {port} in use by {process_name} (PID: {pid})",
                            "impact": f"{server_name} cannot bind to port {port}"
                        })
                        self.results["recommendations"].append({
                            "priority": "MEDIUM",
                            "action": f"Stop process using port {port}",
                            "command": f"kill {pid}"
                        })
            except:
                pass
            
            return False
    
    def check_running_processes(self):
        """Check for running MCP server processes"""
        print("🔍 Checking running MCP processes...")
        
        running_servers = {}
        
        # Check for all expected server processes
        try:
            result = subprocess.run(
                ['ps', 'aux'],
                capture_output=True,
                text=True
            )
            
            processes = result.stdout.split('\n')
            
            for server_name, config in self.expected_servers.items():
                if config.get('external'):
                    # Check for external process
                    process_pattern = config.get('process', server_name)
                    matching_procs = [p for p in processes if process_pattern in p and 'grep' not in p]
                    
                    if matching_procs:
                        running_servers[server_name] = {
                            "status": "RUNNING",
                            "external": True,
                            "processes": len(matching_procs)
                        }
                elif not config.get('built_in'):
                    # Check for internal server process
                    server_dir = config.get('dir', '')
                    matching_procs = [p for p in processes if server_dir in p and 'server.py' in p and 'grep' not in p]
                    
                    if matching_procs:
                        running_servers[server_name] = {
                            "status": "RUNNING",
                            "processes": len(matching_procs),
                            "details": matching_procs[0][:100] + "..." if matching_procs else ""
                        }
        except Exception as e:
            self.results["issues"].append({
                "severity": "LOW",
                "component": "Process Check",
                "issue": f"Could not check processes: {e}",
                "impact": "Cannot determine which servers are running"
            })
        
        self.results["summary"]["running_servers"] = running_servers
        return running_servers
    
    def test_server_connectivity(self, server_name, port):
        """Test if server is responding on its port"""
        if not isinstance(port, int):
            return False
            
        try:
            # Try to connect to the server
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(2)
                result = s.connect_ex(('localhost', port))
                
                if result == 0:
                    # Port is open, try HTTP request
                    try:
                        import urllib.request
                        response = urllib.request.urlopen(f'http://localhost:{port}/health', timeout=2)
                        if response.status == 200:
                            return True
                    except:
                        # Server might not have /health endpoint but port is open
                        return True
                        
        except Exception:
            pass
            
        return False
    
    def analyze_integration_test_results(self):
        """Analyze existing integration test results"""
        print("📊 Analyzing integration test results...")
        
        test_results_file = self.project_root / "tests" / "mcp_integration_test_results.json"
        
        if test_results_file.exists():
            try:
                with open(test_results_file, 'r') as f:
                    test_results = json.load(f)
                
                self.results["summary"]["integration_test_results"] = {
                    "overall_success": test_results["summary"]["overall_integration_success"],
                    "server_compliance": test_results["summary"]["server_compliance_rate"],
                    "servers_meeting_targets": test_results["summary"]["servers_meeting_targets"],
                    "total_servers_tested": test_results["summary"]["total_servers_tested"]
                }
                
                # Analyze specific server issues
                for server_name, server_data in test_results["details"].items():
                    if server_data.get("meets_targets") is False:
                        reliability = server_data.get("reliability_score", 0)
                        
                        self.results["issues"].append({
                            "severity": "HIGH" if reliability < 0.9 else "MEDIUM",
                            "component": server_name,
                            "issue": f"Reliability score {reliability:.2%} below target",
                            "impact": "Server may fail intermittently",
                            "details": server_data.get("operation_success_rates", {})
                        })
                        
            except Exception as e:
                self.results["issues"].append({
                    "severity": "LOW",
                    "component": "Test Results",
                    "issue": f"Could not parse test results: {e}",
                    "impact": "Cannot determine historical performance"
                })
    
    def generate_recommendations(self):
        """Generate specific recommendations to fix issues"""
        print("💡 Generating recommendations...")
        
        # Count servers by status
        server_statuses = {}
        for server_name, config in self.expected_servers.items():
            if config.get('built_in'):
                continue
                
            status = self.results["servers"].get(server_name, {}).get("status", "UNKNOWN")
            server_statuses[status] = server_statuses.get(status, 0) + 1
        
        # Overall recommendation based on Docker status
        if not self.results["summary"].get("docker_running", False):
            self.results["recommendations"].insert(0, {
                "priority": "CRITICAL",
                "action": "Use Python-based local startup instead of Docker",
                "command": "python start_mcp_servers_local.py",
                "reason": "Docker is not available, but Python servers can run directly"
            })
        
        # If many servers are missing files
        missing_files_count = server_statuses.get("MISSING_FILES", 0)
        if missing_files_count > 3:
            self.results["recommendations"].append({
                "priority": "HIGH",
                "action": "Reinstall MCP servers from source",
                "command": "cd mcp_servers && pip install -r requirements.txt",
                "reason": f"{missing_files_count} servers have missing files"
            })
        
        # Calculate overall integration score
        total_servers = len([s for s in self.expected_servers.values() if not s.get('built_in')])
        running_servers = len(self.results["summary"].get("running_servers", {}))
        integration_score = running_servers / total_servers if total_servers > 0 else 0
        
        self.results["summary"]["integration_score"] = integration_score
        self.results["summary"]["target_score"] = 0.95
        self.results["summary"]["gap_to_target"] = 0.95 - integration_score
    
    def run_diagnostics(self):
        """Run all diagnostics"""
        print("🚀 Starting MCP Integration Diagnostics")
        print("=" * 60)
        
        # Run all checks
        docker_ok = self.check_docker_status()
        python_ok = self.check_python_environment()
        running_procs = self.check_running_processes()
        
        # Check each server
        for server_name, config in self.expected_servers.items():
            if config.get('built_in'):
                self.results["servers"][server_name] = {"status": "BUILT_IN"}
                continue
                
            if config.get('external'):
                # Check if external server is running
                if server_name in running_procs:
                    self.results["servers"][server_name] = running_procs[server_name]
                else:
                    self.results["servers"][server_name] = {"status": "NOT_RUNNING"}
                    self.results["issues"].append({
                        "severity": "MEDIUM",
                        "component": server_name,
                        "issue": "External MCP server not running",
                        "impact": f"{server_name} functionality unavailable"
                    })
                continue
            
            # Check internal servers
            files_ok = self.check_server_files(server_name, config)
            
            if files_ok:
                port = config.get('port')
                if port:
                    port_ok = self.check_port_availability(server_name, port)
                    connected = self.test_server_connectivity(server_name, port)
                    
                    if connected:
                        self.results["servers"][server_name] = {
                            "status": "RUNNING",
                            "port": port,
                            "responsive": True
                        }
                    elif server_name in running_procs:
                        self.results["servers"][server_name] = {
                            "status": "RUNNING_NOT_RESPONSIVE",
                            "port": port,
                            "responsive": False
                        }
                        self.results["issues"].append({
                            "severity": "HIGH",
                            "component": server_name,
                            "issue": f"Server running but not responding on port {port}",
                            "impact": "Server may be misconfigured or crashed"
                        })
                    else:
                        self.results["servers"][server_name] = {
                            "status": "NOT_RUNNING",
                            "port": port
                        }
        
        # Analyze test results
        self.analyze_integration_test_results()
        
        # Generate recommendations
        self.generate_recommendations()
        
        # Print results
        self.print_results()
        
        # Save detailed report
        report_file = self.project_root / "mcp_diagnostics_report.json"
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
        
        return self.results["summary"]["integration_score"]
    
    def print_results(self):
        """Print diagnostic results"""
        print("\n" + "=" * 60)
        print("📊 DIAGNOSTIC RESULTS")
        print("=" * 60)
        
        # Summary
        print("\n🔍 Summary:")
        print(f"  • Docker: {'✅ Running' if self.results['summary'].get('docker_running') else '❌ Not Running'}")
        print(f"  • Python Environment: {'✅ OK' if not self.results['summary'].get('missing_packages') else '❌ Missing Packages'}")
        print(f"  • Integration Score: {self.results['summary']['integration_score']:.1%} (Target: 95%)")
        print(f"  • Gap to Target: {self.results['summary']['gap_to_target']:.1%}")
        
        # Server Status
        print("\n📡 Server Status:")
        for server_name, server_info in self.results["servers"].items():
            status = server_info.get("status", "UNKNOWN")
            icon = {
                "RUNNING": "✅",
                "BUILT_IN": "🔧",
                "NOT_RUNNING": "❌",
                "PORT_IN_USE": "⚠️",
                "MISSING_FILES": "📁",
                "RUNNING_NOT_RESPONSIVE": "🔴"
            }.get(status, "❓")
            
            extra_info = ""
            if server_info.get("port"):
                extra_info = f" (port {server_info['port']})"
            elif server_info.get("external"):
                extra_info = " (external)"
                
            print(f"  {icon} {server_name}: {status}{extra_info}")
        
        # Critical Issues
        critical_issues = [i for i in self.results["issues"] if i["severity"] in ["CRITICAL", "HIGH"]]
        if critical_issues:
            print(f"\n🚨 Critical Issues ({len(critical_issues)}):")
            for issue in critical_issues[:5]:  # Show top 5
                print(f"  • {issue['component']}: {issue['issue']}")
        
        # Top Recommendations
        if self.results["recommendations"]:
            print(f"\n💡 Top Recommendations:")
            for i, rec in enumerate(self.results["recommendations"][:3], 1):
                print(f"\n  {i}. {rec['action']} [{rec['priority']}]")
                if rec.get('command'):
                    print(f"     Command: {rec['command']}")
                if rec.get('reason'):
                    print(f"     Reason: {rec['reason']}")

if __name__ == "__main__":
    diagnostics = MCPDiagnostics()
    score = diagnostics.run_diagnostics()
    
    print("\n" + "=" * 60)
    if score >= 0.95:
        print("🎉 MCP Integration is healthy! (95%+ reliability)")
        sys.exit(0)
    else:
        print(f"⚠️  MCP Integration needs attention ({score:.1%} < 95% target)")
        sys.exit(1)