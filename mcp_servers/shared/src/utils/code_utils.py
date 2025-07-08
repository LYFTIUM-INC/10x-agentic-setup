"""
Code Analysis Utilities for MCP Servers
AST parsing, language detection, and code quality analysis
"""

import ast
import re
import subprocess
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass
from pathlib import Path
import hashlib

try:
    import tree_sitter
    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False

import logging
logger = logging.getLogger(__name__)


@dataclass
class CodeMetrics:
    """Code metrics and statistics"""
    lines_of_code: int = 0
    lines_of_comments: int = 0
    cyclomatic_complexity: int = 0
    cognitive_complexity: int = 0
    maintainability_index: float = 0.0
    technical_debt_ratio: float = 0.0
    security_score: float = 100.0
    quality_score: float = 0.0


@dataclass
class CodeIssue:
    """Represents a code issue or suggestion"""
    type: str  # "error", "warning", "suggestion", "security"
    line: int
    column: int
    message: str
    severity: str  # "low", "medium", "high", "critical"
    rule: str
    file_path: Optional[str] = None


class LanguageDetector:
    """Detect programming language from code or file extension"""
    
    LANGUAGE_PATTERNS = {
        'python': [
            r'^\s*import\s+\w+',
            r'^\s*from\s+\w+\s+import',
            r'^\s*def\s+\w+\s*\(',
            r'^\s*class\s+\w+\s*:',
            r'^\s*if\s+__name__\s*==\s*["\']__main__["\']',
        ],
        'javascript': [
            r'^\s*function\s+\w+\s*\(',
            r'^\s*const\s+\w+\s*=',
            r'^\s*let\s+\w+\s*=',
            r'^\s*var\s+\w+\s*=',
            r'console\.log\s*\(',
            r'require\s*\(',
            r'module\.exports',
        ],
        'typescript': [
            r'^\s*interface\s+\w+',
            r'^\s*type\s+\w+\s*=',
            r':\s*\w+(\[\])?(\s*\|\s*\w+)*\s*[=;]',
            r'^\s*import\s+.*\s+from\s+["\']',
            r'^\s*export\s+(interface|type|class|function)',
        ],
        'java': [
            r'^\s*public\s+class\s+\w+',
            r'^\s*package\s+[\w.]+\s*;',
            r'^\s*import\s+[\w.]+\s*;',
            r'public\s+static\s+void\s+main',
            r'System\.out\.print',
        ],
        'cpp': [
            r'^\s*#include\s*<\w+>',
            r'^\s*using\s+namespace\s+\w+',
            r'^\s*int\s+main\s*\(',
            r'std::\w+',
            r'cout\s*<<',
        ],
        'rust': [
            r'^\s*fn\s+\w+\s*\(',
            r'^\s*use\s+\w+',
            r'^\s*mod\s+\w+',
            r'println!\s*\(',
            r'let\s+mut\s+\w+',
        ],
        'go': [
            r'^\s*package\s+\w+',
            r'^\s*import\s+["\(]',
            r'^\s*func\s+\w+\s*\(',
            r'fmt\.Print',
            r'go\s+func\s*\(',
        ]
    }
    
    EXTENSION_MAP = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.tsx': 'typescript',
        '.jsx': 'javascript',
        '.java': 'java',
        '.cpp': 'cpp',
        '.cc': 'cpp',
        '.cxx': 'cpp',
        '.c': 'c',
        '.h': 'c',
        '.hpp': 'cpp',
        '.rs': 'rust',
        '.go': 'go',
        '.php': 'php',
        '.rb': 'ruby',
        '.swift': 'swift',
        '.kt': 'kotlin',
        '.scala': 'scala',
        '.cs': 'csharp',
    }
    
    @classmethod
    def detect_by_extension(cls, filename: str) -> Optional[str]:
        """Detect language by file extension"""
        ext = Path(filename).suffix.lower()
        return cls.EXTENSION_MAP.get(ext)
    
    @classmethod
    def detect_by_content(cls, code: str) -> Optional[str]:
        """Detect language by analyzing code content"""
        scores = {}
        
        for language, patterns in cls.LANGUAGE_PATTERNS.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, code, re.MULTILINE | re.IGNORECASE))
                score += matches
            scores[language] = score
        
        if not scores or max(scores.values()) == 0:
            return None
        
        return max(scores, key=scores.get)
    
    @classmethod
    def detect(cls, code: str, filename: Optional[str] = None) -> str:
        """Detect language using both content and filename"""
        # Try filename first
        if filename:
            lang = cls.detect_by_extension(filename)
            if lang:
                return lang
        
        # Fall back to content analysis
        lang = cls.detect_by_content(code)
        return lang or 'text'


class PythonAnalyzer:
    """Python-specific code analysis using AST"""
    
    def __init__(self):
        self.issues: List[CodeIssue] = []
    
    def analyze(self, code: str) -> Tuple[CodeMetrics, List[CodeIssue]]:
        """Analyze Python code and return metrics and issues"""
        self.issues = []
        
        try:
            tree = ast.parse(code)
            metrics = self._calculate_metrics(code, tree)
            self._check_security_issues(tree)
            self._check_quality_issues(tree)
            
            return metrics, self.issues
        except SyntaxError as e:
            issue = CodeIssue(
                type="error",
                line=e.lineno or 0,
                column=e.offset or 0,
                message=f"Syntax error: {e.msg}",
                severity="high",
                rule="syntax-error"
            )
            return CodeMetrics(), [issue]
    
    def _calculate_metrics(self, code: str, tree: ast.AST) -> CodeMetrics:
        """Calculate code metrics"""
        lines = code.split('\n')
        loc = len([line for line in lines if line.strip() and not line.strip().startswith('#')])
        comments = len([line for line in lines if line.strip().startswith('#')])
        
        # Calculate cyclomatic complexity
        complexity = self._calculate_cyclomatic_complexity(tree)
        
        # Calculate cognitive complexity (simplified)
        cognitive = self._calculate_cognitive_complexity(tree)
        
        # Calculate maintainability index (simplified)
        import math
        mi = max(0, 171 - 5.2 * math.log(max(1, loc)) - 0.23 * complexity - 16.2 * math.log(max(1, loc)))
        
        return CodeMetrics(
            lines_of_code=loc,
            lines_of_comments=comments,
            cyclomatic_complexity=complexity,
            cognitive_complexity=cognitive,
            maintainability_index=mi,
            quality_score=min(100, mi * 0.6 + (100 - complexity * 2))
        )
    
    def _calculate_cyclomatic_complexity(self, tree: ast.AST) -> int:
        """Calculate cyclomatic complexity"""
        complexity = 1  # Base complexity
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler,
                               ast.With, ast.Assert, ast.BoolOp)):
                complexity += 1
            elif isinstance(node, ast.FunctionDef):
                complexity += 1
        
        return complexity
    
    def _calculate_cognitive_complexity(self, tree: ast.AST) -> int:
        """Calculate cognitive complexity (simplified)"""
        cognitive = 0
        nesting_level = 0
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For)):
                cognitive += 1 + nesting_level
            elif isinstance(node, ast.BoolOp):
                cognitive += 1
        
        return cognitive
    
    def _check_security_issues(self, tree: ast.AST) -> None:
        """Check for security issues"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                    if func_name in ['eval', 'exec', 'compile']:
                        self.issues.append(CodeIssue(
                            type="security",
                            line=node.lineno,
                            column=node.col_offset,
                            message=f"Dangerous function '{func_name}' can execute arbitrary code",
                            severity="critical",
                            rule="dangerous-function"
                        ))
                    elif func_name == 'input' and any(
                        isinstance(arg, ast.Constant) and 'password' in str(arg.value).lower()
                        for arg in node.args
                    ):
                        self.issues.append(CodeIssue(
                            type="security",
                            line=node.lineno,
                            column=node.col_offset,
                            message="Use getpass for password input",
                            severity="medium",
                            rule="password-input"
                        ))
    
    def _check_quality_issues(self, tree: ast.AST) -> None:
        """Check for code quality issues"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check function length
                if hasattr(node, 'end_lineno') and node.end_lineno:
                    length = node.end_lineno - node.lineno
                    if length > 50:
                        self.issues.append(CodeIssue(
                            type="warning",
                            line=node.lineno,
                            column=node.col_offset,
                            message=f"Function '{node.name}' is too long ({length} lines)",
                            severity="medium",
                            rule="function-too-long"
                        ))
                
                # Check parameter count
                if len(node.args.args) > 7:
                    self.issues.append(CodeIssue(
                        type="warning",
                        line=node.lineno,
                        column=node.col_offset,
                        message=f"Function '{node.name}' has too many parameters",
                        severity="medium",
                        rule="too-many-parameters"
                    ))


class GeneralCodeAnalyzer:
    """General code analyzer for multiple languages"""
    
    def __init__(self):
        self.python_analyzer = PythonAnalyzer()
    
    def analyze_code(self, code: str, language: str, filename: Optional[str] = None) -> Tuple[CodeMetrics, List[CodeIssue]]:
        """Analyze code and return metrics and issues"""
        if not language:
            language = LanguageDetector.detect(code, filename)
        
        if language == 'python':
            return self.python_analyzer.analyze(code)
        else:
            return self._analyze_general(code, language)
    
    def _analyze_general(self, code: str, language: str) -> Tuple[CodeMetrics, List[CodeIssue]]:
        """General analysis for non-Python languages"""
        lines = code.split('\n')
        
        # Basic metrics
        loc = len([line for line in lines if line.strip()])
        comments = self._count_comments(lines, language)
        
        # Simple complexity estimation
        complexity = self._estimate_complexity(code, language)
        
        metrics = CodeMetrics(
            lines_of_code=loc,
            lines_of_comments=comments,
            cyclomatic_complexity=complexity,
            quality_score=max(0, 100 - complexity * 2)
        )
        
        # Basic issue detection
        issues = self._detect_general_issues(code, language)
        
        return metrics, issues
    
    def _count_comments(self, lines: List[str], language: str) -> int:
        """Count comment lines for different languages"""
        comment_patterns = {
            'javascript': [r'^\s*//', r'/\*.*\*/'],
            'typescript': [r'^\s*//', r'/\*.*\*/'],
            'java': [r'^\s*//', r'/\*.*\*/'],
            'cpp': [r'^\s*//', r'/\*.*\*/', r'^\s*#'],
            'rust': [r'^\s*//'],
            'go': [r'^\s*//'],
        }
        
        patterns = comment_patterns.get(language, [r'^\s*//'])
        count = 0
        
        for line in lines:
            for pattern in patterns:
                if re.match(pattern, line):
                    count += 1
                    break
        
        return count
    
    def _estimate_complexity(self, code: str, language: str) -> int:
        """Estimate cyclomatic complexity for different languages"""
        complexity_keywords = {
            'javascript': ['if', 'while', 'for', 'switch', 'case', 'catch', 'function'],
            'typescript': ['if', 'while', 'for', 'switch', 'case', 'catch', 'function'],
            'java': ['if', 'while', 'for', 'switch', 'case', 'catch', 'public.*method'],
            'cpp': ['if', 'while', 'for', 'switch', 'case', 'catch'],
            'rust': ['if', 'while', 'for', 'match', 'fn'],
            'go': ['if', 'for', 'switch', 'case', 'func'],
        }
        
        keywords = complexity_keywords.get(language, ['if', 'while', 'for'])
        complexity = 1  # Base complexity
        
        for keyword in keywords:
            pattern = r'\b' + keyword + r'\b'
            matches = len(re.findall(pattern, code, re.IGNORECASE))
            complexity += matches
        
        return complexity
    
    def _detect_general_issues(self, code: str, language: str) -> List[CodeIssue]:
        """Detect general issues across languages"""
        issues = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Long lines
            if len(line) > 120:
                issues.append(CodeIssue(
                    type="warning",
                    line=i,
                    column=120,
                    message="Line too long",
                    severity="low",
                    rule="line-too-long"
                ))
            
            # TODO comments
            if 'TODO' in line.upper() or 'FIXME' in line.upper():
                issues.append(CodeIssue(
                    type="suggestion",
                    line=i,
                    column=0,
                    message="TODO/FIXME comment found",
                    severity="low",
                    rule="todo-comment"
                ))
        
        return issues


class CodeHasher:
    """Generate hashes for code deduplication and similarity"""
    
    @staticmethod
    def hash_code(code: str) -> str:
        """Generate SHA-256 hash of code"""
        return hashlib.sha256(code.encode()).hexdigest()
    
    @staticmethod
    def normalize_code(code: str, language: str) -> str:
        """Normalize code for better similarity detection"""
        # Remove comments and whitespace
        lines = []
        for line in code.split('\n'):
            # Remove leading/trailing whitespace
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Remove comments based on language
            if language in ['python']:
                if line.startswith('#'):
                    continue
                # Remove inline comments
                if '#' in line:
                    line = line[:line.find('#')].strip()
            elif language in ['javascript', 'typescript', 'java', 'cpp']:
                if line.startswith('//'):
                    continue
                # Remove inline comments
                if '//' in line:
                    line = line[:line.find('//')].strip()
            
            if line:
                lines.append(line)
        
        return '\n'.join(lines)
    
    @classmethod
    def similarity_hash(cls, code: str, language: str) -> str:
        """Generate hash for similarity comparison"""
        normalized = cls.normalize_code(code, language)
        return cls.hash_code(normalized)


# Convenience functions
def analyze_code_file(filepath: str) -> Tuple[CodeMetrics, List[CodeIssue]]:
    """Analyze a code file"""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    code = path.read_text(encoding='utf-8')
    language = LanguageDetector.detect(code, str(path))
    
    analyzer = GeneralCodeAnalyzer()
    return analyzer.analyze_code(code, language, str(path))


def get_code_summary(code: str, language: Optional[str] = None) -> Dict[str, Any]:
    """Get a summary of code including metrics and basic info"""
    if not language:
        language = LanguageDetector.detect(code)
    
    analyzer = GeneralCodeAnalyzer()
    metrics, issues = analyzer.analyze_code(code, language)
    
    return {
        'language': language,
        'lines_of_code': metrics.lines_of_code,
        'complexity': metrics.cyclomatic_complexity,
        'quality_score': metrics.quality_score,
        'issues_count': len(issues),
        'critical_issues': len([i for i in issues if i.severity == 'critical']),
        'hash': CodeHasher.hash_code(code),
        'similarity_hash': CodeHasher.similarity_hash(code, language)
    }


# Example usage
if __name__ == "__main__":
    sample_code = '''
def calculate_fibonacci(n):
    """Calculate fibonacci number"""
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

# TODO: Optimize this function
def main():
    result = calculate_fibonacci(10)
    print(f"Fibonacci(10) = {result}")

if __name__ == "__main__":
    main()
'''
    
    analyzer = GeneralCodeAnalyzer()
    metrics, issues = analyzer.analyze_code(sample_code, 'python')
    
    print("Metrics:", metrics)
    print("Issues:", [f"{i.type}: {i.message} (line {i.line})" for i in issues])
    print("Summary:", get_code_summary(sample_code, 'python'))