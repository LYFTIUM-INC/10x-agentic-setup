# 🚀 10X Agentic MCP Installation & Configuration Guide
*Comprehensive Setup for All Required MCP Servers with Global Configuration Detection*

**Created**: $(date +%Y-%m-%d_%H-%M-%S)
**Status**: Implementation Ready
**Priority**: Critical

## 🎯 **OVERVIEW**

This guide provides comprehensive instructions for installing and configuring all MCP servers required for the 10X agentic setup, including automatic detection of existing configurations and seamless integration.

## 🔍 **PHASE 1: GLOBAL MCP CONFIGURATION DETECTION**

### **1.1 Claude Desktop Configuration Check**
```bash
# Check if Claude Desktop is configured
config_paths=(
    "$HOME/Library/Application Support/Claude/claude_desktop_config.json"  # macOS
    "$HOME/.config/Claude/claude_desktop_config.json"                      # Linux
    "$APPDATA/Claude/claude_desktop_config.json"                           # Windows
)

for config_path in "${config_paths[@]}"; do
    if [[ -f "$config_path" ]]; then
        echo "✅ Found Claude Desktop config: $config_path"
        CLAUDE_CONFIG="$config_path"
        break
    fi
done

if [[ -z "$CLAUDE_CONFIG" ]]; then
    echo "❌ Claude Desktop configuration not found"
    echo "📋 Please install Claude Desktop first: https://claude.ai/download"
    exit 1
fi
```

### **1.2 Existing MCP Server Detection**
```bash
# Parse existing configuration and detect installed MCPs
if [[ -f "$CLAUDE_CONFIG" ]]; then
    echo "🔍 Scanning existing MCP configuration..."
    
    # Extract MCP server names
    existing_mcps=$(jq -r '.mcpServers | keys[]' "$CLAUDE_CONFIG" 2>/dev/null || echo "[]")
    echo "📊 Found existing MCPs: $existing_mcps"
    
    # Check for our required MCPs
    required_mcps=("chroma-rag" "websearch" "github" "memory" "sqlite" "filesystem" "context7")
    missing_mcps=()
    
    for mcp in "${required_mcps[@]}"; do
        if ! echo "$existing_mcps" | grep -q "$mcp"; then
            missing_mcps+=("$mcp")
        fi
    done
    
    echo "⚠️  Missing MCPs: ${missing_mcps[*]}"
fi
```

## 🛠️ **PHASE 2: REQUIRED MCP SERVERS INSTALLATION**

### **2.1 Core Intelligence MCPs**

#### **ChromaDB MCP (Vector Database & RAG)**
```bash
# Installation
uvx chroma-mcp

# Verification
uvx chroma-mcp --help

# Configuration
{
  "chroma-rag": {
    "command": "uvx",
    "args": [
      "chroma-mcp",
      "--client-type", "persistent",
      "--data-dir", "/your/project/path/Knowledge/intelligence/vector_store"
    ]
  }
}
```

#### **Memory MCP (Session Persistence)**
```bash
# Installation
npx -y @modelcontextprotocol/server-memory

# Configuration
{
  "memory": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-memory"]
  }
}
```

#### **SQLite MCP (Structured Data)**
```bash
# Installation
uvx mcp-server-sqlite

# Configuration
{
  "sqlite": {
    "command": "uvx",
    "args": ["mcp-server-sqlite", "--db-path", "./analytics.db"]
  }
}
```

### **2.2 Research & Intelligence MCPs**

#### **WebSearch MCP (Internet Research)**
```bash
# Option 1: Tavily Search (Recommended)
uvx tavily-mcp-server
# Requires: TAVILY_API_KEY environment variable

# Option 2: Brave Search
npx -y brave-search-mcp
# Requires: BRAVE_API_KEY environment variable

# Configuration
{
  "websearch": {
    "command": "uvx",
    "args": ["tavily-mcp-server"],
    "env": {
      "TAVILY_API_KEY": "your_api_key_here"
    }
  }
}
```

#### **GitHub MCP (Code Research)**
```bash
# Installation
npx -y @modelcontextprotocol/server-github

# Configuration
{
  "github": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-github"],
    "env": {
      "GITHUB_PERSONAL_ACCESS_TOKEN": "your_token_here"
    }
  }
}
```

#### **Context7 MCP (Documentation Access)**
```bash
# Installation
npx -y @upstash/context7-mcp

# Configuration
{
  "context7": {
    "command": "npx",
    "args": ["-y", "@upstash/context7-mcp"]
  }
}
```

### **2.3 Enhanced Intelligence MCPs**

#### **Qdrant MCP (Advanced Vector Search)**
```bash
# Installation
uvx mcp-server-qdrant

# Configuration
{
  "qdrant": {
    "command": "uvx",
    "args": ["mcp-server-qdrant"]
  }
}
```

#### **Meilisearch MCP (Full-Text Search)**
```bash
# Installation
uvx meilisearch-mcp

# Configuration
{
  "meilisearch": {
    "command": "uvx",
    "args": ["meilisearch-mcp"]
  }
}
```

#### **GPT Researcher MCP (Deep Research)**
```bash
# Installation
uvx gpt-researcher-mcp

# Configuration
{
  "gpt-researcher": {
    "command": "uvx",
    "args": ["gpt-researcher-mcp"]
  }
}
```

### **2.4 Filesystem MCP (File Operations)**
```bash
# Installation
npx -y @modelcontextprotocol/server-filesystem

# Configuration
{
  "filesystem": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-filesystem", "/your/projects/path"]
  }
}
```

## 🔧 **PHASE 3: AUTOMATIC CONFIGURATION MERGER**

### **3.1 Smart Configuration Update Script**
```bash
#!/bin/bash
# merge_mcp_config.sh - Intelligent MCP configuration merger

CLAUDE_CONFIG="/home/dell/.config/Claude/claude_desktop_config.json"
BACKUP_CONFIG="${CLAUDE_CONFIG}.backup.$(date +%Y%m%d_%H%M%S)"

# Create backup
cp "$CLAUDE_CONFIG" "$BACKUP_CONFIG"
echo "📋 Configuration backed up to: $BACKUP_CONFIG"

# Define new MCP configurations
read -r -d '' NEW_MCPS << 'EOF'
{
  "chroma-rag": {
    "command": "uvx",
    "args": [
      "chroma-mcp",
      "--client-type", "persistent",
      "--data-dir", "/home/dell/coding/bash/10x-agentic-setup/Knowledge/intelligence/vector_store"
    ]
  },
  "websearch": {
    "command": "uvx",
    "args": ["tavily-mcp-server"],
    "env": {
      "TAVILY_API_KEY": "your_api_key_here"
    }
  },
  "github": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-github"],
    "env": {
      "GITHUB_PERSONAL_ACCESS_TOKEN": "your_token_here"
    }
  },
  "memory": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-memory"]
  },
  "sqlite": {
    "command": "uvx",
    "args": ["mcp-server-sqlite", "--db-path", "./analytics.db"]
  },
  "filesystem": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home/dell/coding"]
  },
  "context7": {
    "command": "npx",
    "args": ["-y", "@upstash/context7-mcp"]
  },
  "qdrant": {
    "command": "uvx",
    "args": ["mcp-server-qdrant"]
  },
  "meilisearch": {
    "command": "uvx",
    "args": ["meilisearch-mcp"]
  },
  "gpt-researcher": {
    "command": "uvx",
    "args": ["gpt-researcher-mcp"]
  }
}
EOF

# Merge configurations intelligently
jq --argjson new_mcps "$NEW_MCPS" '
  .mcpServers = (.mcpServers // {}) + $new_mcps
' "$CLAUDE_CONFIG" > "${CLAUDE_CONFIG}.tmp"

# Validate JSON and update
if jq empty "${CLAUDE_CONFIG}.tmp" 2>/dev/null; then
    mv "${CLAUDE_CONFIG}.tmp" "$CLAUDE_CONFIG"
    echo "✅ Configuration updated successfully"
else
    echo "❌ Configuration merge failed - restoring backup"
    mv "$BACKUP_CONFIG" "$CLAUDE_CONFIG"
    rm -f "${CLAUDE_CONFIG}.tmp"
    exit 1
fi
```

### **3.2 API Keys Configuration Helper**
```bash
#!/bin/bash
# setup_api_keys.sh - Interactive API key setup

echo "🔑 Setting up API keys for MCP servers..."

# GitHub Token Setup
if [[ -z "$GITHUB_PERSONAL_ACCESS_TOKEN" ]]; then
    echo "📋 GitHub Personal Access Token required"
    echo "🔗 Create one at: https://github.com/settings/tokens"
    echo "📝 Required permissions: repo, read:org, read:user"
    read -p "Enter your GitHub token: " github_token
    
    # Update configuration
    jq --arg token "$github_token" '
      .mcpServers.github.env.GITHUB_PERSONAL_ACCESS_TOKEN = $token
    ' "$CLAUDE_CONFIG" > "${CLAUDE_CONFIG}.tmp" && mv "${CLAUDE_CONFIG}.tmp" "$CLAUDE_CONFIG"
fi

# Tavily API Key Setup
if [[ -z "$TAVILY_API_KEY" ]]; then
    echo "📋 Tavily API Key required for web search"
    echo "🔗 Get one at: https://tavily.com/"
    read -p "Enter your Tavily API key: " tavily_key
    
    # Update configuration
    jq --arg key "$tavily_key" '
      .mcpServers.websearch.env.TAVILY_API_KEY = $key
    ' "$CLAUDE_CONFIG" > "${CLAUDE_CONFIG}.tmp" && mv "${CLAUDE_CONFIG}.tmp" "$CLAUDE_CONFIG"
fi

echo "✅ API keys configured successfully"
```

## 🚀 **PHASE 4: VERIFICATION & TESTING**

### **4.1 MCP Server Health Check**
```bash
#!/bin/bash
# test_mcp_servers.sh - Comprehensive MCP server testing

echo "🔍 Testing MCP server connectivity..."

# Test each MCP server
mcps_to_test=("chroma-rag" "memory" "sqlite" "filesystem" "websearch" "github" "context7")

for mcp in "${mcps_to_test[@]}"; do
    echo "Testing $mcp..."
    
    # Extract command from configuration
    command=$(jq -r ".mcpServers.$mcp.command" "$CLAUDE_CONFIG")
    args=$(jq -r ".mcpServers.$mcp.args[]" "$CLAUDE_CONFIG" | tr '\n' ' ')
    
    # Test if command exists
    if command -v "$command" >/dev/null 2>&1; then
        echo "✅ $mcp: Command '$command' available"
    else
        echo "❌ $mcp: Command '$command' not found"
        echo "📋 Install with: npx -y $command (or uvx $command)"
    fi
done
```

### **4.2 Integration Testing**
```bash
# Test 10X agentic setup integration
echo "🧪 Testing 10X agentic setup integration..."

# Verify Knowledge directory structure
knowledge_dirs=(
    "Knowledge/intelligence/vector_store"
    "Knowledge/patterns"
    "Knowledge/context"
    "Instructions"
)

for dir in "${knowledge_dirs[@]}"; do
    if [[ -d "$dir" ]]; then
        echo "✅ Directory exists: $dir"
    else
        echo "📁 Creating directory: $dir"
        mkdir -p "$dir"
    fi
done

# Test ChromaDB vector store
if [[ -d "Knowledge/intelligence/vector_store" ]]; then
    echo "✅ ChromaDB vector store directory ready"
else
    echo "📁 Creating ChromaDB vector store directory"
    mkdir -p "Knowledge/intelligence/vector_store"
fi

echo "🎉 10X agentic setup ready for use!"
```

## 📋 **PHASE 5: COMPLETE INSTALLATION AUTOMATION**

### **5.1 One-Click Installation Script**
```bash
#!/bin/bash
# install_10x_agentic_mcps.sh - Complete automated installation

set -e

echo "🚀 Installing 10X Agentic MCP Setup..."

# Install all required MCPs
echo "📦 Installing MCP servers..."

# Core MCPs
uvx chroma-mcp
npx -y @modelcontextprotocol/server-memory
uvx mcp-server-sqlite
npx -y @modelcontextprotocol/server-filesystem
npx -y @modelcontextprotocol/server-github

# Research MCPs
uvx tavily-mcp-server
npx -y @upstash/context7-mcp

# Enhanced MCPs
uvx mcp-server-qdrant
uvx meilisearch-mcp
uvx gpt-researcher-mcp

echo "✅ All MCP servers installed"

# Configure Claude Desktop
echo "🔧 Configuring Claude Desktop..."
bash merge_mcp_config.sh

# Set up API keys
echo "🔑 Setting up API keys..."
bash setup_api_keys.sh

# Test installation
echo "🧪 Testing installation..."
bash test_mcp_servers.sh

echo "🎉 10X Agentic MCP Setup Complete!"
echo "📋 Next steps:"
echo "   1. Restart Claude Desktop"
echo "   2. Run ./10x-agentic-setup.sh in your project"
echo "   3. Use /analyze_and_execute to start"
```

## 🎯 **USAGE INSTRUCTIONS**

### **For New Users**
1. **Download this guide** to your project directory
2. **Run the automated installer**: `bash install_10x_agentic_mcps.sh`
3. **Follow the prompts** for API key configuration
4. **Restart Claude Desktop** to load new configurations
5. **Run the 10X setup**: `./10x-agentic-setup.sh`

### **For Existing MCP Users**
1. **Backup your current configuration** (automatic backup created)
2. **Run the configuration merger**: `bash merge_mcp_config.sh`
3. **Update API keys if needed**: `bash setup_api_keys.sh`
4. **Test the integration**: `bash test_mcp_servers.sh`

### **Manual Installation**
If you prefer manual installation, follow the individual MCP installation instructions in Phase 2, then manually merge the configurations using the JSON examples provided.

This comprehensive guide ensures seamless integration of all required MCP servers for the 10X agentic setup, with automatic detection of existing configurations and intelligent merging capabilities.

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>