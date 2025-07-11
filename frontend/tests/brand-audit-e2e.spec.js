import { test, expect } from '@playwright/test';

test.describe('Brand Audit App - Complete User Journey', () => {
  
  test.beforeEach(async ({ page }) => {
    // Navigate to the app
    await page.goto('/');
  });

  test('should load the homepage and show brand audit interface', async ({ page }) => {
    // Check if the main heading is visible
    await expect(page.locator('h1')).toContainText('Brand Audit');
    
    // Check if the brand input field is present
    await expect(page.locator('input[placeholder*="brand"]')).toBeVisible();
    
    // Check if the analyze button is present
    await expect(page.locator('button')).toContainText('Analyze');
  });

  test('should perform complete brand analysis workflow', async ({ page }) => {
    // Test brand: Nike (well-known brand for reliable results)
    const testBrand = 'Nike';
    
    // Step 1: Enter brand name
    await page.fill('input[placeholder*="brand"]', testBrand);
    
    // Step 2: Click analyze button
    await page.click('button:has-text("Analyze")');
    
    // Step 3: Wait for analysis to complete (may take 30-60 seconds)
    await expect(page.locator('text=Analysis complete')).toBeVisible({ timeout: 120000 });
    
    // Step 4: Verify results are displayed
    await expect(page.locator('text=Brand Health Score')).toBeVisible();
    
    // Step 5: Check if tabs are present
    await expect(page.locator('[role="tab"]')).toHaveCount(5); // Overview, Visual, Insights, Analysis, Competitive
    
    // Step 6: Test tab navigation
    await page.click('[role="tab"]:has-text("Visual")');
    await expect(page.locator('text=Visual Analysis')).toBeVisible();
    
    await page.click('[role="tab"]:has-text("Insights")');
    await expect(page.locator('text=Strategic Insights')).toBeVisible();
    
    await page.click('[role="tab"]:has-text("Competitive")');
    await expect(page.locator('text=Competitive Analysis')).toBeVisible();
  });

  test('should display visual analysis components', async ({ page }) => {
    // Perform analysis
    await page.fill('input[placeholder*="brand"]', 'Apple');
    await page.click('button:has-text("Analyze")');
    
    // Wait for completion
    await expect(page.locator('text=Analysis complete')).toBeVisible({ timeout: 120000 });
    
    // Navigate to Visual tab
    await page.click('[role="tab"]:has-text("Visual")');
    
    // Check for visual components
    await expect(page.locator('text=Screenshots')).toBeVisible();
    await expect(page.locator('text=Color Palette')).toBeVisible();
    await expect(page.locator('text=Visual Metrics')).toBeVisible();
    
    // Check if screenshots are loaded
    await expect(page.locator('img[alt*="screenshot"]')).toHaveCount(5, { timeout: 30000 });
    
    // Check if color swatches are displayed
    await expect(page.locator('[data-testid="color-swatch"]')).toHaveCountGreaterThan(0);
  });

  test('should show competitor analysis when available', async ({ page }) => {
    // Perform analysis
    await page.fill('input[placeholder*="brand"]', 'Tesla');
    await page.click('button:has-text("Analyze")');
    
    // Wait for completion
    await expect(page.locator('text=Analysis complete')).toBeVisible({ timeout: 120000 });
    
    // Navigate to Competitive tab
    await page.click('[role="tab"]:has-text("Competitive")');
    
    // Check for competitive analysis components
    await expect(page.locator('text=Competitive Analysis')).toBeVisible();
    
    // Should show either competitor data or message about API requirements
    const hasCompetitors = await page.locator('text=competitors identified').isVisible();
    const hasApiMessage = await page.locator('text=API').isVisible();
    
    expect(hasCompetitors || hasApiMessage).toBeTruthy();
  });

  test('should display campaign analysis', async ({ page }) => {
    // Perform analysis
    await page.fill('input[placeholder*="brand"]', 'Coca-Cola');
    await page.click('button:has-text("Analyze")');
    
    // Wait for completion
    await expect(page.locator('text=Analysis complete')).toBeVisible({ timeout: 120000 });
    
    // Navigate to Insights tab (where campaign analysis is shown)
    await page.click('[role="tab"]:has-text("Insights")');
    
    // Check for campaign analysis components
    await expect(page.locator('text=Campaign')).toBeVisible();
  });

  test('should handle errors gracefully', async ({ page }) => {
    // Test with invalid brand name
    await page.fill('input[placeholder*="brand"]', '');
    await page.click('button:has-text("Analyze")');
    
    // Should show validation error
    await expect(page.locator('text=required')).toBeVisible();
    
    // Test with very long brand name
    await page.fill('input[placeholder*="brand"]', 'A'.repeat(100));
    await page.click('button:has-text("Analyze")');
    
    // Should handle gracefully (either process or show appropriate message)
    await page.waitForTimeout(5000);
    
    // Should not crash the app
    await expect(page.locator('body')).toBeVisible();
  });

  test('should be responsive on mobile devices', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Check if interface adapts to mobile
    await expect(page.locator('input[placeholder*="brand"]')).toBeVisible();
    await expect(page.locator('button:has-text("Analyze")')).toBeVisible();
    
    // Perform analysis on mobile
    await page.fill('input[placeholder*="brand"]', 'Nike');
    await page.click('button:has-text("Analyze")');
    
    // Wait for completion
    await expect(page.locator('text=Analysis complete')).toBeVisible({ timeout: 120000 });
    
    // Check if tabs work on mobile
    await page.click('[role="tab"]:has-text("Visual")');
    await expect(page.locator('text=Visual Analysis')).toBeVisible();
    
    // Check if images are responsive
    const screenshots = page.locator('img[alt*="screenshot"]');
    if (await screenshots.count() > 0) {
      const firstImage = screenshots.first();
      const boundingBox = await firstImage.boundingBox();
      expect(boundingBox.width).toBeLessThanOrEqual(375);
    }
  });

  test('should show loading states during analysis', async ({ page }) => {
    // Start analysis
    await page.fill('input[placeholder*="brand"]', 'Microsoft');
    await page.click('button:has-text("Analyze")');
    
    // Check for loading indicators
    await expect(page.locator('text=Analyzing')).toBeVisible();
    
    // Should show progress or loading spinner
    const hasSpinner = await page.locator('[data-testid="loading-spinner"]').isVisible();
    const hasProgress = await page.locator('text=progress').isVisible();
    const hasAnalyzing = await page.locator('text=Analyzing').isVisible();
    
    expect(hasSpinner || hasProgress || hasAnalyzing).toBeTruthy();
    
    // Wait for completion
    await expect(page.locator('text=Analysis complete')).toBeVisible({ timeout: 120000 });
    
    // Loading states should be gone
    await expect(page.locator('text=Analyzing')).not.toBeVisible();
  });

  test('should display brand health scores', async ({ page }) => {
    // Perform analysis
    await page.fill('input[placeholder*="brand"]', 'Google');
    await page.click('button:has-text("Analyze")');
    
    // Wait for completion
    await expect(page.locator('text=Analysis complete')).toBeVisible({ timeout: 120000 });
    
    // Check for score displays
    await expect(page.locator('text=Score')).toBeVisible();
    
    // Should show numerical scores
    const scorePattern = /\d+/;
    await expect(page.locator('text=' + scorePattern)).toBeVisible();
    
    // Check for score categories
    await expect(page.locator('text=Visual')).toBeVisible();
    await expect(page.locator('text=Brand')).toBeVisible();
  });

  test('should allow multiple brand analyses', async ({ page }) => {
    // First analysis
    await page.fill('input[placeholder*="brand"]', 'Amazon');
    await page.click('button:has-text("Analyze")');
    await expect(page.locator('text=Analysis complete')).toBeVisible({ timeout: 120000 });
    
    // Clear and do second analysis
    await page.fill('input[placeholder*="brand"]', '');
    await page.fill('input[placeholder*="brand"]', 'Netflix');
    await page.click('button:has-text("Analyze")');
    await expect(page.locator('text=Analysis complete')).toBeVisible({ timeout: 120000 });
    
    // Should show Netflix results
    await expect(page.locator('text=Netflix')).toBeVisible();
  });

  test('should handle network failures gracefully', async ({ page }) => {
    // Simulate offline condition
    await page.context().setOffline(true);
    
    // Try to perform analysis
    await page.fill('input[placeholder*="brand"]', 'Offline Test');
    await page.click('button:has-text("Analyze")');
    
    // Should show appropriate error message
    await expect(page.locator('text=error')).toBeVisible({ timeout: 30000 });
    
    // Restore connection
    await page.context().setOffline(false);
    
    // Should be able to retry
    await page.click('button:has-text("Analyze")');
    await page.waitForTimeout(5000);
    
    // App should still be functional
    await expect(page.locator('body')).toBeVisible();
  });

});

test.describe('Brand Audit App - Visual Components', () => {
  
  test('should display color palette correctly', async ({ page }) => {
    await page.goto('/');
    
    // Perform analysis
    await page.fill('input[placeholder*="brand"]', 'Spotify');
    await page.click('button:has-text("Analyze")');
    await expect(page.locator('text=Analysis complete')).toBeVisible({ timeout: 120000 });
    
    // Navigate to Visual tab
    await page.click('[role="tab"]:has-text("Visual")');
    
    // Check color palette display
    const colorSwatches = page.locator('[data-testid="color-swatch"]');
    if (await colorSwatches.count() > 0) {
      // Check if colors have proper styling
      const firstSwatch = colorSwatches.first();
      const backgroundColor = await firstSwatch.evaluate(el => 
        window.getComputedStyle(el).backgroundColor
      );
      expect(backgroundColor).not.toBe('rgba(0, 0, 0, 0)'); // Should have actual color
      
      // Check if hex codes are displayed
      await expect(page.locator('text=#')).toBeVisible();
    }
  });

  test('should display screenshots in gallery format', async ({ page }) => {
    await page.goto('/');
    
    // Perform analysis
    await page.fill('input[placeholder*="brand"]', 'Airbnb');
    await page.click('button:has-text("Analyze")');
    await expect(page.locator('text=Analysis complete')).toBeVisible({ timeout: 120000 });
    
    // Navigate to Visual tab
    await page.click('[role="tab"]:has-text("Visual")');
    
    // Check screenshot gallery
    const screenshots = page.locator('img[alt*="screenshot"]');
    if (await screenshots.count() > 0) {
      // Click on first screenshot to test modal
      await screenshots.first().click();
      
      // Should open modal or enlarged view
      await page.waitForTimeout(1000);
      
      // Check if image is enlarged or modal is open
      const modal = page.locator('[role="dialog"]');
      const enlargedImage = page.locator('img[style*="scale"]');
      
      const hasModal = await modal.isVisible();
      const hasEnlarged = await enlargedImage.isVisible();
      
      expect(hasModal || hasEnlarged).toBeTruthy();
    }
  });

});

test.describe('Brand Audit App - Performance', () => {
  
  test('should load within acceptable time', async ({ page }) => {
    const startTime = Date.now();

    await page.goto('/');
    await expect(page.locator('h1')).toBeVisible();
    
    const loadTime = Date.now() - startTime;
    expect(loadTime).toBeLessThan(5000); // Should load within 5 seconds
  });

  test('should handle large brand analysis efficiently', async ({ page }) => {
    await page.goto('/');
    
    const startTime = Date.now();
    
    // Perform analysis
    await page.fill('input[placeholder*="brand"]', 'McDonald\'s');
    await page.click('button:has-text("Analyze")');
    await expect(page.locator('text=Analysis complete')).toBeVisible({ timeout: 180000 });
    
    const analysisTime = Date.now() - startTime;
    console.log(`Analysis completed in ${analysisTime}ms`);
    
    // Should complete within reasonable time (3 minutes max)
    expect(analysisTime).toBeLessThan(180000);
    
    // Check if all components loaded properly
    await page.click('[role="tab"]:has-text("Visual")');
    await expect(page.locator('text=Visual Analysis')).toBeVisible();
    
    await page.click('[role="tab"]:has-text("Insights")');
    await expect(page.locator('text=Strategic Insights')).toBeVisible();
  });

});
