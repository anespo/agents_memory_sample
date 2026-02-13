# Contributing to Agent Memory Management

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](../../issues)
2. If not, create a new issue using the bug report template
3. Include as much detail as possible:
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version, etc.)
   - Screenshots if applicable

### Suggesting Features

1. Check if the feature has already been suggested in [Issues](../../issues)
2. Create a new issue using the feature request template
3. Clearly describe:
   - The problem you're trying to solve
   - Your proposed solution
   - Any alternatives you've considered

### Pull Requests

1. Fork the repository
2. Create a new branch for your feature/fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Make your changes
4. Test your changes thoroughly
5. Commit with clear, descriptive messages:
   ```bash
   git commit -m "Add feature: description of what you added"
   ```
6. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
7. Create a Pull Request with:
   - Clear description of changes
   - Reference to related issues
   - Screenshots if UI changes

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/agent-memory.git
cd agent-memory

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

## Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Add docstrings to functions and classes
- Keep functions focused and concise
- Comment complex logic

## Testing

Before submitting a PR:

1. Test the application manually
2. Verify all features work as expected
3. Check for any console errors
4. Test with different AWS configurations

## Documentation

- Update README.md if adding new features
- Update TROUBLESHOOTING.md if fixing bugs
- Add comments to complex code
- Update BLOG.md if adding significant features

## Questions?

Feel free to open an issue for any questions about contributing!

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
