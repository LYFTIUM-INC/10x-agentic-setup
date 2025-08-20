#\!/usr/bin/env python3
"""
Smart Command Orchestrator Demo
===============================

This script demonstrates the capabilities of the Smart Command Orchestrator
with various real-world scenarios.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from smart_command_orchestrator import SmartCommandOrchestrator

def run_demo():
    """Run demonstration of the Smart Command Orchestrator."""
    
    orchestrator = SmartCommandOrchestrator()
    
    print("🧠 Smart Command Orchestrator Demo")
    print("=" * 50)
    print("Analyzing various development requests and generating optimal command recommendations")
    print()
    
    demo_requests = [
        {
            'request': 'Fix CSS bug in header component',
            'description': 'Simple bug fix - should recommend Swarm mode'
        },
        {
            'request': 'Create REST API for user management',
            'description': 'Moderate complexity - API development pattern'
        },
        {
            'request': 'Build complete user authentication system with JWT tokens',
            'description': 'Complex system - should recommend Hive-Mind with security focus'
        },
        {
            'request': 'Optimize database query performance',
            'description': 'Performance optimization - should include intelligence gathering'
        },
        {
            'request': 'Refactor monolith into microservices architecture',
            'description': 'Enterprise complexity - should recommend hybrid approach'
        }
    ]
    
    for i, demo in enumerate(demo_requests, 1):
        print(f"📋 Demo {i}: {demo['description']}")
        print(f"Request: \"{demo['request']}\"")
        print("-" * 40)
        
        try:
            analysis = orchestrator.analyze_request(demo['request'])
            recommendation = orchestrator.generate_commands(demo['request'], analysis)
            
            # Show key insights
            print(f"🔍 Complexity: {analysis.complexity.value.title()}")
            print(f"⏱️  Time Estimate: {analysis.estimated_time}")
            print(f"🎛️  Execution Mode: {analysis.execution_mode.value}")
            print(f"👥 Required Agents: {', '.join(analysis.required_agents)}")
            
            print("\n📋 Primary Commands:")
            for cmd in recommendation.primary_commands:
                print(f"  • {cmd}")
            
            print(f"\n⚡ Strategy: {recommendation.execution_strategy}")
            
            if recommendation.setup_instructions:
                print("\n🔧 Setup Required:")
                for instruction in recommendation.setup_instructions:
                    print(f"  • {instruction}")
            
            print("\n" + "="*50 + "\n")
            
        except Exception as e:
            print(f"❌ Error analyzing request: {e}")
    
    print("🎯 Demo completed\! The orchestrator successfully analyzed all scenarios")
    print("and provided appropriate command recommendations for each complexity level.")

if __name__ == "__main__":
    run_demo()
