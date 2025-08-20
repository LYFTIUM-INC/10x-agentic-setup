#!/usr/bin/env python3
"""
Enhanced Input Validation for Claude Code
Comprehensive input sanitization and validation
"""

import re
import html
import json
from typing import Any, Dict, List, Tuple, Optional
import logging

class EnhancedInputValidator:
    """Comprehensive input validation and sanitization"""
    
    def __init__(self):
        # Dangerous command patterns
        self.dangerous_command_patterns = [
            r';\s*rm\s+-rf',           # Dangerous deletions
            r';\s*sudo',               # Privilege escalation
            r';\s*su\s+',              # User switching
            r';\s*chmod\s+777',        # Permission changes
            r';\s*wget\s+http',        # External downloads
            r';\s*curl\s+.*\|\s*sh',   # Pipe to shell
            r';\s*nc\s+-l',            # Netcat listeners
            r';\s*python.*-c\s+',      # Python code execution
            r';\s*eval\s*\(',          # Code evaluation
            r';\s*exec\s*\(',          # Code execution
            r'\$\(.*\)',               # Command substitution
            r'`.*`',                   # Command substitution
            r'<\s*script',             # Script injection
            r'javascript:',            # JavaScript URLs
            r'data:.*base64',          # Data URLs
            r'file:/',                 # File URLs
            r'&&\s+wget\s+http',       # Command chaining with wget
            r'&&\s+curl\s+http',       # Command chaining with curl
            r'\|\s*sh\s*$',            # Pipe to shell at end
            r'\|\s*bash',              # Pipe to bash
            r'bash\s+-c\s+',           # Bash -c execution
            r'sh\s+-c\s+',             # Shell -c execution
        ]
        
        # SQL injection patterns
        self.sql_injection_patterns = [
            r"'\s*;\s*drop\s+table",
            r"'\s*;\s*delete\s+from",
            r"'\s*;\s*insert\s+into",
            r"'\s*;\s*update\s+.*\s+set",
            r"union\s+select",
            r"'\s*or\s+'?1'?\s*='?1'?",
            r"'\s*or\s+'?true'?",
        ]
        
        # XSS patterns
        self.xss_patterns = [
            r'<\s*script[^>]*>',
            r'javascript:',
            r'onload\s*=',
            r'onerror\s*=',
            r'onclick\s*=',
            r'onmouseover\s*=',
        ]
        
        # Sensitive data patterns
        self.sensitive_patterns = [
            r'(?i)password\s*[:=]\s*["\']?([^"\'\\s]+)',
            r'(?i)api[_-]?key\s*[:=]\s*["\']?([^"\'\\s]+)',
            r'(?i)secret\s*[:=]\s*["\']?([^"\'\\s]+)',
            r'(?i)token\s*[:=]\s*["\']?([^"\'\\s]+)',
            r'[A-Za-z0-9+/]{20,}={0,2}',  # Base64
            r'[0-9a-fA-F]{32,}',          # Hex keys
        ]
    
    def validate_command_input(self, command: str, args: Dict[str, Any]) -> Tuple[bool, List[str], Dict[str, Any]]:
        """Validate command and arguments for security issues"""
        issues = []
        sanitized_args = {}
        
        # Check command for dangerous patterns
        for pattern in self.dangerous_command_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                issues.append(f"Dangerous command pattern detected: {pattern}")
        
        # Validate and sanitize arguments
        for key, value in args.items():
            sanitized_value, arg_issues = self._sanitize_argument(key, value)
            sanitized_args[key] = sanitized_value
            issues.extend(arg_issues)
        
        is_safe = len(issues) == 0
        return is_safe, issues, sanitized_args
    
    def _sanitize_argument(self, key: str, value: Any) -> Tuple[Any, List[str]]:
        """Sanitize individual argument"""
        issues = []
        
        if isinstance(value, str):
            # Check for command injection
            for pattern in self.dangerous_command_patterns:
                if re.search(pattern, value, re.IGNORECASE):
                    issues.append(f"Command injection pattern in {key}: {pattern}")
            
            # Check for SQL injection
            for pattern in self.sql_injection_patterns:
                if re.search(pattern, value, re.IGNORECASE):
                    issues.append(f"SQL injection pattern in {key}: {pattern}")
            
            # Check for XSS
            for pattern in self.xss_patterns:
                if re.search(pattern, value, re.IGNORECASE):
                    issues.append(f"XSS pattern in {key}: {pattern}")
            
            # Sanitize HTML
            sanitized_value = html.escape(value)
            
            # Limit length
            if len(sanitized_value) > 10000:
                sanitized_value = sanitized_value[:10000]
                issues.append(f"Argument {key} truncated due to excessive length")
            
            return sanitized_value, issues
        
        elif isinstance(value, dict):
            sanitized_dict = {}
            for k, v in value.items():
                sanitized_v, v_issues = self._sanitize_argument(f"{key}.{k}", v)
                sanitized_dict[k] = sanitized_v
                issues.extend(v_issues)
            return sanitized_dict, issues
        
        elif isinstance(value, list):
            sanitized_list = []
            for i, item in enumerate(value):
                sanitized_item, item_issues = self._sanitize_argument(f"{key}[{i}]", item)
                sanitized_list.append(sanitized_item)
                issues.extend(item_issues)
            return sanitized_list, issues
        
        else:
            return value, issues
    
    def sanitize_log_data(self, data: Any) -> Any:
        """Sanitize data before logging to remove sensitive information"""
        if isinstance(data, str):
            # Remove sensitive patterns
            sanitized = data
            for pattern in self.sensitive_patterns:
                sanitized = re.sub(pattern, r'[REDACTED]', sanitized, flags=re.IGNORECASE)
            return sanitized
        
        elif isinstance(data, dict):
            sanitized_dict = {}
            for key, value in data.items():
                # Check if key indicates sensitive data
                if any(sensitive in key.lower() for sensitive in ['password', 'secret', 'token', 'key', 'auth']):
                    sanitized_dict[key] = '[REDACTED]'
                else:
                    sanitized_dict[key] = self.sanitize_log_data(value)
            return sanitized_dict
        
        elif isinstance(data, list):
            return [self.sanitize_log_data(item) for item in data]
        
        else:
            return data
    
    def validate_file_content(self, content: str, file_type: str) -> Tuple[bool, List[str]]:
        """Validate file content for security issues"""
        issues = []
        
        # Check for malicious patterns based on file type
        if file_type in ['py', 'sh', 'bash']:
            # Check for dangerous system calls
            dangerous_calls = [
                r'os\.system\s*\(',
                r'subprocess\.call\s*\(',
                r'exec\s*\(',
                r'eval\s*\(',
                r'__import__\s*\(',
            ]
            
            for pattern in dangerous_calls:
                if re.search(pattern, content):
                    issues.append(f"Potentially dangerous function call: {pattern}")
        
        elif file_type in ['json', 'yaml', 'yml']:
            # Check for code injection in data files
            if re.search(r'__.*__', content):
                issues.append("Suspicious double underscore patterns detected")
        
        # Check for embedded scripts
        if re.search(r'<script[^>]*>', content, re.IGNORECASE):
            issues.append("Embedded script tags detected")
        
        # Check file size
        if len(content) > 10_000_000:  # 10MB limit
            issues.append("File size exceeds security limit")
        
        is_safe = len(issues) == 0
        return is_safe, issues

# Sanitization decorator
def sanitize_input(func):
    """Decorator to automatically sanitize function inputs"""
    def wrapper(*args, **kwargs):
        validator = EnhancedInputValidator()
        
        # Sanitize keyword arguments
        sanitized_kwargs = {}
        for key, value in kwargs.items():
            sanitized_value, _ = validator._sanitize_argument(key, value)
            sanitized_kwargs[key] = sanitized_value
        
        return func(*args, **sanitized_kwargs)
    
    return wrapper