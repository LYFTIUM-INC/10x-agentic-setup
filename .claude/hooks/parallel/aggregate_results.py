#!/usr/bin/env python3
"""
Parallel MCP Result Aggregation Hook
Collects and aggregates results from parallel MCP operations
"""

import json
import sys
import os
import time
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Add the parallel module to path
sys.path.append(str(Path(__file__).parent))

from aggregation_engine import AggregationEngine, ResultMetadata

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResultAggregationTracker:
    """Tracks and aggregates results from parallel MCP operations"""
    
    def __init__(self):
        self.aggregator = AggregationEngine()
        self.session_id = os.getenv('CLAUDE_SESSION_ID', 'unknown')
        self.aggregation_data_file = f"/tmp/claude_aggregation_{self.session_id}.json"
        
        # Expected number of MCP servers for different commands
        self.expected_servers = {
            '/analyze_10x': 5,
            '/implement_10x': 5,
            '/qa:comprehensive_10x': 5
        }
        
    def load_aggregation_data(self) -> Dict[str, Any]:
        """Load existing aggregation data"""
        
        try:
            if os.path.exists(self.aggregation_data_file):
                with open(self.aggregation_data_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load aggregation data: {e}")
        
        return {
            'session_id': self.session_id,
            'results': [],
            'orchestration_context': None,
            'aggregation_status': 'collecting',
            'started_at': time.time()
        }
    
    def save_aggregation_data(self, data: Dict[str, Any]):
        """Save aggregation data"""
        
        try:
            with open(self.aggregation_data_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save aggregation data: {e}")
    
    def load_orchestration_context(self) -> Optional[Dict[str, Any]]:
        """Load orchestration context from parallel orchestration"""
        
        orchestration_file = f"/tmp/claude_orchestration_{self.session_id}.json"
        
        try:
            if os.path.exists(orchestration_file):
                with open(orchestration_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load orchestration context: {e}")
        
        return None
    
    def extract_mcp_result_info(self, hook_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract MCP result information from hook data"""
        
        tool_name = hook_data.get('tool_name', '')
        tool_output = hook_data.get('tool_output', {})
        
        # Check if this is an MCP tool call
        if not tool_name.startswith('mcp__') and not tool_name.startswith('Task'):
            return None
        
        # Parse MCP server name and operation
        if tool_name.startswith('mcp__'):
            # Format: mcp__server_name__operation
            parts = tool_name.split('__')
            if len(parts) >= 3:
                server_name = parts[1].replace('_', '-')
                operation = parts[2]
            else:
                server_name = 'unknown'
                operation = 'unknown'
        else:
            # Task tool - extract from output if available
            server_name = 'task-agent'
            operation = 'research_task'
        
        # Extract timing information
        duration_ms = hook_data.get('duration_ms', 0)
        execution_time = duration_ms / 1000.0 if duration_ms else 0.1
        
        # Assess result confidence based on success and content
        success = hook_data.get('success', True)
        confidence = 0.9 if success else 0.3
        
        # If tool output contains error, reduce confidence
        if isinstance(tool_output, dict) and tool_output.get('error'):
            confidence = 0.2
        
        return {
            'server_name': server_name,
            'operation': operation,
            'result': tool_output,
            'execution_time': execution_time,
            'confidence': confidence,
            'timestamp': time.time(),
            'success': success
        }
    
    def should_aggregate_now(self, aggregation_data: Dict[str, Any], 
                           orchestration_context: Optional[Dict[str, Any]]) -> bool:
        """Determine if we should aggregate results now"""
        
        results_count = len(aggregation_data['results'])
        
        # If we have orchestration context, use that to determine expected count
        if orchestration_context and orchestration_context.get('context'):
            command_type = orchestration_context['context'].get('command_type')
            expected = self.expected_servers.get(command_type, 3)
            
            # Aggregate when we have all expected results or after timeout
            time_since_start = time.time() - aggregation_data['started_at']
            
            return (results_count >= expected or 
                   (results_count > 0 and time_since_start > 30))  # 30 second timeout
        
        # Without orchestration context, aggregate after collecting a few results
        return results_count >= 2
    
    def aggregate_collected_results(self, aggregation_data: Dict[str, Any],
                                  orchestration_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate all collected results"""
        
        results = aggregation_data['results']
        if not results:
            return {'error': 'No results to aggregate'}
        
        logger.info(f"Aggregating {len(results)} collected results")
        
        # Convert to the format expected by aggregation engine
        result_data = [r['result'] for r in results]
        metadatas = [
            ResultMetadata(
                server_name=r['server_name'],
                operation=r['operation'],
                timestamp=r['timestamp'],
                execution_time=r['execution_time'],
                confidence=r['confidence']
            )
            for r in results
        ]
        
        # Determine command type
        command_type = '/analyze_10x'  # Default
        if orchestration_context and orchestration_context.get('context'):
            command_type = orchestration_context['context'].get('command_type', '/analyze_10x')
        
        # Perform aggregation
        try:
            aggregated = self.aggregator.aggregate_results(
                command_type=command_type,
                results=result_data,
                metadatas=metadatas
            )
            
            return {
                'aggregation_successful': True,
                'aggregated_result': aggregated.unified_result,
                'aggregation_metadata': {
                    'confidence_score': aggregated.confidence_score,
                    'quality_metrics': aggregated.quality_metrics,
                    'conflicts_detected': len(aggregated.conflicts_detected),
                    'processing_time': aggregated.processing_time,
                    'strategy_used': aggregated.aggregation_strategy.value,
                    'source_count': len(results),
                    'server_diversity': len(set(r['server_name'] for r in results))
                },
                'individual_results': results,
                'conflicts': aggregated.conflicts_detected
            }
            
        except Exception as e:
            logger.error(f"Aggregation failed: {e}")
            return {
                'aggregation_successful': False,
                'error': str(e),
                'individual_results': results
            }
    
    def generate_aggregation_report(self, final_aggregation: Dict[str, Any]) -> str:
        """Generate a human-readable aggregation report"""
        
        if not final_aggregation.get('aggregation_successful'):
            return f"❌ Result aggregation failed: {final_aggregation.get('error', 'Unknown error')}"
        
        metadata = final_aggregation['aggregation_metadata']
        
        report = [
            "🔄 **Parallel MCP Result Aggregation Complete**",
            "",
            f"📊 **Summary:**",
            f"  • Sources: {metadata['source_count']} MCP operations",
            f"  • Server diversity: {metadata['server_diversity']:.1f}",
            f"  • Confidence: {metadata['confidence_score']:.2f}/1.0",
            f"  • Strategy: {metadata['strategy_used']}",
            f"  • Processing time: {metadata['processing_time']:.3f}s",
            ""
        ]
        
        # Quality metrics
        quality = metadata['quality_metrics']
        report.extend([
            f"🎯 **Quality Metrics:**",
            f"  • Average quality: {quality['avg_quality_score']:.2f}",
            f"  • Execution efficiency: {quality['avg_execution_time']:.2f}s average",
            f"  • Data completeness: {quality.get('total_data_points', 0):,} data points",
            ""
        ])
        
        # Conflicts
        if metadata['conflicts_detected'] > 0:
            report.extend([
                f"⚠️  **Conflicts Detected:** {metadata['conflicts_detected']}",
                f"  • Review individual results for discrepancies",
                ""
            ])
        
        # Individual server results
        report.append("🖥️  **Individual Server Results:**")
        for result in final_aggregation['individual_results']:
            status = "✅" if result['success'] else "❌"
            report.append(
                f"  • {status} {result['server_name']}: "
                f"{result['execution_time']:.2f}s (confidence: {result['confidence']:.2f})"
            )
        
        return "\n".join(report)

def main():
    """Main hook execution function"""
    
    try:
        # Read hook input
        hook_data = json.loads(sys.stdin.read())
        
        # Initialize tracker
        tracker = ResultAggregationTracker()
        
        # Load existing aggregation data
        aggregation_data = tracker.load_aggregation_data()
        
        # Load orchestration context
        orchestration_context = tracker.load_orchestration_context()
        
        # Extract MCP result information
        mcp_result_info = tracker.extract_mcp_result_info(hook_data)
        
        if mcp_result_info:
            # Add this result to the collection
            aggregation_data['results'].append(mcp_result_info)
            aggregation_data['last_updated'] = time.time()
            
            logger.info(f"Collected result from {mcp_result_info['server_name']} "
                       f"({len(aggregation_data['results'])} total results)")
            
            # Check if we should aggregate now
            if tracker.should_aggregate_now(aggregation_data, orchestration_context):
                logger.info("Triggering result aggregation")
                
                # Perform final aggregation
                final_aggregation = tracker.aggregate_collected_results(
                    aggregation_data, orchestration_context
                )
                
                # Generate and display report
                report = tracker.generate_aggregation_report(final_aggregation)
                print(report)
                
                # Update aggregation data with final results
                aggregation_data['final_aggregation'] = final_aggregation
                aggregation_data['aggregation_status'] = 'completed'
                aggregation_data['completed_at'] = time.time()
            
            # Save updated aggregation data
            tracker.save_aggregation_data(aggregation_data)
        
        # Always continue
        print(json.dumps({"continue": True}))
        
    except Exception as e:
        logger.error(f"Result aggregation hook failed: {str(e)}")
        # Always continue to avoid breaking the command
        print(json.dumps({"continue": True}))

if __name__ == "__main__":
    main()