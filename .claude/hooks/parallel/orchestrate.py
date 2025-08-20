#!/usr/bin/env python3
"""
Parallel MCP Orchestration Hook
Detects unified commands and initiates parallel MCP coordination
"""

import json
import sys
import asyncio
import os
import logging
from pathlib import Path

# Add the parallel module to path
sys.path.append(str(Path(__file__).parent))

from dispatch_engine import ParallelDispatcher
from coordination_manager import CoordinationManager, CoordinationTask
from aggregation_engine import AggregationEngine, ResultMetadata

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ParallelOrchestrator:
    """Orchestrates parallel MCP execution for unified commands"""
    
    def __init__(self):
        self.dispatcher = None
        self.coordinator = None
        self.aggregator = AggregationEngine()
        
        self.unified_commands = {
            '/analyze_10x',
            '/implement_10x', 
            '/qa:comprehensive_10x'
        }
        
    async def should_orchestrate(self, prompt: str) -> bool:
        """Check if this prompt should trigger parallel orchestration"""
        
        # Check for unified commands
        for command in self.unified_commands:
            if command in prompt:
                return True
        
        # Check for parallel execution keywords
        parallel_keywords = [
            'parallel', 'simultaneous', 'concurrent',
            'multiple servers', 'all mcps'
        ]
        
        prompt_lower = prompt.lower()
        for keyword in parallel_keywords:
            if keyword in prompt_lower:
                return True
        
        return False
    
    def extract_command_context(self, prompt: str) -> dict:
        """Extract context and parameters from the prompt"""
        
        context = {
            'original_prompt': prompt,
            'command_type': None,
            'mode': 'standard',
            'scope': 'default',
            'focus': None,
            'parameters': {}
        }
        
        # Identify command type
        for command in self.unified_commands:
            if command in prompt:
                context['command_type'] = command
                break
        
        # Extract mode (e.g., --mode deep)
        import re
        mode_match = re.search(r'--mode\s+(\w+)', prompt)
        if mode_match:
            context['mode'] = mode_match.group(1)
        
        # Extract scope
        scope_match = re.search(r'--scope\s+(\w+)', prompt)
        if scope_match:
            context['scope'] = scope_match.group(1)
        
        # Extract focus for QA commands
        focus_match = re.search(r'--focus\s+(\w+)', prompt)
        if focus_match:
            context['focus'] = focus_match.group(1)
        
        # Extract feature for implement commands
        feature_match = re.search(r'--feature\s+"([^"]*)"', prompt)
        if not feature_match:
            feature_match = re.search(r'--spec\s+"([^"]*)"', prompt)
        if feature_match:
            context['parameters']['feature'] = feature_match.group(1)
        
        return context
    
    async def orchestrate_parallel_execution(self, context: dict) -> dict:
        """Orchestrate parallel execution across MCP servers"""
        
        logger.info(f"Orchestrating parallel execution for {context['command_type']}")
        
        try:
            # Initialize components
            self.dispatcher = ParallelDispatcher()
            await self.dispatcher.initialize()
            
            self.coordinator = CoordinationManager(max_concurrent_tasks=5)
            
            # Dispatch parallel tasks
            task_results = await self.dispatcher.dispatch_parallel(
                context['command_type'], 
                context
            )
            
            # Convert to coordination tasks if needed for complex orchestration
            if len(task_results) > 3:  # Use coordinator for complex scenarios
                coord_tasks = self.convert_to_coordination_tasks(task_results, context)
                coordinated_results = await self.coordinator.coordinate_execution(coord_tasks)
                final_results = [task.result for task in coordinated_results if task.result]
                metadatas = [
                    ResultMetadata(
                        server_name=task.server_name,
                        operation=task.operation,
                        timestamp=task.completed_at or task.created_at,
                        execution_time=(task.completed_at or task.created_at) - task.created_at,
                        confidence=0.9 if task.status.value == 'completed' else 0.1
                    )
                    for task in coordinated_results
                ]
            else:
                # Use direct results for simpler scenarios
                final_results = [result.result for result in task_results if result.success]
                metadatas = [
                    ResultMetadata(
                        server_name=result.server_name,
                        operation=result.operation,
                        timestamp=result.timestamp,
                        execution_time=result.execution_time,
                        confidence=0.9 if result.success else 0.1
                    )
                    for result in task_results
                ]
            
            # Aggregate results
            if final_results:
                aggregated = self.aggregator.aggregate_results(
                    context['command_type'],
                    final_results,
                    metadatas
                )
                
                # Generate orchestration summary
                orchestration_result = {
                    'orchestration_successful': True,
                    'parallel_execution_stats': {
                        'servers_used': len(set(r.server_name for r in task_results)),
                        'successful_tasks': len([r for r in task_results if r.success]),
                        'failed_tasks': len([r for r in task_results if not r.success]),
                        'total_execution_time': sum(r.execution_time for r in task_results),
                        'parallel_efficiency': self.calculate_parallel_efficiency(task_results)
                    },
                    'aggregated_result': aggregated.unified_result,
                    'confidence_score': aggregated.confidence_score,
                    'quality_metrics': aggregated.quality_metrics,
                    'conflicts_detected': len(aggregated.conflicts_detected),
                    'server_performance': self.get_server_performance_summary(task_results)
                }
                
                return orchestration_result
            else:
                return {
                    'orchestration_successful': False,
                    'error': 'No successful results from parallel execution',
                    'attempted_servers': len(task_results),
                    'failure_reasons': [r.error for r in task_results if r.error]
                }
                
        except Exception as e:
            logger.error(f"Orchestration failed: {str(e)}")
            return {
                'orchestration_successful': False,
                'error': str(e),
                'context': context
            }
        finally:
            # Cleanup
            if self.dispatcher:
                await self.dispatcher.cleanup()
    
    def convert_to_coordination_tasks(self, task_results, context):
        """Convert task results to coordination tasks for complex orchestration"""
        
        tasks = []
        for result in task_results:
            task = CoordinationTask(
                task_id=result.task_id,
                server_name=result.server_name,
                operation=result.operation,
                parameters=context['parameters']
            )
            
            # Set task result if already completed
            if result.success:
                task.result = result.result
                task.status = 'completed'
            else:
                task.error = result.error
                task.status = 'failed'
            
            tasks.append(task)
        
        return tasks
    
    def calculate_parallel_efficiency(self, task_results):
        """Calculate efficiency of parallel execution"""
        
        if not task_results:
            return 0.0
        
        successful_tasks = [r for r in task_results if r.success]
        if not successful_tasks:
            return 0.0
        
        # Calculate theoretical vs actual time
        total_individual_time = sum(r.execution_time for r in successful_tasks)
        max_execution_time = max(r.execution_time for r in successful_tasks)
        
        if max_execution_time == 0:
            return 1.0
        
        efficiency = total_individual_time / (max_execution_time * len(successful_tasks))
        return min(1.0, efficiency)
    
    def get_server_performance_summary(self, task_results):
        """Get summary of server performance"""
        
        performance = {}
        
        for result in task_results:
            server = result.server_name
            if server not in performance:
                performance[server] = {
                    'success_count': 0,
                    'failure_count': 0,
                    'avg_execution_time': 0.0,
                    'total_execution_time': 0.0
                }
            
            if result.success:
                performance[server]['success_count'] += 1
            else:
                performance[server]['failure_count'] += 1
            
            performance[server]['total_execution_time'] += result.execution_time
        
        # Calculate averages
        for server_data in performance.values():
            total_tasks = server_data['success_count'] + server_data['failure_count']
            if total_tasks > 0:
                server_data['avg_execution_time'] = (
                    server_data['total_execution_time'] / total_tasks
                )
                server_data['success_rate'] = (
                    server_data['success_count'] / total_tasks
                )
        
        return performance

async def main():
    """Main hook execution function"""
    
    try:
        # Read hook input
        hook_data = json.loads(sys.stdin.read())
        
        # Extract prompt
        prompt = hook_data.get('prompt', '')
        
        if not prompt:
            # No prompt to process
            print(json.dumps({"continue": True}))
            return
        
        # Initialize orchestrator
        orchestrator = ParallelOrchestrator()
        
        # Check if we should orchestrate parallel execution
        should_orchestrate = await orchestrator.should_orchestrate(prompt)
        
        if not should_orchestrate:
            # Not a unified command, continue normally
            print(json.dumps({"continue": True}))
            return
        
        # Extract context from prompt
        context = orchestrator.extract_command_context(prompt)
        
        # Store orchestration context for later hooks
        session_id = os.getenv('CLAUDE_SESSION_ID', 'unknown')
        orchestration_file = f"/tmp/claude_orchestration_{session_id}.json"
        
        with open(orchestration_file, 'w') as f:
            json.dump({
                'context': context,
                'initiated_at': __import__('time').time(),
                'status': 'initiated'
            }, f)
        
        # Initiate parallel orchestration
        print(f"🚀 Initiating parallel MCP orchestration for {context['command_type']}...")
        print(f"📊 Mode: {context['mode']}, Scope: {context['scope']}")
        
        orchestration_result = await orchestrator.orchestrate_parallel_execution(context)
        
        if orchestration_result['orchestration_successful']:
            stats = orchestration_result['parallel_execution_stats']
            print(f"✅ Parallel orchestration completed successfully!")
            print(f"📈 Used {stats['servers_used']} servers, "
                  f"{stats['successful_tasks']}/{stats['successful_tasks'] + stats['failed_tasks']} tasks successful")
            print(f"⚡ Parallel efficiency: {stats['parallel_efficiency']:.1%}")
            print(f"🎯 Confidence score: {orchestration_result['confidence_score']:.2f}")
            
            # Update orchestration file with results
            with open(orchestration_file, 'w') as f:
                json.dump({
                    'context': context,
                    'initiated_at': __import__('time').time(),
                    'status': 'completed',
                    'result': orchestration_result
                }, f)
        else:
            print(f"❌ Parallel orchestration failed: {orchestration_result.get('error', 'Unknown error')}")
            
            # Update orchestration file with failure
            with open(orchestration_file, 'w') as f:
                json.dump({
                    'context': context,
                    'initiated_at': __import__('time').time(),
                    'status': 'failed',
                    'error': orchestration_result.get('error', 'Unknown error')
                }, f)
        
        # Continue with normal command processing
        print(json.dumps({"continue": True}))
        
    except Exception as e:
        logger.error(f"Hook execution failed: {str(e)}")
        # Always continue to avoid breaking the command
        print(json.dumps({"continue": True}))

if __name__ == "__main__":
    asyncio.run(main())