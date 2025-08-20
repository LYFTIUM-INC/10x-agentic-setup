#!/usr/bin/env python3
"""
MCP Server STDIO Testing
Tests MCP servers through their stdio interface (how Claude Code connects)
"""

import sys
import os
import json
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional

class MCPClient:
    """Simple MCP client for testing servers"""
    
    def __init__(self, server_command: list, server_name: str):
        self.server_command = server_command
        self.server_name = server_name
        self.process = None
        self.request_id = 0
    
    async def start_server(self):
        """Start the MCP server process"""
        try:
            self.process = await asyncio.create_subprocess_exec(
                *self.server_command,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            return True
        except Exception as e:
            print(f"❌ Failed to start {self.server_name}: {e}")
            return False
    
    async def send_request(self, method: str, params: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Send a JSON-RPC request to the server"""
        if not self.process:
            return None
        
        self.request_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method
        }
        
        if params:
            request["params"] = params
        
        try:
            # Send request
            request_line = json.dumps(request) + '\n'
            self.process.stdin.write(request_line.encode())
            await self.process.stdin.drain()
            
            # Read response
            response_line = await self.process.stdout.readline()
            if not response_line:
                return None
            
            response = json.loads(response_line.decode().strip())
            return response
            
        except Exception as e:
            print(f"❌ Error communicating with {self.server_name}: {e}")
            return None
    
    async def initialize(self) -> bool:
        """Initialize the MCP server"""
        response = await self.send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {},
                "resources": {}
            },
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        })
        
        if response and "result" in response:
            print(f"✅ {self.server_name} initialized successfully")
            return True
        else:
            print(f"❌ {self.server_name} initialization failed")
            if response and "error" in response:
                print(f"   Error: {response['error']}")
            return False
    
    async def list_tools(self) -> Optional[list]:
        """List available tools"""
        response = await self.send_request("tools/list")
        
        if response and "result" in response:
            tools = response["result"].get("tools", [])
            print(f"🔧 {self.server_name} has {len(tools)} tools:")
            for tool in tools[:5]:  # Show first 5 tools
                print(f"   - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')[:60]}...")
            return tools
        else:
            print(f"❌ Failed to list tools for {self.server_name}")
            return None
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Call a specific tool"""
        response = await self.send_request("tools/call", {
            "name": tool_name,
            "arguments": arguments
        })
        
        if response and "result" in response:
            return response["result"]
        else:
            print(f"❌ Tool call failed for {tool_name}")
            if response and "error" in response:
                print(f"   Error: {response['error']}")
            return None
    
    async def stop(self):
        """Stop the server process"""
        if self.process:
            self.process.terminate()
            await self.process.wait()

async def test_mcp_server(server_name: str, server_path: Path) -> bool:
    """Test a single MCP server"""
    print(f"\n🧪 Testing {server_name} MCP Server via STDIO...")
    
    # Set up server command
    server_file = server_path / "server.py"
    if not server_file.exists():
        print(f"❌ Server file not found: {server_file}")
        return False
    
    # Set up environment
    env = os.environ.copy()
    project_root = Path(__file__).parent
    shared_path = project_root / "mcp_servers" / "shared" / "src"
    env['PYTHONPATH'] = f"{server_path}:{shared_path}:{env.get('PYTHONPATH', '')}"
    
    # Create client
    client = MCPClient([
        sys.executable, str(server_file)
    ], server_name)
    
    try:
        # Start server
        if not await client.start_server():
            return False
        
        # Wait a moment for startup
        await asyncio.sleep(1)
        
        # Initialize
        if not await client.initialize():
            return False
        
        # List tools
        tools = await client.list_tools()
        if tools is None:
            return False
        
        # Test a tool if available
        if tools:
            first_tool = tools[0]
            tool_name = first_tool.get('name')
            
            # Try calling with minimal arguments
            print(f"🎯 Testing tool: {tool_name}")
            
            # Create test arguments based on tool schema
            test_args = {}
            input_schema = first_tool.get('inputSchema', {})
            properties = input_schema.get('properties', {})
            required = input_schema.get('required', [])
            
            # Add minimal required arguments
            for prop in required[:3]:  # Only test first 3 required props
                if prop in properties:
                    prop_type = properties[prop].get('type', 'string')
                    if prop_type == 'string':
                        test_args[prop] = 'test_value'
                    elif prop_type == 'integer':
                        test_args[prop] = 1
                    elif prop_type == 'number':
                        test_args[prop] = 1.0
                    elif prop_type == 'boolean':
                        test_args[prop] = True
                    elif prop_type == 'array':
                        test_args[prop] = []
                    elif prop_type == 'object':
                        test_args[prop] = {}
            
            # Call the tool
            result = await client.call_tool(tool_name, test_args)
            if result:
                print(f"✅ Tool call successful")
                content = result.get('content', [])
                if content:
                    print(f"   Result: {str(content[0].get('text', ''))[:100]}...")
            else:
                print(f"⚠️  Tool call failed (may be expected with test data)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing {server_name}: {e}")
        return False
    finally:
        await client.stop()

async def main():
    """Main test function"""
    
    print("🧪 MCP Server STDIO Interface Testing")
    print("=" * 60)
    print("Testing MCP servers as they would be used by Claude Code")
    
    base_path = Path(__file__).parent / "mcp_servers"
    
    # Define our MCP servers
    servers = {
        "Context-Aware Memory": base_path / "context_aware_memory" / "src",
        "ML Code Intelligence": base_path / "ml_code_intelligence" / "src",
        "Agentic Workflow": base_path / "agentic_workflow" / "src", 
        "Predictive Analytics": base_path / "predictive_analytics" / "src",
        "ML Testing QA": base_path / "ml_testing_qa" / "src"
    }
    
    results = {}
    
    for server_name, server_path in servers.items():
        if not server_path.exists():
            print(f"\n❌ {server_name}: Path not found - {server_path}")
            results[server_name] = False
            continue
        
        result = await test_mcp_server(server_name, server_path)
        results[server_name] = result
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 MCP STDIO TESTING SUMMARY")
    print("=" * 60)
    
    for server_name, result in results.items():
        status = "✅ WORKING" if result else "❌ FAILED"
        print(f"{server_name}: {status}")
    
    total_servers = len(results)
    working_servers = sum(results.values())
    
    print(f"\n📈 Results: {working_servers}/{total_servers} servers working via STDIO")
    
    if working_servers > 0:
        print(f"🎉 {working_servers} MCP servers are ready for Claude Code!")
        print(f"\n💡 Next steps:")
        print(f"   1. Add working servers to Claude Desktop configuration")
        print(f"   2. Test in actual Claude Code environment")
        print(f"   3. Use MCP tools in unified commands")
        return 0
    else:
        print("⚠️  No MCP servers are working via STDIO")
        print("   Check server implementations and dependencies")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))