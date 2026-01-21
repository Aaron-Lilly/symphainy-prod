# Symphainy Platform v2.0

**Status:** ✅ **Core Capabilities Operational - Integration Testing**  
**Architecture:** Platform-First Execution Spine  
**Last Updated:** January 2026

---

## 🎯 What is Symphainy?

Symphainy is an **Agentic Integrated Development Platform (IDP) + Agentic Operating System (AOS)** that enables enterprises to:

- Build AI-powered solutions incrementally
- Combine deterministic AI + expert reasoning
- Operate safely in regulated, multi-tenant environments
- Bring their own infrastructure (BYOI)
- Bring their own interfaces (BYOH)

---

## 🏗️ Architecture

### Core Principles

1. **Platform-First, Not MVP-First**: Build the execution spine first, express use cases on top
2. **Execution Ownership**: Runtime Plane owns execution, Curator owns capability registration
3. **Capability by Design, Enabled by Policy**: WAL, Saga, Zero Trust, multi-tenancy exist structurally

### Platform Layers

```
Runtime Plane (Execution Core)
  ↓
Smart City Plane (Capability Governor)
  ↓
Realm Plane (Operating Domains)
  ↓
Experience Plane (Delivery Surface)
```

### Directory Structure

```
symphainy_platform/
  runtime/          # Runtime Plane - execution control, WAL, Saga, state
  agentic/          # Agent Foundation - shared reasoning substrate
  realms/           # Realms - semantic ownership zones
    content/        # Deterministic extraction & normalization
    insights/       # Semantic interpretation & data quality
    journey/        # SOP ↔ Workflow dual views
    solution/       # Solution landing & business outcomes
  experience/       # Experience Plane - REST, WebSocket, UI
  infra/            # Infrastructure adapters
```

**Note:** Package is named `symphainy_platform` (not `platform`) to avoid conflict with Python's built-in `platform` module.

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Redis (for hot state)
- ArangoDB (for durable state)
- Docker & Docker Compose (for infrastructure)

### Setup

```bash
# Clone repository
cd /home/founders/demoversion/symphainy_source_code

# Install dependencies
pip install -r requirements.txt

# Start all services (see docs/VM_DEPLOYMENT_STARTUP_GUIDE.md for details)
docker-compose up -d

# Or use the startup script
./scripts/startup.sh

# Run tests
pytest tests/ -v
```

---

## 📚 Documentation

- **VM Deployment Startup Guide**: `docs/VM_DEPLOYMENT_STARTUP_GUIDE.md` - **Start here for deployment** - Complete guide for starting all containers
- **Platform Overview**: `docs/PLATFORM_OVERVIEW.md` - Executive overview of platform capabilities
- **Developer Guide**: `docs/00_START_HERE.md` - Developer entry point
- **Architecture**: `docs/architecture/north_star.md` - Authoritative architecture guide
- **Platform Rules**: `docs/PLATFORM_RULES.md` - Development standards
- **Cursor Rules**: `.cursorrules` - Cursor AI development guidelines
- **API Contracts**: `docs/execution/api_contracts_frontend_integration.md` - Frontend integration

---

## 🧪 Testing

See `tests/README.md` for detailed testing documentation.

```bash
# Run all tests
pytest tests/ -v

# Run unit tests
pytest tests/unit/ -v -m unit

# Run integration tests
pytest tests/integration/ -v -m integration
```

---

## 🏗️ Development

### Key Patterns

- **Runtime Plane**: Owns execution, sessions, state, WAL, Saga
- **Agents**: Reason, don't execute (use Runtime for execution)
- **Realms**: Compose logic, register saga steps, emit facts
- **Experience**: Submit intents, stream state, deliver outcomes

### Anti-Patterns (DON'T DO)

❌ Direct state storage in services/agents  
❌ Ad hoc orchestration in realms  
❌ Agents executing side effects  
❌ Experience running business logic  

See `.cursorrules` for detailed development guidelines.

---

## 📋 Current Status

### ✅ Completed
- **Content Realm Phases 1-4**: File management, bulk operations, lifecycle management
- **Insights Realm**: Data quality, interpretation, analysis
- **Journey Realm**: Workflow creation, SOP generation, visual generation
- **Runtime Plane**: Intent-based execution, state management, WAL
- **Experience Plane**: REST APIs, WebSocket streaming, agent interfaces
- **Infrastructure**: Multi-tenant isolation, file storage, state management

### 🚧 In Progress
- Frontend integration testing
- Remaining realm implementations
- Production hardening (monitoring, alerting)

### 📊 Test Status
- **85% test pass rate** (22/26 tests)
- **100% integration test pass rate** (8/8)
- **100% E2E test pass rate** (3/3)

---

## 📝 License

[Your License Here]

---

**Last Updated:** January 2026
