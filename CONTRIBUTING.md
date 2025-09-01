# Contributing to Reddit Data Engine 🤝

Thank you for your interest in contributing! This project thrives on community contributions and we welcome developers of all skill levels.

## 🚀 Quick Start for Contributors

### **1. Development Setup**
```bash
# Fork and clone
git clone https://github.com/yourusername/reddit-data.git
cd reddit-data

# Install dependencies
pip install -r requirements.txt
pip install -r gui/requirements.txt

# Setup Reddit API credentials  
python setup_reddit_api.py

# Verify everything works
python full_test.py
```

### **2. Development Workflow**
```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and test
python main.py test
python gui/test_gui.py

# Run full test suite
python full_test.py

# Commit and push
git add .
git commit -m "Add: your feature description"
git push origin feature/your-feature-name

# Create pull request on GitHub
```

## 🎯 Contribution Areas

### **🐛 Bug Fixes** (Great for beginners)
- Fix authentication issues
- Resolve GUI display problems
- Handle API rate limiting better
- Improve error messages and logging

### **✨ New Features** (Intermediate)
- Additional subreddit categories
- New export formats (CSV, Excel)
- Advanced filtering options
- Custom notification systems
- Mobile app development

### **🎨 UI/UX Improvements** (Design-focused)
- GUI theme customization
- Web dashboard responsive design
- Chart improvements and new visualizations
- Accessibility enhancements
- Mobile-friendly interfaces

### **📚 Documentation** (All levels)
- API documentation
- Tutorial improvements
- Code comments and docstrings
- Example projects and integrations
- Video tutorials and guides

### **🧪 Testing & Quality** (QA-focused)
- Unit test coverage
- Integration testing
- Performance benchmarking
- Security audits
- Cross-platform testing

### **⚡ Performance & Architecture** (Advanced)
- Database integration
- Caching mechanisms
- Concurrent processing improvements
- Memory optimization
- API scalability

## 📋 Development Guidelines

### **Code Style**
- **Python**: Follow PEP 8 style guide
- **Line length**: 88 characters (Black formatter)
- **Imports**: Use absolute imports, group by stdlib/third-party/local
- **Documentation**: Use Google-style docstrings
- **Type hints**: Use for all public functions

### **Git Conventions**
```bash
# Commit message format
type: brief description (50 chars max)

Extended description if needed (wrap at 72 chars)

# Types:
Add:    New feature or functionality
Fix:    Bug fix
Update: Existing feature improvement  
Remove: Delete feature/code
Docs:   Documentation changes
Test:   Test-related changes
Style:  Code style/formatting
Refactor: Code restructuring
```

### **Testing Requirements**
- **Unit tests** for new functions
- **Integration tests** for API changes
- **GUI tests** for interface modifications
- **Performance tests** for optimization changes
- All tests must pass before PR merge

### **Documentation Requirements**
- **Docstrings** for all public functions
- **README updates** for new features
- **API documentation** for new endpoints
- **Tutorial updates** for user-facing changes

## 🏗️ Project Architecture

### **Core Components**
```
reddit-data/
├── main.py                 # CLI entry point
├── reddit_client.py        # Reddit API wrapper
├── data_processor.py       # Data analysis logic
├── api_interface.py        # Export/integration API
├── monitor.py              # Real-time monitoring
├── config.py               # Configuration management
├── gui/                    # GUI applications
│   ├── tkinter_app/        # Desktop GUI
│   └── web_app/            # Web dashboard
├── tests/                  # Test suite
├── docs/                   # Documentation
└── examples/               # Usage examples
```

### **Data Flow**
1. **Reddit Client** → Fetches posts from Reddit API
2. **Data Processor** → Analyzes and filters content
3. **Monitor** → Orchestrates real-time collection
4. **API Interface** → Exports processed data
5. **GUI Applications** → Display data to users

## 🧪 Testing Guide

### **Running Tests**
```bash
# Full system test
python full_test.py

# Unit tests
python -m pytest tests/ -v

# GUI tests
python gui/test_gui.py

# Performance tests
python -m pytest tests/test_performance.py

# Coverage report
python -m pytest --cov=. tests/
```

### **Writing Tests**
```python
# Example unit test
import pytest
from reddit_client import RedditClient

class TestRedditClient:
    def test_client_initialization(self):
        client = RedditClient()
        assert client is not None
        
    def test_post_fetching(self):
        client = RedditClient()
        posts = client.get_hot_posts('python', limit=5)
        assert len(posts) <= 5
        assert all(hasattr(p, 'title') for p in posts)
```

## 🐛 Bug Report Guidelines

### **Before Reporting**
- Search existing issues
- Test with latest version
- Reproduce the bug consistently
- Check if it's a configuration issue

### **Bug Report Template**
```markdown
**Describe the Bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. See error

**Expected Behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment:**
- OS: [e.g. macOS 12.0]
- Python: [e.g. 3.9.0]
- Reddit Data Engine: [e.g. v1.2.0]

**Additional Context**
Any other context about the problem.
```

## ✨ Feature Request Guidelines

### **Feature Request Template**
```markdown
**Is your feature related to a problem?**
A clear description of what the problem is.

**Describe the solution you'd like**
A clear description of what you want to happen.

**Describe alternatives you've considered**
Alternative solutions or features you've considered.

**Additional context**
Any other context, mockups, or examples.

**Implementation ideas**
If you have ideas on how to implement this.
```

## 🏆 Recognition

### **Contributors**
All contributors are recognized in:
- **README.md** contributors section
- **CONTRIBUTORS.md** detailed list
- **GitHub contributors** page
- **Release notes** for significant contributions

### **Special Recognition**
- **First-time contributors** get welcome badges
- **Regular contributors** get maintainer status
- **Major contributors** get co-author credit
- **Bug hunters** get special mentions

## 📞 Getting Help

### **Communication Channels**
- **GitHub Discussions**: Best for questions and ideas
- **GitHub Issues**: For bugs and feature requests
- **Discord**: [Coming soon] Real-time chat
- **Email**: For security issues only

### **Mentorship Program**
New contributors can request mentorship:
- **Pair programming** sessions
- **Code review** guidance
- **Architecture** discussions
- **Career advice** for open source

## 🔒 Security

### **Reporting Security Issues**
- **DO NOT** create public issues for security bugs
- Email security issues to: [security@example.com]
- Include detailed steps to reproduce
- Allow 48 hours for initial response

### **Security Considerations**
- Never commit API keys or secrets
- Validate all user inputs
- Use HTTPS for all external requests
- Follow OWASP guidelines for web components

## 📜 Code of Conduct

### **Our Pledge**
We are committed to making participation in our project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

### **Expected Behavior**
- Use welcoming and inclusive language
- Be respectful of differing viewpoints
- Gracefully accept constructive criticism  
- Focus on what is best for the community
- Show empathy towards other community members

### **Unacceptable Behavior**
- Trolling, insulting, or derogatory comments
- Personal or political attacks
- Public or private harassment
- Publishing others' private information
- Other conduct inappropriate in a professional setting

## 🎉 Release Process

### **Version Numbering**
We use Semantic Versioning (SemVer):
- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### **Release Checklist**
- [ ] All tests pass
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version bumped in all relevant files
- [ ] GitHub release created
- [ ] PyPI package updated (if applicable)

## 🙏 Thank You

Contributing to open source is a journey, not a destination. Whether you're fixing a typo, adding a major feature, or helping other users, every contribution makes this project better.

**Happy coding! 🚀**

---

*For questions about contributing, please open a discussion on GitHub or reach out to the maintainers.*