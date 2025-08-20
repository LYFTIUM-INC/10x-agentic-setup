#!/usr/bin/env python3
"""
10X Command Analytics MCP Server

Provides usage pattern analysis and command optimization capabilities.
"""

import asyncio
import sys
from pathlib import Path
import time
import json

# Add the parent directory to the path to import shared modules
sys.path.append(str(Path(__file__).parent.parent.parent / "shared" / "src"))

from base_server import BaseMCPServer, ServerConfig
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server

class CommandAnalyticsServer(BaseMCPServer):
    """10X Command Analytics MCP Server for usage pattern analysis"""
    
    def __init__(self):
        config = ServerConfig(
            name="10x-command-analytics",
            version="1.0.0",
            debug=False
        )
        super().__init__(config)
        self.command_history = []
        self.usage_patterns = {}
        self.success_rates = {}
    
    def setup_tools(self):
        """Setup command analytics tools using FastMCP decorators"""
        
        @self.register_tool(name="track_command", description="Track command usage")
        async def track_command(command: str = "", success: bool = True, duration: float = 0.0) -> dict:
            """Track command usage"""
            
            # Record command usage
            self.command_history.append({
                "command": command,
                "timestamp": time.time(),
                "success": success,
                "duration": duration
            })
            
            # Update usage patterns
            if command not in self.usage_patterns:
                self.usage_patterns[command] = 0
            self.usage_patterns[command] += 1
            
            # Update success rates
            if command not in self.success_rates:
                self.success_rates[command] = {"total": 0, "successful": 0}
            
            self.success_rates[command]["total"] += 1
            if success:
                self.success_rates[command]["successful"] += 1
            
            return self.response_formatter.success({
                "command": command,
                "tracked": True,
                "total_executions": len(self.command_history)
            })
        
        @self.register_tool(name="analyze_patterns", description="Analyze command usage patterns")
        async def analyze_patterns(timeframe: str = "all") -> dict:
            """Analyze command usage patterns"""
            
            # Analyze patterns
            most_used = sorted(self.usage_patterns.items(), 
                              key=lambda x: x[1], reverse=True)[:5]
            
            success_analysis = {}
            for cmd, rates in self.success_rates.items():
                if rates["total"] > 0:
                    success_analysis[cmd] = rates["successful"] / rates["total"]
            
            return self.response_formatter.success({
                "timeframe": timeframe,
                "most_used_commands": most_used,
                "success_rates": success_analysis,
                "total_commands": len(self.command_history)
            })
        
        @self.register_tool(name="predict_success", description="Predict command success rate")
        async def predict_success(command: str = "") -> dict:
            """Predict command success rate"""
            
            # Simple prediction based on historical data
            if command in self.success_rates:
                rates = self.success_rates[command]
                if rates["total"] > 0:
                    predicted_rate = rates["successful"] / rates["total"]
                else:
                    predicted_rate = 0.5  # Default for new commands
            else:
                predicted_rate = 0.7  # Default for unknown commands
            
            return self.response_formatter.success({
                "command": command,
                "predicted_success_rate": predicted_rate,
                "confidence": 0.8,
                "historical_executions": self.success_rates.get(command, {}).get("total", 0)
            })
        
        @self.register_tool(name="optimize_workflow", description="Suggest workflow optimizations")
        async def optimize_workflow(workflow: list = None) -> dict:
            """Suggest workflow optimizations"""
            if workflow is None:
                workflow = []
            
            # Simple optimization suggestions
            optimizations = [
                "Consider batching similar commands together",
                "Use parallel execution for independent operations",
                "Cache frequently accessed data",
                "Implement error handling for low-success commands"
            ]
            
            return self.response_formatter.success({
                "workflow": workflow,
                "optimizations": optimizations,
                "potential_improvement": "15-25%"
            })
        
        @self.register_tool(name="get_analytics_stats", description="Get comprehensive analytics statistics")
        async def get_analytics_stats() -> dict:
            """Get comprehensive analytics statistics"""
            return self.response_formatter.success({
                "total_commands_tracked": len(self.command_history),
                "unique_commands": len(self.usage_patterns),
                "average_success_rate": sum(
                    rates["successful"] / rates["total"] 
                    for rates in self.success_rates.values() 
                    if rates["total"] > 0
                ) / len(self.success_rates) if self.success_rates else 0.0
            })
    
    def setup_resources(self):
        """Setup command analytics resources using FastMCP decorators"""
        
        @self.register_resource(uri="analytics://usage", name="Command Usage Statistics",
                              description="Statistics about command usage patterns")
        async def get_usage_stats() -> dict:
            """Get command usage statistics"""
            return self.response_formatter.success({
                "usage_patterns": self.usage_patterns,
                "total_commands": len(self.command_history)
            })
        
        @self.register_resource(uri="analytics://success_rates", name="Command Success Rates",
                              description="Success rates for different commands")
        async def get_success_rates() -> dict:
            """Get command success rates"""
            return self.response_formatter.success({
                "success_rates": self.success_rates
            })
        
        @self.register_resource(uri="analytics://history", name="Command History",
                              description="Complete command execution history")
        async def get_command_history() -> dict:
            """Get command execution history"""
            return self.response_formatter.success({
                "history": self.command_history[-100:],  # Last 100 commands
                "total_entries": len(self.command_history)
            })

def main():
    """Main entry point"""
    server = CommandAnalyticsServer()
    
    # Setup tools and resources
    server.setup_tools()
    server.setup_resources()
    
    # Run the server using FastMCP
    server.run("stdio")

if __name__ == "__main__":
    main()