#\!/usr/bin/env python3
"""
Test script for Smart Command Orchestrator
"""

import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(__file__))

from smart_command_orchestrator import SmartCommandOrchestrator

def test_orchestrator():
    """Test the orchestrator with various scenarios."""
    
    orchestrator = SmartCommandOrchestrator()
    
    test_cases = [
        "Build a user authentication system with JWT tokens",
        "Fix CSS bug in header component",
        "Create REST API for user management", 
        "Optimize database query performance",
        "Set up CI/CD pipeline for deployment",
        "Refactor monolith into microservices"
    ]
    
    print("🧠 Smart Command Orchestrator Test Suite")
    print("=" * 50)
    
    for i, request in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}: {request}")
        print("-" * 40)
        
        try:
            analysis = orchestrator.analyze_request(request)
            recommendation = orchestrator.generate_commands(request, analysis)
            response = orchestrator.format_response(request, analysis, recommendation)
            
            # Show abbreviated results
            lines = response.split('\n')
            for line in lines[:15]:  # Show first 15 lines
                print(line)
            
            if len(lines) > 15:
                print("... (truncated)")
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_orchestrator()
