# Civic Systems

**Status:** Rebuild in Progress  
**Phase:** Phase 3 (Platform SDK & Experience Plane)

---

## Purpose

Civic Systems are the **platform's behavioral center**.

They do not execute domain work.
They do not own infrastructure.
They **coordinate, govern, translate, and validate**.

---

## Civic Systems

### Smart City
- **SDK-First:** Smart City SDK provides coordination logic
- **Primitives:** Smart City Primitives provide policy decisions
- **Separation:** SDK coordinates, Primitives validate

### Experience
- **Separate Service:** Experience is a separate service
- **Intent Submission:** Submits intents to Runtime
- **WebSocket Streaming:** Streams execution updates

### Agentic
- **Agent SDK:** Provides agent framework
- **Pattern Adoption:** Inspired by CrewAI/LangGraph, but custom (swappable)

### Platform SDK
- **Solution Builder:** Creates Solutions
- **Realm SDK:** Creates domain services
- **Composition:** Composes Civic Systems

---

## References

- [Architecture Guide](../../docs/architecture/north_star.md) - Section 4 Civic Systems
- [Phase 3 Execution Plan](../../docs/execution/phase_3_execution_plan.md)
