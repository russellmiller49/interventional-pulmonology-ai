# Contributing to Interventional Pulmonology AI Assistant

Thank you for your interest in contributing to this project! This document provides guidelines for contributing.

## 🎯 Project Overview

This is an AI-powered chatbot for interventional pulmonology that processes medical documents using LangExtract and provides evidence-based responses through a RAG (Retrieval-Augmented Generation) pipeline.

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Git
- API keys for Gemini and OpenAI

### Setup

1. **Fork the repository**
   ```bash
   git clone https://github.com/your-username/interventional-pulmonology-ai.git
   cd interventional-pulmonology-ai
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

## 📝 Development Guidelines

### Code Style

- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Write docstrings for functions and classes
- Keep functions focused and single-purpose

### Testing

- Write tests for new features
- Ensure existing tests pass
- Use descriptive test names

### Commit Messages

Use conventional commit format:
```
feat: add new feature
fix: resolve bug
docs: update documentation
style: format code
refactor: restructure code
test: add tests
chore: maintenance tasks
```

## 🏗️ Project Structure

```
interventional-pulmonology-ai/
├── src/
│   ├── extractors/          # LangExtract processing
│   ├── knowledge_base/      # Vector store and document processing
│   └── chatbot/            # RAG pipeline
├── data/                   # Data storage
├── config/                 # Configuration files
├── tests/                  # Test files
├── docs/                   # Documentation
└── examples/               # Usage examples
```

## 🔧 Development Workflow

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write code
   - Add tests
   - Update documentation

3. **Test your changes**
   ```bash
   python -m pytest tests/
   ```

4. **Submit a pull request**
   - Provide a clear description
   - Reference any related issues
   - Ensure CI checks pass

## 🐛 Bug Reports

When reporting bugs, please include:

- **Description**: Clear description of the issue
- **Steps to reproduce**: Detailed steps to reproduce the bug
- **Expected behavior**: What you expected to happen
- **Actual behavior**: What actually happened
- **Environment**: OS, Python version, dependencies
- **Screenshots**: If applicable

## 💡 Feature Requests

When requesting features, please include:

- **Description**: Clear description of the feature
- **Use case**: Why this feature would be useful
- **Implementation ideas**: Any thoughts on implementation
- **Priority**: High/Medium/Low

## 📚 Documentation

- Keep documentation up to date
- Add examples for new features
- Update README.md when needed

## 🤝 Code Review

- Be respectful and constructive
- Focus on the code, not the person
- Provide specific feedback
- Suggest improvements

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 🆘 Getting Help

- Check existing issues and discussions
- Create a new issue for bugs or feature requests
- Join our community discussions

Thank you for contributing! 🎉
