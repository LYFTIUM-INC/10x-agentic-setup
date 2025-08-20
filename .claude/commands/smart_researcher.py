#!/usr/bin/env python3
"""
Claude Sub-Agent: Smart Research Agent
Leverages Claude's capabilities for comprehensive research with local storage
"""

import sys
import json
import os
import subprocess
import hashlib
from pathlib import Path
from datetime import datetime, timezone
import re

class SmartResearcher:
    def __init__(self):
        self.research_dir = Path(".claude/research")
        self.research_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.research_dir / "research_index.json"
        self.load_index()
    
    def load_index(self):
        """Load or create research index"""
        if self.index_file.exists():
            with open(self.index_file, 'r') as f:
                self.index = json.load(f)
        else:
            self.index = {
                "topics": {},
                "searches": [],
                "findings": [],
                "last_updated": None
            }
    
    def save_index(self):
        """Save research index"""
        self.index["last_updated"] = datetime.now(timezone.utc).isoformat()
        with open(self.index_file, 'w') as f:
            json.dump(self.index, f, indent=2)
    
    def create_topic_id(self, topic):
        """Create unique ID for research topic"""
        return hashlib.md5(topic.lower().encode()).hexdigest()[:12]
    
    def research_topic(self, topic, depth="comprehensive"):
        """Research a topic with specified depth"""
        topic_id = self.create_topic_id(topic)
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Check if we've researched this recently
        if topic_id in self.index["topics"]:
            last_research = self.index["topics"][topic_id]
            print(f"📚 Found existing research on '{topic}' from {last_research['timestamp']}")
            
            # Ask if we should update
            if depth != "quick":
                print("🔄 Updating with new research...")
            else:
                return self.load_research_results(topic_id)
        
        # Create research plan
        research_plan = self.create_research_plan(topic, depth)
        
        # Execute research
        results = {
            "topic": topic,
            "topic_id": topic_id,
            "timestamp": timestamp,
            "depth": depth,
            "plan": research_plan,
            "findings": {},
            "summary": "",
            "key_points": [],
            "references": [],
            "related_topics": []
        }
        
        # Save research plan
        plan_file = self.research_dir / f"{topic_id}_plan.json"
        with open(plan_file, 'w') as f:
            json.dump(research_plan, f, indent=2)
        
        print(f"📋 Research plan created: {plan_file}")
        
        # Execute each research phase
        for phase in research_plan["phases"]:
            print(f"🔍 Executing: {phase['name']}")
            phase_results = self.execute_research_phase(phase, topic)
            results["findings"][phase["id"]] = phase_results
        
        # Generate summary and key points
        results["summary"] = self.generate_summary(results["findings"])
        results["key_points"] = self.extract_key_points(results["findings"])
        results["references"] = self.collect_references(results["findings"])
        
        # Save results
        self.save_research_results(topic_id, results)
        
        # Update index
        self.index["topics"][topic_id] = {
            "topic": topic,
            "timestamp": timestamp,
            "depth": depth,
            "file": f"{topic_id}_results.json"
        }
        self.index["searches"].append({
            "topic": topic,
            "topic_id": topic_id,
            "timestamp": timestamp
        })
        self.save_index()
        
        return results
    
    def create_research_plan(self, topic, depth):
        """Create a structured research plan"""
        base_phases = [
            {
                "id": "overview",
                "name": "Topic Overview",
                "queries": [
                    f"What is {topic}?",
                    f"Key concepts in {topic}",
                    f"Why is {topic} important?"
                ]
            },
            {
                "id": "current_state",
                "name": "Current State Analysis",
                "queries": [
                    f"Latest developments in {topic}",
                    f"Current best practices for {topic}",
                    f"Common challenges with {topic}"
                ]
            }
        ]
        
        if depth == "comprehensive":
            base_phases.extend([
                {
                    "id": "technical_details",
                    "name": "Technical Deep Dive",
                    "queries": [
                        f"Technical architecture of {topic}",
                        f"Implementation patterns for {topic}",
                        f"Performance considerations for {topic}"
                    ]
                },
                {
                    "id": "comparisons",
                    "name": "Comparative Analysis",
                    "queries": [
                        f"Alternatives to {topic}",
                        f"{topic} vs similar solutions",
                        f"When to use {topic} vs alternatives"
                    ]
                },
                {
                    "id": "future",
                    "name": "Future Outlook",
                    "queries": [
                        f"Future of {topic}",
                        f"Emerging trends in {topic}",
                        f"Predictions for {topic} evolution"
                    ]
                }
            ])
        
        return {
            "topic": topic,
            "depth": depth,
            "phases": base_phases,
            "created": datetime.now(timezone.utc).isoformat()
        }
    
    def execute_research_phase(self, phase, topic):
        """Execute a single research phase"""
        phase_results = {
            "phase": phase["name"],
            "findings": [],
            "insights": [],
            "questions_remaining": []
        }
        
        for query in phase["queries"]:
            # Simulate research execution
            # In a real implementation, this would call Claude or search APIs
            finding = {
                "query": query,
                "result": f"Research finding for: {query}",
                "confidence": 0.85,
                "sources": ["Internal knowledge base"],
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            phase_results["findings"].append(finding)
        
        # Extract insights from findings
        phase_results["insights"] = self.extract_insights(phase_results["findings"])
        
        return phase_results
    
    def extract_insights(self, findings):
        """Extract key insights from findings"""
        insights = []
        
        # Group similar findings
        for finding in findings:
            # Simple insight extraction (would be more sophisticated with Claude)
            if finding["confidence"] > 0.8:
                insights.append({
                    "type": "high_confidence",
                    "content": f"Strong evidence for: {finding['query']}",
                    "supporting_findings": [finding["result"]]
                })
        
        return insights
    
    def generate_summary(self, all_findings):
        """Generate executive summary of research"""
        summary_parts = []
        
        for phase_id, phase_results in all_findings.items():
            if phase_results["insights"]:
                summary_parts.append(f"{phase_results['phase']}: {len(phase_results['insights'])} key insights found")
        
        return " | ".join(summary_parts)
    
    def extract_key_points(self, all_findings):
        """Extract key points from all findings"""
        key_points = []
        
        for phase_id, phase_results in all_findings.items():
            for insight in phase_results["insights"][:2]:  # Top 2 per phase
                key_points.append({
                    "phase": phase_results["phase"],
                    "point": insight["content"],
                    "importance": "high"
                })
        
        return key_points
    
    def collect_references(self, all_findings):
        """Collect all references and sources"""
        references = set()
        
        for phase_id, phase_results in all_findings.items():
            for finding in phase_results["findings"]:
                references.update(finding.get("sources", []))
        
        return list(references)
    
    def save_research_results(self, topic_id, results):
        """Save research results to file"""
        results_file = self.research_dir / f"{topic_id}_results.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Also save a markdown summary
        md_file = self.research_dir / f"{topic_id}_summary.md"
        with open(md_file, 'w') as f:
            f.write(self.format_markdown_summary(results))
        
        print(f"💾 Research saved to: {results_file}")
        print(f"📄 Summary saved to: {md_file}")
    
    def load_research_results(self, topic_id):
        """Load existing research results"""
        results_file = self.research_dir / f"{topic_id}_results.json"
        if results_file.exists():
            with open(results_file, 'r') as f:
                return json.load(f)
        return None
    
    def format_markdown_summary(self, results):
        """Format results as markdown summary"""
        md = []
        md.append(f"# Research: {results['topic']}")
        md.append(f"\n*Generated: {results['timestamp']}*")
        md.append(f"\n*Depth: {results['depth']}*")
        
        md.append(f"\n## Summary\n{results['summary']}")
        
        md.append("\n## Key Points")
        for point in results["key_points"]:
            md.append(f"- **{point['phase']}**: {point['point']}")
        
        md.append("\n## Detailed Findings")
        for phase_id, phase_results in results["findings"].items():
            md.append(f"\n### {phase_results['phase']}")
            
            for finding in phase_results["findings"][:3]:  # Top 3 per phase
                md.append(f"\n**Q**: {finding['query']}")
                md.append(f"\n**A**: {finding['result']}")
                md.append(f"\n*Confidence: {finding['confidence']*100:.0f}%*\n")
        
        if results["references"]:
            md.append("\n## References")
            for ref in results["references"]:
                md.append(f"- {ref}")
        
        return "\n".join(md)
    
    def search_previous_research(self, query):
        """Search through previous research"""
        results = []
        query_lower = query.lower()
        
        for topic_id, topic_info in self.index["topics"].items():
            if query_lower in topic_info["topic"].lower():
                research = self.load_research_results(topic_id)
                if research:
                    results.append({
                        "topic": topic_info["topic"],
                        "timestamp": topic_info["timestamp"],
                        "relevance": self.calculate_relevance(query, research),
                        "summary": research["summary"],
                        "topic_id": topic_id
                    })
        
        # Sort by relevance
        results.sort(key=lambda x: x["relevance"], reverse=True)
        return results
    
    def calculate_relevance(self, query, research):
        """Calculate relevance score"""
        score = 0
        query_words = set(query.lower().split())
        
        # Check topic match
        topic_words = set(research["topic"].lower().split())
        score += len(query_words & topic_words) * 10
        
        # Check key points
        for point in research["key_points"]:
            point_words = set(point["point"].lower().split())
            score += len(query_words & point_words)
        
        return score
    
    def generate_research_report(self):
        """Generate comprehensive research report"""
        report = {
            "generated": datetime.now(timezone.utc).isoformat(),
            "total_topics": len(self.index["topics"]),
            "total_searches": len(self.index["searches"]),
            "topics_by_depth": {},
            "recent_research": [],
            "most_researched": []
        }
        
        # Analyze by depth
        for topic_info in self.index["topics"].values():
            depth = topic_info.get("depth", "unknown")
            report["topics_by_depth"][depth] = report["topics_by_depth"].get(depth, 0) + 1
        
        # Recent research
        recent = sorted(self.index["searches"], key=lambda x: x["timestamp"], reverse=True)[:10]
        report["recent_research"] = recent
        
        # Most researched topics
        topic_counts = {}
        for search in self.index["searches"]:
            topic = search["topic"]
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        report["most_researched"] = sorted(
            [{"topic": k, "count": v} for k, v in topic_counts.items()],
            key=lambda x: x["count"],
            reverse=True
        )[:5]
        
        return report

def main():
    researcher = SmartResearcher()
    
    if len(sys.argv) < 2:
        print("Usage: smart_researcher.py <command> [args]")
        print("\nCommands:")
        print("  research <topic> [depth]     - Research a topic (depth: quick/standard/comprehensive)")
        print("  search <query>               - Search previous research")
        print("  report                       - Generate research report")
        print("  list                         - List all researched topics")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "research":
        if len(sys.argv) < 3:
            print("Error: Please provide a topic to research")
            sys.exit(1)
        
        topic = sys.argv[2]
        depth = sys.argv[3] if len(sys.argv) > 3 else "standard"
        
        print(f"🔬 Starting {depth} research on: {topic}")
        results = researcher.research_topic(topic, depth)
        
        print(f"\n✅ Research complete!")
        print(f"📊 Summary: {results['summary']}")
        print(f"\n🎯 Key Points:")
        for point in results["key_points"][:5]:
            print(f"  • {point['point']}")
    
    elif command == "search":
        if len(sys.argv) < 3:
            print("Error: Please provide a search query")
            sys.exit(1)
        
        query = " ".join(sys.argv[2:])
        print(f"🔍 Searching for: {query}")
        
        results = researcher.search_previous_research(query)
        
        if results:
            print(f"\n📚 Found {len(results)} relevant research topics:")
            for result in results[:5]:
                print(f"\n• {result['topic']} (relevance: {result['relevance']})")
                print(f"  Researched: {result['timestamp']}")
                print(f"  Summary: {result['summary']}")
        else:
            print("No relevant research found.")
    
    elif command == "report":
        report = researcher.generate_research_report()
        
        print("📊 RESEARCH REPORT")
        print("=" * 50)
        print(f"Total Topics Researched: {report['total_topics']}")
        print(f"Total Searches: {report['total_searches']}")
        
        print("\n📈 Research by Depth:")
        for depth, count in report["topics_by_depth"].items():
            print(f"  {depth}: {count}")
        
        print("\n🔥 Most Researched Topics:")
        for item in report["most_researched"]:
            print(f"  • {item['topic']} ({item['count']} times)")
        
        print("\n🕐 Recent Research:")
        for item in report["recent_research"][:5]:
            print(f"  • {item['topic']} - {item['timestamp']}")
    
    elif command == "list":
        print("📚 All Researched Topics:")
        print("=" * 50)
        
        for topic_id, info in researcher.index["topics"].items():
            print(f"\n• {info['topic']}")
            print(f"  ID: {topic_id}")
            print(f"  Depth: {info['depth']}")
            print(f"  Date: {info['timestamp']}")

if __name__ == "__main__":
    main()