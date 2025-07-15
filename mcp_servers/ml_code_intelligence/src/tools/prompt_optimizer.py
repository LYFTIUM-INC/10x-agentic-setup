"""
Prompt Template Optimization Engine
Self-improving prompt optimization system based on PromptBreeder techniques and DSPy optimization 
that continuously evolves prompt templates for maximum effectiveness.
"""

import random
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np
import logging
import hashlib
import json
import time
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class PromptTemplate:
    """Enhanced prompt template with evolution tracking"""
    id: str
    content: str
    task_type: str
    performance_score: float
    generation: int
    parent_ids: List[str]
    mutation_strategy: str
    metadata: Dict[str, Any]

@dataclass
class OptimizationResult:
    """Result of prompt optimization"""
    optimized_template: PromptTemplate
    improvement_score: float
    optimization_history: List[Dict[str, Any]]
    performance_predictions: Dict[str, float]

class PromptBreederOptimizer:
    """Advanced PromptBreeder implementation for self-improving prompts"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        self.population_size = self.config.get('population_size', 20)
        self.elite_size = self.config.get('elite_size', 5)
        self.mutation_rate = self.config.get('mutation_rate', 0.7)
        self.crossover_rate = self.config.get('crossover_rate', 0.3)
        self.max_generations = self.config.get('max_generations', 10)
        
        self.mutation_strategies = [
            'self_referential',
            'context_enhancement',
            'performance_focused',
            'clarity_improvement',
            'specificity_increase'
        ]
        
        self.performance_tracker = PromptPerformanceTracker()
        self.template_store = OptimizedTemplateStore()
        
    async def optimize_prompt_template(
        self, 
        base_template: str, 
        task_type: str, 
        success_metrics: Dict[str, float],
        training_data: Optional[List[Dict[str, Any]]] = None
    ) -> OptimizationResult:
        """Optimize prompt template using PromptBreeder evolution"""
        
        start_time = time.time()
        optimization_history = []
        
        try:
            # Initialize population with base template and variants
            population = await self.initialize_population(base_template, task_type)
            
            best_template = None
            best_score = 0.0
            
            for generation in range(self.max_generations):
                generation_start = time.time()
                
                # Evaluate population performance
                evaluation_results = await self.evaluate_population(
                    population, task_type, training_data or [], success_metrics
                )
                
                # Track best performer
                current_best = max(evaluation_results, key=lambda x: x['score'])
                if current_best['score'] > best_score:
                    best_score = current_best['score']
                    best_template = current_best['template']
                
                # Record generation history
                optimization_history.append({
                    'generation': generation,
                    'best_score': best_score,
                    'population_size': len(population),
                    'avg_score': np.mean([r['score'] for r in evaluation_results]),
                    'generation_time': time.time() - generation_start
                })
                
                # Early stopping if target performance reached
                target_score = success_metrics.get('target_score', 0.95)
                if best_score >= target_score:
                    logger.info(f"Target score {target_score} reached at generation {generation}")
                    break
                
                # Selection and reproduction
                population = await self.evolve_population(
                    population, evaluation_results, generation
                )
            
            # Store optimized template
            if best_template:
                await self.template_store.store_optimized_template(
                    best_template, task_type, best_score
                )
            
            # Performance predictions
            performance_predictions = await self.predict_performance(best_template, task_type)
            
            improvement_score = best_score - success_metrics.get('baseline_score', 0.0)
            
            return OptimizationResult(
                optimized_template=best_template,
                improvement_score=improvement_score,
                optimization_history=optimization_history,
                performance_predictions=performance_predictions
            )
            
        except Exception as e:
            logger.error(f"Prompt optimization failed: {e}")
            # Return baseline template
            baseline_template = PromptTemplate(
                id=f"baseline_{task_type}",
                content=base_template,
                task_type=task_type,
                performance_score=0.0,
                generation=0,
                parent_ids=[],
                mutation_strategy="baseline",
                metadata={'error': str(e)}
            )
            
            return OptimizationResult(
                optimized_template=baseline_template,
                improvement_score=0.0,
                optimization_history=[],
                performance_predictions={}
            )
    
    async def initialize_population(self, base_template: str, task_type: str) -> List[PromptTemplate]:
        """Initialize population with base template and initial variants"""
        
        population = []
        
        # Add base template
        base = PromptTemplate(
            id=f"base_{task_type}_{int(time.time())}",
            content=base_template,
            task_type=task_type,
            performance_score=0.0,
            generation=0,
            parent_ids=[],
            mutation_strategy="original",
            metadata={}
        )
        population.append(base)
        
        # Generate initial variants
        for i in range(self.population_size - 1):
            strategy = random.choice(self.mutation_strategies)
            variant = await self.mutate_template(base, strategy, 0)
            variant.id = f"init_{i}_{task_type}_{int(time.time())}"
            population.append(variant)
        
        return population
    
    async def evaluate_population(
        self, 
        population: List[PromptTemplate], 
        task_type: str, 
        training_data: List[Dict[str, Any]], 
        success_metrics: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """Evaluate performance of population"""
        
        evaluation_results = []
        
        for template in population:
            try:
                # Evaluate template performance
                score = await self.evaluate_template_performance(
                    template, task_type, training_data, success_metrics
                )
                
                evaluation_results.append({
                    'template': template,
                    'score': score,
                    'metrics': await self.get_detailed_metrics(template, score)
                })
                
            except Exception as e:
                logger.warning(f"Failed to evaluate template {template.id}: {e}")
                evaluation_results.append({
                    'template': template,
                    'score': 0.0,
                    'metrics': {'error': str(e)}
                })
        
        return evaluation_results
    
    async def evaluate_template_performance(
        self, 
        template: PromptTemplate, 
        task_type: str, 
        training_data: List[Dict[str, Any]], 
        success_metrics: Dict[str, float]
    ) -> float:
        """Evaluate individual template performance"""
        
        # Mock evaluation - in production, use actual LLM evaluation
        score_factors = []
        
        # Length consideration (prompts should be neither too short nor too long)
        length = len(template.content)
        if 100 <= length <= 1000:
            score_factors.append(0.3)
        elif 50 <= length <= 1500:
            score_factors.append(0.2)
        else:
            score_factors.append(0.1)
        
        # Clarity consideration (presence of clear instructions)
        clarity_keywords = ['analyze', 'generate', 'provide', 'ensure', 'consider']
        clarity_score = sum(1 for keyword in clarity_keywords if keyword in template.content.lower()) / len(clarity_keywords)
        score_factors.append(clarity_score * 0.2)
        
        # Context consideration (reference to context and requirements)
        context_keywords = ['context', 'requirement', 'constraint', 'standard', 'pattern']
        context_score = sum(1 for keyword in context_keywords if keyword in template.content.lower()) / len(context_keywords)
        score_factors.append(context_score * 0.2)
        
        # Task-specific considerations
        if task_type == 'code_generation':
            code_keywords = ['code', 'function', 'class', 'variable', 'syntax']
            code_score = sum(1 for keyword in code_keywords if keyword in template.content.lower()) / len(code_keywords)
            score_factors.append(code_score * 0.2)
        
        # Specificity consideration (specific vs generic instructions)
        specificity_indicators = ['specific', 'detailed', 'comprehensive', 'step-by-step', 'examples']
        specificity_score = sum(1 for indicator in specificity_indicators if indicator in template.content.lower()) / len(specificity_indicators)
        score_factors.append(specificity_score * 0.1)
        
        return min(sum(score_factors), 1.0)
    
    async def get_detailed_metrics(self, template: PromptTemplate, score: float) -> Dict[str, Any]:
        """Get detailed metrics for template evaluation"""
        
        return {
            'overall_score': score,
            'length': len(template.content),
            'clarity': await self._assess_clarity(template.content),
            'specificity': await self._assess_specificity(template.content),
            'context_awareness': await self._assess_context_awareness(template.content),
            'task_alignment': await self._assess_task_alignment(template.content, template.task_type)
        }
    
    async def evolve_population(
        self, 
        population: List[PromptTemplate], 
        evaluation_results: List[Dict[str, Any]], 
        generation: int
    ) -> List[PromptTemplate]:
        """Evolve population through selection and reproduction"""
        
        # Sort by performance
        sorted_results = sorted(evaluation_results, key=lambda x: x['score'], reverse=True)
        
        # Select elite templates
        elite_templates = [result['template'] for result in sorted_results[:self.elite_size]]
        
        # Create new population
        new_population = elite_templates.copy()
        
        # Fill remaining population with mutations and crossovers
        while len(new_population) < self.population_size:
            if random.random() < self.crossover_rate and len(elite_templates) >= 2:
                # Crossover
                parent1, parent2 = random.sample(elite_templates, 2)
                offspring = await self.crossover_templates(parent1, parent2, generation)
                new_population.append(offspring)
            else:
                # Mutation
                parent = random.choice(elite_templates)
                strategy = random.choice(self.mutation_strategies)
                mutant = await self.mutate_template(parent, strategy, generation)
                new_population.append(mutant)
        
        return new_population[:self.population_size]
    
    async def mutate_template(
        self, 
        template: PromptTemplate, 
        strategy: str, 
        generation: int
    ) -> PromptTemplate:
        """Apply mutation strategy to create template variant"""
        
        if strategy == 'self_referential':
            mutated_content = await self.self_referential_mutation(template)
        elif strategy == 'context_enhancement':
            mutated_content = await self.context_enhancement_mutation(template)
        elif strategy == 'performance_focused':
            mutated_content = await self.performance_focused_mutation(template)
        elif strategy == 'clarity_improvement':
            mutated_content = await self.clarity_improvement_mutation(template)
        elif strategy == 'specificity_increase':
            mutated_content = await self.specificity_increase_mutation(template)
        else:
            mutated_content = template.content
        
        return PromptTemplate(
            id=f"gen{generation}_{strategy}_{random.randint(1000, 9999)}",
            content=mutated_content,
            task_type=template.task_type,
            performance_score=0.0,
            generation=generation + 1,
            parent_ids=[template.id],
            mutation_strategy=strategy,
            metadata={'mutation_applied': strategy, 'parent_score': template.performance_score}
        )
    
    async def self_referential_mutation(self, template: PromptTemplate) -> str:
        """PromptBreeder self-referential improvement mutation"""
        
        # Simulate self-referential improvement
        improvements = [
            "Be more specific in your instructions.",
            "Consider the context and requirements carefully.",
            "Provide clear, actionable guidance.",
            "Include examples where appropriate.",
            "Ensure consistency with established patterns."
        ]
        
        selected_improvement = random.choice(improvements)
        
        # Add improvement instruction to the template
        improved_template = f"{template.content}\n\nAdditional Guidance: {selected_improvement}"
        
        return improved_template
    
    async def context_enhancement_mutation(self, template: PromptTemplate) -> str:
        """Enhance template with additional context awareness"""
        
        context_additions = [
            "Consider the project architecture and existing patterns.",
            "Take into account the coding standards and style guidelines.",
            "Ensure compatibility with existing dependencies and frameworks.",
            "Consider performance implications and optimization opportunities.",
            "Think about maintainability and future extensibility."
        ]
        
        selected_addition = random.choice(context_additions)
        
        # Insert context enhancement
        enhanced_template = template.content + f"\n\nAdditional Context: {selected_addition}"
        
        return enhanced_template
    
    async def performance_focused_mutation(self, template: PromptTemplate) -> str:
        """Optimize template for better performance metrics"""
        
        performance_improvements = [
            "Prioritize code quality and best practices.",
            "Focus on generating efficient and optimized solutions.",
            "Ensure comprehensive error handling and edge case consideration.",
            "Emphasize clear documentation and commenting.",
            "Generate code that follows SOLID principles and design patterns."
        ]
        
        improvement = random.choice(performance_improvements)
        
        # Add performance focus
        enhanced_template = template.content.replace(
            "Generate",
            f"Generate high-quality code that {improvement.lower()}"
        )
        
        if enhanced_template == template.content:
            enhanced_template = f"{template.content}\n\nPerformance Focus: {improvement}"
        
        return enhanced_template

    async def clarity_improvement_mutation(self, template: PromptTemplate) -> str:
        """Improve template clarity and readability"""
        
        clarity_improvements = [
            "Step-by-step approach:",
            "Clear requirements:",
            "Specific examples:",
            "Detailed instructions:",
            "Structured format:"
        ]
        
        improvement = random.choice(clarity_improvements)
        
        # Add clarity improvement
        if ":" in template.content:
            # Insert improvement after first colon
            parts = template.content.split(":", 1)
            enhanced_template = f"{parts[0]}: {improvement} {parts[1]}"
        else:
            enhanced_template = f"{improvement}\n{template.content}"
        
        return enhanced_template

    async def specificity_increase_mutation(self, template: PromptTemplate) -> str:
        """Increase template specificity"""
        
        specificity_additions = [
            "Provide specific implementation details.",
            "Include concrete examples and use cases.",
            "Define clear success criteria.",
            "Specify expected output format.",
            "Detail any constraints or limitations."
        ]
        
        addition = random.choice(specificity_additions)
        
        # Add specificity
        enhanced_template = f"{template.content}\n\nSpecific Requirements: {addition}"
        
        return enhanced_template

    async def crossover_templates(
        self, 
        parent1: PromptTemplate, 
        parent2: PromptTemplate, 
        generation: int
    ) -> PromptTemplate:
        """Create offspring through crossover"""
        
        # Split templates into sections
        sections1 = await self.split_template_sections(parent1.content)
        sections2 = await self.split_template_sections(parent2.content)
        
        # Crossover sections
        offspring_sections = []
        max_sections = max(len(sections1), len(sections2))
        
        for i in range(max_sections):
            section1 = sections1[i] if i < len(sections1) else ""
            section2 = sections2[i] if i < len(sections2) else ""
            
            if random.random() < 0.5:
                offspring_sections.append(section1)
            else:
                offspring_sections.append(section2)
        
        # Combine sections
        offspring_content = "\n\n".join(filter(None, offspring_sections))
        
        return PromptTemplate(
            id=f"crossover_{generation}_{random.randint(1000, 9999)}",
            content=offspring_content,
            task_type=parent1.task_type,
            performance_score=0.0,
            generation=generation + 1,
            parent_ids=[parent1.id, parent2.id],
            mutation_strategy="crossover",
            metadata={
                'crossover_applied': True,
                'parent_scores': [parent1.performance_score, parent2.performance_score]
            }
        )

    async def split_template_sections(self, content: str) -> List[str]:
        """Split template into sections for crossover"""
        
        # Simple section splitting - in production, use more sophisticated parsing
        sections = content.split('\n\n')
        return [section.strip() for section in sections if section.strip()]

    async def predict_performance(self, template: PromptTemplate, task_type: str) -> Dict[str, float]:
        """Predict performance for optimized template"""
        
        # Mock performance predictions
        return {
            'quality_score': min(template.performance_score + 0.1, 1.0),
            'efficiency_score': 0.85,
            'clarity_score': await self._assess_clarity(template.content),
            'context_score': await self._assess_context_awareness(template.content)
        }

    async def _assess_clarity(self, content: str) -> float:
        """Assess clarity of template content"""
        clarity_indicators = ['clear', 'specific', 'detailed', 'step', 'example']
        score = sum(1 for indicator in clarity_indicators if indicator in content.lower()) / len(clarity_indicators)
        return min(score, 1.0)

    async def _assess_specificity(self, content: str) -> float:
        """Assess specificity of template content"""
        specificity_indicators = ['specific', 'exact', 'precise', 'detailed', 'particular']
        score = sum(1 for indicator in specificity_indicators if indicator in content.lower()) / len(specificity_indicators)
        return min(score, 1.0)

    async def _assess_context_awareness(self, content: str) -> float:
        """Assess context awareness of template content"""
        context_indicators = ['context', 'consider', 'take into account', 'based on', 'according to']
        score = sum(1 for indicator in context_indicators if indicator in content.lower()) / len(context_indicators)
        return min(score, 1.0)

    async def _assess_task_alignment(self, content: str, task_type: str) -> float:
        """Assess alignment with specific task type"""
        
        task_keywords = {
            'code_generation': ['code', 'function', 'class', 'implement', 'generate'],
            'analysis': ['analyze', 'examine', 'evaluate', 'assess', 'review'],
            'refactoring': ['refactor', 'improve', 'optimize', 'restructure', 'enhance']
        }
        
        keywords = task_keywords.get(task_type, [])
        if not keywords:
            return 0.5  # Neutral score for unknown task types
        
        score = sum(1 for keyword in keywords if keyword in content.lower()) / len(keywords)
        return min(score, 1.0)


class SelfImprovingPromptTemplate:
    """Self-improving prompt template with adaptive optimization"""
    
    def __init__(self, base_template: str, optimization_config: Dict[str, Any]):
        self.template = base_template
        self.performance_history = []
        self.optimization_cycles = 0
        self.improvement_threshold = optimization_config.get('threshold', 0.8)
        self.max_cycles = optimization_config.get('max_cycles', 5)
        self.target_performance = optimization_config.get('target_performance', 0.95)
        
        self.prompt_breeder = PromptBreederOptimizer(optimization_config)
        
    async def execute_and_learn(self, context: Dict[str, Any], task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute template and adapt based on performance"""
        
        # Execute current template
        start_time = time.time()
        result = await self.execute_template(context, task)
        execution_time = time.time() - start_time
        
        # Evaluate performance
        performance = await self.evaluate_performance(result, task.get('expected_outcome'))
        
        # Record performance
        self.performance_history.append({
            'timestamp': start_time,
            'performance': performance,
            'execution_time': execution_time,
            'context': context,
            'task': task
        })
        
        # Trigger optimization if needed
        if self.should_optimize(performance):
            await self.optimize_template(context, task, performance)
        
        return {
            'result': result,
            'performance': performance,
            'template_version': self.optimization_cycles,
            'improvement_applied': self.optimization_cycles > 0
        }
    
    async def execute_template(self, context: Dict[str, Any], task: Dict[str, Any]) -> str:
        """Execute the current template"""
        
        # Mock template execution
        template_with_context = self.template.format(
            context=context.get('summary', 'Unknown context'),
            task=task.get('description', 'Unknown task')
        )
        
        # Simulate execution result
        return f"Executed: {template_with_context[:100]}..."
    
    async def evaluate_performance(self, result: str, expected_outcome: Optional[str] = None) -> Dict[str, float]:
        """Evaluate performance of template execution"""
        
        # Mock performance evaluation
        base_score = 0.7
        
        # Length consideration
        if 50 <= len(result) <= 500:
            base_score += 0.1
        
        # Content quality consideration
        if expected_outcome and expected_outcome.lower() in result.lower():
            base_score += 0.15
        
        return {
            'overall_score': min(base_score, 1.0),
            'relevance_score': 0.8,
            'quality_score': 0.75,
            'completeness_score': 0.85
        }
    
    async def optimize_template(
        self, 
        context: Dict[str, Any], 
        task: Dict[str, Any], 
        performance: Dict[str, float]
    ):
        """Optimize template based on performance feedback"""
        
        if self.optimization_cycles < self.max_cycles:
            # Prepare training data from performance history
            training_data = self.prepare_training_data()
            
            # Calculate performance gap
            performance_gap = self.calculate_performance_gap(performance)
            
            # Use PromptBreeder to improve template
            optimization_result = await self.prompt_breeder.optimize_prompt_template(
                base_template=self.template,
                task_type=task.get('type', 'unknown'),
                success_metrics={
                    'target_score': self.target_performance,
                    'current_gap': performance_gap,
                    'baseline_score': performance.get('overall_score', 0.0)
                },
                training_data=training_data
            )
            
            # Validate improvement
            if await self.validate_improvement(optimization_result.optimized_template, context, task):
                self.template = optimization_result.optimized_template.content
                self.optimization_cycles += 1
                
                # Log optimization
                await self.log_optimization(
                    old_template=self.template,
                    new_template=optimization_result.optimized_template.content,
                    performance_improvement=optimization_result.improvement_score
                )
    
    def should_optimize(self, performance: Dict[str, float]) -> bool:
        """Determine if template optimization is needed"""
        
        current_score = performance.get('overall_score', 0.0)
        
        # Optimize if below threshold
        if current_score < self.improvement_threshold:
            return True
        
        # Optimize if performance is declining
        if len(self.performance_history) >= 3:
            recent_scores = [p['performance']['overall_score'] for p in self.performance_history[-3:]]
            if all(recent_scores[i] <= recent_scores[i-1] for i in range(1, len(recent_scores))):
                return True
        
        return False
    
    def prepare_training_data(self) -> List[Dict[str, Any]]:
        """Prepare training data from performance history"""
        
        training_data = []
        for entry in self.performance_history[-10:]:  # Use last 10 entries
            training_data.append({
                'context': entry['context'],
                'task': entry['task'],
                'performance': entry['performance']
            })
        
        return training_data
    
    def calculate_performance_gap(self, current_performance: Dict[str, float]) -> float:
        """Calculate gap between current and target performance"""
        
        current_score = current_performance.get('overall_score', 0.0)
        return max(0, self.target_performance - current_score)
    
    async def validate_improvement(self, optimized_template: PromptTemplate, context: Dict[str, Any], task: Dict[str, Any]) -> bool:
        """Validate that optimized template is actually better"""
        
        # Simple validation - check if template is longer and more specific
        original_length = len(self.template)
        optimized_length = len(optimized_template.content)
        
        # Templates should generally become more detailed through optimization
        return optimized_length >= original_length * 0.9  # Allow slight reduction
    
    async def log_optimization(self, old_template: str, new_template: str, performance_improvement: float):
        """Log optimization for tracking"""
        
        logger.info(f"Template optimized. Improvement: {performance_improvement:.3f}")
        logger.debug(f"Old template length: {len(old_template)}")
        logger.debug(f"New template length: {len(new_template)}")


class PromptPerformanceTracker:
    """Track and analyze prompt template performance over time"""
    
    def __init__(self):
        self.performance_log = []
        self.template_metrics = {}
    
    async def track_performance(self, template_id: str, performance_data: Dict[str, Any]):
        """Track performance for a specific template"""
        
        entry = {
            'template_id': template_id,
            'timestamp': time.time(),
            'performance': performance_data,
            'context': performance_data.get('context', {})
        }
        
        self.performance_log.append(entry)
        
        # Update template metrics
        if template_id not in self.template_metrics:
            self.template_metrics[template_id] = {
                'total_executions': 0,
                'avg_performance': 0.0,
                'best_performance': 0.0,
                'trend': 'unknown'
            }
        
        metrics = self.template_metrics[template_id]
        metrics['total_executions'] += 1
        
        current_score = performance_data.get('overall_score', 0.0)
        metrics['avg_performance'] = (
            (metrics['avg_performance'] * (metrics['total_executions'] - 1) + current_score) /
            metrics['total_executions']
        )
        
        if current_score > metrics['best_performance']:
            metrics['best_performance'] = current_score
    
    async def analyze_trends(self, template_id: str, time_window: str = "30d") -> Dict[str, Any]:
        """Analyze performance trends for a template"""
        
        # Filter entries for the template and time window
        cutoff_time = time.time() - self._parse_time_window(time_window)
        entries = [
            entry for entry in self.performance_log
            if entry['template_id'] == template_id and entry['timestamp'] >= cutoff_time
        ]
        
        if not entries:
            return {'trend': 'no_data', 'metrics': {}}
        
        # Calculate trend
        scores = [entry['performance'].get('overall_score', 0.0) for entry in entries]
        trend = 'improving' if scores[-1] > scores[0] else 'declining' if scores[-1] < scores[0] else 'stable'
        
        return {
            'trend': trend,
            'metrics': {
                'total_executions': len(entries),
                'avg_score': np.mean(scores),
                'min_score': min(scores),
                'max_score': max(scores),
                'std_score': np.std(scores)
            }
        }
    
    def _parse_time_window(self, time_window: str) -> int:
        """Parse time window string to seconds"""
        
        if time_window.endswith('d'):
            return int(time_window[:-1]) * 24 * 60 * 60
        elif time_window.endswith('h'):
            return int(time_window[:-1]) * 60 * 60
        else:
            return 30 * 24 * 60 * 60  # Default to 30 days


class OptimizedTemplateStore:
    """Store and retrieve optimized prompt templates"""
    
    def __init__(self, storage_path: str = "data/optimized_templates.json"):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.templates = self._load_templates()
    
    async def store_optimized_template(self, template: PromptTemplate, task_type: str, score: float):
        """Store an optimized template"""
        
        template_data = {
            'id': template.id,
            'content': template.content,
            'task_type': task_type,
            'performance_score': score,
            'generation': template.generation,
            'parent_ids': template.parent_ids,
            'mutation_strategy': template.mutation_strategy,
            'metadata': template.metadata,
            'timestamp': time.time()
        }
        
        self.templates[template.id] = template_data
        await self._save_templates()
    
    async def get_best_template(self, task_type: str) -> Optional[PromptTemplate]:
        """Get the best template for a task type"""
        
        task_templates = [
            template for template in self.templates.values()
            if template['task_type'] == task_type
        ]
        
        if not task_templates:
            return None
        
        best_template_data = max(task_templates, key=lambda x: x['performance_score'])
        
        return PromptTemplate(
            id=best_template_data['id'],
            content=best_template_data['content'],
            task_type=best_template_data['task_type'],
            performance_score=best_template_data['performance_score'],
            generation=best_template_data['generation'],
            parent_ids=best_template_data['parent_ids'],
            mutation_strategy=best_template_data['mutation_strategy'],
            metadata=best_template_data['metadata']
        )
    
    async def get_template_by_id(self, template_id: str) -> Optional[PromptTemplate]:
        """Get template by ID"""
        
        template_data = self.templates.get(template_id)
        if not template_data:
            return None
        
        return PromptTemplate(
            id=template_data['id'],
            content=template_data['content'],
            task_type=template_data['task_type'],
            performance_score=template_data['performance_score'],
            generation=template_data['generation'],
            parent_ids=template_data['parent_ids'],
            mutation_strategy=template_data['mutation_strategy'],
            metadata=template_data['metadata']
        )
    
    def _load_templates(self) -> Dict[str, Any]:
        """Load templates from storage"""
        
        if not self.storage_path.exists():
            return {}
        
        try:
            with open(self.storage_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load templates: {e}")
            return {}
    
    async def _save_templates(self):
        """Save templates to storage"""
        
        try:
            with open(self.storage_path, 'w') as f:
                json.dump(self.templates, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save templates: {e}")


class PromptOptimizationEngine:
    """Main engine for prompt optimization"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.prompt_breeder = PromptBreederOptimizer(config)
        self.template_store = OptimizedTemplateStore()
        self.performance_tracker = PromptPerformanceTracker()
    
    async def get_optimized_templates(self, task_type: str) -> Dict[str, Any]:
        """Get optimized templates for a task type"""
        
        best_template = await self.template_store.get_best_template(task_type)
        
        if best_template:
            return {
                'has_optimized': True,
                'template': best_template,
                'performance_score': best_template.performance_score
            }
        else:
            return {
                'has_optimized': False,
                'template': None,
                'performance_score': 0.0
            }
    
    async def optimize_template_for_task(
        self, 
        base_template: str, 
        task_type: str, 
        target_performance: float = 0.95
    ) -> OptimizationResult:
        """Optimize a template for a specific task"""
        
        success_metrics = {
            'target_score': target_performance,
            'baseline_score': 0.5
        }
        
        return await self.prompt_breeder.optimize_prompt_template(
            base_template=base_template,
            task_type=task_type,
            success_metrics=success_metrics,
            training_data=[]
        )