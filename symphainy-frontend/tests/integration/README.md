# Integration Tests for Supabase Authentication

## Overview

These integration tests verify that the frontend and backend work together correctly with Supabase authentication.

## Test Structure

### Backend Integration Tests (`test_auth_integration.py`)
- Tests backend API endpoints directly
- Verifies Supabase integration
- Tests error handling and edge cases

### Frontend Integration Tests (`test_auth_integration.ts`)
- Tests frontend auth functions (`loginUser`, `registerUser`)
- Verifies communication with backend
- Tests response format consistency

## Prerequisites

1. **Backend Server Running**
   ```bash
   cd symphainy-platform
   ./startup.sh --background --minimal
   ```

2. **Environment Variables** (optional)
   ```bash
   export TEST_BACKEND_URL=http://localhost:8000
   export TEST_FRONTEND_URL=http://localhost:3000
   export TEST_EMAIL_DOMAIN=example.com
   export TEST_PASSWORD=TestPassword123!
   ```

3. **Supabase Configuration**
   - Backend must be configured with Supabase credentials
   - Test accounts will be created in your Supabase project

## Running Tests

### Backend Integration Tests

```bash
cd symphainy-platform
pytest tests/integration/test_auth_integration.py -v
```

### Frontend Integration Tests

```bash
cd symphainy-frontend
npm run test:integration
```

Or if using Jest/Vitest directly:

```bash
# Install test dependencies if needed
npm install --save-dev @testing-library/jest-dom vitest

# Run tests
npx vitest tests/integration/test_auth_integration.ts
```

## Test Coverage

### ✅ Registration Flow
- Successful user registration
- Duplicate user handling
- Invalid email format
- Weak password validation

### ✅ Login Flow
- Successful login with valid credentials
- Invalid email rejection
- Invalid password rejection
- Token format validation

### ✅ Integration
- Frontend-backend communication
- Response format consistency
- Error handling
- Network error handling

## Test Account Management

- Each test creates a unique test account using UUID
- Test accounts use format: `test-integration-{uuid}@{domain}`
- Accounts are **not automatically deleted** (manual cleanup may be needed)
- Consider using a dedicated test Supabase project

## Cleanup

To clean up test accounts manually:

1. **Via Supabase Dashboard**:
   - Go to Authentication → Users
   - Search for `test-integration-`
   - Delete test accounts

2. **Via Supabase Admin API** (if configured):
   ```python
   from supabase import create_client
   supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
   # Delete user by email
   ```

## Troubleshooting

### Backend Not Accessible
```
Error: Connection refused
```
**Solution**: Ensure backend is running on port 8000

### Supabase Authentication Fails
```
Error: Security Guard service not available
```
**Solution**: 
- Check backend logs for Supabase configuration
- Verify `SUPABASE_URL` and `SUPABASE_SECRET_KEY` are set
- Ensure Security Guard is initialized

### Test Accounts Not Created
```
Error: Registration failed
```
**Solution**:
- Check Supabase project settings
- Verify email domain is allowed
- Check Supabase rate limits

## Best Practices

1. **Use Unique Test Emails**: Each test generates unique email to avoid conflicts
2. **Wait for Supabase**: Add delays after registration before login
3. **Clean Up**: Manually clean up test accounts periodically
4. **Isolated Tests**: Each test should be independent
5. **Error Handling**: Tests should handle both success and failure cases

## CI/CD Integration

For CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Run Integration Tests
  run: |
    cd symphainy-platform
    pytest tests/integration/test_auth_integration.py -v
  env:
    TEST_BACKEND_URL: http://localhost:8000
    TEST_EMAIL_DOMAIN: example.com
```

## Next Steps

1. ✅ Backend integration tests created
2. ✅ Frontend integration tests created
3. ⚠️ Add test account cleanup automation
4. ⚠️ Add CI/CD integration
5. ⚠️ Consider dedicated test Supabase project




