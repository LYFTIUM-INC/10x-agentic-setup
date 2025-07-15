"""
Base Agent Implementation for Agentic Workflow MCP
Provides common functionality for all specialized agents
"""

import asyncio
import time
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class AgentTask:
    """Represents a task assigned to an agent"""
    task_id: str
    task_type: str
    description: str
    parameters: Dict[str, Any]
    priority: int  # 1=highest, 10=lowest
    deadline: Optional[datetime]
    context: Dict[str, Any]
    dependencies: List[str]  # List of task IDs this task depends on

@dataclass
class AgentResult:
    """Represents the result of an agent's task execution"""
    task_id: str
    agent_id: str
    success: bool
    result_data: Dict[str, Any]
    execution_time: float
    confidence: float
    errors: List[str]
    metadata: Dict[str, Any]
    timestamp: datetime

class BaseAgent(ABC):
    """
    Abstract base class for all specialized agents in the Agentic Workflow system
    Provides common functionality and interface for agent implementations
    """
    
    def __init__(self, agent_id: str, agent_type: str, capabilities: List[str]):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.capabilities = capabilities
        self.status = "initializing"
        self.current_task = None
        self.task_history = []
        self.performance_metrics = {}
        self.communication_channels = []
        self.tools = {}
        self.context_memory = {}
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self._initialize_metrics()
    
    def _initialize_metrics(self) -> None:
        """Initialize performance tracking metrics"""
        self.performance_metrics = {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "average_execution_time": 0.0,
            "average_confidence": 0.0,
            "success_rate": 0.0,
            "total_execution_time": 0.0,
            "error_count": 0,
            "last_success": None,
            "last_failure": None
        }
    
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """
        Initialize the agent with specific configuration
        
        Args:
            config: Agent configuration parameters
            
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            self.status = "initializing"
            
            # Initialize tools and resources
            await self._initialize_tools(config.get("tools", {}))
            
            # Setup communication channels
            self.communication_channels = config.get("communication_channels", [])
            
            # Initialize agent-specific components
            await self._agent_specific_initialization(config)
            
            self.status = "ready"
            logger.info(f"Agent {self.agent_id} initialized successfully")
            return True
            
        except Exception as e:
            self.status = "error"
            logger.error(f"Failed to initialize agent {self.agent_id}: {str(e)}")
            return False
    
    @abstractmethod
    async def _agent_specific_initialization(self, config: Dict[str, Any]) -> None:
        """Agent-specific initialization logic (implemented by subclasses)"""
        pass
    
    async def _initialize_tools(self, tools_config: Dict[str, Any]) -> None:
        """Initialize tools available to the agent"""
        self.tools = tools_config.copy()
        
        # Add common tools available to all agents
        self.tools.update({
            "logger": logger,
            "timer": time,
            "id_generator": uuid,
            "datetime": datetime
        })
    
    async def execute_task(self, task: AgentTask) -> AgentResult:
        """
        Execute a task using this agent
        
        Args:
            task: The task to execute
            
        Returns:
            AgentResult containing execution results
        """
        if self.status != "ready":
            return AgentResult(
                task_id=task.task_id,
                agent_id=self.agent_id,
                success=False,
                result_data={},
                execution_time=0.0,
                confidence=0.0,
                errors=[f"Agent not ready (status: {self.status})"],
                metadata={},
                timestamp=datetime.now()
            )
        
        self.status = "working"
        self.current_task = task
        self.last_activity = datetime.now()
        
        start_time = time.time()
        
        try:
            logger.info(f"Agent {self.agent_id} starting task {task.task_id}: {task.description}")
            
            # Validate task compatibility
            if not await self._can_handle_task(task):
                raise ValueError(f"Agent {self.agent_type} cannot handle task type {task.task_type}")
            
            # Execute the task using agent-specific logic
            result_data = await self._execute_agent_task(task)
            
            execution_time = time.time() - start_time
            
            # Calculate confidence based on result quality
            confidence = await self._calculate_confidence(task, result_data, execution_time)
            
            # Create successful result
            result = AgentResult(
                task_id=task.task_id,
                agent_id=self.agent_id,
                success=True,
                result_data=result_data,
                execution_time=execution_time,
                confidence=confidence,
                errors=[],
                metadata={
                    "agent_type": self.agent_type,
                    "capabilities_used": await self._get_capabilities_used(task),
                    "tools_used": await self._get_tools_used(task),
                    "context_size": len(str(task.context))
                },
                timestamp=datetime.now()
            )
            
            # Update performance metrics
            await self._update_performance_metrics(result)
            
            self.status = "ready"
            self.current_task = None
            self.task_history.append(result)
            
            logger.info(f"Agent {self.agent_id} completed task {task.task_id} successfully "
                       f"(confidence: {confidence:.2f}, time: {execution_time:.2f}s)")
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = str(e)
            
            logger.error(f"Agent {self.agent_id} failed task {task.task_id}: {error_msg}")
            
            # Create failure result
            result = AgentResult(
                task_id=task.task_id,
                agent_id=self.agent_id,
                success=False,
                result_data={},
                execution_time=execution_time,
                confidence=0.0,
                errors=[error_msg],
                metadata={
                    "agent_type": self.agent_type,
                    "failure_reason": error_msg,
                    "error_category": type(e).__name__
                },
                timestamp=datetime.now()
            )
            
            # Update performance metrics
            await self._update_performance_metrics(result)
            
            self.status = "ready"
            self.current_task = None
            self.task_history.append(result)
            
            return result
    
    @abstractmethod
    async def _can_handle_task(self, task: AgentTask) -> bool:
        """Check if this agent can handle the given task type"""
        pass
    
    @abstractmethod
    async def _execute_agent_task(self, task: AgentTask) -> Dict[str, Any]:
        """Execute the agent-specific task logic"""
        pass
    
    async def _calculate_confidence(self, task: AgentTask, result_data: Dict[str, Any], 
                                  execution_time: float) -> float:
        """Calculate confidence in the task execution result"""
        
        confidence_factors = []
        
        # Base confidence from result quality
        if result_data:
            # More comprehensive results = higher confidence
            result_size = len(str(result_data))
            size_confidence = min(1.0, result_size / 1000.0)  # Normalize to 1000 chars
            confidence_factors.append(size_confidence)
            
            # Check for error indicators in results
            error_indicators = ["error", "failed", "exception", "problem"]
            has_errors = any(indicator in str(result_data).lower() for indicator in error_indicators)
            error_confidence = 0.2 if has_errors else 0.9
            confidence_factors.append(error_confidence)
        
        # Execution time confidence (faster = higher confidence for simple tasks)
        expected_time = task.parameters.get("expected_duration", 30.0)
        if execution_time > 0:
            time_confidence = min(1.0, expected_time / execution_time)
            confidence_factors.append(time_confidence)
        
        # Historical performance confidence
        if self.performance_metrics["tasks_completed"] > 0:
            historical_confidence = self.performance_metrics["success_rate"]
            confidence_factors.append(historical_confidence)
        
        # Agent capability match confidence
        capability_confidence = await self._calculate_capability_confidence(task)
        confidence_factors.append(capability_confidence)
        
        # Calculate weighted average (recent factors weighted more heavily)
        if confidence_factors:
            # Weight recent factors more heavily
            weights = [1.0, 1.2, 0.8, 0.6, 1.1][:len(confidence_factors)]
            weighted_confidence = sum(c * w for c, w in zip(confidence_factors, weights)) / sum(weights)
            return max(0.0, min(1.0, weighted_confidence))
        
        return 0.5  # Default moderate confidence
    
    async def _calculate_capability_confidence(self, task: AgentTask) -> float:
        """Calculate confidence based on how well agent capabilities match task requirements"""
        
        required_capabilities = task.parameters.get("required_capabilities", [])
        if not required_capabilities:
            return 0.8  # Good confidence if no specific requirements
        
        matching_capabilities = [cap for cap in required_capabilities if cap in self.capabilities]
        
        if not required_capabilities:
            return 0.8
        
        match_ratio = len(matching_capabilities) / len(required_capabilities)
        return match_ratio
    
    async def _get_capabilities_used(self, task: AgentTask) -> List[str]:
        """Get list of capabilities that were used for this task"""
        # Default implementation - can be overridden by subclasses
        task_type = task.task_type
        
        capability_mapping = {
            "research": ["web_search", "documentation_analysis"],
            "code": ["code_generation", "code_analysis"],
            "test": ["test_generation", "test_execution"],
            "analyze": ["data_analysis", "pattern_recognition"]
        }
        
        used_capabilities = []
        for task_keyword, capabilities in capability_mapping.items():
            if task_keyword in task_type.lower():
                used_capabilities.extend([cap for cap in capabilities if cap in self.capabilities])
        
        return used_capabilities or ["general_processing"]
    
    async def _get_tools_used(self, task: AgentTask) -> List[str]:
        """Get list of tools that were used for this task"""
        # Default implementation - can be overridden by subclasses
        return list(self.tools.keys())
    
    async def _update_performance_metrics(self, result: AgentResult) -> None:
        """Update agent performance metrics based on task result"""
        
        if result.success:
            self.performance_metrics["tasks_completed"] += 1
            self.performance_metrics["last_success"] = result.timestamp.isoformat()
        else:
            self.performance_metrics["tasks_failed"] += 1
            self.performance_metrics["error_count"] += 1
            self.performance_metrics["last_failure"] = result.timestamp.isoformat()
        
        # Update averages
        total_tasks = self.performance_metrics["tasks_completed"] + self.performance_metrics["tasks_failed"]
        
        if total_tasks > 0:
            self.performance_metrics["success_rate"] = self.performance_metrics["tasks_completed"] / total_tasks
        
        # Update execution time averages
        self.performance_metrics["total_execution_time"] += result.execution_time
        
        if self.performance_metrics["tasks_completed"] > 0:
            self.performance_metrics["average_execution_time"] = (
                self.performance_metrics["total_execution_time"] / 
                (self.performance_metrics["tasks_completed"] + self.performance_metrics["tasks_failed"])
            )
        
        # Update confidence average
        if result.success:
            completed_tasks = self.performance_metrics["tasks_completed"]
            current_avg = self.performance_metrics["average_confidence"]
            
            # Calculate running average
            new_avg = ((current_avg * (completed_tasks - 1)) + result.confidence) / completed_tasks
            self.performance_metrics["average_confidence"] = new_avg
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current agent status and metrics"""
        
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "status": self.status,
            "capabilities": self.capabilities,
            "current_task": self.current_task.task_id if self.current_task else None,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "performance_metrics": self.performance_metrics,
            "task_history_count": len(self.task_history),
            "communication_channels": self.communication_channels
        }
    
    async def update_context(self, key: str, value: Any) -> None:
        """Update agent's context memory"""
        self.context_memory[key] = {
            "value": value,
            "timestamp": datetime.now().isoformat()
        }
    
    async def get_context(self, key: str) -> Optional[Any]:
        """Get value from agent's context memory"""
        context_entry = self.context_memory.get(key)
        return context_entry["value"] if context_entry else None
    
    async def clear_context(self) -> None:
        """Clear agent's context memory"""
        self.context_memory.clear()
    
    async def can_collaborate_with(self, other_agent_type: str, task_type: str) -> bool:
        """Check if this agent can collaborate with another agent type on a specific task"""
        
        # Define collaboration compatibility matrix
        collaboration_matrix = {
            "research_agent": ["code_agent", "test_agent", "orchestrator_agent"],
            "code_agent": ["research_agent", "test_agent", "orchestrator_agent"],
            "test_agent": ["code_agent", "research_agent", "orchestrator_agent"],
            "orchestrator_agent": ["research_agent", "code_agent", "test_agent", "analysis_agent"],
            "analysis_agent": ["research_agent", "orchestrator_agent"]
        }
        
        compatible_agents = collaboration_matrix.get(self.agent_type, [])
        return other_agent_type in compatible_agents
    
    async def prepare_for_collaboration(self, collaborator_id: str, task: AgentTask) -> Dict[str, Any]:
        """Prepare for collaboration with another agent"""
        
        collaboration_data = {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "relevant_capabilities": await self._get_capabilities_used(task),
            "context_to_share": await self._get_shareable_context(task),
            "collaboration_preferences": {
                "communication_frequency": "on_progress",
                "data_sharing_level": "relevant_only",
                "coordination_style": "cooperative"
            }
        }
        
        return collaboration_data
    
    async def _get_shareable_context(self, task: AgentTask) -> Dict[str, Any]:
        """Get context information that can be shared with other agents"""
        
        # Filter context to only include relevant and shareable information
        shareable_context = {}
        
        # Share recent successful task results that might be relevant
        recent_successes = [
            result for result in self.task_history[-5:] 
            if result.success and result.task_id != task.task_id
        ]
        
        if recent_successes:
            shareable_context["recent_successes"] = [
                {
                    "task_type": self._extract_task_type_from_history(result),
                    "confidence": result.confidence,
                    "execution_time": result.execution_time,
                    "key_insights": self._extract_key_insights(result)
                }
                for result in recent_successes
            ]
        
        # Share relevant performance metrics
        shareable_context["performance_summary"] = {
            "success_rate": self.performance_metrics["success_rate"],
            "average_confidence": self.performance_metrics["average_confidence"],
            "specialization_strength": max(self.capabilities) if self.capabilities else "general"
        }
        
        return shareable_context
    
    def _extract_task_type_from_history(self, result: AgentResult) -> str:
        """Extract task type from historical result"""
        # This would typically be stored with the task, but for simplicity extract from metadata
        return result.metadata.get("task_type", "unknown")
    
    def _extract_key_insights(self, result: AgentResult) -> List[str]:
        """Extract key insights from task result"""
        insights = []
        
        # High confidence results provide reliable insights
        if result.confidence > 0.8:
            insights.append("High-confidence execution pattern")
        
        # Fast execution indicates efficient approach
        if result.execution_time < 10.0:
            insights.append("Efficient execution approach")
        
        # Large result datasets indicate comprehensive processing
        if len(str(result.result_data)) > 1000:
            insights.append("Comprehensive data processing")
        
        return insights
    
    async def terminate(self) -> bool:
        """Terminate the agent and cleanup resources"""
        
        try:
            self.status = "terminating"
            
            # Cancel current task if any
            if self.current_task:
                logger.warning(f"Terminating agent {self.agent_id} with active task {self.current_task.task_id}")
            
            # Cleanup agent-specific resources
            await self._cleanup_agent_resources()
            
            # Clear context and history
            self.context_memory.clear()
            self.task_history.clear()
            
            self.status = "terminated"
            logger.info(f"Agent {self.agent_id} terminated successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to terminate agent {self.agent_id}: {str(e)}")
            self.status = "error"
            return False
    
    async def _cleanup_agent_resources(self) -> None:
        """Cleanup agent-specific resources (implemented by subclasses)"""
        # Default implementation - subclasses can override
        pass
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.agent_id}, type={self.agent_type}, status={self.status})"