# Symphainy Platform v1

**Status:** 🚧 **Week 0 - Scaffolding**  
**Architecture:** Platform-First Execution Spine

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

# Start infrastructure
docker-compose -f docker-compose.infrastructure.yml up -d

# Run tests
pytest tests/ -v
```

---

## 📚 Documentation

- **Architecture**: `docs/final_platform_architecture.md`
- **Implementation Plan**: `docs/rebuild_implementation_plan_v1.md`
- **Discovery**: `docs/week0_discovery.md`
- **Cursor Rules**: `.cursorrules`
- **Cursor Web Agents Setup**: `docs/CURSOR_WEB_AGENTS_SETUP.md` (Quick Start: `docs/CURSOR_SETUP_QUICK_START.md`)

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

## 📋 Week-by-Week Plan

- **Week 0**: Stabilize & Scaffold ✅ (Current)
- **Week 1**: Runtime Plane v0 (Execution Spine)
- **Week 2**: Curator + Agent Foundation + Realm Wiring
- **Week 3**: Experience Plane (Thin but Real)

---

## 📝 License

[Your License Here]

---

**Last Updated:** January 2026
