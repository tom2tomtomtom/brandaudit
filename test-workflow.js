#!/usr/bin/env node

const { chromium } = require('playwright');

async function testWorkflow() {
  console.log('🎯 TESTING AI BRAND AUDIT TOOL WORKFLOW');
  console.log('========================================');
  
  const browser = await chromium.launch({ headless: false, slowMo: 1000 });
  const page = await browser.newPage();
  
  const errors = [];
  const apiCalls = [];
  
  page.on('console', msg => {
    if (msg.type() === 'error') {
      errors.push(msg.text());
      console.log('❌ Console Error:', msg.text());
    }
  });
  
  page.on('request', request => {
    if (request.url().includes('/api/')) {
      apiCalls.push(request.url());
      console.log('📞 API Call:', request.url());
    }
  });
  
  try {
    // 1. Load Application
    console.log('\n📍 STEP 1: Loading Application');
    await page.goto('http://localhost:3000', { waitUntil: 'networkidle' });
    const heading = await page.locator('h1').first().textContent();
    console.log('✅ Application loaded:', heading);
    
    // 2. Test Brand Search
    console.log('\n📍 STEP 2: Testing Brand Search');
    const searchInput = page.locator('[data-testid="brand-search"]');
    await searchInput.fill('Apple');
    console.log('✅ Entered brand name: Apple');
    
    const searchButton = page.locator('button:has-text("Search Brand")');
    await searchButton.click();
    console.log('✅ Clicked search button');
    
    // Wait for next step or error
    await page.waitForTimeout(3000);
    
    // Check if we moved to step 2 (file upload)
    const uploadSection = await page.locator('[data-testid="upload"]').isVisible();
    if (uploadSection) {
      console.log('✅ Moved to file upload step');
      
      // 3. Test File Upload Step
      console.log('\n📍 STEP 3: Testing File Upload');
      const skipButton = page.locator('button:has-text("Skip Upload")');
      await skipButton.click();
      console.log('✅ Skipped file upload');
      
      await page.waitForTimeout(2000);
      
      // 4. Test Analysis Options
      console.log('\n📍 STEP 4: Testing Analysis Options');
      const analysisForm = await page.locator('[data-testid="analysis-form"]').isVisible();
      if (analysisForm) {
        console.log('✅ Analysis form visible');
        
        const startButton = page.locator('button:has-text("Start Analysis")');
        await startButton.click();
        console.log('✅ Started analysis');
        
        await page.waitForTimeout(5000);
        
        // 5. Check for Results
        console.log('\n📍 STEP 5: Checking Results');
        const resultsVisible = await page.locator('[data-testid="results"]').isVisible();
        if (resultsVisible) {
          console.log('✅ Results section visible');
          
          // Check for actual data
          const scoreElements = await page.locator('.text-2xl.font-bold').count();
          console.log(`✅ Found ${scoreElements} score elements`);
        } else {
          console.log('⏳ Analysis still processing...');
        }
      } else {
        console.log('❌ Analysis form not found');
      }
    } else {
      console.log('❌ Did not move to upload step - brand search may have failed');
    }
    
    // Test API Health separately
    console.log('\n📍 STEP 6: Testing API Health');
    const healthTest = await page.evaluate(async () => {
      try {
        const response = await fetch('https://207d-220-244-77-193.ngrok-free.app/api/health', {
          headers: {
            'ngrok-skip-browser-warning': 'true'
          }
        });
        const data = await response.json();
        return { 
          success: true, 
          service: data.service,
          api_keys: data.api_keys_configured,
          keys_loaded: Object.values(data.api_keys_configured || {}).filter(v => v).length
        };
      } catch (error) {
        return { success: false, error: error.message };
      }
    });
    
    if (healthTest.success) {
      console.log('✅ API Health Check Successful');
      console.log('✅ Service:', healthTest.service);
      console.log('✅ API Keys Loaded:', healthTest.keys_loaded, 'out of 4');
    } else {
      console.log('❌ API Health Check Failed:', healthTest.error);
    }
    
    // Final Assessment
    console.log('\n🎯 WORKFLOW ASSESSMENT');
    console.log('======================');
    
    const totalAPICalls = apiCalls.length;
    const hasErrors = errors.length > 0;
    
    console.log(`📞 Total API Calls: ${totalAPICalls}`);
    console.log(`❌ JavaScript Errors: ${errors.length}`);
    console.log(`✅ Backend Health: ${healthTest.success ? 'OK' : 'FAILED'}`);
    console.log(`🔑 API Keys: ${healthTest.keys_loaded || 0}/4`);
    
    // Performance Check
    const metrics = await page.evaluate(() => {
      const navigation = performance.getEntriesByType('navigation')[0];
      return {
        loadTime: Math.round(navigation.loadEventEnd - navigation.fetchStart),
        domReady: Math.round(navigation.domContentLoadedEventEnd - navigation.fetchStart)
      };
    });
    
    console.log(`⚡ Load Time: ${metrics.loadTime}ms`);
    console.log(`⚡ DOM Ready: ${metrics.domReady}ms`);
    
    await page.screenshot({ path: 'workflow-test.png', fullPage: true });
    console.log('\n📸 Screenshot saved as workflow-test.png');
    
  } catch (error) {
    console.log('❌ Test failed:', error.message);
  } finally {
    await browser.close();
  }
}

testWorkflow();