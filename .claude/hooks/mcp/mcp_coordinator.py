#!/usr/bin/env python3
"""
Claude Code Hooks - MCP Server Coordination Hook
Coordinates with our 7 MCP servers for enhanced parallel execution
"""

import os
import json
import time
import asyncio
import aiohttp
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('mcp_coordinator')

@dataclass
class MCPServerInfo:
    name: str
    url: str
    port: int
    status: str
    capabilities: List[str]
    last_health_check: Optional[datetime]
    response_time: Optional[float]
    error_count: int

class MCPCoordinator:
    """Coordinate with MCP servers for enhanced parallel execution"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.session_id = os.environ.get('CLAUDE_SESSION_ID', 'unknown')
        self.coordination_db = self.project_root / '.claude' / 'mcp_coordination.db'
        
        # Define our 7 MCP servers
        self.mcp_servers = {
            'context-aware-memory': MCPServerInfo(
                name='context-aware-memory',
                url='http://localhost:8001',
                port=8001,
                status='unknown',
                capabilities=['memory_storage', 'semantic_retrieval', 'predictive_loading'],
                last_health_check=None,
                response_time=None,
                error_count=0
            ),
            'ml-code-intelligence': MCPServerInfo(
                name='ml-code-intelligence',
                url='http://localhost:8002',
                port=8002,
                status='unknown',
                capabilities=['code_analysis', 'quality_assessment', 'semantic_search'],
                last_health_check=None,
                response_time=None,
                error_count=0
            ),
            'agentic-workflow': MCPServerInfo(
                name='agentic-workflow',
                url='http://localhost:8003',
                port=8003,
                status='unknown',
                capabilities=['agent_spawning', 'workflow_optimization', 'task_delegation'],
                last_health_check=None,
                response_time=None,
                error_count=0
            ),
            'predictive-analytics': MCPServerInfo(
                name='predictive-analytics',
                url='http://localhost:8004',
                port=8004,
                status='unknown',
                capabilities=['velocity_forecasting', 'risk_assessment', 'performance_prediction'],
                last_health_check=None,
                response_time=None,
                error_count=0
            ),
            'ml-testing-qa': MCPServerInfo(
                name='ml-testing-qa',
                url='http://localhost:8005',
                port=8005,
                status='unknown',
                capabilities=['test_generation', 'bug_prediction', 'edge_case_discovery'],
                last_health_check=None,
                response_time=None,
                error_count=0
            ),
            '10x-knowledge-graph': MCPServerInfo(
                name='10x-knowledge-graph',
                url='http://localhost:8006',
                port=8006,
                status='unknown',
                capabilities=['concept_extraction', 'relationship_mapping', 'knowledge_queries'],
                last_health_check=None,
                response_time=None,
                error_count=0
            ),
            '10x-command-analytics': MCPServerInfo(
                name='10x-command-analytics',
                url='http://localhost:8007',
                port=8007,
                status='unknown',
                capabilities=['usage_analysis', 'success_prediction', 'workflow_recommendations'],
                last_health_check=None,
                response_time=None,
                error_count=0
            )
        }
        
        self.init_database()
    
    def init_database(self):
        """Initialize coordination database"""
        import sqlite3
        
        self.coordination_db.parent.mkdir(exist_ok=True)
        
        with sqlite3.connect(self.coordination_db) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS mcp_coordination_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    timestamp TEXT,
                    hook_event TEXT,
                    tool_name TEXT,
                    coordination_type TEXT,
                    servers_involved TEXT,
                    execution_time REAL,
                    success BOOLEAN,
                    error_message TEXT,
                    performance_metrics TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS mcp_server_health (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    server_name TEXT,
                    timestamp TEXT,
                    status TEXT,
                    response_time REAL,
                    capabilities TEXT,
                    error_count INTEGER,
                    last_error TEXT
                )
            """)
    
    async def coordinate_mcp_operation(self) -> Dict[str, Any]:
        """Coordinate MCP operation based on current hook context"""
        
        start_time = time.time()
        
        coordination_result = {
            'session_id': self.session_id,
            'timestamp': datetime.now().isoformat(),
            'hook_event': os.environ.get('CLAUDE_HOOK_EVENT_NAME', ''),
            'tool_name': os.environ.get('CLAUDE_TOOL_NAME', ''),
            'coordination_type': 'unknown',
            'servers_involved': [],
            'execution_time': 0,
            'success': False,
            'performance_metrics': {},
            'coordination_actions': []
        }
        
        try:
            # Determine coordination type based on tool name
            coordination_type = self._determine_coordination_type(coordination_result['tool_name'])
            coordination_result['coordination_type'] = coordination_type
            
            # Check server health
            health_results = await self._check_all_servers_health()
            
            # Determine required servers
            required_servers = self._get_required_servers(coordination_type, coordination_result['tool_name'])
            coordination_result['servers_involved'] = required_servers
            
            # Execute coordination based on hook event
            hook_event = coordination_result['hook_event']
            
            if hook_event == 'PreToolUse':
                await self._pre_tool_coordination(coordination_result, required_servers)
            elif hook_event == 'PostToolUse':
                await self._post_tool_coordination(coordination_result, required_servers)
            elif hook_event == 'UserPromptSubmit':
                await self._prompt_submit_coordination(coordination_result)
            elif hook_event == 'SubagentStop':
                await self._subagent_coordination(coordination_result, required_servers)
            
            coordination_result['success'] = True
            coordination_result['execution_time'] = time.time() - start_time
            
            # Log coordination event
            self._log_coordination_event(coordination_result)
            
            return coordination_result
            
        except Exception as e:
            logger.error(f"MCP coordination failed: {e}")
            coordination_result['success'] = False
            coordination_result['error_message'] = str(e)
            coordination_result['execution_time'] = time.time() - start_time
            return coordination_result
    
    def _determine_coordination_type(self, tool_name: str) -> str:
        """Determine coordination type based on tool name"""
        
        if not tool_name:
            return 'general'
        
        coordination_mapping = {
            'analyze': 'analysis',
            'implement': 'implementation', 
            'qa': 'quality_assurance',
            'memory': 'memory_operation',
            'code': 'code_operation',
            'test': 'testing_operation',
            'predict': 'prediction_operation',
            'workflow': 'workflow_operation'
        }
        
        tool_lower = tool_name.lower()
        
        for key, coord_type in coordination_mapping.items():
            if key in tool_lower:
                return coord_type
        
        # Check if it's an MCP tool
        if tool_name.startswith('mcp__'):
            return 'mcp_direct'
        
        return 'general'
    
    def _get_required_servers(self, coordination_type: str, tool_name: str) -> List[str]:
        """Get required MCP servers for coordination type"""
        
        server_requirements = {
            'analysis': ['ml-code-intelligence', 'context-aware-memory', '10x-knowledge-graph'],
            'implementation': ['ml-code-intelligence', 'context-aware-memory', 'predictive-analytics', 'agentic-workflow'],
            'quality_assurance': ['ml-testing-qa', 'ml-code-intelligence', 'predictive-analytics'],
            'memory_operation': ['context-aware-memory'],
            'code_operation': ['ml-code-intelligence', 'context-aware-memory'],
            'testing_operation': ['ml-testing-qa', 'predictive-analytics'],
            'prediction_operation': ['predictive-analytics', 'context-aware-memory'],
            'workflow_operation': ['agentic-workflow', '10x-command-analytics'],
            'mcp_direct': self._extract_mcp_server_from_tool(tool_name),
            'general': ['context-aware-memory', '10x-command-analytics']
        }
        
        return server_requirements.get(coordination_type, ['context-aware-memory'])
    
    def _extract_mcp_server_from_tool(self, tool_name: str) -> List[str]:
        """Extract MCP server name from tool name"""
        
        if not tool_name.startswith('mcp__'):
            return []
        
        # Tool format: mcp__server_name__tool_name
        parts = tool_name.split('__')
        if len(parts) >= 2:
            server_name = parts[1].replace('_', '-')
            return [server_name] if server_name in self.mcp_servers else []
        
        return []
    
    async def _check_all_servers_health(self) -> Dict[str, Dict[str, Any]]:
        """Check health of all MCP servers in parallel"""
        
        health_results = {}
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
            tasks = []
            
            for server_name, server_info in self.mcp_servers.items():
                task = self._check_server_health(session, server_name, server_info)
                tasks.append(task)
            
            # Execute health checks in parallel
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(results):
                server_name = list(self.mcp_servers.keys())[i]
                
                if isinstance(result, Exception):
                    health_results[server_name] = {
                        'status': 'error',
                        'error': str(result),
                        'response_time': None
                    }
                else:
                    health_results[server_name] = result
        
        # Update server info
        for server_name, health in health_results.items():
            if server_name in self.mcp_servers:
                self.mcp_servers[server_name].status = health['status']
                self.mcp_servers[server_name].response_time = health.get('response_time')
                self.mcp_servers[server_name].last_health_check = datetime.now()
                
                if health['status'] == 'error':
                    self.mcp_servers[server_name].error_count += 1
        
        return health_results
    
    async def _check_server_health(self, session: aiohttp.ClientSession, 
                                 server_name: str, server_info: MCPServerInfo) -> Dict[str, Any]:
        """Check health of individual MCP server"""
        
        start_time = time.time()
        
        try:
            # Try health endpoint first
            health_url = f"{server_info.url}/health"
            
            async with session.get(health_url) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    health_data = await response.json()
                    return {
                        'status': 'healthy',
                        'response_time': response_time,
                        'health_data': health_data
                    }
                else:
                    return {
                        'status': 'unhealthy',
                        'response_time': response_time,
                        'error': f"HTTP {response.status}"
                    }
                    
        except aiohttp.ClientConnectorError:
            # Server not running
            return {
                'status': 'offline',
                'response_time': None,
                'error': 'Connection refused'
            }
        except asyncio.TimeoutError:
            return {
                'status': 'timeout',
                'response_time': None,
                'error': 'Health check timeout'
            }
        except Exception as e:
            return {
                'status': 'error',
                'response_time': None,
                'error': str(e)
            }
    
    async def _pre_tool_coordination(self, result: Dict[str, Any], required_servers: List[str]):
        """Coordinate before tool execution"""
        
        coordination_actions = []
        
        # Prepare servers for operation
        for server_name in required_servers:
            if server_name in self.mcp_servers:
                server_info = self.mcp_servers[server_name]
                
                if server_info.status == 'healthy':
                    # Send preparation signal
                    prep_action = await self._send_preparation_signal(server_info, result)
                    coordination_actions.append(prep_action)
                else:
                    coordination_actions.append({
                        'server': server_name,
                        'action': 'skip',
                        'reason': f"Server status: {server_info.status}"
                    })
        
        # Set up parallel execution context
        if len(required_servers) > 1:
            context_action = await self._setup_parallel_context(required_servers, result)
            coordination_actions.append(context_action)
        
        result['coordination_actions'] = coordination_actions
    
    async def _post_tool_coordination(self, result: Dict[str, Any], required_servers: List[str]):
        """Coordinate after tool execution"""
        
        coordination_actions = []
        
        # Collect results from servers
        for server_name in required_servers:
            if server_name in self.mcp_servers:
                server_info = self.mcp_servers[server_name]
                
                if server_info.status == 'healthy':
                    # Collect execution data
                    collect_action = await self._collect_execution_data(server_info, result)
                    coordination_actions.append(collect_action)
        
        # Aggregate parallel results
        if len(required_servers) > 1:
            aggregate_action = await self._aggregate_parallel_results(required_servers, result)
            coordination_actions.append(aggregate_action)
        
        # Store learning data
        learning_action = await self._store_learning_data(result)
        coordination_actions.append(learning_action)
        
        result['coordination_actions'] = coordination_actions
    
    async def _prompt_submit_coordination(self, result: Dict[str, Any]):
        """Coordinate on prompt submission"""
        
        coordination_actions = []
        
        # Analyze prompt for context
        context_action = await self._analyze_prompt_context(result)
        coordination_actions.append(context_action)
        
        # Prepare predictive loading
        prediction_action = await self._setup_predictive_loading(result)
        coordination_actions.append(prediction_action)
        
        result['coordination_actions'] = coordination_actions
    
    async def _subagent_coordination(self, result: Dict[str, Any], required_servers: List[str]):
        """Coordinate subagent operations"""
        
        coordination_actions = []
        
        # Synchronize subagent results
        for server_name in required_servers:
            if server_name in self.mcp_servers:
                sync_action = await self._synchronize_subagent_results(server_name, result)
                coordination_actions.append(sync_action)
        
        result['coordination_actions'] = coordination_actions
    
    async def _send_preparation_signal(self, server_info: MCPServerInfo, 
                                     result: Dict[str, Any]) -> Dict[str, Any]:
        """Send preparation signal to MCP server"""
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                prep_data = {
                    'session_id': result['session_id'],
                    'hook_event': result['hook_event'],
                    'tool_name': result['tool_name'],
                    'preparation_mode': 'parallel_coordination'
                }
                
                prep_url = f"{server_info.url}/api/prepare"
                
                async with session.post(prep_url, json=prep_data) as response:
                    if response.status == 200:
                        prep_result = await response.json()
                        return {
                            'server': server_info.name,
                            'action': 'prepare',
                            'success': True,
                            'result': prep_result
                        }
                    else:
                        return {
                            'server': server_info.name,
                            'action': 'prepare',
                            'success': False,
                            'error': f"HTTP {response.status}"
                        }
                        
        except Exception as e:
            return {
                'server': server_info.name,
                'action': 'prepare',
                'success': False,
                'error': str(e)
            }
    
    async def _setup_parallel_context(self, servers: List[str], 
                                    result: Dict[str, Any]) -> Dict[str, Any]:
        """Set up parallel execution context"""
        
        try:
            context_data = {
                'session_id': result['session_id'],
                'parallel_servers': servers,
                'coordination_mode': 'synchronized',
                'execution_strategy': 'parallel_with_aggregation'
            }
            
            # Send context to agentic-workflow server for coordination
            if 'agentic-workflow' in self.mcp_servers:
                workflow_server = self.mcp_servers['agentic-workflow']
                
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                    context_url = f"{workflow_server.url}/api/setup-parallel-context"
                    
                    async with session.post(context_url, json=context_data) as response:
                        if response.status == 200:
                            context_result = await response.json()
                            return {
                                'action': 'setup_parallel_context',
                                'success': True,
                                'servers': servers,
                                'coordination_id': context_result.get('coordination_id'),
                                'result': context_result
                            }
            
            return {
                'action': 'setup_parallel_context',
                'success': False,
                'servers': servers,
                'error': 'Agentic workflow server not available'
            }
            
        except Exception as e:
            return {
                'action': 'setup_parallel_context',
                'success': False,
                'servers': servers,
                'error': str(e)
            }
    
    async def _collect_execution_data(self, server_info: MCPServerInfo, 
                                    result: Dict[str, Any]) -> Dict[str, Any]:
        """Collect execution data from MCP server"""
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                collect_url = f"{server_info.url}/api/collect-execution-data"
                
                collect_data = {
                    'session_id': result['session_id'],
                    'tool_name': result['tool_name']
                }
                
                async with session.post(collect_url, json=collect_data) as response:
                    if response.status == 200:
                        execution_data = await response.json()
                        return {
                            'server': server_info.name,
                            'action': 'collect_data',
                            'success': True,
                            'execution_data': execution_data
                        }
                    else:
                        return {
                            'server': server_info.name,
                            'action': 'collect_data',
                            'success': False,
                            'error': f"HTTP {response.status}"
                        }
                        
        except Exception as e:
            return {
                'server': server_info.name,
                'action': 'collect_data',
                'success': False,
                'error': str(e)
            }
    
    async def _aggregate_parallel_results(self, servers: List[str], 
                                        result: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate results from parallel server execution"""
        
        try:
            if 'agentic-workflow' in self.mcp_servers:
                workflow_server = self.mcp_servers['agentic-workflow']
                
                aggregate_data = {
                    'session_id': result['session_id'],
                    'servers': servers,
                    'aggregation_mode': 'intelligent_merge'
                }
                
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                    aggregate_url = f"{workflow_server.url}/api/aggregate-results"
                    
                    async with session.post(aggregate_url, json=aggregate_data) as response:
                        if response.status == 200:
                            aggregate_result = await response.json()
                            return {
                                'action': 'aggregate_results',
                                'success': True,
                                'servers': servers,
                                'result': aggregate_result
                            }
            
            return {
                'action': 'aggregate_results',
                'success': False,
                'servers': servers,
                'error': 'Aggregation service not available'
            }
            
        except Exception as e:
            return {
                'action': 'aggregate_results',
                'success': False,
                'servers': servers,
                'error': str(e)
            }
    
    async def _analyze_prompt_context(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze prompt context for coordination"""
        
        try:
            if 'context-aware-memory' in self.mcp_servers:
                memory_server = self.mcp_servers['context-aware-memory']
                
                context_data = {
                    'session_id': result['session_id'],
                    'prompt_analysis_mode': 'coordination_context'
                }
                
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                    analyze_url = f"{memory_server.url}/api/analyze-prompt-context"
                    
                    async with session.post(analyze_url, json=context_data) as response:
                        if response.status == 200:
                            analysis_result = await response.json()
                            return {
                                'action': 'analyze_prompt_context',
                                'success': True,
                                'result': analysis_result
                            }
            
            return {
                'action': 'analyze_prompt_context',
                'success': False,
                'error': 'Memory server not available'
            }
            
        except Exception as e:
            return {
                'action': 'analyze_prompt_context',
                'success': False,
                'error': str(e)
            }
    
    async def _setup_predictive_loading(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Set up predictive loading based on prompt analysis"""
        
        try:
            if 'predictive-analytics' in self.mcp_servers:
                analytics_server = self.mcp_servers['predictive-analytics']
                
                prediction_data = {
                    'session_id': result['session_id'],
                    'prediction_type': 'workflow_anticipation'
                }
                
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                    predict_url = f"{analytics_server.url}/api/setup-predictive-loading"
                    
                    async with session.post(predict_url, json=prediction_data) as response:
                        if response.status == 200:
                            prediction_result = await response.json()
                            return {
                                'action': 'setup_predictive_loading',
                                'success': True,
                                'result': prediction_result
                            }
            
            return {
                'action': 'setup_predictive_loading',
                'success': False,
                'error': 'Analytics server not available'
            }
            
        except Exception as e:
            return {
                'action': 'setup_predictive_loading',
                'success': False,
                'error': str(e)
            }
    
    async def _synchronize_subagent_results(self, server_name: str, 
                                          result: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronize subagent results"""
        
        try:
            if server_name in self.mcp_servers:
                server_info = self.mcp_servers[server_name]
                
                sync_data = {
                    'session_id': result['session_id'],
                    'synchronization_mode': 'subagent_completion'
                }
                
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                    sync_url = f"{server_info.url}/api/synchronize-subagent"
                    
                    async with session.post(sync_url, json=sync_data) as response:
                        if response.status == 200:
                            sync_result = await response.json()
                            return {
                                'server': server_name,
                                'action': 'synchronize_subagent',
                                'success': True,
                                'result': sync_result
                            }
            
            return {
                'server': server_name,
                'action': 'synchronize_subagent',
                'success': False,
                'error': 'Server not available'
            }
            
        except Exception as e:
            return {
                'server': server_name,
                'action': 'synchronize_subagent',
                'success': False,
                'error': str(e)
            }
    
    async def _store_learning_data(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Store learning data from coordination"""
        
        try:
            if 'context-aware-memory' in self.mcp_servers:
                memory_server = self.mcp_servers['context-aware-memory']
                
                learning_data = {
                    'session_id': result['session_id'],
                    'coordination_type': result['coordination_type'],
                    'servers_involved': result['servers_involved'],
                    'execution_time': result.get('execution_time', 0),
                    'success': result['success'],
                    'learning_mode': 'coordination_pattern'
                }
                
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                    store_url = f"{memory_server.url}/api/store-learning-data"
                    
                    async with session.post(store_url, json=learning_data) as response:
                        if response.status == 200:
                            store_result = await response.json()
                            return {
                                'action': 'store_learning_data',
                                'success': True,
                                'result': store_result
                            }
            
            return {
                'action': 'store_learning_data',
                'success': False,
                'error': 'Memory server not available'
            }
            
        except Exception as e:
            return {
                'action': 'store_learning_data',
                'success': False,
                'error': str(e)
            }
    
    def _log_coordination_event(self, result: Dict[str, Any]):
        """Log coordination event to database"""
        
        import sqlite3
        
        try:
            with sqlite3.connect(self.coordination_db) as conn:
                conn.execute("""
                    INSERT INTO mcp_coordination_events 
                    (session_id, timestamp, hook_event, tool_name, coordination_type,
                     servers_involved, execution_time, success, error_message, performance_metrics)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    result['session_id'],
                    result['timestamp'],
                    result['hook_event'],
                    result['tool_name'],
                    result['coordination_type'],
                    json.dumps(result['servers_involved']),
                    result['execution_time'],
                    result['success'],
                    result.get('error_message'),
                    json.dumps(result.get('performance_metrics', {}))
                ))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to log coordination event: {e}")

def main():
    """Main MCP coordination entry point"""
    
    async def async_main():
        coordinator = MCPCoordinator()
        
        # Perform coordination
        result = await coordinator.coordinate_mcp_operation()
        
        # Print coordination result
        print(f"MCP Coordination: {result['coordination_type']}")
        print(f"Servers involved: {len(result['servers_involved'])}")
        print(f"Success: {result['success']}")
        print(f"Execution time: {result['execution_time']:.3f}s")
        
        if result['coordination_actions']:
            print(f"Actions executed: {len(result['coordination_actions'])}")
            for action in result['coordination_actions']:
                action_name = action.get('action', 'unknown')
                action_success = action.get('success', False)
                print(f"  - {action_name}: {'✓' if action_success else '✗'}")
        
        return 0 if result['success'] else 1
    
    # Run async coordination
    import asyncio
    exit_code = asyncio.run(async_main())
    exit(exit_code)

if __name__ == "__main__":
    main()