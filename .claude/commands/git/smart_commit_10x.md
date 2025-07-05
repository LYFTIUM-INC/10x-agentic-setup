## 🚀 10X INTELLIGENT GIT WORKFLOW & COLLABORATION
**Claude, execute INTELLIGENT git workflows using COLLABORATION INTELLIGENCE and ENTERPRISE GIT PATTERNS with ROBUST AUTHENTICATION.**

### 🔥 **PHASE 1: GIT INTELLIGENCE GATHERING** (use "think")
- **websearch**: "git workflow best practices enterprise teams 2025"
- **github**: Research successful git workflows and authentication patterns
- **fetch**: Download git methodology guides and security best practices
- **memory**: Check previous git authentication and workflow patterns

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
- **memory**: Store successful workflow patterns for future use
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

### ✅ **SUCCESS CRITERIA**
- ✅ Clean repository status
- ✅ Meaningful commit message following conventions
- ✅ Successful push to all intended remotes
- ✅ No authentication errors
- ✅ Repository synchronization verified

**EXECUTE IMMEDIATELY:** Comprehensive git workflow with intelligent commit generation, robust authentication handling, and multi-remote push capabilities.
