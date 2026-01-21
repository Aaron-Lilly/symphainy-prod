# Artifact Plane Proposal Analysis

**Date:** January 19, 2026  
**Proposal:** Derived Artifact Plane as first-class architectural layer

---

## Executive Summary

**Verdict:** ✅ **This is the right architectural direction**

The proposal correctly identifies that artifacts are a distinct concern requiring their own plane. However, full implementation is a **significant architectural change** requiring careful migration planning.

---

## Strengths of the Proposal

### 1. Clean Separation of Concerns

**Current Problem:**
- Artifacts are scattered (execution state, session state, ad-hoc storage)
- No clear ownership or lifecycle
- Hard to retrieve cross-realm
- Blurs execution truth with representations

**Proposed Solution:**
- Artifacts get their own plane
- Clear ownership (Realms produce, Artifact Plane stores)
- Cross-realm consumable by design
- Execution state stays minimal and deterministic

**Assessment:** ✅ **Correctly identifies the architectural gap**

### 2. Infrastructure Mapping

**GCS → Payloads:**
- PDFs, images, diagrams, rendered documents
- Content-addressable, cheap, durable
- ✅ **Makes sense** - GCS is perfect for binary payloads

**Supabase → Registry & Metadata:**
- Artifact catalog, ownership, type, lineage pointers
- ✅ **Makes sense** - Postgres is ideal for relational metadata

**Arango → Semantic & Lineage Graph:**
- Relationships, artifact → intent, artifact → journey
- ✅ **Makes sense** - Arango excels at graph relationships

**Redis → Transient Working Memory:**
- In-flight generation, streaming assembly
- ✅ **Makes sense** - Redis for ephemeral coordination

**Assessment:** ✅ **Infrastructure choices are sound**

### 3. Aligns with Platform Principles

**"Facts not files"** - Artifacts are representations, not raw data
**"Governed representations"** - Policy-driven, lineage-aware
**"Cross-realm consumable"** - Designed for reuse
**"Human-facing by design"** - Purpose-built for human consumption

**Assessment:** ✅ **Reinforces platform vision**

---

## Concerns & Risks

### 1. Implementation Scope

**What Would Need to Change:**

1. **New Abstraction Layer:**
   - `ArtifactPlane` or `DerivedArtifactPlane` abstraction
   - Artifact lifecycle management
   - Artifact registry interface
   - Artifact retrieval patterns

2. **Storage Integration:**
   - GCS integration for payloads
   - Supabase schema for artifact registry
   - Arango graph for lineage
   - Migration from current storage

3. **Realm Updates:**
   - All realms that produce artifacts need to use Artifact Plane
   - Update artifact creation patterns
   - Update artifact retrieval patterns

4. **Runtime Integration:**
   - Artifact Plane hooks into execution lifecycle
   - Materialization policy integration
   - Artifact registration during execution

5. **API Updates:**
   - New artifact retrieval endpoints
   - Artifact lifecycle management APIs
   - Cross-realm artifact access

**Estimated Effort:** 4-6 weeks for full implementation + migration

**Risk Level:** 🔴 **High** - Significant architectural change

### 2. Migration Complexity

**Current State:**
- Artifacts stored in execution state
- Some artifacts may be in session state (wrong, but exists)
- Artifact retrieval via execution_id lookup
- No centralized artifact registry

**Migration Required:**
- Identify all artifact-producing intents
- Migrate existing artifacts to Artifact Plane
- Update all artifact retrieval code
- Ensure backward compatibility during transition

**Risk Level:** 🟡 **Medium** - Requires careful planning

### 3. Breaking Changes

**Potential Breaking Points:**
- Frontend expects artifacts in execution state
- Tests assume artifacts in execution state
- Other realms may depend on current artifact location
- API contracts may change

**Risk Level:** 🟡 **Medium** - Can be mitigated with compatibility layer

---

## Recommended Approach: Phased Implementation

### Phase 1: Tactical Bridge (Immediate - 1-2 days)

**Goal:** Fix the 500 errors NOW

**Approach:**
- Include `execution_id` in artifact's `semantic_payload` when created
- Use `execution_id` to retrieve artifacts from execution state
- Minimal change, solves immediate problem

**Files to Change:**
- `outcomes_orchestrator.py` - Include execution_id in semantic_payload
- `_handle_create_solution` - Use execution_id for retrieval

**Risk:** ✅ **Low** - Minimal change, backward compatible

---

### Phase 2: Proof of Concept (1-2 weeks)

**Goal:** Validate Artifact Plane concept with one artifact type

**Approach:**
- Implement Artifact Plane for **roadmaps only**
- Create artifact registry in Supabase
- Store roadmap payloads in GCS
- Update roadmap creation/retrieval to use Artifact Plane
- Keep execution state as fallback

**Artifacts:**
- New `ArtifactPlane` abstraction
- Supabase schema for artifact registry
- GCS integration for payloads
- Updated roadmap creation/retrieval

**Validation:**
- Roadmap creation works
- Roadmap retrieval works
- Solution creation from roadmap works
- No regressions in other functionality

**Risk:** 🟡 **Medium** - Isolated to one artifact type

---

### Phase 3: Expand to All Artifacts (2-3 weeks)

**Goal:** Migrate all artifacts to Artifact Plane

**Approach:**
- Expand Artifact Plane to POCs, blueprints, SOPs, etc.
- Migrate existing artifacts
- Update all realm artifact creation
- Update all artifact retrieval
- Remove execution state artifact storage

**Risk:** 🔴 **High** - Touches many systems

---

### Phase 4: Full Integration (1-2 weeks)

**Goal:** Complete Artifact Plane integration

**Approach:**
- Arango graph for lineage
- Full policy integration
- Artifact lifecycle management
- Cross-realm artifact access
- Remove compatibility layers

**Risk:** 🟡 **Medium** - Final integration phase

---

## Immediate Recommendation

### For the 500 Errors (Today):

**Implement Phase 1 (Tactical Bridge):**
1. Include `execution_id` in roadmap/POC `semantic_payload`
2. Use `execution_id` to retrieve from execution state
3. Fix the immediate problem
4. Document as temporary solution

**Code Changes:**
```python
# In _handle_generate_roadmap:
semantic_payload = {
    "roadmap_id": roadmap_result.get("roadmap_id"),
    "execution_id": context.execution_id,  # ADD THIS
    "session_id": context.session_id,
    "status": roadmap_result.get("status")
}

# In _handle_create_solution:
# Extract execution_id from artifact's semantic_payload
# Use it to retrieve full execution state
```

**Time:** 1-2 hours
**Risk:** ✅ **Very Low**

---

### For Long-Term Architecture (Next Sprint):

**Plan Phase 2 (Proof of Concept):**
1. Design Artifact Plane abstraction
2. Design Supabase schema
3. Design GCS integration
4. Implement for roadmaps only
5. Validate approach

**Time:** 1-2 weeks
**Risk:** 🟡 **Medium** (isolated)

---

## Questions for Decision

1. **Timeline:** Can we wait 1-2 weeks for Phase 2, or do we need immediate fix?
   - **Recommendation:** Do Phase 1 now, Phase 2 next sprint

2. **Scope:** Should we do full Artifact Plane or tactical bridge?
   - **Recommendation:** Tactical bridge now, full implementation phased

3. **Infrastructure:** Do we have Supabase/GCS ready, or need setup?
   - **Need to check:** Current infrastructure state

4. **Breaking Changes:** Can we accept API changes, or need backward compatibility?
   - **Recommendation:** Compatibility layer during migration

---

## Conclusion

**The proposal is architecturally sound and aligns with platform vision.**

**However, full implementation is a significant change requiring:**
- 4-6 weeks of development
- Careful migration planning
- Phased rollout

**Recommended Path:**
1. ✅ **Today:** Implement Phase 1 (tactical bridge) to fix 500 errors
2. ✅ **Next Sprint:** Implement Phase 2 (proof of concept) for roadmaps
3. ✅ **Following Sprints:** Expand to all artifacts (Phase 3-4)

This gives us:
- Immediate problem solved
- Validation of approach
- Reduced risk through phased rollout
- Clear migration path

---

**Next Steps:**
1. Implement Phase 1 (tactical bridge) - fix 500 errors
2. Review infrastructure readiness (Supabase/GCS)
3. Design Artifact Plane abstraction
4. Plan Phase 2 implementation
