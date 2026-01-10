# Semantic Components E2E Test Guide

## Overview

This test suite validates the new production-grade components that use semantic APIs:

- **FileUploader** - File upload with semantic test IDs
- **FileDashboard** - File listing and management with semantic test IDs
- **ParsePreview** - File parsing and preview with semantic test IDs
- **MetadataExtractor** - Metadata extraction with semantic test IDs

## Prerequisites

1. **Install Playwright**:
   ```bash
   cd symphainy-frontend
   npm install
   npx playwright install chromium
   ```

2. **Start Backend Server**:
   ```bash
   # From project root
   cd symphainy-platform
   python3 main.py
   # Backend should be running on http://localhost:8000
   ```

3. **Start Frontend Server** (or let Playwright start it):
   ```bash
   # From symphainy-frontend directory
   npm run dev
   # Frontend should be running on http://localhost:3000
   ```

## Running Tests

### Run All Semantic Component Tests

```bash
cd symphainy-frontend
npx playwright test tests/e2e/semantic-components.spec.ts
```

### Run Specific Test

```bash
# Test file upload
npx playwright test tests/e2e/semantic-components.spec.ts -g "FileUploader"

# Test file dashboard
npx playwright test tests/e2e/semantic-components.spec.ts -g "FileDashboard"

# Test parse preview
npx playwright test tests/e2e/semantic-components.spec.ts -g "ParsePreview"

# Test metadata extraction
npx playwright test tests/e2e/semantic-components.spec.ts -g "MetadataExtractor"

# Test complete workflow
npx playwright test tests/e2e/semantic-components.spec.ts -g "Complete workflow"
```

### Run in Headed Mode (See Browser)

```bash
npx playwright test tests/e2e/semantic-components.spec.ts --headed
```

### Run with Debug Mode

```bash
npx playwright test tests/e2e/semantic-components.spec.ts --debug
```

### Run with UI Mode (Interactive)

```bash
npx playwright test tests/e2e/semantic-components.spec.ts --ui
```

## Test Coverage

### 1. FileUploader Test
- ✅ Multi-step file type selection (Structured Data → CSV)
- ✅ File selection using semantic test ID
- ✅ File upload using semantic test ID
- ✅ Semantic API endpoint: `/api/content-pillar/upload-file`

### 2. FileDashboard Test
- ✅ Dashboard visibility using semantic test ID
- ✅ File list refresh using semantic test ID
- ✅ File list items using semantic test IDs
- ✅ View file button using semantic test ID
- ✅ Parse file button using semantic test ID
- ✅ "Show All" toggle using semantic test ID
- ✅ Semantic API endpoint: `/api/content-pillar/list-uploaded-files`

### 3. ParsePreview Test
- ✅ Parse preview component visibility using semantic test ID
- ✅ File selection dropdown using semantic test ID
- ✅ Parse button using semantic test ID
- ✅ Parse results display using semantic test ID
- ✅ Tab navigation using semantic test IDs
- ✅ Details modal using semantic test ID
- ✅ Semantic API endpoint: `/api/content-pillar/process-file/{fileId}`

### 4. MetadataExtractor Test
- ✅ Metadata extractor component visibility using semantic test ID
- ✅ File selection using semantic test ID
- ✅ Extraction type selection using semantic test ID
- ✅ Extract button using semantic test ID
- ✅ Semantic API endpoints: 
  - `/api/content-pillar/list-uploaded-files`
  - `/api/content-pillar/get-file-details/{fileId}`

### 5. Complete Workflow Test
- ✅ End-to-end flow: Upload → Parse → Extract Metadata
- ✅ Validates all components work together
- ✅ Tests semantic API integration across all components

## Semantic Test IDs Used

### FileUploader
- `content-pillar-file-upload-area`
- `file-type-selector`
- `file-upload-dropzone`
- `select-files-to-upload`
- `select-copybook-file`
- `complete-file-upload`

### FileDashboard
- `content-pillar-file-dashboard`
- `refresh-files-button`
- `file-list-item-{fileId}`
- `view-file-{fileId}`
- `enhanced-processing-{fileId}`
- `parse-file-{fileId}`
- `delete-file-{fileId}`
- `toggle-show-all-files`

### ParsePreview
- `content-pillar-parse-preview`
- `parse-file-selector`
- `parse-file-button`
- `reset-parse-button`
- `view-parse-details-button`
- `parse-results-content`
- `parse-tab-{tabId}`
- `parse-details-modal`

### MetadataExtractor
- `content-pillar-metadata-extractor`
- `metadata-file-selector`
- `metadata-extraction-type-selector`
- `extract-metadata-button`

## Troubleshooting

### Authentication Issues

If you encounter authentication issues:

1. **Check if backend is running**:
   ```bash
   curl http://localhost:8000/health
   ```

2. **Check if frontend is running**:
   ```bash
   curl http://localhost:3000
   ```

3. **Run in headed mode to see what's happening**:
   ```bash
   npx playwright test tests/e2e/semantic-components.spec.ts --headed
   ```

4. **Check browser console**:
   - Open DevTools in headed mode
   - Look for authentication errors
   - Check network tab for API calls

### Test Timeouts

If tests timeout:

1. **Increase timeout in test**:
   ```typescript
   test('My test', async ({ page }) => {
     test.setTimeout(120000); // 2 minutes
     // ...
   });
   ```

2. **Check if services are slow**:
   - Backend may be processing requests slowly
   - Frontend may be slow to render
   - Network may be slow

### Element Not Found

If elements are not found:

1. **Check if component is rendered**:
   - Use `--headed` mode to see the page
   - Check if React has hydrated
   - Check if component is conditionally rendered

2. **Check semantic test IDs**:
   - Verify test IDs are correct in component
   - Check if test IDs are dynamically generated
   - Ensure test IDs are present in DOM

3. **Wait for elements**:
   - Increase timeout
   - Add explicit waits
   - Check for loading states

## Environment Variables

Set these environment variables if needed:

```bash
export TEST_FRONTEND_URL="http://localhost:3000"
export TEST_BACKEND_URL="http://localhost:8000"
```

## Test Files

Test files are automatically created in `tests/fixtures/`:
- `sample.csv` - Sample CSV file for testing
- `sample.json` - Sample JSON file for testing

## CI/CD Integration

These tests can be integrated into CI/CD pipelines:

```yaml
- name: Run Semantic Component Tests
  run: |
    cd symphainy-frontend
    npx playwright test tests/e2e/semantic-components.spec.ts
```

## Next Steps

1. ✅ Tests created with semantic test IDs
2. ✅ Test file upload flow
3. ✅ Test file dashboard
4. ✅ Test parse preview
5. ✅ Test metadata extraction
6. ✅ Test complete workflow
7. ⏳ Add more edge cases
8. ⏳ Add error handling tests
9. ⏳ Add performance tests
10. ⏳ Add accessibility tests





