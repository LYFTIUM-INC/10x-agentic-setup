#!/usr/bin/env python3
"""
Test script to validate MCP server functionality
"""

import os
import sys
import json
import subprocess
import tempfile
from pathlib import Path
import time

def test_server_import(server_name, server_path):
    """Test if a server can be imported and run"""
    print(f"\n🧪 Testing {server_name} server...")
    
    # Create test script
    test_script = f"""
import sys
sys.path.insert(0, '{server_path}')
sys.path.insert(0, '{Path(__file__).parent / "mcp_servers" / "shared" / "src"}')

try:
    import server
    print("✅ Server imports successfully")
    
    # Try to get server info if available
    if hasattr(server, '__name__'):
        print(f"📦 Server module: {{server.__name__}}")
    
    # Check for MCP tools
    if hasattr(server, 'app') and hasattr(server.app, 'list_tools'):
        try:
            tools = server.app.list_tools()
            print(f"🔧 Available tools: {{len(tools.tools)}}")
            for tool in tools.tools[:3]:  # Show first 3 tools
                print(f"   - {{tool.name}}: {{tool.description[:50]}}...")
        except Exception as e:
            print(f"⚠️  Could not list tools: {{e}}")
    
    print("✅ Server test completed successfully")
    
except ImportError as e:
    print(f"❌ Import error: {{e}}")
    sys.exit(1)
except Exception as e:
    print(f"⚠️  Error during server test: {{e}}")
    sys.exit(1)
"""
    
    # Write and run test script
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(test_script)
        temp_script = f.name
    
    try:
        # Set proper environment
        env = os.environ.copy()
        env['PYTHONPATH'] = f"{server_path}:{Path(__file__).parent / 'mcp_servers' / 'shared' / 'src'}"
        
        result = subprocess.run([
            sys.executable, temp_script
        ], capture_output=True, text=True, env=env, timeout=30)
        
        if result.returncode == 0:
            print(result.stdout)
            return True
        else:
            print(f"❌ Server test failed:")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ Server test timed out")
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

def test_server_standalone(server_name, server_path):
    """Test if server can run standalone"""
    print(f"\n🚀 Testing {server_name} standalone execution...")
    
    server_file = Path(server_path) / "server.py"
    if not server_file.exists():
        print(f"❌ Server file not found: {server_file}")
        return False
    
    try:
        env = os.environ.copy()
        env['PYTHONPATH'] = f"{server_path}:{Path(__file__).parent / 'mcp_servers' / 'shared' / 'src'}"
        
        # Try to run server with --help or similar
        result = subprocess.run([
            sys.executable, str(server_file), "--help"
        ], capture_output=True, text=True, env=env, timeout=10)
        
        # Even if --help fails, check if import works
        if "ImportError" not in result.stderr and "ModuleNotFoundError" not in result.stderr:
            print("✅ Server can execute without import errors")
            return True
        else:
            print(f"⚠️  Server has import issues:")
            print(result.stderr[:200] + "..." if len(result.stderr) > 200 else result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Server execution timed out")
        return False
    except Exception as e:
        print(f"❌ Error testing standalone: {e}")
        return False

def main():
    """Main test function"""
    
    print("🚀 MCP Server Validation Test")
    print("=" * 50)
    
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
        
        # Test imports
        import_result = test_server_import(server_name, str(server_path))
        
        # Test standalone execution
        standalone_result = test_server_standalone(server_name, str(server_path))
        
        results[server_name] = import_result and standalone_result
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)
    
    for server_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{server_name}: {status}")
    
    total_servers = len(results)
    passing_servers = sum(results.values())
    
    print(f"\n📈 Results: {passing_servers}/{total_servers} servers validated")
    
    if passing_servers == total_servers:
        print("🎉 All MCP servers are functional!")
        return 0
    else:
        print("⚠️  Some MCP servers need attention")
        return 1

if __name__ == "__main__":
    sys.exit(main())