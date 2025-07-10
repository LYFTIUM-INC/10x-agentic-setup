"""
Standard Response Formatter for ML-Enhanced MCP Servers
Ensures consistent response formats across all servers
"""

from typing import Any, Dict, Optional, List
from datetime import datetime
from dataclasses import dataclass, asdict
import time


@dataclass
class StandardResponse:
    """Standard response format for all MCP servers"""
    status: str = "success"  # success, error, partial
    data: Any = None
    error: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with timestamp"""
        response = {
            "status": self.status,
            "timestamp": datetime.now().isoformat(),
            "data": self.data
        }
        
        if self.error:
            response["error"] = self.error
            
        if self.metadata:
            response["metadata"] = self.metadata
            
        return response


class ResponseFormatter:
    """Utility class for formatting responses consistently"""
    
    def __init__(self, server_name: str, server_version: str = "1.0.0"):
        self.server_name = server_name
        self.server_version = server_version
        self.start_time = time.time()
    
    def success(self, data: Any, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Format a successful response"""
        base_metadata = {
            "server": self.server_name,
            "version": self.server_version,
            "processing_time": None  # Will be set by decorator
        }
        
        if metadata:
            base_metadata.update(metadata)
        
        response = StandardResponse(
            status="success",
            data=data,
            metadata=base_metadata
        )
        
        return response.to_dict()
    
    def error(self, error_message: str, error_code: Optional[str] = None, 
             details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Format an error response"""
        error_info = {
            "message": error_message,
            "code": error_code or "UNKNOWN_ERROR"
        }
        
        if details:
            error_info["details"] = details
        
        response = StandardResponse(
            status="error",
            error=error_info,
            metadata={
                "server": self.server_name,
                "version": self.server_version
            }
        )
        
        return response.to_dict()
    
    def partial(self, data: Any, completed: int, total: int, 
               metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Format a partial/progress response"""
        base_metadata = {
            "server": self.server_name,
            "version": self.server_version,
            "progress": {
                "completed": completed,
                "total": total,
                "percentage": round((completed / total) * 100, 2) if total > 0 else 0
            }
        }
        
        if metadata:
            base_metadata.update(metadata)
        
        response = StandardResponse(
            status="partial",
            data=data,
            metadata=base_metadata
        )
        
        return response.to_dict()
    
    def with_timing(self, func):
        """Decorator to add processing time to responses"""
        import functools
        import asyncio
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                processing_time = time.time() - start_time
                
                # Add processing time to metadata if it's a dict response
                if isinstance(result, dict) and "metadata" in result:
                    result["metadata"]["processing_time"] = round(processing_time, 3)
                    
                return result
            except Exception as e:
                processing_time = time.time() - start_time
                # Return error with processing time
                return self.error(
                    str(e),
                    error_code=type(e).__name__,
                    details={"processing_time": round(processing_time, 3)}
                )
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                processing_time = time.time() - start_time
                
                # Add processing time to metadata if it's a dict response
                if isinstance(result, dict) and "metadata" in result:
                    result["metadata"]["processing_time"] = round(processing_time, 3)
                    
                return result
            except Exception as e:
                processing_time = time.time() - start_time
                # Return error with processing time
                return self.error(
                    str(e),
                    error_code=type(e).__name__,
                    details={"processing_time": round(processing_time, 3)}
                )
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper


# Convenience functions for common response patterns
def success_response(data: Any, server_name: str, **metadata) -> Dict[str, Any]:
    """Quick success response"""
    formatter = ResponseFormatter(server_name)
    return formatter.success(data, metadata)


def error_response(message: str, server_name: str, code: Optional[str] = None, **details) -> Dict[str, Any]:
    """Quick error response"""
    formatter = ResponseFormatter(server_name)
    return formatter.error(message, code, details)


def progress_response(data: Any, completed: int, total: int, server_name: str, **metadata) -> Dict[str, Any]:
    """Quick progress response"""
    formatter = ResponseFormatter(server_name)
    return formatter.partial(data, completed, total, metadata)