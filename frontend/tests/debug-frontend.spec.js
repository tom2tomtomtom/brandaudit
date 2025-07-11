import { test, expect } from '@playwright/test';

test.describe('Frontend Debug Tests', () => {
  
  test('should capture all network activity and console logs', async ({ page }) => {
    // Capture console logs
    const consoleLogs = [];
    page.on('console', msg => {
      consoleLogs.push({
        type: msg.type(),
        text: msg.text(),
        location: msg.location()
      });
    });

    // Capture network requests
    const networkRequests = [];
    page.on('request', request => {
      networkRequests.push({
        url: request.url(),
        method: request.method(),
        headers: request.headers(),
        postData: request.postData()
      });
    });

    // Capture network responses
    const networkResponses = [];
    page.on('response', response => {
      networkResponses.push({
        url: response.url(),
        status: response.status(),
        statusText: response.statusText(),
        headers: response.headers()
      });
    });

    // Capture failed requests
    const failedRequests = [];
    page.on('requestfailed', request => {
      failedRequests.push({
        url: request.url(),
        method: request.method(),
        failure: request.failure()
      });
    });

    // Navigate to the app
    await page.goto('/');
    
    // Wait for initial load
    await page.waitForTimeout(2000);
    
    console.log('=== INITIAL PAGE LOAD ===');
    console.log('Console logs:', consoleLogs);
    console.log('Network requests:', networkRequests.filter(r => !r.url.includes('vite') && !r.url.includes('node_modules')));
    
    // Clear logs for the test
    consoleLogs.length = 0;
    networkRequests.length = 0;
    networkResponses.length = 0;
    failedRequests.length = 0;

    // Find input and button
    const companyInput = page.locator('input[type="text"]');
    const submitButton = page.locator('button').filter({ hasText: /Start Audit|Audit|Search/i });
    
    await expect(companyInput).toBeVisible();
    await expect(submitButton).toBeVisible();
    
    // Enter company name and submit
    console.log('=== ENTERING COMPANY NAME ===');
    await companyInput.fill('Patagonia Provisions');
    
    console.log('=== CLICKING SUBMIT BUTTON ===');
    await submitButton.click();
    
    // Wait and monitor for 10 seconds
    console.log('=== MONITORING FOR 10 SECONDS ===');
    await page.waitForTimeout(10000);
    
    // Log all captured data
    console.log('=== FINAL RESULTS ===');
    console.log('Console logs during test:', consoleLogs);
    console.log('Network requests during test:', networkRequests);
    console.log('Network responses during test:', networkResponses);
    console.log('Failed requests during test:', failedRequests);
    
    // Check current page state
    const currentUrl = page.url();
    const inputVisible = await companyInput.isVisible();
    const inputValue = await companyInput.inputValue();
    
    console.log('Current URL:', currentUrl);
    console.log('Input still visible:', inputVisible);
    console.log('Input value:', inputValue);
    
    // Check for any error elements
    const errorElements = await page.locator('text=/error|Error|failed|Failed/i').all();
    console.log('Error elements found:', errorElements.length);
    
    // Check for loading elements
    const loadingElements = await page.locator('text=/loading|Loading|Analyzing|Processing/i').all();
    console.log('Loading elements found:', loadingElements.length);
    
    // Check for results elements
    const resultElements = await page.locator('[data-testid="results"], .results, #results').all();
    console.log('Result elements found:', resultElements.length);
    
    // Take a screenshot for debugging
    await page.screenshot({ path: 'debug-screenshot.png', fullPage: true });
    
    // This test always passes - it's just for debugging
    expect(true).toBe(true);
  });

  test('should test form submission step by step', async ({ page }) => {
    await page.goto('/');
    
    // Step 1: Check initial state
    console.log('=== STEP 1: INITIAL STATE ===');
    const companyInput = page.locator('input[type="text"]');
    const submitButton = page.locator('button').filter({ hasText: /Start Audit|Audit|Search/i });
    
    await expect(companyInput).toBeVisible();
    await expect(submitButton).toBeVisible();
    
    const initialInputValue = await companyInput.inputValue();
    console.log('Initial input value:', initialInputValue);
    
    // Step 2: Fill input
    console.log('=== STEP 2: FILLING INPUT ===');
    await companyInput.fill('Test Company');
    
    const filledInputValue = await companyInput.inputValue();
    console.log('Filled input value:', filledInputValue);
    expect(filledInputValue).toBe('Test Company');
    
    // Step 3: Check button state
    console.log('=== STEP 3: BUTTON STATE ===');
    const buttonEnabled = await submitButton.isEnabled();
    const buttonText = await submitButton.textContent();
    console.log('Button enabled:', buttonEnabled);
    console.log('Button text:', buttonText);
    
    // Step 4: Click button
    console.log('=== STEP 4: CLICKING BUTTON ===');
    await submitButton.click();
    
    // Step 5: Check immediate response
    console.log('=== STEP 5: IMMEDIATE RESPONSE ===');
    await page.waitForTimeout(1000);
    
    const afterClickInputValue = await companyInput.inputValue();
    const afterClickInputVisible = await companyInput.isVisible();
    console.log('After click input value:', afterClickInputValue);
    console.log('After click input visible:', afterClickInputVisible);
    
    // Step 6: Wait for any changes
    console.log('=== STEP 6: WAITING FOR CHANGES ===');
    await page.waitForTimeout(5000);
    
    const finalInputValue = await companyInput.inputValue();
    const finalInputVisible = await companyInput.isVisible();
    console.log('Final input value:', finalInputValue);
    console.log('Final input visible:', finalInputVisible);
    
    expect(true).toBe(true);
  });
});
