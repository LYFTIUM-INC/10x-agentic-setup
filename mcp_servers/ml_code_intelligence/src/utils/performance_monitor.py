"""
Performance Monitoring and Caching System
Advanced performance monitoring with caching capabilities for the ML Code Intelligence MCP server.
"""

import asyncio
import logging
import time
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
import json
import hashlib
from functools import wraps
import threading
from collections import deque, defaultdict
import weakref

try:
    import prometheus_client
    from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Prometheus client not available. Metrics collection disabled.")

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Performance metrics for operations"""
    operation_name: str
    start_time: float
    end_time: float
    duration: float
    success: bool
    error_message: Optional[str] = None
    input_size: Optional[int] = None
    output_size: Optional[int] = None
    memory_used: Optional[float] = None
    cache_hit: bool = False
    quality_score: Optional[float] = None

@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    key: str
    value: Any
    created_at: float
    last_accessed: float
    access_count: int
    size_bytes: int
    ttl: Optional[float] = None

class PerformanceMonitor:
    """Advanced performance monitoring system"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.metrics_history = deque(maxlen=self.config.get('max_history', 10000))
        self.operation_stats = defaultdict(list)
        
        # Prometheus metrics (if available)
        self.prometheus_registry = None
        self.prometheus_metrics = {}
        
        if PROMETHEUS_AVAILABLE and self.config.get('enable_prometheus', False):
            self._setup_prometheus_metrics()
        
        # Performance thresholds
        self.performance_thresholds = self.config.get('performance_thresholds', {
            'code_generation': {'warning': 5.0, 'critical': 10.0},
            'analysis': {'warning': 3.0, 'critical': 8.0},
            'search': {'warning': 1.0, 'critical': 3.0}
        })
        
        # Real-time monitoring
        self.active_operations = {}
        self.alerts = deque(maxlen=100)
        
    def _setup_prometheus_metrics(self):
        """Setup Prometheus metrics collection"""
        
        self.prometheus_registry = CollectorRegistry()
        
        # Operation counters
        self.prometheus_metrics['operation_total'] = Counter(
            'mcp_operations_total',
            'Total number of operations performed',
            ['operation', 'status'],
            registry=self.prometheus_registry
        )
        
        # Operation duration histogram
        self.prometheus_metrics['operation_duration'] = Histogram(
            'mcp_operation_duration_seconds',
            'Duration of operations in seconds',
            ['operation'],
            registry=self.prometheus_registry
        )
        
        # Cache metrics
        self.prometheus_metrics['cache_hits'] = Counter(
            'mcp_cache_hits_total',
            'Total number of cache hits',
            ['operation'],
            registry=self.prometheus_registry
        )
        
        self.prometheus_metrics['cache_misses'] = Counter(
            'mcp_cache_misses_total',
            'Total number of cache misses',
            ['operation'],
            registry=self.prometheus_registry
        )
        
        # Quality score gauge
        self.prometheus_metrics['quality_score'] = Gauge(
            'mcp_quality_score',
            'Quality score of generated outputs',
            ['operation'],
            registry=self.prometheus_registry
        )
        
        # Memory usage gauge
        self.prometheus_metrics['memory_usage'] = Gauge(
            'mcp_memory_usage_bytes',
            'Memory usage in bytes',
            registry=self.prometheus_registry
        )
    
    async def record_operation(
        self, 
        operation_name: str, 
        duration: float, 
        success: bool,
        quality_score: Optional[float] = None,
        error_message: Optional[str] = None,
        input_size: Optional[int] = None,
        output_size: Optional[int] = None,
        cache_hit: bool = False
    ):
        """Record a completed operation"""
        
        end_time = time.time()
        start_time = end_time - duration
        
        metrics = PerformanceMetrics(
            operation_name=operation_name,
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            success=success,
            error_message=error_message,
            input_size=input_size,
            output_size=output_size,
            quality_score=quality_score,
            cache_hit=cache_hit
        )
        
        # Store metrics
        self.metrics_history.append(metrics)
        self.operation_stats[operation_name].append(metrics)
        
        # Update Prometheus metrics if available
        if PROMETHEUS_AVAILABLE and self.prometheus_metrics:
            status = 'success' if success else 'error'
            self.prometheus_metrics['operation_total'].labels(
                operation=operation_name, status=status
            ).inc()
            
            self.prometheus_metrics['operation_duration'].labels(
                operation=operation_name
            ).observe(duration)
            
            if cache_hit:
                self.prometheus_metrics['cache_hits'].labels(
                    operation=operation_name
                ).inc()
            else:
                self.prometheus_metrics['cache_misses'].labels(
                    operation=operation_name
                ).inc()
            
            if quality_score is not None:
                self.prometheus_metrics['quality_score'].labels(
                    operation=operation_name
                ).set(quality_score)
        
        # Check performance thresholds
        await self._check_performance_thresholds(operation_name, duration, success)
        
        logger.debug(f"Recorded operation: {operation_name}, duration: {duration:.3f}s, success: {success}")
    
    async def start_operation(self, operation_name: str, operation_id: str) -> str:
        """Start tracking an operation"""
        
        start_time = time.time()
        self.active_operations[operation_id] = {
            'operation_name': operation_name,
            'start_time': start_time,
            'status': 'running'
        }
        
        return operation_id
    
    async def finish_operation(
        self, 
        operation_id: str, 
        success: bool = True,
        quality_score: Optional[float] = None,
        error_message: Optional[str] = None
    ):
        """Finish tracking an operation"""
        
        if operation_id not in self.active_operations:
            logger.warning(f"Operation {operation_id} not found in active operations")
            return
        
        operation_info = self.active_operations.pop(operation_id)
        duration = time.time() - operation_info['start_time']
        
        await self.record_operation(
            operation_name=operation_info['operation_name'],
            duration=duration,
            success=success,
            quality_score=quality_score,
            error_message=error_message
        )
    
    async def _check_performance_thresholds(self, operation_name: str, duration: float, success: bool):
        """Check if operation exceeds performance thresholds"""
        
        thresholds = self.performance_thresholds.get(operation_name, {})
        
        if not success:
            alert = {
                'type': 'error',
                'operation': operation_name,
                'message': f"Operation {operation_name} failed",
                'timestamp': time.time(),
                'severity': 'high'
            }
            self.alerts.append(alert)
        
        elif 'critical' in thresholds and duration > thresholds['critical']:
            alert = {
                'type': 'performance',
                'operation': operation_name,
                'message': f"Operation {operation_name} exceeded critical threshold ({duration:.2f}s > {thresholds['critical']}s)",
                'timestamp': time.time(),
                'severity': 'critical',
                'duration': duration
            }
            self.alerts.append(alert)
            
        elif 'warning' in thresholds and duration > thresholds['warning']:
            alert = {
                'type': 'performance',
                'operation': operation_name,
                'message': f"Operation {operation_name} exceeded warning threshold ({duration:.2f}s > {thresholds['warning']}s)",
                'timestamp': time.time(),
                'severity': 'warning',
                'duration': duration
            }
            self.alerts.append(alert)
    
    def get_operation_stats(self, operation_name: str, time_window: Optional[float] = None) -> Dict[str, Any]:
        """Get statistics for a specific operation"""
        
        metrics = self.operation_stats.get(operation_name, [])
        
        if time_window:
            cutoff_time = time.time() - time_window
            metrics = [m for m in metrics if m.end_time >= cutoff_time]
        
        if not metrics:
            return {
                'operation_name': operation_name,
                'total_operations': 0,
                'success_rate': 0.0,
                'avg_duration': 0.0,
                'min_duration': 0.0,
                'max_duration': 0.0,
                'avg_quality_score': 0.0
            }
        
        durations = [m.duration for m in metrics]
        success_count = sum(1 for m in metrics if m.success)
        quality_scores = [m.quality_score for m in metrics if m.quality_score is not None]
        
        return {
            'operation_name': operation_name,
            'total_operations': len(metrics),
            'success_rate': success_count / len(metrics),
            'avg_duration': sum(durations) / len(durations),
            'min_duration': min(durations),
            'max_duration': max(durations),
            'avg_quality_score': sum(quality_scores) / len(quality_scores) if quality_scores else 0.0,
            'cache_hit_rate': sum(1 for m in metrics if m.cache_hit) / len(metrics),
            'error_rate': 1 - (success_count / len(metrics))
        }
    
    def get_overall_stats(self) -> Dict[str, Any]:
        """Get overall performance statistics"""
        
        if not self.metrics_history:
            return {
                'total_operations': 0,
                'success_rate': 0.0,
                'avg_duration': 0.0,
                'active_operations': 0,
                'recent_alerts': 0
            }
        
        total_ops = len(self.metrics_history)
        success_count = sum(1 for m in self.metrics_history if m.success)
        durations = [m.duration for m in self.metrics_history]
        recent_alerts = len([a for a in self.alerts if time.time() - a['timestamp'] < 3600])  # Last hour
        
        return {
            'total_operations': total_ops,
            'success_rate': success_count / total_ops,
            'avg_duration': sum(durations) / len(durations),
            'active_operations': len(self.active_operations),
            'recent_alerts': recent_alerts,
            'operations_by_type': dict(self.operation_stats.keys())
        }
    
    def get_alerts(self, severity: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent alerts"""
        
        alerts = list(self.alerts)
        
        if severity:
            alerts = [a for a in alerts if a.get('severity') == severity]
        
        # Sort by timestamp (newest first)
        alerts.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return alerts[:limit]
    
    def monitor_function(self, operation_name: str, track_quality: bool = False):
        """Decorator to monitor function performance"""
        
        def decorator(func: Callable):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                operation_id = f"{operation_name}_{int(time.time() * 1000)}"
                await self.start_operation(operation_name, operation_id)
                
                try:
                    result = await func(*args, **kwargs)
                    
                    # Extract quality score if available
                    quality_score = None
                    if track_quality and isinstance(result, dict):
                        quality_score = result.get('quality_score')
                    
                    await self.finish_operation(
                        operation_id, 
                        success=True, 
                        quality_score=quality_score
                    )
                    
                    return result
                    
                except Exception as e:
                    await self.finish_operation(
                        operation_id, 
                        success=False, 
                        error_message=str(e)
                    )
                    raise
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                start_time = time.time()
                
                try:
                    result = func(*args, **kwargs)
                    duration = time.time() - start_time
                    
                    # Extract quality score if available
                    quality_score = None
                    if track_quality and isinstance(result, dict):
                        quality_score = result.get('quality_score')
                    
                    # Record operation (needs to be run in event loop)
                    asyncio.create_task(self.record_operation(
                        operation_name=operation_name,
                        duration=duration,
                        success=True,
                        quality_score=quality_score
                    ))
                    
                    return result
                    
                except Exception as e:
                    duration = time.time() - start_time
                    
                    # Record operation (needs to be run in event loop)
                    asyncio.create_task(self.record_operation(
                        operation_name=operation_name,
                        duration=duration,
                        success=False,
                        error_message=str(e)
                    ))
                    raise
            
            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        
        return decorator


class SmartCache:
    """Intelligent caching system with LRU eviction and TTL support"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.max_size = self.config.get('max_size', 1000)
        self.default_ttl = self.config.get('default_ttl', 3600)  # 1 hour
        self.max_memory_mb = self.config.get('max_memory_mb', 100)
        
        self.cache: Dict[str, CacheEntry] = {}
        self.access_order = deque()  # For LRU tracking
        self.lock = threading.RLock()
        
        # Statistics
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        
        # Cleanup thread
        self.cleanup_interval = self.config.get('cleanup_interval', 300)  # 5 minutes
        self._start_cleanup_thread()
    
    def _start_cleanup_thread(self):
        """Start background cleanup thread"""
        
        def cleanup_worker():
            while True:
                try:
                    self._cleanup_expired()
                    time.sleep(self.cleanup_interval)
                except Exception as e:
                    logger.error(f"Cache cleanup error: {e}")
                    time.sleep(60)  # Wait 1 minute before retry
        
        thread = threading.Thread(target=cleanup_worker, daemon=True)
        thread.start()
    
    def _generate_key(self, operation: str, *args, **kwargs) -> str:
        """Generate cache key from operation and parameters"""
        
        # Create a hash of the operation and parameters
        key_data = {
            'operation': operation,
            'args': args,
            'kwargs': sorted(kwargs.items())
        }
        
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _estimate_size(self, value: Any) -> int:
        """Estimate memory size of cached value"""
        
        try:
            if isinstance(value, str):
                return len(value.encode('utf-8'))
            elif isinstance(value, (dict, list)):
                return len(json.dumps(value, default=str).encode('utf-8'))
            else:
                return len(str(value).encode('utf-8'))
        except Exception:
            return 1024  # Default estimate
    
    def get(self, operation: str, *args, **kwargs) -> Optional[Any]:
        """Get value from cache"""
        
        key = self._generate_key(operation, *args, **kwargs)
        
        with self.lock:
            if key not in self.cache:
                self.misses += 1
                return None
            
            entry = self.cache[key]
            current_time = time.time()
            
            # Check TTL
            if entry.ttl and current_time - entry.created_at > entry.ttl:
                del self.cache[key]
                if key in self.access_order:
                    self.access_order.remove(key)
                self.misses += 1
                return None
            
            # Update access information
            entry.last_accessed = current_time
            entry.access_count += 1
            
            # Move to end of access order (most recently used)
            if key in self.access_order:
                self.access_order.remove(key)
            self.access_order.append(key)
            
            self.hits += 1
            return entry.value
    
    def put(self, operation: str, value: Any, ttl: Optional[float] = None, *args, **kwargs):
        """Put value in cache"""
        
        key = self._generate_key(operation, *args, **kwargs)
        size_bytes = self._estimate_size(value)
        current_time = time.time()
        
        with self.lock:
            # Check if we need to evict entries
            self._evict_if_needed(size_bytes)
            
            # Create cache entry
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=current_time,
                last_accessed=current_time,
                access_count=1,
                size_bytes=size_bytes,
                ttl=ttl or self.default_ttl
            )
            
            # Remove old entry if exists
            if key in self.cache:
                if key in self.access_order:
                    self.access_order.remove(key)
            
            # Add new entry
            self.cache[key] = entry
            self.access_order.append(key)
    
    def _evict_if_needed(self, new_size: int):
        """Evict entries if cache is full"""
        
        # Check size limit
        while len(self.cache) >= self.max_size:
            self._evict_lru()
        
        # Check memory limit
        current_memory = sum(entry.size_bytes for entry in self.cache.values())
        max_memory_bytes = self.max_memory_mb * 1024 * 1024
        
        while current_memory + new_size > max_memory_bytes and self.cache:
            evicted_size = self._evict_lru()
            current_memory -= evicted_size
    
    def _evict_lru(self) -> int:
        """Evict least recently used entry"""
        
        if not self.access_order:
            return 0
        
        # Get least recently used key
        lru_key = self.access_order.popleft()
        
        if lru_key in self.cache:
            evicted_entry = self.cache.pop(lru_key)
            self.evictions += 1
            return evicted_entry.size_bytes
        
        return 0
    
    def _cleanup_expired(self):
        """Remove expired entries"""
        
        current_time = time.time()
        expired_keys = []
        
        with self.lock:
            for key, entry in self.cache.items():
                if entry.ttl and current_time - entry.created_at > entry.ttl:
                    expired_keys.append(key)
            
            for key in expired_keys:
                if key in self.cache:
                    del self.cache[key]
                if key in self.access_order:
                    self.access_order.remove(key)
        
        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def clear(self):
        """Clear all cache entries"""
        
        with self.lock:
            self.cache.clear()
            self.access_order.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        
        with self.lock:
            total_requests = self.hits + self.misses
            hit_rate = self.hits / total_requests if total_requests > 0 else 0.0
            
            total_memory = sum(entry.size_bytes for entry in self.cache.values())
            
            return {
                'size': len(self.cache),
                'max_size': self.max_size,
                'hits': self.hits,
                'misses': self.misses,
                'hit_rate': hit_rate,
                'evictions': self.evictions,
                'memory_usage_bytes': total_memory,
                'memory_usage_mb': total_memory / (1024 * 1024),
                'max_memory_mb': self.max_memory_mb
            }
    
    def cache_function(self, operation_name: str, ttl: Optional[float] = None):
        """Decorator to cache function results"""
        
        def decorator(func: Callable):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                # Try to get from cache
                cached_result = self.get(operation_name, *args, **kwargs)
                if cached_result is not None:
                    return cached_result
                
                # Execute function and cache result
                result = await func(*args, **kwargs)
                self.put(operation_name, result, ttl, *args, **kwargs)
                
                return result
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                # Try to get from cache
                cached_result = self.get(operation_name, *args, **kwargs)
                if cached_result is not None:
                    return cached_result
                
                # Execute function and cache result
                result = func(*args, **kwargs)
                self.put(operation_name, result, ttl, *args, **kwargs)
                
                return result
            
            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        
        return decorator


class PerformanceOptimizer:
    """Performance optimization recommendations and automated tuning"""
    
    def __init__(self, monitor: PerformanceMonitor, cache: SmartCache):
        self.monitor = monitor
        self.cache = cache
        
    def analyze_performance(self, time_window: float = 3600) -> Dict[str, Any]:
        """Analyze performance and provide optimization recommendations"""
        
        recommendations = []
        
        # Analyze cache performance
        cache_stats = self.cache.get_stats()
        if cache_stats['hit_rate'] < 0.7:  # Less than 70% hit rate
            recommendations.append({
                'type': 'cache',
                'priority': 'medium',
                'issue': 'Low cache hit rate',
                'current_value': cache_stats['hit_rate'],
                'recommendation': 'Consider increasing cache size or TTL values',
                'impact': 'Reduced latency and improved response times'
            })
        
        # Analyze operation performance
        overall_stats = self.monitor.get_overall_stats()
        if overall_stats['success_rate'] < 0.95:  # Less than 95% success rate
            recommendations.append({
                'type': 'reliability',
                'priority': 'high',
                'issue': 'Low success rate',
                'current_value': overall_stats['success_rate'],
                'recommendation': 'Investigate and fix recurring errors',
                'impact': 'Improved system reliability'
            })
        
        # Check for slow operations
        for operation_name in self.monitor.operation_stats.keys():
            stats = self.monitor.get_operation_stats(operation_name, time_window)
            if stats['avg_duration'] > 5.0:  # More than 5 seconds average
                recommendations.append({
                    'type': 'performance',
                    'priority': 'medium',
                    'issue': f'Slow operation: {operation_name}',
                    'current_value': stats['avg_duration'],
                    'recommendation': f'Optimize {operation_name} implementation or add caching',
                    'impact': 'Reduced response times'
                })
        
        return {
            'analysis_timestamp': time.time(),
            'time_window': time_window,
            'overall_health': 'good' if len(recommendations) == 0 else 'needs_attention',
            'recommendations': recommendations,
            'cache_stats': cache_stats,
            'performance_stats': overall_stats
        }
    
    def get_optimization_suggestions(self) -> List[Dict[str, Any]]:
        """Get specific optimization suggestions"""
        
        suggestions = [
            {
                'category': 'caching',
                'suggestion': 'Implement semantic caching for code analysis results',
                'benefit': 'Reduce duplicate analysis work',
                'effort': 'medium'
            },
            {
                'category': 'performance',
                'suggestion': 'Use batching for embedding generation',
                'benefit': 'Improved throughput for large requests',
                'effort': 'low'
            },
            {
                'category': 'memory',
                'suggestion': 'Implement streaming for large file analysis',
                'benefit': 'Reduced memory usage for large codebases',
                'effort': 'high'
            }
        ]
        
        return suggestions