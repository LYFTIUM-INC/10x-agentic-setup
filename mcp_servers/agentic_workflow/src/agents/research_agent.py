"""
Research Agent Implementation for Agentic Workflow MCP
Specialized agent for research, information gathering, and analysis tasks
"""

import asyncio
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from .base_agent import BaseAgent, AgentTask

logger = logging.getLogger(__name__)

class ResearchAgent(BaseAgent):
    """
    Specialized agent for research and information gathering tasks
    
    Capabilities:
    - Web search and information retrieval
    - Documentation analysis and parsing
    - Competitive intelligence gathering
    - Trend analysis and pattern recognition
    - Content synthesis and summarization
    """
    
    def __init__(self, agent_id: str):
        capabilities = [
            "web_search",
            "documentation_analysis", 
            "competitive_intelligence",
            "trend_analysis",
            "content_synthesis",
            "pattern_recognition",
            "information_extraction",
            "source_validation"
        ]
        
        super().__init__(agent_id, "research_agent", capabilities)
        
        self.search_history = []
        self.knowledge_cache = {}
        self.research_strategies = {}
        self.source_reliability_scores = {}
        self._initialize_research_strategies()
    
    def _initialize_research_strategies(self) -> None:
        """Initialize research strategies for different types of queries"""
        
        self.research_strategies = {
            "technical_documentation": {
                "sources": ["official_docs", "github", "stack_overflow", "academic_papers"],
                "depth": "comprehensive",
                "validation_required": True,
                "time_sensitivity": "medium"
            },
            "competitive_analysis": {
                "sources": ["company_websites", "news", "industry_reports", "social_media"],
                "depth": "broad",
                "validation_required": True,
                "time_sensitivity": "high"
            },
            "trend_analysis": {
                "sources": ["news", "social_media", "industry_reports", "analytics_platforms"],
                "depth": "comprehensive",
                "validation_required": False,
                "time_sensitivity": "high"
            },
            "problem_solving": {
                "sources": ["documentation", "forums", "tutorials", "expert_blogs"],
                "depth": "targeted",
                "validation_required": True,
                "time_sensitivity": "medium"
            },
            "market_research": {
                "sources": ["industry_reports", "news", "company_data", "surveys"],
                "depth": "comprehensive",
                "validation_required": True,
                "time_sensitivity": "low"
            }
        }
    
    async def _agent_specific_initialization(self, config: Dict[str, Any]) -> None:
        """Initialize research-specific tools and configurations"""
        
        # Initialize search tools
        self.tools.update({
            "web_searcher": self._simulate_web_search,
            "document_parser": self._parse_document,
            "content_analyzer": self._analyze_content,
            "trend_detector": self._detect_trends,
            "source_validator": self._validate_source,
            "synthesizer": self._synthesize_information
        })
        
        # Initialize knowledge cache
        self.knowledge_cache = config.get("knowledge_cache", {})
        
        # Initialize source reliability scores
        self.source_reliability_scores = config.get("source_reliability", {
            "official_documentation": 0.95,
            "github": 0.85,
            "stack_overflow": 0.75,
            "academic_papers": 0.9,
            "news_sites": 0.7,
            "blogs": 0.6,
            "social_media": 0.4
        })
    
    async def _can_handle_task(self, task: AgentTask) -> bool:
        """Check if this research agent can handle the given task"""
        
        research_task_types = [
            "research", "investigate", "analyze", "gather", "explore",
            "study", "examine", "survey", "review", "discover"
        ]
        
        task_type_lower = task.task_type.lower()
        task_description_lower = task.description.lower()
        
        # Check if task type or description contains research-related keywords
        return (any(keyword in task_type_lower for keyword in research_task_types) or
                any(keyword in task_description_lower for keyword in research_task_types))
    
    async def _execute_agent_task(self, task: AgentTask) -> Dict[str, Any]:
        """Execute research-specific task logic"""
        
        research_type = await self._determine_research_type(task)
        strategy = self.research_strategies.get(research_type, self.research_strategies["problem_solving"])
        
        logger.info(f"Research agent {self.agent_id} executing {research_type} research")
        
        # Execute research workflow
        research_plan = await self._create_research_plan(task, strategy)
        search_results = await self._execute_research_plan(research_plan)
        analyzed_results = await self._analyze_research_results(search_results)
        synthesized_results = await self._synthesize_research_findings(analyzed_results, task)
        
        # Update knowledge cache
        await self._update_knowledge_cache(task, synthesized_results)
        
        return {
            "research_type": research_type,
            "research_plan": research_plan,
            "search_results": search_results,
            "analysis": analyzed_results,
            "findings": synthesized_results,
            "confidence": await self._calculate_research_confidence(synthesized_results),
            "sources_used": await self._get_sources_used(search_results),
            "recommendations": await self._generate_research_recommendations(synthesized_results)
        }
    
    async def _determine_research_type(self, task: AgentTask) -> str:
        """Determine the type of research needed based on task parameters"""
        
        description = task.description.lower()
        parameters = task.parameters
        
        # Check for specific research type indicators
        if any(keyword in description for keyword in ["competitor", "competitive", "market share"]):
            return "competitive_analysis"
        elif any(keyword in description for keyword in ["trend", "trending", "popular", "emerging"]):
            return "trend_analysis"
        elif any(keyword in description for keyword in ["documentation", "api", "technical", "implementation"]):
            return "technical_documentation"
        elif any(keyword in description for keyword in ["market", "industry", "sector", "business"]):
            return "market_research"
        else:
            return "problem_solving"
    
    async def _create_research_plan(self, task: AgentTask, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Create a detailed research plan based on task and strategy"""
        
        research_plan = {
            "objective": task.description,
            "strategy": strategy,
            "search_queries": await self._generate_search_queries(task),
            "source_priorities": strategy["sources"],
            "depth_level": strategy["depth"],
            "validation_required": strategy["validation_required"],
            "estimated_duration": self._estimate_research_duration(task, strategy),
            "success_criteria": await self._define_success_criteria(task)
        }
        
        return research_plan
    
    async def _generate_search_queries(self, task: AgentTask) -> List[str]:
        """Generate search queries based on task parameters"""
        
        base_query = task.description
        parameters = task.parameters
        
        queries = [base_query]
        
        # Add parameter-specific queries
        if "topic" in parameters:
            topic = parameters["topic"]
            queries.extend([
                f"{topic} best practices",
                f"{topic} implementation guide",
                f"{topic} examples",
                f"{topic} tutorial"
            ])
        
        # Add context-specific queries
        if "context" in task.parameters:
            context = task.parameters["context"]
            if isinstance(context, dict):
                for key, value in context.items():
                    queries.append(f"{base_query} {key} {value}")
        
        # Add problem-specific queries
        if "problem" in parameters:
            problem = parameters["problem"]
            queries.extend([
                f"how to {problem}",
                f"{problem} solution",
                f"{problem} troubleshooting",
                f"{problem} fix"
            ])
        
        return queries[:10]  # Limit to 10 queries for efficiency
    
    def _estimate_research_duration(self, task: AgentTask, strategy: Dict[str, Any]) -> float:
        """Estimate research duration based on task complexity and strategy"""
        
        base_duration = 30.0  # Base 30 seconds
        
        # Adjust based on depth level
        depth_multipliers = {"targeted": 1.0, "broad": 1.5, "comprehensive": 2.0}
        duration = base_duration * depth_multipliers.get(strategy["depth"], 1.0)
        
        # Adjust based on number of sources
        source_count = len(strategy["sources"])
        duration *= (1.0 + (source_count - 1) * 0.2)
        
        # Adjust based on validation requirement
        if strategy["validation_required"]:
            duration *= 1.3
        
        return duration
    
    async def _define_success_criteria(self, task: AgentTask) -> List[str]:
        """Define success criteria for the research task"""
        
        criteria = [
            "Found relevant information addressing the query",
            "Identified credible sources",
            "Synthesized findings into actionable insights"
        ]
        
        # Add task-specific criteria
        if "specific_outcome" in task.parameters:
            criteria.append(f"Achieved specific outcome: {task.parameters['specific_outcome']}")
        
        if "accuracy_requirement" in task.parameters:
            criteria.append(f"Met accuracy requirement: {task.parameters['accuracy_requirement']}")
        
        return criteria
    
    async def _execute_research_plan(self, research_plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute the research plan and gather information"""
        
        search_results = []
        
        for query in research_plan["search_queries"]:
            for source_type in research_plan["source_priorities"]:
                try:
                    # Simulate search in different sources
                    source_results = await self._search_in_source(query, source_type)
                    
                    if source_results:
                        search_results.extend(source_results)
                        
                        # Break if we have enough results for targeted research
                        if (research_plan["depth_level"] == "targeted" and 
                            len(search_results) >= 10):
                            break
                
                except Exception as e:
                    logger.warning(f"Search failed for query '{query}' in source '{source_type}': {str(e)}")
                    continue
        
        return search_results
    
    async def _search_in_source(self, query: str, source_type: str) -> List[Dict[str, Any]]:
        """Search for information in a specific source type"""
        
        # Simulate search results based on source type
        if source_type == "official_docs":
            return await self._search_official_documentation(query)
        elif source_type == "github":
            return await self._search_github(query)
        elif source_type == "stack_overflow":
            return await self._search_stack_overflow(query)
        elif source_type == "news":
            return await self._search_news(query)
        elif source_type == "academic_papers":
            return await self._search_academic_papers(query)
        else:
            return await self._simulate_web_search(query, source_type)
    
    async def _search_official_documentation(self, query: str) -> List[Dict[str, Any]]:
        """Search official documentation sources"""
        
        # Simulate official documentation search
        await asyncio.sleep(0.2)  # Simulate network delay
        
        return [
            {
                "source": "official_documentation",
                "title": f"Official Guide: {query}",
                "content": f"Comprehensive official documentation for {query}. This covers best practices, implementation details, and examples.",
                "url": f"https://docs.example.com/{query.replace(' ', '-')}",
                "reliability": self.source_reliability_scores.get("official_documentation", 0.95),
                "timestamp": datetime.now().isoformat(),
                "relevance": 0.9
            }
        ]
    
    async def _search_github(self, query: str) -> List[Dict[str, Any]]:
        """Search GitHub repositories and discussions"""
        
        await asyncio.sleep(0.3)  # Simulate network delay
        
        return [
            {
                "source": "github",
                "title": f"GitHub Repository: {query}",
                "content": f"Open source implementation and examples for {query}. Includes code samples and community discussions.",
                "url": f"https://github.com/search?q={query.replace(' ', '+')}",
                "reliability": self.source_reliability_scores.get("github", 0.85),
                "timestamp": datetime.now().isoformat(),
                "relevance": 0.85,
                "code_examples": True
            }
        ]
    
    async def _search_stack_overflow(self, query: str) -> List[Dict[str, Any]]:
        """Search Stack Overflow for solutions and discussions"""
        
        await asyncio.sleep(0.2)  # Simulate network delay
        
        return [
            {
                "source": "stack_overflow",
                "title": f"Stack Overflow: {query}",
                "content": f"Community solutions and discussions about {query}. Includes practical examples and common pitfalls.",
                "url": f"https://stackoverflow.com/search?q={query.replace(' ', '+')}",
                "reliability": self.source_reliability_scores.get("stack_overflow", 0.75),
                "timestamp": datetime.now().isoformat(),
                "relevance": 0.8,
                "community_validated": True
            }
        ]
    
    async def _search_news(self, query: str) -> List[Dict[str, Any]]:
        """Search news sources for current information"""
        
        await asyncio.sleep(0.4)  # Simulate network delay
        
        return [
            {
                "source": "news",
                "title": f"Recent News: {query}",
                "content": f"Latest developments and news about {query}. Current trends and industry insights.",
                "url": f"https://news.example.com/search?q={query.replace(' ', '+')}",
                "reliability": self.source_reliability_scores.get("news_sites", 0.7),
                "timestamp": datetime.now().isoformat(),
                "relevance": 0.7,
                "recency": "high"
            }
        ]
    
    async def _search_academic_papers(self, query: str) -> List[Dict[str, Any]]:
        """Search academic papers and research publications"""
        
        await asyncio.sleep(0.5)  # Simulate network delay
        
        return [
            {
                "source": "academic",
                "title": f"Research Paper: {query}",
                "content": f"Academic research and peer-reviewed findings on {query}. Includes methodological approaches and empirical results.",
                "url": f"https://scholar.example.com/search?q={query.replace(' ', '+')}",
                "reliability": self.source_reliability_scores.get("academic_papers", 0.9),
                "timestamp": datetime.now().isoformat(),
                "relevance": 0.8,
                "peer_reviewed": True
            }
        ]
    
    async def _simulate_web_search(self, query: str, source_type: str = "web") -> List[Dict[str, Any]]:
        """Simulate web search results"""
        
        await asyncio.sleep(0.3)  # Simulate network delay
        
        return [
            {
                "source": source_type,
                "title": f"Web Result: {query}",
                "content": f"General web information about {query}. Includes various perspectives and practical information.",
                "url": f"https://example.com/search?q={query.replace(' ', '+')}",
                "reliability": self.source_reliability_scores.get(source_type, 0.6),
                "timestamp": datetime.now().isoformat(),
                "relevance": 0.6
            }
        ]
    
    async def _analyze_research_results(self, search_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze and process search results"""
        
        analysis = {
            "total_sources": len(search_results),
            "source_breakdown": {},
            "reliability_analysis": {},
            "content_themes": [],
            "key_insights": [],
            "credibility_score": 0.0
        }
        
        # Analyze source breakdown
        for result in search_results:
            source = result["source"]
            analysis["source_breakdown"][source] = analysis["source_breakdown"].get(source, 0) + 1
        
        # Analyze reliability
        reliability_scores = [result["reliability"] for result in search_results]
        analysis["reliability_analysis"] = {
            "average_reliability": sum(reliability_scores) / len(reliability_scores) if reliability_scores else 0,
            "high_reliability_sources": len([s for s in reliability_scores if s >= 0.8]),
            "low_reliability_sources": len([s for s in reliability_scores if s < 0.6])
        }
        
        # Extract content themes
        analysis["content_themes"] = await self._extract_content_themes(search_results)
        
        # Generate key insights
        analysis["key_insights"] = await self._extract_key_insights(search_results)
        
        # Calculate overall credibility score
        analysis["credibility_score"] = await self._calculate_credibility_score(search_results)
        
        return analysis
    
    async def _extract_content_themes(self, search_results: List[Dict[str, Any]]) -> List[str]:
        """Extract main themes from search results"""
        
        # Simple theme extraction based on content analysis
        themes = []
        
        # Analyze content for common themes
        all_content = " ".join([result["content"] for result in search_results])
        
        # Look for common technical terms and concepts
        technical_terms = re.findall(r'\b[A-Z][a-z]+(?:[A-Z][a-z]+)*\b', all_content)
        common_terms = [term for term in set(technical_terms) if all_content.count(term) >= 2]
        
        # Create themes based on common terms
        if common_terms:
            themes.extend([f"Technical focus: {term}" for term in common_terms[:3]])
        
        # Add source-specific themes
        source_types = set(result["source"] for result in search_results)
        if "official_documentation" in source_types:
            themes.append("Official guidance available")
        if "github" in source_types:
            themes.append("Open source implementations exist")
        if "academic" in source_types:
            themes.append("Research-backed information")
        
        return themes[:5]  # Limit to top 5 themes
    
    async def _extract_key_insights(self, search_results: List[Dict[str, Any]]) -> List[str]:
        """Extract key insights from search results"""
        
        insights = []
        
        # Analyze result characteristics
        high_reliability_results = [r for r in search_results if r["reliability"] >= 0.8]
        if high_reliability_results:
            insights.append(f"Found {len(high_reliability_results)} high-reliability sources")
        
        # Check for code examples
        code_results = [r for r in search_results if r.get("code_examples", False)]
        if code_results:
            insights.append("Code examples and implementations available")
        
        # Check for community validation
        community_results = [r for r in search_results if r.get("community_validated", False)]
        if community_results:
            insights.append("Community-validated solutions found")
        
        # Check for recent information
        recent_results = [r for r in search_results if r.get("recency") == "high"]
        if recent_results:
            insights.append("Recent developments and updates available")
        
        # Check for peer-reviewed content
        peer_reviewed_results = [r for r in search_results if r.get("peer_reviewed", False)]
        if peer_reviewed_results:
            insights.append("Peer-reviewed research available")
        
        return insights
    
    async def _calculate_credibility_score(self, search_results: List[Dict[str, Any]]) -> float:
        """Calculate overall credibility score for the research"""
        
        if not search_results:
            return 0.0
        
        # Weight factors for credibility calculation
        reliability_scores = [result["reliability"] for result in search_results]
        relevance_scores = [result.get("relevance", 0.5) for result in search_results]
        
        # Calculate weighted credibility
        credibility = 0.0
        
        # Base credibility from reliability
        avg_reliability = sum(reliability_scores) / len(reliability_scores)
        credibility += avg_reliability * 0.6
        
        # Add relevance factor
        avg_relevance = sum(relevance_scores) / len(relevance_scores)
        credibility += avg_relevance * 0.3
        
        # Add source diversity factor
        unique_sources = len(set(result["source"] for result in search_results))
        diversity_score = min(1.0, unique_sources / 3.0)  # Normalize to 3 sources
        credibility += diversity_score * 0.1
        
        return min(1.0, credibility)
    
    async def _synthesize_research_findings(self, analyzed_results: Dict[str, Any], 
                                          task: AgentTask) -> Dict[str, Any]:
        """Synthesize research findings into actionable insights"""
        
        synthesis = {
            "executive_summary": await self._create_executive_summary(analyzed_results, task),
            "key_findings": await self._extract_key_findings(analyzed_results),
            "recommendations": await self._generate_recommendations(analyzed_results, task),
            "implementation_guidance": await self._provide_implementation_guidance(analyzed_results, task),
            "risk_factors": await self._identify_risk_factors(analyzed_results),
            "next_steps": await self._suggest_next_steps(analyzed_results, task),
            "confidence_level": analyzed_results["credibility_score"]
        }
        
        return synthesis
    
    async def _create_executive_summary(self, analyzed_results: Dict[str, Any], 
                                      task: AgentTask) -> str:
        """Create executive summary of research findings"""
        
        total_sources = analyzed_results["total_sources"]
        credibility = analyzed_results["credibility_score"]
        themes = analyzed_results["content_themes"]
        
        summary = f"""
Research completed for: {task.description}

Sources analyzed: {total_sources}
Credibility score: {credibility:.2f}
Main themes identified: {', '.join(themes[:3])}

The research indicates {'high' if credibility >= 0.8 else 'moderate' if credibility >= 0.6 else 'limited'} confidence in the findings.
Key insights have been extracted and actionable recommendations have been formulated.
        """.strip()
        
        return summary
    
    async def _extract_key_findings(self, analyzed_results: Dict[str, Any]) -> List[str]:
        """Extract key findings from the analysis"""
        
        findings = []
        
        # Add reliability findings
        reliability = analyzed_results["reliability_analysis"]
        if reliability["high_reliability_sources"] > 0:
            findings.append(f"Identified {reliability['high_reliability_sources']} high-reliability sources")
        
        # Add theme findings
        themes = analyzed_results["content_themes"]
        if themes:
            findings.append(f"Main themes: {', '.join(themes[:2])}")
        
        # Add insight findings
        insights = analyzed_results["key_insights"]
        findings.extend(insights[:3])
        
        return findings
    
    async def _generate_recommendations(self, analyzed_results: Dict[str, Any], 
                                      task: AgentTask) -> List[str]:
        """Generate actionable recommendations"""
        
        recommendations = []
        
        credibility = analyzed_results["credibility_score"]
        insights = analyzed_results["key_insights"]
        
        # Credibility-based recommendations
        if credibility >= 0.8:
            recommendations.append("High-confidence research: Proceed with implementation")
        elif credibility >= 0.6:
            recommendations.append("Moderate-confidence research: Consider additional validation")
        else:
            recommendations.append("Low-confidence research: Conduct deeper investigation")
        
        # Insight-based recommendations
        if "Code examples and implementations available" in insights:
            recommendations.append("Leverage available code examples for implementation")
        
        if "Community-validated solutions found" in insights:
            recommendations.append("Consider community-validated approaches")
        
        if "Recent developments and updates available" in insights:
            recommendations.append("Stay updated with latest developments")
        
        # Add general recommendations
        recommendations.append("Monitor for new developments in this area")
        
        return recommendations
    
    async def _provide_implementation_guidance(self, analyzed_results: Dict[str, Any], 
                                            task: AgentTask) -> Dict[str, Any]:
        """Provide implementation guidance based on research"""
        
        guidance = {
            "approach": "standard",
            "complexity": "medium",
            "timeline": "2-4 weeks",
            "resources_needed": ["development", "testing"],
            "success_factors": [],
            "potential_challenges": []
        }
        
        # Adjust guidance based on findings
        credibility = analyzed_results["credibility_score"]
        
        if credibility >= 0.8:
            guidance["approach"] = "confident"
            guidance["complexity"] = "low"
            guidance["timeline"] = "1-2 weeks"
        elif credibility < 0.6:
            guidance["approach"] = "cautious"
            guidance["complexity"] = "high"
            guidance["timeline"] = "4-6 weeks"
            guidance["resources_needed"].append("additional_research")
        
        # Add success factors from insights
        insights = analyzed_results["key_insights"]
        if "Official guidance available" in insights:
            guidance["success_factors"].append("Follow official guidelines")
        
        if "Code examples and implementations available" in insights:
            guidance["success_factors"].append("Use proven implementations")
        
        return guidance
    
    async def _identify_risk_factors(self, analyzed_results: Dict[str, Any]) -> List[str]:
        """Identify potential risk factors"""
        
        risks = []
        
        reliability = analyzed_results["reliability_analysis"]
        
        # Low reliability risks
        if reliability["low_reliability_sources"] > reliability["high_reliability_sources"]:
            risks.append("High proportion of low-reliability sources")
        
        # Source diversity risks
        source_breakdown = analyzed_results["source_breakdown"]
        if len(source_breakdown) < 2:
            risks.append("Limited source diversity")
        
        # Credibility risks
        credibility = analyzed_results["credibility_score"]
        if credibility < 0.6:
            risks.append("Low overall credibility score")
        
        return risks
    
    async def _suggest_next_steps(self, analyzed_results: Dict[str, Any], 
                                task: AgentTask) -> List[str]:
        """Suggest next steps based on research findings"""
        
        next_steps = []
        
        credibility = analyzed_results["credibility_score"]
        insights = analyzed_results["key_insights"]
        
        # Credibility-based next steps
        if credibility >= 0.8:
            next_steps.append("Proceed with implementation planning")
        elif credibility >= 0.6:
            next_steps.append("Conduct targeted validation research")
        else:
            next_steps.append("Expand research scope and sources")
        
        # Insight-based next steps
        if "Code examples and implementations available" in insights:
            next_steps.append("Review and evaluate available implementations")
        
        if "Recent developments and updates available" in insights:
            next_steps.append("Set up monitoring for ongoing developments")
        
        # Add general next steps
        next_steps.append("Document findings and share with team")
        
        return next_steps
    
    async def _calculate_research_confidence(self, synthesized_results: Dict[str, Any]) -> float:
        """Calculate confidence in research results"""
        
        # Base confidence from synthesis confidence level
        base_confidence = synthesized_results["confidence_level"]
        
        # Adjust based on findings comprehensiveness
        findings_count = len(synthesized_results["key_findings"])
        findings_confidence = min(1.0, findings_count / 5.0)  # Normalize to 5 findings
        
        # Adjust based on recommendations quality
        recommendations_count = len(synthesized_results["recommendations"])
        recommendations_confidence = min(1.0, recommendations_count / 3.0)  # Normalize to 3 recommendations
        
        # Calculate weighted confidence
        confidence = (base_confidence * 0.5 + 
                     findings_confidence * 0.3 + 
                     recommendations_confidence * 0.2)
        
        return min(1.0, confidence)
    
    async def _get_sources_used(self, search_results: List[Dict[str, Any]]) -> List[str]:
        """Get list of sources used in research"""
        
        sources = []
        for result in search_results:
            source_info = {
                "source": result["source"],
                "title": result["title"],
                "url": result["url"],
                "reliability": result["reliability"]
            }
            sources.append(source_info)
        
        return sources
    
    async def _generate_research_recommendations(self, synthesized_results: Dict[str, Any]) -> List[str]:
        """Generate research-specific recommendations"""
        
        recommendations = synthesized_results["recommendations"]
        
        # Add research-specific recommendations
        research_recommendations = []
        
        # Source improvement recommendations
        if synthesized_results["confidence_level"] < 0.8:
            research_recommendations.append("Consider consulting additional authoritative sources")
        
        # Validation recommendations
        if "risk_factors" in synthesized_results and synthesized_results["risk_factors"]:
            research_recommendations.append("Validate findings through multiple independent sources")
        
        # Update recommendations
        research_recommendations.append("Schedule periodic research updates on this topic")
        
        return recommendations + research_recommendations
    
    async def _update_knowledge_cache(self, task: AgentTask, results: Dict[str, Any]) -> None:
        """Update knowledge cache with research results"""
        
        cache_key = f"research_{hash(task.description)}"
        
        cache_entry = {
            "task_description": task.description,
            "results": results,
            "timestamp": datetime.now().isoformat(),
            "confidence": results.get("confidence_level", 0.0),
            "sources_count": len(results.get("sources_used", [])),
            "research_type": results.get("research_type", "unknown")
        }
        
        self.knowledge_cache[cache_key] = cache_entry
        
        # Limit cache size
        if len(self.knowledge_cache) > 100:
            # Remove oldest entries
            oldest_key = min(self.knowledge_cache.keys(), 
                           key=lambda k: self.knowledge_cache[k]["timestamp"])
            del self.knowledge_cache[oldest_key]
    
    async def _cleanup_agent_resources(self) -> None:
        """Cleanup research agent specific resources"""
        
        # Clear caches
        self.knowledge_cache.clear()
        self.search_history.clear()
        
        # Reset tools
        self.tools.clear()
        
        logger.info(f"Research agent {self.agent_id} resources cleaned up")