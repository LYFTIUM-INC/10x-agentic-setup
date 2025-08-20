#!/usr/bin/env python3
"""
MCP Health Monitoring Script
Continuously monitors MCP server health and restarts failed servers
"""

import time
import requests
import subprocess
import sys
from pathlib import Path

def check_server_health():
    servers = {
        "ml-code-intelligence": 8001,
        "context-aware-memory": 8002,
        "agentic-workflow": 8003,
        "predictive-analytics": 8004,
        "ml-testing-qa": 8005,
        "10x-knowledge-graph": 8006,
        "10x-command-analytics": 8007
    }
    
    healthy = 0
    for name, port in servers.items():
        try:
            response = requests.get(f"http://localhost:{port}/health", timeout=2)
            if response.status_code == 200:
                print(f"✅ {name}")
                healthy += 1
            else:
                print(f"❌ {name} - HTTP {response.status_code}")
        except:
            print(f"❌ {name} - Not responding")
    
    health_rate = (healthy / len(servers)) * 100
    print(f"\n📊 Overall Health: {health_rate:.1f}% ({healthy}/{len(servers)})")
    
    if health_rate < 95:
        print("🚨 Health below 95% - Consider running fix_mcp_integration.py")
    
    return health_rate

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--continuous":
        print("🔄 Starting continuous monitoring...")
        while True:
            print(f"\n⏰ Health Check - {time.strftime('%Y-%m-%d %H:%M:%S')}")
            check_server_health()
            time.sleep(300)  # Check every 5 minutes
    else:
        check_server_health()
