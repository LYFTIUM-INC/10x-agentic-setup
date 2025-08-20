#!/usr/bin/env python3
"""
Content Scanner for Security Validation System
Scans file content for secrets, PII, malicious patterns, and security vulnerabilities
"""

import re
import logging
import hashlib
import base64
from typing import List, Dict, Any, Optional, Set, Pattern
from dataclasses import dataclass
from enum import Enum
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FindingSeverity(Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class FindingType(Enum):
    SECRET = "secret"
    PII = "pii"
    MALICIOUS_PATTERN = "malicious_pattern"
    ENCODING_ISSUE = "encoding_issue"
    SUSPICIOUS_CONTENT = "suspicious_content"

@dataclass
class SecurityFinding:
    finding_type: FindingType
    severity: FindingSeverity
    pattern_name: str
    matched_text: str
    line_number: int
    column_start: int
    column_end: int
    description: str
    suggestion: str = ""
    confidence: float = 1.0
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class ScanResult:
    file_path: str
    findings: List[SecurityFinding]
    scan_duration: float
    total_lines: int
    total_bytes: int
    encoding: str
    is_binary: bool = False
    overall_risk_score: float = 0.0
    recommendations: List[str] = None

    def __post_init__(self):
        if self.recommendations is None:
            self.recommendations = []
        
        # Calculate overall risk score
        if self.findings:
            severity_weights = {
                FindingSeverity.INFO: 0.1,
                FindingSeverity.LOW: 0.3,
                FindingSeverity.MEDIUM: 0.6,
                FindingSeverity.HIGH: 0.8,
                FindingSeverity.CRITICAL: 1.0
            }
            
            total_weight = sum(severity_weights[f.severity] * f.confidence for f in self.findings)
            self.overall_risk_score = min(1.0, total_weight / len(self.findings))

class SecretPatterns:
    """Predefined patterns for secret detection"""
    
    def __init__(self):
        self.patterns = {
            # API Keys and Tokens
            'api_key_generic': {
                'pattern': r'(?i)(api[_-]?key|apikey)\s*[:=]\s*["\']?([A-Za-z0-9_\-]{16,})["\']?',
                'severity': FindingSeverity.CRITICAL,
                'description': 'Generic API key detected'
            },
            'bearer_token': {
                'pattern': r'(?i)bearer\s+([A-Za-z0-9_\-\.]{20,})',
                'severity': FindingSeverity.HIGH,
                'description': 'Bearer token detected'
            },
            'jwt_token': {
                'pattern': r'eyJ[A-Za-z0-9_\-]*\.eyJ[A-Za-z0-9_\-]*\.[A-Za-z0-9_\-]*',
                'severity': FindingSeverity.HIGH,
                'description': 'JWT token detected'
            },
            
            # Passwords
            'password_field': {
                'pattern': r'(?i)(password|passwd|pwd)\s*[:=]\s*["\']?([^\s"\']{6,})["\']?',
                'severity': FindingSeverity.CRITICAL,
                'description': 'Password field detected'
            },
            'basic_auth': {
                'pattern': r'(?i)authorization:\s*basic\s+([A-Za-z0-9+/=]{16,})',
                'severity': FindingSeverity.HIGH,
                'description': 'Basic authentication credentials detected'
            },
            
            # Private Keys and Certificates
            'private_key_rsa': {
                'pattern': r'-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----',
                'severity': FindingSeverity.CRITICAL,
                'description': 'RSA private key detected'
            },
            'private_key_ec': {
                'pattern': r'-----BEGIN\s+EC\s+PRIVATE\s+KEY-----',
                'severity': FindingSeverity.CRITICAL,
                'description': 'EC private key detected'
            },
            'openssh_private_key': {
                'pattern': r'-----BEGIN\s+OPENSSH\s+PRIVATE\s+KEY-----',
                'severity': FindingSeverity.CRITICAL,
                'description': 'OpenSSH private key detected'
            },
            
            # Cloud Provider Keys
            'aws_access_key': {
                'pattern': r'AKIA[0-9A-Z]{16}',
                'severity': FindingSeverity.CRITICAL,
                'description': 'AWS access key ID detected'
            },
            'aws_secret_key': {
                'pattern': r'(?i)aws[_-]?secret[_-]?access[_-]?key["\']?\s*[:=]\s*["\']?([A-Za-z0-9+/]{40})["\']?',
                'severity': FindingSeverity.CRITICAL,
                'description': 'AWS secret access key detected'
            },
            'github_token': {
                'pattern': r'ghp_[A-Za-z0-9]{36}',
                'severity': FindingSeverity.HIGH,
                'description': 'GitHub personal access token detected'
            },
            'slack_token': {
                'pattern': r'xox[baprs]-[A-Za-z0-9\-]{10,48}',
                'severity': FindingSeverity.HIGH,
                'description': 'Slack token detected'
            },
            
            # Database Connection Strings
            'mongodb_uri': {
                'pattern': r'mongodb(\+srv)?://[^\s"\'<>]{10,}',
                'severity': FindingSeverity.HIGH,
                'description': 'MongoDB connection string detected'
            },
            'mysql_connection': {
                'pattern': r'(?i)mysql://[^:\s"\'<>]+:[^@\s"\'<>]+@[^\s"\'<>/]+',
                'severity': FindingSeverity.HIGH,
                'description': 'MySQL connection string with credentials detected'
            },
            'postgres_connection': {
                'pattern': r'(?i)postgres(ql)?://[^:\s"\'<>]+:[^@\s"\'<>]+@[^\s"\'<>/]+',
                'severity': FindingSeverity.HIGH,
                'description': 'PostgreSQL connection string with credentials detected'
            },
            
            # Encryption Keys and Hashes
            'hex_key_32': {
                'pattern': r'(?i)(secret|key|token)\s*[:=]\s*["\']?([a-f0-9]{64})["\']?',
                'severity': FindingSeverity.MEDIUM,
                'description': '32-byte hex key detected'
            },
            'base64_key': {
                'pattern': r'(?i)(secret|key|token)\s*[:=]\s*["\']?([A-Za-z0-9+/]{40,}={0,2})["\']?',
                'severity': FindingSeverity.MEDIUM,
                'description': 'Base64 encoded key detected'
            }
        }
    
    def get_compiled_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Get compiled regex patterns"""
        compiled = {}
        for name, config in self.patterns.items():
            compiled[name] = {
                **config,
                'compiled': re.compile(config['pattern'])
            }
        return compiled

class PIIPatterns:
    """Patterns for Personally Identifiable Information detection"""
    
    def __init__(self):
        self.patterns = {
            # Social Security Numbers
            'ssn': {
                'pattern': r'\b\d{3}-\d{2}-\d{4}\b',
                'severity': FindingSeverity.HIGH,
                'description': 'Social Security Number detected'
            },
            'ssn_no_dash': {
                'pattern': r'\b\d{9}\b',
                'severity': FindingSeverity.MEDIUM,
                'description': 'Potential SSN (9 digits) detected'
            },
            
            # Credit Card Numbers
            'credit_card_visa': {
                'pattern': r'\b4\d{3}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
                'severity': FindingSeverity.HIGH,
                'description': 'Visa credit card number detected'
            },
            'credit_card_mastercard': {
                'pattern': r'\b5[1-5]\d{2}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
                'severity': FindingSeverity.HIGH,
                'description': 'Mastercard credit card number detected'
            },
            'credit_card_amex': {
                'pattern': r'\b3[47]\d{2}[-\s]?\d{6}[-\s]?\d{5}\b',
                'severity': FindingSeverity.HIGH,
                'description': 'American Express credit card number detected'
            },
            
            # Email addresses (potentially PII in certain contexts)
            'email_address': {
                'pattern': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                'severity': FindingSeverity.LOW,
                'description': 'Email address detected'
            },
            
            # Phone Numbers
            'phone_us': {
                'pattern': r'\b(\+1[-\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b',
                'severity': FindingSeverity.LOW,
                'description': 'US phone number detected'
            },
            
            # IP Addresses (can be PII in logs)
            'ipv4_address': {
                'pattern': r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b',
                'severity': FindingSeverity.LOW,
                'description': 'IPv4 address detected'
            }
        }
    
    def get_compiled_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Get compiled regex patterns"""
        compiled = {}
        for name, config in self.patterns.items():
            compiled[name] = {
                **config,
                'compiled': re.compile(config['pattern'])
            }
        return compiled

class MaliciousPatterns:
    """Patterns for malicious content detection"""
    
    def __init__(self):
        self.patterns = {
            # Code Injection
            'eval_injection': {
                'pattern': r'(?i)eval\s*\(\s*["\'].*["\'].*\)',
                'severity': FindingSeverity.HIGH,
                'description': 'Potential eval() injection detected'
            },
            'exec_injection': {
                'pattern': r'(?i)exec\s*\(\s*["\'].*["\'].*\)',
                'severity': FindingSeverity.HIGH,
                'description': 'Potential exec() injection detected'
            },
            
            # SQL Injection patterns
            'sql_injection_union': {
                'pattern': r'(?i)union\s+select.*from',
                'severity': FindingSeverity.MEDIUM,
                'description': 'Potential SQL injection (UNION SELECT) detected'
            },
            'sql_injection_drop': {
                'pattern': r'(?i);\s*drop\s+table',
                'severity': FindingSeverity.HIGH,
                'description': 'Potential SQL injection (DROP TABLE) detected'
            },
            
            # Command Injection
            'command_injection_pipe': {
                'pattern': r'[;&|]+\s*(rm|del|format|shutdown|reboot)',
                'severity': FindingSeverity.HIGH,
                'description': 'Potential command injection detected'
            },
            'shell_metacharacters': {
                'pattern': r'`[^`]*`|\$\([^)]*\)',
                'severity': FindingSeverity.MEDIUM,
                'description': 'Shell metacharacters detected'
            },
            
            # XSS patterns
            'xss_script': {
                'pattern': r'(?i)<script[^>]*>.*</script>',
                'severity': FindingSeverity.MEDIUM,
                'description': 'Potential XSS script tag detected'
            },
            'xss_javascript': {
                'pattern': r'(?i)javascript:[^"\']*',
                'severity': FindingSeverity.MEDIUM,
                'description': 'Potential XSS javascript: URL detected'
            },
            
            # Suspicious imports and functions
            'dangerous_imports': {
                'pattern': r'(?i)import\s+(os|subprocess|pickle|marshal|exec|eval)',
                'severity': FindingSeverity.MEDIUM,
                'description': 'Potentially dangerous import detected'
            },
            'globals_locals_access': {
                'pattern': r'(?i)(globals|locals)\s*\(\s*\)',
                'severity': FindingSeverity.MEDIUM,
                'description': 'Access to globals() or locals() detected'
            },
            
            # Obfuscation patterns
            'base64_decode': {
                'pattern': r'(?i)(base64|b64decode|atob)\s*\(',
                'severity': FindingSeverity.LOW,
                'description': 'Base64 decoding detected (potential obfuscation)'
            },
            'hex_decode': {
                'pattern': r'(?i)(hex|unhexlify|fromhex)\s*\(',
                'severity': FindingSeverity.LOW,
                'description': 'Hex decoding detected (potential obfuscation)'
            }
        }
    
    def get_compiled_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Get compiled regex patterns"""
        compiled = {}
        for name, config in self.patterns.items():
            compiled[name] = {
                **config,
                'compiled': re.compile(config['pattern'], re.MULTILINE | re.DOTALL)
            }
        return compiled

class ContentScanner:
    """Main content scanner for security validation"""
    
    def __init__(self):
        self.secret_patterns = SecretPatterns().get_compiled_patterns()
        self.pii_patterns = PIIPatterns().get_compiled_patterns()
        self.malicious_patterns = MaliciousPatterns().get_compiled_patterns()
        
        # Configuration
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.max_line_length = 10000
        
        # Whitelist for known false positives
        self.whitelist = {
            'example_keys': set([
                'your-api-key-here',
                'INSERT_API_KEY_HERE',
                'REPLACE_WITH_YOUR_KEY',
                'dummy-secret-key',
                'test-key-123'
            ])
        }
        
        logger.info("Content scanner initialized with pattern sets")
    
    def scan_content(self, content: str, file_path: str = "unknown") -> ScanResult:
        """Scan content for security issues"""
        
        import time
        start_time = time.time()
        
        # Basic content analysis
        total_bytes = len(content.encode('utf-8', errors='ignore'))
        lines = content.split('\n')
        total_lines = len(lines)
        
        # Check if content is binary
        is_binary = self.is_binary_content(content)
        encoding = self.detect_encoding(content)
        
        # Initialize findings list
        findings = []
        
        if not is_binary and total_bytes <= self.max_file_size:
            # Scan for secrets
            findings.extend(self.scan_for_secrets(content, lines))
            
            # Scan for PII
            findings.extend(self.scan_for_pii(content, lines))
            
            # Scan for malicious patterns
            findings.extend(self.scan_for_malicious_patterns(content, lines))
            
            # Scan for encoding issues
            findings.extend(self.scan_for_encoding_issues(content, lines))
        
        scan_duration = time.time() - start_time
        
        # Create result
        result = ScanResult(
            file_path=file_path,
            findings=findings,
            scan_duration=scan_duration,
            total_lines=total_lines,
            total_bytes=total_bytes,
            encoding=encoding,
            is_binary=is_binary
        )
        
        # Generate recommendations
        result.recommendations = self.generate_recommendations(result)
        
        logger.info(f"Content scan completed: {len(findings)} findings in {scan_duration:.3f}s")
        
        return result
    
    def scan_for_secrets(self, content: str, lines: List[str]) -> List[SecurityFinding]:
        """Scan for secret patterns"""
        
        findings = []
        
        for pattern_name, pattern_config in self.secret_patterns.items():
            pattern = pattern_config['compiled']
            
            for line_num, line in enumerate(lines, 1):
                matches = pattern.finditer(line)
                
                for match in matches:
                    matched_text = match.group()
                    
                    # Check whitelist
                    if self.is_whitelisted_secret(matched_text):
                        continue
                    
                    # Extract the actual secret if it's in a capture group
                    secret_value = match.group(2) if match.lastindex and match.lastindex >= 2 else matched_text
                    
                    findings.append(SecurityFinding(
                        finding_type=FindingType.SECRET,
                        severity=pattern_config['severity'],
                        pattern_name=pattern_name,
                        matched_text=self.sanitize_secret(matched_text),
                        line_number=line_num,
                        column_start=match.start(),
                        column_end=match.end(),
                        description=pattern_config['description'],
                        suggestion=self.get_secret_suggestion(pattern_name),
                        confidence=self.calculate_secret_confidence(secret_value),
                        metadata={
                            'pattern_type': 'secret',
                            'secret_length': len(secret_value),
                            'has_special_chars': any(c in secret_value for c in '!@#$%^&*()'),
                            'is_placeholder': self.looks_like_placeholder(secret_value)
                        }
                    ))
        
        return findings
    
    def scan_for_pii(self, content: str, lines: List[str]) -> List[SecurityFinding]:
        """Scan for PII patterns"""
        
        findings = []
        
        for pattern_name, pattern_config in self.pii_patterns.items():
            pattern = pattern_config['compiled']
            
            for line_num, line in enumerate(lines, 1):
                matches = pattern.finditer(line)
                
                for match in matches:
                    matched_text = match.group()
                    
                    # Validate PII patterns (reduce false positives)
                    if not self.validate_pii_match(pattern_name, matched_text):
                        continue
                    
                    findings.append(SecurityFinding(
                        finding_type=FindingType.PII,
                        severity=pattern_config['severity'],
                        pattern_name=pattern_name,
                        matched_text=self.sanitize_pii(matched_text),
                        line_number=line_num,
                        column_start=match.start(),
                        column_end=match.end(),
                        description=pattern_config['description'],
                        suggestion=self.get_pii_suggestion(pattern_name),
                        confidence=self.calculate_pii_confidence(pattern_name, matched_text),
                        metadata={
                            'pattern_type': 'pii',
                            'sanitized': True
                        }
                    ))
        
        return findings
    
    def scan_for_malicious_patterns(self, content: str, lines: List[str]) -> List[SecurityFinding]:
        """Scan for malicious patterns"""
        
        findings = []
        
        for pattern_name, pattern_config in self.malicious_patterns.items():
            pattern = pattern_config['compiled']
            
            # Scan entire content for multiline patterns
            matches = pattern.finditer(content)
            
            for match in matches:
                matched_text = match.group()
                
                # Find line number
                line_num = content[:match.start()].count('\n') + 1
                
                findings.append(SecurityFinding(
                    finding_type=FindingType.MALICIOUS_PATTERN,
                    severity=pattern_config['severity'],
                    pattern_name=pattern_name,
                    matched_text=matched_text[:100] + "..." if len(matched_text) > 100 else matched_text,
                    line_number=line_num,
                    column_start=match.start() - content[:match.start()].rfind('\n') - 1,
                    column_end=match.end() - content[:match.start()].rfind('\n') - 1,
                    description=pattern_config['description'],
                    suggestion=self.get_malicious_pattern_suggestion(pattern_name),
                    confidence=0.8,  # Default confidence for malicious patterns
                    metadata={
                        'pattern_type': 'malicious',
                        'full_match_length': len(matched_text)
                    }
                ))
        
        return findings
    
    def scan_for_encoding_issues(self, content: str, lines: List[str]) -> List[SecurityFinding]:
        """Scan for encoding and formatting issues"""
        
        findings = []
        
        # Check for very long lines (potential obfuscation)
        for line_num, line in enumerate(lines, 1):
            if len(line) > self.max_line_length:
                findings.append(SecurityFinding(
                    finding_type=FindingType.ENCODING_ISSUE,
                    severity=FindingSeverity.LOW,
                    pattern_name="long_line",
                    matched_text=f"Line length: {len(line)} characters",
                    line_number=line_num,
                    column_start=0,
                    column_end=len(line),
                    description="Extremely long line detected (potential obfuscation)",
                    suggestion="Consider breaking long lines or review for obfuscated content",
                    confidence=0.6,
                    metadata={'line_length': len(line)}
                ))
        
        # Check for null bytes
        null_byte_positions = [i for i, char in enumerate(content) if char == '\x00']
        if null_byte_positions:
            findings.append(SecurityFinding(
                finding_type=FindingType.ENCODING_ISSUE,
                severity=FindingSeverity.MEDIUM,
                pattern_name="null_bytes",
                matched_text=f"Null bytes at positions: {null_byte_positions[:5]}",
                line_number=1,
                column_start=null_byte_positions[0],
                column_end=null_byte_positions[0] + 1,
                description="Null bytes detected in content",
                suggestion="Remove null bytes or verify file integrity",
                confidence=1.0,
                metadata={'null_byte_count': len(null_byte_positions)}
            ))
        
        return findings
    
    def is_binary_content(self, content: str) -> bool:
        """Check if content is binary"""
        
        # Check for null bytes
        if '\x00' in content:
            return True
        
        # Check for high ratio of non-printable characters
        printable_chars = sum(1 for c in content if c.isprintable() or c in '\n\r\t')
        total_chars = len(content)
        
        if total_chars > 0:
            printable_ratio = printable_chars / total_chars
            return printable_ratio < 0.7
        
        return False
    
    def detect_encoding(self, content: str) -> str:
        """Detect content encoding"""
        
        try:
            # Try to encode as UTF-8
            content.encode('utf-8')
            return 'utf-8'
        except UnicodeEncodeError:
            pass
        
        try:
            # Try to encode as Latin-1
            content.encode('latin-1')
            return 'latin-1'
        except UnicodeEncodeError:
            pass
        
        return 'unknown'
    
    def is_whitelisted_secret(self, matched_text: str) -> bool:
        """Check if a secret match is whitelisted"""
        
        # Check exact matches
        if matched_text.lower() in self.whitelist['example_keys']:
            return True
        
        # Check for common placeholder patterns
        placeholder_patterns = [
            r'(?i)(your|my|the)[-_]?(api[-_]?)?key',
            r'(?i)insert[-_]?.*[-_]?here',
            r'(?i)replace[-_]?.*[-_]?your',
            r'(?i)(dummy|fake|test|example)[-_]?',
            r'(?i)xxx+',
            r'\*{3,}'
        ]
        
        for pattern in placeholder_patterns:
            if re.search(pattern, matched_text):
                return True
        
        return False
    
    def validate_pii_match(self, pattern_name: str, matched_text: str) -> bool:
        """Validate PII matches to reduce false positives"""
        
        if pattern_name == 'ssn_no_dash':
            # Check if 9-digit number is likely an SSN
            digits = matched_text
            
            # Common false positives
            false_positives = ['123456789', '000000000', '111111111']
            if digits in false_positives:
                return False
            
            # Check for sequential or repeated patterns
            if len(set(digits)) < 3:  # Too few unique digits
                return False
        
        elif pattern_name == 'email_address':
            # Basic email validation
            if '@' not in matched_text or '.' not in matched_text.split('@')[-1]:
                return False
        
        return True
    
    def sanitize_secret(self, secret: str) -> str:
        """Sanitize secret for safe logging"""
        if len(secret) <= 8:
            return '*' * len(secret)
        
        # Show first 3 and last 3 characters
        return secret[:3] + '*' * (len(secret) - 6) + secret[-3:]
    
    def sanitize_pii(self, pii: str) -> str:
        """Sanitize PII for safe logging"""
        if len(pii) <= 4:
            return '*' * len(pii)
        
        # Show first 2 and last 2 characters
        return pii[:2] + '*' * (len(pii) - 4) + pii[-2:]
    
    def looks_like_placeholder(self, value: str) -> bool:
        """Check if a value looks like a placeholder"""
        
        placeholder_indicators = [
            'example', 'dummy', 'test', 'fake', 'your', 'insert',
            'replace', 'here', 'xxx', 'abc', '123'
        ]
        
        value_lower = value.lower()
        return any(indicator in value_lower for indicator in placeholder_indicators)
    
    def calculate_secret_confidence(self, secret_value: str) -> float:
        """Calculate confidence score for secret detection"""
        
        if self.looks_like_placeholder(secret_value):
            return 0.2
        
        # Higher confidence for longer, more complex secrets
        length_factor = min(1.0, len(secret_value) / 32)
        complexity_factor = 0.5
        
        # Check for character diversity
        has_upper = any(c.isupper() for c in secret_value)
        has_lower = any(c.islower() for c in secret_value)
        has_digit = any(c.isdigit() for c in secret_value)
        has_special = any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in secret_value)
        
        diversity_score = sum([has_upper, has_lower, has_digit, has_special]) / 4
        complexity_factor = 0.3 + (0.7 * diversity_score)
        
        return min(1.0, length_factor * complexity_factor + 0.3)
    
    def calculate_pii_confidence(self, pattern_name: str, matched_text: str) -> float:
        """Calculate confidence score for PII detection"""
        
        confidence_map = {
            'ssn': 0.9,
            'ssn_no_dash': 0.6,
            'credit_card_visa': 0.8,
            'credit_card_mastercard': 0.8,
            'credit_card_amex': 0.8,
            'email_address': 0.4,
            'phone_us': 0.6,
            'ipv4_address': 0.3
        }
        
        return confidence_map.get(pattern_name, 0.7)
    
    def get_secret_suggestion(self, pattern_name: str) -> str:
        """Get suggestion for secret findings"""
        
        suggestions = {
            'api_key_generic': 'Use environment variables or secure key management',
            'password_field': 'Use secure password storage and hashing',
            'private_key_rsa': 'Store private keys in secure key management system',
            'aws_access_key': 'Use IAM roles or environment variables',
            'github_token': 'Use GitHub secrets or environment variables'
        }
        
        return suggestions.get(pattern_name, 'Remove or secure this credential')
    
    def get_pii_suggestion(self, pattern_name: str) -> str:
        """Get suggestion for PII findings"""
        
        suggestions = {
            'ssn': 'Remove or mask SSN, use tokenization if needed',
            'credit_card_visa': 'Remove or mask credit card number',
            'email_address': 'Consider if email exposure is necessary',
            'phone_us': 'Remove or mask phone number'
        }
        
        return suggestions.get(pattern_name, 'Review if this PII is necessary')
    
    def get_malicious_pattern_suggestion(self, pattern_name: str) -> str:
        """Get suggestion for malicious pattern findings"""
        
        suggestions = {
            'eval_injection': 'Use safer alternatives to eval()',
            'sql_injection_union': 'Use parameterized queries',
            'command_injection_pipe': 'Validate and sanitize command inputs',
            'xss_script': 'Sanitize HTML content and use CSP headers',
            'dangerous_imports': 'Review necessity of dangerous imports'
        }
        
        return suggestions.get(pattern_name, 'Review and validate this pattern')
    
    def generate_recommendations(self, scan_result: ScanResult) -> List[str]:
        """Generate overall recommendations based on scan results"""
        
        recommendations = []
        
        # Count findings by severity
        severity_counts = {}
        for finding in scan_result.findings:
            severity_counts[finding.severity] = severity_counts.get(finding.severity, 0) + 1
        
        # Generate recommendations based on findings
        if severity_counts.get(FindingSeverity.CRITICAL, 0) > 0:
            recommendations.append("🚨 CRITICAL: Immediate action required - secrets or critical vulnerabilities detected")
        
        if severity_counts.get(FindingSeverity.HIGH, 0) > 0:
            recommendations.append("⚠️ HIGH: Review and remediate high-risk findings before deployment")
        
        if len(scan_result.findings) > 10:
            recommendations.append("📊 Multiple issues detected - consider systematic security review")
        
        if scan_result.is_binary:
            recommendations.append("🔍 Binary file detected - consider manual review if security-sensitive")
        
        # General recommendations
        if scan_result.findings:
            recommendations.extend([
                "🔒 Use environment variables for sensitive configuration",
                "🛡️ Implement secrets scanning in CI/CD pipeline",
                "📝 Review code for security best practices"
            ])
        else:
            recommendations.append("✅ No security issues detected - good security hygiene")
        
        return recommendations

# Example usage and testing
def test_content_scanner():
    """Test the content scanner functionality"""
    
    scanner = ContentScanner()
    
    # Test content with various security issues
    test_content = '''
# Configuration file
API_KEY = "sk-1234567890abcdef1234567890abcdef"
password = "super_secret_password"
database_url = "postgresql://user:pass@localhost/db"

# Some code
import os
import subprocess

def dangerous_function():
    eval("print('hello')")
    
# Personal data
ssn = "123-45-6789"
email = "user@example.com"
phone = "555-123-4567"

# Suspicious patterns
credit_card = "4111-1111-1111-1111"
'''
    
    print("🧪 Testing Content Scanner...")
    
    result = scanner.scan_content(test_content, "test_file.py")
    
    print(f"📊 Scan Results:")
    print(f"  File: {result.file_path}")
    print(f"  Findings: {len(result.findings)}")
    print(f"  Risk Score: {result.overall_risk_score:.2f}")
    print(f"  Scan Duration: {result.scan_duration:.3f}s")
    print(f"  Binary: {result.is_binary}")
    
    print(f"\n🔍 Detailed Findings:")
    for finding in result.findings:
        print(f"  {finding.severity.value.upper()}: {finding.description}")
        print(f"    Line {finding.line_number}: {finding.matched_text}")
        print(f"    Confidence: {finding.confidence:.2f}")
        print()
    
    print(f"💡 Recommendations:")
    for rec in result.recommendations:
        print(f"  {rec}")

if __name__ == "__main__":
    test_content_scanner()