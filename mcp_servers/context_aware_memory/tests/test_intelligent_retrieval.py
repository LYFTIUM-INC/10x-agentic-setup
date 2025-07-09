"""
Tests for Intelligent Retrieval System (Phase 2)
"""

import pytest
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add paths
sys.path.append(str(Path(__file__).parent.parent / "src"))
sys.path.append(str(Path(__file__).parent.parent.parent / "shared" / "src"))

from tools.semantic_storage import SemanticMemoryStore, MemoryItem, MemoryContext, MemoryQuery, MemoryType, AccessLevel
from tools.intelligent_retrieval import IntelligentRetriever, RetrievalStrategy, ContextAnalyzer, UserProfile
from utils.config_utils import create_development_config


class TestIntelligentRetrieval:
    """Test suite for intelligent retrieval system"""
    
    @pytest.fixture
    async def setup_retrieval_system(self):
        """Set up memory store and retriever for testing"""
        store = SemanticMemoryStore(data_dir="./test_memory_retrieval")
        await store.initialize()
        
        retriever = IntelligentRetriever(store)
        
        # Create test memories
        test_memories = [
            MemoryItem(
                content="Python function for calculating Fibonacci numbers recursively",
                memory_type=MemoryType.CODE,
                context=MemoryContext(
                    project="math_library",
                    user="alice",
                    session="session_1",
                    application="vscode"
                ),
                tags=["python", "fibonacci", "recursion", "math"],
                importance=0.8
            ),
            MemoryItem(
                content="Meeting notes about API design and REST endpoints",
                memory_type=MemoryType.CONVERSATION,
                context=MemoryContext(
                    project="web_service",
                    user="bob",
                    session="session_2",
                    application="slack"
                ),
                tags=["meeting", "api", "rest", "design"],
                importance=0.9
            ),
            MemoryItem(
                content="Documentation for database connection pooling",
                memory_type=MemoryType.DOCUMENT,
                context=MemoryContext(
                    project="web_service",
                    user="alice",
                    session="session_3",
                    application="confluence"
                ),
                tags=["documentation", "database", "connection", "pooling"],
                importance=0.7
            ),
            MemoryItem(
                content="TODO: Implement caching for frequently accessed data",
                memory_type=MemoryType.TASK,
                context=MemoryContext(
                    project="web_service",
                    user="charlie",
                    session="session_4",
                    application="jira"
                ),
                tags=["todo", "caching", "performance", "optimization"],
                importance=0.6
            ),
            MemoryItem(
                content="JavaScript async/await pattern for handling promises",
                memory_type=MemoryType.CODE,
                context=MemoryContext(
                    project="frontend_app",
                    user="alice",
                    session="session_5",
                    application="vscode"
                ),
                tags=["javascript", "async", "await", "promises"],
                importance=0.7
            )
        ]
        
        # Store memories
        for memory in test_memories:
            await store.store_memory(memory)
        
        return store, retriever, test_memories
    
    @pytest.mark.asyncio
    async def test_semantic_retrieval_strategy(self, setup_retrieval_system):
        """Test semantic similarity-based retrieval"""
        store, retriever, test_memories = await setup_retrieval_system
        
        # Test semantic search for programming content
        query = MemoryQuery(
            query_text="fibonacci calculation function",
            context=MemoryContext(user="alice"),
            max_results=3,
            similarity_threshold=0.1,
            strategy=RetrievalStrategy.SEMANTIC
        )
        
        results = await retriever.retrieve(query)
        
        # Should find the fibonacci-related memory
        assert len(results) > 0
        
        # Check that fibonacci memory is in results
        fibonacci_found = any("fibonacci" in result.content.lower() for result in results)
        assert fibonacci_found, "Fibonacci memory should be found in semantic search"
        
        print(f"✅ Semantic retrieval found {len(results)} memories")
        for result in results:
            print(f"   - {result.content[:50]}... (similarity: {getattr(result, 'similarity_score', 0.0):.3f})")
    
    @pytest.mark.asyncio
    async def test_contextual_retrieval_strategy(self, setup_retrieval_system):
        """Test context-based retrieval"""
        store, retriever, test_memories = await setup_retrieval_system
        
        # Test contextual search for same project
        query = MemoryQuery(
            query_text="web service documentation",
            context=MemoryContext(project="web_service", user="alice"),
            max_results=5,
            strategy=RetrievalStrategy.CONTEXTUAL
        )
        
        results = await retriever.retrieve(query)
        
        # Should find memories from the same project
        assert len(results) > 0
        
        # Check project context matching
        web_service_results = [r for r in results if r.context and r.context.project == "web_service"]
        assert len(web_service_results) > 0, "Should find memories from web_service project"
        
        print(f"✅ Contextual retrieval found {len(results)} memories")
        for result in results:
            project = result.context.project if result.context else "unknown"
            print(f"   - {result.content[:50]}... (project: {project})")
    
    @pytest.mark.asyncio
    async def test_hybrid_retrieval_strategy(self, setup_retrieval_system):
        """Test hybrid retrieval combining multiple strategies"""
        store, retriever, test_memories = await setup_retrieval_system
        
        # Test hybrid search
        query = MemoryQuery(
            query_text="API database connection",
            context=MemoryContext(project="web_service", user="alice"),
            max_results=5,
            strategy=RetrievalStrategy.HYBRID
        )
        
        results = await retriever.retrieve(query)
        
        # Should find relevant memories using multiple factors
        assert len(results) > 0
        
        # Should include both semantic and contextual matches
        api_related = any("api" in result.content.lower() for result in results)
        db_related = any("database" in result.content.lower() for result in results)
        
        assert api_related or db_related, "Should find API or database related content"
        
        print(f"✅ Hybrid retrieval found {len(results)} memories")
        for result in results:
            similarity = getattr(result, 'similarity_score', 0.0)
            print(f"   - {result.content[:50]}... (score: {similarity:.3f})")
    
    @pytest.mark.asyncio
    async def test_importance_based_retrieval(self, setup_retrieval_system):
        """Test importance-based retrieval"""
        store, retriever, test_memories = await setup_retrieval_system
        
        # Test importance-based search
        query = MemoryQuery(
            query_text="important items",
            context=MemoryContext(user="alice"),
            max_results=3,
            strategy=RetrievalStrategy.IMPORTANCE
        )
        
        results = await retriever.retrieve(query)
        
        # Should find memories ordered by importance
        assert len(results) > 0
        
        # Check that results are ordered by importance
        if len(results) > 1:
            for i in range(len(results) - 1):
                assert results[i].importance >= results[i + 1].importance, \
                    "Results should be ordered by importance"
        
        print(f"✅ Importance-based retrieval found {len(results)} memories")
        for result in results:
            print(f"   - {result.content[:50]}... (importance: {result.importance})")
    
    @pytest.mark.asyncio
    async def test_temporal_retrieval_strategy(self, setup_retrieval_system):
        """Test temporal relevance-based retrieval"""
        store, retriever, test_memories = await setup_retrieval_system
        
        # Test temporal search
        query = MemoryQuery(
            query_text="recent items",
            context=MemoryContext(user="alice"),
            max_results=5,
            strategy=RetrievalStrategy.TEMPORAL
        )
        
        results = await retriever.retrieve(query)
        
        # Should find memories based on temporal relevance
        assert len(results) > 0
        
        # Check that recent memories are prioritized
        for result in results:
            age_hours = (datetime.now() - result.created_at).total_seconds() / 3600
            assert age_hours < 24 * 365, "Should return reasonably recent memories"
        
        print(f"✅ Temporal retrieval found {len(results)} memories")
        for result in results:
            age_hours = (datetime.now() - result.created_at).total_seconds() / 3600
            print(f"   - {result.content[:50]}... (age: {age_hours:.1f}h)")
    
    @pytest.mark.asyncio
    async def test_context_analyzer(self, setup_retrieval_system):
        """Test context analysis functionality"""
        store, retriever, test_memories = await setup_retrieval_system
        
        analyzer = ContextAnalyzer()
        
        # Test context analysis
        context = MemoryContext(
            project="web_service",
            user="alice",
            session="session_1",
            application="vscode",
            environment="development"
        )
        
        query = "How do I implement async API endpoints?"
        features = analyzer.analyze_context(context, query)
        
        # Check that context features are extracted
        assert 'temporal_context' in features
        assert 'semantic_context' in features
        assert 'project_context' in features
        assert 'user_context' in features
        assert 'session_context' in features
        assert 'environment_context' in features
        
        # Check semantic analysis
        semantic = features['semantic_context']
        assert 'query_type' in semantic
        assert 'domain' in semantic
        assert 'has_technical_terms' in semantic
        
        # Should detect technical terms
        assert semantic['has_technical_terms'] == True
        
        print(f"✅ Context analyzer extracted {len(features)} feature groups")
        print(f"   - Query type: {semantic['query_type']}")
        print(f"   - Domain: {semantic['domain']}")
        print(f"   - Technical terms: {semantic['has_technical_terms']}")
    
    @pytest.mark.asyncio
    async def test_user_profile_learning(self, setup_retrieval_system):
        """Test user profile creation and learning"""
        store, retriever, test_memories = await setup_retrieval_system
        
        # Simulate multiple queries to build user profile
        queries = [
            MemoryQuery(
                query_text="python functions",
                context=MemoryContext(user="alice", project="math_library"),
                max_results=3
            ),
            MemoryQuery(
                query_text="fibonacci algorithm",
                context=MemoryContext(user="alice", project="math_library"),
                max_results=3
            ),
            MemoryQuery(
                query_text="recursion patterns",
                context=MemoryContext(user="alice", project="math_library"),
                max_results=3
            )
        ]
        
        # Execute queries to build profile
        for query in queries:
            await retriever.retrieve(query)
        
        # Check that user profile was created
        user_profile = retriever._get_user_profile(MemoryContext(user="alice"))
        assert user_profile.user_id == "alice"
        
        # Check that preferences were learned
        assert len(user_profile.content_preferences) > 0
        assert MemoryType.CODE in user_profile.content_preferences
        
        print(f"✅ User profile created for alice")
        print(f"   - Content preferences: {len(user_profile.content_preferences)}")
        print(f"   - Tag preferences: {len(user_profile.preferences)}")
    
    @pytest.mark.asyncio
    async def test_retrieval_caching(self, setup_retrieval_system):
        """Test query caching functionality"""
        store, retriever, test_memories = await setup_retrieval_system
        
        query = MemoryQuery(
            query_text="fibonacci calculation",
            context=MemoryContext(user="alice"),
            max_results=3
        )
        
        # First retrieval
        start_time = asyncio.get_event_loop().time()
        results1 = await retriever.retrieve(query)
        time1 = asyncio.get_event_loop().time() - start_time
        
        # Second retrieval (should be cached)
        start_time = asyncio.get_event_loop().time()
        results2 = await retriever.retrieve(query)
        time2 = asyncio.get_event_loop().time() - start_time
        
        # Results should be the same
        assert len(results1) == len(results2)
        
        # Should have used cache (may not be significantly faster in test)
        assert len(retriever.query_cache) > 0
        
        print(f"✅ Query caching working")
        print(f"   - First query: {time1:.4f}s")
        print(f"   - Second query: {time2:.4f}s")
        print(f"   - Cache size: {len(retriever.query_cache)}")
    
    @pytest.mark.asyncio
    async def test_strategy_performance_tracking(self, setup_retrieval_system):
        """Test strategy performance tracking"""
        store, retriever, test_memories = await setup_retrieval_system
        
        # Test different strategies
        strategies = [
            RetrievalStrategy.SEMANTIC,
            RetrievalStrategy.CONTEXTUAL,
            RetrievalStrategy.HYBRID
        ]
        
        for strategy in strategies:
            query = MemoryQuery(
                query_text="API documentation",
                context=MemoryContext(user="alice", project="web_service"),
                max_results=3,
                strategy=strategy
            )
            
            await retriever.retrieve(query)
        
        # Check that performance is being tracked
        assert len(retriever.strategy_performance) > 0
        
        # Check that strategies were recorded
        for strategy in strategies:
            if strategy in retriever.strategy_performance:
                assert len(retriever.strategy_performance[strategy]) > 0
        
        print(f"✅ Strategy performance tracking working")
        print(f"   - Strategies tracked: {len(retriever.strategy_performance)}")
    
    @pytest.mark.asyncio
    async def test_diversity_filtering(self, setup_retrieval_system):
        """Test diversity filtering in results"""
        store, retriever, test_memories = await setup_retrieval_system
        
        # Add some duplicate-like memories
        duplicate_memories = [
            MemoryItem(
                content="Another Python fibonacci implementation using iteration",
                memory_type=MemoryType.CODE,
                context=MemoryContext(project="math_library", user="bob"),
                tags=["python", "fibonacci", "iteration"],
                importance=0.6
            ),
            MemoryItem(
                content="Third fibonacci function with memoization",
                memory_type=MemoryType.CODE,
                context=MemoryContext(project="math_library", user="charlie"),
                tags=["python", "fibonacci", "memoization"],
                importance=0.7
            )
        ]
        
        for memory in duplicate_memories:
            await store.store_memory(memory)
        
        # Query for fibonacci
        query = MemoryQuery(
            query_text="fibonacci function",
            context=MemoryContext(user="alice"),
            max_results=10,
            strategy=RetrievalStrategy.SEMANTIC
        )
        
        results = await retriever.retrieve(query)
        
        # Should find multiple fibonacci memories
        fibonacci_results = [r for r in results if "fibonacci" in r.content.lower()]
        assert len(fibonacci_results) > 1
        
        # Check diversity (different content hashes)
        content_hashes = set(r.content_hash for r in results)
        assert len(content_hashes) == len(results), "Results should have diverse content"
        
        print(f"✅ Diversity filtering working")
        print(f"   - Total results: {len(results)}")
        print(f"   - Fibonacci results: {len(fibonacci_results)}")
        print(f"   - Unique content: {len(content_hashes)}")


@pytest.mark.asyncio
async def test_end_to_end_retrieval():
    """Test complete end-to-end retrieval workflow"""
    store = SemanticMemoryStore(data_dir="./test_memory_e2e")
    await store.initialize()
    
    retriever = IntelligentRetriever(store)
    
    # Create diverse test memories
    memories = [
        MemoryItem(
            content="React component for user authentication with hooks",
            memory_type=MemoryType.CODE,
            context=MemoryContext(project="frontend", user="alice"),
            tags=["react", "authentication", "hooks"],
            importance=0.8
        ),
        MemoryItem(
            content="Meeting about sprint planning and task assignments",
            memory_type=MemoryType.CONVERSATION,
            context=MemoryContext(project="frontend", user="bob"),
            tags=["meeting", "sprint", "planning"],
            importance=0.7
        ),
        MemoryItem(
            content="API documentation for user management endpoints",
            memory_type=MemoryType.DOCUMENT,
            context=MemoryContext(project="backend", user="charlie"),
            tags=["api", "documentation", "user"],
            importance=0.9
        )
    ]
    
    # Store memories
    for memory in memories:
        await store.store_memory(memory)
    
    # Test comprehensive retrieval
    query = MemoryQuery(
        query_text="user authentication system",
        context=MemoryContext(project="frontend", user="alice"),
        max_results=5,
        strategy=RetrievalStrategy.HYBRID
    )
    
    results = await retriever.retrieve(query)
    
    # Should find relevant memories
    assert len(results) > 0
    
    # Should prioritize relevant content
    auth_related = any("authentication" in result.content.lower() for result in results)
    user_related = any("user" in result.content.lower() for result in results)
    
    assert auth_related or user_related, "Should find authentication or user related content"
    
    print(f"✅ End-to-end retrieval test passed")
    print(f"   - Found {len(results)} relevant memories")
    
    # Cleanup
    await store.save_state()


if __name__ == "__main__":
    async def run_tests():
        print("🧪 Running Intelligent Retrieval Tests (Phase 2)...")
        
        # Create test instance
        test_instance = TestIntelligentRetrieval()
        
        # Run individual tests
        setup = await test_instance.setup_retrieval_system()
        
        await test_instance.test_semantic_retrieval_strategy(setup)
        await test_instance.test_contextual_retrieval_strategy(setup)
        await test_instance.test_hybrid_retrieval_strategy(setup)
        await test_instance.test_importance_based_retrieval(setup)
        await test_instance.test_temporal_retrieval_strategy(setup)
        await test_instance.test_context_analyzer(setup)
        await test_instance.test_user_profile_learning(setup)
        await test_instance.test_retrieval_caching(setup)
        await test_instance.test_strategy_performance_tracking(setup)
        await test_instance.test_diversity_filtering(setup)
        
        # Run end-to-end test
        await test_end_to_end_retrieval()
        
        print("\n✅ All intelligent retrieval tests passed!")
        print("🎉 Phase 2 (Intelligent Retrieval) implementation complete!")
    
    asyncio.run(run_tests())