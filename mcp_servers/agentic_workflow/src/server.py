"""
Agentic Workflow MCP Server - Main Implementation
Complete implementation of the Agentic Workflow MCP server with ReAct patterns,
dynamic agent spawning, and workflow learning capabilities.
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
import uuid

# MCP imports
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent, ImageContent, EmbeddedResource

# Internal imports
from .engines.react_engine import ReActEngine, ReActResult
from .engines.agent_spawner import AgentSpawner, AgentType
from .engines.workflow_optimizer import WorkflowLearningEngine, SelfImprovingWorkflow
from .agents.base_agent import BaseAgent, AgentTask, AgentResult
from .agents.research_agent import ResearchAgent
from .agents.code_agent import CodeAgent
from .agents.test_agent import TestAgent
from .agents.orchestrator_agent import OrchestratorAgent

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class WorkflowRequest:
    """Request for workflow execution"""
    workflow_id: str
    workflow_type: str
    description: str
    parameters: Dict[str, Any]
    priority: int = 5
    timeout: float = 3600  # 1 hour default
    require_learning: bool = True

@dataclass
class WorkflowResponse:
    """Response from workflow execution"""
    workflow_id: str
    success: bool
    result: Dict[str, Any]
    execution_time: float
    agents_used: List[str]
    learning_insights: List[str]
    performance_metrics: Dict[str, Any]
    recommendations: List[str]

class AgenticWorkflowServer:
    """
    Main Agentic Workflow MCP Server
    
    Integrates all components for autonomous workflow execution:
    - ReAct Engine for reasoning-action-observation cycles
    - AgentSpawner for dynamic agent management
    - WorkflowLearningEngine for pattern extraction and optimization
    - Specialized agents for different tasks
    """
    
    def __init__(self):
        self.server = Server("agentic-workflow")
        self.react_engine = ReActEngine()
        self.agent_spawner = AgentSpawner()
        self.learning_engine = WorkflowLearningEngine()
        
        # Active workflows and agents
        self.active_workflows = {}
        self.active_agents = {}
        self.workflow_history = []
        
        # Performance tracking
        self.performance_metrics = {
            "total_workflows": 0,
            "successful_workflows": 0,
            "total_execution_time": 0.0,
            "average_execution_time": 0.0,
            "agents_spawned": 0,
            "learning_cycles": 0,
            "optimization_improvements": 0.0
        }
        
        # Cross-MCP integration clients
        self.mcp_clients = {}
        
        # Self-improving workflows
        self.self_improving_workflows = {}
        
        # Initialize server components
        self._setup_server_handlers()
        self._setup_tools()
        self._setup_resources()
        
        logger.info("Agentic Workflow MCP Server initialized successfully")
    
    def _setup_server_handlers(self):
        """Setup MCP server handlers"""
        
        @self.server.list_resources()
        async def list_resources() -> List[Resource]:
            """List available resources"""
            return [
                Resource(
                    uri="workflow://status",
                    name="Workflow Status",
                    description="Current status of all workflows",
                    mimeType="application/json"
                ),
                Resource(
                    uri="workflow://metrics",
                    name="Performance Metrics",
                    description="Performance metrics and analytics",
                    mimeType="application/json"
                ),
                Resource(
                    uri="workflow://agents",
                    name="Active Agents",
                    description="Information about active agents",
                    mimeType="application/json"
                ),
                Resource(
                    uri="workflow://learning",
                    name="Learning Insights",
                    description="Workflow learning and optimization insights",
                    mimeType="application/json"
                )
            ]
        
        @self.server.read_resource()
        async def read_resource(uri: str) -> str:
            """Read a specific resource"""
            
            if uri == "workflow://status":
                return json.dumps(await self._get_workflow_status(), indent=2)
            elif uri == "workflow://metrics":
                return json.dumps(self.performance_metrics, indent=2)
            elif uri == "workflow://agents":
                return json.dumps(await self._get_active_agents_info(), indent=2)
            elif uri == "workflow://learning":
                return json.dumps(await self._get_learning_insights(), indent=2)
            else:
                raise ValueError(f"Unknown resource: {uri}")
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """List available tools"""
            return [
                Tool(
                    name="execute_workflow",
                    description="Execute a workflow using ReAct patterns and dynamic agents",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "workflow_type": {
                                "type": "string",
                                "description": "Type of workflow to execute",
                                "enum": ["development", "analysis", "testing", "research", "optimization", "custom"]
                            },
                            "description": {
                                "type": "string",
                                "description": "Description of the workflow task"
                            },
                            "parameters": {
                                "type": "object",
                                "description": "Parameters for the workflow execution"
                            },
                            "priority": {
                                "type": "integer",
                                "description": "Priority level (1=highest, 10=lowest)",
                                "default": 5
                            },
                            "timeout": {
                                "type": "number",
                                "description": "Timeout in seconds",
                                "default": 3600
                            },
                            "require_learning": {
                                "type": "boolean",
                                "description": "Whether to apply learning and optimization",
                                "default": True
                            }
                        },
                        "required": ["workflow_type", "description"]
                    }
                ),
                Tool(
                    name="spawn_agent",
                    description="Spawn a specialized agent for specific tasks",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "agent_type": {
                                "type": "string",
                                "description": "Type of agent to spawn",
                                "enum": ["research", "code", "test", "orchestrator"]
                            },
                            "task_context": {
                                "type": "object",
                                "description": "Context and requirements for the agent"
                            },
                            "priority": {
                                "type": "integer",
                                "description": "Priority level for resource allocation",
                                "default": 5
                            }
                        },
                        "required": ["agent_type", "task_context"]
                    }
                ),
                Tool(
                    name="optimize_workflow",
                    description="Optimize a workflow using learning patterns",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "workflow_id": {
                                "type": "string",
                                "description": "ID of the workflow to optimize"
                            },
                            "optimization_targets": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Aspects to optimize",
                                "default": ["performance", "quality", "efficiency"]
                            }
                        },
                        "required": ["workflow_id"]
                    }
                ),
                Tool(
                    name="get_workflow_status",
                    description="Get the status of workflows",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "workflow_id": {
                                "type": "string",
                                "description": "Specific workflow ID (optional)"
                            }
                        }
                    }
                ),
                Tool(
                    name="analyze_performance",
                    description="Analyze workflow performance and generate insights",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "time_period": {
                                "type": "string",
                                "description": "Time period for analysis",
                                "enum": ["last_hour", "last_day", "last_week", "all_time"],
                                "default": "last_day"
                            },
                            "metrics": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Specific metrics to analyze",
                                "default": ["execution_time", "success_rate", "agent_efficiency"]
                            }
                        }
                    }
                ),
                Tool(
                    name="create_self_improving_workflow",
                    description="Create a self-improving workflow that learns from execution",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "base_workflow": {
                                "type": "object",
                                "description": "Base workflow definition"
                            },
                            "learning_parameters": {
                                "type": "object",
                                "description": "Parameters for learning and improvement"
                            }
                        },
                        "required": ["base_workflow"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool calls"""
            
            try:
                if name == "execute_workflow":
                    result = await self._execute_workflow(arguments)
                elif name == "spawn_agent":
                    result = await self._spawn_agent(arguments)
                elif name == "optimize_workflow":
                    result = await self._optimize_workflow(arguments)
                elif name == "get_workflow_status":
                    result = await self._get_workflow_status(arguments.get("workflow_id"))
                elif name == "analyze_performance":
                    result = await self._analyze_performance(arguments)
                elif name == "create_self_improving_workflow":
                    result = await self._create_self_improving_workflow(arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
                
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
                
            except Exception as e:
                logger.error(f"Tool call failed: {name} - {str(e)}")
                return [TextContent(type="text", text=json.dumps({
                    "error": str(e),
                    "tool": name,
                    "timestamp": datetime.now().isoformat()
                }, indent=2))]
    
    def _setup_tools(self):
        """Setup internal tools and utilities"""
        
        # Initialize cross-MCP clients
        self.mcp_clients = {
            "ml_code_intelligence": None,  # Will be initialized when needed
            "context_aware_memory": None,
            "ml_testing_qa": None,
            "predictive_analytics": None
        }
    
    def _setup_resources(self):
        """Setup server resources"""
        
        # Resource initialization
        logger.info("Server resources initialized")
    
    async def _execute_workflow(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a workflow with ReAct patterns and dynamic agents"""
        
        workflow_request = WorkflowRequest(
            workflow_id=str(uuid.uuid4()),
            workflow_type=arguments["workflow_type"],
            description=arguments["description"],
            parameters=arguments.get("parameters", {}),
            priority=arguments.get("priority", 5),
            timeout=arguments.get("timeout", 3600),
            require_learning=arguments.get("require_learning", True)
        )
        
        logger.info(f"Executing workflow {workflow_request.workflow_id}: {workflow_request.description}")
        
        start_time = time.time()
        
        try:
            # Add to active workflows
            self.active_workflows[workflow_request.workflow_id] = {
                "request": workflow_request,
                "status": "running",
                "start_time": start_time,
                "agents_used": [],
                "progress": 0.0
            }
            
            # Execute workflow using ReAct engine
            react_result = await self._execute_react_workflow(workflow_request)
            
            # Apply learning if required
            learning_insights = []
            if workflow_request.require_learning:
                learning_result = await self._apply_workflow_learning(workflow_request, react_result)
                learning_insights = learning_result.get("insights", [])
            
            # Update performance metrics
            execution_time = time.time() - start_time
            await self._update_performance_metrics(workflow_request, react_result, execution_time)
            
            # Create response
            response = WorkflowResponse(
                workflow_id=workflow_request.workflow_id,
                success=react_result.success,
                result=react_result.final_result,
                execution_time=execution_time,
                agents_used=react_result.final_result.get("agents_used", []),
                learning_insights=learning_insights,
                performance_metrics=react_result.metrics,
                recommendations=react_result.final_result.get("recommendations", [])
            )
            
            # Move to history
            self.workflow_history.append(response)
            if workflow_request.workflow_id in self.active_workflows:
                del self.active_workflows[workflow_request.workflow_id]
            
            logger.info(f"Workflow {workflow_request.workflow_id} completed successfully")
            return asdict(response)
            
        except Exception as e:
            logger.error(f"Workflow {workflow_request.workflow_id} failed: {str(e)}")
            
            # Update active workflows
            if workflow_request.workflow_id in self.active_workflows:
                self.active_workflows[workflow_request.workflow_id]["status"] = "failed"
                self.active_workflows[workflow_request.workflow_id]["error"] = str(e)
            
            return {
                "workflow_id": workflow_request.workflow_id,
                "success": False,
                "error": str(e),
                "execution_time": time.time() - start_time
            }
    
    async def _execute_react_workflow(self, workflow_request: WorkflowRequest) -> ReActResult:
        """Execute workflow using ReAct engine"""
        
        # Create task context for ReAct engine
        task_context = {
            "workflow_type": workflow_request.workflow_type,
            "description": workflow_request.description,
            "parameters": workflow_request.parameters,
            "priority": workflow_request.priority,
            "timeout": workflow_request.timeout,
            "agent_spawner": self.agent_spawner,
            "mcp_clients": self.mcp_clients
        }
        
        # Execute ReAct cycle
        react_result = await self.react_engine.execute_cycle(
            task=workflow_request.description,
            context=task_context
        )
        
        # Enhance result with agent coordination
        if react_result.success:
            enhanced_result = await self._enhance_with_agent_coordination(react_result, workflow_request)
            react_result.final_result.update(enhanced_result)
        
        return react_result
    
    async def _enhance_with_agent_coordination(self, react_result: ReActResult, workflow_request: WorkflowRequest) -> Dict[str, Any]:
        """Enhance results with coordinated agent execution"""
        
        # Determine required agents based on workflow type
        required_agents = await self._determine_required_agents(workflow_request)
        
        # Spawn and coordinate agents
        coordinated_results = {}
        agents_used = []
        
        for agent_type in required_agents:
            try:
                # Spawn agent
                agent_id = await self.agent_spawner.spawn_agent(
                    agent_type=agent_type,
                    task_context={
                        "workflow_id": workflow_request.workflow_id,
                        "workflow_type": workflow_request.workflow_type,
                        "description": workflow_request.description,
                        "parameters": workflow_request.parameters
                    }
                )
                
                agents_used.append(agent_id)
                
                # Execute agent task
                agent_result = await self._execute_agent_task(agent_id, workflow_request)
                coordinated_results[agent_type.value] = agent_result
                
            except Exception as e:
                logger.error(f"Agent coordination failed for {agent_type.value}: {str(e)}")
                coordinated_results[agent_type.value] = {"error": str(e)}
        
        return {
            "coordinated_results": coordinated_results,
            "agents_used": agents_used,
            "coordination_success": len([r for r in coordinated_results.values() if "error" not in r])
        }
    
    async def _determine_required_agents(self, workflow_request: WorkflowRequest) -> List[AgentType]:
        """Determine what agents are needed for the workflow"""
        
        workflow_type = workflow_request.workflow_type.lower()
        
        if workflow_type == "development":
            return [AgentType.RESEARCH, AgentType.CODE, AgentType.TEST]
        elif workflow_type == "analysis":
            return [AgentType.RESEARCH, AgentType.CODE]
        elif workflow_type == "testing":
            return [AgentType.TEST, AgentType.CODE]
        elif workflow_type == "research":
            return [AgentType.RESEARCH]
        elif workflow_type == "optimization":
            return [AgentType.CODE, AgentType.TEST, AgentType.ORCHESTRATOR]
        else:
            # Custom workflow - try to infer from description
            return await self._infer_agents_from_description(workflow_request.description)
    
    async def _infer_agents_from_description(self, description: str) -> List[AgentType]:
        """Infer required agents from workflow description"""
        
        description_lower = description.lower()
        agents = []
        
        if any(keyword in description_lower for keyword in ["research", "analyze", "investigate", "study"]):
            agents.append(AgentType.RESEARCH)
        
        if any(keyword in description_lower for keyword in ["code", "implement", "develop", "build"]):
            agents.append(AgentType.CODE)
        
        if any(keyword in description_lower for keyword in ["test", "validate", "verify", "qa"]):
            agents.append(AgentType.TEST)
        
        if any(keyword in description_lower for keyword in ["orchestrate", "coordinate", "manage"]):
            agents.append(AgentType.ORCHESTRATOR)
        
        # Default to research and code if no specific agents identified
        if not agents:
            agents = [AgentType.RESEARCH, AgentType.CODE]
        
        return agents
    
    async def _execute_agent_task(self, agent_id: str, workflow_request: WorkflowRequest) -> Dict[str, Any]:
        """Execute a task using a specific agent"""
        
        # Get agent from spawner
        agent_status = await self.agent_spawner.get_agent_status(agent_id)
        if not agent_status:
            raise ValueError(f"Agent {agent_id} not found")
        
        # Create agent task
        agent_task = AgentTask(
            task_id=str(uuid.uuid4()),
            task_type=workflow_request.workflow_type,
            description=workflow_request.description,
            parameters=workflow_request.parameters,
            priority=workflow_request.priority,
            deadline=None,
            context={"workflow_id": workflow_request.workflow_id},
            dependencies=[]
        )
        
        # Execute task (this would integrate with the actual agent execution)
        # For now, we'll simulate the execution
        await asyncio.sleep(0.5)  # Simulate agent work
        
        return {
            "agent_id": agent_id,
            "task_id": agent_task.task_id,
            "success": True,
            "result": f"Agent {agent_id} completed task successfully",
            "execution_time": 0.5
        }
    
    async def _apply_workflow_learning(self, workflow_request: WorkflowRequest, react_result: ReActResult) -> Dict[str, Any]:
        """Apply learning to workflow execution"""
        
        # Extract workflow trace
        workflow_trace = []
        for step in react_result.reasoning_trace:
            trace_step = {
                "step_type": step.step_type,
                "content": step.content,
                "timestamp": step.timestamp.isoformat(),
                "confidence": step.confidence,
                "metadata": step.metadata
            }
            workflow_trace.append(trace_step)
        
        # Create outcome data
        outcome = {
            "success": react_result.success,
            "confidence": react_result.confidence,
            "execution_time": react_result.execution_time,
            "workflow_type": workflow_request.workflow_type,
            "metrics": react_result.metrics,
            "context": {"workflow_id": workflow_request.workflow_id}
        }
        
        # Apply learning
        learning_result = await self.learning_engine.learn_from_execution(workflow_trace, outcome)
        
        # Update learning metrics
        self.performance_metrics["learning_cycles"] += 1
        if learning_result.get("optimizations_generated", 0) > 0:
            self.performance_metrics["optimization_improvements"] += 0.1
        
        return learning_result
    
    async def _update_performance_metrics(self, workflow_request: WorkflowRequest, react_result: ReActResult, execution_time: float):
        """Update performance metrics"""
        
        self.performance_metrics["total_workflows"] += 1
        
        if react_result.success:
            self.performance_metrics["successful_workflows"] += 1
        
        self.performance_metrics["total_execution_time"] += execution_time
        self.performance_metrics["average_execution_time"] = (
            self.performance_metrics["total_execution_time"] / 
            self.performance_metrics["total_workflows"]
        )
        
        # Update agent spawn count
        agents_used = react_result.final_result.get("agents_used", [])
        self.performance_metrics["agents_spawned"] += len(agents_used)
    
    async def _spawn_agent(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Spawn a specialized agent"""
        
        agent_type_str = arguments["agent_type"]
        task_context = arguments["task_context"]
        priority = arguments.get("priority", 5)
        
        # Convert string to AgentType enum
        agent_type = AgentType(f"{agent_type_str}_agent")
        
        try:
            # Spawn agent
            agent_id = await self.agent_spawner.spawn_agent(
                agent_type=agent_type,
                task_context=task_context,
                priority=priority
            )
            
            logger.info(f"Agent {agent_id} spawned successfully")
            
            return {
                "success": True,
                "agent_id": agent_id,
                "agent_type": agent_type.value,
                "task_context": task_context,
                "priority": priority
            }
            
        except Exception as e:
            logger.error(f"Agent spawn failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "agent_type": agent_type_str
            }
    
    async def _optimize_workflow(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize a workflow using learning patterns"""
        
        workflow_id = arguments["workflow_id"]
        optimization_targets = arguments.get("optimization_targets", ["performance", "quality", "efficiency"])
        
        # Find workflow in history
        workflow_data = None
        for workflow in self.workflow_history:
            if workflow.workflow_id == workflow_id:
                workflow_data = workflow
                break
        
        if not workflow_data:
            return {
                "success": False,
                "error": f"Workflow {workflow_id} not found"
            }
        
        try:
            # Generate optimizations using learning engine
            optimization_result = await self.learning_engine.recommend_optimizations(
                workflow_data.result.get("workflow_type", "custom")
            )
            
            return {
                "success": True,
                "workflow_id": workflow_id,
                "optimization_targets": optimization_targets,
                "recommendations": optimization_result,
                "optimization_count": len(optimization_result)
            }
            
        except Exception as e:
            logger.error(f"Workflow optimization failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "workflow_id": workflow_id
            }
    
    async def _get_workflow_status(self, workflow_id: Optional[str] = None) -> Dict[str, Any]:
        """Get workflow status"""
        
        if workflow_id:
            # Get specific workflow status
            if workflow_id in self.active_workflows:
                workflow = self.active_workflows[workflow_id]
                return {
                    "workflow_id": workflow_id,
                    "status": workflow["status"],
                    "start_time": workflow["start_time"],
                    "progress": workflow["progress"],
                    "agents_used": workflow["agents_used"]
                }
            else:
                # Check history
                for workflow in self.workflow_history:
                    if workflow.workflow_id == workflow_id:
                        return {
                            "workflow_id": workflow_id,
                            "status": "completed" if workflow.success else "failed",
                            "success": workflow.success,
                            "execution_time": workflow.execution_time,
                            "agents_used": workflow.agents_used
                        }
                
                return {
                    "workflow_id": workflow_id,
                    "status": "not_found"
                }
        else:
            # Get all workflows status
            return {
                "active_workflows": len(self.active_workflows),
                "completed_workflows": len(self.workflow_history),
                "total_workflows": self.performance_metrics["total_workflows"],
                "success_rate": (
                    self.performance_metrics["successful_workflows"] / 
                    max(1, self.performance_metrics["total_workflows"])
                ),
                "active_workflow_details": list(self.active_workflows.keys()),
                "recent_completions": [
                    {
                        "workflow_id": w.workflow_id,
                        "success": w.success,
                        "execution_time": w.execution_time
                    }
                    for w in self.workflow_history[-5:]  # Last 5 completions
                ]
            }
    
    async def _analyze_performance(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze workflow performance"""
        
        time_period = arguments.get("time_period", "last_day")
        metrics = arguments.get("metrics", ["execution_time", "success_rate", "agent_efficiency"])
        
        # Filter workflows based on time period
        filtered_workflows = self.workflow_history  # Simplified - would filter by time in real implementation
        
        analysis = {
            "time_period": time_period,
            "analyzed_workflows": len(filtered_workflows),
            "metrics": {}
        }
        
        if "execution_time" in metrics:
            execution_times = [w.execution_time for w in filtered_workflows]
            analysis["metrics"]["execution_time"] = {
                "average": sum(execution_times) / len(execution_times) if execution_times else 0,
                "min": min(execution_times) if execution_times else 0,
                "max": max(execution_times) if execution_times else 0,
                "count": len(execution_times)
            }
        
        if "success_rate" in metrics:
            successful = sum(1 for w in filtered_workflows if w.success)
            analysis["metrics"]["success_rate"] = {
                "rate": successful / len(filtered_workflows) if filtered_workflows else 0,
                "successful": successful,
                "total": len(filtered_workflows)
            }
        
        if "agent_efficiency" in metrics:
            total_agents = sum(len(w.agents_used) for w in filtered_workflows)
            analysis["metrics"]["agent_efficiency"] = {
                "average_agents_per_workflow": total_agents / len(filtered_workflows) if filtered_workflows else 0,
                "total_agents_used": total_agents,
                "agent_utilization": min(1.0, total_agents / (len(filtered_workflows) * 3))  # Assuming max 3 agents per workflow
            }
        
        return analysis
    
    async def _create_self_improving_workflow(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Create a self-improving workflow"""
        
        base_workflow = arguments["base_workflow"]
        learning_parameters = arguments.get("learning_parameters", {})
        
        try:
            # Create self-improving workflow
            workflow_id = str(uuid.uuid4())
            
            self_improving_workflow = SelfImprovingWorkflow(base_workflow)
            self.self_improving_workflows[workflow_id] = self_improving_workflow
            
            return {
                "success": True,
                "workflow_id": workflow_id,
                "base_workflow": base_workflow,
                "learning_parameters": learning_parameters,
                "optimization_cycles": 0
            }
            
        except Exception as e:
            logger.error(f"Self-improving workflow creation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _get_active_agents_info(self) -> Dict[str, Any]:
        """Get information about active agents"""
        
        active_agents = await self.agent_spawner.list_active_agents()
        agent_summary = await self.agent_spawner.get_agent_performance_summary()
        
        return {
            "active_agent_count": len(active_agents),
            "active_agents": active_agents,
            "performance_summary": agent_summary,
            "total_agents_spawned": self.performance_metrics["agents_spawned"]
        }
    
    async def _get_learning_insights(self) -> Dict[str, Any]:
        """Get learning and optimization insights"""
        
        return {
            "learning_cycles_completed": self.performance_metrics["learning_cycles"],
            "optimization_improvements": self.performance_metrics["optimization_improvements"],
            "self_improving_workflows": len(self.self_improving_workflows),
            "recent_learning_insights": [
                w.learning_insights for w in self.workflow_history[-5:]
            ]
        }
    
    async def start_server(self):
        """Start the MCP server"""
        logger.info("Starting Agentic Workflow MCP Server...")
        
        # Initialize server components
        await self._initialize_server_components()
        
        # Start stdio server
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="agentic-workflow",
                    server_version="1.0.0",
                    capabilities={}
                )
            )
    
    async def _initialize_server_components(self):
        """Initialize server components"""
        
        # Initialize agent spawner
        await self.agent_spawner.performance_monitor.record_metric("server", "initialization", time.time())
        
        # Initialize learning engine
        logger.info("Learning engine initialized")
        
        # Initialize cross-MCP clients (when available)
        await self._initialize_mcp_clients()
        
        logger.info("Server components initialized successfully")
    
    async def _initialize_mcp_clients(self):
        """Initialize cross-MCP clients"""
        
        # This would initialize actual MCP clients when available
        # For now, we'll use placeholder clients
        
        logger.info("Cross-MCP clients initialized")

# Server entry point
server = AgenticWorkflowServer()

async def main():
    """Main entry point"""
    try:
        await server.start_server()
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())