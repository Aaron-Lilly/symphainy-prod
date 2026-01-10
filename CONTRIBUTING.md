# Contributing to Symphainy Platform

Thank you for your interest in contributing to Symphainy Platform!

## Development Setup

1. **Clone the repository**
   ```bash
   git clone git@github.com:Aaron-Lilly/symphainy-prod.git
   cd symphainy-prod
   ```

2. **Set up environment**
   ```bash
   # Copy environment template
   cp .env.example .env.secrets
   # Edit .env.secrets with your values
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r tests/requirements.txt
   ```

4. **Start infrastructure**
   ```bash
   docker-compose -f docker-compose.infrastructure.yml up -d
   ```

5. **Run tests**
   ```bash
   pytest tests/ -v
   ```

## Development Guidelines

### Architecture Principles

- **Platform-First**: Build execution spine first, express use cases on top
- **Execution Ownership**: Runtime Plane owns execution, not realms/agents
- **State Management**: Use State Surface, never store state directly in services/agents

### Code Style

- Follow `.cursorrules` for architecture patterns
- Use type hints everywhere
- Write async code for I/O operations
- Follow PEP 8 style guide

### Testing

- Write tests for all new features
- Use appropriate markers (`@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.e2e`)
- Ensure tests pass before submitting PR

### Git Workflow

1. Create a feature branch from `main`
2. Make your changes
3. Write/update tests
4. Ensure all tests pass
5. Submit a pull request

## Questions?

See `.cursorrules` for detailed architecture guidelines and patterns.
