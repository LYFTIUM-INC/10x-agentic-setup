#!/usr/bin/env python3
"""
MCP Server Verification and Setup Script
Checks for MCP server availability and provides setup instructions if missing.
"""

import os
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

class MCPServerVerifier:
    def __init__(self):
        self.base_path = Path(__file__).parent.parent.parent
        self.mcp_path = self.base_path / "mcp_servers"
        self.required_servers = {
            "ml-code-intelligence": {
                "description": "Semantic code search and quality assessment",
                "required_files": ["server.py", "config.json"],
                "features": ["semantic search", "code quality metrics", "pattern detection"]
            },
            "context-aware-memory": {
                "description": "Predictive memory loading with pattern matching",
                "required_files": ["server.py", "memory_store.json"],
                "features": ["context prediction", "memory persistence", "pattern learning"]
            },
            "predictive-analytics": {
                "description": "TimeGPT-inspired forecasting for development velocity",
                "required_files": ["server.py", "models/", "analytics_config.json"],
                "features": ["velocity prediction", "risk assessment", "trend analysis"]
            },
            "ml-testing-qa": {
                "description": "TestGen-LLM powered test generation",
                "required_files": ["server.py", "test_templates/", "qa_config.json"],
                "features": ["test generation", "bug prediction", "edge case discovery"]
            },
            "agentic-workflow": {
                "description": "Self-improving workflow orchestration",
                "required_files": ["server.py", "workflows/", "learning_engine.py"],
                "features": ["workflow optimization", "reinforcement learning", "pattern adaptation"]
            },
            "10x-knowledge-graph": {
                "description": "Concept extraction with relationship mapping",
                "required_files": ["server.py", "graph_db/", "extraction_engine.py"],
                "features": ["concept extraction", "relationship mapping", "knowledge synthesis"]
            },
            "10x-command-analytics": {
                "description": "Usage patterns and workflow optimization",
                "required_files": ["server.py", "analytics_db/", "optimization_engine.py"],
                "features": ["usage analytics", "command optimization", "workflow insights"]
            }
        }
        
    def check_server_exists(self, server_name: str) -> Tuple[bool, List[str]]:
        """Check if a server exists and has required files."""
        server_path = self.mcp_path / server_name
        if not server_path.exists():
            return False, []
            
        server_info = self.required_servers[server_name]
        missing_files = []
        
        for required_file in server_info["required_files"]:
            file_path = server_path / required_file
            if not file_path.exists():
                missing_files.append(required_file)
                
        return len(missing_files) == 0, missing_files
        
    def create_mock_server(self, server_name: str):
        """Create a mock MCP server structure for testing."""
        server_path = self.mcp_path / server_name
        server_path.mkdir(parents=True, exist_ok=True)
        
        server_info = self.required_servers[server_name]
        
        # Create mock server.py
        server_py_content = f'''#!/usr/bin/env python3
"""
Mock {server_name} MCP Server
{server_info["description"]}
"""

import json
import sys
from datetime import datetime

class {server_name.replace("-", "_").title()}Server:
    def __init__(self):
        self.name = "{server_name}"
        self.description = "{server_info['description']}"
        self.features = {json.dumps(server_info['features'])}
        self.initialized = datetime.now().isoformat()
        
    def handle_request(self, request):
        """Handle incoming MCP requests."""
        return {{
            "status": "mock_response",
            "server": self.name,
            "timestamp": datetime.now().isoformat()
        }}

if __name__ == "__main__":
    server = {server_name.replace("-", "_").title()}Server()
    print(f"Mock {{server.name}} server initialized at {{server.initialized}}")
'''
        
        with open(server_path / "server.py", "w") as f:
            f.write(server_py_content)
            
        # Create config files
        config_files = {
            "config.json": {
                "server_name": server_name,
                "version": "1.0.0",
                "features": server_info["features"],
                "status": "mock"
            },
            "analytics_config.json": {
                "analytics_enabled": True,
                "metrics": ["performance", "usage", "errors"]
            },
            "qa_config.json": {
                "test_generation": True,
                "bug_prediction": True,
                "coverage_target": 0.95
            }
        }
        
        for filename, content in config_files.items():
            if filename in server_info["required_files"]:
                with open(server_path / filename, "w") as f:
                    json.dump(content, f, indent=2)
                    
        # Create required directories
        for required_file in server_info["required_files"]:
            if required_file.endswith("/"):
                (server_path / required_file).mkdir(exist_ok=True)
                
    def verify_all_servers(self) -> Dict[str, Dict]:
        """Verify all required MCP servers."""
        results = {
            "timestamp": datetime.now().isoformat(),
            "servers": {},
            "summary": {
                "total": len(self.required_servers),
                "available": 0,
                "missing": 0,
                "incomplete": 0
            }
        }
        
        print("MCP SERVER VERIFICATION")
        print("="*60)
        
        for server_name, server_info in self.required_servers.items():
            exists, missing_files = self.check_server_exists(server_name)
            
            status = "available" if exists else ("incomplete" if missing_files else "missing")
            
            results["servers"][server_name] = {
                "status": status,
                "description": server_info["description"],
                "missing_files": missing_files,
                "features": server_info["features"]
            }
            
            if status == "available":
                results["summary"]["available"] += 1
                print(f"✅ {server_name}: Available")
            elif status == "incomplete":
                results["summary"]["incomplete"] += 1
                print(f"⚠️  {server_name}: Incomplete (missing: {', '.join(missing_files)})")
            else:
                results["summary"]["missing"] += 1
                print(f"❌ {server_name}: Not Found")
                
        return results
        
    def setup_missing_servers(self, create_mocks: bool = False):
        """Setup missing servers or provide instructions."""
        print("\nSETUP INSTRUCTIONS")
        print("="*60)
        
        for server_name, server_info in self.required_servers.items():
            exists, _ = self.check_server_exists(server_name)
            
            if not exists:
                if create_mocks:
                    print(f"\n📦 Creating mock for {server_name}...")
                    self.create_mock_server(server_name)
                    print(f"   ✓ Mock server created at: mcp_servers/{server_name}/")
                else:
                    print(f"\n📋 {server_name}:")
                    print(f"   Description: {server_info['description']}")
                    print(f"   Features: {', '.join(server_info['features'])}")
                    print(f"   Setup: Create directory 'mcp_servers/{server_name}/' with:")
                    for req_file in server_info["required_files"]:
                        print(f"     - {req_file}")
                        
    def save_verification_log(self, results: Dict):
        """Save verification results to log file."""
        log_dir = self.base_path / ".claude" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f"mcp_verification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(log_file, "w") as f:
            json.dump(results, f, indent=2)
            
        return log_file

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Verify and setup MCP servers")
    parser.add_argument("--create-mocks", action="store_true", 
                       help="Create mock servers for testing")
    parser.add_argument("--json", action="store_true",
                       help="Output results as JSON")
    
    args = parser.parse_args()
    
    verifier = MCPServerVerifier()
    results = verifier.verify_all_servers()
    
    # Get summary before conditional
    summary = results["summary"]
    
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        # Save log
        log_file = verifier.save_verification_log(results)
        
        # Print summary
        print(f"\nSUMMARY:")
        print(f"  Total Servers: {summary['total']}")
        print(f"  Available: {summary['available']}")
        print(f"  Missing: {summary['missing']}")
        print(f"  Incomplete: {summary['incomplete']}")
        print(f"\nLog saved to: {log_file}")
        
        # Setup instructions or mock creation
        if summary["missing"] > 0 or summary["incomplete"] > 0:
            verifier.setup_missing_servers(create_mocks=args.create_mocks)
            
    return 0 if summary["available"] == summary["total"] else 1

if __name__ == "__main__":
    exit(main())