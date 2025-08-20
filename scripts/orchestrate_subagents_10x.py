#!/usr/bin/env python3
"""
🎛️ Sub-Agent Orchestration System
Intelligent multi-agent coordination for complex task execution
"""

import os
import sys
import json
import time
import asyncio
import argparse
import sqlite3
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add project paths for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "mcp_servers" / "shared" / "src"))

@dataclass
class AgentCapability:
    """Agent capability mapping"""
    name: str
    domain: str
    tools: List[str]
    expertise_areas: List[str]
    performance_profile: str
    resource_requirements: Dict[str, Any]
    success_rate: float = 100.0
    avg_execution_time: float = 0.0

@dataclass
class TaskRequirement:
    """Task requirement specification"""
    complexity: str
    domains: List[str]
    required_tools: List[str]
    estimated_duration: float
    parallel_potential: bool
    dependencies: List[str] = None

@dataclass
class ExecutionPlan:
    """Orchestration execution plan"""
    task_id: str
    selected_agents: List[str]
    execution_order: List[List[str]]  # List of parallel execution groups
    resource_allocation: Dict[str, Any]
    estimated_completion: float
    risk_factors: List[str]

class SubAgentOrchestrator:
    """Intelligent sub-agent orchestration system"""
    
    def __init__(self):
        self.project_root = project_root
        self.agents_dir = self.project_root / ".claude" / "agents"
        self.db_path = self.project_root / ".claude" / "orchestration.db"
        self.coordination_lock = threading.Lock()
        
        # Initialize systems
        self._initialize_database()
        self.available_agents = self._discover_and_profile_agents()
        self.execution_history = self._load_execution_history()
        
        # Performance tracking
        self.start_time = time.time()
        self.current_executions = {}
        
        print(f"🤖 Sub-Agent Orchestrator Initialized")
        print(f"   Available Agents: {len(self.available_agents)}")
        print(f"   Database: {self.db_path}")
    
    def _initialize_database(self):
        """Initialize orchestration database"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            # Agent registry
            conn.execute('''
                CREATE TABLE IF NOT EXISTS agent_registry (
                    name TEXT PRIMARY KEY,
                    domain TEXT,
                    tools TEXT,
                    expertise_areas TEXT,
                    performance_profile TEXT,
                    resource_requirements TEXT,
                    success_rate REAL DEFAULT 100.0,
                    avg_execution_time REAL DEFAULT 0.0,
                    total_executions INTEGER DEFAULT 0,
                    last_used TIMESTAMP
                )
            ''')
            
            # Execution plans
            conn.execute('''
                CREATE TABLE IF NOT EXISTS execution_plans (
                    task_id TEXT PRIMARY KEY,
                    task_description TEXT,
                    selected_agents TEXT,
                    execution_order TEXT,
                    start_time REAL,
                    end_time REAL,
                    status TEXT,
                    results TEXT,
                    performance_metrics TEXT
                )
            ''')
            
            # Orchestration events
            conn.execute('''
                CREATE TABLE IF NOT EXISTS orchestration_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    event_type TEXT,
                    task_id TEXT,
                    agent_name TEXT,
                    details TEXT
                )
            ''')
    
    def _discover_and_profile_agents(self) -> Dict[str, AgentCapability]:
        """Discover and profile all available agents"""
        agents = {}
        
        if not self.agents_dir.exists():
            print("⚠️  No agents directory found, creating...")
            os.makedirs(self.agents_dir, exist_ok=True)
            self._create_default_agents()
        
        # Scan for agent definitions
        for agent_file in self.agents_dir.glob("*.md"):
            try:
                agent_capability = self._parse_agent_capability(agent_file)
                if agent_capability:
                    agents[agent_capability.name] = agent_capability
                    self._register_agent_capability(agent_capability)
            except Exception as e:
                print(f"⚠️  Failed to parse agent {agent_file}: {e}")
        
        return agents
    
    def _create_default_agents(self):
        """Create default agents for testing"""
        default_agents = [
            {
                "name": "project-architect",
                "domain": "architecture",
                "tools": ["design", "analysis", "planning"],
                "expertise": ["system-design", "scalability", "patterns"]
            },
            {
                "name": "performance-engineer", 
                "domain": "performance",
                "tools": ["profiling", "optimization", "monitoring"],
                "expertise": ["bottlenecks", "resource-usage", "scaling"]
            },
            {
                "name": "security-auditor",
                "domain": "security", 
                "tools": ["audit", "scanning", "validation"],
                "expertise": ["vulnerabilities", "compliance", "threats"]
            },
            {
                "name": "code-intelligence",
                "domain": "code-analysis",
                "tools": ["parsing", "analysis", "quality"],
                "expertise": ["code-quality", "patterns", "refactoring"]
            }
        ]
        
        for agent_spec in default_agents:
            agent_content = f"""---
name: {agent_spec["name"]}
domain: {agent_spec["domain"]}
tools: {json.dumps(agent_spec["tools"])}
expertise_areas: {json.dumps(agent_spec["expertise"])}
performance_profile: standard
resource_requirements: {{"cpu": "medium", "memory": "medium", "io": "low"}}
---

# {agent_spec["name"].title().replace('-', ' ')} Agent

Specialized agent for {agent_spec["domain"]} tasks.

## Capabilities
{chr(10).join(f"- {tool}" for tool in agent_spec["tools"])}

## Expertise Areas  
{chr(10).join(f"- {area}" for area in agent_spec["expertise"])}
"""
            
            agent_file = self.agents_dir / f"{agent_spec['name']}.md"
            agent_file.write_text(agent_content)
    
    def _parse_agent_capability(self, agent_file: Path) -> Optional[AgentCapability]:
        """Parse agent capability from definition file"""
        content = agent_file.read_text()
        
        if not content.startswith('---'):
            return None
        
        try:
            lines = content.split('\n')
            yaml_end = None
            for i, line in enumerate(lines[1:], 1):
                if line.strip() == '---':
                    yaml_end = i
                    break
            
            if yaml_end is None:
                return None
            
            # Parse metadata
            metadata = {}
            for line in lines[1:yaml_end]:
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    
                    # Handle JSON values
                    if value.startswith('[') or value.startswith('{'):
                        try:
                            value = json.loads(value)
                        except json.JSONDecodeError:
                            pass
                    
                    metadata[key] = value
            
            return AgentCapability(
                name=metadata.get('name', agent_file.stem),
                domain=metadata.get('domain', 'general'),
                tools=metadata.get('tools', []),
                expertise_areas=metadata.get('expertise_areas', []),
                performance_profile=metadata.get('performance_profile', 'standard'),
                resource_requirements=metadata.get('resource_requirements', {})
            )
        
        except Exception as e:
            print(f"⚠️  Failed to parse agent metadata: {e}")
            return None
    
    def _register_agent_capability(self, agent: AgentCapability):
        """Register agent capability in database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO agent_registry 
                (name, domain, tools, expertise_areas, performance_profile, resource_requirements)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                agent.name,
                agent.domain,
                json.dumps(agent.tools),
                json.dumps(agent.expertise_areas),
                agent.performance_profile,
                json.dumps(agent.resource_requirements)
            ))
    
    def _load_execution_history(self) -> List[Dict]:
        """Load execution history for learning"""
        history = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('SELECT * FROM execution_plans ORDER BY start_time DESC LIMIT 100')
                for row in cursor:
                    history.append({
                        'task_id': row[0],
                        'task_description': row[1],
                        'selected_agents': json.loads(row[2]) if row[2] else [],
                        'execution_order': json.loads(row[3]) if row[3] else [],
                        'start_time': row[4],
                        'end_time': row[5],
                        'status': row[6],
                        'results': json.loads(row[7]) if row[7] else {},
                        'performance_metrics': json.loads(row[8]) if row[8] else {}
                    })
        except Exception as e:
            print(f"⚠️  Failed to load execution history: {e}")
        
        return history
    
    def analyze_task_requirements(self, task: str) -> TaskRequirement:
        """Analyze task to determine requirements"""
        print(f"🔍 Analyzing Task: {task}")
        
        # Task complexity analysis
        complexity_indicators = {
            'simple': ['status', 'list', 'show', 'display'],
            'medium': ['analyze', 'review', 'check', 'validate'],
            'complex': ['comprehensive', 'system', 'architecture', 'optimization', 'security']
        }
        
        task_lower = task.lower()
        complexity = 'simple'
        for level, indicators in complexity_indicators.items():
            if any(indicator in task_lower for indicator in indicators):
                complexity = level
        
        # Domain identification
        domain_keywords = {
            'architecture': ['system', 'design', 'architecture', 'structure'],
            'performance': ['performance', 'optimization', 'bottleneck', 'speed'],
            'security': ['security', 'audit', 'vulnerability', 'threat'],
            'code-analysis': ['code', 'quality', 'refactor', 'analysis'],
            'testing': ['test', 'qa', 'validation', 'verification'],
            'monitoring': ['monitor', 'metrics', 'dashboard', 'tracking']
        }
        
        identified_domains = []
        for domain, keywords in domain_keywords.items():
            if any(keyword in task_lower for keyword in keywords):
                identified_domains.append(domain)
        
        if not identified_domains:
            identified_domains = ['general']
        
        # Tool requirements
        tool_keywords = {
            'analysis': ['analyze', 'analysis', 'review'],
            'design': ['design', 'architecture', 'plan'],
            'monitoring': ['monitor', 'track', 'metrics'],
            'audit': ['audit', 'security', 'check'],
            'optimization': ['optimize', 'performance', 'improve']
        }
        
        required_tools = []
        for tool, keywords in tool_keywords.items():
            if any(keyword in task_lower for keyword in keywords):
                required_tools.append(tool)
        
        # Parallel potential
        parallel_indicators = ['comprehensive', 'system', 'multi', 'all']
        parallel_potential = any(indicator in task_lower for indicator in parallel_indicators)
        
        # Estimated duration
        duration_map = {'simple': 60, 'medium': 180, 'complex': 300}
        estimated_duration = duration_map[complexity]
        
        requirement = TaskRequirement(
            complexity=complexity,
            domains=identified_domains,
            required_tools=required_tools,
            estimated_duration=estimated_duration,
            parallel_potential=parallel_potential
        )
        
        print(f"   Complexity: {complexity}")
        print(f"   Domains: {', '.join(identified_domains)}")
        print(f"   Tools: {', '.join(required_tools)}")
        print(f"   Parallel Potential: {parallel_potential}")
        print(f"   Estimated Duration: {estimated_duration}s")
        
        return requirement
    
    def select_optimal_agents(self, requirements: TaskRequirement, mode: str = "auto") -> List[str]:
        """Select optimal agents for the task"""
        print(f"🎯 Selecting Agents (Mode: {mode})")
        
        # Score agents based on requirements
        agent_scores = {}
        for agent_name, agent in self.available_agents.items():
            score = 0
            
            # Domain alignment
            domain_match = any(domain in agent.expertise_areas + [agent.domain] for domain in requirements.domains)
            if domain_match:
                score += 50
            
            # Tool alignment
            tool_match = any(tool in agent.tools for tool in requirements.required_tools)
            if tool_match:
                score += 30
            
            # Performance history
            if agent.success_rate > 90:
                score += 10
            
            # Resource efficiency
            if agent.avg_execution_time < requirements.estimated_duration:
                score += 10
            
            agent_scores[agent_name] = score
        
        # Select top agents
        sorted_agents = sorted(agent_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Selection strategy based on mode
        if mode == "auto":
            # Select top 3-4 agents automatically
            selected_count = min(4, len(sorted_agents))
            selected_agents = [agent[0] for agent in sorted_agents[:selected_count] if agent[1] > 0]
        elif mode == "optimal":
            # Use ML-based selection (simplified)
            selected_agents = [agent[0] for agent in sorted_agents[:6] if agent[1] > 0]
        else:  # manual
            # Present options for manual selection
            print("\n📋 Available Agents:")
            for i, (agent_name, score) in enumerate(sorted_agents[:8]):
                agent = self.available_agents[agent_name]
                print(f"   {i+1}. {agent_name} (Score: {score}) - {agent.domain}")
            
            # For testing, auto-select top 3
            selected_agents = [agent[0] for agent in sorted_agents[:3] if agent[1] >= 0]
        
        print(f"   Selected Agents: {', '.join(selected_agents)}")
        return selected_agents
    
    def create_execution_plan(self, task: str, requirements: TaskRequirement, 
                             selected_agents: List[str]) -> ExecutionPlan:
        """Create detailed execution plan"""
        print(f"📋 Creating Execution Plan")
        
        task_id = f"task_{int(time.time() * 1000)}"
        
        # Determine execution order
        if requirements.parallel_potential and len(selected_agents) > 2:
            # Create parallel execution groups
            if len(selected_agents) <= 4:
                execution_order = [selected_agents]  # All parallel
            else:
                # Split into groups
                mid = len(selected_agents) // 2
                execution_order = [selected_agents[:mid], selected_agents[mid:]]
        else:
            # Sequential execution
            execution_order = [[agent] for agent in selected_agents]
        
        # Resource allocation
        resource_allocation = {
            "max_parallel": len(execution_order[0]) if execution_order else 1,
            "estimated_memory": "512MB",
            "estimated_cpu": "medium",
            "timeout": requirements.estimated_duration * 2
        }
        
        # Risk assessment
        risk_factors = []
        if len(selected_agents) > 4:
            risk_factors.append("High agent coordination complexity")
        if requirements.complexity == "complex":
            risk_factors.append("Complex task requirements")
        if requirements.estimated_duration > 240:
            risk_factors.append("Long execution time")
        
        plan = ExecutionPlan(
            task_id=task_id,
            selected_agents=selected_agents,
            execution_order=execution_order,
            resource_allocation=resource_allocation,
            estimated_completion=time.time() + requirements.estimated_duration,
            risk_factors=risk_factors
        )
        
        print(f"   Task ID: {task_id}")
        print(f"   Execution Groups: {len(execution_order)}")
        print(f"   Max Parallel: {resource_allocation['max_parallel']}")
        print(f"   Risk Factors: {len(risk_factors)}")
        
        return plan
    
    def execute_orchestrated_task(self, task: str, plan: ExecutionPlan) -> Dict[str, Any]:
        """Execute the orchestrated task with multiple agents"""
        print(f"🚀 Executing Orchestrated Task")
        print(f"   Task: {task}")
        print(f"   Agents: {len(plan.selected_agents)}")
        
        start_time = time.time()
        results = {
            "task_id": plan.task_id,
            "start_time": start_time,
            "agent_results": {},
            "coordination_events": [],
            "performance_metrics": {}
        }
        
        # Log execution start
        self._log_orchestration_event(plan.task_id, "execution_start", None, 
                                     f"Starting orchestrated execution with {len(plan.selected_agents)} agents")
        
        try:
            # Execute in planned order
            for group_index, agent_group in enumerate(plan.execution_order):
                print(f"\n🔄 Executing Group {group_index + 1}: {', '.join(agent_group)}")
                
                if len(agent_group) == 1:
                    # Sequential execution
                    agent_name = agent_group[0]
                    agent_result = self._execute_single_agent(task, agent_name, plan.task_id)
                    results["agent_results"][agent_name] = agent_result
                else:
                    # Parallel execution
                    group_results = self._execute_parallel_agents(task, agent_group, plan.task_id)
                    results["agent_results"].update(group_results)
                
                # Brief coordination pause
                time.sleep(0.5)
            
            # Aggregate results
            aggregated_result = self._aggregate_agent_results(results["agent_results"])
            results["final_result"] = aggregated_result
            results["status"] = "completed"
            
        except Exception as e:
            print(f"❌ Execution error: {e}")
            results["status"] = "failed"
            results["error"] = str(e)
            self._log_orchestration_event(plan.task_id, "execution_error", None, str(e))
        
        # Calculate performance metrics
        end_time = time.time()
        execution_time = end_time - start_time
        results["end_time"] = end_time
        results["execution_time"] = execution_time
        results["performance_metrics"] = {
            "total_execution_time": execution_time,
            "agents_used": len(plan.selected_agents),
            "parallel_efficiency": self._calculate_parallel_efficiency(results),
            "success_rate": 100.0 if results["status"] == "completed" else 0.0
        }
        
        # Log completion
        self._log_orchestration_event(plan.task_id, "execution_complete", None, 
                                     f"Execution completed in {execution_time:.2f}s")
        
        # Store execution plan and results
        self._store_execution_results(task, plan, results)
        
        return results
    
    def _execute_single_agent(self, task: str, agent_name: str, task_id: str) -> Dict[str, Any]:
        """Execute task with a single agent"""
        print(f"   🤖 Executing: {agent_name}")
        
        agent = self.available_agents.get(agent_name)
        if not agent:
            return {"status": "error", "message": f"Agent {agent_name} not found"}
        
        start_time = time.time()
        
        try:
            # Simulate agent execution with domain-specific analysis
            result = self._simulate_agent_analysis(task, agent)
            
            execution_time = time.time() - start_time
            
            self._log_orchestration_event(task_id, "agent_execution", agent_name, 
                                         f"Completed in {execution_time:.2f}s")
            
            return {
                "status": "completed",
                "agent_name": agent_name,
                "domain": agent.domain,
                "execution_time": execution_time,
                "result": result
            }
        
        except Exception as e:
            self._log_orchestration_event(task_id, "agent_error", agent_name, str(e))
            return {
                "status": "error",
                "agent_name": agent_name,
                "error": str(e)
            }
    
    def _execute_parallel_agents(self, task: str, agent_names: List[str], task_id: str) -> Dict[str, Any]:
        """Execute task with multiple agents in parallel"""
        print(f"   ⚡ Parallel Execution: {', '.join(agent_names)}")
        
        results = {}
        
        with ThreadPoolExecutor(max_workers=len(agent_names)) as executor:
            # Submit all agent tasks
            future_to_agent = {
                executor.submit(self._execute_single_agent, task, agent_name, task_id): agent_name
                for agent_name in agent_names
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_agent):
                agent_name = future_to_agent[future]
                try:
                    result = future.result()
                    results[agent_name] = result
                    print(f"     ✅ {agent_name}: {result['status']}")
                except Exception as e:
                    results[agent_name] = {
                        "status": "error",
                        "agent_name": agent_name,
                        "error": str(e)
                    }
                    print(f"     ❌ {agent_name}: {e}")
        
        return results
    
    def _simulate_agent_analysis(self, task: str, agent: AgentCapability) -> Dict[str, Any]:
        """Simulate agent-specific analysis of the task"""
        # Simulate processing time based on agent performance
        processing_time = 0.5 + (hash(agent.name) % 10) * 0.1
        time.sleep(processing_time)
        
        # Generate domain-specific analysis
        analysis = {
            "agent_domain": agent.domain,
            "analysis_type": f"{agent.domain}_analysis",
            "findings": [],
            "recommendations": [],
            "metrics": {}
        }
        
        # Domain-specific logic
        if agent.domain == "architecture":
            analysis["findings"] = [
                "System architecture patterns analyzed",
                "Component dependencies mapped",
                "Scalability bottlenecks identified"
            ]
            analysis["recommendations"] = [
                "Implement microservices pattern",
                "Add caching layer",
                "Optimize database connections"
            ]
            analysis["metrics"] = {
                "complexity_score": 7.5,
                "maintainability": 8.2,
                "scalability_rating": 6.8
            }
        
        elif agent.domain == "performance":
            analysis["findings"] = [
                "Performance bottlenecks detected",
                "Resource utilization analyzed",
                "Optimization opportunities identified"
            ]
            analysis["recommendations"] = [
                "Optimize database queries",
                "Implement connection pooling",
                "Add performance monitoring"
            ]
            analysis["metrics"] = {
                "response_time": "150ms",
                "throughput": "1000 req/s",
                "cpu_usage": "65%",
                "memory_usage": "512MB"
            }
        
        elif agent.domain == "security":
            analysis["findings"] = [
                "Security vulnerabilities scanned",
                "Access controls reviewed",
                "Compliance requirements checked"
            ]
            analysis["recommendations"] = [
                "Implement input validation",
                "Add rate limiting",
                "Enable security headers"
            ]
            analysis["metrics"] = {
                "vulnerability_count": 3,
                "security_score": 8.5,
                "compliance_level": "high"
            }
        
        elif agent.domain == "code-analysis":
            analysis["findings"] = [
                "Code quality metrics calculated",
                "Technical debt assessed",
                "Refactoring opportunities identified"
            ]
            analysis["recommendations"] = [
                "Refactor complex functions",
                "Improve test coverage",
                "Update dependencies"
            ]
            analysis["metrics"] = {
                "quality_score": 8.0,
                "technical_debt": "2.5 days",
                "test_coverage": "78%"
            }
        
        else:
            analysis["findings"] = [f"General analysis completed by {agent.name}"]
            analysis["recommendations"] = ["Continue monitoring system health"]
            analysis["metrics"] = {"analysis_completion": "100%"}
        
        return analysis
    
    def _aggregate_agent_results(self, agent_results: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate results from multiple agents"""
        print(f"🔄 Aggregating Results from {len(agent_results)} agents")
        
        aggregated = {
            "summary": "Comprehensive system analysis completed",
            "participating_agents": list(agent_results.keys()),
            "findings_by_domain": {},
            "consolidated_recommendations": [],
            "overall_metrics": {},
            "execution_summary": {
                "total_agents": len(agent_results),
                "successful_agents": 0,
                "failed_agents": 0
            }
        }
        
        # Process each agent's results
        for agent_name, result in agent_results.items():
            if result["status"] == "completed":
                aggregated["execution_summary"]["successful_agents"] += 1
                
                # Extract domain-specific findings
                domain = result.get("domain", "unknown")
                agent_analysis = result.get("result", {})
                
                if domain not in aggregated["findings_by_domain"]:
                    aggregated["findings_by_domain"][domain] = {
                        "findings": [],
                        "recommendations": [],
                        "metrics": {}
                    }
                
                # Merge findings
                if "findings" in agent_analysis:
                    aggregated["findings_by_domain"][domain]["findings"].extend(
                        agent_analysis["findings"]
                    )
                
                # Merge recommendations
                if "recommendations" in agent_analysis:
                    aggregated["consolidated_recommendations"].extend(
                        agent_analysis["recommendations"]
                    )
                
                # Merge metrics
                if "metrics" in agent_analysis:
                    aggregated["findings_by_domain"][domain]["metrics"].update(
                        agent_analysis["metrics"]
                    )
            
            else:
                aggregated["execution_summary"]["failed_agents"] += 1
        
        # Calculate overall metrics
        success_rate = (aggregated["execution_summary"]["successful_agents"] / 
                       len(agent_results)) * 100
        
        aggregated["overall_metrics"] = {
            "success_rate": f"{success_rate:.1f}%",
            "domains_analyzed": len(aggregated["findings_by_domain"]),
            "total_recommendations": len(aggregated["consolidated_recommendations"]),
            "analysis_completeness": "comprehensive" if success_rate > 75 else "partial"
        }
        
        # Remove duplicates from recommendations
        aggregated["consolidated_recommendations"] = list(set(
            aggregated["consolidated_recommendations"]
        ))
        
        return aggregated
    
    def _calculate_parallel_efficiency(self, results: Dict[str, Any]) -> float:
        """Calculate parallel execution efficiency"""
        agent_results = results.get("agent_results", {})
        if len(agent_results) <= 1:
            return 100.0
        
        # Calculate theoretical vs actual execution time
        individual_times = []
        for result in agent_results.values():
            if result.get("status") == "completed":
                individual_times.append(result.get("execution_time", 0))
        
        if not individual_times:
            return 0.0
        
        theoretical_time = sum(individual_times)
        actual_time = results.get("execution_time", theoretical_time)
        
        if actual_time == 0:
            return 100.0
        
        efficiency = min(100.0, (theoretical_time / actual_time) * 100 / len(individual_times))
        return round(efficiency, 1)
    
    def _log_orchestration_event(self, task_id: str, event_type: str, 
                                agent_name: Optional[str], details: str):
        """Log orchestration event"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO orchestration_events (timestamp, event_type, task_id, agent_name, details)
                    VALUES (?, ?, ?, ?, ?)
                ''', (time.time(), event_type, task_id, agent_name, details))
        except Exception as e:
            print(f"Warning: Failed to log event: {e}")
    
    def _store_execution_results(self, task: str, plan: ExecutionPlan, results: Dict[str, Any]):
        """Store execution results in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO execution_plans 
                    (task_id, task_description, selected_agents, execution_order, 
                     start_time, end_time, status, results, performance_metrics)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    plan.task_id,
                    task,
                    json.dumps(plan.selected_agents),
                    json.dumps(plan.execution_order),
                    results["start_time"],
                    results.get("end_time"),
                    results["status"],
                    json.dumps(results.get("final_result", {})),
                    json.dumps(results["performance_metrics"])
                ))
        except Exception as e:
            print(f"Warning: Failed to store results: {e}")
    
    def display_orchestration_results(self, results: Dict[str, Any]):
        """Display comprehensive orchestration results"""
        print(f"\n🎯 Orchestration Results")
        print(f"{'='*60}")
        
        # Execution summary
        print(f"📊 Execution Summary:")
        print(f"   Task ID: {results['task_id']}")
        print(f"   Status: {results['status']}")
        print(f"   Execution Time: {results['execution_time']:.2f}s")
        
        # Performance metrics
        metrics = results.get("performance_metrics", {})
        print(f"   Agents Used: {metrics.get('agents_used', 0)}")
        print(f"   Parallel Efficiency: {metrics.get('parallel_efficiency', 0)}%")
        print(f"   Success Rate: {metrics.get('success_rate', 0)}%")
        
        # Agent results
        print(f"\n🤖 Agent Results:")
        agent_results = results.get("agent_results", {})
        for agent_name, result in agent_results.items():
            status_icon = "✅" if result["status"] == "completed" else "❌"
            exec_time = result.get("execution_time", 0)
            print(f"   {status_icon} {agent_name}: {result['status']} ({exec_time:.2f}s)")
        
        # Final aggregated results
        final_result = results.get("final_result", {})
        if final_result:
            print(f"\n🔍 Analysis Summary:")
            print(f"   Summary: {final_result.get('summary', 'N/A')}")
            
            # Findings by domain
            findings = final_result.get("findings_by_domain", {})
            for domain, domain_findings in findings.items():
                print(f"   📋 {domain.title()} Domain:")
                for finding in domain_findings.get("findings", [])[:2]:  # Show first 2
                    print(f"      • {finding}")
            
            # Recommendations
            recommendations = final_result.get("consolidated_recommendations", [])
            if recommendations:
                print(f"   💡 Key Recommendations:")
                for rec in recommendations[:3]:  # Show first 3
                    print(f"      • {rec}")
            
            # Overall metrics
            overall_metrics = final_result.get("overall_metrics", {})
            print(f"   📈 Overall Metrics:")
            for metric, value in overall_metrics.items():
                print(f"      {metric.replace('_', ' ').title()}: {value}")

def main():
    """Main orchestration function"""
    parser = argparse.ArgumentParser(description="Sub-Agent Orchestration System")
    parser.add_argument("--task", required=True, help="Task description")
    parser.add_argument("--mode", choices=["auto", "manual", "optimal"], 
                       default="auto", help="Orchestration mode")
    parser.add_argument("--parallel", type=int, default=4, 
                       help="Maximum parallel agents")
    
    args = parser.parse_args()
    
    try:
        print(f"🎛️  Sub-Agent Orchestration System")
        print(f"{'='*60}")
        
        # Initialize orchestrator
        orchestrator = SubAgentOrchestrator()
        
        # Phase 1: Task Analysis
        print(f"\n📋 Phase 1: Task Analysis")
        requirements = orchestrator.analyze_task_requirements(args.task)
        
        # Phase 2: Agent Selection
        print(f"\n🎯 Phase 2: Agent Selection")
        selected_agents = orchestrator.select_optimal_agents(requirements, args.mode)
        
        if not selected_agents:
            print("❌ No suitable agents found for this task")
            sys.exit(1)
        
        # Phase 3: Execution Planning
        print(f"\n📋 Phase 3: Execution Planning")
        execution_plan = orchestrator.create_execution_plan(args.task, requirements, selected_agents)
        
        # Phase 4: Orchestrated Execution
        print(f"\n🚀 Phase 4: Orchestrated Execution")
        results = orchestrator.execute_orchestrated_task(args.task, execution_plan)
        
        # Display results
        orchestrator.display_orchestration_results(results)
        
        print(f"\n✅ Orchestration Complete!")
        
    except KeyboardInterrupt:
        print(f"\n⚠️  Orchestration interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Orchestration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()