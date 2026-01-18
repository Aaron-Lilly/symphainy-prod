# Supabase Rate Limit Constraint

## Overview

This document describes the Supabase rate limit constraints that affect our platform and how we design around them.

**Last Updated:** January 17, 2026  
**Status:** ✅ **Known Constraint - Design Consideration**

---

## Constraint Summary

**External Service:** Supabase Authentication  
**Impact:** Rate limits on user registration and authentication  
**Affected Operations:** User registration, login, token validation  
**Mitigation:** Test mode, graceful degradation, monitoring

---

## Supabase Rate Limits

### Free Tier Limits

Based on Supabase documentation and observed behavior:

| Operation | Limit | Window | Notes |
|-----------|-------|--------|-------|
| **Anonymous Users** | 30 req/min | Per minute | Main bottleneck for testing |
| **User Registration** | ~3-5 req/5min | Per 5 minutes | Very restrictive |
| **Email Sent** | 2/hour | Per hour | Extremely low |
| **Token Refresh** | 150 req/min | Per minute | Highest limit |
| **OTP** | 30 req/min | Per minute | Low |
| **SMS Sent** | 30 req/min | Per minute | Low |

### Pro Tier Limits

| Operation | Limit | Window | Notes |
|-----------|-------|--------|-------|
| **Anonymous Users** | ~300 req/min | Per minute | 10x increase |
| **User Registration** | Higher limits | Varies | More permissive |
| **Email Sent** | Higher limits | Varies | More permissive |

**Note:** Exact Pro tier limits vary and are not publicly documented. Contact Supabase support for specific limits.

---

## Impact on Platform

### Affected Features

1. **User Registration**
   - **Impact:** Can only register 3-5 users per 5 minutes (Free tier)
   - **Error:** `429 Too Many Requests` or `Request rate limit reached`
   - **User Experience:** Registration may fail during high load

2. **Authentication/Login**
   - **Impact:** 30 requests/minute limit (Free tier)
   - **Error:** `429 Too Many Requests`
   - **User Experience:** Login may fail during high load

3. **Testing**
   - **Impact:** Comprehensive test suites hit limits quickly
   - **Error:** Tests fail with rate limit errors
   - **Development:** Slows down development and CI/CD

### Observed Behavior

**Error Messages:**
- `"Request rate limit reached"` - Supabase rate limit exceeded
- `429 Too Many Requests` - HTTP rate limit response
- Logs show: `"Unexpected error in sign_up_with_password: Request rate limit reached"`

**When Limits Are Hit:**
- User registration fails
- Authentication may fail
- Tests cannot create users
- High-volume operations blocked

---

## Design Considerations

### 1. Test Mode Implementation ✅

**Solution:** Test mode with relaxed application-level rate limits

**Implementation:**
- `X-Test-Mode: true` header enables test mode
- Test mode uses relaxed limits (1000 requests/minute)
- Tests use test mode to avoid application rate limits
- **Note:** Does NOT bypass Supabase limits (external service)

**Location:**
- `symphainy_platform/civic_systems/experience/middleware/rate_limiter.py`
- Tests use `TEST_HEADERS = {"X-Test-Mode": "true"}`

**Limitation:**
- Test mode only affects our application rate limits
- Supabase limits still apply (external service)
- Tests may still hit Supabase limits

### 2. Graceful Degradation ✅

**Solution:** Handle rate limit errors gracefully

**Implementation:**
- Return appropriate error responses (429)
- Log rate limit hits for monitoring
- Provide clear error messages to users
- Retry logic with exponential backoff (where appropriate)

**Error Response Format:**
```json
{
  "error": "rate_limit_exceeded",
  "message": "Too many requests. Please try again later.",
  "retry_after": 300
}
```

### 3. Monitoring & Alerting ⏳

**Recommended:** Monitor Supabase rate limit hits

**Implementation:**
- Log all 429 errors from Supabase
- Track rate limit hit frequency
- Alert when approaching limits
- Dashboard showing rate limit status

**Metrics to Track:**
- Rate limit hits per hour/day
- Average requests per minute
- Peak request rates
- User registration success rate

### 4. Test Strategy Adjustments ✅

**Solution:** Design tests to work within Supabase limits

**Current Approach:**
- Use test mode for application rate limits
- Accept that some tests may hit Supabase limits
- Document which tests depend on external limits
- Consider mocking Supabase for high-volume tests

**Test Categories:**
- **Unit Tests:** Mock Supabase (no limits)
- **Integration Tests:** Use test mode, accept Supabase limits
- **Performance Tests:** May hit Supabase limits (expected)

### 5. Production Considerations ⏳

**Recommendations:**

1. **Upgrade to Pro Tier** (if needed)
   - Higher rate limits
   - Better for production workloads
   - Cost: ~$25/month

2. **Implement Request Queuing**
   - Queue registration requests
   - Process at rate limit pace
   - Provide user feedback on queue position

3. **Caching & Optimization**
   - Cache authentication results
   - Reduce redundant Supabase calls
   - Optimize token refresh patterns

4. **Load Balancing**
   - Distribute requests across time
   - Implement request throttling
   - Use CDN for static assets

---

## Known Limitations

### What We Cannot Control

1. **Supabase Rate Limits**
   - External service limits
   - Cannot be bypassed
   - Must design around them

2. **Free Tier Restrictions**
   - Very low limits
   - Not suitable for high-volume testing
   - Production may need Pro tier

3. **Email Sending Limits**
   - 2 emails/hour (Free tier)
   - Affects password reset, verification
   - May need email service alternative

### What We Can Control

1. **Application Rate Limiting** ✅
   - Our own rate limits
   - Test mode for development
   - Configurable limits

2. **Error Handling** ✅
   - Graceful degradation
   - Clear error messages
   - Retry logic

3. **Test Strategy** ✅
   - Test mode implementation
   - Mocking for unit tests
   - Documentation of constraints

---

## Testing Impact

### Tests Affected by Supabase Limits

1. **High Message Volume Test**
   - **Issue:** Cannot create users (Supabase limit)
   - **Status:** Expected failure (external limit)
   - **Workaround:** Use test accounts or mock Supabase

2. **Concurrent WebSocket Connections Test**
   - **Issue:** Cannot create users (Supabase limit)
   - **Status:** Expected failure (external limit)
   - **Workaround:** Use test accounts or mock Supabase

3. **Concurrent Users Test**
   - **Status:** ✅ Passing (test mode helps)
   - **Note:** May still hit Supabase limits with many users

### Test Recommendations

1. **For Unit Tests:**
   - Mock Supabase adapter
   - No rate limit concerns
   - Fast execution

2. **For Integration Tests:**
   - Use test mode (application limits)
   - Accept Supabase limits as constraint
   - Document expected failures

3. **For Performance Tests:**
   - Use Supabase Pro tier (if available)
   - Or mock Supabase for high-volume tests
   - Document Supabase dependency

---

## Monitoring & Alerts

### Recommended Monitoring

1. **Rate Limit Hit Tracking**
   - Count 429 errors from Supabase
   - Track by endpoint/operation
   - Alert when threshold exceeded

2. **Request Rate Monitoring**
   - Track requests per minute
   - Monitor peak rates
   - Compare to Supabase limits

3. **User Impact Metrics**
   - Registration success rate
   - Authentication success rate
   - Error rate by error type

### Alert Thresholds

- **Warning:** 50% of Supabase limit
- **Critical:** 80% of Supabase limit
- **Action Required:** 90% of Supabase limit

---

## Future Considerations

### Short Term

1. ✅ Test mode implementation (done)
2. ✅ Graceful error handling (done)
3. ⏳ Monitoring dashboard (recommended)
4. ⏳ Alert system (recommended)

### Medium Term

1. **Request Queuing**
   - Queue registration requests
   - Process at sustainable rate
   - User feedback on queue

2. **Caching Strategy**
   - Cache authentication results
   - Reduce Supabase calls
   - Optimize token refresh

3. **Load Distribution**
   - Distribute requests over time
   - Implement request throttling
   - Use CDN where possible

### Long Term

1. **Supabase Pro Tier**
   - Upgrade if needed for production
   - Higher rate limits
   - Better support

2. **Alternative Auth Providers**
   - Consider alternatives if limits become issue
   - Multi-provider support
   - Fallback mechanisms

3. **Self-Hosted Auth**
   - Consider self-hosted solution
   - Full control over limits
   - Higher complexity

---

## Documentation References

- **Supabase Rate Limits:** https://supabase.com/docs/guides/platform/rate-limits
- **Supabase Pricing:** https://supabase.com/pricing
- **Test Mode Implementation:** `docs/execution/test_suite_final_status.md`
- **Rate Limiter Code:** `symphainy_platform/civic_systems/experience/middleware/rate_limiter.py`

---

## Summary

**Constraint:** Supabase rate limits (external service)  
**Impact:** User registration and authentication may be rate limited  
**Mitigation:** Test mode, graceful degradation, monitoring  
**Status:** ✅ **Known constraint - design consideration**

**Key Points:**
- Supabase limits are external and cannot be bypassed
- Test mode helps with application limits, not Supabase limits
- Some tests may fail due to Supabase limits (expected)
- Production may need Pro tier for higher limits
- Design around limits with queuing, caching, and optimization

---

**Last Updated:** January 17, 2026  
**Maintained By:** Platform Team  
**Review Frequency:** Quarterly or when limits change
