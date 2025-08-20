#!/usr/bin/env python3
"""
Security Validation Hook for Claude Code
Integrates all security validation components for comprehensive protection
"""

import sys
import json
import time
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

# Add security modules to path
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir / "security"))

from path_validator import PathValidator
from content_scanner import ContentScanner
from command_validator import CommandValidator
from audit_logger import AuditLogger, AuditEvent, AuditEventType, AuditSeverity
from backup_manager import BackupManager, BackupType

class SecurityValidationHook:
    """Comprehensive security validation hook for Claude Code"""
    
    def __init__(self):
        # Initialize security components
        self.path_validator = PathValidator()
        self.content_scanner = ContentScanner()
        self.command_validator = CommandValidator()
        self.audit_logger = AuditLogger()
        self.backup_manager = BackupManager()
        
        # Configuration
        self.strict_mode = os.getenv('SECURITY_STRICT_MODE', 'true').lower() == 'true'
        self.auto_backup = os.getenv('SECURITY_AUTO_BACKUP', 'true').lower() == 'true'
        self.block_on_critical = os.getenv('SECURITY_BLOCK_CRITICAL', 'true').lower() == 'true'
        
        # Session tracking
        self.session_id = self._generate_session_id()
        self.user_id = os.getenv('USER', 'unknown')
        
    def pre_tool_use_hook(self, tool_name: str, arguments: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        """Pre-tool validation hook"""
        
        start_time = time.time()
        validation_results = {
            'tool_name': tool_name,
            'timestamp': start_time,
            'session_id': self.session_id,
            'user_id': self.user_id,
            'security_checks': {}
        }
        
        try:
            # 1. Path validation for file operations
            if self._is_file_operation(tool_name):
                path_result = self._validate_paths(tool_name, arguments)
                validation_results['security_checks']['path_validation'] = path_result
                
                if not path_result['allowed']:
                    self._log_security_violation(
                        'path_traversal', 
                        path_result.get('path', 'unknown'),
                        AuditSeverity.HIGH,
                        path_result
                    )
                    if self.block_on_critical:
                        return False, f"Security violation: {path_result['reason']}", validation_results
            
            # 2. Command validation for bash operations
            if tool_name == 'Bash':
                command_result = self._validate_command(arguments)
                validation_results['security_checks']['command_validation'] = command_result
                
                if not command_result['allowed']:
                    self._log_security_violation(
                        'dangerous_command',
                        command_result.get('command', 'unknown'),
                        AuditSeverity.HIGH,
                        command_result
                    )
                    if self.block_on_critical:
                        return False, f"Command blocked: {command_result['reason']}", validation_results
            
            # 3. Content validation for write operations
            if self._is_write_operation(tool_name):
                content_result = self._validate_content(arguments)
                validation_results['security_checks']['content_validation'] = content_result
                
                if content_result.get('critical_findings', 0) > 0:
                    self._log_security_violation(
                        'malicious_content',
                        arguments.get('file_path', 'unknown'),
                        AuditSeverity.CRITICAL,
                        content_result
                    )
                    if self.block_on_critical:
                        return False, f"Content validation failed: {content_result['reason']}", validation_results
            
            # 4. Create backup for file modifications
            if self.auto_backup and self._is_modification_operation(tool_name):
                backup_result = self._create_pre_modification_backup(arguments)
                validation_results['security_checks']['backup'] = backup_result
            
            # Log successful validation
            self._log_tool_access(tool_name, arguments, 'allowed', validation_results)
            
            return True, "Security validation passed", validation_results
            
        except Exception as e:
            error_msg = f"Security validation error: {str(e)}"
            validation_results['error'] = error_msg
            
            self._log_security_violation(
                'validation_error',
                tool_name,
                AuditSeverity.MEDIUM,
                {'error': str(e)}
            )
            
            # In strict mode, block on validation errors
            if self.strict_mode:
                return False, error_msg, validation_results
            else:
                return True, f"Warning: {error_msg}", validation_results
    
    def post_tool_use_hook(self, tool_name: str, arguments: Dict[str, Any], 
                          result: Any, execution_time: float) -> Dict[str, Any]:
        """Post-tool analysis hook"""
        
        analysis_results = {
            'tool_name': tool_name,
            'execution_time': execution_time,
            'timestamp': time.time(),
            'session_id': self.session_id,
            'analysis': {}
        }
        
        try:
            # 1. Analyze file modifications
            if self._is_modification_operation(tool_name):
                file_analysis = self._analyze_file_modification(arguments, result)
                analysis_results['analysis']['file_modification'] = file_analysis
            
            # 2. Analyze command execution results
            if tool_name == 'Bash':
                command_analysis = self._analyze_command_execution(arguments, result)
                analysis_results['analysis']['command_execution'] = command_analysis
                
                # Check for suspicious command output
                if self._has_suspicious_output(result):
                    self._log_security_violation(
                        'suspicious_output',
                        arguments.get('command', 'unknown'),
                        AuditSeverity.MEDIUM,
                        {'output_snippet': str(result)[:200]}
                    )
            
            # 3. Update security metrics
            self._update_security_metrics(tool_name, arguments, result, execution_time)
            
            # Log successful completion
            self._log_tool_completion(tool_name, arguments, result, analysis_results)
            
        except Exception as e:
            analysis_results['error'] = str(e)
            self._log_security_violation(
                'analysis_error',
                tool_name,
                AuditSeverity.LOW,
                {'error': str(e)}
            )
        
        return analysis_results
    
    def _validate_paths(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Validate file paths in tool arguments"""
        
        path_fields = ['file_path', 'path', 'notebook_path', 'pattern']
        validation_result = {'allowed': True, 'checks': [], 'paths_validated': []}
        
        for field in path_fields:
            if field in arguments:
                path_value = arguments[field]
                if isinstance(path_value, str):
                    result = self.path_validator.validate_path(path_value)
                    validation_result['checks'].append({
                        'field': field,
                        'path': path_value,
                        'result': result
                    })
                    validation_result['paths_validated'].append(path_value)
                    
                    if not result.allowed:
                        validation_result['allowed'] = False
                        validation_result['reason'] = result.reason
                        validation_result['path'] = path_value
                        break
        
        return validation_result
    
    def _validate_command(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Validate bash command"""
        
        command = arguments.get('command', '')
        if not command:
            return {'allowed': True, 'reason': 'No command to validate'}
        
        result = self.command_validator.validate_command(command)
        
        return {
            'allowed': result.allowed,
            'command': command,
            'risk_score': result.risk_score,
            'threats': [{'type': t.threat_type.value, 'severity': t.severity.value, 'description': t.description} for t in result.threats],
            'reason': f"Risk score: {result.risk_score:.2f}, Threats: {len(result.threats)}" if not result.allowed else "Command allowed",
            'sanitized_command': result.sanitized_command,
            'alternatives': result.alternative_suggestions
        }
    
    def _validate_content(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Validate file content for write operations"""
        
        content = arguments.get('content', '')
        file_path = arguments.get('file_path', 'unknown')
        
        if not content:
            return {'allowed': True, 'reason': 'No content to validate'}
        
        scan_result = self.content_scanner.scan_content(content, file_path)
        
        critical_findings = sum(1 for f in scan_result.findings if f.severity.value == 'critical')
        high_findings = sum(1 for f in scan_result.findings if f.severity.value == 'high')
        
        return {
            'allowed': critical_findings == 0,
            'file_path': file_path,
            'total_findings': len(scan_result.findings),
            'critical_findings': critical_findings,
            'high_findings': high_findings,
            'overall_risk_score': scan_result.overall_risk_score,
            'reason': f"Critical findings: {critical_findings}, High findings: {high_findings}" if critical_findings > 0 else "Content validation passed",
            'recommendations': scan_result.recommendations
        }
    
    def _create_pre_modification_backup(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Create backup before file modification"""
        
        file_path = arguments.get('file_path')
        if not file_path or not os.path.exists(file_path):
            return {'backup_created': False, 'reason': 'File does not exist'}
        
        backup_id = self.backup_manager.create_pre_modification_backup(file_path)
        
        return {
            'backup_created': backup_id is not None,
            'backup_id': backup_id,
            'file_path': file_path,
            'reason': 'Backup created successfully' if backup_id else 'Backup creation failed'
        }
    
    def _analyze_file_modification(self, arguments: Dict[str, Any], result: Any) -> Dict[str, Any]:
        """Analyze file modification results"""
        
        file_path = arguments.get('file_path')
        if not file_path:
            return {'analyzed': False, 'reason': 'No file path specified'}
        
        try:
            # Get file stats after modification
            if os.path.exists(file_path):
                stat = os.stat(file_path)
                return {
                    'analyzed': True,
                    'file_path': file_path,
                    'file_size': stat.st_size,
                    'modified_time': stat.st_mtime,
                    'permissions': oct(stat.st_mode)[-3:],
                    'success': True
                }
            else:
                return {
                    'analyzed': True,
                    'file_path': file_path,
                    'success': False,
                    'reason': 'File does not exist after operation'
                }
        except Exception as e:
            return {
                'analyzed': False,
                'error': str(e)
            }
    
    def _analyze_command_execution(self, arguments: Dict[str, Any], result: Any) -> Dict[str, Any]:
        """Analyze command execution results"""
        
        command = arguments.get('command', '')
        
        return {
            'command': command,
            'output_length': len(str(result)) if result else 0,
            'has_errors': 'error' in str(result).lower() if result else False,
            'exit_success': True,  # Assume success if no exception
            'suspicious_patterns': self._detect_suspicious_patterns(str(result) if result else '')
        }
    
    def _detect_suspicious_patterns(self, output: str) -> List[str]:
        """Detect suspicious patterns in command output"""
        
        suspicious_patterns = [
            r'password.*:',
            r'access.*denied',
            r'permission.*denied',
            r'unauthorized',
            r'failed.*login',
            r'connection.*refused'
        ]
        
        import re
        detected = []
        for pattern in suspicious_patterns:
            if re.search(pattern, output, re.IGNORECASE):
                detected.append(pattern)
        
        return detected
    
    def _has_suspicious_output(self, result: Any) -> bool:
        """Check if command output contains suspicious content"""
        
        if not result:
            return False
        
        output = str(result).lower()
        suspicious_keywords = [
            'permission denied', 'access denied', 'unauthorized',
            'failed login', 'connection refused', 'timeout'
        ]
        
        return any(keyword in output for keyword in suspicious_keywords)
    
    def _update_security_metrics(self, tool_name: str, arguments: Dict[str, Any], 
                                result: Any, execution_time: float):
        """Update security metrics"""
        
        # This could be expanded to integrate with monitoring systems
        # For now, we'll just track basic metrics in the audit log
        
        metrics = {
            'tool_usage': tool_name,
            'execution_time': execution_time,
            'arguments_count': len(arguments),
            'result_size': len(str(result)) if result else 0,
            'timestamp': time.time()
        }
        
        # Log metrics for analysis
        self.audit_logger.log_system_change(
            'metrics_update',
            f"tool_usage_{tool_name}",
            self.user_id,
            self.session_id,
            'success',
            metrics
        )
    
    def _log_security_violation(self, violation_type: str, resource: str, 
                              severity: AuditSeverity, details: Dict[str, Any]):
        """Log security violation"""
        
        self.audit_logger.log_security_violation(
            violation_type,
            resource,
            self.user_id,
            self.session_id,
            severity,
            details
        )
    
    def _log_tool_access(self, tool_name: str, arguments: Dict[str, Any], 
                        result: str, details: Dict[str, Any]):
        """Log tool access attempt"""
        
        self.audit_logger.log_system_change(
            'tool_access',
            tool_name,
            self.user_id,
            self.session_id,
            result,
            {
                'arguments': list(arguments.keys()),
                'validation_details': details
            }
        )
    
    def _log_tool_completion(self, tool_name: str, arguments: Dict[str, Any], 
                           result: Any, analysis: Dict[str, Any]):
        """Log tool completion"""
        
        self.audit_logger.log_system_change(
            'tool_completion',
            tool_name,
            self.user_id,
            self.session_id,
            'success',
            {
                'arguments': list(arguments.keys()),
                'analysis': analysis
            }
        )
    
    def _is_file_operation(self, tool_name: str) -> bool:
        """Check if tool performs file operations"""
        return tool_name in ['Read', 'Write', 'Edit', 'MultiEdit', 'NotebookRead', 'NotebookEdit', 'Glob']
    
    def _is_write_operation(self, tool_name: str) -> bool:
        """Check if tool performs write operations"""
        return tool_name in ['Write', 'Edit', 'MultiEdit', 'NotebookEdit']
    
    def _is_modification_operation(self, tool_name: str) -> bool:
        """Check if tool modifies files"""
        return tool_name in ['Write', 'Edit', 'MultiEdit', 'NotebookEdit']
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        import uuid
        return str(uuid.uuid4())

# Hook integration functions for Claude Code
def pre_tool_use(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Pre-tool use hook entry point"""
    
    try:
        hook = SecurityValidationHook()
        allowed, message, details = hook.pre_tool_use_hook(tool_name, arguments)
        
        return {
            'allowed': allowed,
            'message': message,
            'details': details,
            'hook_name': 'security_validation',
            'timestamp': time.time()
        }
    except Exception as e:
        return {
            'allowed': True,  # Default to allow on hook failure
            'message': f"Security hook error: {str(e)}",
            'details': {'error': str(e)},
            'hook_name': 'security_validation',
            'timestamp': time.time()
        }

def post_tool_use(tool_name: str, arguments: Dict[str, Any], 
                 result: Any, execution_time: float) -> Dict[str, Any]:
    """Post-tool use hook entry point"""
    
    try:
        hook = SecurityValidationHook()
        analysis = hook.post_tool_use_hook(tool_name, arguments, result, execution_time)
        
        return {
            'analysis': analysis,
            'hook_name': 'security_validation',
            'timestamp': time.time()
        }
    except Exception as e:
        return {
            'analysis': {'error': str(e)},
            'hook_name': 'security_validation',
            'timestamp': time.time()
        }

# Example usage and testing
def test_security_validation_hook():
    """Test the security validation hook"""
    
    print("🧪 Testing Security Validation Hook...")
    
    hook = SecurityValidationHook()
    
    # Test file operation validation
    print("\n1. Testing file operation validation:")
    file_args = {'file_path': '/tmp/test.txt', 'content': 'Hello world'}
    allowed, message, details = hook.pre_tool_use_hook('Write', file_args)
    print(f"   Write operation: {'✅ ALLOWED' if allowed else '🚫 BLOCKED'}")
    print(f"   Message: {message}")
    
    # Test dangerous path validation
    print("\n2. Testing dangerous path validation:")
    dangerous_args = {'file_path': '../../../etc/passwd'}
    allowed, message, details = hook.pre_tool_use_hook('Read', dangerous_args)
    print(f"   Dangerous path: {'✅ ALLOWED' if allowed else '🚫 BLOCKED'}")
    print(f"   Message: {message}")
    
    # Test command validation
    print("\n3. Testing command validation:")
    safe_cmd_args = {'command': 'ls -la'}
    allowed, message, details = hook.pre_tool_use_hook('Bash', safe_cmd_args)
    print(f"   Safe command: {'✅ ALLOWED' if allowed else '🚫 BLOCKED'}")
    
    dangerous_cmd_args = {'command': 'rm -rf /'}
    allowed, message, details = hook.pre_tool_use_hook('Bash', dangerous_cmd_args)
    print(f"   Dangerous command: {'✅ ALLOWED' if allowed else '🚫 BLOCKED'}")
    print(f"   Message: {message}")
    
    # Test content validation
    print("\n4. Testing content validation:")
    secret_content = '''
    API_KEY = "sk-1234567890abcdef"
    password = "super_secret"
    '''
    secret_args = {'file_path': 'config.py', 'content': secret_content}
    allowed, message, details = hook.pre_tool_use_hook('Write', secret_args)
    print(f"   Content with secrets: {'✅ ALLOWED' if allowed else '🚫 BLOCKED'}")
    print(f"   Message: {message}")
    
    print("\n🎉 Security validation hook test completed!")

if __name__ == "__main__":
    test_security_validation_hook()