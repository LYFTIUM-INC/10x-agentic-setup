"""
Configuration Management Utilities for MCP Servers
Environment-based configuration with validation and security
"""

import os
import json
import yaml
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass, field
from pathlib import Path
from pydantic import Field, validator
from pydantic_settings import BaseSettings
import logging

logger = logging.getLogger(__name__)


class MCPServerSettings(BaseSettings):
    """Base MCP server configuration with environment variable support"""
    
    # Server identification
    server_name: str = Field(..., description="MCP server name")
    server_version: str = Field("1.0.0", description="Server version")
    
    # Runtime configuration
    debug: bool = Field(False, env="DEBUG")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    max_workers: int = Field(4, env="MAX_WORKERS")
    
    # Performance settings
    cache_enabled: bool = Field(True, env="CACHE_ENABLED")
    cache_ttl: int = Field(300, env="CACHE_TTL")
    rate_limit: int = Field(100, env="RATE_LIMIT")
    
    # Security settings
    enable_security: bool = Field(True, env="ENABLE_SECURITY")
    allowed_origins: List[str] = Field(["*"], env="ALLOWED_ORIGINS")
    
    # Storage paths
    data_dir: str = Field("./data", env="DATA_DIR")
    cache_dir: str = Field("./cache", env="CACHE_DIR")
    model_cache_dir: str = Field("./models", env="MODEL_CACHE_DIR")
    
    # ML Configuration
    ml_device: str = Field("auto", env="ML_DEVICE")  # auto, cpu, cuda
    embedding_model: str = Field("all-MiniLM-L6-v2", env="EMBEDDING_MODEL")
    max_embedding_length: int = Field(512, env="MAX_EMBEDDING_LENGTH")
    
    # Vector Database
    vector_db_type: str = Field("faiss", env="VECTOR_DB_TYPE")  # faiss, qdrant, chroma
    vector_dimension: int = Field(384, env="VECTOR_DIMENSION")
    
    # External Services
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(None, env="ANTHROPIC_API_KEY")
    
    @validator('log_level')
    def validate_log_level(cls, v):
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v.upper()
    
    @validator('ml_device')
    def validate_ml_device(cls, v):
        valid_devices = ['auto', 'cpu', 'cuda', 'mps']
        if v not in valid_devices:
            raise ValueError(f"ML device must be one of {valid_devices}")
        return v
    
    @validator('vector_db_type')
    def validate_vector_db_type(cls, v):
        valid_types = ['faiss', 'qdrant', 'chroma']
        if v not in valid_types:
            raise ValueError(f"Vector DB type must be one of {valid_types}")
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"  # Allow additional fields for server-specific config


class ConfigManager:
    """Configuration manager for MCP servers"""
    
    def __init__(self, config_file: Optional[str] = None, env_prefix: str = "MCP"):
        self.config_file = config_file
        self.env_prefix = env_prefix
        self._config_cache: Dict[str, Any] = {}
    
    def load_config(self, server_name: str, config_class=MCPServerSettings) -> MCPServerSettings:
        """Load configuration for a specific server"""
        cache_key = f"{server_name}_{config_class.__name__}"
        
        if cache_key in self._config_cache:
            return self._config_cache[cache_key]
        
        # Start with default values
        config_data = {"server_name": server_name}
        
        # Load from file if specified
        if self.config_file:
            file_config = self._load_from_file(self.config_file)
            if server_name in file_config:
                config_data.update(file_config[server_name])
        
        # Load server-specific config file
        server_config_file = f"config/{server_name}.yaml"
        if Path(server_config_file).exists():
            server_config = self._load_from_file(server_config_file)
            config_data.update(server_config)
        
        # Create settings instance (will automatically load from environment)
        settings = config_class(**config_data)
        
        # Ensure required directories exist
        self._ensure_directories(settings)
        
        # Cache the configuration
        self._config_cache[cache_key] = settings
        
        logger.info(f"Loaded configuration for {server_name}")
        return settings
    
    def _load_from_file(self, filepath: str) -> Dict[str, Any]:
        """Load configuration from YAML or JSON file"""
        path = Path(filepath)
        if not path.exists():
            logger.warning(f"Configuration file not found: {filepath}")
            return {}
        
        try:
            with open(path, 'r') as f:
                if path.suffix.lower() in ['.yaml', '.yml']:
                    return yaml.safe_load(f) or {}
                elif path.suffix.lower() == '.json':
                    return json.load(f)
                else:
                    logger.warning(f"Unsupported config file format: {path.suffix}")
                    return {}
        except Exception as e:
            logger.error(f"Failed to load config file {filepath}: {e}")
            return {}
    
    def _ensure_directories(self, settings: MCPServerSettings) -> None:
        """Ensure required directories exist"""
        directories = [
            settings.data_dir,
            settings.cache_dir,
            settings.model_cache_dir
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def save_config(self, server_name: str, config: MCPServerSettings, filepath: Optional[str] = None) -> None:
        """Save configuration to file"""
        if not filepath:
            filepath = f"config/{server_name}.yaml"
        
        # Convert to dictionary, excluding environment-loaded values
        config_dict = config.dict(exclude_unset=True)
        
        # Save to file
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w') as f:
            yaml.dump(config_dict, f, default_flow_style=False)
        
        logger.info(f"Saved configuration for {server_name} to {filepath}")


@dataclass
class MLModelConfig:
    """Configuration for ML models"""
    name: str
    type: str  # "embedding", "classification", "generation"
    model_path: str
    device: str = "auto"
    max_length: int = 512
    batch_size: int = 32
    cache_enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VectorDBConfig:
    """Configuration for vector databases"""
    type: str  # "faiss", "qdrant", "chroma"
    dimension: int
    index_type: str = "flat"  # For FAISS: "flat", "ivf", "hnsw"
    connection_params: Dict[str, Any] = field(default_factory=dict)
    persistence_path: Optional[str] = None


class ServerConfigBuilder:
    """Builder pattern for creating server configurations"""
    
    def __init__(self, server_name: str):
        self.server_name = server_name
        self._config_data = {"server_name": server_name}
    
    def with_debug(self, debug: bool = True):
        """Enable debug mode"""
        self._config_data["debug"] = debug
        return self
    
    def with_cache(self, enabled: bool = True, ttl: int = 300):
        """Configure caching"""
        self._config_data["cache_enabled"] = enabled
        self._config_data["cache_ttl"] = ttl
        return self
    
    def with_ml_device(self, device: str = "auto"):
        """Configure ML device"""
        self._config_data["ml_device"] = device
        return self
    
    def with_embedding_model(self, model: str, max_length: int = 512):
        """Configure embedding model"""
        self._config_data["embedding_model"] = model
        self._config_data["max_embedding_length"] = max_length
        return self
    
    def with_vector_db(self, db_type: str = "faiss", dimension: int = 384):
        """Configure vector database"""
        self._config_data["vector_db_type"] = db_type
        self._config_data["vector_dimension"] = dimension
        return self
    
    def with_directories(self, data_dir: str = "./data", cache_dir: str = "./cache"):
        """Configure directories"""
        self._config_data["data_dir"] = data_dir
        self._config_data["cache_dir"] = cache_dir
        return self
    
    def with_security(self, enabled: bool = True, rate_limit: int = 100):
        """Configure security settings"""
        self._config_data["enable_security"] = enabled
        self._config_data["rate_limit"] = rate_limit
        return self
    
    def build(self) -> MCPServerSettings:
        """Build the configuration"""
        return MCPServerSettings(**self._config_data)


class EnvironmentManager:
    """Manage environment variables and secrets"""
    
    @staticmethod
    def get_required_env(key: str, default: Optional[str] = None) -> str:
        """Get required environment variable"""
        value = os.environ.get(key, default)
        if value is None:
            raise ValueError(f"Required environment variable not set: {key}")
        return value
    
    @staticmethod
    def get_optional_env(key: str, default: str = "") -> str:
        """Get optional environment variable"""
        return os.environ.get(key, default)
    
    @staticmethod
    def set_env(key: str, value: str) -> None:
        """Set environment variable"""
        os.environ[key] = value
    
    @staticmethod
    def load_env_file(filepath: str = ".env") -> None:
        """Load environment variables from file"""
        env_path = Path(filepath)
        if not env_path.exists():
            logger.warning(f"Environment file not found: {filepath}")
            return
        
        try:
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        os.environ[key] = value
            
            logger.info(f"Loaded environment variables from {filepath}")
        except Exception as e:
            logger.error(f"Failed to load environment file {filepath}: {e}")


def create_development_config(server_name: str) -> MCPServerSettings:
    """Create a development configuration"""
    return (ServerConfigBuilder(server_name)
            .with_debug(True)
            .with_cache(enabled=True, ttl=60)  # Short TTL for development
            .with_ml_device("cpu")  # Use CPU for development
            .with_security(enabled=False)  # Disable security for development
            .build())


def create_production_config(server_name: str) -> MCPServerSettings:
    """Create a production configuration"""
    return (ServerConfigBuilder(server_name)
            .with_debug(False)
            .with_cache(enabled=True, ttl=3600)  # Long TTL for production
            .with_ml_device("auto")  # Auto-detect best device
            .with_security(enabled=True, rate_limit=1000)  # Enable security
            .build())


def validate_config(config: MCPServerSettings) -> List[str]:
    """Validate configuration and return list of issues"""
    issues = []
    
    # Check directory permissions
    for dir_attr in ['data_dir', 'cache_dir', 'model_cache_dir']:
        directory = getattr(config, dir_attr)
        path = Path(directory)
        
        if not path.exists():
            try:
                path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                issues.append(f"Cannot create directory {directory}: {e}")
        elif not os.access(path, os.W_OK):
            issues.append(f"Directory {directory} is not writable")
    
    # Validate ML device
    if config.ml_device == "cuda":
        try:
            import torch
            if not torch.cuda.is_available():
                issues.append("CUDA requested but not available")
        except ImportError:
            issues.append("PyTorch not available for CUDA check")
    
    # Validate embedding model format
    if not config.embedding_model:
        issues.append("Embedding model not specified")
    
    # Validate vector dimension
    if config.vector_dimension <= 0:
        issues.append("Vector dimension must be positive")
    
    return issues


# Example usage and testing
if __name__ == "__main__":
    # Create configuration manager
    config_manager = ConfigManager()
    
    # Create development configuration
    dev_config = create_development_config("test-server")
    print("Development Config:", dev_config.dict())
    
    # Validate configuration
    issues = validate_config(dev_config)
    if issues:
        print("Configuration issues:", issues)
    else:
        print("Configuration valid!")
    
    # Test builder pattern
    custom_config = (ServerConfigBuilder("custom-server")
                    .with_debug(True)
                    .with_embedding_model("sentence-transformers/all-MiniLM-L6-v2")
                    .with_vector_db("qdrant", 384)
                    .build())
    
    print("Custom Config:", custom_config.dict())