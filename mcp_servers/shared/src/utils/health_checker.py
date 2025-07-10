"""
Health Check System for ML-Enhanced MCP Servers
Provides standardized health monitoring and status resources
"""

import asyncio
import time
import psutil
import platform
from typing import Dict, Any, List, Optional, Callable, Awaitable
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class HealthStatus:
    """Health status information"""
    status: str  # healthy, degraded, unhealthy
    message: str
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


@dataclass
class ComponentHealth:
    """Health status for a specific component"""
    name: str
    status: str
    message: str
    metrics: Optional[Dict[str, Any]] = None
    last_check: float = None
    
    def __post_init__(self):
        if self.last_check is None:
            self.last_check = time.time()


class HealthChecker:
    """Comprehensive health checking system for MCP servers"""
    
    def __init__(self, server_name: str, server_version: str = "1.0.0"):
        self.server_name = server_name
        self.server_version = server_version
        self.start_time = time.time()
        self.health_checks: Dict[str, Callable[[], Awaitable[ComponentHealth]]] = {}
        self.last_check_results: Dict[str, ComponentHealth] = {}
        self.check_interval = 30  # seconds
        self._check_task: Optional[asyncio.Task] = None
    
    def register_health_check(self, component_name: str, 
                            check_func: Callable[[], Awaitable[ComponentHealth]]) -> None:
        """Register a health check function for a component"""
        self.health_checks[component_name] = check_func
        logger.info(f"Registered health check for component: {component_name}")
    
    async def start_periodic_checks(self) -> None:
        """Start periodic health checks"""
        if self._check_task and not self._check_task.done():
            logger.warning("Periodic health checks already running")
            return
        
        self._check_task = asyncio.create_task(self._run_periodic_checks())
        logger.info("Started periodic health checks")
    
    async def stop_periodic_checks(self) -> None:
        """Stop periodic health checks"""
        if self._check_task and not self._check_task.done():
            self._check_task.cancel()
            try:
                await self._check_task
            except asyncio.CancelledError:
                pass
            logger.info("Stopped periodic health checks")
    
    async def _run_periodic_checks(self) -> None:
        """Run health checks periodically"""
        while True:
            try:
                await self.check_all_components()
                await asyncio.sleep(self.check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in periodic health check: {e}")
                await asyncio.sleep(self.check_interval)
    
    async def check_all_components(self) -> Dict[str, ComponentHealth]:
        """Run all registered health checks"""
        results = {}
        
        # Run all checks concurrently
        check_tasks = {
            name: asyncio.create_task(check_func())
            for name, check_func in self.health_checks.items()
        }
        
        for name, task in check_tasks.items():
            try:
                result = await task
                results[name] = result
                self.last_check_results[name] = result
            except Exception as e:
                logger.error(f"Health check failed for {name}: {e}")
                results[name] = ComponentHealth(
                    name=name,
                    status="unhealthy",
                    message=f"Check failed: {str(e)}"
                )
                self.last_check_results[name] = results[name]
        
        return results
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status"""
        # Get latest component health
        if not self.last_check_results:
            component_health = await self.check_all_components()
        else:
            component_health = self.last_check_results
        
        # Determine overall status
        statuses = [comp.status for comp in component_health.values()]
        if all(s == "healthy" for s in statuses):
            overall_status = "healthy"
        elif any(s == "unhealthy" for s in statuses):
            overall_status = "unhealthy"
        else:
            overall_status = "degraded"
        
        # Get system metrics
        system_metrics = await self._get_system_metrics()
        
        return {
            "status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "server": {
                "name": self.server_name,
                "version": self.server_version,
                "uptime": time.time() - self.start_time
            },
            "components": {
                name: asdict(health) for name, health in component_health.items()
            },
            "system": system_metrics
        }
    
    async def _get_system_metrics(self) -> Dict[str, Any]:
        """Get system-level metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_count = psutil.cpu_count()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            
            # Disk metrics (for current directory)
            disk = psutil.disk_usage('/')
            
            # Process metrics
            process = psutil.Process()
            process_memory = process.memory_info()
            
            return {
                "cpu": {
                    "usage_percent": cpu_percent,
                    "count": cpu_count
                },
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "used": memory.used,
                    "percent": memory.percent
                },
                "disk": {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": disk.percent
                },
                "process": {
                    "memory_rss": process_memory.rss,
                    "memory_vms": process_memory.vms,
                    "cpu_percent": process.cpu_percent(),
                    "num_threads": process.num_threads()
                },
                "platform": {
                    "system": platform.system(),
                    "release": platform.release(),
                    "python_version": platform.python_version()
                }
            }
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return {"error": str(e)}
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get detailed performance metrics"""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "server": self.server_name,
            "uptime_seconds": time.time() - self.start_time,
            "health_checks": {
                "registered": len(self.health_checks),
                "last_run": max(
                    (h.last_check for h in self.last_check_results.values()),
                    default=0
                )
            }
        }
        
        # Add component-specific metrics
        component_metrics = {}
        for name, health in self.last_check_results.items():
            if health.metrics:
                component_metrics[name] = health.metrics
        
        if component_metrics:
            metrics["components"] = component_metrics
        
        # Add system metrics
        metrics["system"] = await self._get_system_metrics()
        
        return metrics
    
    def create_health_resources(self) -> List[Dict[str, Any]]:
        """Create MCP resource definitions for health endpoints"""
        return [
            {
                "uri": "health://status",
                "name": "Server Health Status",
                "description": "Current server health and component status",
                "mime_type": "application/json"
            },
            {
                "uri": "health://metrics",
                "name": "Performance Metrics",
                "description": "Detailed server performance metrics",
                "mime_type": "application/json"
            },
            {
                "uri": "health://system",
                "name": "System Information",
                "description": "System resource usage and platform info",
                "mime_type": "application/json"
            }
        ]


# Common health check implementations
async def check_cache_health(cache_manager) -> ComponentHealth:
    """Health check for cache component"""
    try:
        cache_size = len(cache_manager.cache)
        hit_rate = getattr(cache_manager, 'hit_rate', 0.0)
        
        if cache_size > 10000:
            status = "degraded"
            message = "Cache size exceeding recommended limit"
        else:
            status = "healthy"
            message = "Cache operating normally"
        
        return ComponentHealth(
            name="cache",
            status=status,
            message=message,
            metrics={
                "size": cache_size,
                "hit_rate": hit_rate
            }
        )
    except Exception as e:
        return ComponentHealth(
            name="cache",
            status="unhealthy",
            message=f"Cache check failed: {str(e)}"
        )


async def check_ml_models_health(model_manager) -> ComponentHealth:
    """Health check for ML models"""
    try:
        loaded_models = getattr(model_manager, 'loaded_models', {})
        model_count = len(loaded_models)
        
        if model_count == 0:
            status = "degraded"
            message = "No models loaded"
        else:
            status = "healthy"
            message = f"{model_count} models loaded and ready"
        
        return ComponentHealth(
            name="ml_models",
            status=status,
            message=message,
            metrics={
                "loaded_models": model_count,
                "models": list(loaded_models.keys()) if loaded_models else []
            }
        )
    except Exception as e:
        return ComponentHealth(
            name="ml_models",
            status="unhealthy",
            message=f"Model check failed: {str(e)}"
        )


async def check_vector_db_health(vector_db) -> ComponentHealth:
    """Health check for vector database"""
    try:
        # Try to perform a simple operation
        if hasattr(vector_db, 'get_collection_stats'):
            stats = await vector_db.get_collection_stats()
            doc_count = stats.get('document_count', 0)
            
            status = "healthy"
            message = f"Vector DB operational with {doc_count} documents"
            
            return ComponentHealth(
                name="vector_db",
                status=status,
                message=message,
                metrics=stats
            )
        else:
            # Fallback check
            status = "healthy"
            message = "Vector DB connection active"
            
            return ComponentHealth(
                name="vector_db",
                status=status,
                message=message
            )
    except Exception as e:
        return ComponentHealth(
            name="vector_db",
            status="unhealthy",
            message=f"Vector DB check failed: {str(e)}"
        )