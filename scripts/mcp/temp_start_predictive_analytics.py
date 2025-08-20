
import sys
import os

# Add paths
sys.path.insert(0, r'/home/dell/coding/bash/10x-agentic-setup/mcp_servers/predictive_analytics/src')
sys.path.insert(0, r'/home/dell/coding/bash/10x-agentic-setup/mcp_servers/shared/src')

# Set environment
os.environ['MCP_SERVER_PORT'] = '8004'
os.environ['MCP_SERVER_HOST'] = 'localhost'

# Import and run server
try:
    import server
    print(f'✅ {server.__name__} server started on port 8004')
    
    # Keep server running
    if hasattr(server, 'main'):
        server.main()
    elif hasattr(server, 'app'):
        # Run the MCP app
        import asyncio
        if hasattr(server.app, 'run'):
            asyncio.run(server.app.run())
        else:
            print(f'Server {server.__name__} loaded but no run method found')
            # Keep alive
            import time
            while True:
                time.sleep(1)
    else:
        print(f'Server {server.__name__} loaded but no main function found')
        # Keep alive anyway
        import time
        while True:
            time.sleep(1)
            
except KeyboardInterrupt:
    print(f'Server Predictive Analytics stopping...')
except Exception as e:
    print(f'Error in server Predictive Analytics: {e}')
    import traceback
    traceback.print_exc()
