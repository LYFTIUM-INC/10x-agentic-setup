#!/usr/bin/env python3
"""
Test Cache Performance and Hit Rates
Validates 70% cache hit rate target
"""

import os
import time
import sqlite3
import hashlib
import json
from pathlib import Path
from datetime import datetime

class CachePerformanceTester:
    def __init__(self):
        self.knowledge_path = Path("/home/dell/coding/bash/10x-agentic-setup/Knowledge/intelligence")
        self.cache_path = self.knowledge_path / "search_cache"
        self.cache_db_path = self.cache_path / "index/cache.db"
        self.results = []
        
    def setup_cache_database(self):
        """Setup cache database with proper schema"""
        print("🔧 Setting up cache database...")
        
        # Create directories
        self.cache_db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create/update database schema
        conn = sqlite3.connect(str(self.cache_db_path))
        
        # Drop old table if exists and create new with correct schema
        conn.execute("DROP TABLE IF EXISTS search_cache")
        
        conn.execute("""
            CREATE TABLE search_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                keywords TEXT NOT NULL,
                results_file TEXT,
                query_hash TEXT UNIQUE,
                relevance_score REAL DEFAULT 100.0,
                usage_count INTEGER DEFAULT 1,
                last_accessed DATETIME DEFAULT CURRENT_TIMESTAMP,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                file_size INTEGER DEFAULT 0,
                domain TEXT,
                status TEXT DEFAULT 'active'
            )
        """)
        
        # Create search metrics table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS search_metrics (
                date DATE PRIMARY KEY,
                total_searches INTEGER DEFAULT 0,
                cache_hits INTEGER DEFAULT 0,
                api_calls_saved INTEGER DEFAULT 0
            )
        """)
        
        # Create indexes
        conn.execute("CREATE INDEX IF NOT EXISTS idx_query_hash ON search_cache(query_hash)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_keywords ON search_cache(keywords)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON search_cache(timestamp)")
        
        conn.commit()
        conn.close()
        
        print("✅ Cache database setup complete")
    
    def test_cache_operations(self):
        """Test cache hit rate with realistic queries"""
        print("\n🎯 Testing Cache Operations...")
        
        # Test queries with expected duplicates
        test_queries = [
            # First wave - all cache misses
            "react performance optimization best practices 2024",
            "python async await patterns production",
            "kubernetes scaling strategies enterprise",
            "machine learning deployment pipelines",
            "microservices architecture patterns",
            
            # Second wave - mix of hits and misses
            "react performance optimization best practices 2024",  # HIT
            "golang concurrency patterns channels",
            "python async await patterns production",              # HIT
            "docker container security scanning",
            "kubernetes scaling strategies enterprise",            # HIT
            
            # Third wave - mostly hits
            "react performance optimization best practices 2024",  # HIT
            "machine learning deployment pipelines",               # HIT
            "python async await patterns production",              # HIT
            "microservices architecture patterns",                 # HIT
            "kubernetes scaling strategies enterprise",            # HIT
            
            # Fourth wave - testing variations
            "react performance optimization",                      # Partial match
            "python async patterns",                              # Partial match
            "enterprise kubernetes scaling",                      # Reordered
            "ML deployment pipelines",                           # Abbreviation
            "microservice patterns architecture"                 # Reordered
        ]
        
        cache_hits = 0
        cache_misses = 0
        
        for i, query in enumerate(test_queries):
            print(f"\n  Query {i+1}: {query[:50]}...")
            
            # Check cache
            hit, similarity = self._check_advanced_cache(query)
            
            if hit:
                cache_hits += 1
                print(f"    ✅ CACHE HIT (similarity: {similarity:.1f}%)")
            else:
                cache_misses += 1
                print(f"    ❌ CACHE MISS")
                # Add to cache
                self._add_to_cache(query)
        
        total = len(test_queries)
        hit_rate = (cache_hits / total) * 100
        
        print(f"\n📊 Cache Performance Summary:")
        print(f"  Total Queries: {total}")
        print(f"  Cache Hits: {cache_hits}")
        print(f"  Cache Misses: {cache_misses}")
        print(f"  Hit Rate: {hit_rate:.1f}%")
        print(f"  Target: 70%")
        print(f"  Status: {'✅ PASSED' if hit_rate >= 70 else '❌ FAILED'}")
        
        # Update metrics
        self._update_metrics(total, cache_hits)
        
        return {
            'total_queries': total,
            'cache_hits': cache_hits,
            'cache_misses': cache_misses,
            'hit_rate': hit_rate,
            'target_met': hit_rate >= 70
        }
    
    def test_cache_intelligence(self):
        """Test intelligent cache matching"""
        print("\n🧠 Testing Cache Intelligence...")
        
        # Test semantic similarity matching
        test_pairs = [
            ("react performance optimization", "react optimize performance"),
            ("kubernetes deployment", "k8s deploy"),
            ("python testing best practices", "python test best practice"),
            ("machine learning models", "ML models"),
            ("docker container security", "container security docker")
        ]
        
        for original, variant in test_pairs:
            # Add original to cache
            self._add_to_cache(original)
            
            # Check if variant hits cache
            hit, similarity = self._check_advanced_cache(variant)
            print(f"\n  Original: {original}")
            print(f"  Variant: {variant}")
            print(f"  Match: {'YES' if hit else 'NO'} (similarity: {similarity:.1f}%)")
        
        return True
    
    def test_cache_performance_gains(self):
        """Test actual performance improvements from caching"""
        print("\n⚡ Testing Cache Performance Gains...")
        
        # Simulate API call vs cache retrieval
        api_times = []
        cache_times = []
        
        # Test query
        test_query = "comprehensive react performance optimization guide 2024"
        
        # First call - API (simulated)
        start = time.time()
        time.sleep(2.0)  # Simulate API delay
        api_time = time.time() - start
        api_times.append(api_time)
        self._add_to_cache(test_query)
        
        # Subsequent calls - Cache
        for i in range(5):
            start = time.time()
            hit, _ = self._check_advanced_cache(test_query)
            cache_time = time.time() - start
            cache_times.append(cache_time)
        
        avg_api_time = sum(api_times) / len(api_times)
        avg_cache_time = sum(cache_times) / len(cache_times)
        speedup = avg_api_time / avg_cache_time if avg_cache_time > 0 else float('inf')
        
        print(f"\n📊 Performance Results:")
        print(f"  Average API Time: {avg_api_time:.3f}s")
        print(f"  Average Cache Time: {avg_cache_time:.3f}s")
        print(f"  Speedup: {speedup:.1f}x")
        print(f"  Time Saved: {(avg_api_time - avg_cache_time):.3f}s per query")
        
        return {
            'api_time': avg_api_time,
            'cache_time': avg_cache_time,
            'speedup': speedup,
            'time_saved': avg_api_time - avg_cache_time
        }
    
    def test_cache_storage_efficiency(self):
        """Test cache storage and retrieval efficiency"""
        print("\n💾 Testing Cache Storage Efficiency...")
        
        conn = sqlite3.connect(str(self.cache_db_path))
        
        # Check storage stats
        cursor = conn.execute("""
            SELECT 
                COUNT(*) as total_entries,
                SUM(file_size) as total_size,
                AVG(usage_count) as avg_usage,
                MAX(usage_count) as max_usage
            FROM search_cache
            WHERE status = 'active'
        """)
        
        stats = cursor.fetchone()
        
        # Check most used queries
        cursor = conn.execute("""
            SELECT query, usage_count, relevance_score
            FROM search_cache
            WHERE status = 'active'
            ORDER BY usage_count DESC
            LIMIT 5
        """)
        
        top_queries = cursor.fetchall()
        
        conn.close()
        
        print(f"\n📊 Cache Storage Stats:")
        print(f"  Total Entries: {stats[0]}")
        print(f"  Average Usage: {stats[2]:.1f}" if stats[2] else "  Average Usage: 0")
        print(f"  Max Usage: {stats[3]}" if stats[3] else "  Max Usage: 0")
        
        if top_queries:
            print(f"\n🔝 Most Used Cached Queries:")
            for query, count, score in top_queries[:3]:
                print(f"  - {query[:50]}... (used {count}x, score: {score:.0f})")
        
        return True
    
    def _check_advanced_cache(self, query):
        """Check cache with intelligent matching"""
        conn = sqlite3.connect(str(self.cache_db_path))
        
        # Clean and hash query
        query_clean = query.lower().strip()
        query_hash = hashlib.sha256(query_clean.encode()).hexdigest()
        
        # Extract keywords
        keywords = ' '.join(sorted(query_clean.split()))
        
        # First check exact match
        cursor = conn.execute(
            "SELECT relevance_score FROM search_cache WHERE query_hash = ?",
            (query_hash,)
        )
        result = cursor.fetchone()
        
        if result:
            # Update usage
            conn.execute("""
                UPDATE search_cache 
                SET usage_count = usage_count + 1,
                    last_accessed = CURRENT_TIMESTAMP
                WHERE query_hash = ?
            """, (query_hash,))
            conn.commit()
            conn.close()
            return True, 100.0
        
        # Check fuzzy match using keywords
        query_keywords = set(query_clean.split())
        
        cursor = conn.execute("""
            SELECT query, keywords, relevance_score
            FROM search_cache
            WHERE status = 'active'
        """)
        
        best_match = None
        best_similarity = 0
        
        for cached_query, cached_keywords, score in cursor.fetchall():
            cached_set = set(cached_keywords.split())
            
            # Calculate Jaccard similarity
            intersection = len(query_keywords & cached_set)
            union = len(query_keywords | cached_set)
            similarity = (intersection / union * 100) if union > 0 else 0
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = (cached_query, score)
        
        conn.close()
        
        # Consider it a hit if similarity > 70%
        if best_similarity > 70:
            return True, best_similarity
        
        return False, best_similarity
    
    def _add_to_cache(self, query):
        """Add query to cache with metadata"""
        conn = sqlite3.connect(str(self.cache_db_path))
        
        query_clean = query.lower().strip()
        query_hash = hashlib.sha256(query_clean.encode()).hexdigest()
        keywords = ' '.join(sorted(query_clean.split()))
        
        # Create cache file path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        cache_file = f"test_cache/{timestamp}_{query_hash[:8]}.md"
        
        # Determine domain
        domain = "general"
        if any(word in query_clean for word in ["react", "vue", "angular"]):
            domain = "frontend"
        elif any(word in query_clean for word in ["python", "golang", "java"]):
            domain = "backend"
        elif any(word in query_clean for word in ["kubernetes", "docker", "container"]):
            domain = "devops"
        elif any(word in query_clean for word in ["machine learning", "ml", "ai"]):
            domain = "ml"
        
        try:
            conn.execute("""
                INSERT INTO search_cache
                (query, keywords, results_file, query_hash, file_size, domain)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (query, keywords, cache_file, query_hash, 1024, domain))
            conn.commit()
        except sqlite3.IntegrityError:
            # Query already exists, just update access time
            conn.execute("""
                UPDATE search_cache
                SET usage_count = usage_count + 1,
                    last_accessed = CURRENT_TIMESTAMP
                WHERE query_hash = ?
            """, (query_hash,))
            conn.commit()
        
        conn.close()
    
    def _update_metrics(self, total_searches, cache_hits):
        """Update search metrics"""
        conn = sqlite3.connect(str(self.cache_db_path))
        
        today = datetime.now().date()
        api_saved = cache_hits  # Each cache hit saves one API call
        
        # Update or insert metrics
        conn.execute("""
            INSERT OR REPLACE INTO search_metrics
            (date, total_searches, cache_hits, api_calls_saved)
            VALUES (?, ?, ?, ?)
        """, (today, total_searches, cache_hits, api_saved))
        
        conn.commit()
        conn.close()
    
    def generate_report(self):
        """Generate cache performance report"""
        print("\n" + "="*60)
        print("📊 CACHE PERFORMANCE VALIDATION REPORT")
        print("="*60)
        
        # Get final metrics
        conn = sqlite3.connect(str(self.cache_db_path))
        
        cursor = conn.execute("""
            SELECT 
                SUM(total_searches) as total,
                SUM(cache_hits) as hits,
                SUM(api_calls_saved) as saved
            FROM search_metrics
        """)
        
        metrics = cursor.fetchone()
        
        if metrics and metrics[0]:
            overall_hit_rate = (metrics[1] / metrics[0]) * 100
            print(f"\n📈 Overall Cache Performance:")
            print(f"  Total Searches: {metrics[0]}")
            print(f"  Total Cache Hits: {metrics[1]}")
            print(f"  API Calls Saved: {metrics[2]}")
            print(f"  Overall Hit Rate: {overall_hit_rate:.1f}%")
            print(f"\n✅ 70% Cache Hit Rate Target: {'ACHIEVED' if overall_hit_rate >= 70 else 'NOT MET'}")
        
        conn.close()
        
        # Save detailed report
        report = {
            'timestamp': datetime.now().isoformat(),
            'results': self.results,
            'summary': {
                'total_searches': metrics[0] if metrics else 0,
                'cache_hits': metrics[1] if metrics else 0,
                'api_calls_saved': metrics[2] if metrics else 0,
                'hit_rate': overall_hit_rate if metrics and metrics[0] else 0
            }
        }
        
        report_path = Path("tests/cache_performance_report.json")
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_path}")

def main():
    """Run cache performance tests"""
    tester = CachePerformanceTester()
    
    # Setup
    tester.setup_cache_database()
    
    # Run tests
    print("\n🚀 Starting Cache Performance Tests...")
    
    # Test 1: Cache Operations
    cache_results = tester.test_cache_operations()
    tester.results.append({
        'test': 'cache_operations',
        'results': cache_results
    })
    
    # Test 2: Cache Intelligence
    tester.test_cache_intelligence()
    
    # Test 3: Performance Gains
    perf_results = tester.test_cache_performance_gains()
    tester.results.append({
        'test': 'performance_gains',
        'results': perf_results
    })
    
    # Test 4: Storage Efficiency
    tester.test_cache_storage_efficiency()
    
    # Generate report
    tester.generate_report()

if __name__ == "__main__":
    main()