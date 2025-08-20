#!/usr/bin/env python3
"""
Agent Registration System for Claude Code
Automatically registers all 20+ agents with Claude Code Task system for /agent interface visibility
"""

import os
import yaml
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AgentRegistrationSystem:
    """System to register all agents with Claude Code for /agent interface visibility"""
    
    def __init__(self, agents_dir: Path, settings_file: Path):
        self.agents_dir = agents_dir
        self.settings_file = settings_file
        self.registered_agents = []
        
    def parse_agent_metadata(self, agent_file: Path) -> Optional[Dict[str, Any]]:
        """Parse YAML frontmatter from agent file"""
        try:
            with open(agent_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract YAML frontmatter
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    yaml_content = parts[1].strip()
                    metadata = yaml.safe_load(yaml_content)
                    
                    # Add file path and content for reference
                    metadata['file_path'] = str(agent_file)
                    metadata['content_length'] = len(parts[2]) if len(parts) > 2 else 0
                    
                    return metadata
            
            logger.warning(f"No YAML frontmatter found in {agent_file}")
            return None
            
        except Exception as e:
            logger.error(f"Error parsing {agent_file}: {e}")
            return None
    
    def discover_agents(self) -> List[Dict[str, Any]]:
        """Discover all agent files and parse their metadata"""
        agents = []
        
        if not self.agents_dir.exists():
            logger.error(f"Agents directory does not exist: {self.agents_dir}")
            return agents
        
        for agent_file in self.agents_dir.glob("*.md"):
            metadata = self.parse_agent_metadata(agent_file)
            if metadata:
                agents.append(metadata)
                logger.info(f"Discovered agent: {metadata.get('name', 'unknown')}")
            
        logger.info(f"Discovered {len(agents)} agents total")
        return agents
    
    def create_agent_configs(self, agents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create Claude Code agent configurations"""
        agent_configs = {}
        
        for agent in agents:
            name = agent.get('name', 'unknown')
            description = agent.get('description', 'Agent description not available')
            tools = agent.get('tools', ['Read', 'Grep', 'Glob', 'Bash', 'Task', 'LS'])
            domain = agent.get('domain', 'general')
            integration_mcps = agent.get('integration_mcps', [])
            
            # Create configuration for Claude Code Task system
            config = {
                "type": "specialized_agent",
                "name": name,
                "description": description,
                "tools": tools if isinstance(tools, list) else tools.split(', ') if isinstance(tools, str) else ['Read', 'Grep', 'Glob', 'Bash', 'Task', 'LS'],
                "domain": domain,
                "integration_mcps": integration_mcps,
                "file_path": agent['file_path'],
                "performance_profile": agent.get('performance_profile', 'balanced'),
                "security_level": agent.get('security_level', 'read-only'),
                "registered_at": datetime.now().isoformat(),
                "available": True
            }
            
            agent_configs[name] = config
        
        return agent_configs
    
    def register_with_claude_code(self, agent_configs: Dict[str, Any]) -> bool:
        """Register agents with Claude Code settings"""
        try:
            # Load existing settings
            settings = {}
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
            
            # Add or update agent registrations
            if 'agentRegistry' not in settings:
                settings['agentRegistry'] = {}
            
            settings['agentRegistry'].update(agent_configs)
            
            # Add metadata
            settings['agentRegistry']['_metadata'] = {
                "total_agents": len(agent_configs),
                "last_updated": datetime.now().isoformat(),
                "registration_system_version": "1.0.0",
                "discovery_source": str(self.agents_dir)
            }
            
            # Save updated settings
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
            
            logger.info(f"Successfully registered {len(agent_configs)} agents with Claude Code")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register agents with Claude Code: {e}")
            return False
    
    def create_agent_manifest(self, agents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a manifest file for agent discovery"""
        manifest = {
            "manifest_version": "1.0.0",
            "generated_at": datetime.now().isoformat(),
            "total_agents": len(agents),
            "agents": {
                agent['name']: {
                    "name": agent['name'],
                    "description": agent.get('description', ''),
                    "domain": agent.get('domain', 'general'),
                    "tools": agent.get('tools', []),
                    "integration_mcps": agent.get('integration_mcps', []),
                    "performance_profile": agent.get('performance_profile', 'balanced'),
                    "security_level": agent.get('security_level', 'read-only'),
                    "file_path": agent['file_path']
                } for agent in agents
            },
            "domains": list(set(agent.get('domain', 'general') for agent in agents)),
            "available_tools": list(set(
                tool for agent in agents 
                for tool in (agent.get('tools', []) if isinstance(agent.get('tools'), list) 
                           else agent.get('tools', '').split(', ') if isinstance(agent.get('tools'), str) 
                           else [])
            )),
            "integrated_mcps": list(set(
                mcp for agent in agents 
                for mcp in agent.get('integration_mcps', [])
            ))
        }
        
        return manifest
    
    def generate_registration_report(self, agents: List[Dict[str, Any]], 
                                   agent_configs: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive registration report"""
        
        # Group agents by domain
        domains = {}
        for agent in agents:
            domain = agent.get('domain', 'general')
            if domain not in domains:
                domains[domain] = []
            domains[domain].append(agent['name'])
        
        # Analyze MCP integration coverage
        mcp_usage = {}
        for agent in agents:
            for mcp in agent.get('integration_mcps', []):
                if mcp not in mcp_usage:
                    mcp_usage[mcp] = []
                mcp_usage[mcp].append(agent['name'])
        
        # Generate report
        report = {
            "registration_summary": {
                "total_agents_discovered": len(agents),
                "total_agents_registered": len(agent_configs),
                "registration_success_rate": f"{(len(agent_configs)/len(agents)*100):.1f}%" if agents else "0%",
                "timestamp": datetime.now().isoformat()
            },
            "domain_distribution": {
                domain: {
                    "agent_count": len(agent_list),
                    "agents": agent_list
                } for domain, agent_list in domains.items()
            },
            "mcp_integration_analysis": {
                "total_mcps_used": len(mcp_usage),
                "mcp_usage_details": {
                    mcp: {
                        "agent_count": len(agent_list),
                        "agents": agent_list
                    } for mcp, agent_list in mcp_usage.items()
                }
            },
            "tool_analysis": {
                "unique_tools": list(set(
                    tool for agent in agents 
                    for tool in (agent.get('tools', []) if isinstance(agent.get('tools'), list) 
                               else agent.get('tools', '').split(', ') if isinstance(agent.get('tools'), str) 
                               else [])
                )),
                "tool_coverage": "Standard Claude Code tools + MCP extensions"
            },
            "recommendations": [
                f"Successfully registered {len(agent_configs)} agents for /agent interface visibility",
                f"Agents span {len(domains)} specialized domains for comprehensive coverage",
                f"{len(mcp_usage)} custom MCP servers integrated across agent ecosystem",
                "All agents now discoverable through /agent interface in Claude Code",
                "Multi-agent workflows can leverage specialized agent capabilities"
            ]
        }
        
        return report
    
    def run_registration(self) -> Dict[str, Any]:
        """Run complete agent registration process"""
        logger.info("Starting agent registration process...")
        
        # Discover agents
        agents = self.discover_agents()
        if not agents:
            logger.error("No agents discovered. Registration failed.")
            return {"success": False, "error": "No agents found"}
        
        # Create agent configurations
        agent_configs = self.create_agent_configs(agents)
        
        # Register with Claude Code
        registration_success = self.register_with_claude_code(agent_configs)
        
        # Create manifest
        manifest = self.create_agent_manifest(agents)
        manifest_path = self.agents_dir.parent / 'agent_manifest.json'
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        # Generate report
        report = self.generate_registration_report(agents, agent_configs)
        report_path = self.agents_dir.parent / 'agent_registration_report.json'
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Registration process completed. Success: {registration_success}")
        
        return {
            "success": registration_success,
            "agents_discovered": len(agents),
            "agents_registered": len(agent_configs),
            "manifest_path": str(manifest_path),
            "report_path": str(report_path),
            "report": report
        }

def main():
    """Main entry point for agent registration"""
    
    # Paths
    base_dir = Path(__file__).parent.parent
    agents_dir = base_dir / 'agents'
    settings_file = base_dir / 'settings.json'
    
    # Create registration system
    registration_system = AgentRegistrationSystem(agents_dir, settings_file)
    
    # Run registration
    result = registration_system.run_registration()
    
    if result['success']:
        print("🎉 Agent Registration Completed Successfully!")
        print(f"✅ Discovered: {result['agents_discovered']} agents")
        print(f"✅ Registered: {result['agents_registered']} agents")
        print(f"📋 Manifest: {result['manifest_path']}")
        print(f"📊 Report: {result['report_path']}")
        print("\n🚀 All agents are now visible in /agent interface!")
    else:
        print("❌ Agent Registration Failed")
        if 'error' in result:
            print(f"Error: {result['error']}")
    
    return result

if __name__ == "__main__":
    main()