#!/usr/bin/env python3
"""
TLS Configuration for MCP Servers
Implements HTTPS encryption for secure communication
"""

import ssl
import os
from pathlib import Path
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from datetime import datetime, timedelta

class TLSManager:
    """Manages TLS certificates and SSL contexts for MCP servers"""
    
    def __init__(self):
        self.cert_dir = Path("/home/dell/coding/bash/10x-agentic-setup/mcp_servers/security/certs")
        self.cert_dir.mkdir(exist_ok=True, parents=True)
        
        # Set secure permissions
        os.chmod(self.cert_dir, 0o700)
    
    def generate_self_signed_cert(self, hostname: str = "localhost", validity_days: int = 365) -> tuple:
        """Generate self-signed certificate for development"""
        
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        
        # Create certificate
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "California"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "San Francisco"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "10X Agentic Setup"),
            x509.NameAttribute(NameOID.COMMON_NAME, hostname),
        ])
        
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + timedelta(days=validity_days)
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName(hostname),
                x509.DNSName("127.0.0.1"),
                x509.IPAddress("127.0.0.1".encode()),
            ]),
            critical=False,
        ).add_extension(
            x509.KeyUsage(
                key_cert_sign=False,
                crl_sign=False,
                digital_signature=True,
                content_commitment=False,
                key_encipherment=True,
                data_encipherment=False,
                key_agreement=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        ).add_extension(
            x509.ExtendedKeyUsage([
                x509.oid.ExtendedKeyUsageOID.SERVER_AUTH,
            ]),
            critical=True,
        ).sign(private_key, hashes.SHA256())
        
        # Save certificate and private key
        cert_file = self.cert_dir / f"{hostname}.crt"
        key_file = self.cert_dir / f"{hostname}.key"
        
        with open(cert_file, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        
        with open(key_file, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        # Set secure permissions
        os.chmod(cert_file, 0o644)
        os.chmod(key_file, 0o600)
        
        return str(cert_file), str(key_file)
    
    def create_ssl_context(self, cert_file: str, key_file: str) -> ssl.SSLContext:
        """Create secure SSL context for HTTPS servers"""
        
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(cert_file, key_file)
        
        # Security hardening
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        context.set_ciphers('ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS')
        context.options |= ssl.OP_NO_SSLv2
        context.options |= ssl.OP_NO_SSLv3
        context.options |= ssl.OP_NO_TLSv1
        context.options |= ssl.OP_NO_TLSv1_1
        context.options |= ssl.OP_SINGLE_DH_USE
        context.options |= ssl.OP_SINGLE_ECDH_USE
        
        return context
    
    def setup_server_tls(self, server_name: str, port: int) -> dict:
        """Setup TLS configuration for an MCP server"""
        
        # Generate certificate if not exists
        cert_file = self.cert_dir / f"{server_name}.crt"
        key_file = self.cert_dir / f"{server_name}.key"
        
        if not cert_file.exists() or not key_file.exists():
            cert_path, key_path = self.generate_self_signed_cert(server_name)
        else:
            cert_path, key_path = str(cert_file), str(key_file)
        
        # Create SSL context
        ssl_context = self.create_ssl_context(cert_path, key_path)
        
        return {
            'ssl_context': ssl_context,
            'cert_file': cert_path,
            'key_file': key_path,
            'port': port,
            'url': f"https://{server_name}:{port}"
        }

# Secure server configuration template
SECURE_SERVER_CONFIG = """
import ssl
from flask import Flask
from mcp_auth_middleware import require_auth

app = Flask(__name__)

# Load TLS configuration
tls_manager = TLSManager()
tls_config = tls_manager.setup_server_tls("{server_name}", {port})

@app.route('/health')
@require_auth("{server_name}")
def health_check():
    return {{"status": "healthy", "server": "{server_name}"}}

@app.route('/api/v1/{endpoint}', methods=['POST'])
@require_auth("{server_name}")
def {endpoint}_handler():
    # Your API logic here
    return {{"message": "Secure endpoint"}}

if __name__ == '__main__':
    app.run(
        host='127.0.0.1',
        port={port},
        ssl_context=tls_config['ssl_context'],
        debug=False
    )
"""

def generate_secure_server_configs():
    """Generate secure server configuration files"""
    servers = [
        ('ml-code-intelligence', 8001, 'analyze'),
        ('context-aware-memory', 8002, 'retrieve'),
        ('agentic-workflow', 8003, 'orchestrate'),
        ('predictive-analytics', 8004, 'predict'),
        ('ml-testing-qa', 8005, 'test'),
        ('10x-knowledge-graph', 8006, 'query'),
        ('10x-command-analytics', 8007, 'analytics')
    ]
    
    for server_name, port, endpoint in servers:
        config_content = SECURE_SERVER_CONFIG.format(
            server_name=server_name,
            port=port,
            endpoint=endpoint
        )
        
        config_file = Path(f"/home/dell/coding/bash/10x-agentic-setup/mcp_servers/{server_name}/secure_server.py")
        config_file.parent.mkdir(exist_ok=True, parents=True)
        
        with open(config_file, 'w') as f:
            f.write(config_content)
        
        print(f"Generated secure config for {server_name}")

if __name__ == "__main__":
    tls_manager = TLSManager()
    
    # Generate certificates for all servers
    servers = ['ml-code-intelligence', 'context-aware-memory', 'agentic-workflow',
               'predictive-analytics', 'ml-testing-qa', '10x-knowledge-graph', 
               '10x-command-analytics']
    
    for server in servers:
        cert_path, key_path = tls_manager.generate_self_signed_cert(server)
        print(f"Generated TLS certificate for {server}: {cert_path}")
    
    # Generate secure server configurations
    generate_secure_server_configs()
    print("TLS setup complete!")