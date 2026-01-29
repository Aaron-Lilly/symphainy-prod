# Agent B Task: Remove `any` Types (Phase 4)

**Branch:** `cursor/parameter-assertion-tests-829c`
**Priority:** High
**Estimated Scope:** ~565 `any` usages

## Context

The frontend build passes and all major API stubs have been replaced with real backend calls. Now we need to remove permissive `any` types to get full TypeScript safety.

## Your Task

Systematically remove `any` types across the codebase, replacing them with proper types.

## How to Find `any` Usages

```bash
# Count all any usages
cd /workspace/symphainy-frontend
grep -r ": any" --include="*.ts" --include="*.tsx" | wc -l

# Find any usages by directory
grep -rn ": any" --include="*.ts" --include="*.tsx" shared/
grep -rn ": any" --include="*.tsx" app/
grep -rn ": any" --include="*.tsx" components/
```

## Priority Order

1. **`shared/managers/`** - API managers (highest impact)
2. **`shared/services/`** - Service layer
3. **`shared/hooks/`** - Hooks
4. **`shared/types/`** - Type definitions
5. **`app/`** - Page components
6. **`components/`** - UI components

## Common Patterns to Fix

### Pattern 1: Function parameters
```typescript
// Bad
function processData(data: any): void

// Good - use unknown + type guard
function processData(data: unknown): void {
  if (isValidData(data)) { ... }
}

// Or use specific type
function processData(data: DataPayload): void
```

### Pattern 2: State variables
```typescript
// Bad
const [data, setData] = useState<any>(null);

// Good
const [data, setData] = useState<DataType | null>(null);
```

### Pattern 3: Object properties
```typescript
// Bad
interface Config {
  options: any;
}

// Good
interface Config {
  options: Record<string, unknown>;
}
// Or specific type
interface Config {
  options: ConfigOptions;
}
```

### Pattern 4: API responses
```typescript
// Bad
const response: any = await fetch(...);

// Good - use the canonical types from runtime-contracts.ts
import type { ExecutionStatusResponse } from '@/shared/types/runtime-contracts';
const response: ExecutionStatusResponse = await client.getExecutionStatus(...);
```

### Pattern 5: Event handlers
```typescript
// Bad
onChange={(e: any) => ...}

// Good
onChange={(e: React.ChangeEvent<HTMLInputElement>) => ...}
```

## Canonical Types to Use

Import from `@/shared/types/runtime-contracts.ts`:
- `SessionCreateRequest`, `SessionCreateResponse`
- `IntentSubmitRequest`, `IntentSubmitResponse`
- `ExecutionStatusResponse`
- `FileArtifact`, `ParsedContentArtifact`

Import from `@/shared/types/file.ts`:
- `FileMetadata`, `FileStatus`, `FileType`
- `ApiUploadRequest`

## Files to Skip

- `*.test.ts` / `*.test.tsx` - Tests can keep some `any` for mocking
- `archive/` - Archived code
- `node_modules/` - External deps

## Verification

After each file, verify build still passes:
```bash
npm run build 2>&1 | tail -10
```

## Success Criteria

- [ ] No `any` types in `shared/managers/`
- [ ] No `any` types in `shared/services/`
- [ ] No `any` types in `shared/hooks/`
- [ ] Build still passes
- [ ] Reduced `any` count by at least 50%

## Git Workflow

```bash
# Commit after each directory
git add -A
git commit -m "Remove any types from shared/managers/"
git push
```

## What NOT to Do

- Don't use `// @ts-ignore` to hide errors
- Don't replace `any` with `unknown` without adding type guards
- Don't break the build - verify after each change

## Coordination

- **Agent A** is working on: Hook consolidation (Phase 5) and test alignment (Phase 6)
- **You** are working on: `any` type removal
- Commit and push frequently to avoid conflicts
