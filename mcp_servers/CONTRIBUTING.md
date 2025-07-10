# Contributing to ML-Enhanced MCP Servers

Thank you for your interest in contributing to the ML-Enhanced MCP Servers project! This document provides guidelines and instructions for contributing.

## 🎯 Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct:
- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on constructive criticism
- Respect differing viewpoints and experiences

## 🚀 Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/ml-enhanced-mcp-servers.git
   cd ml-enhanced-mcp-servers
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/original-owner/ml-enhanced-mcp-servers.git
   ```
4. **Create a virtual environment** and install dependencies:
   ```bash
   uv venv
   source .venv/bin/activate
   uv pip install -r requirements.txt
   uv pip install -r requirements-dev.txt
   ```

## 📝 Development Process

### 1. Create a Feature Branch
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 2. Make Your Changes
- Write clean, documented code
- Follow the existing code style
- Add tests for new functionality
- Update documentation as needed

### 3. Code Style
We use automated tools to maintain code quality:
```bash
# Format code
black .
ruff format .

# Check linting
ruff check .
mypy .

# Run all checks
make lint  # if Makefile is available
```

### 4. Testing
```bash
# Run all tests
pytest tests/ -v

# Run specific tests
pytest tests/unit/test_your_feature.py -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

### 5. Commit Your Changes
```bash
git add .
git commit -m "feat: add amazing new feature

- Detailed description of what changed
- Why it was changed
- Any breaking changes or migrations needed"
```

Follow [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` new feature
- `fix:` bug fix
- `docs:` documentation changes
- `style:` formatting, missing semi-colons, etc.
- `refactor:` code change that neither fixes a bug nor adds a feature
- `perf:` performance improvements
- `test:` adding missing tests
- `chore:` updating build tasks, package manager configs, etc.

### 6. Push and Create Pull Request
```bash
git push origin feature/your-feature-name
```
Then create a Pull Request on GitHub.

## 🏗️ Project Structure

```
ml-enhanced-mcp-servers/
├── ml_code_intelligence/      # Each MCP server
│   ├── src/                  # Source code
│   │   ├── server.py        # Main server entry
│   │   ├── tools/           # MCP tools
│   │   ├── models/          # ML models
│   │   └── utils/           # Utilities
│   ├── tests/               # Tests
│   ├── docs/                # Documentation
│   └── requirements.txt     # Dependencies
├── shared/                   # Shared code
├── tests/                   # Integration tests
└── docs/                    # Project documentation
```

## 📋 Pull Request Guidelines

### PR Title
Use conventional commit format: `type(scope): description`

### PR Description Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] No sensitive data exposed
```

## 🧪 Testing Guidelines

### Unit Tests
- Test individual functions and classes
- Mock external dependencies
- Aim for >80% coverage

### Integration Tests
- Test MCP server endpoints
- Test ML model integration
- Verify tool functionality

### Example Test
```python
import pytest
from ml_code_intelligence.tools import analyze_code

@pytest.mark.asyncio
async def test_analyze_code():
    result = await analyze_code("def hello(): pass")
    assert result.quality_score > 0
    assert "function" in result.analysis
```

## 📚 Documentation

### Code Documentation
- Add docstrings to all public functions/classes
- Use type hints
- Include examples in docstrings

### Example Docstring
```python
def analyze_code(code: str, language: str = "python") -> CodeAnalysis:
    """
    Analyze code quality using ML models.
    
    Args:
        code: Source code to analyze
        language: Programming language (default: "python")
        
    Returns:
        CodeAnalysis object with quality metrics
        
    Example:
        >>> result = analyze_code("def hello(): pass")
        >>> print(result.quality_score)
        0.85
    """
```

## 🐛 Reporting Issues

### Bug Reports
Include:
- Python version
- OS and version
- Steps to reproduce
- Expected vs actual behavior
- Error messages/logs

### Feature Requests
Include:
- Use case description
- Proposed solution
- Alternative solutions considered
- Impact on existing functionality

## 🔍 Code Review Process

All PRs require:
1. Passing CI/CD checks
2. Code review approval
3. No merge conflicts
4. Up-to-date with main branch

Reviewers will check:
- Code quality and style
- Test coverage
- Documentation
- Security considerations
- Performance impact

## 🎁 Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Given credit in commit messages

## 💡 Tips for Contributors

1. **Start small**: Pick beginner-friendly issues
2. **Ask questions**: Use discussions or issues
3. **Read existing code**: Understand patterns and conventions
4. **Test thoroughly**: Including edge cases
5. **Document clearly**: Help future contributors

## 📞 Getting Help

- **Discord**: [Join our server](https://discord.gg/example)
- **Discussions**: Use GitHub Discussions
- **Issues**: For bugs and feature requests
- **Email**: maintainers@example.com

## 🙏 Thank You!

Your contributions make this project better for everyone. Whether it's code, documentation, bug reports, or feature requests - every contribution matters!

---

**Happy coding!** 🚀