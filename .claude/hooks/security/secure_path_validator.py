#!/usr/bin/env python3
"""
Enhanced Secure Path Validator
Prevents path traversal attacks and enforces secure file access
"""

import os
import re
from pathlib import Path
from typing import List, Optional, Tuple, Set
import logging

class SecurePathValidator:
    """Enhanced path validator with comprehensive security checks"""
    
    def __init__(self):
        # Define allowed base directories
        self.allowed_base_dirs = {
            '/home/dell/coding/bash/10x-agentic-setup',
            '/tmp/claude-secure',
            '/var/log/claude'
        }
        
        # Dangerous path patterns
        self.dangerous_patterns = [
            r'\.\.',           # Parent directory traversal
            r'~/',            # Home directory shortcuts
            r'\$\{.*\}',      # Environment variable expansion
            r'`.*`',          # Command substitution
            r'\$\(.*\)',      # Command substitution
            r';',             # Command chaining
            r'&',             # Background execution
            r'\|',            # Pipes
            r'>',             # Redirects
            r'<',             # Redirects
        ]
        
        # Forbidden directories
        self.forbidden_dirs = {
            '/etc',
            '/bin', 
            '/sbin',
            '/usr/bin',
            '/usr/sbin',
            '/root',
            '/proc',
            '/sys',
            '/dev'
        }
        
        # Allowed file extensions
        self.allowed_extensions = {
            '.py', '.md', '.txt', '.json', '.yaml', '.yml',
            '.log', '.csv', '.xml', '.html', '.js', '.ts',
            '.sh', '.sql', '.toml', '.ini', '.cfg'
        }
        
    def validate_path(self, path: str) -> Tuple[bool, str, Optional[Path]]:
        """
        Comprehensive path validation
        
        Returns:
            (is_valid, error_message, resolved_path)
        """
        if not path:
            return False, "Empty path provided", None
            
        # Check for dangerous patterns
        for pattern in self.dangerous_patterns:
            if re.search(pattern, path):
                return False, f"Dangerous pattern detected: {pattern}", None
        
        try:
            # Resolve path securely
            resolved_path = Path(path).resolve()
            
            # Check if path is within allowed directories
            is_allowed = False
            for allowed_dir in self.allowed_base_dirs:
                if resolved_path.is_relative_to(allowed_dir):
                    is_allowed = True
                    break
            
            if not is_allowed:
                return False, f"Path outside allowed directories: {resolved_path}", None
                
            # Check forbidden directories
            for forbidden_dir in self.forbidden_dirs:
                if resolved_path.is_relative_to(forbidden_dir):
                    return False, f"Access to forbidden directory: {forbidden_dir}", None
            
            # Check file extension if it's a file
            if resolved_path.is_file() or not resolved_path.exists():
                ext = resolved_path.suffix.lower()
                if ext and ext not in self.allowed_extensions:
                    return False, f"Forbidden file extension: {ext}", None
            
            return True, "Path validation successful", resolved_path
            
        except (OSError, ValueError) as e:
            return False, f"Path resolution error: {str(e)}", None
    
    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename to prevent injection attacks"""
        # Remove dangerous characters
        safe_filename = re.sub(r'[^\w\-_\.]', '_', filename)
        
        # Limit length
        if len(safe_filename) > 255:
            safe_filename = safe_filename[:255]
            
        return safe_filename
    
    def validate_command_path(self, command: str) -> Tuple[bool, str]:
        """Validate command paths for execution"""
        allowed_commands = {
            '/usr/bin/python3',
            '/usr/bin/python',
            '/bin/bash',
            '/usr/bin/git',
            '/usr/bin/npm',
            '/usr/bin/node'
        }
        
        if command in allowed_commands:
            return True, "Command allowed"
        
        return False, f"Command not in allowlist: {command}"