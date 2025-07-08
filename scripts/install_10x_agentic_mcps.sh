#!/bin/bash
# install_10x_agentic_mcps.sh - Complete automated installation for 10X Agentic MCP Setup

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${PURPLE}========================================${NC}"
    echo -e "${PURPLE}🚀 10X AGENTIC MCP INSTALLATION${NC}"
    echo -e "${PURPLE}========================================${NC}"
    echo ""
}

# Detect Claude Desktop configuration path
detect_claude_config() {
    config_paths=(
        "$HOME/Library/Application Support/Claude/claude_desktop_config.json"  # macOS
        "$HOME/.config/Claude/claude_desktop_config.json"                      # Linux
        "$APPDATA/Claude/claude_desktop_config.json"                           # Windows
    )
    
    for config_path in "${config_paths[@]}"; do
        if [[ -f "$config_path" ]]; then
            echo "$config_path"
            return 0
        fi
    done
    
    return 1
}

# Install MCP servers
install_mcp_servers() {
    print_status "Installing core MCP servers..."
    
    # ChromaDB MCP
    print_status "Installing ChromaDB MCP for vector database..."
    if command -v uvx >/dev/null 2>&1; then
        uvx chroma-mcp --help >/dev/null 2>&1 || uvx install chroma-mcp
        print_success "ChromaDB MCP installed"
    else
        print_error "uvx not found. Please install it first: pip install uv"
        return 1
    fi
    
    # Memory MCP
    print_status "Installing Memory MCP for session persistence..."
    npx -y @modelcontextprotocol/server-memory --help >/dev/null 2>&1
    print_success "Memory MCP installed"
    
    # SQLite MCP
    print_status "Installing SQLite MCP for structured data..."
    uvx mcp-server-sqlite --help >/dev/null 2>&1 || uvx install mcp-server-sqlite
    print_success "SQLite MCP installed"
    
    # Filesystem MCP
    print_status "Installing Filesystem MCP for file operations..."
    npx -y @modelcontextprotocol/server-filesystem --help >/dev/null 2>&1
    print_success "Filesystem MCP installed"
    
    # GitHub MCP
    print_status "Installing GitHub MCP for code research..."
    npx -y @modelcontextprotocol/server-github --help >/dev/null 2>&1
    print_success "GitHub MCP installed"
    
    # WebSearch MCP (Tavily)
    print_status "Installing WebSearch MCP (Tavily) for internet research..."
    uvx tavily-mcp-server --help >/dev/null 2>&1 || uvx install tavily-mcp-server
    print_success "WebSearch MCP installed"
    
    # Context7 MCP
    print_status "Installing Context7 MCP for documentation access..."
    npx -y @upstash/context7-mcp --help >/dev/null 2>&1
    print_success "Context7 MCP installed"
    
    # Enhanced MCPs
    print_status "Installing enhanced intelligence MCPs..."
    
    # Qdrant MCP
    uvx mcp-server-qdrant --help >/dev/null 2>&1 || uvx install mcp-server-qdrant
    print_success "Qdrant MCP installed"
    
    # Meilisearch MCP
    uvx meilisearch-mcp --help >/dev/null 2>&1 || uvx install meilisearch-mcp
    print_success "Meilisearch MCP installed"
    
    # GPT Researcher MCP
    uvx gpt-researcher-mcp --help >/dev/null 2>&1 || uvx install gpt-researcher-mcp
    print_success "GPT Researcher MCP installed"
    
    print_success "All MCP servers installed successfully!"
}

# Configure Claude Desktop
configure_claude_desktop() {
    print_status "Configuring Claude Desktop..."
    
    local claude_config
    if claude_config=$(detect_claude_config); then
        print_success "Found Claude Desktop config: $claude_config"
        CLAUDE_CONFIG="$claude_config"
    else
        print_error "Claude Desktop configuration not found"
        print_warning "Please install Claude Desktop first: https://claude.ai/download"
        return 1
    fi
    
    # Create backup
    local backup_config="${CLAUDE_CONFIG}.backup.$(date +%Y%m%d_%H%M%S)"
    cp "$CLAUDE_CONFIG" "$backup_config"
    print_success "Configuration backed up to: $backup_config"
    
    # Define new MCP configurations
    local project_path="$(pwd)"
    local vector_store_path="$project_path/Knowledge/intelligence/vector_store"
    
    # Create vector store directory if it doesn't exist
    mkdir -p "$vector_store_path"
    
    # Create new MCP configuration
    local new_mcps=$(cat << EOF
{
  "chroma-rag": {
    "command": "uvx",
    "args": [
      "chroma-mcp",
      "--client-type", "persistent",
      "--data-dir", "$vector_store_path"
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
    "args": ["-y", "@modelcontextprotocol/server-filesystem", "$project_path"]
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
    )
    
    # Merge configurations using jq
    if command -v jq >/dev/null 2>&1; then
        jq --argjson new_mcps "$new_mcps" '
          .mcpServers = (.mcpServers // {}) + $new_mcps
        ' "$CLAUDE_CONFIG" > "${CLAUDE_CONFIG}.tmp"
        
        # Validate JSON and update
        if jq empty "${CLAUDE_CONFIG}.tmp" 2>/dev/null; then
            mv "${CLAUDE_CONFIG}.tmp" "$CLAUDE_CONFIG"
            print_success "Configuration updated successfully"
        else
            print_error "Configuration merge failed - restoring backup"
            mv "$backup_config" "$CLAUDE_CONFIG"
            rm -f "${CLAUDE_CONFIG}.tmp"
            return 1
        fi
    else
        print_error "jq not found. Please install jq to merge configurations automatically"
        print_warning "Manual configuration required. See: Knowledge/specifications/mcp_installation_configuration_guide.md"
        return 1
    fi
}

# Setup API keys
setup_api_keys() {
    print_status "Setting up API keys for MCP servers..."
    
    # GitHub Token Setup
    if [[ -z "$GITHUB_PERSONAL_ACCESS_TOKEN" ]]; then
        echo ""
        print_warning "GitHub Personal Access Token required for code research"
        echo "🔗 Create one at: https://github.com/settings/tokens"
        echo "📝 Required permissions: repo, read:org, read:user"
        echo ""
        read -p "Enter your GitHub token (or press Enter to skip): " github_token
        
        if [[ -n "$github_token" ]]; then
            # Update configuration
            jq --arg token "$github_token" '
              .mcpServers.github.env.GITHUB_PERSONAL_ACCESS_TOKEN = $token
            ' "$CLAUDE_CONFIG" > "${CLAUDE_CONFIG}.tmp" && mv "${CLAUDE_CONFIG}.tmp" "$CLAUDE_CONFIG"
            print_success "GitHub token configured"
        else
            print_warning "GitHub token skipped - you can add it later in $CLAUDE_CONFIG"
        fi
    fi
    
    # Tavily API Key Setup
    if [[ -z "$TAVILY_API_KEY" ]]; then
        echo ""
        print_warning "Tavily API Key required for web search functionality"
        echo "🔗 Get one at: https://tavily.com/"
        echo ""
        read -p "Enter your Tavily API key (or press Enter to skip): " tavily_key
        
        if [[ -n "$tavily_key" ]]; then
            # Update configuration
            jq --arg key "$tavily_key" '
              .mcpServers.websearch.env.TAVILY_API_KEY = $key
            ' "$CLAUDE_CONFIG" > "${CLAUDE_CONFIG}.tmp" && mv "${CLAUDE_CONFIG}.tmp" "$CLAUDE_CONFIG"
            print_success "Tavily API key configured"
        else
            print_warning "Tavily API key skipped - you can add it later in $CLAUDE_CONFIG"
        fi
    fi
}

# Test MCP servers
test_mcp_servers() {
    print_status "Testing MCP server installations..."
    
    local mcps_to_test=("chroma-rag" "memory" "sqlite" "filesystem" "websearch" "github" "context7")
    local all_good=true
    
    for mcp in "${mcps_to_test[@]}"; do
        print_status "Testing $mcp..."
        
        # Extract command from configuration
        local command=$(jq -r ".mcpServers.$mcp.command" "$CLAUDE_CONFIG" 2>/dev/null || echo "unknown")
        
        # Test if command exists
        if command -v "$command" >/dev/null 2>&1; then
            print_success "$mcp: Command '$command' available"
        else
            print_error "$mcp: Command '$command' not found"
            all_good=false
        fi
    done
    
    if $all_good; then
        print_success "All MCP servers are properly installed!"
    else
        print_warning "Some MCP servers may need manual installation"
    fi
}

# Create directory structure
setup_directory_structure() {
    print_status "Setting up 10X agentic directory structure..."
    
    local dirs=(
        "Knowledge/intelligence/vector_store"
        "Knowledge/patterns"
        "Knowledge/context"
        "Knowledge/specifications"
        "Instructions/development"
        "Instructions/testing"
        "Instructions/deployment"
        "scripts"
    )
    
    for dir in "${dirs[@]}"; do
        if [[ ! -d "$dir" ]]; then
            mkdir -p "$dir"
            print_success "Created directory: $dir"
        fi
    done
}

# Main installation function
main() {
    print_header
    
    # Check prerequisites
    print_status "Checking prerequisites..."
    
    if ! command -v node >/dev/null 2>&1; then
        print_error "Node.js not found. Please install Node.js first."
        exit 1
    fi
    
    if ! command -v npx >/dev/null 2>&1; then
        print_error "npx not found. Please install Node.js first."
        exit 1
    fi
    
    if ! command -v python3 >/dev/null 2>&1; then
        print_error "Python 3 not found. Please install Python 3 first."
        exit 1
    fi
    
    if ! command -v jq >/dev/null 2>&1; then
        print_warning "jq not found. Installing jq for JSON processing..."
        if command -v apt-get >/dev/null 2>&1; then
            sudo apt-get install -y jq
        elif command -v brew >/dev/null 2>&1; then
            brew install jq
        else
            print_error "Please install jq manually: https://stedolan.github.io/jq/"
            exit 1
        fi
    fi
    
    print_success "Prerequisites check passed"
    
    # Install UV if not present
    if ! command -v uvx >/dev/null 2>&1; then
        print_status "Installing UV for Python package management..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        source ~/.bashrc 2>/dev/null || source ~/.zshrc 2>/dev/null || true
        
        if ! command -v uvx >/dev/null 2>&1; then
            print_error "UV installation failed. Please install manually: https://github.com/astral-sh/uv"
            exit 1
        fi
        print_success "UV installed successfully"
    fi
    
    # Run installation steps
    install_mcp_servers
    setup_directory_structure
    configure_claude_desktop
    setup_api_keys
    test_mcp_servers
    
    # Final instructions
    echo ""
    print_success "🎉 10X Agentic MCP Setup Complete!"
    echo ""
    print_status "📋 Next steps:"
    echo "   1. Restart Claude Desktop to load new MCP configurations"
    echo "   2. Run ./10x-agentic-setup.sh in your project directory"
    echo "   3. Use /analyze_and_execute to start intelligent project orchestration"
    echo "   4. Use /rag_intelligence_orchestrator_10x for vector-enhanced knowledge retrieval"
    echo ""
    print_status "📚 For more information, see:"
    echo "   - Knowledge/specifications/mcp_installation_configuration_guide.md"
    echo "   - README.md for complete command reference"
    echo ""
    print_status "🔧 Configuration file location: $CLAUDE_CONFIG"
    echo ""
}

# Run main function
main "$@"