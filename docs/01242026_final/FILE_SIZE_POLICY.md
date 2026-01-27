# File Size Policy

**Date:** January 25, 2026  
**Status:** ✅ **ACTIVE**  
**Policy Type:** Platform Policy (Data Steward / Civic Systems)

---

## Policy Definition

### Maximum File Size
- **Default Limit:** 100 MB (104,857,600 bytes)
- **Scope:** All file uploads via `ingest_file` intent
- **Enforcement:** Frontend validation before intent submission
- **Policy Store:** Configurable via MaterializationPolicyStore (future)

---

## Enforcement

### Frontend Validation
- **Location:** `ContentAPIManager.uploadFile()`
- **Check:** File size must be ≤ 100 MB before `submitIntent('ingest_file', ...)`
- **Error:** "File size exceeds 100MB limit. Maximum allowed size is 100MB."

### Runtime Validation (Future)
- **Location:** Runtime / Data Steward (Civic Systems)
- **Check:** Validate file size in boundary contract
- **Policy Store:** Configurable per tenant/workspace

---

## Rationale

1. **Performance:** Large files impact parsing, embedding extraction, and analysis performance
2. **Storage:** GCS storage costs and limits
3. **User Experience:** Large files cause timeouts and poor UX
4. **Infrastructure:** Prevents resource exhaustion

---

## Configuration

### Default Value
```typescript
const DEFAULT_MAX_FILE_SIZE = 100 * 1024 * 1024; // 100MB
```

### Policy Store (Future)
```yaml
materialization_policy:
  file_size_limits:
    default: 104857600  # 100MB
    per_tenant:
      tenant_123: 524288000  # 500MB (enterprise)
      tenant_456: 104857600  # 100MB (standard)
```

---

## Intent Contract Integration

### Required in Intent Contract
- **Boundary Constraint:** File size must be ≤ policy limit
- **Validation:** Enforced before intent submission
- **Error Handling:** Clear error message if limit exceeded

---

**Prepared By:** Development Team  
**Date:** January 25, 2026  
**Status:** ✅ **ACTIVE POLICY**
