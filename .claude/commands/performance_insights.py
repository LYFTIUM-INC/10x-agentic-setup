#!/usr/bin/env python3
"""
Claude Sub-Agent: Performance Insights Generator
On-demand analysis of performance patterns and recommendations
"""

import sys
import json
import os
from pathlib import Path
from datetime import datetime, timezone, timedelta
import glob

def analyze_performance_patterns():
    """Analyze all performance data to generate insights"""
    
    data_dir = Path(".claude/data")
    
    # Collect all performance histories
    performance_files = glob.glob(str(data_dir / "performance_history_*.json"))
    session_files = glob.glob(str(data_dir / "sessions" / "*_performance_report.json"))
    
    insights = {
        "overall_stats": {
            "total_tasks": 0,
            "unique_task_types": 0,
            "repeated_tasks": 0,
            "average_completion_score": 0.0,
            "user_satisfaction_concerns": 0
        },
        "patterns": {
            "most_repeated_tasks": [],
            "lowest_performing_tasks": [],
            "improving_tasks": [],
            "declining_tasks": []
        },
        "recommendations": [],
        "alerts": []
    }
    
    all_scores = []
    task_patterns = {}
    
    # Analyze performance histories
    for perf_file in performance_files:
        try:
            with open(perf_file, 'r') as f:
                history = json.load(f)
            
            task_sig = history["task_signature"]
            attempts = history["attempts"]
            
            if len(attempts) == 0:
                continue
                
            task_patterns[task_sig] = {
                "attempts": len(attempts),
                "average_score": history["average_score"],
                "trend": history["trend"],
                "satisfaction_pattern": history["user_satisfaction_pattern"],
                "latest_score": attempts[-1]["completion_score"]
            }
            
            all_scores.extend([a["completion_score"] for a in attempts])
            
            # Count repeated tasks
            if len(attempts) > 1:
                insights["overall_stats"]["repeated_tasks"] += 1
            
            # Check for user satisfaction concerns
            if history["user_satisfaction_pattern"] in ["user_unsatisfied_low_quality", "user_unsatisfied_persistent"]:
                insights["overall_stats"]["user_satisfaction_concerns"] += 1
        
        except Exception as e:
            print(f"Error reading {perf_file}: {e}")
    
    # Calculate overall stats
    insights["overall_stats"]["total_tasks"] = len(task_patterns)
    insights["overall_stats"]["unique_task_types"] = len(task_patterns)
    
    if all_scores:
        insights["overall_stats"]["average_completion_score"] = sum(all_scores) / len(all_scores)
    
    # Identify patterns
    sorted_by_attempts = sorted(task_patterns.items(), key=lambda x: x[1]["attempts"], reverse=True)
    insights["patterns"]["most_repeated_tasks"] = [
        {"task": k, "attempts": v["attempts"], "avg_score": v["average_score"]}
        for k, v in sorted_by_attempts[:5] if v["attempts"] > 1
    ]
    
    sorted_by_score = sorted(task_patterns.items(), key=lambda x: x[1]["average_score"])
    insights["patterns"]["lowest_performing_tasks"] = [
        {"task": k, "avg_score": v["average_score"], "attempts": v["attempts"]}
        for k, v in sorted_by_score[:5] if v["average_score"] < 70
    ]
    
    # Trends
    for task, data in task_patterns.items():
        if data["trend"] == "improving":
            insights["patterns"]["improving_tasks"].append({
                "task": task,
                "trend": "improving",
                "latest_score": data["latest_score"]
            })
        elif data["trend"] == "declining":
            insights["patterns"]["declining_tasks"].append({
                "task": task, 
                "trend": "declining",
                "latest_score": data["latest_score"]
            })
    
    # Generate recommendations
    recommendations = []
    
    # High repeat, low performance tasks
    for task_data in insights["patterns"]["most_repeated_tasks"]:
        if task_data["avg_score"] < 70:
            recommendations.append({
                "type": "critical",
                "task": task_data["task"],
                "issue": f"Task repeated {task_data['attempts']} times with low avg score ({task_data['avg_score']:.1f})",
                "recommendation": "Consider fundamentally different approach or break into smaller subtasks"
            })
    
    # Overall performance concerns
    if insights["overall_stats"]["average_completion_score"] < 75:
        recommendations.append({
            "type": "warning",
            "issue": f"Overall completion score is low ({insights['overall_stats']['average_completion_score']:.1f})",
            "recommendation": "Review common failure patterns and improve verification processes"
        })
    
    # User satisfaction alerts
    if insights["overall_stats"]["user_satisfaction_concerns"] > 0:
        recommendations.append({
            "type": "alert",
            "issue": f"{insights['overall_stats']['user_satisfaction_concerns']} tasks show user dissatisfaction",
            "recommendation": "Focus on quality over speed, implement better testing"
        })
    
    insights["recommendations"] = recommendations
    
    # Generate alerts for immediate attention
    alerts = []
    
    for task, data in task_patterns.items():
        if data["attempts"] > 3 and data["average_score"] < 60:
            alerts.append({
                "severity": "high",
                "message": f"Task '{task[:20]}...' failing repeatedly (avg: {data['average_score']:.1f})",
                "action": "Consider alternative implementation strategy"
            })
        
        if data["satisfaction_pattern"] == "user_unsatisfied_persistent":
            alerts.append({
                "severity": "critical", 
                "message": f"User persistently unsatisfied with task '{task[:20]}...'",
                "action": "Manual review required - may need human intervention"
            })
    
    insights["alerts"] = alerts
    
    return insights

def main():
    try:
        insights = analyze_performance_patterns()
        
        print("🎯 CLAUDE SUB-AGENT PERFORMANCE INSIGHTS")
        print("=" * 50)
        
        # Overall stats
        stats = insights["overall_stats"]
        print(f"📊 Overall Performance:")
        print(f"   Total Tasks: {stats['total_tasks']}")
        print(f"   Repeated Tasks: {stats['repeated_tasks']}")
        print(f"   Avg Completion Score: {stats['average_completion_score']:.1f}/100")
        print(f"   User Satisfaction Concerns: {stats['user_satisfaction_concerns']}")
        print()
        
        # Alerts
        if insights["alerts"]:
            print("🚨 IMMEDIATE ALERTS:")
            for alert in insights["alerts"]:
                severity_emoji = "🔴" if alert["severity"] == "critical" else "🟠"
                print(f"   {severity_emoji} {alert['message']}")
                print(f"      → {alert['action']}")
            print()
        
        # Most repeated tasks
        if insights["patterns"]["most_repeated_tasks"]:
            print("🔄 MOST REPEATED TASKS:")
            for task in insights["patterns"]["most_repeated_tasks"]:
                score_emoji = "🔴" if task["avg_score"] < 70 else "🟡" if task["avg_score"] < 85 else "🟢"
                print(f"   {score_emoji} {task['task'][:30]}... ({task['attempts']} attempts, {task['avg_score']:.1f} avg)")
            print()
        
        # Recommendations
        if insights["recommendations"]:
            print("💡 RECOMMENDATIONS:")
            for rec in insights["recommendations"]:
                type_emoji = "🔴" if rec["type"] == "critical" else "🟠" if rec["type"] == "warning" else "🔵"
                print(f"   {type_emoji} {rec.get('issue', rec.get('recommendation', ''))}")
                if 'recommendation' in rec and 'issue' in rec:
                    print(f"      → {rec['recommendation']}")
            print()
        
        # Save insights
        insights_file = Path(".claude/data/performance_insights.json")
        insights_file.parent.mkdir(parents=True, exist_ok=True)
        
        insights["generated_at"] = datetime.now(timezone.utc).isoformat()
        with open(insights_file, 'w') as f:
            json.dump(insights, f, indent=2)
        
        print(f"💾 Insights saved to {insights_file}")
        
    except Exception as e:
        print(f"Error generating insights: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()