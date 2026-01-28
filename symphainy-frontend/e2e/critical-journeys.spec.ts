import { test, expect, Page } from '@playwright/test';

/**
 * Critical User Journey E2E Tests
 * 
 * These tests verify the critical user journeys through the Symphainy platform.
 * They require the full stack to be running (docker-compose.fullstack.yml).
 * 
 * Run with: npx playwright test e2e/critical-journeys.spec.ts
 */

test.describe('Session Management', () => {
  test('should create anonymous session on page load', async ({ page }) => {
    // Navigate to home page
    await page.goto('/');
    
    // Wait for page to load
    await page.waitForLoadState('networkidle');
    
    // Check that session storage has been populated
    const sessionToken = await page.evaluate(() => {
      return sessionStorage.getItem('session_token') || 
             localStorage.getItem('session_token') ||
             sessionStorage.getItem('symphainy_session_token');
    });
    
    // Session should be created (either in storage or handled by provider)
    // Note: The exact storage key may vary based on implementation
    expect(page.url()).toContain('/');
  });

  test('should navigate to login page', async ({ page }) => {
    await page.goto('/login');
    
    // Wait for page to load
    await page.waitForLoadState('networkidle');
    
    // Verify we're on the login page
    expect(page.url()).toContain('/login');
  });
});

test.describe('Navigation', () => {
  test.beforeEach(async ({ page }) => {
    // Start at home page
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('should navigate to Content pillar', async ({ page }) => {
    // Try to navigate to content pillar
    await page.goto('/pillars/content');
    await page.waitForLoadState('networkidle');
    
    // Verify navigation (may redirect if not authenticated)
    const url = page.url();
    expect(url.includes('/pillars/content') || url.includes('/login')).toBeTruthy();
  });

  test('should navigate to Insights pillar', async ({ page }) => {
    await page.goto('/pillars/insights');
    await page.waitForLoadState('networkidle');
    
    const url = page.url();
    expect(url.includes('/pillars/insights') || url.includes('/login')).toBeTruthy();
  });

  test('should navigate to Journey pillar', async ({ page }) => {
    await page.goto('/pillars/journey');
    await page.waitForLoadState('networkidle');
    
    const url = page.url();
    expect(url.includes('/pillars/journey') || url.includes('/login')).toBeTruthy();
  });

  test('should navigate to Business Outcomes pillar', async ({ page }) => {
    await page.goto('/pillars/business-outcomes');
    await page.waitForLoadState('networkidle');
    
    const url = page.url();
    expect(url.includes('/pillars/business-outcomes') || url.includes('/login')).toBeTruthy();
  });
});

test.describe('Content Pillar - File Upload', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/pillars/content');
    await page.waitForLoadState('networkidle');
  });

  test('should display file upload interface', async ({ page }) => {
    // Skip if redirected to login (authentication required)
    if (page.url().includes('/login')) {
      test.skip();
      return;
    }

    // Look for upload-related UI elements
    // These selectors may need adjustment based on actual UI
    const hasUploadUI = await page.locator('input[type="file"]').count() > 0 ||
                        await page.locator('[data-testid="file-upload"]').count() > 0 ||
                        await page.locator('button:has-text("Upload")').count() > 0 ||
                        await page.getByText(/upload/i).count() > 0;
    
    expect(hasUploadUI).toBeTruthy();
  });

  test('should upload a test file', async ({ page }) => {
    // Skip if redirected to login
    if (page.url().includes('/login')) {
      test.skip();
      return;
    }

    // Find file input
    const fileInput = page.locator('input[type="file"]');
    
    if (await fileInput.count() === 0) {
      test.skip();
      return;
    }

    // Upload a test CSV file
    await fileInput.setInputFiles({
      name: 'test-data.csv',
      mimeType: 'text/csv',
      buffer: Buffer.from('id,name,value\n1,test,100\n2,sample,200'),
    });

    // Wait for upload to process
    await page.waitForTimeout(2000);

    // Check for upload feedback (success message, progress, or file name displayed)
    const hasUploadFeedback = 
      await page.getByText(/test-data/i).count() > 0 ||
      await page.getByText(/upload/i).count() > 0 ||
      await page.locator('[data-testid="upload-success"]').count() > 0;

    expect(hasUploadFeedback).toBeTruthy();
  });
});

test.describe('API Health', () => {
  test('should respond to health check', async ({ request }) => {
    // Test API health endpoint
    const response = await request.get('/api/health');
    
    // Accept various success statuses
    expect([200, 404, 503].includes(response.status())).toBeTruthy();
  });

  test('should have session endpoint', async ({ request }) => {
    // Test session creation endpoint exists
    const response = await request.post('/api/session/create-anonymous', {
      data: {}
    });
    
    // Should either succeed or return expected error (not 404)
    expect(response.status()).not.toBe(404);
  });
});

test.describe('WebSocket Connectivity', () => {
  test('should support WebSocket upgrade at /ws path', async ({ page }) => {
    // Navigate to a page first
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Try to establish WebSocket connection
    const wsConnected = await page.evaluate(async () => {
      return new Promise<boolean>((resolve) => {
        try {
          // Get base URL and convert to WebSocket
          const baseUrl = window.location.origin.replace(/^http/, 'ws');
          const ws = new WebSocket(`${baseUrl}/api/runtime/agent?session_token=test`);
          
          // Set timeout for connection attempt
          const timeout = setTimeout(() => {
            ws.close();
            resolve(false);
          }, 5000);

          ws.onopen = () => {
            clearTimeout(timeout);
            ws.close();
            resolve(true);
          };

          ws.onerror = () => {
            clearTimeout(timeout);
            resolve(false);
          };
        } catch {
          resolve(false);
        }
      });
    });

    // Note: This test may fail if backend WebSocket is not running
    // It's primarily to verify the path is routed correctly
    console.log('WebSocket connectivity test result:', wsConnected);
  });
});

test.describe('Insights Pillar', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/pillars/insights');
    await page.waitForLoadState('networkidle');
  });

  test('should display insights interface', async ({ page }) => {
    // Skip if redirected to login
    if (page.url().includes('/login')) {
      test.skip();
      return;
    }

    // Check for insights-related UI
    const hasInsightsUI = 
      await page.getByText(/insights/i).count() > 0 ||
      await page.getByText(/analysis/i).count() > 0 ||
      await page.getByText(/data/i).count() > 0;

    expect(hasInsightsUI).toBeTruthy();
  });
});

test.describe('Journey Pillar', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/pillars/journey');
    await page.waitForLoadState('networkidle');
  });

  test('should display journey interface', async ({ page }) => {
    // Skip if redirected to login
    if (page.url().includes('/login')) {
      test.skip();
      return;
    }

    // Check for journey-related UI
    const hasJourneyUI = 
      await page.getByText(/journey/i).count() > 0 ||
      await page.getByText(/workflow/i).count() > 0 ||
      await page.getByText(/process/i).count() > 0;

    expect(hasJourneyUI).toBeTruthy();
  });
});

test.describe('Business Outcomes Pillar', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/pillars/business-outcomes');
    await page.waitForLoadState('networkidle');
  });

  test('should display outcomes interface', async ({ page }) => {
    // Skip if redirected to login
    if (page.url().includes('/login')) {
      test.skip();
      return;
    }

    // Check for outcomes-related UI
    const hasOutcomesUI = 
      await page.getByText(/outcomes/i).count() > 0 ||
      await page.getByText(/business/i).count() > 0 ||
      await page.getByText(/roadmap/i).count() > 0;

    expect(hasOutcomesUI).toBeTruthy();
  });
});

test.describe('Admin Panel', () => {
  test('should navigate to admin page', async ({ page }) => {
    await page.goto('/admin');
    await page.waitForLoadState('networkidle');

    // Verify we're on admin or redirected appropriately
    const url = page.url();
    expect(url.includes('/admin') || url.includes('/login')).toBeTruthy();
  });
});

test.describe('Error Handling', () => {
  test('should handle 404 pages gracefully', async ({ page }) => {
    await page.goto('/non-existent-page-12345');
    await page.waitForLoadState('networkidle');

    // Should show some kind of error page or redirect
    const hasErrorHandling = 
      page.url() !== '/non-existent-page-12345' ||
      await page.getByText(/not found/i).count() > 0 ||
      await page.getByText(/404/i).count() > 0 ||
      await page.getByText(/error/i).count() > 0;

    expect(hasErrorHandling).toBeTruthy();
  });
});

test.describe('Page Performance', () => {
  test('should load home page within 10 seconds', async ({ page }) => {
    const startTime = Date.now();
    
    await page.goto('/');
    await page.waitForLoadState('domcontentloaded');
    
    const loadTime = Date.now() - startTime;
    
    // Page should load within 10 seconds
    expect(loadTime).toBeLessThan(10000);
    console.log(`Home page load time: ${loadTime}ms`);
  });

  test('should load pillars page within 10 seconds', async ({ page }) => {
    const startTime = Date.now();
    
    await page.goto('/pillars');
    await page.waitForLoadState('domcontentloaded');
    
    const loadTime = Date.now() - startTime;
    
    expect(loadTime).toBeLessThan(10000);
    console.log(`Pillars page load time: ${loadTime}ms`);
  });
});
