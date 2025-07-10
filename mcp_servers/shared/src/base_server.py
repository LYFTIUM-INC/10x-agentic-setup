"""
Base MCP Server Template with FastMCP and Best Practices
Following 2024 MCP development standards and security guidelines
"""

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from typing import AsyncIterator, Dict, Any, Optional, List
from dataclasses import dataclass
from functools import wraps

from pydantic import BaseModel, Field, validator
from mcp.server.fastmcp import Context, FastMCP

# Import new utilities
from .utils.response_formatter import ResponseFormatter
from .utils.progress_manager import ProgressManager, ProgressContext
from .utils.health_checker import HealthChecker

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ServerConfig:
    """Server configuration with validation"""
    name: str
    version: str = "1.0.0"
    debug: bool = False
    max_workers: int = 4
    cache_ttl: int = 300
    rate_limit: int = 100  # requests per minute


class BaseRequest(BaseModel):
    """Base request model with validation"""
    request_id: Optional[str] = Field(None, description="Request identifier")
    
    @validator('request_id')
    def validate_request_id(cls, v):
        if v and len(v) > 100:
            raise ValueError("Request ID too long")
        return v


class BaseResponse(BaseModel):
    """Base response model with metadata"""
    success: bool = Field(..., description="Operation success status")
    data: Any = Field(None, description="Response data")
    error: Optional[str] = Field(None, description="Error message if any")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    timestamp: float = Field(default_factory=time.time, description="Response timestamp")


class CacheManager:
    """Intelligent caching system for MCP servers"""
    
    def __init__(self, ttl: int = 300):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl = ttl
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value with TTL check"""
        if key in self.cache:
            entry = self.cache[key]
            if time.time() - entry['timestamp'] < self.ttl:
                logger.debug(f"Cache hit for key: {key}")
                return entry['value']
            else:
                del self.cache[key]
                logger.debug(f"Cache expired for key: {key}")
        return None
    
    def set(self, key: str, value: Any) -> None:
        """Set cached value with timestamp"""
        self.cache[key] = {
            'value': value,
            'timestamp': time.time()
        }
        logger.debug(f"Cache set for key: {key}")
    
    def clear(self) -> None:
        """Clear all cached values"""
        self.cache.clear()
        logger.info("Cache cleared")


class SecurityManager:
    """Security manager for input validation and rate limiting"""
    
    def __init__(self, rate_limit: int = 100):
        self.rate_limit = rate_limit
        self.request_counts: Dict[str, List[float]] = {}
    
    def validate_input(self, data: Any) -> bool:
        """Validate input for security threats"""
        if isinstance(data, str):
            # Check for common injection patterns
            dangerous_patterns = ['<script', 'javascript:', 'eval(', 'exec(']
            data_lower = data.lower()
            for pattern in dangerous_patterns:
                if pattern in data_lower:
                    logger.warning(f"Dangerous pattern detected: {pattern}")
                    return False
        return True
    
    def check_rate_limit(self, client_id: str) -> bool:
        """Check if client is within rate limits"""
        now = time.time()
        if client_id not in self.request_counts:
            self.request_counts[client_id] = []
        
        # Remove old requests (older than 1 minute)
        self.request_counts[client_id] = [
            req_time for req_time in self.request_counts[client_id]
            if now - req_time < 60
        ]
        
        # Check rate limit
        if len(self.request_counts[client_id]) >= self.rate_limit:
            logger.warning(f"Rate limit exceeded for client: {client_id}")
            return False
        
        # Add current request
        self.request_counts[client_id].append(now)
        return True


class ResourceManager:
    """Resource management for memory and performance monitoring"""
    
    def __init__(self, max_memory_mb: int = 1000):
        self.max_memory_mb = max_memory_mb
        self.active_operations: set = set()
    
    @asynccontextmanager
    async def managed_operation(self, operation_id: str) -> AsyncIterator[None]:
        """Context manager for operation resource management"""
        self.active_operations.add(operation_id)
        start_time = time.time()
        
        try:
            logger.info(f"Starting operation: {operation_id}")
            yield
        except Exception as e:
            logger.error(f"Operation {operation_id} failed: {e}")
            raise
        finally:
            self.active_operations.discard(operation_id)
            duration = time.time() - start_time
            logger.info(f"Completed operation: {operation_id} in {duration:.2f}s")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current resource usage statistics"""
        return {
            "active_operations": len(self.active_operations),
            "operations_list": list(self.active_operations)
        }


class BaseMCPServer:
    """Base MCP Server with all best practices integrated"""
    
    def __init__(self, config: ServerConfig):
        self.config = config
        self.mcp = FastMCP(name=config.name)
        self.cache = CacheManager(ttl=config.cache_ttl)
        self.security = SecurityManager(rate_limit=config.rate_limit)
        self.resources = ResourceManager()
        
        # Initialize new components
        self.response_formatter = ResponseFormatter(config.name, config.version)
        self.progress_manager = ProgressManager(config.name)
        self.health_checker = HealthChecker(config.name, config.version)
        
        # Set up lifecycle management
        self.mcp.lifespan = self._lifespan
        
        # Register built-in health resources
        self._register_health_resources()
        
        logger.info(f"Initialized {config.name} MCP Server v{config.version}")
    
    @asynccontextmanager
    async def _lifespan(self) -> AsyncIterator[None]:
        """Lifecycle management for startup/shutdown"""
        logger.info(f"Starting {self.config.name} MCP Server...")
        await self._startup()
        try:
            yield
        finally:
            logger.info(f"Shutting down {self.config.name} MCP Server...")
            await self._shutdown()
    
    async def _startup(self) -> None:
        """Server startup logic - override in subclasses"""
        # Start health check monitoring
        await self.health_checker.start_periodic_checks()
    
    async def _shutdown(self) -> None:
        """Server shutdown logic - override in subclasses"""
        # Stop health checks
        await self.health_checker.stop_periodic_checks()
        self.cache.clear()
    
    def _register_health_resources(self) -> None:
        """Register built-in health check resources"""
        @self.mcp.resource("health://status")
        async def get_health_status() -> Dict[str, Any]:
            """Get server health status"""
            status = await self.health_checker.get_health_status()
            return self.response_formatter.success(status)
        
        @self.mcp.resource("health://metrics")
        async def get_health_metrics() -> Dict[str, Any]:
            """Get server performance metrics"""
            metrics = await self.health_checker.get_metrics()
            return self.response_formatter.success(metrics)
        
        @self.mcp.resource("health://system")
        async def get_system_info() -> Dict[str, Any]:
            """Get system information"""
            system_info = await self.health_checker._get_system_metrics()
            return self.response_formatter.success(system_info)
    
    def with_caching(self, cache_key_func=None):
        """Decorator for adding caching to tools"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Generate cache key
                if cache_key_func:
                    cache_key = cache_key_func(*args, **kwargs)
                else:
                    cache_key = f"{func.__name__}_{hash(str(args) + str(kwargs))}"
                
                # Check cache
                cached_result = self.cache.get(cache_key)
                if cached_result is not None:
                    return cached_result
                
                # Execute function
                result = await func(*args, **kwargs)
                
                # Cache result
                self.cache.set(cache_key, result)
                return result
            return wrapper
        return decorator
    
    def with_security(self, func):
        """Decorator for adding security validation"""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Validate all string inputs
            for arg in args:
                if not self.security.validate_input(arg):
                    raise ValueError("Invalid input detected")
            
            for value in kwargs.values():
                if not self.security.validate_input(value):
                    raise ValueError("Invalid input detected")
            
            return await func(*args, **kwargs)
        return wrapper
    
    def with_monitoring(self, func):
        """Decorator for adding performance monitoring"""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            operation_id = f"{func.__name__}_{int(time.time())}"
            
            async with self.resources.managed_operation(operation_id):
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    duration = time.time() - start_time
                    logger.info(f"Tool {func.__name__} completed in {duration:.2f}s")
                    return result
                except Exception as e:
                    duration = time.time() - start_time
                    logger.error(f"Tool {func.__name__} failed after {duration:.2f}s: {e}")
                    raise
        return wrapper
    
    def register_tool(self, name: str = None, description: str = None):
        """Register a tool with the MCP server"""
        def decorator(func):
            # Apply all decorators
            enhanced_func = self.with_monitoring(
                self.with_security(
                    self.with_caching()(func)
                )
            )
            
            # Register with MCP
            return self.mcp.tool(name=name, description=description)(enhanced_func)
        return decorator
    
    def register_resource(self, uri: str, name: str = None, description: str = None):
        """Register a resource with the MCP server"""
        def decorator(func):
            enhanced_func = self.with_monitoring(
                self.with_security(func)
            )
            return self.mcp.resource(uri=uri, name=name, description=description)(enhanced_func)
        return decorator
    
    def register_prompt(self, name: str, description: str = None, arguments: List[Dict[str, Any]] = None):
        """Register a prompt template with the MCP server"""
        def decorator(func):
            # Create prompt configuration
            prompt_config = {
                "name": name,
                "description": description or f"Prompt template: {name}",
                "arguments": arguments or []
            }
            
            # Register with MCP
            return self.mcp.prompt(**prompt_config)(func)
        return decorator
    
    async def get_server_stats(self) -> Dict[str, Any]:
        """Get comprehensive server statistics"""
        stats = {
            "server_name": self.config.name,
            "version": self.config.version,
            "uptime": time.time() - self.health_checker.start_time,
            "cache_size": len(self.cache.cache),
            "resource_stats": self.resources.get_stats(),
            "active_operations": len(self.progress_manager.active_operations),
            "config": {
                "debug": self.config.debug,
                "max_workers": self.config.max_workers,
                "cache_ttl": self.config.cache_ttl,
                "rate_limit": self.config.rate_limit
            }
        }
        return self.response_formatter.success(stats)
    
    def run(self, transport="stdio"):
        """Run the MCP server"""
        logger.info(f"Starting {self.config.name} MCP Server with {transport} transport")
        if transport == "stdio":
            import sys
            from mcp.server.stdio import run_server
            asyncio.run(run_server(self.mcp, sys.stdin, sys.stdout))
        else:
            raise ValueError(f"Unsupported transport: {transport}")


# Example usage and testing
if __name__ == "__main__":
    # Create a test server
    config = ServerConfig(name="test-server", debug=True)
    server = BaseMCPServer(config)
    
    @server.register_tool(name="hello", description="Say hello")
    async def hello_world(name: str) -> str:
        """Simple hello world tool for testing"""
        return f"Hello, {name}!"
    
    @server.register_tool(name="stats", description="Get server statistics")
    async def get_stats() -> Dict[str, Any]:
        """Get server statistics"""
        return await server.get_server_stats()
    
    # Run the server
    server.run()