# Contributing to AI Resume Classifier

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing.

## Code of Conduct

Be respectful, inclusive, and professional in all interactions.

## Getting Started

### 1. Fork and Clone
```bash
git clone https://github.com/frankTheCodeBoy/ai_doc_classifier.git
cd ai_doc_classifier
```

### 2. Create Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 3. Set Up Development Environment
```bash
docker compose up -d
docker compose exec resume-prod bash
```

### 4. Make Changes
- Follow PEP 8 style guide
- Write clear commit messages
- Add tests for new features

### 5. Run Tests
```bash
docker compose exec resume-prod pytest -v
```

### 6. Push and Open PR
```bash
git push origin feature/your-feature-name
```

## Development Workflow

### Adding a Feature
1. Create issue describing feature
2. Implement feature with tests
3. Ensure all tests pass
4. Open PR with clear description

### Bug Fixes
1. Create issue with bug description
2. Fix the bug
3. Add regression test
4. Open PR

### Documentation
1. Update README.md if needed
2. Add docstrings to functions
3. Update docs/ folder if applicable

## Code Standards

### Python
- Use `black` for formatting
- Type hints for functions
- Docstrings for classes/functions
- Max line length: 100 characters

Example:
```python
def classify_resume(text: str) -> str:
    """
    Classify resume text into category.
    
    Args:
        text: Resume text to classify
        
    Returns:
        Category name (tech, finance, healthcare, education)
    """
    # implementation
    pass
```

### Tests
- Minimum 80% coverage
- Test both success and error cases
- Use descriptive test names

```python
def test_classify_endpoint_returns_category():
    """Test that classify endpoint returns valid category."""
    # test code
```

## Pull Request Process

1. **Title**: Clear, descriptive title
2. **Description**: What changes, why, and how to test
3. **Tests**: All tests passing
4. **Documentation**: Updated if needed
5. **Commits**: Clean, logical commit history

### PR Template
```markdown
## Description
Brief description of changes

## Changes
- Change 1
- Change 2

## Testing
- [ ] Tests added/updated
- [ ] All tests passing
- [ ] Manual testing done

## Related Issues
Closes #(issue number)
```

## Commit Guidelines

**Format**: `type: description`

**Types**:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `style:` Formatting
- `refactor:` Code restructuring
- `test:` Tests
- `chore:` Maintenance

**Examples**:
```bash
git commit -m "feat: add resume scoring algorithm"
git commit -m "fix: correct CORS allowed origins"
git commit -m "docs: update deployment guide"
```

## Testing Requirements

### Run Tests Locally
```bash
docker compose exec resume-prod pytest -v --cov
```

### Test Coverage
- `api/` endpoints: 100%
- `utils/` functions: 95%+
- `ui/` components: 80%+

### GitHub Actions
- Tests run automatically on push/PR
- Must pass before merge
- Check status in PR

## Documentation

### README.md
- Keep up-to-date with features
- Include examples
- Add new deployment methods

### Docstrings
- All public functions
- All classes
- Complex logic

### docs/ Folder
- Deployment guides
- Architecture diagrams
- Troubleshooting

## Reporting Issues

### Bug Report
```markdown
## Description
What is the bug?

## Steps to Reproduce
1. Step 1
2. Step 2

## Expected vs Actual
- Expected: X
- Actual: Y

## Environment
- Python: 3.11
- Docker: version X
```

### Feature Request
```markdown
## Description
What should be added?

## Use Case
Why is this needed?

## Solution
How should it work?
```

## Getting Help

- 📖 Check [README.md](README.md)
- 📚 Review [docs/](docs/)
- 💬 Open a discussion
- 🐛 File an issue

## Recognition

Contributors will be recognized in:
- README.md acknowledgments
- Release notes
- Project contributors list

## Questions?

Feel free to:
- Open an issue
- Start a discussion
- Email: (contact if available)

Thank you for contributing! 🙏
