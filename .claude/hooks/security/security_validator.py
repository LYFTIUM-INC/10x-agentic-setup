#!/usr/bin/env python3
"""
Claude Code Hooks - Security Validation Hook
Validates all hook executions and tool calls for security compliance
"""

import os
import json
import re
import sys
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('security_validator')

class SecurityValidator:
    """Comprehensive security validation for Claude Code hooks"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.security_config = self._load_security_config()
        self.validation_db = self.project_root / '.claude' / 'security_validation.db'
        self.session_id = os.environ.get('CLAUDE_SESSION_ID', 'unknown')
        
    def _load_security_config(self) -> Dict[str, Any]:
        """Load security configuration"""
        config_path = self.project_root / '.claude' / 'security_config.json'
        
        default_config = {
            "allowed_commands": [
                "python", "python3", "uv", "pip", "npm", "node", "git",
                "ls", "cat", "grep", "find", "mkdir", "touch", "cp", "mv"
            ],
            "blocked_patterns": [
                r"rm\s+-rf\s*/",  # Dangerous file deletion
                r"sudo\s+",       # Elevated privileges
                r"curl.*\|\s*sh", # Pipe to shell
                r"wget.*\|\s*sh", # Pipe to shell
                r"eval\s*\(",     # Dynamic code execution
                r"exec\s*\(",     # Process execution
                r"__import__",    # Dynamic imports
                r"globals\(\)",   # Global scope access
                r"locals\(\)"     # Local scope access
            ],
            "sensitive_file_patterns": [
                r"\.env",
                r"\.secret",
                r"\.key",
                r"id_rsa",
                r"\.pem",
                r"password",
                r"token",
                r"config\.json",
                r"secrets\."
            ],
            "max_file_size": 50 * 1024 * 1024,  # 50MB
            "max_execution_time": 300,  # 5 minutes
            "trusted_domains": [
                "github.com",
                "api.github.com",
                "pypi.org",
                "npmjs.com",
                "anthropic.com",
                "docs.anthropic.com"
            ]
        }
        
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    custom_config = json.load(f)
                    default_config.update(custom_config)
            except Exception as e:
                logger.warning(f"Failed to load security config: {e}")
        
        return default_config
    
    def validate_tool_call(self) -> Dict[str, Any]:
        """Validate current tool call for security compliance"""
        
        validation_result = {
            'session_id': self.session_id,
            'timestamp': datetime.now().isoformat(),
            'hook_event': os.environ.get('CLAUDE_HOOK_EVENT_NAME', ''),
            'tool_name': os.environ.get('CLAUDE_TOOL_NAME', ''),
            'validation_status': 'pending',
            'security_issues': [],
            'warnings': [],
            'recommendations': [],
            'risk_level': 'low'
        }
        
        try:
            # Validate hook event
            if not self._validate_hook_event(validation_result):
                validation_result['validation_status'] = 'failed'
                validation_result['risk_level'] = 'high'
                return validation_result
            
            # Validate tool name
            if not self._validate_tool_name(validation_result):
                validation_result['validation_status'] = 'failed'
                validation_result['risk_level'] = 'medium'
                return validation_result
            
            # Validate tool arguments
            if not self._validate_tool_arguments(validation_result):
                validation_result['validation_status'] = 'failed'
                validation_result['risk_level'] = 'high'
                return validation_result
            
            # Validate file access
            if not self._validate_file_access(validation_result):
                validation_result['validation_status'] = 'warning'
                validation_result['risk_level'] = 'medium'
            
            # Validate network access
            if not self._validate_network_access(validation_result):
                validation_result['validation_status'] = 'warning'
                validation_result['risk_level'] = 'medium'
            
            # Final validation status
            if validation_result['validation_status'] == 'pending':
                validation_result['validation_status'] = 'passed'
            
            # Log validation result
            self._log_validation_result(validation_result)
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Security validation failed: {e}")
            validation_result['validation_status'] = 'error'
            validation_result['security_issues'].append(f"Validation error: {str(e)}")
            validation_result['risk_level'] = 'high'
            return validation_result
    
    def _validate_hook_event(self, result: Dict[str, Any]) -> bool:
        """Validate hook event type"""
        
        allowed_events = [
            'PreToolUse', 'PostToolUse', 'UserPromptSubmit', 
            'Notification', 'Stop', 'SubagentStop', 'PreCompact'
        ]
        
        hook_event = result['hook_event']
        
        if not hook_event:
            result['security_issues'].append("Missing hook event name")
            return False
        
        if hook_event not in allowed_events:
            result['security_issues'].append(f"Unknown hook event: {hook_event}")
            return False
        
        return True
    
    def _validate_tool_name(self, result: Dict[str, Any]) -> bool:
        """Validate tool name for suspicious patterns"""
        
        tool_name = result['tool_name']
        
        if not tool_name:
            result['warnings'].append("Missing tool name")
            return True  # Not a security issue, just a warning
        
        # Check for suspicious tool patterns
        suspicious_patterns = [
            r'eval_.*',
            r'exec_.*',
            r'shell_.*',
            r'system_.*',
            r'.*_inject.*',
            r'.*_exploit.*'
        ]
        
        for pattern in suspicious_patterns:
            if re.match(pattern, tool_name, re.IGNORECASE):
                result['security_issues'].append(f"Suspicious tool name pattern: {tool_name}")
                return False
        
        return True
    
    def _validate_tool_arguments(self, result: Dict[str, Any]) -> bool:
        """Validate tool arguments for security issues"""
        
        tool_args = os.environ.get('CLAUDE_TOOL_ARGUMENTS', '{}')
        
        try:
            args = json.loads(tool_args) if tool_args else {}
        except json.JSONDecodeError:
            result['warnings'].append("Failed to parse tool arguments")
            return True
        
        # Check for blocked command patterns
        for key, value in args.items():
            if isinstance(value, str):
                for pattern in self.security_config['blocked_patterns']:
                    if re.search(pattern, value, re.IGNORECASE):
                        result['security_issues'].append(
                            f"Blocked command pattern in {key}: {pattern}"
                        )
                        return False
        
        # Check for command injection attempts
        if self._check_command_injection(args, result):
            return False
        
        return True
    
    def _check_command_injection(self, args: Dict[str, Any], result: Dict[str, Any]) -> bool:
        """Check for command injection attempts"""
        
        injection_indicators = [
            ';', '&&', '||', '|', '`', '$(',
            '../', '..\\', '/etc/', '/bin/',
            'passwd', 'shadow', '/dev/', '/proc/'
        ]
        
        for key, value in args.items():
            if isinstance(value, str):
                for indicator in injection_indicators:
                    if indicator in value:
                        result['security_issues'].append(
                            f"Potential command injection in {key}: {indicator}"
                        )
                        return True
        
        return False
    
    def _validate_file_access(self, result: Dict[str, Any]) -> bool:
        """Validate file access patterns"""
        
        file_paths = os.environ.get('CLAUDE_FILE_PATHS', '')
        
        if not file_paths:
            return True
        
        paths = file_paths.split(',')
        
        for path in paths:
            path = path.strip()
            
            # Check for sensitive file patterns
            for pattern in self.security_config['sensitive_file_patterns']:
                if re.search(pattern, path, re.IGNORECASE):
                    result['warnings'].append(f"Accessing sensitive file pattern: {path}")
                    break
            
            # Check for path traversal attempts
            if '../' in path or '..' in path:
                result['security_issues'].append(f"Path traversal attempt: {path}")
                return False
            
            # Check for system directory access
            system_dirs = ['/etc/', '/bin/', '/sbin/', '/usr/bin/', '/root/']
            for sys_dir in system_dirs:
                if path.startswith(sys_dir):
                    result['security_issues'].append(f"System directory access: {path}")
                    return False
        
        return True
    
    def _validate_network_access(self, result: Dict[str, Any]) -> bool:
        """Validate network access requests"""
        
        # Check for URLs in tool arguments
        tool_args = os.environ.get('CLAUDE_TOOL_ARGUMENTS', '{}')
        
        try:
            args = json.loads(tool_args) if tool_args else {}
        except json.JSONDecodeError:
            return True
        
        url_pattern = r'https?://([a-zA-Z0-9.-]+)'
        
        for key, value in args.items():
            if isinstance(value, str):
                urls = re.findall(url_pattern, value, re.IGNORECASE)
                
                for url in urls:
                    domain = url.lower()
                    
                    # Check if domain is in trusted list
                    if not any(trusted in domain for trusted in self.security_config['trusted_domains']):
                        result['warnings'].append(f"Untrusted domain access: {domain}")
                    
                    # Check for suspicious domains
                    suspicious_patterns = [
                        r'.*\.exe$',
                        r'.*\.bin$',
                        r'.*\.sh$',
                        r'bit\.ly',
                        r'tinyurl\.',
                        r'[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+',  # IP addresses
                    ]
                    
                    for pattern in suspicious_patterns:
                        if re.search(pattern, domain, re.IGNORECASE):
                            result['security_issues'].append(f"Suspicious domain pattern: {domain}")
                            return False
        
        return True
    
    def _log_validation_result(self, result: Dict[str, Any]):
        """Log validation result to database"""
        
        import sqlite3
        
        # Ensure database directory exists
        self.validation_db.parent.mkdir(exist_ok=True)
        
        try:
            with sqlite3.connect(self.validation_db) as conn:
                # Create table if not exists
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS security_validations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT,
                        timestamp TEXT,
                        hook_event TEXT,
                        tool_name TEXT,
                        validation_status TEXT,
                        risk_level TEXT,
                        security_issues TEXT,
                        warnings TEXT,
                        recommendations TEXT
                    )
                """)
                
                # Insert validation result
                conn.execute("""
                    INSERT INTO security_validations 
                    (session_id, timestamp, hook_event, tool_name, validation_status, 
                     risk_level, security_issues, warnings, recommendations)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    result['session_id'],
                    result['timestamp'],
                    result['hook_event'],
                    result['tool_name'],
                    result['validation_status'],
                    result['risk_level'],
                    json.dumps(result['security_issues']),
                    json.dumps(result['warnings']),
                    json.dumps(result['recommendations'])
                ))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to log validation result: {e}")
    
    def generate_security_report(self) -> Dict[str, Any]:
        """Generate security report for current session"""
        
        import sqlite3
        
        report = {
            'session_id': self.session_id,
            'report_timestamp': datetime.now().isoformat(),
            'total_validations': 0,
            'passed_validations': 0,
            'failed_validations': 0,
            'warnings_count': 0,
            'high_risk_events': 0,
            'security_summary': {},
            'recommendations': []
        }
        
        try:
            with sqlite3.connect(self.validation_db) as conn:
                # Get validation statistics
                cursor = conn.execute("""
                    SELECT validation_status, risk_level, COUNT(*) 
                    FROM security_validations 
                    WHERE session_id = ?
                    GROUP BY validation_status, risk_level
                """, (self.session_id,))
                
                for status, risk, count in cursor.fetchall():
                    report['total_validations'] += count
                    
                    if status == 'passed':
                        report['passed_validations'] += count
                    elif status == 'failed':
                        report['failed_validations'] += count
                    elif status == 'warning':
                        report['warnings_count'] += count
                    
                    if risk == 'high':
                        report['high_risk_events'] += count
                
                # Get security issues summary
                cursor = conn.execute("""
                    SELECT security_issues, warnings 
                    FROM security_validations 
                    WHERE session_id = ? AND (security_issues != '[]' OR warnings != '[]')
                """, (self.session_id,))
                
                all_issues = []
                all_warnings = []
                
                for issues_json, warnings_json in cursor.fetchall():
                    if issues_json and issues_json != '[]':
                        issues = json.loads(issues_json)
                        all_issues.extend(issues)
                    
                    if warnings_json and warnings_json != '[]':
                        warnings = json.loads(warnings_json)
                        all_warnings.extend(warnings)
                
                report['security_summary'] = {
                    'total_issues': len(all_issues),
                    'total_warnings': len(all_warnings),
                    'unique_issues': list(set(all_issues)),
                    'unique_warnings': list(set(all_warnings))
                }
                
                # Generate recommendations
                if report['failed_validations'] > 0:
                    report['recommendations'].append(
                        "Review failed validations and implement security fixes"
                    )
                
                if report['high_risk_events'] > 0:
                    report['recommendations'].append(
                        "Investigate high-risk events and strengthen security controls"
                    )
                
                if report['warnings_count'] > 5:
                    report['recommendations'].append(
                        "Consider reviewing warning patterns for potential security improvements"
                    )
                
        except Exception as e:
            logger.error(f"Failed to generate security report: {e}")
            report['error'] = str(e)
        
        return report

def main():
    """Main security validation entry point"""
    
    validator = SecurityValidator()
    
    # Perform validation
    result = validator.validate_tool_call()
    
    # Print validation result
    print(f"Security Validation: {result['validation_status']}")
    print(f"Risk Level: {result['risk_level']}")
    
    if result['security_issues']:
        print(f"Security Issues: {len(result['security_issues'])}")
        for issue in result['security_issues']:
            print(f"  - {issue}")
    
    if result['warnings']:
        print(f"Warnings: {len(result['warnings'])}")
        for warning in result['warnings']:
            print(f"  - {warning}")
    
    # Exit with appropriate code
    if result['validation_status'] == 'failed':
        sys.exit(1)
    elif result['validation_status'] == 'error':
        sys.exit(2)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()