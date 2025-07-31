#!/usr/bin/env python3
"""
🧠 Research Intelligence Coordinator
Advanced research orchestration system that integrates with existing knowledge assets,
intelligent caching, and multi-agent coordination for world-class research intelligence.
"""

import os
import sys
import json
import time
import sqlite3
import hashlib
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timezone

# Add project paths for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "mcp_servers" / "shared" / "src"))

@dataclass
class ResearchQuery:
    """Research query with intelligent caching and diversification"""
    original_query: str
    domain_type: str
    variations: List[str]
    cache_key: str
    priority: int
    expected_sources: int
    creative_exploration: bool = True

@dataclass
class ResearchResult:
    """Research result with quality metrics and integration data"""
    query: str
    sources: List[str]
    findings: str
    insights: List[str]
    cache_status: str
    quality_score: float
    strategic_value: float
    timestamp: str

class ResearchIntelligenceCoordinator:
    """Advanced research coordination with existing knowledge integration"""
    
    def __init__(self):
        self.project_root = project_root
        self.intelligence_dir = self.project_root / "Knowledge" / "intelligence"
        self.cache_dir = self.intelligence_dir / "search_cache"
        self.vector_db = self.intelligence_dir / "vector_store" / "chroma.sqlite3"
        
        # Research coordination database
        self.research_db = self.project_root / ".claude" / "research_coordination.db"
        
        # Initialize systems
        self._initialize_database()
        self._load_existing_knowledge()
        self._initialize_cache_system()
        
    def _initialize_database(self):
        """Initialize research coordination database"""
        os.makedirs(os.path.dirname(self.research_db), exist_ok=True)
        
        with sqlite3.connect(self.research_db) as conn:
            # Research queries and results
            conn.execute('''
                CREATE TABLE IF NOT EXISTS research_queries (
                    id INTEGER PRIMARY KEY,
                    original_query TEXT,
                    domain_type TEXT,
                    variations TEXT,
                    cache_key TEXT UNIQUE,
                    priority INTEGER,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'pending'
                )
            ''')
            
            # Research results with quality metrics
            conn.execute('''
                CREATE TABLE IF NOT EXISTS research_results (
                    id INTEGER PRIMARY KEY,
                    query_id INTEGER,
                    query TEXT,
                    sources TEXT,
                    findings TEXT,
                    insights TEXT,
                    cache_status TEXT,
                    quality_score REAL,
                    strategic_value REAL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (query_id) REFERENCES research_queries (id)
                )
            ''')
            
            # Knowledge asset mapping
            conn.execute('''
                CREATE TABLE IF NOT EXISTS knowledge_assets (
                    id INTEGER PRIMARY KEY,
                    file_path TEXT UNIQUE,
                    domain_type TEXT,
                    topics TEXT,
                    semantic_hash TEXT,
                    last_modified TIMESTAMP,
                    relevance_score REAL DEFAULT 0.0
                )
            ''')
            
            # Research agent coordination
            conn.execute('''
                CREATE TABLE IF NOT EXISTS agent_coordination (
                    id INTEGER PRIMARY KEY,
                    research_id INTEGER,
                    agent_name TEXT,
                    task_description TEXT,
                    status TEXT DEFAULT 'assigned',
                    start_time TIMESTAMP,
                    completion_time TIMESTAMP,
                    result_summary TEXT,
                    FOREIGN KEY (research_id) REFERENCES research_queries (id)
                )
            ''')
    
    def _load_existing_knowledge(self):
        """Load and index existing knowledge assets"""
        knowledge_assets = []
        
        # Scan intelligence directory
        for md_file in self.intelligence_dir.glob("*.md"):
            try:
                content = md_file.read_text()
                # Extract domain type from filename patterns
                domain_type = self._classify_domain(md_file.name, content)
                # Extract topics/keywords
                topics = self._extract_topics(content)
                # Generate semantic hash
                semantic_hash = self._generate_semantic_hash(content)
                
                knowledge_assets.append({
                    'file_path': str(md_file),
                    'domain_type': domain_type,
                    'topics': json.dumps(topics),
                    'semantic_hash': semantic_hash,
                    'last_modified': datetime.fromtimestamp(md_file.stat().st_mtime).isoformat()
                })
            except Exception as e:
                print(f"Error processing {md_file}: {e}")
        
        # Store in database
        with sqlite3.connect(self.research_db) as conn:
            for asset in knowledge_assets:
                conn.execute('''
                    INSERT OR REPLACE INTO knowledge_assets 
                    (file_path, domain_type, topics, semantic_hash, last_modified)
                    VALUES (?, ?, ?, ?, ?)
                ''', (asset['file_path'], asset['domain_type'], asset['topics'], 
                     asset['semantic_hash'], asset['last_modified']))
    
    def _classify_domain(self, filename: str, content: str) -> str:
        """Classify domain type based on filename and content"""
        filename_lower = filename.lower()
        content_lower = content.lower()
        
        # Technical domain indicators
        if any(term in filename_lower for term in ['technical', 'architecture', 'implementation', 'performance']):
            return 'technical'
        if any(term in content_lower for term in ['architecture', 'performance', 'implementation', 'technical']):
            return 'technical'
            
        # Market domain indicators  
        if any(term in filename_lower for term in ['competitive', 'market', 'analysis', 'intelligence']):
            return 'market'
        if any(term in content_lower for term in ['competitive', 'market', 'industry', 'business']):
            return 'market'
            
        # Innovation domain indicators
        if any(term in filename_lower for term in ['research', 'innovation', 'trends', 'emerging']):
            return 'innovation'
        if any(term in content_lower for term in ['research', 'innovation', 'emerging', 'academic']):
            return 'innovation'
            
        return 'general'
    
    def _extract_topics(self, content: str) -> List[str]:
        """Extract key topics from content"""
        # Simple topic extraction - in production, would use NLP
        topics = []
        lines = content.split('\n')
        
        for line in lines:
            # Extract from headers
            if line.startswith('#'):
                topic = line.strip('#').strip()
                if len(topic) > 3:
                    topics.append(topic)
            
            # Extract from bullet points
            if line.strip().startswith('-'):
                topic = line.strip('- ').strip()
                if len(topic) > 10 and len(topic) < 100:
                    topics.append(topic)
        
        return topics[:20]  # Limit to 20 topics
    
    def _generate_semantic_hash(self, content: str) -> str:
        """Generate semantic hash for content similarity"""
        # Simple semantic hash - in production, would use embeddings
        normalized = content.lower()
        # Remove common words
        for word in ['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by']:
            normalized = normalized.replace(f' {word} ', ' ')
        
        return hashlib.md5(normalized.encode()).hexdigest()[:16]
    
    def _initialize_cache_system(self):
        """Initialize intelligent caching system"""
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Create cache directories
        cache_dirs = ['by_date', 'by_domain', 'index']
        for dir_name in cache_dirs:
            os.makedirs(self.cache_dir / dir_name, exist_ok=True)
        
        # Initialize cache database
        cache_db = self.cache_dir / "index" / "cache.db"
        with sqlite3.connect(cache_db) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS search_cache (
                    id INTEGER PRIMARY KEY,
                    query_hash TEXT UNIQUE,
                    original_query TEXT,
                    domain_type TEXT,
                    results TEXT,
                    quality_score REAL,
                    hit_count INTEGER DEFAULT 0,
                    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
    
    def generate_research_variations(self, query: str, domain_type: str) -> List[str]:
        """Generate creative research query variations"""
        variations = [query]  # Start with original
        
        # Domain-specific variation patterns
        if domain_type == 'technical':
            variations.extend([
                f"{query} implementation patterns",
                f"{query} architecture best practices", 
                f"{query} performance optimization",
                f"{query} scalability strategies",
                f"{query} integration approaches"
            ])
        elif domain_type == 'market':
            variations.extend([
                f"{query} competitive landscape",
                f"{query} market trends 2024-2025",
                f"{query} industry analysis",
                f"{query} business model analysis", 
                f"{query} market positioning"
            ])
        elif domain_type == 'innovation':
            variations.extend([
                f"{query} research trends",
                f"{query} emerging technologies",
                f"{query} academic research 2024-2025",
                f"{query} innovation opportunities",
                f"{query} future developments"
            ])
        
        # Creative cross-domain variations
        variations.extend([
            f"{query} lessons from other industries",
            f"{query} biological inspiration",
            f"{query} mathematical foundations",
            f"{query} interdisciplinary applications"
        ])
        
        return variations[:10]  # Limit to 10 variations
    
    def check_cache(self, query: str) -> Optional[Dict]:
        """Check cache for similar queries with 85%+ similarity"""
        query_hash = hashlib.md5(query.lower().encode()).hexdigest()
        
        cache_db = self.cache_dir / "index" / "cache.db"
        with sqlite3.connect(cache_db) as conn:
            # Check exact match first
            result = conn.execute(
                'SELECT * FROM search_cache WHERE query_hash = ?', 
                (query_hash,)
            ).fetchone()
            
            if result:
                # Update hit count and access time
                conn.execute(
                    'UPDATE search_cache SET hit_count = hit_count + 1, last_accessed = ? WHERE query_hash = ?',
                    (datetime.now().isoformat(), query_hash)
                )
                return {
                    'query_hash': result[1],
                    'original_query': result[2],
                    'results': json.loads(result[4]),
                    'quality_score': result[5],
                    'cache_status': 'hit'
                }
            
            # Check for semantic similarity (simplified)
            all_cached = conn.execute(
                'SELECT * FROM search_cache ORDER BY last_accessed DESC LIMIT 100'
            ).fetchall()
            
            for cached in all_cached:
                similarity = self._calculate_query_similarity(query, cached[2])
                if similarity >= 0.85:  # 85% similarity threshold
                    conn.execute(
                        'UPDATE search_cache SET hit_count = hit_count + 1, last_accessed = ? WHERE id = ?',
                        (datetime.now().isoformat(), cached[0])
                    )
                    return {
                        'query_hash': cached[1],
                        'original_query': cached[2], 
                        'results': json.loads(cached[4]),
                        'quality_score': cached[5],
                        'cache_status': f'semantic_hit_{similarity:.2f}'
                    }
        
        return None
    
    def _calculate_query_similarity(self, query1: str, query2: str) -> float:
        """Calculate similarity between two queries (simplified implementation)"""
        words1 = set(query1.lower().split())
        words2 = set(query2.lower().split())
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        if not union:
            return 0.0
        
        return len(intersection) / len(union)
    
    def find_relevant_knowledge(self, query: str, domain_type: str) -> List[Dict]:
        """Find relevant existing knowledge assets"""
        with sqlite3.connect(self.research_db) as conn:
            # Find assets by domain type
            domain_results = conn.execute('''
                SELECT file_path, topics, semantic_hash 
                FROM knowledge_assets 
                WHERE domain_type = ? OR domain_type = 'general'
                ORDER BY relevance_score DESC
            ''', (domain_type,)).fetchall()
            
            relevant_assets = []
            query_words = set(query.lower().split())
            
            for file_path, topics_json, semantic_hash in domain_results:
                try:
                    topics = json.loads(topics_json)
                    # Calculate relevance based on topic overlap
                    topic_words = set()
                    for topic in topics:
                        topic_words.update(topic.lower().split())
                    
                    overlap = len(query_words.intersection(topic_words))
                    relevance = overlap / max(len(query_words), 1)
                    
                    if relevance > 0.1:  # 10% relevance threshold
                        relevant_assets.append({
                            'file_path': file_path,
                            'topics': topics,
                            'relevance_score': relevance,
                            'semantic_hash': semantic_hash
                        })
                except:
                    continue
            
            # Sort by relevance and return top 10
            relevant_assets.sort(key=lambda x: x['relevance_score'], reverse=True)
            return relevant_assets[:10]
    
    def coordinate_research_agents(self, research_query: ResearchQuery) -> Dict[str, Any]:
        """Coordinate multiple research agents for comprehensive research"""
        
        # Store research query
        with sqlite3.connect(self.research_db) as conn:
            cursor = conn.execute('''
                INSERT INTO research_queries 
                (original_query, domain_type, variations, cache_key, priority)
                VALUES (?, ?, ?, ?, ?)
            ''', (research_query.original_query, research_query.domain_type,
                 json.dumps(research_query.variations), research_query.cache_key,
                 research_query.priority))
            research_id = cursor.lastrowid
        
        # Define agent coordination strategy
        agent_tasks = []
        
        if research_query.domain_type == 'technical':
            agent_tasks = [
                ('10x-technical-pattern-discovery', f'Technical patterns for {research_query.original_query}'),
                ('10x-code-architecture-specialist', f'Architecture analysis for {research_query.original_query}'),
                ('research-domain-specialist', f'Technical implementation research for {research_query.original_query}')
            ]
        elif research_query.domain_type == 'market':
            agent_tasks = [
                ('10x-competitive-intelligence-researcher', f'Competitive analysis for {research_query.original_query}'),
                ('10x-innovation-intelligence-analyst', f'Market trends for {research_query.original_query}'),
                ('research-domain-specialist', f'Market intelligence for {research_query.original_query}')
            ]
        elif research_query.domain_type == 'innovation':
            agent_tasks = [
                ('10x-innovation-intelligence-analyst', f'Innovation trends for {research_query.original_query}'),
                ('10x-knowledge-synthesis-coordinator', f'Knowledge synthesis for {research_query.original_query}'),
                ('research-domain-specialist', f'Innovation research for {research_query.original_query}')
            ]
        
        # Assign tasks to agents
        with sqlite3.connect(self.research_db) as conn:
            for agent_name, task_description in agent_tasks:
                conn.execute('''
                    INSERT INTO agent_coordination 
                    (research_id, agent_name, task_description, start_time)
                    VALUES (?, ?, ?, ?)
                ''', (research_id, agent_name, task_description, datetime.now().isoformat()))
        
        return {
            'research_id': research_id,
            'agent_tasks': agent_tasks,
            'coordination_status': 'initiated',
            'expected_completion': '15-30 minutes'
        }
    
    def execute_strategic_research(self, query: str, domain_type: str = 'general') -> Dict[str, Any]:
        """Execute strategic research with full system integration"""
        
        print(f"🧠 Executing Strategic Research: {query}")
        print(f"📊 Domain Type: {domain_type}")
        
        # Generate cache key
        cache_key = hashlib.md5(f"{query}_{domain_type}".encode()).hexdigest()
        
        # Check cache first
        cached_result = self.check_cache(query)
        if cached_result:
            print(f"✅ Cache Hit: {cached_result['cache_status']}")
            return {
                'status': 'completed',
                'source': 'cache',
                'cache_status': cached_result['cache_status'],
                'results': cached_result['results'],
                'quality_score': cached_result['quality_score']
            }
        
        # Find relevant existing knowledge
        relevant_knowledge = self.find_relevant_knowledge(query, domain_type)
        print(f"📚 Found {len(relevant_knowledge)} relevant knowledge assets")
        
        # Generate research variations
        variations = self.generate_research_variations(query, domain_type)
        print(f"🔄 Generated {len(variations)} research variations")
        
        # Create research query object
        research_query = ResearchQuery(
            original_query=query,
            domain_type=domain_type,
            variations=variations,
            cache_key=cache_key,
            priority=1,
            expected_sources=5
        )
        
        # Coordinate research agents
        coordination_result = self.coordinate_research_agents(research_query)
        print(f"🤖 Coordinated {len(coordination_result['agent_tasks'])} research agents")
        
        return {
            'status': 'in_progress',
            'research_id': coordination_result['research_id'],
            'cache_status': 'miss',
            'relevant_knowledge': len(relevant_knowledge),
            'research_variations': len(variations),
            'coordinated_agents': len(coordination_result['agent_tasks']),
            'expected_completion': coordination_result['expected_completion']
        }

def main():
    """Main execution function"""
    if len(sys.argv) < 2:
        print("Usage: python research_intelligence_coordinator.py <query> [domain_type]")
        sys.exit(1)
    
    query = sys.argv[1]
    domain_type = sys.argv[2] if len(sys.argv) > 2 else 'general'
    
    coordinator = ResearchIntelligenceCoordinator()
    result = coordinator.execute_strategic_research(query, domain_type)
    
    print("\n" + "="*60)
    print("🎯 STRATEGIC RESEARCH COORDINATION COMPLETE")
    print("="*60)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()