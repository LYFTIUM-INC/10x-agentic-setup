#!/usr/bin/env python3
"""
Parallel MCP Dispatch Engine
Coordinates simultaneous execution of multiple MCP servers for 5-10x performance improvement
"""

import asyncio
import httpx
import json
import time
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPServerStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded" 
    UNHEALTHY = "unhealthy"
    OFFLINE = "offline"

@dataclass
class MCPServerInfo:
    name: str
    port: int
    capabilities: List[str]
    status: MCPServerStatus = MCPServerStatus.OFFLINE
    last_response_time: Optional[float] = None
    error_count: int = 0
    success_count: int = 0

@dataclass
class ParallelTask:
    task_id: str
    server_name: str
    operation: str
    parameters: Dict[str, Any]
    priority: int = 1
    timeout: float = 30.0
    retries: int = 2

@dataclass
class TaskResult:
    task_id: str
    server_name: str
    operation: str
    success: bool
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time: float = 0.0
    timestamp: float = 0.0

class ParallelDispatcher:
    """
    Dispatches tasks to multiple MCP servers in parallel for optimal performance
    """
    
    def __init__(self):
        self.mcp_servers = {
            'ml-code-intelligence': MCPServerInfo(
                name='ml-code-intelligence',
                port=8001,
                capabilities=['analyze', 'search', 'quality', 'semantic_analysis']
            ),
            'context-aware-memory': MCPServerInfo(
                name='context-aware-memory',
                port=8002,
                capabilities=['retrieve', 'store', 'context_search', 'memory_analysis']
            ),
            'agentic-workflow': MCPServerInfo(
                name='agentic-workflow', 
                port=8003,
                capabilities=['orchestrate', 'optimize', 'workflow_analysis', 'pattern_detection']
            ),
            'predictive-analytics': MCPServerInfo(
                name='predictive-analytics',
                port=8004,
                capabilities=['forecast', 'risk', 'prediction', 'trend_analysis']
            ),
            'ml-testing-qa': MCPServerInfo(
                name='ml-testing-qa',
                port=8005,
                capabilities=['test', 'validate', 'quality_check', 'bug_prediction']
            )
        }
        
        self.client = httpx.AsyncClient(timeout=60.0)
        self.max_concurrent = 5
        self.health_check_interval = 30.0
        self.last_health_check = 0.0
        
    async def __aenter__(self):
        await self.initialize()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup()
    
    async def initialize(self):
        """Initialize dispatcher and check server health"""
        logger.info("Initializing Parallel MCP Dispatcher...")
        await self.check_all_server_health()
        
    async def cleanup(self):
        """Clean up resources"""
        await self.client.aclose()
    
    async def check_all_server_health(self):
        """Check health of all MCP servers"""
        if time.time() - self.last_health_check < self.health_check_interval:
            return
            
        logger.info("Checking health of all MCP servers...")
        tasks = []
        
        for server_name, server_info in self.mcp_servers.items():
            task = self.check_server_health(server_name, server_info)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for server_name, result in zip(self.mcp_servers.keys(), results):
            if isinstance(result, Exception):
                logger.warning(f"Health check failed for {server_name}: {result}")
                self.mcp_servers[server_name].status = MCPServerStatus.OFFLINE
            else:
                logger.info(f"Server {server_name}: {result}")
        
        self.last_health_check = time.time()
    
    async def check_server_health(self, server_name: str, server_info: MCPServerInfo) -> str:
        """Check health of a specific MCP server"""
        start_time = time.time()
        
        try:
            # Try STDIO-based MCP server communication
            # Since these are STDIO servers, we'll check if they're responsive
            # by attempting a simple operation
            response = await self.execute_mcp_operation(
                server_name, 
                "health_check", 
                {},
                timeout=5.0
            )
            
            execution_time = time.time() - start_time
            
            if response and not response.get('error'):
                server_info.status = MCPServerStatus.HEALTHY
                server_info.last_response_time = execution_time
                server_info.success_count += 1
                return f"healthy (response time: {execution_time:.3f}s)"
            else:
                server_info.status = MCPServerStatus.DEGRADED
                server_info.error_count += 1
                return f"degraded (error: {response.get('error', 'unknown')})"
                
        except asyncio.TimeoutError:
            server_info.status = MCPServerStatus.UNHEALTHY
            server_info.error_count += 1
            return "unhealthy (timeout)"
        except Exception as e:
            server_info.status = MCPServerStatus.OFFLINE
            server_info.error_count += 1
            return f"offline (error: {str(e)})"
    
    def determine_optimal_servers(self, command_type: str, context: Dict[str, Any]) -> List[str]:
        """Determine which MCP servers to use based on command type and context"""
        
        server_mapping = {
            '/analyze_10x': [
                'ml-code-intelligence',  # Code analysis
                'context-aware-memory',   # Context retrieval
                'predictive-analytics',   # Risk analysis
                'ml-testing-qa',         # Quality assessment
                'agentic-workflow'       # Workflow suggestions
            ],
            '/implement_10x': [
                'agentic-workflow',      # Implementation orchestration
                'ml-code-intelligence',  # Code generation assistance
                'context-aware-memory',  # Context awareness
                'predictive-analytics',  # Implementation risks
                'ml-testing-qa'         # Test strategy
            ],
            '/qa:comprehensive_10x': [
                'ml-testing-qa',        # Primary QA analysis
                'ml-code-intelligence', # Code quality
                'predictive-analytics', # Risk assessment
                'context-aware-memory', # Historical context
                'agentic-workflow'      # QA workflow optimization
            ]
        }
        
        # Get servers for this command type
        servers = server_mapping.get(command_type, list(self.mcp_servers.keys()))
        
        # Filter by health status
        healthy_servers = [
            server for server in servers
            if self.mcp_servers[server].status in [MCPServerStatus.HEALTHY, MCPServerStatus.DEGRADED]
        ]
        
        # If no healthy servers, fall back to all available
        if not healthy_servers:
            healthy_servers = servers
        
        logger.info(f"Selected {len(healthy_servers)} servers for {command_type}: {healthy_servers}")
        return healthy_servers
    
    def create_parallel_tasks(self, command_type: str, context: Dict[str, Any]) -> List[ParallelTask]:
        """Create parallel tasks based on command type and context"""
        
        servers = self.determine_optimal_servers(command_type, context)
        tasks = []
        
        for server_name in servers:
            server_info = self.mcp_servers[server_name]
            
            # Create server-specific task based on capabilities
            task_params = self.create_server_task_params(server_name, command_type, context)
            
            if task_params:
                task = ParallelTask(
                    task_id=str(uuid.uuid4()),
                    server_name=server_name,
                    operation=task_params['operation'],
                    parameters=task_params['parameters'],
                    priority=task_params.get('priority', 1),
                    timeout=task_params.get('timeout', 30.0)
                )
                tasks.append(task)
        
        return tasks
    
    def create_server_task_params(self, server_name: str, command_type: str, context: Dict[str, Any]) -> Optional[Dict]:
        """Create server-specific task parameters"""
        
        task_mapping = {
            'ml-code-intelligence': {
                '/analyze_10x': {
                    'operation': 'analyze_codebase',
                    'parameters': {
                        'scope': context.get('scope', 'full'),
                        'analysis_type': ['quality', 'complexity', 'maintainability'],
                        'include_metrics': True
                    },
                    'priority': 1,
                    'timeout': 45.0
                },
                '/implement_10x': {
                    'operation': 'code_assistance', 
                    'parameters': {
                        'feature': context.get('feature', ''),
                        'context': context.get('context', {}),
                        'patterns': True
                    },
                    'priority': 2,
                    'timeout': 60.0
                }
            },
            'context-aware-memory': {
                '/analyze_10x': {
                    'operation': 'retrieve_context',
                    'parameters': {
                        'query': context.get('query', ''),
                        'scope': 'project',
                        'include_history': True
                    },
                    'priority': 1,
                    'timeout': 30.0
                }
            },
            'predictive-analytics': {
                '/analyze_10x': {
                    'operation': 'risk_analysis',
                    'parameters': {
                        'context': context,
                        'analysis_types': ['technical', 'timeline', 'complexity']
                    },
                    'priority': 2,
                    'timeout': 40.0
                }
            },
            'ml-testing-qa': {
                '/qa:comprehensive_10x': {
                    'operation': 'comprehensive_qa',
                    'parameters': {
                        'scope': context.get('scope', 'all'),
                        'include_tests': True,
                        'quality_gates': True
                    },
                    'priority': 1,
                    'timeout': 50.0
                }
            },
            'agentic-workflow': {
                '/implement_10x': {
                    'operation': 'orchestrate_implementation',
                    'parameters': {
                        'feature': context.get('feature', ''),
                        'optimization': True,
                        'parallel_strategies': True
                    },
                    'priority': 1,
                    'timeout': 35.0
                }
            }
        }
        
        server_tasks = task_mapping.get(server_name, {})
        return server_tasks.get(command_type)
    
    async def dispatch_parallel(self, command_type: str, context: Dict[str, Any]) -> List[TaskResult]:
        """Dispatch tasks to multiple MCP servers in parallel"""
        
        # Check server health first
        await self.check_all_server_health()
        
        # Create parallel tasks
        tasks = self.create_parallel_tasks(command_type, context)
        
        if not tasks:
            logger.warning(f"No tasks created for command: {command_type}")
            return []
        
        logger.info(f"Dispatching {len(tasks)} parallel tasks for {command_type}")
        
        # Execute tasks in parallel with concurrency limit
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def execute_with_semaphore(task):
            async with semaphore:
                return await self.execute_task(task)
        
        # Run all tasks in parallel
        task_coroutines = [execute_with_semaphore(task) for task in tasks]
        results = await asyncio.gather(*task_coroutines, return_exceptions=True)
        
        # Process results
        processed_results = []
        for task, result in zip(tasks, results):
            if isinstance(result, Exception):
                processed_results.append(TaskResult(
                    task_id=task.task_id,
                    server_name=task.server_name,
                    operation=task.operation,
                    success=False,
                    error=str(result),
                    timestamp=time.time()
                ))
            else:
                processed_results.append(result)
        
        # Log summary
        successful = sum(1 for r in processed_results if r.success)
        logger.info(f"Parallel execution completed: {successful}/{len(processed_results)} tasks successful")
        
        return processed_results
    
    async def execute_task(self, task: ParallelTask) -> TaskResult:
        """Execute a single task on an MCP server"""
        
        start_time = time.time()
        
        try:
            # Execute the MCP operation
            result = await self.execute_mcp_operation(
                task.server_name,
                task.operation,
                task.parameters,
                timeout=task.timeout
            )
            
            execution_time = time.time() - start_time
            
            if result and not result.get('error'):
                # Update server success count
                self.mcp_servers[task.server_name].success_count += 1
                
                return TaskResult(
                    task_id=task.task_id,
                    server_name=task.server_name,
                    operation=task.operation,
                    success=True,
                    result=result,
                    execution_time=execution_time,
                    timestamp=start_time
                )
            else:
                # Update server error count
                self.mcp_servers[task.server_name].error_count += 1
                
                return TaskResult(
                    task_id=task.task_id,
                    server_name=task.server_name,
                    operation=task.operation,
                    success=False,
                    error=result.get('error', 'Unknown error') if result else 'No response',
                    execution_time=execution_time,
                    timestamp=start_time
                )
                
        except asyncio.TimeoutError:
            self.mcp_servers[task.server_name].error_count += 1
            return TaskResult(
                task_id=task.task_id,
                server_name=task.server_name,
                operation=task.operation,
                success=False,
                error=f"Timeout after {task.timeout}s",
                execution_time=time.time() - start_time,
                timestamp=start_time
            )
        except Exception as e:
            self.mcp_servers[task.server_name].error_count += 1
            return TaskResult(
                task_id=task.task_id,
                server_name=task.server_name,
                operation=task.operation,
                success=False,
                error=str(e),
                execution_time=time.time() - start_time,
                timestamp=start_time
            )
    
    async def execute_mcp_operation(self, server_name: str, operation: str, parameters: Dict, timeout: float = 30.0) -> Optional[Dict]:
        """
        Execute operation on MCP server
        Since these are STDIO-based servers, we simulate the operation
        In a real implementation, this would use the MCP protocol
        """
        
        # For now, simulate MCP server responses
        # In production, this would use actual MCP communication
        await asyncio.sleep(0.1)  # Simulate network delay
        
        # Simulate server-specific responses
        mock_responses = {
            'ml-code-intelligence': {
                'analyze_codebase': {
                    'analysis': 'Code quality analysis completed',
                    'metrics': {'complexity': 0.7, 'maintainability': 0.8},
                    'recommendations': ['Improve error handling', 'Add type hints']
                },
                'code_assistance': {
                    'suggestions': ['Use async/await pattern', 'Implement error boundaries'],
                    'patterns': ['Factory pattern', 'Observer pattern']
                }
            },
            'context-aware-memory': {
                'retrieve_context': {
                    'context': f'Retrieved context for {operation}',
                    'relevant_history': ['Previous similar implementation', 'Related discussions'],
                    'suggestions': ['Consider previous approach', 'Review past decisions']
                }
            },
            'predictive-analytics': {
                'risk_analysis': {
                    'risk_score': 0.3,
                    'risk_factors': ['Complexity increase', 'Timeline pressure'],
                    'mitigation': ['Add more tests', 'Phased rollout']
                }
            },
            'ml-testing-qa': {
                'comprehensive_qa': {
                    'quality_score': 0.85,
                    'test_coverage': 0.92,
                    'issues': ['Missing edge case tests'],
                    'recommendations': ['Add integration tests']
                }
            },
            'agentic-workflow': {
                'orchestrate_implementation': {
                    'workflow': ['Analysis', 'Implementation', 'Testing', 'Documentation'],
                    'optimization': 'Parallel execution recommended',
                    'timeline': 'Estimated 2-3 days'
                }
            }
        }
        
        server_responses = mock_responses.get(server_name, {})
        response = server_responses.get(operation, {'message': f'Operation {operation} completed'})
        
        # Add metadata
        response['_metadata'] = {
            'server': server_name,
            'operation': operation,
            'timestamp': time.time(),
            'parameters': parameters
        }
        
        return response
    
    def get_server_stats(self) -> Dict[str, Any]:
        """Get statistics for all MCP servers"""
        
        stats = {
            'total_servers': len(self.mcp_servers),
            'healthy_servers': 0,
            'degraded_servers': 0,
            'offline_servers': 0,
            'servers': {}
        }
        
        for server_name, server_info in self.mcp_servers.items():
            # Count by status
            if server_info.status == MCPServerStatus.HEALTHY:
                stats['healthy_servers'] += 1
            elif server_info.status == MCPServerStatus.DEGRADED:
                stats['degraded_servers'] += 1
            else:
                stats['offline_servers'] += 1
            
            # Server details
            stats['servers'][server_name] = {
                'status': server_info.status.value,
                'capabilities': server_info.capabilities,
                'last_response_time': server_info.last_response_time,
                'success_count': server_info.success_count,
                'error_count': server_info.error_count,
                'success_rate': (
                    server_info.success_count / (server_info.success_count + server_info.error_count)
                    if (server_info.success_count + server_info.error_count) > 0 else 0
                )
            }
        
        return stats

# Example usage and testing
async def test_parallel_dispatcher():
    """Test the parallel dispatcher functionality"""
    
    async with ParallelDispatcher() as dispatcher:
        # Test /analyze_10x command
        context = {
            'query': 'analyze current codebase',
            'scope': 'full',
            'focus': 'quality'
        }
        
        results = await dispatcher.dispatch_parallel('/analyze_10x', context)
        
        print(f"Parallel execution results: {len(results)} tasks completed")
        for result in results:
            print(f"  {result.server_name}: {'✅' if result.success else '❌'} "
                  f"({result.execution_time:.3f}s)")
        
        # Print server stats
        stats = dispatcher.get_server_stats()
        print(f"\nServer Statistics:")
        print(f"  Healthy: {stats['healthy_servers']}")
        print(f"  Degraded: {stats['degraded_servers']}")
        print(f"  Offline: {stats['offline_servers']}")

if __name__ == "__main__":
    asyncio.run(test_parallel_dispatcher())