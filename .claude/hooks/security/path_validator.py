#!/usr/bin/env python3
"""
Path Validator for Security Validation System
Validates file paths and prevents unauthorized access to critical infrastructure
"""

import os
import re
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
import fnmatch
import hashlib
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ValidationSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class ValidationResult:
    allowed: bool
    reason: str = ""
    severity: ValidationSeverity = ValidationSeverity.LOW
    suggested_alternative: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class PathValidator:
    """Validates file paths for security compliance"""
    
    def __init__(self):
        # Critical path patterns that require special protection
        self.critical_patterns = [
            "mcp_servers/*/src/server.py",      # MCP server implementations
            ".claude/hooks/**/*",               # Hook configurations and scripts
            ".claude/commands/**/*",            # Command definitions  
            ".claude/**/config*.json",          # Configuration files
            "Knowledge/intelligence/**/*",      # Intelligence data
            "Instructions/**/*",                # Development procedures
            "**/.env*",                        # Environment files
            "**/secrets*",                     # Secret files
            "**/*credentials*",                # Credential files
            "**/config/production*",           # Production configs
            "**/deployment/**/*",              # Deployment files
            "**/*.key",                        # Key files
            "**/*.pem",                        # Certificate files
            "**/database.sqlite*",             # Database files
            "**/*backup*",                     # Backup files
        ]
        
        # Patterns that are completely blocked
        self.blocked_patterns = [
            "**/.git/**/*",                    # Git internals
            "**/node_modules/**/*",            # Dependencies
            "**/__pycache__/**/*",             # Python cache
            "**/venv/**/*",                    # Virtual environments
            "**/.venv/**/*",                   # Virtual environments
            "/etc/**/*",                       # System configs (absolute)
            "/root/**/*",                      # Root directory
            "/home/*/.*ssh*",                  # SSH configs
            "**/*.log",                        # Log files
            "**/tmp/**/*",                     # Temporary files
        ]
        
        # Allowed file extensions for editing
        self.allowed_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.scss',
            '.json', '.yaml', '.yml', '.toml', '.xml', '.md', '.txt',
            '.sh', '.bash', '.zsh', '.fish', '.ps1', '.bat', '.cmd',
            '.sql', '.graphql', '.proto', '.dockerfile', '.docker',
            '.conf', '.config', '.ini', '.properties'
        }
        
        # Whitelist for trusted operations
        self.whitelist_cache = {}
        self.validation_cache = {}
        
        # Load project root
        self.project_root = Path.cwd()
        while self.project_root.parent != self.project_root:
            if (self.project_root / ".claude").exists():
                break
            self.project_root = self.project_root.parent
        
        logger.info(f"Path validator initialized with project root: {self.project_root}")
    
    def validate_path(self, path: str, operation: str = "read") -> ValidationResult:
        """Validate a file path for the given operation"""
        
        # Check cache first
        cache_key = f"{path}:{operation}"
        if cache_key in self.validation_cache:
            return self.validation_cache[cache_key]
        
        # Normalize path
        normalized_path = self.normalize_path(path)
        
        # Basic security checks
        basic_result = self.check_basic_security(normalized_path)
        if not basic_result.allowed:
            self.validation_cache[cache_key] = basic_result
            return basic_result
        
        # Check against blocked patterns
        blocked_result = self.check_blocked_patterns(normalized_path)
        if not blocked_result.allowed:
            self.validation_cache[cache_key] = blocked_result
            return blocked_result
        
        # Check file extension
        extension_result = self.check_file_extension(normalized_path, operation)
        if not extension_result.allowed:
            self.validation_cache[cache_key] = extension_result
            return extension_result
        
        # Check critical paths
        critical_result = self.check_critical_paths(normalized_path, operation)
        if not critical_result.allowed:
            self.validation_cache[cache_key] = critical_result
            return critical_result
        
        # Check operation-specific rules
        operation_result = self.check_operation_specific(normalized_path, operation)
        
        self.validation_cache[cache_key] = operation_result
        return operation_result
    
    def normalize_path(self, path: str) -> str:
        """Normalize and clean the path"""
        
        # Convert to Path object for normalization
        try:
            path_obj = Path(path).resolve()
            
            # Make relative to project root if possible
            try:
                relative_path = path_obj.relative_to(self.project_root)
                return str(relative_path)
            except ValueError:
                # Path is outside project root
                return str(path_obj)
        except Exception:
            # If path resolution fails, return cleaned version
            return os.path.normpath(path)
    
    def check_basic_security(self, path: str) -> ValidationResult:
        """Check for basic security violations"""
        
        # Path traversal attempts
        if ".." in path:
            return ValidationResult(
                allowed=False,
                reason="Path traversal attempt detected",
                severity=ValidationSeverity.CRITICAL,
                metadata={"security_violation": "path_traversal", "path": path}
            )
        
        # Absolute paths outside project
        if os.path.isabs(path):
            # Allow some specific absolute paths
            allowed_absolute = [
                "/tmp/claude_",  # Temporary Claude files
                str(self.project_root)  # Project root
            ]
            
            if not any(path.startswith(allowed) for allowed in allowed_absolute):
                return ValidationResult(
                    allowed=False,
                    reason="Absolute path outside project scope",
                    severity=ValidationSeverity.HIGH,
                    metadata={"security_violation": "absolute_path", "path": path}
                )
        
        # Null byte injection
        if '\x00' in path:
            return ValidationResult(
                allowed=False,
                reason="Null byte injection detected",
                severity=ValidationSeverity.CRITICAL,
                metadata={"security_violation": "null_byte", "path": path}
            )
        
        # Extremely long paths (potential buffer overflow)
        if len(path) > 4096:
            return ValidationResult(
                allowed=False,
                reason="Path length exceeds maximum allowed",
                severity=ValidationSeverity.MEDIUM,
                metadata={"security_violation": "path_length", "length": len(path)}
            )
        
        return ValidationResult(allowed=True)
    
    def check_blocked_patterns(self, path: str) -> ValidationResult:
        """Check if path matches blocked patterns"""
        
        for pattern in self.blocked_patterns:
            if fnmatch.fnmatch(path, pattern):
                return ValidationResult(
                    allowed=False,
                    reason=f"Path matches blocked pattern: {pattern}",
                    severity=ValidationSeverity.HIGH,
                    metadata={"blocked_pattern": pattern, "path": path}
                )
        
        return ValidationResult(allowed=True)
    
    def check_file_extension(self, path: str, operation: str) -> ValidationResult:
        """Check file extension for allowed operations"""
        
        # Skip extension check for read operations on existing files
        if operation == "read" and os.path.exists(path):
            return ValidationResult(allowed=True)
        
        # For write operations, check extension
        if operation in ["write", "edit", "create"]:
            path_obj = Path(path)
            extension = path_obj.suffix.lower()
            
            if extension and extension not in self.allowed_extensions:
                return ValidationResult(
                    allowed=False,
                    reason=f"File extension '{extension}' not allowed for {operation} operations",
                    severity=ValidationSeverity.MEDIUM,
                    suggested_alternative=f"Use allowed extensions: {', '.join(sorted(self.allowed_extensions))}",
                    metadata={"disallowed_extension": extension, "operation": operation}
                )
        
        return ValidationResult(allowed=True)
    
    def check_critical_paths(self, path: str, operation: str) -> ValidationResult:
        """Check access to critical infrastructure paths"""
        
        for pattern in self.critical_patterns:
            if fnmatch.fnmatch(path, pattern):
                logger.warning(f"Critical path access: {path} (pattern: {pattern}, operation: {operation})")
                
                # For critical paths, we allow read but require extra validation for write
                if operation == "read":
                    return ValidationResult(
                        allowed=True,
                        reason=f"Read access to critical path: {pattern}",
                        severity=ValidationSeverity.MEDIUM,
                        metadata={"critical_path": True, "pattern": pattern}
                    )
                else:
                    # Write operations to critical paths require validation
                    return self.validate_critical_write_operation(path, operation, pattern)
        
        return ValidationResult(allowed=True)
    
    def validate_critical_write_operation(self, path: str, operation: str, pattern: str) -> ValidationResult:
        """Validate write operations to critical paths"""
        
        # Check if this is a known safe operation
        if self.is_safe_critical_operation(path, operation):
            return ValidationResult(
                allowed=True,
                reason=f"Validated safe operation on critical path",
                severity=ValidationSeverity.MEDIUM,
                metadata={
                    "critical_path": True,
                    "pattern": pattern,
                    "validated_safe": True
                }
            )
        
        # For now, allow with warning (in production, might require approval)
        return ValidationResult(
            allowed=True,
            reason=f"Critical path modification requires careful review",
            severity=ValidationSeverity.HIGH,
            metadata={
                "critical_path": True,
                "pattern": pattern,
                "requires_review": True,
                "backup_recommended": True
            }
        )
    
    def is_safe_critical_operation(self, path: str, operation: str) -> bool:
        """Check if a critical path operation is considered safe"""
        
        safe_operations = {
            # Adding new files is generally safer than modifying existing ones
            "create": ["mcp_servers/*/tests/*", ".claude/hooks/*/test_*"],
            
            # Documentation updates are generally safe
            "edit": ["**/*.md", "Instructions/**.md"],
            
            # Configuration additions (not modifications) can be safe
            "write": [".claude/hooks/*/new_*"]
        }
        
        if operation in safe_operations:
            patterns = safe_operations[operation]
            return any(fnmatch.fnmatch(path, pattern) for pattern in patterns)
        
        return False
    
    def check_operation_specific(self, path: str, operation: str) -> ValidationResult:
        """Check operation-specific rules"""
        
        # Delete operations are highly restricted
        if operation == "delete":
            return ValidationResult(
                allowed=False,
                reason="Delete operations are not permitted through this interface",
                severity=ValidationSeverity.HIGH,
                suggested_alternative="Use version control or move to archive folder",
                metadata={"blocked_operation": "delete"}
            )
        
        # Execute permissions for scripts
        if operation == "execute":
            if not path.endswith(('.sh', '.py', '.js', '.ts')):
                return ValidationResult(
                    allowed=False,
                    reason="Execute permission only allowed for script files",
                    severity=ValidationSeverity.MEDIUM,
                    metadata={"blocked_execution": True, "file_type": Path(path).suffix}
                )
        
        return ValidationResult(allowed=True)
    
    def add_to_whitelist(self, path: str, operation: str, reason: str = ""):
        """Add a path to the whitelist for future operations"""
        
        whitelist_key = f"{path}:{operation}"
        self.whitelist_cache[whitelist_key] = {
            "added_at": __import__('time').time(),
            "reason": reason,
            "hash": hashlib.md5(path.encode()).hexdigest()
        }
        
        logger.info(f"Added to whitelist: {path} for {operation} - {reason}")
    
    def is_whitelisted(self, path: str, operation: str) -> bool:
        """Check if a path/operation combination is whitelisted"""
        
        whitelist_key = f"{path}:{operation}"
        return whitelist_key in self.whitelist_cache
    
    def get_validation_stats(self) -> Dict[str, Any]:
        """Get validation statistics"""
        
        return {
            "total_validations": len(self.validation_cache),
            "critical_patterns": len(self.critical_patterns),
            "blocked_patterns": len(self.blocked_patterns),
            "allowed_extensions": len(self.allowed_extensions),
            "whitelist_entries": len(self.whitelist_cache),
            "project_root": str(self.project_root)
        }
    
    def clear_cache(self):
        """Clear validation cache"""
        self.validation_cache.clear()
        logger.info("Validation cache cleared")

# Example usage and testing
def test_path_validator():
    """Test the path validator functionality"""
    
    validator = PathValidator()
    
    test_cases = [
        # Valid paths
        ("src/main.py", "read", True),
        ("docs/readme.md", "write", True),
        ("tests/test_something.py", "edit", True),
        
        # Invalid paths - traversal
        ("../../../etc/passwd", "read", False),
        ("src/../../../secret.txt", "read", False),
        
        # Invalid paths - blocked patterns
        (".git/config", "read", False),
        ("node_modules/something/file.js", "read", False),
        ("__pycache__/module.pyc", "read", False),
        
        # Critical paths - read allowed
        ("mcp_servers/ml_code_intelligence/src/server.py", "read", True),
        (".claude/hooks/security/validator.py", "read", True),
        
        # Critical paths - write needs validation
        ("mcp_servers/ml_code_intelligence/src/server.py", "write", True),
        (".claude/hooks/security/validator.py", "edit", True),
        
        # Blocked operations
        ("any_file.txt", "delete", False),
        ("script.txt", "execute", False),
    ]
    
    print("🧪 Testing Path Validator...")
    passed = 0
    failed = 0
    
    for path, operation, expected_allowed in test_cases:
        result = validator.validate_path(path, operation)
        actual_allowed = result.allowed
        
        status = "✅" if actual_allowed == expected_allowed else "❌"
        print(f"  {status} {path} ({operation}): {actual_allowed} - {result.reason}")
        
        if actual_allowed == expected_allowed:
            passed += 1
        else:
            failed += 1
    
    print(f"\n📊 Results: {passed} passed, {failed} failed")
    
    # Print statistics
    stats = validator.get_validation_stats()
    print(f"📈 Validator Stats: {stats}")

if __name__ == "__main__":
    test_path_validator()