## 🚀 10X INTELLIGENT GIT WORKFLOW & COLLABORATION
**Claude, execute INTELLIGENT git workflows using COLLABORATION INTELLIGENCE and ENTERPRISE GIT PATTERNS with ROBUST AUTHENTICATION.**

### 🔥 **PHASE 1: GIT INTELLIGENCE GATHERING** (use "think")
- **websearch**: "git workflow best practices enterprise teams 2025"
- **github**: Research successful git workflows and authentication patterns
- **fetch**: Download git methodology guides and security best practices
- **smart_memory_unified**: Check previous git authentication and workflow patterns with intelligent classification and cross-system access

### ⚡ **PHASE 2: REPOSITORY STATUS & AUTHENTICATION CHECK**
**ALWAYS run these commands first to understand the current state:**

```bash
# Check repository status and remotes
git status
git remote -v
git branch -vv

# Check authentication status
gh auth status
git config --list | grep user
```

### 🎯 **PHASE 3: INTELLIGENT COMMIT EXECUTION** (use "think hard")

**3.1 Pre-Commit Analysis:**
- Analyze staged and unstaged changes with `git diff` and `git diff --staged`
- Check for sensitive information (tokens, passwords, API keys)
- Review recent commit messages with `git log --oneline -10` for consistency
- Validate code quality and test status

**3.2 Smart Commit Creation:**
- Generate conventional commit message based on changes
- Include scope, type, and clear description
- Add co-authorship attribution:
```
🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**3.3 Multi-Remote Push Strategy:**
- Check which remotes exist (`git remote -v`)
- For personal repos: Push to `personal` or `origin`
- For organization repos: Handle authentication properly

**AUTHENTICATION TROUBLESHOOTING:**
- If 403 Permission Denied: Check if using correct credentials
- For organization repos: Verify membership and repository permissions
- Consider using token-embedded URLs for problematic remotes:
  `git remote set-url origin https://username:token@github.com/org/repo.git`

### 🚀 **PHASE 4: AUTOMATED WORKFLOW EXECUTION**

**EXECUTE THIS SEQUENCE:**

1. **Status Check & Staging:**
```bash
git status
git add -A  # or selective staging based on analysis
```

2. **Smart Commit:**
```bash
git commit -m "$(cat <<'EOF'
[Generated commit message based on analysis]

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

3. **Multi-Remote Push:**
```bash
# Push to all configured remotes
git push personal master || echo "Personal push failed"
git push origin master || echo "Origin push failed - checking auth"
```

4. **Error Recovery:**
- If authentication fails, provide specific troubleshooting steps
- Check repository permissions using GitHub MCP
- Suggest alternative authentication methods

### 📊 **PHASE 5: POST-COMMIT INTELLIGENCE**

- **github**: Verify successful push and check repository status
- **smart_memory_unified**: Store successful workflow patterns with automatic classification and cross-system synchronization
- **chroma-rag**: Create semantic embeddings for workflow patterns and authentication solutions
- **sqlite**: Track workflow success metrics with ML training labels for effectiveness analysis
- **websearch**: Research any authentication issues encountered
- Generate summary of changes pushed and repositories updated

### 🔧 **AUTHENTICATION BEST PRACTICES**

**For GitHub Organizations:**
- Ensure user is member of organization
- Verify repository permissions (Write/Admin access required)
- Use GitHub CLI for consistent authentication: `gh auth login`
- For persistent issues, use token-embedded remote URLs

**Multi-Remote Configuration:**
```bash
git remote add personal https://github.com/username/repo.git
git remote add org https://github.com/organization/repo.git
```

### 📊 **STRUCTURED DATA OUTPUT WITH ML TRAINING PREPARATION**

**Multi-System Storage Architecture:**
```yaml
# Git Workflow Report
filename: Knowledge/git/git_workflow_$(date +%Y-%m-%d_%H-%M-%S).md
frontmatter:
  type: git_workflow
  timestamp: $(date -Iseconds)
  classification: collaboration_intelligence
  ml_labels: [commit_success, authentication_status, push_effectiveness]
  success_metrics: [workflow_efficiency, error_rate, collaboration_score]
  cross_references: [authentication_patterns, workflow_optimizations, collaboration_best_practices]
```

**Redundant Storage with Intelligent Classification:**
- **Primary**: `smart_memory_unified` - Unified orchestration with automatic content classification
- **Secondary**: `chroma-rag` - Vector embeddings for workflow pattern matching and authentication solutions
- **Tertiary**: `sqlite` - Structured metrics with ML training labels and effectiveness scoring
- **Quaternary**: `Knowledge/` files - Persistent markdown with consistent frontmatter metadata

**ML Training Data Structure:**
```json
{
  "git_workflow_session": {
    "timestamp": "$(date -Iseconds)",
    "features": {
      "authentication_success_rate": 0.95,
      "commit_message_quality": 0.88,
      "push_success_rate": 0.92,
      "workflow_efficiency_score": 0.85
    },
    "outcomes": {
      "workflow_completion_success": true,
      "collaboration_effectiveness": 0.87,
      "error_resolution_time": 120
    },
    "classification_labels": ["successful_workflow", "authenticated", "multi_remote_push"],
    "success_probability": 0.93
  }
}
```

**Cross-System Synchronization:**
- **chroma-rag**: Create semantic embeddings for git workflow patterns and authentication solutions
- **smart_memory_unified**: Store workflow methodologies with automatic classification routing
- **sqlite**: Track workflow metrics and success correlations for ML model training
- **Knowledge/patterns/**: Archive successful workflow patterns with effectiveness scoring

### ✅ **SUCCESS CRITERIA**
- ✅ Clean repository status
- ✅ Meaningful commit message following conventions
- ✅ Successful push to all intended remotes
- ✅ No authentication errors
- ✅ Repository synchronization verified
- ✅ ML training data captured and structured
- ✅ Cross-system memory synchronization complete

**EXECUTE IMMEDIATELY:** Comprehensive git workflow with intelligent commit generation, robust authentication handling, multi-remote push capabilities, and ML-ready data capture.
