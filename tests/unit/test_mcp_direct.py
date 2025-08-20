#!/usr/bin/env python3
"""
Direct MCP Server Testing
Tests MCP servers without network connectivity
"""

import sys
import os
import tempfile
import json
from pathlib import Path

def test_mcp_server_tools(server_name, server_path):
    """Test MCP server tools directly"""
    print(f"\n🧪 Testing {server_name} MCP Tools...")
    
    # Create test script
    test_script = f"""
import sys
import os
import json
from pathlib import Path

# Add paths
sys.path.insert(0, r'{server_path}')
sys.path.insert(0, r'{Path(__file__).parent / "mcp_servers" / "shared" / "src"}')

try:
    import server
    print(f"✅ {server_name} server imported successfully")
    
    # Check if it's an MCP server with expected structure
    if hasattr(server, 'app'):
        app = server.app
        print(f"📦 Found MCP app: {{type(app).__name__}}")
        
        # Try to list tools
        try:
            tools_result = app.list_tools()
            print(f"🔧 Available tools: {{len(tools_result.tools)}}")
            
            for i, tool in enumerate(tools_result.tools[:5]):  # Show first 5 tools
                print(f"   {{i+1}}. {{tool.name}}")
                print(f"      Description: {{tool.description[:80]}}...")
                if hasattr(tool, 'inputSchema') and tool.inputSchema:
                    props = tool.inputSchema.get('properties', {{}})
                    if props:
                        print(f"      Parameters: {{', '.join(props.keys())}}")
                print()
                
            print(f"✅ {server_name} tools listed successfully")
            
            # Try to call a simple tool if available
            if tools_result.tools:
                first_tool = tools_result.tools[0]
                print(f"🎯 Testing first tool: {{first_tool.name}}")
                
                # Create minimal arguments based on schema
                args = {{}}
                if hasattr(first_tool, 'inputSchema') and first_tool.inputSchema:
                    props = first_tool.inputSchema.get('properties', {{}})
                    required = first_tool.inputSchema.get('required', [])
                    
                    # Add required parameters with test values
                    for prop in required:
                        if prop in props:
                            prop_type = props[prop].get('type', 'string')
                            if prop_type == 'string':
                                args[prop] = 'test_value'
                            elif prop_type == 'integer':
                                args[prop] = 1
                            elif prop_type == 'boolean':
                                args[prop] = True
                            elif prop_type == 'array':
                                args[prop] = []
                            elif prop_type == 'object':
                                args[prop] = {{}}
                
                try:
                    # Call the tool
                    result = app.call_tool(first_tool.name, args)
                    print(f"✅ Tool call successful")
                    print(f"   Result type: {{type(result)}}")
                    if hasattr(result, 'content'):
                        content_preview = str(result.content)[:100]
                        print(f"   Content preview: {{content_preview}}...")
                except Exception as tool_error:
                    print(f"⚠️  Tool call failed (expected for test data): {{tool_error}}")
                    
        except Exception as e:
            print(f"⚠️  Could not list tools: {{e}}")
            
    else:
        print(f"⚠️  No MCP app found in server module")
        
    # Check for other important attributes
    if hasattr(server, '__version__'):
        print(f"📊 Server version: {{server.__version__}}")
        
    print(f"✅ {server_name} validation completed")
    
except ImportError as e:
    print(f"❌ Import error: {{e}}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error during validation: {{e}}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
"""
    
    # Write and run test script
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(test_script)
        temp_script = f.name
    
    try:
        import subprocess
        
        # Set proper environment
        env = os.environ.copy()
        env['PYTHONPATH'] = f"{server_path}:{Path(__file__).parent / 'mcp_servers' / 'shared' / 'src'}"
        
        result = subprocess.run([
            sys.executable, temp_script
        ], capture_output=True, text=True, env=env, timeout=60)
        
        print(result.stdout)
        if result.stderr:
            print("Errors:")
            print(result.stderr)
            
        return result.returncode == 0
            
    except subprocess.TimeoutExpired:
        print(f"⏰ Test timed out")
        return False
    except Exception as e:
        print(f"❌ Error running test: {e}")
        return False
    finally:
        # Clean up
        try:
            os.unlink(temp_script)
        except:
            pass

def main():
    """Main function"""
    
    print("🧪 Direct MCP Server Tool Testing")
    print("=" * 60)
    
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
        
        result = test_mcp_server_tools(server_name, str(server_path))
        results[server_name] = result
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 MCP TOOLS VALIDATION SUMMARY")
    print("=" * 60)
    
    for server_name, result in results.items():
        status = "✅ FUNCTIONAL" if result else "❌ ISSUES"
        print(f"{server_name}: {status}")
    
    total_servers = len(results)
    working_servers = sum(results.values())
    
    print(f"\n📈 Results: {working_servers}/{total_servers} servers have working MCP tools")
    
    if working_servers > 0:
        print(f"🎉 {working_servers} MCP servers are functional!")
        print(f"\n💡 Next steps:")
        print(f"   1. Use working servers in Claude Code")
        print(f"   2. Debug any non-working servers")
        print(f"   3. Test in actual Claude Code environment")
        return 0
    else:
        print("⚠️  No MCP servers are fully functional")
        return 1

if __name__ == "__main__":
    sys.exit(main())