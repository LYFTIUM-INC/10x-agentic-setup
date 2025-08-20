#!/usr/bin/env python3
"""
Smart Command Orchestrator
=========================

Intelligent assistant for optimal 10X Command Selection and Claude Flow execution.
Analyzes user requests and generates the exact command needed from 42+ specialized agents.

Features:
- Natural language processing for user requests
- Complexity assessment and mode selection
- Intelligent command generation
- Workflow optimization recommendations
- Integration with Claude Flow and 10X Agentic Setup

Usage:
    python smart_command_orchestrator.py "Build a user authentication system"
    python smart_command_orchestrator.py --interactive
    python smart_command_orchestrator.py --analyze "Create REST API"

Author: 10X Agentic Setup Team
License: MIT
"""

import sys
import re
import json
import argparse
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class ComplexityLevel(Enum):
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    ENTERPRISE = "enterprise"


class ExecutionMode(Enum):
    SWARM = "swarm"
    HIVE_MIND = "hive-mind"
    TEN_X_COMMANDS = "10x-commands"
    HYBRID = "hybrid"


@dataclass
class TaskAnalysis:
    complexity: ComplexityLevel
    estimated_time: str
    execution_mode: ExecutionMode
    required_agents: List[str]
    prerequisites: List[str]
    follow_up_actions: List[str]


@dataclass
class CommandRecommendation:
    primary_commands: List[str]
    setup_instructions: List[str]
    execution_strategy: str
    success_metrics: List[str]


class SmartCommandOrchestrator:
    """
    Intelligent command orchestrator for Claude Flow and 10X Agentic Setup.
    
    This class analyzes user requests, assesses complexity, and generates
    optimal command recommendations with execution strategies.
    """
    
    def __init__(self):
        self.complexity_patterns = {
            ComplexityLevel.SIMPLE: [
                r'\b(fix|bug|small|quick|simple|single)\b',
                r'\b(css|style|typo|minor)\b',
                r'\b(one|small|tiny|brief)\b'
            ],
            ComplexityLevel.MODERATE: [
                r'\b(feature|enhance|add|create|build)\b',
                r'\b(api|endpoint|component|function)\b',
                r'\b(integrate|connect|link)\b'
            ],
            ComplexityLevel.COMPLEX: [
                r'\b(system|architecture|full|complete|comprehensive)\b',
                r'\b(authentication|security|database|backend)\b',
                r'\b(application|platform|service|dashboard)\b'
            ],
            ComplexityLevel.ENTERPRISE: [
                r'\b(enterprise|scalable|production|microservice)\b',
                r'\b(migration|refactor|infrastructure|deployment)\b',
                r'\b(multi\-\w+|distributed|cluster|pipeline)\b'
            ]
        }
        
        self.command_mappings = {
            'authentication': {
                'complexity': ComplexityLevel.COMPLEX,
                'commands': [
                    'npx claude-flow@alpha hive-mind --project "auth_system"',
                    '/intelligence:gather_insights_10x --technical "JWT authentication patterns"',
                    '/implement_10x --feature "JWT authentication system" --full',
                    '/qa:comprehensive_10x --focus security'
                ]
            },
            'api': {
                'complexity': ComplexityLevel.MODERATE,
                'commands': [
                    'npx claude-flow@alpha swarm "create REST API endpoint"',
                    '/qa:smart_test_generator_10x --focus "API testing"'
                ]
            },
            'bug_fix': {
                'complexity': ComplexityLevel.SIMPLE,
                'commands': [
                    'npx claude-flow@alpha swarm "fix bug in component"'
                ]
            },
            'performance': {
                'complexity': ComplexityLevel.MODERATE,
                'commands': [
                    '/intelligence:gather_insights_10x --technical "performance optimization"',
                    '/analyze_10x --mode deep --focus "performance"',
                    'npx claude-flow@alpha swarm "optimize performance bottlenecks"'
                ]
            },
            'full_application': {
                'complexity': ComplexityLevel.COMPLEX,
                'commands': [
                    'npx claude-flow@alpha hive-mind --project "webapp_development"',
                    '/intelligence:gather_insights_10x --full "modern web application"',
                    '/implement_10x --feature "full-stack application" --full'
                ]
            }
        }
    
    def analyze_request(self, user_request: str) -> TaskAnalysis:
        """
        Analyze user request to determine complexity, execution mode, and requirements.
        
        Args:
            user_request: Natural language description of what user wants to build
            
        Returns:
            TaskAnalysis object with complexity assessment and recommendations
        """
        complexity = self._assess_complexity(user_request)
        execution_mode = self._determine_execution_mode(complexity, user_request)
        
        # Estimate time based on complexity
        time_estimates = {
            ComplexityLevel.SIMPLE: "5-20 minutes",
            ComplexityLevel.MODERATE: "20-60 minutes", 
            ComplexityLevel.COMPLEX: "1-3 hours",
            ComplexityLevel.ENTERPRISE: "Multiple days"
        }
        
        # Determine required agents
        required_agents = self._identify_required_agents(user_request, complexity)
        
        # Generate prerequisites and follow-up actions
        prerequisites = self._generate_prerequisites(user_request, complexity)
        follow_up_actions = self._generate_follow_up_actions(user_request, complexity)
        
        return TaskAnalysis(
            complexity=complexity,
            estimated_time=time_estimates[complexity],
            execution_mode=execution_mode,
            required_agents=required_agents,
            prerequisites=prerequisites,
            follow_up_actions=follow_up_actions
        )
    
    def generate_commands(self, user_request: str, analysis: TaskAnalysis) -> CommandRecommendation:
        """
        Generate specific command recommendations based on analysis.
        
        Args:
            user_request: Original user request
            analysis: TaskAnalysis from analyze_request
            
        Returns:
            CommandRecommendation with specific commands and strategies
        """
        # Identify the best matching command pattern
        command_type = self._identify_command_type(user_request)
        
        if command_type in self.command_mappings:
            base_commands = self.command_mappings[command_type]['commands']
        else:
            base_commands = self._generate_generic_commands(analysis)
        
        # Customize commands based on analysis
        customized_commands = self._customize_commands(base_commands, user_request, analysis)
        
        # Generate setup instructions
        setup_instructions = self._generate_setup_instructions(analysis)
        
        # Create execution strategy
        execution_strategy = self._create_execution_strategy(analysis)
        
        # Define success metrics
        success_metrics = self._define_success_metrics(analysis)
        
        return CommandRecommendation(
            primary_commands=customized_commands,
            setup_instructions=setup_instructions,
            execution_strategy=execution_strategy,
            success_metrics=success_metrics
        )
    
    def format_response(self, user_request: str, analysis: TaskAnalysis, 
                       recommendation: CommandRecommendation) -> str:
        """
        Format the complete response for the user.
        
        Args:
            user_request: Original user request
            analysis: TaskAnalysis object
            recommendation: CommandRecommendation object
            
        Returns:
            Formatted string response ready for display
        """
        response = []
        response.append("# 🧠 Smart Command Orchestrator Analysis")
        response.append("")
        response.append(f"**Your Request:** {user_request}")
        response.append("")
        
        # Analysis section
        response.append("## 🔍 Analysis")
        response.append(f"- **Complexity:** {analysis.complexity.value.title()}")
        response.append(f"- **Estimated Time:** {analysis.estimated_time}")
        response.append(f"- **Execution Mode:** {analysis.execution_mode.value}")
        response.append(f"- **Required Agents:** {', '.join(analysis.required_agents)}")
        response.append("")
        
        # Command recommendations
        response.append("## 📋 Recommended Commands")
        response.append("```bash")
        for cmd in recommendation.primary_commands:
            response.append(cmd)
        response.append("```")
        response.append("")
        
        # Setup instructions
        if recommendation.setup_instructions:
            response.append("## 🔧 Setup Instructions")
            for instruction in recommendation.setup_instructions:
                response.append(f"- {instruction}")
            response.append("")
        
        # Execution strategy
        response.append("## ⚡ Execution Strategy")
        response.append(recommendation.execution_strategy)
        response.append("")
        
        # Prerequisites
        if analysis.prerequisites:
            response.append("## 📋 Prerequisites")
            for prereq in analysis.prerequisites:
                response.append(f"- {prereq}")
            response.append("")
        
        # Follow-up actions
        if analysis.follow_up_actions:
            response.append("## 🔄 Follow-up Actions")
            for action in analysis.follow_up_actions:
                response.append(f"- {action}")
            response.append("")
        
        # Success metrics
        response.append("## 🎯 Success Metrics")
        for metric in recommendation.success_metrics:
            response.append(f"- {metric}")
        
        return "\n".join(response)
    
    def interactive_mode(self):
        """Run the orchestrator in interactive mode."""
        print("🧠 Smart Command Orchestrator - Interactive Mode")
        print("=" * 50)
        print("Tell me what you want to build, and I'll recommend the optimal commands!")
        print("Type 'exit' to quit, 'help' for examples.")
        print()
        
        while True:
            try:
                user_input = input("🎯 What would you like to build? ").strip()
                
                if user_input.lower() in ['exit', 'quit', 'q']:
                    print("👋 Happy coding! See you next time!")
                    break
                    
                if user_input.lower() == 'help':
                    self._show_examples()
                    continue
                    
                if not user_input:
                    print("Please describe what you'd like to build.")
                    continue
                
                # Process the request
                analysis = self.analyze_request(user_input)
                recommendation = self.generate_commands(user_input, analysis)
                response = self.format_response(user_input, analysis, recommendation)
                
                print("\n" + response + "\n")
                print("-" * 50)
                
            except KeyboardInterrupt:
                print("\n👋 Happy coding! See you next time!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def _assess_complexity(self, request: str) -> ComplexityLevel:
        """Assess the complexity level of the user request."""
        request_lower = request.lower()
        
        # Score each complexity level
        scores = {}
        for complexity, patterns in self.complexity_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, request_lower))
                score += matches
            scores[complexity] = score
        
        # Return the complexity with highest score, default to moderate
        if not any(scores.values()):
            return ComplexityLevel.MODERATE
            
        return max(scores.items(), key=lambda x: x[1])[0]
    
    def _determine_execution_mode(self, complexity: ComplexityLevel, request: str) -> ExecutionMode:
        """Determine the optimal execution mode based on complexity."""
        if complexity == ComplexityLevel.SIMPLE:
            return ExecutionMode.SWARM
        elif complexity == ComplexityLevel.MODERATE:
            # Check if it's more analysis-focused or implementation-focused
            if any(word in request.lower() for word in ['analyze', 'review', 'audit']):
                return ExecutionMode.TEN_X_COMMANDS
            return ExecutionMode.SWARM
        elif complexity == ComplexityLevel.COMPLEX:
            return ExecutionMode.HIVE_MIND
        else:  # ENTERPRISE
            return ExecutionMode.HYBRID
    
    def _identify_required_agents(self, request: str, complexity: ComplexityLevel) -> List[str]:
        """Identify which agents are likely needed for this request."""
        agents = []
        request_lower = request.lower()
        
        # Map keywords to required agents
        agent_keywords = {
            'architect': ['architecture', 'design', 'system', 'structure'],
            'coder': ['implement', 'build', 'create', 'develop', 'code'],
            'tester': ['test', 'testing', 'quality', 'bug', 'validation'],
            'devops': ['deploy', 'infrastructure', 'ci/cd', 'pipeline', 'docker'],
            'security': ['security', 'authentication', 'authorization', 'audit'],
            'queen': ['coordinate', 'orchestrate', 'manage', 'complex']
        }
        
        for agent, keywords in agent_keywords.items():
            if any(keyword in request_lower for keyword in keywords):
                agents.append(agent)
        
        # Ensure we have at least basic agents for complex tasks
        if complexity in [ComplexityLevel.COMPLEX, ComplexityLevel.ENTERPRISE]:
            if 'queen' not in agents:
                agents.append('queen')
            if 'architect' not in agents:
                agents.append('architect')
        
        return agents if agents else ['queen', 'coder']
    
    def _identify_command_type(self, request: str) -> str:
        """Identify the type of command pattern that best matches the request."""
        request_lower = request.lower()
        
        # Keyword mapping to command types
        type_keywords = {
            'authentication': ['auth', 'login', 'jwt', 'token', 'user management'],
            'api': ['api', 'endpoint', 'rest', 'service'],
            'bug_fix': ['bug', 'fix', 'error', 'issue', 'problem'],
            'performance': ['performance', 'optimize', 'speed', 'slow', 'bottleneck'],
            'full_application': ['application', 'app', 'full-stack', 'complete', 'comprehensive']
        }
        
        for cmd_type, keywords in type_keywords.items():
            if any(keyword in request_lower for keyword in keywords):
                return cmd_type
        
        return 'generic'
    
    def _generate_generic_commands(self, analysis: TaskAnalysis) -> List[str]:
        """Generate generic commands based on analysis when no specific pattern matches."""
        commands = []
        
        if analysis.execution_mode == ExecutionMode.SWARM:
            commands.append('npx claude-flow@alpha swarm "[describe your specific task]"')
        elif analysis.execution_mode == ExecutionMode.HIVE_MIND:
            commands.extend([
                'npx claude-flow@alpha hive-mind --project "[project_name]"',
                '/intelligence:gather_insights_10x --full "[domain]"',
                '/implement_10x --feature "[feature_name]" --full'
            ])
        elif analysis.execution_mode == ExecutionMode.TEN_X_COMMANDS:
            commands.extend([
                '/analyze_10x --mode deep',
                '/qa:comprehensive_10x --all'
            ])
        
        return commands
    
    def _customize_commands(self, base_commands: List[str], request: str, 
                          analysis: TaskAnalysis) -> List[str]:
        """Customize base commands with specific details from the request."""
        customized = []
        
        for cmd in base_commands:
            # Replace placeholders with extracted information
            customized_cmd = cmd
            
            # Extract project/feature names from request
            if '[project_name]' in cmd or '[feature_name]' in cmd:
                # Simple extraction - could be enhanced with NLP
                words = request.lower().split()
                feature_words = [w for w in words if w.isalpha() and len(w) > 3]
                if feature_words:
                    project_name = '_'.join(feature_words[:2])
                    customized_cmd = customized_cmd.replace('[project_name]', project_name)
                    customized_cmd = customized_cmd.replace('[feature_name]', project_name)
            
            customized.append(customized_cmd)
        
        return customized
    
    def _generate_prerequisites(self, request: str, complexity: ComplexityLevel) -> List[str]:
        """Generate prerequisites based on the request and complexity."""
        prerequisites = []
        request_lower = request.lower()
        
        # Common prerequisites
        if complexity in [ComplexityLevel.COMPLEX, ComplexityLevel.ENTERPRISE]:
            prerequisites.append("Ensure Claude Flow is installed: npm install -g @anthropic-ai/claude-code")
            prerequisites.append("Verify MCP servers are running")
        
        # Specific prerequisites based on content
        if any(word in request_lower for word in ['database', 'sql', 'postgres', 'mysql']):
            prerequisites.append("Database system should be installed and running")
        
        if any(word in request_lower for word in ['docker', 'container']):
            prerequisites.append("Docker should be installed and running")
        
        if any(word in request_lower for word in ['security', 'auth']):
            prerequisites.append("Review security requirements and compliance needs")
        
        return prerequisites
    
    def _generate_follow_up_actions(self, request: str, complexity: ComplexityLevel) -> List[str]:
        """Generate follow-up actions based on the request."""
        actions = []
        request_lower = request.lower()
        
        # Always recommend testing for moderate+ complexity
        if complexity != ComplexityLevel.SIMPLE:
            actions.append("Run comprehensive tests with /qa:comprehensive_10x --all")
        
        # Security audit for sensitive features
        if any(word in request_lower for word in ['auth', 'user', 'security', 'payment']):
            actions.append("Perform security audit with /qa:comprehensive_10x --focus security")
        
        # Performance testing for performance-related requests
        if any(word in request_lower for word in ['performance', 'speed', 'optimize']):
            actions.append("Validate performance improvements with benchmarks")
        
        # Documentation for complex features
        if complexity in [ComplexityLevel.COMPLEX, ComplexityLevel.ENTERPRISE]:
            actions.append("Generate documentation with /docs:generate_docs_10x")
        
        actions.append("Commit changes with /git:smart_commit_10x")
        
        return actions
    
    def _generate_setup_instructions(self, analysis: TaskAnalysis) -> List[str]:
        """Generate setup instructions based on analysis."""
        instructions = []
        
        if analysis.execution_mode in [ExecutionMode.HIVE_MIND, ExecutionMode.HYBRID]:
            instructions.append("Initialize Claude Flow if not done: npx claude-flow@alpha init --force")
            instructions.append("Check agent status: npx claude-flow@alpha status")
        
        if analysis.complexity in [ComplexityLevel.COMPLEX, ComplexityLevel.ENTERPRISE]:
            instructions.append("Ensure all MCP servers are running")
            instructions.append("Open dashboard for monitoring: .claude/dashboard.html")
        
        return instructions
    
    def _create_execution_strategy(self, analysis: TaskAnalysis) -> str:
        """Create an execution strategy description."""
        if analysis.execution_mode == ExecutionMode.SWARM:
            return ("Single-objective execution with fast completion. "
                   "Agents work independently on focused tasks.")
        elif analysis.execution_mode == ExecutionMode.HIVE_MIND:
            return ("Multi-phase execution with persistent state management. "
                   "Agents coordinate through shared memory and planning.")
        elif analysis.execution_mode == ExecutionMode.TEN_X_COMMANDS:
            return ("Intelligence-driven analysis followed by optimized implementation. "
                   "Leverages parallel research and proven patterns.")
        else:  # HYBRID
            return ("Hybrid approach combining Hive-Mind planning with Swarm execution. "
                   "Optimal for enterprise-scale implementations.")
    
    def _define_success_metrics(self, analysis: TaskAnalysis) -> List[str]:
        """Define success metrics based on complexity and execution mode."""
        metrics = []
        
        # Base metrics
        metrics.append("Task completion within estimated timeframe")
        metrics.append("All generated code passes quality checks")
        
        # Complexity-based metrics
        if analysis.complexity in [ComplexityLevel.COMPLEX, ComplexityLevel.ENTERPRISE]:
            metrics.append("Comprehensive test coverage (>80%)")
            metrics.append("Security validation passes")
            metrics.append("Performance benchmarks meet requirements")
        
        if analysis.execution_mode == ExecutionMode.HIVE_MIND:
            metrics.append("Successful state persistence and recovery")
            metrics.append("Effective agent coordination")
        
        return metrics
    
    def _show_examples(self):
        """Show example requests and their classifications."""
        examples = [
            "Build a user authentication system with JWT tokens",
            "Fix CSS bug in header component", 
            "Create REST API for user management",
            "Optimize database query performance",
            "Set up CI/CD pipeline for deployment",
            "Refactor monolith into microservices"
        ]
        
        print("\n📚 Example Requests:")
        for i, example in enumerate(examples, 1):
            print(f"{i}. {example}")
        print()


def main():
    """Main entry point for the Smart Command Orchestrator."""
    parser = argparse.ArgumentParser(
        description="Smart Command Orchestrator for Claude Flow and 10X Agentic Setup",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python smart_command_orchestrator.py "Build user authentication"
  python smart_command_orchestrator.py --interactive
  python smart_command_orchestrator.py --analyze "Create REST API" --json
        """
    )
    
    parser.add_argument(
        'request',
        nargs='?',
        help='Natural language description of what you want to build'
    )
    
    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Run in interactive mode'
    )
    
    parser.add_argument(
        '--analyze', '-a',
        metavar='REQUEST',
        help='Analyze a specific request and show detailed breakdown'
    )
    
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results in JSON format'
    )
    
    args = parser.parse_args()
    
    orchestrator = SmartCommandOrchestrator()
    
    if args.interactive:
        orchestrator.interactive_mode()
    elif args.analyze or args.request:
        request = args.analyze or args.request
        
        analysis = orchestrator.analyze_request(request)
        recommendation = orchestrator.generate_commands(request, analysis)
        
        if args.json:
            result = {
                'request': request,
                'analysis': {
                    'complexity': analysis.complexity.value,
                    'estimated_time': analysis.estimated_time,
                    'execution_mode': analysis.execution_mode.value,
                    'required_agents': analysis.required_agents,
                    'prerequisites': analysis.prerequisites,
                    'follow_up_actions': analysis.follow_up_actions
                },
                'recommendation': {
                    'primary_commands': recommendation.primary_commands,
                    'setup_instructions': recommendation.setup_instructions,
                    'execution_strategy': recommendation.execution_strategy,
                    'success_metrics': recommendation.success_metrics
                }
            }
            print(json.dumps(result, indent=2))
        else:
            response = orchestrator.format_response(request, analysis, recommendation)
            print(response)
    else:
        parser.print_help()
        print("\n🧠 Smart Command Orchestrator")
        print("Intelligent assistant for Claude Flow and 10X Agentic Setup command selection")
        print("\nQuick start: python smart_command_orchestrator.py --interactive")


if __name__ == "__main__":
    main()
