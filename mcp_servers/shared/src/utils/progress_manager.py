"""
Progress Token Manager for ML-Enhanced MCP Servers
Handles progress notifications for long-running operations
"""

import asyncio
import time
from typing import Dict, Any, Optional, Callable, Awaitable
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ProgressUpdate:
    """Progress update information"""
    operation_id: str
    progress: float  # 0.0 to 1.0
    message: str
    current: Optional[int] = None
    total: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


class ProgressManager:
    """Manages progress tokens and notifications for long-running operations"""
    
    def __init__(self, server_name: str):
        self.server_name = server_name
        self.active_operations: Dict[str, Dict[str, Any]] = {}
        self.progress_callbacks: Dict[str, Callable[[ProgressUpdate], Awaitable[None]]] = {}
    
    async def start_operation(self, operation_id: str, progress_token: Optional[str] = None,
                            total_steps: Optional[int] = None) -> Dict[str, Any]:
        """Start tracking a long-running operation"""
        operation_info = {
            "operation_id": operation_id,
            "progress_token": progress_token,
            "start_time": time.time(),
            "total_steps": total_steps,
            "current_step": 0,
            "status": "running",
            "last_update": time.time()
        }
        
        self.active_operations[operation_id] = operation_info
        logger.info(f"Started operation: {operation_id}")
        
        # Send initial progress if token provided
        if progress_token:
            await self.send_progress(operation_id, 0.0, "Operation started")
        
        return operation_info
    
    async def update_progress(self, operation_id: str, current: int, total: Optional[int] = None,
                            message: Optional[str] = None) -> None:
        """Update progress for an operation"""
        if operation_id not in self.active_operations:
            logger.warning(f"Unknown operation: {operation_id}")
            return
        
        operation = self.active_operations[operation_id]
        operation["current_step"] = current
        
        if total is not None:
            operation["total_steps"] = total
        
        # Calculate progress percentage
        if operation["total_steps"]:
            progress = current / operation["total_steps"]
        else:
            progress = 0.0
        
        operation["last_update"] = time.time()
        
        # Send progress notification if token exists
        if operation["progress_token"]:
            await self.send_progress(
                operation_id,
                progress,
                message or f"Processing step {current}/{operation.get('total_steps', '?')}"
            )
    
    async def send_progress(self, operation_id: str, progress: float, message: str,
                          metadata: Optional[Dict[str, Any]] = None) -> None:
        """Send progress notification"""
        if operation_id not in self.active_operations:
            return
        
        operation = self.active_operations[operation_id]
        progress_token = operation.get("progress_token")
        
        if not progress_token:
            return
        
        update = ProgressUpdate(
            operation_id=operation_id,
            progress=min(1.0, max(0.0, progress)),  # Clamp to 0-1
            message=message,
            current=operation.get("current_step"),
            total=operation.get("total_steps"),
            metadata=metadata
        )
        
        # Call registered callback if exists
        if progress_token in self.progress_callbacks:
            try:
                await self.progress_callbacks[progress_token](update)
            except Exception as e:
                logger.error(f"Error sending progress update: {e}")
        
        logger.debug(f"Progress update for {operation_id}: {progress:.1%} - {message}")
    
    async def complete_operation(self, operation_id: str, 
                               message: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Mark an operation as complete"""
        if operation_id not in self.active_operations:
            logger.warning(f"Unknown operation: {operation_id}")
            return None
        
        operation = self.active_operations[operation_id]
        operation["status"] = "completed"
        operation["end_time"] = time.time()
        operation["duration"] = operation["end_time"] - operation["start_time"]
        
        # Send final progress
        if operation["progress_token"]:
            await self.send_progress(
                operation_id,
                1.0,
                message or "Operation completed",
                metadata={"duration": operation["duration"]}
            )
        
        # Remove from active operations
        del self.active_operations[operation_id]
        logger.info(f"Completed operation: {operation_id} in {operation['duration']:.2f}s")
        
        return operation
    
    async def fail_operation(self, operation_id: str, error: str) -> Optional[Dict[str, Any]]:
        """Mark an operation as failed"""
        if operation_id not in self.active_operations:
            logger.warning(f"Unknown operation: {operation_id}")
            return None
        
        operation = self.active_operations[operation_id]
        operation["status"] = "failed"
        operation["error"] = error
        operation["end_time"] = time.time()
        operation["duration"] = operation["end_time"] - operation["start_time"]
        
        # Send error notification
        if operation["progress_token"]:
            await self.send_progress(
                operation_id,
                operation.get("current_step", 0) / max(operation.get("total_steps", 1), 1),
                f"Operation failed: {error}",
                metadata={"error": error, "duration": operation["duration"]}
            )
        
        # Remove from active operations
        del self.active_operations[operation_id]
        logger.error(f"Failed operation: {operation_id} - {error}")
        
        return operation
    
    def register_progress_callback(self, progress_token: str, 
                                 callback: Callable[[ProgressUpdate], Awaitable[None]]) -> None:
        """Register a callback for progress updates"""
        self.progress_callbacks[progress_token] = callback
    
    def unregister_progress_callback(self, progress_token: str) -> None:
        """Unregister a progress callback"""
        if progress_token in self.progress_callbacks:
            del self.progress_callbacks[progress_token]
    
    def get_active_operations(self) -> Dict[str, Dict[str, Any]]:
        """Get all active operations"""
        return self.active_operations.copy()
    
    async def cleanup_stale_operations(self, timeout: int = 3600) -> int:
        """Clean up operations that haven't updated in a while"""
        now = time.time()
        stale_operations = []
        
        for op_id, op_info in self.active_operations.items():
            if now - op_info["last_update"] > timeout:
                stale_operations.append(op_id)
        
        for op_id in stale_operations:
            await self.fail_operation(op_id, "Operation timed out")
        
        return len(stale_operations)


# Context manager for progress tracking
class ProgressContext:
    """Context manager for automatic progress tracking"""
    
    def __init__(self, progress_manager: ProgressManager, operation_id: str,
                 progress_token: Optional[str] = None, total_steps: Optional[int] = None):
        self.progress_manager = progress_manager
        self.operation_id = operation_id
        self.progress_token = progress_token
        self.total_steps = total_steps
        self.current_step = 0
    
    async def __aenter__(self):
        await self.progress_manager.start_operation(
            self.operation_id, self.progress_token, self.total_steps
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            await self.progress_manager.complete_operation(self.operation_id)
        else:
            await self.progress_manager.fail_operation(
                self.operation_id, f"{exc_type.__name__}: {exc_val}"
            )
    
    async def update(self, message: str, increment: int = 1) -> None:
        """Update progress with a message"""
        self.current_step += increment
        await self.progress_manager.update_progress(
            self.operation_id, self.current_step, self.total_steps, message
        )
    
    async def set_progress(self, current: int, message: str) -> None:
        """Set absolute progress"""
        self.current_step = current
        await self.progress_manager.update_progress(
            self.operation_id, current, self.total_steps, message
        )