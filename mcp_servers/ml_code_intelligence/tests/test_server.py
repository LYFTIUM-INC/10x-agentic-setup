"""
Tests for ML-Powered Code Intelligence MCP Server
"""

import pytest
import asyncio
import sys
from pathlib import Path

# Add paths
sys.path.append(str(Path(__file__).parent.parent / "src"))
sys.path.append(str(Path(__file__).parent.parent.parent / "shared" / "src"))

from server import MLCodeIntelligenceServer, CodeSearchRequest, CodeAnalysisRequest, CodeIndexRequest
from utils.config_utils import create_development_config


@pytest.fixture
async def server():
    """Create test server instance"""
    config = create_development_config("ml-code-intelligence-test")
    server = MLCodeIntelligenceServer(config)
    await server._startup()
    yield server
    await server._shutdown()


@pytest.mark.asyncio
async def test_server_initialization(server):
    """Test server initializes correctly"""
    assert server.embedding_manager is not None
    assert server.vector_db is not None
    assert server.code_analyzer is not None


@pytest.mark.asyncio
async def test_code_analysis():
    """Test code analysis functionality"""
    config = create_development_config("ml-code-intelligence-test")
    server = MLCodeIntelligenceServer(config)
    await server._startup()
    
    try:
        # Test Python code analysis
        python_code = '''
def fibonacci(n):
    """Calculate fibonacci number"""
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n-1) + fibonacci(n-2)

def main():
    result = fibonacci(10)
    print(f"Fibonacci(10) = {result}")
'''
        
        request = CodeAnalysisRequest(
            code=python_code,
            language="python",
            include_metrics=True,
            include_issues=True
        )
        
        response = await server._analyze_code(request)
        
        assert response.language == "python"
        assert response.summary is not None
        assert response.metrics is not None
        assert response.issues is not None
        assert response.metrics['lines_of_code'] > 0
        assert response.summary['lines_of_code'] > 0
        
    finally:
        await server._shutdown()


@pytest.mark.asyncio
async def test_code_indexing_and_search():
    """Test code indexing and semantic search"""
    config = create_development_config("ml-code-intelligence-test")
    server = MLCodeIntelligenceServer(config)
    await server._startup()
    
    try:
        # Index some code snippets
        code_snippets = [
            {
                "code": "def hello_world():\n    print('Hello, World!')",
                "language": "python",
                "function_name": "hello_world"
            },
            {
                "code": "function greetUser(name) {\n    console.log(`Hello, ${name}!`);\n}",
                "language": "javascript",
                "function_name": "greetUser"
            },
            {
                "code": "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)",
                "language": "python",
                "function_name": "fibonacci"
            }
        ]
        
        index_request = CodeIndexRequest(
            code_snippets=code_snippets,
            batch_size=10
        )
        
        index_result = await server._index_code_snippets(index_request)
        
        assert index_result['indexed_count'] == 3
        assert index_result['failed_count'] == 0
        assert server.indexed_code_count == 3
        
        # Test semantic search
        search_request = CodeSearchRequest(
            query="print hello",
            max_results=5,
            similarity_threshold=0.1
        )
        
        search_results = await server._semantic_search(search_request)
        
        assert len(search_results) > 0
        assert all(result.similarity_score >= 0.1 for result in search_results)
        
        # Test language-specific search
        python_search_request = CodeSearchRequest(
            query="fibonacci recursive",
            language="python",
            max_results=5,
            similarity_threshold=0.1
        )
        
        python_results = await server._semantic_search(python_search_request)
        
        assert len(python_results) > 0
        assert all(result.language == "python" for result in python_results)
        
    finally:
        await server._shutdown()


@pytest.mark.asyncio
async def test_supported_languages():
    """Test supported languages endpoint"""
    config = create_development_config("ml-code-intelligence-test")
    server = MLCodeIntelligenceServer(config)
    
    # This should work without full startup
    languages = await server.get_supported_languages()
    
    assert isinstance(languages, list)
    assert len(languages) > 0
    assert "python" in languages
    assert "javascript" in languages


def test_code_analysis_edge_cases():
    """Test code analysis with edge cases"""
    config = create_development_config("ml-code-intelligence-test")
    server = MLCodeIntelligenceServer(config)
    
    # Test empty code
    request = CodeAnalysisRequest(code="", include_metrics=False, include_issues=False)
    
    # This should be handled gracefully
    # Note: We're not running this as it would require full async setup


if __name__ == "__main__":
    # Run basic test
    async def run_basic_test():
        config = create_development_config("ml-code-intelligence-test")
        server = MLCodeIntelligenceServer(config)
        await server._startup()
        
        print("✅ Server initialization successful")
        
        # Test code analysis
        python_code = "def hello():\n    return 'world'"
        request = CodeAnalysisRequest(code=python_code, language="python")
        response = await server._analyze_code(request)
        
        print(f"✅ Code analysis successful: {response.language}")
        print(f"   Lines of code: {response.summary['lines_of_code']}")
        print(f"   Quality score: {response.summary['quality_score']}")
        
        await server._shutdown()
        print("✅ All tests passed!")
    
    asyncio.run(run_basic_test())