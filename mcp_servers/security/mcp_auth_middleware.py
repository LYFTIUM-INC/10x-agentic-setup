#!/usr/bin/env python3
"""
MCP Server Authentication Middleware
Implements secure API key authentication for all MCP servers
"""

import os
import secrets
import hashlib
import time
import json
from typing import Dict, Optional, List, Tuple
from functools import wraps
from pathlib import Path

class MCPAuthMiddleware:
    """Authentication middleware for MCP servers"""
    
    def __init__(self):
        self.api_keys = {}
        self.rate_limits = {}
        self.failed_attempts = {}
        
        # Load or generate API keys
        self._load_or_generate_keys()
        
        # Security configuration
        self.max_failed_attempts = 5
        self.lockout_duration = 300  # 5 minutes
        self.rate_limit_window = 60  # 1 minute
        self.rate_limit_requests = 100  # requests per window
        
    def _load_or_generate_keys(self):
        """Load existing API keys or generate new ones"""
        auth_file = Path("/home/dell/coding/bash/10x-agentic-setup/mcp_servers/.auth_keys.json")
        
        if auth_file.exists():
            try:
                with open(auth_file, 'r') as f:
                    data = json.load(f)
                    self.api_keys = data.get('api_keys', {})
            except (json.JSONDecodeError, IOError):
                self._generate_new_keys()
        else:
            self._generate_new_keys()
    
    def _generate_new_keys(self):
        """Generate new API keys for all MCP servers"""
        servers = [
            'ml-code-intelligence',
            'context-aware-memory', 
            'agentic-workflow',
            'predictive-analytics',
            'ml-testing-qa',
            '10x-knowledge-graph',
            '10x-command-analytics'
        ]
        
        for server in servers:
            # Generate secure API key
            api_key = secrets.token_urlsafe(32)
            # Hash for storage
            key_hash = hashlib.sha256(api_key.encode()).hexdigest()
            
            self.api_keys[server] = {
                'key_hash': key_hash,
                'created': int(time.time()),
                'permissions': ['read', 'write', 'execute']
            }
            
            # Also store the plain key for initial setup (remove after deployment)
            print(f"Generated API key for {server}: {api_key}")
        
        # Save to secure file
        auth_file = Path("/home/dell/coding/bash/10x-agentic-setup/mcp_servers/.auth_keys.json")
        auth_file.parent.mkdir(exist_ok=True)
        
        with open(auth_file, 'w') as f:
            json.dump({
                'api_keys': self.api_keys,
                'generated': int(time.time())
            }, f, indent=2)
        
        # Set secure permissions
        os.chmod(auth_file, 0o600)
    
    def validate_api_key(self, api_key: str, server_name: str, client_ip: str = "127.0.0.1") -> Tuple[bool, str]:
        """Validate API key with rate limiting and brute force protection"""
        
        # Check rate limiting
        if not self._check_rate_limit(client_ip):
            return False, "Rate limit exceeded"
        
        # Check failed attempts lockout
        if self._is_locked_out(client_ip):
            return False, "IP locked out due to failed attempts"
        
        # Validate API key
        if server_name not in self.api_keys:
            self._record_failed_attempt(client_ip)
            return False, "Invalid server name"
        
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        stored_hash = self.api_keys[server_name]['key_hash']
        
        if key_hash == stored_hash:
            # Reset failed attempts on successful auth
            self.failed_attempts.pop(client_ip, None)
            return True, "Authentication successful"
        else:
            self._record_failed_attempt(client_ip)
            return False, "Invalid API key"
    
    def _check_rate_limit(self, client_ip: str) -> bool:
        """Check if client IP is within rate limits"""
        current_time = int(time.time())
        
        if client_ip not in self.rate_limits:
            self.rate_limits[client_ip] = []
        
        # Clean old requests outside the window
        self.rate_limits[client_ip] = [
            req_time for req_time in self.rate_limits[client_ip]
            if current_time - req_time < self.rate_limit_window
        ]
        
        # Check if under limit
        if len(self.rate_limits[client_ip]) < self.rate_limit_requests:
            self.rate_limits[client_ip].append(current_time)
            return True
        
        return False
    
    def _is_locked_out(self, client_ip: str) -> bool:
        """Check if IP is locked out due to failed attempts"""
        if client_ip not in self.failed_attempts:
            return False
        
        attempts, last_attempt = self.failed_attempts[client_ip]
        current_time = int(time.time())
        
        # Check if lockout period has expired
        if current_time - last_attempt > self.lockout_duration:
            del self.failed_attempts[client_ip]
            return False
        
        return attempts >= self.max_failed_attempts
    
    def _record_failed_attempt(self, client_ip: str):
        """Record failed authentication attempt"""
        current_time = int(time.time())
        
        if client_ip in self.failed_attempts:
            attempts, _ = self.failed_attempts[client_ip]
            self.failed_attempts[client_ip] = (attempts + 1, current_time)
        else:
            self.failed_attempts[client_ip] = (1, current_time)

# Authentication decorator for MCP server endpoints
def require_auth(server_name: str):
    """Decorator to require authentication for MCP endpoints"""
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            auth_middleware = MCPAuthMiddleware()
            
            # Extract API key from header or query param
            api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
            client_ip = request.remote_addr or "127.0.0.1"
            
            if not api_key:
                return {"error": "API key required", "status": 401}
            
            # Validate API key
            is_valid, message = auth_middleware.validate_api_key(api_key, server_name, client_ip)
            
            if not is_valid:
                return {"error": message, "status": 401}
            
            # Proceed with authenticated request
            return func(request, *args, **kwargs)
        
        return wrapper
    return decorator

# Generate environment variables file for easy setup
def generate_env_file():
    """Generate .env file with API keys"""
    auth_middleware = MCPAuthMiddleware()
    
    env_file = Path("/home/dell/coding/bash/10x-agentic-setup/mcp_servers/.env.auth")
    
    with open(env_file, 'w') as f:
        f.write("# MCP Server API Keys - Keep Secure!\n")
        f.write("# Generated on: " + time.strftime("%Y-%m-%d %H:%M:%S") + "\n\n")
        
        for server_name in auth_middleware.api_keys:
            # Generate new key for .env file
            api_key = secrets.token_urlsafe(32)
            f.write(f"MCP_{server_name.upper().replace('-', '_')}_API_KEY={api_key}\n")
    
    os.chmod(env_file, 0o600)
    print(f"Environment file generated: {env_file}")

if __name__ == "__main__":
    # Generate API keys and environment file
    generate_env_file()