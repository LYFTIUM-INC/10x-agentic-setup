#!/usr/bin/env python3
"""
Thread-Safe Agent Coordination
Prevents race conditions in multi-agent operations
"""

import threading
import time
import uuid
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

@dataclass
class AgentTask:
    """Represents a task for an agent"""
    task_id: str
    agent_id: str
    task_type: str
    parameters: Dict[str, Any]
    priority: int = 0
    created_at: float = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()

@dataclass
class AgentResult:
    """Represents result from an agent task"""
    task_id: str
    agent_id: str
    status: str  # 'success', 'error', 'timeout'
    result: Any
    execution_time: float
    completed_at: float = None
    
    def __post_init__(self):
        if self.completed_at is None:
            self.completed_at = time.time()

class ThreadSafeCoordinator:
    """Thread-safe coordinator for multi-agent operations"""
    
    def __init__(self, max_concurrent_agents: int = 10):
        # Thread synchronization
        self._lock = threading.RLock()
        self._agent_locks = {}
        self._resource_locks = {}
        
        # Agent management
        self._active_agents = {}
        self._agent_states = {}
        self._task_queue = []
        self._results = {}
        
        # Configuration
        self.max_concurrent_agents = max_concurrent_agents
        self.default_timeout = 300  # 5 minutes
        
        # Thread pool for agent execution
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent_agents)
        
        # Logging
        self.logger = logging.getLogger(__name__)
    
    def get_agent_lock(self, agent_id: str) -> threading.Lock:
        """Get or create a lock for a specific agent"""
        with self._lock:
            if agent_id not in self._agent_locks:
                self._agent_locks[agent_id] = threading.Lock()
            return self._agent_locks[agent_id]
    
    def get_resource_lock(self, resource_id: str) -> threading.Lock:
        """Get or create a lock for a specific resource"""
        with self._lock:
            if resource_id not in self._resource_locks:
                self._resource_locks[resource_id] = threading.Lock()
            return self._resource_locks[resource_id]
    
    def submit_task(self, agent_id: str, task_type: str, parameters: Dict[str, Any], 
                   priority: int = 0) -> str:
        """Submit a task for an agent to execute"""
        task_id = str(uuid.uuid4())
        task = AgentTask(
            task_id=task_id,
            agent_id=agent_id,
            task_type=task_type,
            parameters=parameters,
            priority=priority
        )
        
        with self._lock:
            # Add to queue, sorted by priority (higher priority first)
            self._task_queue.append(task)
            self._task_queue.sort(key=lambda x: (-x.priority, x.created_at))
        
        self.logger.info(f"Task {task_id} submitted for agent {agent_id}")
        return task_id
    
    def execute_task_safely(self, task: AgentTask, agent_function: Callable) -> AgentResult:
        """Execute a task with proper synchronization"""
        start_time = time.time()
        
        # Acquire agent lock
        agent_lock = self.get_agent_lock(task.agent_id)
        
        try:
            with agent_lock:
                # Update agent state
                with self._lock:
                    self._agent_states[task.agent_id] = {
                        'status': 'executing',
                        'task_id': task.task_id,
                        'started_at': start_time
                    }
                
                # Execute the task
                result = agent_function(task.parameters)
                
                # Calculate execution time
                execution_time = time.time() - start_time
                
                # Create result
                agent_result = AgentResult(
                    task_id=task.task_id,
                    agent_id=task.agent_id,
                    status='success',
                    result=result,
                    execution_time=execution_time
                )
                
        except Exception as e:
            execution_time = time.time() - start_time
            agent_result = AgentResult(
                task_id=task.task_id,
                agent_id=task.agent_id,
                status='error',
                result=str(e),
                execution_time=execution_time
            )
            self.logger.error(f"Task {task.task_id} failed: {e}")
            
        finally:
            # Update agent state
            with self._lock:
                self._agent_states[task.agent_id] = {
                    'status': 'idle',
                    'last_task': task.task_id,
                    'completed_at': time.time()
                }
                
                # Store result
                self._results[task.task_id] = agent_result
        
        return agent_result
    
    def coordinate_parallel_execution(self, tasks: List[Dict[str, Any]], 
                                    agent_functions: Dict[str, Callable],
                                    timeout: Optional[float] = None) -> Dict[str, AgentResult]:
        """Coordinate parallel execution of multiple agent tasks"""
        if timeout is None:
            timeout = self.default_timeout
        
        # Submit all tasks
        submitted_tasks = []
        futures = {}
        
        for task_config in tasks:
            agent_id = task_config['agent_id']
            task_type = task_config['task_type']
            parameters = task_config.get('parameters', {})
            priority = task_config.get('priority', 0)
            
            # Create task
            task = AgentTask(
                task_id=str(uuid.uuid4()),
                agent_id=agent_id,
                task_type=task_type,
                parameters=parameters,
                priority=priority
            )
            
            # Get agent function
            agent_function = agent_functions.get(agent_id)
            if not agent_function:
                self.logger.error(f"No function found for agent {agent_id}")
                continue
            
            # Submit for execution
            future = self.executor.submit(self.execute_task_safely, task, agent_function)
            futures[future] = task
            submitted_tasks.append(task)
        
        # Wait for completion
        results = {}
        
        try:
            for future in as_completed(futures, timeout=timeout):
                task = futures[future]
                try:
                    result = future.result()
                    results[task.task_id] = result
                    self.logger.info(f"Task {task.task_id} completed successfully")
                except Exception as e:
                    # Create error result
                    error_result = AgentResult(
                        task_id=task.task_id,
                        agent_id=task.agent_id,
                        status='error',
                        result=str(e),
                        execution_time=0
                    )
                    results[task.task_id] = error_result
                    self.logger.error(f"Task {task.task_id} failed with exception: {e}")
                    
        except TimeoutError:
            self.logger.error(f"Parallel execution timed out after {timeout} seconds")
        
        return results
    
    def acquire_shared_resource(self, resource_id: str, timeout: float = 30) -> bool:
        """Acquire a shared resource with timeout"""
        resource_lock = self.get_resource_lock(resource_id)
        
        try:
            acquired = resource_lock.acquire(timeout=timeout)
            if acquired:
                self.logger.debug(f"Acquired resource {resource_id}")
            else:
                self.logger.warning(f"Failed to acquire resource {resource_id} within {timeout}s")
            return acquired
        except Exception as e:
            self.logger.error(f"Error acquiring resource {resource_id}: {e}")
            return False
    
    def release_shared_resource(self, resource_id: str):
        """Release a shared resource"""
        if resource_id in self._resource_locks:
            try:
                self._resource_locks[resource_id].release()
                self.logger.debug(f"Released resource {resource_id}")
            except Exception as e:
                self.logger.error(f"Error releasing resource {resource_id}: {e}")
    
    def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of an agent"""
        with self._lock:
            return self._agent_states.get(agent_id)
    
    def get_task_result(self, task_id: str) -> Optional[AgentResult]:
        """Get result of a completed task"""
        with self._lock:
            return self._results.get(task_id)
    
    def cleanup(self):
        """Clean up resources"""
        self.executor.shutdown(wait=True)
        
        with self._lock:
            self._active_agents.clear()
            self._agent_states.clear()
            self._task_queue.clear()
            self._results.clear()

# Context manager for resource locking
class ResourceLockContext:
    """Context manager for acquiring and releasing shared resources"""
    
    def __init__(self, coordinator: ThreadSafeCoordinator, resource_id: str, timeout: float = 30):
        self.coordinator = coordinator
        self.resource_id = resource_id
        self.timeout = timeout
        self.acquired = False
    
    def __enter__(self):
        self.acquired = self.coordinator.acquire_shared_resource(self.resource_id, self.timeout)
        if not self.acquired:
            raise RuntimeError(f"Failed to acquire resource {self.resource_id}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.acquired:
            self.coordinator.release_shared_resource(self.resource_id)

# Usage example
def safe_multi_agent_execution():
    """Example of safe multi-agent execution"""
    coordinator = ThreadSafeCoordinator(max_concurrent_agents=5)
    
    # Define agent functions
    def project_architect_agent(params):
        # Simulate project architect work
        time.sleep(2)
        return {"analysis": "architecture complete", "recommendations": ["optimize db", "add caching"]}
    
    def performance_engineer_agent(params):
        # Simulate performance engineer work
        time.sleep(1.5)
        return {"metrics": {"response_time": "0.02s", "throughput": "1000rps"}}
    
    def security_auditor_agent(params):
        # Simulate security auditor work
        time.sleep(2.5)
        return {"vulnerabilities": 0, "security_score": 95}
    
    agent_functions = {
        'project-architect': project_architect_agent,
        'performance-engineer': performance_engineer_agent,
        'security-auditor': security_auditor_agent
    }
    
    # Define tasks
    tasks = [
        {
            'agent_id': 'project-architect',
            'task_type': 'analyze_architecture',
            'parameters': {'project_path': '/path/to/project'},
            'priority': 1
        },
        {
            'agent_id': 'performance-engineer',
            'task_type': 'analyze_performance',
            'parameters': {'metrics': ['response_time', 'throughput']},
            'priority': 2
        },
        {
            'agent_id': 'security-auditor',
            'task_type': 'security_audit',
            'parameters': {'scan_depth': 'comprehensive'},
            'priority': 3
        }
    ]
    
    # Execute tasks in parallel
    results = coordinator.coordinate_parallel_execution(tasks, agent_functions, timeout=60)
    
    # Process results
    for task_id, result in results.items():
        print(f"Task {task_id}: {result.status} - {result.execution_time:.2f}s")
    
    # Cleanup
    coordinator.cleanup()
    
    return results