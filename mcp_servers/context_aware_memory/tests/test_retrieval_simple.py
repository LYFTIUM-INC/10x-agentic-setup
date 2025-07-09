"""
Simple Tests for Intelligent Retrieval System (Phase 2)
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add paths
sys.path.append(str(Path(__file__).parent.parent / "src"))
sys.path.append(str(Path(__file__).parent.parent.parent / "shared" / "src"))

from tools.semantic_storage import SemanticMemoryStore, MemoryItem, MemoryContext, MemoryQuery, MemoryType, AccessLevel
from tools.intelligent_retrieval import IntelligentRetriever, RetrievalStrategy, ContextAnalyzer


async def test_semantic_retrieval():
    """Test semantic retrieval functionality"""
    print("🧪 Testing semantic retrieval...")
    
    store = SemanticMemoryStore(data_dir="./test_memory_semantic")
    await store.initialize()
    
    retriever = IntelligentRetriever(store)
    
    # Create test memories
    memories = [
        MemoryItem(
            content="Python function for calculating Fibonacci numbers",
            memory_type=MemoryType.CODE,
            context=MemoryContext(project="math_lib", user="alice"),
            tags=["python", "fibonacci", "math"],
            importance=0.8
        ),
        MemoryItem(
            content="Meeting notes about API design",
            memory_type=MemoryType.CONVERSATION,
            context=MemoryContext(project="web_service", user="bob"),
            tags=["meeting", "api", "design"],
            importance=0.7
        ),
        MemoryItem(
            content="JavaScript async/await patterns",
            memory_type=MemoryType.CODE,
            context=MemoryContext(project="frontend", user="charlie"),
            tags=["javascript", "async", "patterns"],
            importance=0.6
        )
    ]
    
    # Store memories
    for memory in memories:
        await store.store_memory(memory)
    
    # Test semantic search
    query = MemoryQuery(
        query_text="fibonacci calculation",
        context=MemoryContext(user="alice"),
        max_results=3,
        strategy=RetrievalStrategy.SEMANTIC
    )
    
    results = await retriever.retrieve(query)
    
    # Should find the fibonacci memory
    assert len(results) > 0
    fibonacci_found = any("fibonacci" in result.content.lower() for result in results)
    assert fibonacci_found, "Should find fibonacci memory"
    
    print(f"✅ Semantic retrieval found {len(results)} memories")
    for result in results:
        print(f"   - {result.content[:50]}...")
    
    return store, retriever


async def test_contextual_retrieval():
    """Test contextual retrieval functionality"""
    print("\n🧪 Testing contextual retrieval...")
    
    store = SemanticMemoryStore(data_dir="./test_memory_contextual")
    await store.initialize()
    
    retriever = IntelligentRetriever(store)
    
    # Create memories with different contexts
    memories = [
        MemoryItem(
            content="Database schema for user management",
            memory_type=MemoryType.DOCUMENT,
            context=MemoryContext(project="user_service", user="alice"),
            tags=["database", "schema", "user"],
            importance=0.8
        ),
        MemoryItem(
            content="API endpoints for user authentication",
            memory_type=MemoryType.DOCUMENT,
            context=MemoryContext(project="user_service", user="bob"),
            tags=["api", "authentication", "user"],
            importance=0.9
        ),
        MemoryItem(
            content="Frontend component for login form",
            memory_type=MemoryType.CODE,
            context=MemoryContext(project="frontend_app", user="charlie"),
            tags=["frontend", "login", "form"],
            importance=0.7
        )
    ]
    
    # Store memories
    for memory in memories:
        await store.store_memory(memory)
    
    # Test contextual search for same project
    query = MemoryQuery(
        query_text="user management",
        context=MemoryContext(project="user_service", user="alice"),
        max_results=5,
        strategy=RetrievalStrategy.CONTEXTUAL
    )
    
    results = await retriever.retrieve(query)
    
    # Should find memories from same project
    assert len(results) > 0
    user_service_results = [r for r in results if r.context and r.context.project == "user_service"]
    assert len(user_service_results) > 0, "Should find user_service project memories"
    
    print(f"✅ Contextual retrieval found {len(results)} memories")
    for result in results:
        project = result.context.project if result.context else "unknown"
        print(f"   - {result.content[:50]}... (project: {project})")
    
    return store, retriever


async def test_hybrid_retrieval():
    """Test hybrid retrieval functionality"""
    print("\n🧪 Testing hybrid retrieval...")
    
    store = SemanticMemoryStore(data_dir="./test_memory_hybrid")
    await store.initialize()
    
    retriever = IntelligentRetriever(store)
    
    # Create diverse memories
    memories = [
        MemoryItem(
            content="React component for data visualization",
            memory_type=MemoryType.CODE,
            context=MemoryContext(project="dashboard", user="alice"),
            tags=["react", "visualization", "data"],
            importance=0.8
        ),
        MemoryItem(
            content="Data processing pipeline documentation",
            memory_type=MemoryType.DOCUMENT,
            context=MemoryContext(project="dashboard", user="bob"),
            tags=["data", "pipeline", "processing"],
            importance=0.9
        ),
        MemoryItem(
            content="SQL queries for analytics dashboard",
            memory_type=MemoryType.CODE,
            context=MemoryContext(project="analytics", user="charlie"),
            tags=["sql", "analytics", "queries"],
            importance=0.7
        )
    ]
    
    # Store memories
    for memory in memories:
        await store.store_memory(memory)
    
    # Test hybrid search
    query = MemoryQuery(
        query_text="data dashboard visualization",
        context=MemoryContext(project="dashboard", user="alice"),
        max_results=5,
        strategy=RetrievalStrategy.HYBRID
    )
    
    results = await retriever.retrieve(query)
    
    # Should find relevant memories
    assert len(results) > 0
    data_related = any("data" in result.content.lower() for result in results)
    assert data_related, "Should find data-related content"
    
    print(f"✅ Hybrid retrieval found {len(results)} memories")
    for result in results:
        similarity = getattr(result, 'similarity_score', 0.0)
        print(f"   - {result.content[:50]}... (score: {similarity:.3f})")
    
    return store, retriever


async def test_context_analyzer():
    """Test context analyzer functionality"""
    print("\n🧪 Testing context analyzer...")
    
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
    
    # Check that features are extracted
    assert 'temporal_context' in features
    assert 'semantic_context' in features
    assert 'project_context' in features
    
    # Check semantic analysis
    semantic = features['semantic_context']
    assert 'query_type' in semantic
    assert 'domain' in semantic
    assert 'has_technical_terms' in semantic
    
    # Should detect technical terms
    assert semantic['has_technical_terms'] == True
    
    print(f"✅ Context analyzer working")
    print(f"   - Query type: {semantic['query_type']}")
    print(f"   - Domain: {semantic['domain']}")
    print(f"   - Technical terms: {semantic['has_technical_terms']}")


async def test_user_profile_learning():
    """Test user profile learning"""
    print("\n🧪 Testing user profile learning...")
    
    store = SemanticMemoryStore(data_dir="./test_memory_profile")
    await store.initialize()
    
    retriever = IntelligentRetriever(store)
    
    # Add some memories
    memories = [
        MemoryItem(
            content="Python function for data processing",
            memory_type=MemoryType.CODE,
            context=MemoryContext(project="data_app", user="alice"),
            tags=["python", "data", "processing"],
            importance=0.8
        ),
        MemoryItem(
            content="Machine learning model training",
            memory_type=MemoryType.DOCUMENT,
            context=MemoryContext(project="ml_project", user="alice"),
            tags=["ml", "training", "model"],
            importance=0.9
        )
    ]
    
    for memory in memories:
        await store.store_memory(memory)
    
    # Simulate queries to build profile
    queries = [
        MemoryQuery(
            query_text="python data processing",
            context=MemoryContext(user="alice"),
            max_results=3
        ),
        MemoryQuery(
            query_text="machine learning models",
            context=MemoryContext(user="alice"),
            max_results=3
        )
    ]
    
    # Execute queries
    for query in queries:
        await retriever.retrieve(query)
    
    # Check user profile
    user_profile = retriever._get_user_profile(MemoryContext(user="alice"))
    assert user_profile.user_id == "alice"
    
    print(f"✅ User profile learning working")
    print(f"   - User ID: {user_profile.user_id}")
    print(f"   - Content preferences: {len(user_profile.content_preferences)}")


async def test_retrieval_strategies():
    """Test different retrieval strategies"""
    print("\n🧪 Testing retrieval strategies...")
    
    store = SemanticMemoryStore(data_dir="./test_memory_strategies")
    await store.initialize()
    
    retriever = IntelligentRetriever(store)
    
    # Add test memory
    memory = MemoryItem(
        content="Important API documentation for authentication",
        memory_type=MemoryType.DOCUMENT,
        context=MemoryContext(project="auth_service", user="alice"),
        tags=["api", "authentication", "important"],
        importance=0.9
    )
    await store.store_memory(memory)
    
    # Test different strategies
    strategies = [
        RetrievalStrategy.SEMANTIC,
        RetrievalStrategy.CONTEXTUAL,
        RetrievalStrategy.IMPORTANCE,
        RetrievalStrategy.HYBRID
    ]
    
    for strategy in strategies:
        query = MemoryQuery(
            query_text="authentication documentation",
            context=MemoryContext(project="auth_service", user="alice"),
            max_results=3,
            strategy=strategy
        )
        
        results = await retriever.retrieve(query)
        
        print(f"   - {strategy.value}: {len(results)} results")
        
        # Should find at least one result for each strategy
        assert len(results) > 0, f"Strategy {strategy.value} should return results"
    
    print("✅ All retrieval strategies working")


async def main():
    """Run all tests"""
    print("🧪 Running Intelligent Retrieval Tests (Phase 2)...")
    
    try:
        await test_semantic_retrieval()
        await test_contextual_retrieval()
        await test_hybrid_retrieval()
        await test_context_analyzer()
        await test_user_profile_learning()
        await test_retrieval_strategies()
        
        print("\n✅ All intelligent retrieval tests passed!")
        print("🎉 Phase 2 (Intelligent Retrieval) implementation complete!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())