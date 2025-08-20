#!/usr/bin/env python3
"""
Parallel MCP Coordination Manager
Manages task dependencies, resource allocation, and deadlock prevention
"""

import asyncio
import time
import logging
import psutil
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import uuid
import threading
from collections import defaultdict, deque

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ResourceType(Enum):
    CPU = "cpu"
    MEMORY = "memory"
    NETWORK = "network"
    MCP_SERVER = "mcp_server"

@dataclass
class ResourceRequirement:
    resource_type: ResourceType
    amount: float
    exclusive: bool = False
    timeout: float = 30.0

@dataclass
class CoordinationTask:
    task_id: str
    server_name: str
    operation: str
    parameters: Dict[str, Any]
    dependencies: Set[str] = field(default_factory=set)
    resource_requirements: List[ResourceRequirement] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    priority: int = 1
    timeout: float = 30.0
    retry_count: int = 0
    max_retries: int = 2
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@dataclass
class ResourceAllocation:
    resource_type: ResourceType
    allocated_amount: float
    task_id: str
    allocated_at: float
    exclusive: bool = False

class ResourceManager:
    """Manages system resources for optimal parallel execution"""
    
    def __init__(self):
        self.system_resources = {
            ResourceType.CPU: psutil.cpu_count(),
            ResourceType.MEMORY: psutil.virtual_memory().total // (1024 * 1024),  # MB
            ResourceType.NETWORK: 100.0,  # Arbitrary network bandwidth units
        }
        
        # MCP server specific resources (1 per server)
        self.mcp_server_resources = {
            'ml-code-intelligence': 1.0,
            'context-aware-memory': 1.0,
            'agentic-workflow': 1.0,
            'predictive-analytics': 1.0,
            'ml-testing-qa': 1.0
        }
        
        self.allocations: List[ResourceAllocation] = []
        self.allocation_lock = threading.RLock()
        
    def get_available_resources(self) -> Dict[ResourceType, float]:
        """Get currently available resources"""
        with self.allocation_lock:
            available = self.system_resources.copy()
            
            # Subtract allocated resources
            for allocation in self.allocations:
                if allocation.resource_type in available:
                    available[allocation.resource_type] -= allocation.allocated_amount
            
            # Ensure non-negative
            for resource_type in available:
                available[resource_type] = max(0, available[resource_type])
            
            return available
    
    def can_allocate(self, requirements: List[ResourceRequirement]) -> bool:
        """Check if resources can be allocated for given requirements"""
        with self.allocation_lock:
            available = self.get_available_resources()
            
            for req in requirements:
                if req.resource_type == ResourceType.MCP_SERVER:
                    # Check MCP server availability (exclusive by default)
                    server_name = req.amount  # Server name passed as amount for MCP servers
                    if any(alloc.resource_type == ResourceType.MCP_SERVER and 
                           alloc.allocated_amount == server_name for alloc in self.allocations):
                        return False
                else:
                    available_amount = available.get(req.resource_type, 0)
                    if available_amount < req.amount:
                        return False
                    
                    if req.exclusive:
                        # Check if any resources of this type are already allocated
                        if any(alloc.resource_type == req.resource_type for alloc in self.allocations):
                            return False
            
            return True
    
    def allocate_resources(self, task_id: str, requirements: List[ResourceRequirement]) -> bool:
        """Allocate resources for a task"""
        with self.allocation_lock:
            if not self.can_allocate(requirements):
                return False
            
            # Allocate resources
            for req in requirements:
                allocation = ResourceAllocation(
                    resource_type=req.resource_type,
                    allocated_amount=req.amount,
                    task_id=task_id,
                    allocated_at=time.time(),
                    exclusive=req.exclusive
                )
                self.allocations.append(allocation)
            
            return True
    
    def deallocate_resources(self, task_id: str):
        """Deallocate resources for a task"""
        with self.allocation_lock:
            self.allocations = [
                alloc for alloc in self.allocations 
                if alloc.task_id != task_id
            ]
    
    def get_resource_usage(self) -> Dict[str, Any]:
        """Get current resource usage statistics"""
        with self.allocation_lock:
            usage = {
                'total_resources': self.system_resources,
                'available_resources': self.get_available_resources(),
                'active_allocations': len(self.allocations),
                'allocated_by_type': defaultdict(float)
            }
            
            for allocation in self.allocations:
                usage['allocated_by_type'][allocation.resource_type.value] += allocation.allocated_amount
            
            return dict(usage)

class DependencyManager:
    """Manages task dependencies and prevents deadlocks"""
    
    def __init__(self):
        self.dependency_graph: Dict[str, Set[str]] = defaultdict(set)
        self.reverse_graph: Dict[str, Set[str]] = defaultdict(set)
        self.completed_tasks: Set[str] = set()
        
    def add_dependency(self, task_id: str, depends_on: str):
        """Add a dependency relationship"""
        self.dependency_graph[task_id].add(depends_on)
        self.reverse_graph[depends_on].add(task_id)
        
    def remove_dependency(self, task_id: str, depends_on: str):
        """Remove a dependency relationship"""
        self.dependency_graph[task_id].discard(depends_on)
        self.reverse_graph[depends_on].discard(task_id)
    
    def mark_completed(self, task_id: str) -> List[str]:
        """Mark task as completed and return newly ready tasks"""
        self.completed_tasks.add(task_id)
        
        # Find tasks that are now ready
        ready_tasks = []
        for dependent_task in self.reverse_graph[task_id]:
            if self.is_ready(dependent_task):
                ready_tasks.append(dependent_task)
        
        return ready_tasks
    
    def is_ready(self, task_id: str) -> bool:
        """Check if a task is ready to run (all dependencies completed)"""
        dependencies = self.dependency_graph.get(task_id, set())
        return dependencies.issubset(self.completed_tasks)
    
    def detect_cycles(self) -> List[List[str]]:
        """Detect cycles in dependency graph (potential deadlocks)"""
        visited = set()
        rec_stack = set()
        cycles = []
        
        def dfs(node, path):
            if node in rec_stack:
                # Found cycle
                cycle_start = path.index(node)
                cycles.append(path[cycle_start:] + [node])
                return
            
            if node in visited:
                return
                
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in self.dependency_graph[node]:
                dfs(neighbor, path + [node])
            
            rec_stack.remove(node)
        
        for task_id in self.dependency_graph:
            if task_id not in visited:
                dfs(task_id, [])
        
        return cycles
    
    def get_execution_order(self, task_ids: List[str]) -> List[List[str]]:
        """Get topological execution order (tasks that can run in parallel)"""
        # Create subgraph for given tasks
        subgraph = {task_id: self.dependency_graph[task_id].intersection(task_ids) 
                   for task_id in task_ids}
        
        execution_order = []
        remaining_tasks = set(task_ids)
        
        while remaining_tasks:
            # Find tasks with no dependencies in remaining set
            ready_tasks = [
                task_id for task_id in remaining_tasks
                if not subgraph[task_id]
            ]
            
            if not ready_tasks:
                # Deadlock detected
                logger.error(f"Deadlock detected in tasks: {remaining_tasks}")
                break
            
            execution_order.append(ready_tasks)
            remaining_tasks -= set(ready_tasks)
            
            # Remove completed tasks from dependencies
            for task_id in remaining_tasks:
                subgraph[task_id] -= set(ready_tasks)
        
        return execution_order

class CoordinationManager:
    """Coordinates parallel MCP task execution with resource management and dependency resolution"""
    
    def __init__(self, max_concurrent_tasks: int = 5):
        self.tasks: Dict[str, CoordinationTask] = {}
        self.task_queue = deque()
        self.running_tasks: Dict[str, asyncio.Task] = {}
        
        self.resource_manager = ResourceManager()
        self.dependency_manager = DependencyManager()
        
        self.max_concurrent_tasks = max_concurrent_tasks
        self.coordination_lock = asyncio.Lock()
        self.task_completion_event = asyncio.Event()
        
        self.stats = {
            'total_tasks': 0,
            'completed_tasks': 0,
            'failed_tasks': 0,
            'cancelled_tasks': 0,
            'avg_execution_time': 0.0,
            'resource_wait_time': 0.0
        }
        
    def add_task(self, task: CoordinationTask):
        """Add a task to the coordination system"""
        self.tasks[task.task_id] = task
        
        # Add dependencies to dependency manager
        for dep_id in task.dependencies:
            self.dependency_manager.add_dependency(task.task_id, dep_id)
        
        # Add to queue if ready
        if self.dependency_manager.is_ready(task.task_id):
            task.status = TaskStatus.READY
            self.task_queue.append(task.task_id)
        
        self.stats['total_tasks'] += 1
        logger.info(f"Added task {task.task_id} for server {task.server_name}")
    
    def estimate_resource_requirements(self, task: CoordinationTask) -> List[ResourceRequirement]:
        """Estimate resource requirements for a task"""
        if task.resource_requirements:
            return task.resource_requirements
        
        # Default resource requirements based on server and operation
        requirements = [
            ResourceRequirement(ResourceType.MCP_SERVER, task.server_name, exclusive=True),
            ResourceRequirement(ResourceType.CPU, 1.0),  # 1 CPU core
            ResourceRequirement(ResourceType.MEMORY, 512.0),  # 512 MB
            ResourceRequirement(ResourceType.NETWORK, 10.0)   # 10 network units
        ]
        
        # Adjust based on operation complexity
        operation_multipliers = {
            'analyze_codebase': {'cpu': 1.5, 'memory': 2.0},
            'comprehensive_qa': {'cpu': 1.3, 'memory': 1.5},
            'orchestrate_implementation': {'cpu': 1.2, 'memory': 1.0},
            'risk_analysis': {'cpu': 1.4, 'memory': 1.8},
            'retrieve_context': {'cpu': 0.8, 'memory': 1.2}
        }
        
        multipliers = operation_multipliers.get(task.operation, {})
        
        for req in requirements:
            if req.resource_type == ResourceType.CPU and 'cpu' in multipliers:
                req.amount *= multipliers['cpu']
            elif req.resource_type == ResourceType.MEMORY and 'memory' in multipliers:
                req.amount *= multipliers['memory']
        
        return requirements
    
    async def coordinate_execution(self, tasks: List[CoordinationTask]) -> List[CoordinationTask]:
        """Coordinate execution of multiple tasks"""
        logger.info(f"Coordinating execution of {len(tasks)} tasks")
        
        # Add all tasks
        for task in tasks:
            self.add_task(task)
        
        # Check for dependency cycles
        cycles = self.dependency_manager.detect_cycles()
        if cycles:
            logger.error(f"Dependency cycles detected: {cycles}")
            # Cancel tasks in cycles
            for cycle in cycles:
                for task_id in cycle:
                    if task_id in self.tasks:
                        self.tasks[task_id].status = TaskStatus.CANCELLED
                        self.stats['cancelled_tasks'] += 1
        
        # Start execution loop
        await self.execution_loop()
        
        # Return completed tasks
        return list(self.tasks.values())
    
    async def execution_loop(self):
        """Main execution loop for coordinating tasks"""
        while self.task_queue or self.running_tasks:
            async with self.coordination_lock:
                # Start new tasks if possible
                while (len(self.running_tasks) < self.max_concurrent_tasks and 
                       self.task_queue):
                    
                    task_id = self.task_queue.popleft()
                    task = self.tasks[task_id]
                    
                    if task.status != TaskStatus.READY:
                        continue
                    
                    # Check resource availability
                    requirements = self.estimate_resource_requirements(task)
                    if not self.resource_manager.can_allocate(requirements):
                        # Put task back in queue
                        self.task_queue.append(task_id)
                        logger.debug(f"Task {task_id} waiting for resources")
                        break
                    
                    # Allocate resources and start task
                    if self.resource_manager.allocate_resources(task_id, requirements):
                        await self.start_task(task)
                    else:
                        # Put task back in queue
                        self.task_queue.append(task_id)
                        break
            
            # Wait for at least one task to complete
            if self.running_tasks:
                done, pending = await asyncio.wait(
                    list(self.running_tasks.values()),
                    return_when=asyncio.FIRST_COMPLETED,
                    timeout=1.0
                )
                
                # Process completed tasks
                for completed_task in done:
                    await self.handle_task_completion(completed_task)
            else:
                # No running tasks, wait a bit
                await asyncio.sleep(0.1)
    
    async def start_task(self, task: CoordinationTask):
        """Start execution of a task"""
        task.status = TaskStatus.RUNNING
        task.started_at = time.time()
        
        # Create and start async task
        async_task = asyncio.create_task(self.execute_task(task))
        self.running_tasks[task.task_id] = async_task
        
        logger.info(f"Started task {task.task_id} on server {task.server_name}")
    
    async def execute_task(self, task: CoordinationTask) -> CoordinationTask:
        """Execute a single task (placeholder for actual execution)"""
        try:
            # Simulate task execution
            await asyncio.sleep(0.5 + (task.priority * 0.1))
            
            # Simulate success/failure based on server reliability
            server_reliability = {
                'ml-code-intelligence': 0.95,
                'context-aware-memory': 0.98,
                'agentic-workflow': 0.93,
                'predictive-analytics': 0.90,
                'ml-testing-qa': 0.96
            }
            
            import random
            reliability = server_reliability.get(task.server_name, 0.95)
            success = random.random() < reliability
            
            if success:
                task.status = TaskStatus.COMPLETED
                task.result = {
                    'server': task.server_name,
                    'operation': task.operation,
                    'success': True,
                    'data': f'Result from {task.server_name} for {task.operation}'
                }
                self.stats['completed_tasks'] += 1
            else:
                task.status = TaskStatus.FAILED
                task.error = f"Simulated failure on {task.server_name}"
                self.stats['failed_tasks'] += 1
            
            task.completed_at = time.time()
            
        except asyncio.CancelledError:
            task.status = TaskStatus.CANCELLED
            task.error = "Task was cancelled"
            self.stats['cancelled_tasks'] += 1
            raise
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            self.stats['failed_tasks'] += 1
        
        return task
    
    async def handle_task_completion(self, async_task: asyncio.Task):
        """Handle completion of a task"""
        # Find the task ID for this async task
        task_id = None
        for tid, at in self.running_tasks.items():
            if at == async_task:
                task_id = tid
                break
        
        if task_id is None:
            logger.error("Completed task not found in running tasks")
            return
        
        task = self.tasks[task_id]
        
        # Remove from running tasks
        del self.running_tasks[task_id]
        
        # Deallocate resources
        self.resource_manager.deallocate_resources(task_id)
        
        # Update statistics
        if task.completed_at and task.started_at:
            execution_time = task.completed_at - task.started_at
            current_avg = self.stats['avg_execution_time']
            total_completed = self.stats['completed_tasks'] + self.stats['failed_tasks']
            if total_completed > 0:
                self.stats['avg_execution_time'] = (
                    (current_avg * (total_completed - 1) + execution_time) / total_completed
                )
        
        # Mark as completed in dependency manager and get newly ready tasks
        if task.status == TaskStatus.COMPLETED:
            ready_tasks = self.dependency_manager.mark_completed(task_id)
            
            # Add newly ready tasks to queue
            for ready_task_id in ready_tasks:
                if ready_task_id in self.tasks:
                    self.tasks[ready_task_id].status = TaskStatus.READY
                    self.task_queue.append(ready_task_id)
        
        logger.info(f"Task {task_id} completed with status: {task.status.value}")
        
        # Set completion event
        self.task_completion_event.set()
        self.task_completion_event.clear()
    
    def get_coordination_stats(self) -> Dict[str, Any]:
        """Get coordination statistics"""
        resource_usage = self.resource_manager.get_resource_usage()
        
        return {
            'task_stats': self.stats.copy(),
            'resource_usage': resource_usage,
            'active_tasks': len(self.running_tasks),
            'queued_tasks': len(self.task_queue),
            'total_managed_tasks': len(self.tasks),
            'task_statuses': {
                status.value: sum(1 for t in self.tasks.values() if t.status == status)
                for status in TaskStatus
            }
        }
    
    def optimize_task_priority(self, tasks: List[CoordinationTask]):
        """Optimize task priorities based on dependencies and resource requirements"""
        # Calculate dependency depth for each task
        depth_cache = {}
        
        def calculate_depth(task_id: str) -> int:
            if task_id in depth_cache:
                return depth_cache[task_id]
            
            dependencies = self.dependency_manager.dependency_graph.get(task_id, set())
            if not dependencies:
                depth_cache[task_id] = 0
                return 0
            
            max_dep_depth = max(calculate_depth(dep_id) for dep_id in dependencies)
            depth_cache[task_id] = max_dep_depth + 1
            return depth_cache[task_id]
        
        # Update priorities based on depth (deeper tasks get higher priority)
        for task in tasks:
            depth = calculate_depth(task.task_id)
            resource_reqs = self.estimate_resource_requirements(task)
            resource_complexity = sum(req.amount for req in resource_reqs if req.resource_type != ResourceType.MCP_SERVER)
            
            # Higher priority for deeper dependencies and lower resource requirements
            task.priority = max(1, depth * 2 - int(resource_complexity / 100))

# Example usage and testing
async def test_coordination_manager():
    """Test the coordination manager functionality"""
    
    coordinator = CoordinationManager(max_concurrent_tasks=3)
    
    # Create test tasks with dependencies
    tasks = []
    
    # Task 1: Retrieve context (no dependencies)
    task1 = CoordinationTask(
        task_id="task_1",
        server_name="context-aware-memory",
        operation="retrieve_context",
        parameters={"query": "test query"}
    )
    tasks.append(task1)
    
    # Task 2: Analyze code (depends on task1)
    task2 = CoordinationTask(
        task_id="task_2", 
        server_name="ml-code-intelligence",
        operation="analyze_codebase",
        parameters={"scope": "full"},
        dependencies={"task_1"}
    )
    tasks.append(task2)
    
    # Task 3: Risk analysis (depends on task1)
    task3 = CoordinationTask(
        task_id="task_3",
        server_name="predictive-analytics", 
        operation="risk_analysis",
        parameters={"context": {}},
        dependencies={"task_1"}
    )
    tasks.append(task3)
    
    # Task 4: QA analysis (depends on task2 and task3)
    task4 = CoordinationTask(
        task_id="task_4",
        server_name="ml-testing-qa",
        operation="comprehensive_qa", 
        parameters={"scope": "all"},
        dependencies={"task_2", "task_3"}
    )
    tasks.append(task4)
    
    # Optimize priorities
    coordinator.optimize_task_priority(tasks)
    
    print(f"Coordinating {len(tasks)} tasks...")
    
    # Execute tasks
    start_time = time.time()
    completed_tasks = await coordinator.coordinate_execution(tasks)
    execution_time = time.time() - start_time
    
    print(f"\nExecution completed in {execution_time:.2f}s")
    
    # Print results
    for task in completed_tasks:
        print(f"Task {task.task_id} ({task.server_name}): {task.status.value}")
        if task.error:
            print(f"  Error: {task.error}")
    
    # Print statistics
    stats = coordinator.get_coordination_stats()
    print(f"\nCoordination Statistics:")
    print(f"  Completed: {stats['task_stats']['completed_tasks']}")
    print(f"  Failed: {stats['task_stats']['failed_tasks']}")
    print(f"  Cancelled: {stats['task_stats']['cancelled_tasks']}")
    print(f"  Average execution time: {stats['task_stats']['avg_execution_time']:.2f}s")

if __name__ == "__main__":
    asyncio.run(test_coordination_manager())