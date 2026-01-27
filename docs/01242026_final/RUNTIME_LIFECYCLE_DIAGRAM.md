# Runtime Lifecycle Diagram (One-Page Reference)

**CTO Request:** "The one-page runtime lifecycle diagram you can keep on your desk"

---

## The Three Things That Matter

```
┌─────────────────────────────────────────────────────────────┐
│  1. PROCESS ENTRY POINT                                     │
│     "Where does execution begin?"                          │
│                                                             │
│     runtime_main.py → main()                               │
│     - Load config                                           │
│     - One function call                                    │
│     - Zero logic                                           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  2. OBJECT GRAPH CREATION                                   │
│     "Who wires the world together?"                         │
│                                                             │
│     create_runtime_services(config)                         │
│                                                             │
│     Adapters (Layer 0)                                      │
│       ↓                                                     │
│     Foundation Abstractions (Layer 1)                       │
│       ↓                                                     │
│     StateSurface (with ArtifactRegistry)                   │
│       ↓                                                     │
│     WriteAheadLog                                           │
│       ↓                                                     │
│     IntentRegistry                                          │
│       ↓                                                     │
│     ExecutionLifecycleManager                              │
│                                                             │
│     Returns: RuntimeServices object                        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  3. LONG-LIVED OWNERS                                       │
│     "Who keeps things alive?"                               │
│                                                             │
│     RuntimeServices object owns:                            │
│     - Redis clients (must stay alive)                       │
│     - StateSurface (singleton)                             │
│     - ExecutionLifecycleManager (singleton)                 │
│     - Artifact registries (stable)                         │
│                                                             │
│     FastAPI receives services (doesn't create them)         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  FASTAPI APP CREATION                                       │
│                                                             │
│     create_fastapi_app(services)                            │
│     - Receives RuntimeServices                             │
│     - Registers all API routes                             │
│     - Returns FastAPI app                                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  SERVER START                                               │
│                                                             │
│     uvicorn.run(app)                                       │
│     - Server runs                                           │
│     - Routes handle requests                               │
│     - Services stay alive for process lifetime             │
└─────────────────────────────────────────────────────────────┘
```

---

## Initialization Order (CRITICAL)

```
1. PublicWorksFoundationService
   ├── Initialize adapters (Redis, Arango, Supabase, GCS, etc.)
   └── Initialize abstractions (StateManagement, FileStorage, etc.)

2. StateSurface
   └── Creates ArtifactRegistry internally

3. WriteAheadLog
   └── Uses RedisAdapter from PublicWorksFoundationService

4. IntentRegistry
   └── Empty initially, handlers registered explicitly

5. ExecutionLifecycleManager
   ├── Receives IntentRegistry
   ├── Receives StateSurface
   ├── Receives WriteAheadLog
   └── Receives ArtifactStorageAbstraction

6. RuntimeServices Container
   └── Owns all services

7. FastAPI App
   └── Receives RuntimeServices, registers routes
```

---

## Red Flags (Guardrails)

### 🚩 Red Flag #1: "Importing causes side effects"
**If:** `import module` initializes Redis/registers routes  
**Then:** ❌ Stop immediately

### 🚩 Red Flag #2: "Routes create services"
**If:** `@app.post("/do-thing")` creates ExecutionLifecycleManager  
**Then:** ❌ Architectural drift

### 🚩 Red Flag #3: "We don't know startup order"
**If:** "I think Redis initializes before StateSurface... maybe?"  
**Then:** ❌ Lost the graph

### 🚩 Red Flag #4: "Docker fixes it"
**If:** "It works in Docker but not locally"  
**Then:** ❌ Startup logic is implicit

---

## Key Principles

1. **Entry point is boring** - One file, one function, zero logic
2. **Object graph is explicit** - Created once, in order, in `create_runtime_services()`
3. **Ownership is clear** - RuntimeServices object owns all services
4. **FastAPI receives, doesn't create** - Routes call services, don't construct them
5. **No side effects on import** - All initialization is explicit

---

## Connection to Intents & Journeys

> **Your intent and journey contracts only mean something if the runtime wiring is deterministic.**

**If services are recreated unpredictably:**
- ❌ Intent idempotency breaks
- ❌ Journeys resume incorrectly
- ❌ Artifact graphs fork silently

**This startup architecture is the physical foundation that makes contract tests truthful.**

---

## File Structure

```
runtime_main.py              # Entry point (boring)
  ↓
service_factory.py           # Object graph creation
  ├── create_runtime_services()  # Build graph
  └── create_fastapi_app()        # Create app
  ↓
runtime_services.py          # Service container
runtime_api.py               # Route definitions
```

---

**Keep this on your desk. When in doubt, refer to this diagram.**
