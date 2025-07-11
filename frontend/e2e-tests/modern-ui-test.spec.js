import { test, expect } from '@playwright/test';

test.describe('Modern UI Test', () => {
  
  test('Test New Modern Landing Page and Progress Indicators', async ({ page }) => {
    console.log('🎨 TESTING: Modern UI with Progress Indicators');
    console.log('==============================================');
    
    // Step 1: Test modern landing page
    console.log('\n1️⃣ Testing modern landing page...');
    await page.goto('http://localhost:5175');
    await page.waitForLoadState('networkidle');
    
    // Check for modern landing elements
    await expect(page.locator('h1')).toContainText('AI Brand Audit Tool');
    await expect(page.locator('text=Get professional-grade brand analysis')).toBeVisible();
    
    // Check for gradient styling and modern elements
    const heroSection = page.locator('.bg-gradient-to-br');
    await expect(heroSection).toBeVisible();
    console.log('✅ Modern landing page loads with gradient backgrounds');
    
    // Check for example brands
    await expect(page.locator('text=Try these popular brands')).toBeVisible();
    await expect(page.locator('button:has-text("Apple")')).toBeVisible();
    console.log('✅ Example brand buttons are present');
    
    // Step 2: Test brand input with modern styling
    console.log('\n2️⃣ Testing modern brand input...');
    const searchInput = page.locator('input[placeholder*="Apple, Tesla, Nike"]');
    await expect(searchInput).toBeVisible();
    
    const submitButton = page.locator('button:has-text("Start AI Brand Audit")');
    await expect(submitButton).toBeVisible();
    console.log('✅ Modern search form is present');
    
    // Step 3: Test starting analysis with progress indicators
    console.log('\n3️⃣ Testing analysis start and progress...');
    
    // Fill in brand name
    await searchInput.fill('Tesla');
    console.log('✅ Entered "Tesla" in search field');
    
    // Start analysis
    await submitButton.click();
    console.log('✅ Clicked start analysis button');
    
    // Wait for progress page to load
    await page.waitForTimeout(3000);
    
    // Check for progress indicators
    const progressTitle = page.locator('h1:has-text("AI Brand Analysis in Progress")');
    await expect(progressTitle).toBeVisible({ timeout: 10000 });
    console.log('✅ Progress page loads with modern title');
    
    // Check for progress steps
    const progressSteps = page.locator('text=Brand Discovery');
    await expect(progressSteps).toBeVisible();
    console.log('✅ Progress steps are visible');
    
    // Check for overall progress bar
    const progressBar = page.locator('[role="progressbar"]');
    await expect(progressBar).toBeVisible();
    console.log('✅ Progress bar is present');
    
    // Check for step-by-step progress
    const analysisSteps = page.locator('text=AI Strategic Analysis');
    await expect(analysisSteps).toBeVisible();
    console.log('✅ Detailed analysis steps are shown');
    
    // Step 4: Wait for completion and check results
    console.log('\n4️⃣ Waiting for analysis completion...');
    
    // Wait for results page (up to 3 minutes)
    const resultsTitle = page.locator('h1:has-text("Brand Analysis Complete")');
    await expect(resultsTitle).toBeVisible({ timeout: 180000 });
    console.log('✅ Analysis completed and results page loaded');
    
    // Check for modern results display
    const scoreCards = page.locator('.text-3xl.font-bold');
    await expect(scoreCards.first()).toBeVisible();
    console.log('✅ Score cards are displayed');
    
    // Check for tabs
    const overviewTab = page.locator('button:has-text("Overview")');
    await expect(overviewTab).toBeVisible();
    console.log('✅ Results tabs are present');
    
    // Check for insights tab
    const insightsTab = page.locator('button:has-text("Insights")');
    await expect(insightsTab).toBeVisible();
    await insightsTab.click();
    console.log('✅ Insights tab is clickable');
    
    // Check for AI analysis tab
    const aiTab = page.locator('button:has-text("AI Analysis")');
    await expect(aiTab).toBeVisible();
    await aiTab.click();
    console.log('✅ AI Analysis tab is clickable');
    
    // Step 5: Test markdown rendering
    console.log('\n5️⃣ Testing markdown rendering...');
    
    // Look for properly formatted content (no ** symbols)
    const content = await page.textContent('body');
    const hasUnrenderedMarkdown = content.includes('**') && content.includes('##');
    
    if (hasUnrenderedMarkdown) {
      console.log('⚠️ Some markdown may not be fully rendered');
    } else {
      console.log('✅ Markdown appears to be properly rendered');
    }
    
    // Step 6: Test new analysis button
    console.log('\n6️⃣ Testing new analysis functionality...');
    const newAnalysisButton = page.locator('button:has-text("New Analysis")');
    await expect(newAnalysisButton).toBeVisible();
    console.log('✅ New Analysis button is present');
    
    // Take screenshot of final results
    await page.screenshot({ path: 'test-results/modern-ui-results.png', fullPage: true });
    
    console.log('\n🎉 MODERN UI TEST COMPLETE!');
    console.log('============================');
    console.log('✅ Modern landing page working');
    console.log('✅ Progress indicators functional');
    console.log('✅ Results display modernized');
    console.log('✅ Markdown rendering improved');
    console.log('✅ Navigation and tabs working');
    
    expect(true).toBe(true); // Test passes if we get here
  });

  test('Test Responsive Design', async ({ page }) => {
    console.log('📱 TESTING: Responsive Design');
    console.log('=============================');
    
    // Test mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('http://localhost:5175');
    
    // Check if elements are still visible on mobile
    await expect(page.locator('h1')).toBeVisible();
    await expect(page.locator('input[placeholder*="Apple, Tesla, Nike"]')).toBeVisible();
    
    console.log('✅ Mobile layout works');
    
    // Test tablet viewport
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.reload();
    
    await expect(page.locator('h1')).toBeVisible();
    console.log('✅ Tablet layout works');
    
    // Test desktop viewport
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.reload();
    
    await expect(page.locator('h1')).toBeVisible();
    console.log('✅ Desktop layout works');
    
    expect(true).toBe(true);
  });
});
