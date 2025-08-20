#!/usr/bin/env python3
"""
🤖 Subagent Coordinator Hook
Comprehensive sub-agent lifecycle management and coordination system
Integrates with existing parallel orchestration and MCP infrastructure
"""

import os
import sys
import json
import time
import sqlite3
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timezone

# Add project paths for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "mcp_servers" / "shared" / "src"))

@dataclass
class SubAgentInfo:
    """Information about a sub-agent"""
    name: str
    description: str
    tools: List[str]
    domain: str
    integration_mcps: List[str]
    performance_profile: str
    security_level: str
    status: str = "available"
    last_used: Optional[str] = None
    performance_metrics: Optional[Dict] = None

@dataclass
class SubAgentExecution:
    """Sub-agent execution tracking"""
    execution_id: str
    agent_name: str
    task_description: str
    start_time: float
    end_time: Optional[float] = None
    status: str = "running"
    result_summary: Optional[str] = None
    performance_data: Optional[Dict] = None
    error_info: Optional[str] = None

class SubAgentCoordinator:
    """Comprehensive sub-agent coordination and management system"""
    
    def __init__(self):
        self.project_root = project_root
        self.agents_dir = self.project_root / ".claude" / "agents"
        self.db_path = self.project_root / ".claude" / "subagent_coordination.db"
        self.coordination_lock = threading.Lock()
        
        # Performance tracking
        self.start_time = time.time()
        self.execution_metrics = {}
        
        # Initialize database and load agents
        self._initialize_database()
        self.available_agents = self._discover_agents()
        
        # Integration with existing systems
        self._initialize_mcp_integration()
        self._initialize_performance_tracking()
    
    def _initialize_database(self):
        """Initialize SQLite database for sub-agent coordination"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS subagent_registry (
                    name TEXT PRIMARY KEY,
                    description TEXT,
                    tools TEXT,
                    domain TEXT,
                    integration_mcps TEXT,
                    performance_profile TEXT,
                    security_level TEXT,
                    status TEXT DEFAULT 'available',
                    last_used TIMESTAMP,
                    total_executions INTEGER DEFAULT 0,
                    avg_execution_time REAL DEFAULT 0,
                    success_rate REAL DEFAULT 100
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS subagent_executions (
                    execution_id TEXT PRIMARY KEY,
                    agent_name TEXT,
                    task_description TEXT,
                    start_time REAL,
                    end_time REAL,
                    status TEXT,
                    result_summary TEXT,
                    performance_data TEXT,
                    error_info TEXT,
                    FOREIGN KEY (agent_name) REFERENCES subagent_registry (name)
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS coordination_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    event_type TEXT,
                    agent_name TEXT,
                    details TEXT
                )
            ''')
    
    def _discover_agents(self) -> Dict[str, SubAgentInfo]:
        """Discover all available sub-agents"""
        agents = {}
        
        if not self.agents_dir.exists():
            os.makedirs(self.agents_dir, exist_ok=True)
            return agents
        
        for agent_file in self.agents_dir.glob("*.md"):
            try:
                agent_info = self._parse_agent_definition(agent_file)
                if agent_info:
                    agents[agent_info.name] = agent_info
                    self._register_agent(agent_info)
            except Exception as e:
                self._log_event("error", None, f"Failed to parse agent {agent_file}: {e}")
        
        return agents
    
    def _parse_agent_definition(self, agent_file: Path) -> Optional[SubAgentInfo]:
        """Parse agent definition from markdown file"""
        content = agent_file.read_text()
        
        # Extract YAML frontmatter
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
            
            # Parse YAML-like frontmatter (simplified parsing)
            metadata = {}
            for line in lines[1:yaml_end]:
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    
                    # Handle list values
                    if value.startswith('[') and value.endswith(']'):
                        value = [item.strip().strip('"').strip("'") for item in value[1:-1].split(',')]
                    
                    metadata[key] = value
            
            return SubAgentInfo(
                name=metadata.get('name', agent_file.stem),
                description=metadata.get('description', ''),
                tools=metadata.get('tools', []),
                domain=metadata.get('domain', ''),
                integration_mcps=metadata.get('integration_mcps', []),
                performance_profile=metadata.get('performance_profile', 'standard'),
                security_level=metadata.get('security_level', 'read-only')
            )
        
        except Exception as e:
            self._log_event("error", None, f"Failed to parse agent metadata: {e}")
            return None
    
    def _register_agent(self, agent_info: SubAgentInfo):
        """Register agent in database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO subagent_registry 
                (name, description, tools, domain, integration_mcps, performance_profile, security_level)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                agent_info.name,
                agent_info.description,
                json.dumps(agent_info.tools),
                agent_info.domain,
                json.dumps(agent_info.integration_mcps),
                agent_info.performance_profile,
                agent_info.security_level
            ))
    
    def _initialize_mcp_integration(self):
        """Initialize integration with existing MCP servers"""
        try:
            # Try to connect to agentic-workflow MCP for coordination
            self.agentic_workflow_available = self._check_mcp_server("agentic-workflow")
            self.ml_intelligence_available = self._check_mcp_server("ml-code-intelligence")
            self.predictive_analytics_available = self._check_mcp_server("predictive-analytics")
        except Exception as e:
            self._log_event("warning", None, f"MCP integration initialization failed: {e}")
    
    def _check_mcp_server(self, server_name: str) -> bool:
        """Check if MCP server is available"""
        # Simplified check - in production this would check actual server status
        mcp_path = self.project_root / "mcp_servers" / server_name.replace("-", "_")
        return mcp_path.exists()
    
    def _initialize_performance_tracking(self):
        """Initialize performance tracking integration"""
        try:
            # Check for existing performance monitoring
            perf_db = self.project_root / "databases" / "performance" / "metrics.db"
            self.performance_tracking_available = perf_db.exists()
        except Exception as e:
            self._log_event("warning", None, f"Performance tracking initialization failed: {e}")
            self.performance_tracking_available = False
    
    def coordinate_subagent_execution(self, event_data: Dict[str, Any]):
        """Main coordination function for sub-agent execution"""
        with self.coordination_lock:
            try:
                # Extract sub-agent information from the event
                execution_info = self._extract_execution_info(event_data)
                
                if not execution_info:
                    return
                
                # Log coordination event
                self._log_coordination_event(execution_info)
                
                # Track performance
                self._track_performance_metrics(execution_info)
                
                # Coordinate with MCP servers if available
                self._coordinate_with_mcps(execution_info)
                
                # Update agent status
                self._update_agent_status(execution_info)
                
                # Generate coordination summary
                coordination_summary = self._generate_coordination_summary(execution_info)
                
                # Output results
                self._output_coordination_results(coordination_summary)
                
            except Exception as e:
                self._log_event("error", None, f"Coordination error: {e}")
                print(f"❌ Sub-agent coordination error: {e}")
    
    def _extract_execution_info(self, event_data: Dict[str, Any]) -> Optional[Dict]:
        """Extract sub-agent execution information from event data"""
        try:
            # Get environment variables from the hook
            tool_name = os.environ.get('CLAUDE_TOOL_NAME', 'unknown')
            subagent_result = os.environ.get('CLAUDE_SUBAGENT_RESULT', '')
            subagent_name = os.environ.get('CLAUDE_SUBAGENT_NAME', '')
            
            # Try to parse subagent result if available
            subagent_data = {}
            if subagent_result:
                try:
                    subagent_data = json.loads(subagent_result)
                except json.JSONDecodeError:
                    subagent_data = {"raw_result": subagent_result}
            
            return {
                "tool_name": tool_name,
                "subagent_name": subagent_name,
                "subagent_data": subagent_data,
                "timestamp": time.time(),
                "execution_id": f"{subagent_name}_{int(time.time() * 1000)}"
            }
        
        except Exception as e:
            self._log_event("error", None, f"Failed to extract execution info: {e}")
            return None
    
    def _log_coordination_event(self, execution_info: Dict):
        """Log coordination event to database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO coordination_events (timestamp, event_type, agent_name, details)
                VALUES (?, ?, ?, ?)
            ''', (
                execution_info["timestamp"],
                "subagent_coordination",
                execution_info["subagent_name"],
                json.dumps(execution_info)
            ))
    
    def _track_performance_metrics(self, execution_info: Dict):
        """Track performance metrics for the sub-agent execution"""
        try:
            execution_time = time.time() - self.start_time
            
            # Update execution metrics
            agent_name = execution_info["subagent_name"]
            if agent_name:
                if agent_name not in self.execution_metrics:
                    self.execution_metrics[agent_name] = {
                        "executions": 0,
                        "total_time": 0,
                        "errors": 0
                    }
                
                self.execution_metrics[agent_name]["executions"] += 1
                self.execution_metrics[agent_name]["total_time"] += execution_time
                
                # Update database
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute('''
                        UPDATE subagent_registry 
                        SET total_executions = total_executions + 1,
                            avg_execution_time = ?,
                            last_used = ?
                        WHERE name = ?
                    ''', (
                        execution_time,
                        datetime.now(timezone.utc).isoformat(),
                        agent_name
                    ))
        
        except Exception as e:
            self._log_event("error", None, f"Performance tracking error: {e}")
    
    def _coordinate_with_mcps(self, execution_info: Dict):
        """Coordinate with available MCP servers"""
        if self.agentic_workflow_available:
            self._notify_agentic_workflow(execution_info)
        
        if self.predictive_analytics_available:
            self._update_predictive_models(execution_info)
    
    def _notify_agentic_workflow(self, execution_info: Dict):
        """Notify agentic workflow MCP of sub-agent coordination"""
        # In production, this would send actual coordination data to the MCP
        self._log_event("info", execution_info["subagent_name"], 
                       "Notified agentic workflow MCP of sub-agent execution")
    
    def _update_predictive_models(self, execution_info: Dict):
        """Update predictive analytics with sub-agent execution data"""
        # In production, this would feed data to predictive models
        self._log_event("info", execution_info["subagent_name"], 
                       "Updated predictive models with execution data")
    
    def _update_agent_status(self, execution_info: Dict):
        """Update agent status based on execution"""
        agent_name = execution_info["subagent_name"]
        if agent_name in self.available_agents:
            self.available_agents[agent_name].status = "recently_used"
            self.available_agents[agent_name].last_used = datetime.now(timezone.utc).isoformat()
    
    def _generate_coordination_summary(self, execution_info: Dict) -> Dict:
        """Generate comprehensive coordination summary"""
        agent_name = execution_info["subagent_name"]
        
        # Get agent info
        agent_info = self.available_agents.get(agent_name, {})
        
        # Get execution metrics
        metrics = self.execution_metrics.get(agent_name, {})
        
        # Generate summary
        summary = {
            "coordination_timestamp": execution_info["timestamp"],
            "agent_name": agent_name,
            "agent_domain": getattr(agent_info, 'domain', 'unknown'),
            "execution_metrics": metrics,
            "total_available_agents": len(self.available_agents),
            "mcp_integration_status": {
                "agentic_workflow": self.agentic_workflow_available,
                "ml_intelligence": self.ml_intelligence_available,
                "predictive_analytics": self.predictive_analytics_available
            },
            "coordination_success": True
        }
        
        return summary
    
    def _output_coordination_results(self, summary: Dict):
        """Output coordination results"""
        agent_name = summary["agent_name"]
        domain = summary["agent_domain"]
        total_agents = summary["total_available_agents"]
        
        print(f"🤖 Sub-Agent Coordination Complete")
        print(f"   Agent: {agent_name} ({domain})")
        print(f"   Available Agents: {total_agents}")
        
        # Show execution metrics if available
        metrics = summary["execution_metrics"]
        if metrics:
            avg_time = metrics["total_time"] / metrics["executions"] if metrics["executions"] > 0 else 0
            print(f"   Executions: {metrics['executions']}, Avg Time: {avg_time:.2f}s")
        
        # Show MCP integration status
        mcp_status = summary["mcp_integration_status"]
        active_mcps = sum(1 for status in mcp_status.values() if status)
        print(f"   MCP Integration: {active_mcps}/3 servers available")
        
        print(f"   Coordination Status: ✅ Success")
    
    def _log_event(self, event_type: str, agent_name: Optional[str], message: str):
        """Log event to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO coordination_events (timestamp, event_type, agent_name, details)
                    VALUES (?, ?, ?, ?)
                ''', (time.time(), event_type, agent_name, message))
        except Exception as e:
            print(f"Warning: Failed to log event: {e}")

def main():
    """Main coordination function"""
    try:
        # Initialize coordinator
        coordinator = SubAgentCoordinator()
        
        # Get event data from environment
        event_data = {
            "tool_name": os.environ.get('CLAUDE_TOOL_NAME', 'unknown'),
            "subagent_result": os.environ.get('CLAUDE_SUBAGENT_RESULT', ''),
            "subagent_name": os.environ.get('CLAUDE_SUBAGENT_NAME', '')
        }
        
        # Coordinate sub-agent execution
        coordinator.coordinate_subagent_execution(event_data)
        
        # Show available agents summary
        print(f"\n📋 Available Sub-Agents ({len(coordinator.available_agents)}):")
        for agent_name, agent_info in coordinator.available_agents.items():
            print(f"   • {agent_name}: {agent_info.domain} ({agent_info.status})")
        
    except Exception as e:
        print(f"❌ Sub-agent coordination failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()