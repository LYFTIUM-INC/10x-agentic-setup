#!/usr/bin/env python3
"""
Memory Optimization Module
Implements strategies to optimize memory usage and prevent exhaustion.
"""

import gc
import sys
import psutil
import tracemalloc
import weakref
import threading
import time
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from collections import defaultdict
from functools import wraps
import numpy as np

class MemoryOptimizer:
    """Implements memory optimization strategies for the 10x agentic system."""
    
    def __init__(self):
        self.base_path = Path(__file__).parent.parent.parent
        self.db_path = self.base_path / "performance" / "performance_metrics.db"
        self.cache = weakref.WeakValueDictionary()
        self.memory_pools = {}
        self.monitoring_enabled = True
        self.memory_threshold = 0.80  # 80% memory usage threshold
        self.gc_threshold = 0.70  # 70% memory usage triggers GC
        
        # Initialize tracking
        tracemalloc.start()
        self._init_database()
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitor_memory, daemon=True)
        self.monitor_thread.start()
        
    def _init_database(self):
        """Initialize memory metrics database tables."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                total_memory_gb REAL,
                used_memory_gb REAL,
                available_memory_gb REAL,
                percent_used REAL,
                gc_collections INTEGER,
                cached_objects INTEGER,
                memory_pools INTEGER
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory_leaks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                location TEXT,
                size_mb REAL,
                traceback TEXT
            )
        """)
        
        conn.commit()
        conn.close()
        
    def _monitor_memory(self):
        """Background thread to monitor memory usage."""
        while self.monitoring_enabled:
            try:
                memory = psutil.virtual_memory()
                
                # Check if we need to trigger GC
                if memory.percent / 100 > self.gc_threshold:
                    self.force_garbage_collection()
                    
                # Save metrics every 30 seconds
                self._save_memory_metrics()
                
                # Check for potential memory leaks
                self._check_memory_leaks()
                
                time.sleep(30)
            except Exception as e:
                print(f"Memory monitoring error: {e}")
                
    def _save_memory_metrics(self):
        """Save current memory metrics to database."""
        memory = psutil.virtual_memory()
        gc_stats = gc.get_stats()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO memory_metrics 
            (timestamp, total_memory_gb, used_memory_gb, available_memory_gb, 
             percent_used, gc_collections, cached_objects, memory_pools)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            time.time(),
            memory.total / (1024**3),
            memory.used / (1024**3),
            memory.available / (1024**3),
            memory.percent,
            sum(stat.get('collections', 0) for stat in gc_stats),
            len(self.cache),
            len(self.memory_pools)
        ))
        
        conn.commit()
        conn.close()
        
    def _check_memory_leaks(self):
        """Check for potential memory leaks using tracemalloc."""
        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics('lineno')
        
        # Check for suspicious memory usage (>100MB from single location)
        for stat in top_stats[:10]:
            size_mb = stat.size / (1024**2)
            if size_mb > 100:
                self._log_potential_leak(stat, size_mb)
                
    def _log_potential_leak(self, stat, size_mb):
        """Log potential memory leak to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO memory_leaks (timestamp, location, size_mb, traceback)
            VALUES (?, ?, ?, ?)
        """, (
            time.time(),
            str(stat.traceback),
            size_mb,
            str(stat.traceback.format())
        ))
        
        conn.commit()
        conn.close()
        
    def memory_efficient(self, max_memory_mb: int = 100):
        """
        Decorator to ensure a function doesn't exceed memory limits.
        
        Args:
            max_memory_mb: Maximum memory usage in MB
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Check available memory before execution
                memory = psutil.virtual_memory()
                available_mb = memory.available / (1024**2)
                
                if available_mb < max_memory_mb * 1.5:  # 1.5x safety margin
                    # Try to free memory
                    self.optimize_memory()
                    
                    # Re-check
                    memory = psutil.virtual_memory()
                    available_mb = memory.available / (1024**2)
                    
                    if available_mb < max_memory_mb:
                        raise MemoryError(f"Insufficient memory. Required: {max_memory_mb}MB, Available: {available_mb:.1f}MB")
                        
                # Execute function
                result = func(*args, **kwargs)
                
                # Clean up after execution
                gc.collect()
                
                return result
            return wrapper
        return decorator
        
    def create_memory_pool(self, name: str, size_mb: int) -> 'MemoryPool':
        """
        Create a memory pool for efficient allocation.
        
        Args:
            name: Pool name
            size_mb: Pool size in MB
            
        Returns:
            MemoryPool instance
        """
        if name in self.memory_pools:
            return self.memory_pools[name]
            
        pool = MemoryPool(name, size_mb)
        self.memory_pools[name] = pool
        return pool
        
    def optimize_memory(self):
        """Perform memory optimization."""
        # Clear weak reference cache
        self.cache.clear()
        
        # Force garbage collection
        self.force_garbage_collection()
        
        # Clear numpy cache if available
        try:
            import numpy as np
            np.ndarray([0]).resize(0)
        except:
            pass
            
        # Clear Python's internal caches
        sys.intern('')
        
        # Trim memory pools
        for pool in self.memory_pools.values():
            pool.trim()
            
    def force_garbage_collection(self):
        """Force full garbage collection."""
        # Collect all generations
        for i in range(3):
            gc.collect(i)
            
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get current memory statistics."""
        memory = psutil.virtual_memory()
        process = psutil.Process()
        
        # Get tracemalloc stats
        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics('lineno')
        
        return {
            "system": {
                "total_gb": memory.total / (1024**3),
                "used_gb": memory.used / (1024**3),
                "available_gb": memory.available / (1024**3),
                "percent": memory.percent
            },
            "process": {
                "rss_gb": process.memory_info().rss / (1024**3),
                "vms_gb": process.memory_info().vms / (1024**3),
                "percent": process.memory_percent()
            },
            "gc": {
                "collections": gc.get_count(),
                "garbage": len(gc.garbage),
                "stats": gc.get_stats()
            },
            "top_allocations": [
                {
                    "file": stat.traceback[0].filename,
                    "line": stat.traceback[0].lineno,
                    "size_mb": stat.size / (1024**2),
                    "count": stat.count
                }
                for stat in top_stats[:5]
            ]
        }
        
    def cache_with_limit(self, max_size: int = 1000):
        """
        Decorator for caching with size limits.
        
        Args:
            max_size: Maximum cache size
        """
        cache = {}
        cache_order = []
        
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Create cache key
                key = str(args) + str(kwargs)
                
                # Check cache
                if key in cache:
                    # Move to end (LRU)
                    cache_order.remove(key)
                    cache_order.append(key)
                    return cache[key]
                    
                # Execute function
                result = func(*args, **kwargs)
                
                # Add to cache
                cache[key] = result
                cache_order.append(key)
                
                # Enforce size limit
                while len(cache) > max_size:
                    oldest = cache_order.pop(0)
                    del cache[oldest]
                    
                return result
            return wrapper
        return decorator
        
    def batch_process_memory_efficient(self, items: List[Any], 
                                     process_func: Callable,
                                     batch_size: Optional[int] = None) -> List[Any]:
        """
        Process items in memory-efficient batches.
        
        Args:
            items: List of items to process
            process_func: Function to process each item
            batch_size: Batch size (auto-calculated if None)
            
        Returns:
            Processed results
        """
        if batch_size is None:
            # Calculate based on available memory
            memory = psutil.virtual_memory()
            available_gb = memory.available / (1024**3)
            
            # Estimate memory per item (assume 10MB average)
            memory_per_item_mb = 10
            batch_size = max(1, int(available_gb * 1024 * 0.3 / memory_per_item_mb))  # Use 30% of available
            
        results = []
        
        # Process in batches
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            batch_results = [process_func(item) for item in batch]
            results.extend(batch_results)
            
            # Clean up after each batch
            del batch
            del batch_results
            gc.collect()
            
        return results

class MemoryPool:
    """Memory pool for efficient allocation and reuse."""
    
    def __init__(self, name: str, size_mb: int):
        self.name = name
        self.size_mb = size_mb
        self.size_bytes = size_mb * 1024 * 1024
        self.allocated = 0
        self.free_blocks = []
        self.used_blocks = []
        self.lock = threading.Lock()
        
    def allocate(self, size_bytes: int) -> Optional[memoryview]:
        """Allocate memory from pool."""
        with self.lock:
            if self.allocated + size_bytes > self.size_bytes:
                return None
                
            # Check for reusable blocks
            for i, block in enumerate(self.free_blocks):
                if len(block) >= size_bytes:
                    # Reuse this block
                    self.free_blocks.pop(i)
                    allocated_block = memoryview(block)[:size_bytes]
                    self.used_blocks.append(allocated_block)
                    return allocated_block
                    
            # Allocate new block
            try:
                block = bytearray(size_bytes)
                self.allocated += size_bytes
                allocated_block = memoryview(block)
                self.used_blocks.append(allocated_block)
                return allocated_block
            except MemoryError:
                return None
                
    def free(self, block: memoryview):
        """Free memory back to pool."""
        with self.lock:
            if block in self.used_blocks:
                self.used_blocks.remove(block)
                # Convert back to bytearray for reuse
                self.free_blocks.append(bytearray(block))
                
    def trim(self):
        """Trim unused memory from pool."""
        with self.lock:
            # Clear free blocks
            freed = sum(len(block) for block in self.free_blocks)
            self.free_blocks.clear()
            self.allocated -= freed
            
    def get_stats(self) -> Dict[str, Any]:
        """Get pool statistics."""
        with self.lock:
            return {
                "name": self.name,
                "size_mb": self.size_mb,
                "allocated_mb": self.allocated / (1024 * 1024),
                "used_blocks": len(self.used_blocks),
                "free_blocks": len(self.free_blocks),
                "utilization": self.allocated / self.size_bytes * 100
            }

# Singleton instance
_optimizer_instance = None

def get_memory_optimizer() -> MemoryOptimizer:
    """Get singleton memory optimizer instance."""
    global _optimizer_instance
    if _optimizer_instance is None:
        _optimizer_instance = MemoryOptimizer()
    return _optimizer_instance

# Example usage
if __name__ == "__main__":
    optimizer = get_memory_optimizer()
    
    print("Memory Optimizer Status")
    print("-" * 50)
    
    stats = optimizer.get_memory_stats()
    print(f"System Memory: {stats['system']['used_gb']:.1f}/{stats['system']['total_gb']:.1f} GB ({stats['system']['percent']:.1f}%)")
    print(f"Process Memory: {stats['process']['rss_gb']:.2f} GB")
    print(f"GC Collections: {stats['gc']['collections']}")
    
    # Test memory pool
    pool = optimizer.create_memory_pool("test_pool", 100)
    print(f"\nCreated memory pool: {pool.get_stats()}")
    
    # Test memory-efficient processing
    @optimizer.memory_efficient(max_memory_mb=50)
    def process_data(data):
        # Simulate processing
        return sum(data)
        
    test_data = list(range(1000000))
    result = process_data(test_data)
    print(f"\nProcessed {len(test_data)} items, result: {result}")