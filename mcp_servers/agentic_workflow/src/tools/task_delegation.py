"""
Task Delegation Implementation for Agentic Workflow MCP
Handles intelligent task distribution and delegation across agents
"""

import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class TaskComplexity(Enum):
    """Task complexity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXTREME = "extreme"

@dataclass
class TaskDelegationRequest:
    """Request for task delegation"""
    task_id: str
    description: str
    requirements: Dict[str, Any]
    complexity: TaskComplexity
    priority: int
    deadline: Optional[datetime]
    preferred_agents: List[str]
    required_capabilities: List[str]

@dataclass
class DelegationResult:
    """Result of task delegation"""
    task_id: str
    assigned_agent: str
    agent_type: str
    delegation_confidence: float
    estimated_duration: float
    resource_allocation: Dict[str, Any]
    delegation_reason: str

class TaskDelegationEngine:
    """
    Intelligent task delegation engine that analyzes tasks and assigns them
    to the most suitable agents based on capabilities, availability, and performance
    """
    
    def __init__(self):
        self.agent_capabilities = {}
        self.agent_performance_history = {}
        self.delegation_rules = {}
        self.load_balancer = TaskLoadBalancer()
        self._initialize_delegation_rules()
    
    def _initialize_delegation_rules(self):
        """Initialize delegation rules and heuristics"""
        
        self.delegation_rules = {
            "capability_matching": {
                "weight": 0.4,
                "description": "Match task requirements with agent capabilities"
            },
            "performance_history": {
                "weight": 0.3,
                "description": "Consider agent's historical performance"
            },
            "current_load": {
                "weight": 0.2,
                "description": "Consider agent's current workload"
            },
            "specialization_bonus": {
                "weight": 0.1,
                "description": "Bonus for highly specialized agents"
            }
        }
    
    async def delegate_task(self, request: TaskDelegationRequest) -> DelegationResult:
        """
        Delegate a task to the most suitable agent
        
        Args:
            request: Task delegation request
            
        Returns:
            DelegationResult containing assignment details
        """
        
        logger.info(f"Delegating task {request.task_id}: {request.description}")
        
        # Analyze task requirements
        task_analysis = await self._analyze_task_requirements(request)
        
        # Find suitable agents
        suitable_agents = await self._find_suitable_agents(request, task_analysis)
        
        # Score and rank agents
        agent_scores = await self._score_agents(suitable_agents, request, task_analysis)
        
        # Select best agent
        best_agent = await self._select_best_agent(agent_scores, request)
        
        # Create delegation result
        delegation_result = DelegationResult(
            task_id=request.task_id,
            assigned_agent=best_agent["agent_id"],
            agent_type=best_agent["agent_type"],
            delegation_confidence=best_agent["score"],
            estimated_duration=best_agent["estimated_duration"],
            resource_allocation=best_agent["resource_allocation"],
            delegation_reason=best_agent["reason"]
        )
        
        # Update load balancer
        await self.load_balancer.assign_task(best_agent["agent_id"], request)
        
        logger.info(f"Task {request.task_id} delegated to {best_agent['agent_id']} (confidence: {best_agent['score']:.2f})")
        
        return delegation_result
    
    async def _analyze_task_requirements(self, request: TaskDelegationRequest) -> Dict[str, Any]:
        """Analyze task requirements and characteristics"""
        
        analysis = {
            "complexity_score": await self._calculate_complexity_score(request),
            "required_capabilities": request.required_capabilities,
            "estimated_effort": await self._estimate_task_effort(request),
            "parallelizable": await self._check_parallelizable(request),
            "domain": await self._identify_task_domain(request),
            "urgency": await self._calculate_urgency(request)
        }
        
        return analysis
    
    async def _calculate_complexity_score(self, request: TaskDelegationRequest) -> float:
        """Calculate numeric complexity score"""
        
        complexity_scores = {
            TaskComplexity.LOW: 0.25,
            TaskComplexity.MEDIUM: 0.5,
            TaskComplexity.HIGH: 0.75,
            TaskComplexity.EXTREME: 1.0
        }
        
        base_score = complexity_scores[request.complexity]
        
        # Adjust based on requirements
        if len(request.required_capabilities) > 3:
            base_score += 0.1
        
        if request.deadline and (request.deadline - datetime.now()).days < 1:
            base_score += 0.1
        
        return min(1.0, base_score)
    
    async def _estimate_task_effort(self, request: TaskDelegationRequest) -> float:
        """Estimate task effort in hours"""
        
        base_effort = {
            TaskComplexity.LOW: 1.0,
            TaskComplexity.MEDIUM: 4.0,
            TaskComplexity.HIGH: 8.0,
            TaskComplexity.EXTREME: 16.0
        }
        
        effort = base_effort[request.complexity]
        
        # Adjust based on requirements
        effort *= len(request.required_capabilities) * 0.2 + 0.8
        
        return effort
    
    async def _check_parallelizable(self, request: TaskDelegationRequest) -> bool:
        """Check if task can be parallelized"""
        
        # Simple heuristics for parallelizability
        description_lower = request.description.lower()
        
        parallelizable_keywords = ["analyze", "process", "test", "validate", "research"]
        sequential_keywords = ["design", "plan", "coordinate", "integrate"]
        
        parallel_score = sum(1 for keyword in parallelizable_keywords if keyword in description_lower)
        sequential_score = sum(1 for keyword in sequential_keywords if keyword in description_lower)
        
        return parallel_score > sequential_score
    
    async def _identify_task_domain(self, request: TaskDelegationRequest) -> str:
        """Identify the domain of the task"""
        
        description_lower = request.description.lower()
        
        if any(keyword in description_lower for keyword in ["code", "program", "implement", "develop"]):
            return "development"
        elif any(keyword in description_lower for keyword in ["test", "qa", "validate", "verify"]):
            return "testing"
        elif any(keyword in description_lower for keyword in ["research", "analyze", "investigate"]):
            return "research"
        elif any(keyword in description_lower for keyword in ["coordinate", "manage", "orchestrate"]):
            return "coordination"
        else:
            return "general"
    
    async def _calculate_urgency(self, request: TaskDelegationRequest) -> float:
        """Calculate task urgency score"""
        
        urgency = 0.5  # Base urgency
        
        # Priority-based urgency
        if request.priority <= 2:
            urgency += 0.3
        elif request.priority <= 4:
            urgency += 0.1
        
        # Deadline-based urgency
        if request.deadline:
            time_to_deadline = (request.deadline - datetime.now()).total_seconds()
            if time_to_deadline < 3600:  # Less than 1 hour
                urgency += 0.2
            elif time_to_deadline < 86400:  # Less than 1 day
                urgency += 0.1
        
        return min(1.0, urgency)
    
    async def _find_suitable_agents(self, request: TaskDelegationRequest, task_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find agents suitable for the task"""
        
        suitable_agents = []
        
        # Mock agent registry - in real implementation, this would query actual agent registry
        mock_agents = [
            {
                "agent_id": "research_001",
                "agent_type": "research_agent",
                "capabilities": ["web_search", "documentation_analysis", "competitive_intelligence"],
                "availability": 0.8,
                "performance_score": 0.9,
                "specialization": "research"
            },
            {
                "agent_id": "code_001",
                "agent_type": "code_agent",
                "capabilities": ["code_generation", "code_analysis", "refactoring"],
                "availability": 0.6,
                "performance_score": 0.85,
                "specialization": "development"
            },
            {
                "agent_id": "test_001",
                "agent_type": "test_agent",
                "capabilities": ["test_generation", "test_execution", "qa_analysis"],
                "availability": 0.9,
                "performance_score": 0.88,
                "specialization": "testing"
            },
            {
                "agent_id": "orchestrator_001",
                "agent_type": "orchestrator_agent",
                "capabilities": ["workflow_orchestration", "agent_coordination", "resource_management"],
                "availability": 0.7,
                "performance_score": 0.82,
                "specialization": "coordination"
            }
        ]
        
        # Filter agents based on capabilities
        required_capabilities = set(request.required_capabilities)
        
        for agent in mock_agents:
            agent_capabilities = set(agent["capabilities"])
            
            # Check if agent has required capabilities
            if required_capabilities.issubset(agent_capabilities) or not required_capabilities:
                # Check domain match
                if task_analysis["domain"] == "general" or agent["specialization"] == task_analysis["domain"]:
                    suitable_agents.append(agent)
        
        return suitable_agents
    
    async def _score_agents(self, suitable_agents: List[Dict[str, Any]], request: TaskDelegationRequest, task_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score and rank suitable agents"""
        
        scored_agents = []
        
        for agent in suitable_agents:
            score = await self._calculate_agent_score(agent, request, task_analysis)
            
            agent_with_score = agent.copy()
            agent_with_score["score"] = score
            agent_with_score["estimated_duration"] = await self._estimate_agent_duration(agent, request)
            agent_with_score["resource_allocation"] = await self._calculate_resource_allocation(agent, request)
            agent_with_score["reason"] = await self._generate_delegation_reason(agent, request, score)
            
            scored_agents.append(agent_with_score)
        
        # Sort by score (descending)
        scored_agents.sort(key=lambda x: x["score"], reverse=True)
        
        return scored_agents
    
    async def _calculate_agent_score(self, agent: Dict[str, Any], request: TaskDelegationRequest, task_analysis: Dict[str, Any]) -> float:
        """Calculate score for an agent"""
        
        score = 0.0
        
        # Capability matching score
        required_caps = set(request.required_capabilities)
        agent_caps = set(agent["capabilities"])
        
        if required_caps:
            capability_match = len(required_caps.intersection(agent_caps)) / len(required_caps)
        else:
            capability_match = 1.0
        
        score += capability_match * self.delegation_rules["capability_matching"]["weight"]
        
        # Performance history score
        performance_score = agent.get("performance_score", 0.5)
        score += performance_score * self.delegation_rules["performance_history"]["weight"]
        
        # Current load score (inverse of load - less load = higher score)
        availability = agent.get("availability", 0.5)
        score += availability * self.delegation_rules["current_load"]["weight"]
        
        # Specialization bonus
        if task_analysis["domain"] == agent.get("specialization", "general"):
            score += self.delegation_rules["specialization_bonus"]["weight"]
        
        return score
    
    async def _estimate_agent_duration(self, agent: Dict[str, Any], request: TaskDelegationRequest) -> float:
        """Estimate how long the agent will take to complete the task"""
        
        base_duration = await self._estimate_task_effort(request)
        
        # Adjust based on agent performance and specialization
        performance_multiplier = 2.0 - agent.get("performance_score", 0.5)
        
        # Specialization reduces duration
        if request.description.lower() in agent.get("specialization", ""):
            performance_multiplier *= 0.8
        
        return base_duration * performance_multiplier
    
    async def _calculate_resource_allocation(self, agent: Dict[str, Any], request: TaskDelegationRequest) -> Dict[str, Any]:
        """Calculate resource allocation for the agent"""
        
        complexity_multiplier = {
            TaskComplexity.LOW: 0.5,
            TaskComplexity.MEDIUM: 1.0,
            TaskComplexity.HIGH: 1.5,
            TaskComplexity.EXTREME: 2.0
        }
        
        multiplier = complexity_multiplier[request.complexity]
        
        return {
            "cpu_cores": int(2 * multiplier),
            "memory_mb": int(1024 * multiplier),
            "storage_gb": int(10 * multiplier),
            "network_bandwidth": int(100 * multiplier)
        }
    
    async def _generate_delegation_reason(self, agent: Dict[str, Any], request: TaskDelegationRequest, score: float) -> str:
        """Generate reason for delegation"""
        
        reasons = []
        
        # Capability match
        required_caps = set(request.required_capabilities)
        agent_caps = set(agent["capabilities"])
        
        if required_caps.issubset(agent_caps):
            reasons.append("Perfect capability match")
        elif required_caps.intersection(agent_caps):
            reasons.append("Partial capability match")
        
        # Performance
        performance = agent.get("performance_score", 0.5)
        if performance > 0.8:
            reasons.append("High performance history")
        elif performance > 0.6:
            reasons.append("Good performance history")
        
        # Availability
        availability = agent.get("availability", 0.5)
        if availability > 0.8:
            reasons.append("High availability")
        elif availability > 0.6:
            reasons.append("Good availability")
        
        # Specialization
        agent_spec = agent.get("specialization", "general")
        task_domain = await self._identify_task_domain(request)
        if agent_spec == task_domain:
            reasons.append("Domain specialization match")
        
        if not reasons:
            reasons.append("General suitability")
        
        return f"Selected due to: {', '.join(reasons)} (score: {score:.2f})"
    
    async def _select_best_agent(self, scored_agents: List[Dict[str, Any]], request: TaskDelegationRequest) -> Dict[str, Any]:
        """Select the best agent from scored list"""
        
        if not scored_agents:
            raise ValueError("No suitable agents found for task")
        
        # Return highest scored agent
        best_agent = scored_agents[0]
        
        # Additional validation
        if best_agent["score"] < 0.3:
            logger.warning(f"Best agent score is low ({best_agent['score']:.2f}) for task {request.task_id}")
        
        return best_agent
    
    async def update_agent_capabilities(self, agent_id: str, capabilities: List[str]) -> None:
        """Update agent capabilities"""
        
        self.agent_capabilities[agent_id] = capabilities
        logger.info(f"Updated capabilities for agent {agent_id}: {capabilities}")
    
    async def record_task_completion(self, agent_id: str, task_id: str, success: bool, duration: float) -> None:
        """Record task completion for performance tracking"""
        
        if agent_id not in self.agent_performance_history:
            self.agent_performance_history[agent_id] = []
        
        completion_record = {
            "task_id": task_id,
            "success": success,
            "duration": duration,
            "timestamp": datetime.now()
        }
        
        self.agent_performance_history[agent_id].append(completion_record)
        
        # Update load balancer
        await self.load_balancer.complete_task(agent_id, task_id, success)
        
        logger.info(f"Recorded task completion for agent {agent_id}: {task_id} ({'success' if success else 'failure'})")

class TaskLoadBalancer:
    """
    Load balancer for distributing tasks across agents
    """
    
    def __init__(self):
        self.agent_loads = {}
        self.task_assignments = {}
    
    async def assign_task(self, agent_id: str, task_request: TaskDelegationRequest) -> None:
        """Assign a task to an agent"""
        
        if agent_id not in self.agent_loads:
            self.agent_loads[agent_id] = {"active_tasks": 0, "total_effort": 0.0}
        
        # Estimate task effort
        effort = await self._estimate_task_effort(task_request)
        
        # Update agent load
        self.agent_loads[agent_id]["active_tasks"] += 1
        self.agent_loads[agent_id]["total_effort"] += effort
        
        # Track assignment
        self.task_assignments[task_request.task_id] = {
            "agent_id": agent_id,
            "effort": effort,
            "assigned_at": datetime.now()
        }
        
        logger.debug(f"Task {task_request.task_id} assigned to {agent_id} (load: {self.agent_loads[agent_id]})")
    
    async def complete_task(self, agent_id: str, task_id: str, success: bool) -> None:
        """Mark task as completed"""
        
        if task_id in self.task_assignments:
            assignment = self.task_assignments[task_id]
            
            if agent_id in self.agent_loads:
                self.agent_loads[agent_id]["active_tasks"] -= 1
                self.agent_loads[agent_id]["total_effort"] -= assignment["effort"]
                
                # Ensure non-negative values
                self.agent_loads[agent_id]["active_tasks"] = max(0, self.agent_loads[agent_id]["active_tasks"])
                self.agent_loads[agent_id]["total_effort"] = max(0.0, self.agent_loads[agent_id]["total_effort"])
            
            del self.task_assignments[task_id]
            
            logger.debug(f"Task {task_id} completed by {agent_id} ({'success' if success else 'failure'})")
    
    async def get_agent_load(self, agent_id: str) -> Dict[str, Any]:
        """Get current load for an agent"""
        
        return self.agent_loads.get(agent_id, {"active_tasks": 0, "total_effort": 0.0})
    
    async def get_balanced_agent(self, suitable_agents: List[str]) -> str:
        """Get the agent with the lowest load"""
        
        if not suitable_agents:
            raise ValueError("No suitable agents provided")
        
        # Calculate load scores
        agent_loads = {}
        for agent_id in suitable_agents:
            load = await self.get_agent_load(agent_id)
            # Simple load score: combination of active tasks and effort
            agent_loads[agent_id] = load["active_tasks"] * 0.5 + load["total_effort"] * 0.5
        
        # Return agent with lowest load
        return min(agent_loads, key=agent_loads.get)
    
    async def _estimate_task_effort(self, task_request: TaskDelegationRequest) -> float:
        """Estimate task effort for load balancing"""
        
        complexity_effort = {
            TaskComplexity.LOW: 1.0,
            TaskComplexity.MEDIUM: 2.0,
            TaskComplexity.HIGH: 4.0,
            TaskComplexity.EXTREME: 8.0
        }
        
        return complexity_effort[task_request.complexity]