# Compatibility shim for tests expecting imports from shared.src.server
from base_server import ServerConfig, BaseMCPServer  # re-export for tests

# Provide a placeholder MLCodeIntelligenceServer to satisfy test import without heavy deps
class MLCodeIntelligenceServer:  # type: ignore
    pass