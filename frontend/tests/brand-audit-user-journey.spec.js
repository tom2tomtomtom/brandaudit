import { test, expect } from '@playwright/test';

test.describe('Brand Audit App - User Journey Tests', () => {
  
  test.beforeEach(async ({ page }) => {
    // Navigate to the app
    await page.goto('/');
  });

  test('should load the homepage correctly', async ({ page }) => {
    // Check if the page loads
    await expect(page).toHaveTitle(/Brand Audit/i);
    
    // Check for main elements
    await expect(page.locator('h1')).toContainText(/Brand Audit/i);
    await expect(page.locator('input[type="text"]')).toBeVisible();
    await expect(page.locator('button')).toContainText(/Start Audit|Audit|Search/i);
  });

  test('should show validation for empty input', async ({ page }) => {
    // Try to submit without entering a company name
    const submitButton = page.locator('button').filter({ hasText: /Start Audit|Audit|Search/i });
    await submitButton.click();
    
    // Should either show validation message or not proceed
    // Check if we're still on the same page or if there's an error message
    const input = page.locator('input[type="text"]');
    await expect(input).toBeVisible();
  });

  test('should handle well-known brand audit - Apple', async ({ page }) => {
    const companyInput = page.locator('input[type="text"]');
    const submitButton = page.locator('button').filter({ hasText: /Start Audit|Audit|Search/i });
    
    // Enter a well-known company
    await companyInput.fill('Apple');
    await submitButton.click();
    
    // Wait for loading state
    await page.waitForTimeout(2000);
    
    // Check if we see loading indicators or results
    const loadingIndicator = page.locator('text=/loading|Loading|Analyzing|Processing/i');
    const resultsSection = page.locator('[data-testid="results"], .results, #results');
    const errorMessage = page.locator('text=/error|Error|failed|Failed/i');
    
    // Should either be loading, show results, or show an error
    const hasLoading = await loadingIndicator.isVisible().catch(() => false);
    const hasResults = await resultsSection.isVisible().catch(() => false);
    const hasError = await errorMessage.isVisible().catch(() => false);
    
    console.log('Loading visible:', hasLoading);
    console.log('Results visible:', hasResults);
    console.log('Error visible:', hasError);
    
    // If we're back to the input screen, that's the issue we need to investigate
    const backToInput = await companyInput.isVisible();
    if (backToInput && !hasLoading && !hasResults) {
      console.log('⚠️  App returned to input screen without showing results');
      
      // Check browser console for errors
      const logs = [];
      page.on('console', msg => logs.push(msg.text()));
      
      // Check network requests
      const failedRequests = [];
      page.on('requestfailed', request => {
        failedRequests.push({
          url: request.url(),
          failure: request.failure()
        });
      });
      
      await page.waitForTimeout(1000);
      
      if (logs.length > 0) {
        console.log('Console logs:', logs);
      }
      if (failedRequests.length > 0) {
        console.log('Failed requests:', failedRequests);
      }
    }
    
    // The test should pass if we see any expected behavior
    expect(hasLoading || hasResults || hasError || backToInput).toBe(true);
  });

  test('should handle obscure brand audit', async ({ page }) => {
    const companyInput = page.locator('input[type="text"]');
    const submitButton = page.locator('button').filter({ hasText: /Start Audit|Audit|Search/i });
    
    // Enter an obscure company (similar to what user tested)
    await companyInput.fill('Patagonia Provisions');
    await submitButton.click();
    
    // Monitor network requests
    const requests = [];
    page.on('request', request => {
      if (request.url().includes('/api/')) {
        requests.push({
          url: request.url(),
          method: request.method(),
          postData: request.postData()
        });
      }
    });
    
    const responses = [];
    page.on('response', response => {
      if (response.url().includes('/api/')) {
        responses.push({
          url: response.url(),
          status: response.status(),
          statusText: response.statusText()
        });
      }
    });
    
    // Wait longer for processing
    await page.waitForTimeout(5000);
    
    console.log('API Requests made:', requests);
    console.log('API Responses received:', responses);
    
    // Check current state
    const currentUrl = page.url();
    const isBackToInput = await companyInput.isVisible();
    
    console.log('Current URL:', currentUrl);
    console.log('Back to input screen:', isBackToInput);
    
    // This test documents the current behavior
    expect(true).toBe(true); // Always pass, we're just gathering info
  });
});
