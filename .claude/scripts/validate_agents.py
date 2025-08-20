#!/usr/bin/env python3
"""
Agent Validation and Registration System
Validates all agents in .claude/agents/ directory and ensures proper YAML frontmatter
"""

import os
import re
import yaml
from pathlib import Path

def validate_agent_file(agent_path):
    """Validate a single agent file for proper structure"""
    try:
        with open(agent_path, 'r') as f:
            content = f.read()
        
        # Check for YAML frontmatter
        yaml_match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
        if not yaml_match:
            return False, "No YAML frontmatter found"
        
        # Parse YAML
        yaml_content = yaml_match.group(1)
        try:
            metadata = yaml.safe_load(yaml_content)
        except yaml.YAMLError as e:
            return False, f"Invalid YAML: {e}"
        
        # Check required fields
        required_fields = ['name', 'description']
        for field in required_fields:
            if field not in metadata:
                return False, f"Missing required field: {field}"
        
        # Validate name format (lowercase, hyphens)
        name = metadata['name']
        if not re.match(r'^[a-z0-9-]+$', name):
            return False, f"Invalid name format: {name}. Use lowercase letters, numbers, and hyphens only"
        
        return True, "Valid agent file"
        
    except Exception as e:
        return False, f"Error reading file: {e}"

def validate_all_agents(agents_dir):
    """Validate all agent files in the directory"""
    agents_dir = Path(agents_dir)
    if not agents_dir.exists():
        print(f"❌ Agents directory not found: {agents_dir}")
        return
    
    print(f"🔍 Validating agents in: {agents_dir}")
    print("=" * 60)
    
    valid_agents = []
    invalid_agents = []
    
    for agent_file in agents_dir.glob("*.md"):
        is_valid, message = validate_agent_file(agent_file)
        
        if is_valid:
            print(f"✅ {agent_file.name}: {message}")
            valid_agents.append(agent_file.name)
        else:
            print(f"❌ {agent_file.name}: {message}")
            invalid_agents.append((agent_file.name, message))
    
    print("=" * 60)
    print(f"📊 Summary: {len(valid_agents)} valid, {len(invalid_agents)} invalid")
    
    if invalid_agents:
        print("\n❌ Invalid Agents:")
        for agent, error in invalid_agents:
            print(f"  - {agent}: {error}")
    
    if valid_agents:
        print(f"\n✅ Valid Agents ({len(valid_agents)}):")
        for agent in valid_agents:
            print(f"  - {agent}")
    
    return valid_agents, invalid_agents

def fix_agent_frontmatter(agent_path):
    """Fix common issues with agent frontmatter"""
    try:
        with open(agent_path, 'r') as f:
            content = f.read()
        
        # Check if it already has proper frontmatter
        if re.match(r'^---\n.*?name:.*?\n.*?description:.*?\n---\n', content, re.DOTALL):
            print(f"✅ {agent_path.name} already has proper frontmatter")
            return True
        
        # Extract filename as name
        name = agent_path.stem
        
        # Create minimal frontmatter
        frontmatter = f"""---
name: {name}
description: Specialized agent for {name.replace('-', ' ').title()}
---

"""
        
        # Add frontmatter to beginning
        new_content = frontmatter + content
        
        # Backup original
        backup_path = agent_path.with_suffix('.md.backup')
        with open(backup_path, 'w') as f:
            f.write(content)
        
        # Write new content
        with open(agent_path, 'w') as f:
            f.write(new_content)
        
        print(f"🔧 Fixed frontmatter for {agent_path.name} (backup: {backup_path.name})")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing {agent_path.name}: {e}")
        return False

def main():
    """Main validation and fixing routine"""
    script_dir = Path(__file__).parent
    agents_dir = script_dir.parent / "agents"
    
    print("🤖 10X Agentic Setup - Agent Validation System")
    print("=" * 60)
    
    # First validation pass
    valid_agents, invalid_agents = validate_all_agents(agents_dir)
    
    # Try to fix invalid agents
    if invalid_agents:
        print(f"\n🔧 Attempting to fix {len(invalid_agents)} invalid agents...")
        for agent_name, error in invalid_agents:
            agent_path = agents_dir / agent_name
            fix_agent_frontmatter(agent_path)
        
        # Re-validate after fixes
        print(f"\n🔄 Re-validating after fixes...")
        valid_agents, invalid_agents = validate_all_agents(agents_dir)
    
    # Generate agent registry report
    if valid_agents:
        registry_path = script_dir.parent / "agent_registry_report.md"
        generate_registry_report(agents_dir, valid_agents, registry_path)
    
    print(f"\n{'🎉' if not invalid_agents else '⚠️'} Validation complete!")

def generate_registry_report(agents_dir, valid_agents, output_path):
    """Generate a registry report of all valid agents"""
    agents_dir = Path(agents_dir)
    
    report = "# Agent Registry Report\n\n"
    report += f"Generated: {os.popen('date').read().strip()}\n"
    report += f"Total Valid Agents: {len(valid_agents)}\n\n"
    
    report += "## Registered Agents\n\n"
    
    for agent_file in valid_agents:
        agent_path = agents_dir / agent_file
        try:
            with open(agent_path, 'r') as f:
                content = f.read()
            
            # Extract metadata
            yaml_match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
            if yaml_match:
                metadata = yaml.safe_load(yaml_match.group(1))
                name = metadata.get('name', 'Unknown')
                description = metadata.get('description', 'No description')
                tools = metadata.get('tools', 'Inherited')
                
                report += f"### {name}\n"
                report += f"**Description**: {description}\n\n"
                report += f"**Tools**: {tools}\n\n"
                report += f"**File**: `{agent_file}`\n\n"
                report += "---\n\n"
        
        except Exception as e:
            report += f"### {agent_file}\n"
            report += f"**Error**: Could not parse metadata - {e}\n\n"
            report += "---\n\n"
    
    with open(output_path, 'w') as f:
        f.write(report)
    
    print(f"📄 Registry report generated: {output_path}")

if __name__ == "__main__":
    main()