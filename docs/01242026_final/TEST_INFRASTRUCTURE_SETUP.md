# Test Infrastructure Setup for Journey 1

**Date:** January 25, 2026  
**Status:** ✅ **COMPLETE**  
**Purpose:** Automated testing infrastructure for intent contracts and journey contracts

---

## What Was Created

### 1. Test Utilities (`__tests__/utils/test-helpers.ts`)

**Purpose:** Reusable test utilities and mocks for testing intents and journeys.

**Key Functions:**
- `createMockPlatformState()` - Creates mock platform state for testing
- `mockSuccessfulIntent()` - Mocks successful intent execution
- `mockFailedIntent()` - Mocks failed intent execution
- `createMockFile()` - Creates mock file for testing
- `createMockLargeFile()` - Creates mock file exceeding size limit (for boundary tests)
- `expectIntentCalled()` - Asserts intent was called with correct parameters
- `expectExecutionTracked()` - Asserts execution was tracked
- `resetAllMocks()` - Resets all mocks between tests

### 2. Test Directory Structure

```
__tests__/
├── utils/
│   └── test-helpers.ts          # Test utilities and mocks
├── intents/
│   └── content/
│       └── [intent_name].test.ts  # Intent contract tests (to be created)
└── journeys/
    └── journey_1_file_upload_processing.test.ts  # Journey contract tests (to be created)
```

### 3. Example Test Files (Templates Created)

**Intent Contract Test Template:**
- `__tests__/intents/content/ingest_file.test.ts` - Example intent contract test
- Tests direct API call prevention, parameter validation, boundary violations, etc.

**Journey Contract Test Template:**
- `__tests__/journeys/journey_1_file_upload_processing.test.ts` - Example journey contract test
- Tests all 5 scenarios: Happy Path, Injected Failure, Partial Success, Retry/Recovery, Boundary Violation

---

## How to Use

### Running Tests

```bash
# Run all tests
npm test

# Run intent tests only
npm test -- intents

# Run journey tests only
npm test -- journeys

# Run specific test file
npm test -- journey_1_file_upload_processing.test.ts

# Run in watch mode
npm test -- --watch
```

### Writing Intent Contract Tests

```typescript
import { ContentAPIManager } from '@/shared/managers/ContentAPIManager';
import {
  createMockPlatformState,
  createMockFile,
  mockSuccessfulIntent,
  expectIntentCalled,
} from '../../utils/test-helpers';

describe('Intent Contract: ingest_file', () => {
  let contentAPIManager: ContentAPIManager;
  let mockPlatformState: ReturnType<typeof createMockPlatformState>;

  beforeEach(() => {
    mockPlatformState = createMockPlatformState();
    contentAPIManager = new ContentAPIManager();
    jest.spyOn(contentAPIManager as any, 'getPlatformState').mockReturnValue(mockPlatformState);
  });

  test('test_ingest_file_direct_api_call_fails', async () => {
    const file = createMockFile();
    mockSuccessfulIntent(mockPlatformState, 'ingest_file', {
      file: { semantic_payload: { file_id: 'test-id' } }
    });

    await contentAPIManager.uploadFile(file);

    expect(mockPlatformState.submitIntent).toHaveBeenCalled();
    expect(global.fetch).not.toHaveBeenCalled();
  });
});
```

### Writing Journey Contract Tests

```typescript
describe('Journey 1: File Upload & Processing', () => {
  describe('Scenario 1: Happy Path', () => {
    test('should complete journey end-to-end', async () => {
      // Step 1: ingest_file
      mockSuccessfulIntent(mockPlatformState, 'ingest_file', {...});
      await contentAPIManager.uploadFile(file);

      // Step 2: parse_content
      mockSuccessfulIntent(mockPlatformState, 'parse_content', {...});
      await contentAPIManager.parseFile(...);

      // Verify all intents used intent-based API
      expect(mockPlatformState.submitIntent).toHaveBeenCalledTimes(5);
    });
  });
});
```

---

## Test Coverage Goals

### Intent Level
- [ ] Direct API call prevention (all intents)
- [ ] Parameter validation (all intents)
- [ ] Boundary violations (all intents)
- [ ] Negative journey evidence (all intents)
- [ ] Idempotency (when implemented)

### Journey Level
- [ ] Scenario 1: Happy Path (all journeys)
- [ ] Scenario 2: Injected Failure (all journeys)
- [ ] Scenario 3: Partial Success (all journeys)
- [ ] Scenario 4: Retry/Recovery (all journeys)
- [ ] Scenario 5: Boundary Violation (all journeys)

---

## Next Steps

1. **Create Intent Contract Tests**
   - Create test files for all 7 Content Realm intents
   - Implement all proof tests from intent contracts

2. **Create Journey Contract Tests**
   - Complete Journey 1 test file
   - Test all 5 scenarios

3. **Run Tests**
   - Verify all tests pass
   - Fix any issues discovered

4. **Add to CI/CD**
   - Integrate tests into CI/CD pipeline
   - Ensure tests run on every commit

---

## Benefits

1. **Automated Validation** - Tests run automatically, catch regressions
2. **Fast Feedback** - Know immediately if changes break contracts
3. **Documentation** - Tests serve as executable documentation
4. **Confidence** - Prove contracts are actually enforced
5. **Scalability** - Easy to add tests for new intents/journeys

---

**Last Updated:** January 25, 2026  
**Owner:** Development Team  
**Status:** ✅ **INFRASTRUCTURE READY** - Ready for test implementation
