#!/usr/bin/env python3
"""Universal MCP Server Launcher - Works from any directory"""

import sys
import os
import importlib.util
import argparse

# Add base paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, "shared", "src"))

# Server mappings
SERVERS = {
    "ml-code-intelligence": "ml_code_intelligence/src/server.py",
    "context-aware-memory": "context_aware_memory/src/server.py",
    "ml-testing-qa": "ml_testing_qa/src/server.py",
    "agentic-workflow": "agentic_workflow/src/server.py",
    "predictive-analytics": "predictive_analytics/src/server.py",
    "10x-knowledge-graph": "knowledge_graph/src/server.py",
    "10x-command-analytics": "command_analytics/src/server.py"
}

def main():
    parser = argparse.ArgumentParser(description="Universal MCP Server Launcher")
    parser.add_argument("server", choices=list(SERVERS.keys()), help="Server to launch")
    parser.add_argument("--port", type=int, help="Override default port")
    args, unknown = parser.parse_known_args()
    
    # Set working directory to server directory
    server_path = os.path.join(BASE_DIR, SERVERS[args.server])
    server_dir = os.path.dirname(os.path.dirname(server_path))
    os.chdir(server_dir)
    
    # Set port if provided
    if args.port:
        os.environ["MCP_SERVER_PORT"] = str(args.port)
    
    # Load and run the server
    spec = importlib.util.spec_from_file_location("server", server_path)
    server = importlib.util.module_from_spec(spec)
    sys.modules["server"] = server
    spec.loader.exec_module(server)

if __name__ == "__main__":
    main()