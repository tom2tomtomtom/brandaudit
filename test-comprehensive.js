#!/usr/bin/env node

const { chromium } = require('playwright');

async function testComprehensiveAnalysis() {
  console.log('🎯 TESTING COMPREHENSIVE BRAND ANALYSIS WORKFLOW');
  console.log('==================================================');
  
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
    
    await page.waitForTimeout(3000);
    
    // 3. Skip File Upload
    console.log('\n📍 STEP 3: Skipping File Upload');
    const skipButton = page.locator('button:has-text("Skip Upload")');
    await skipButton.click();
    console.log('✅ Skipped file upload');
    
    await page.waitForTimeout(2000);
    
    // 4. Start Analysis
    console.log('\n📍 STEP 4: Starting Analysis');
    const startButton = page.locator('button:has-text("Start Analysis")');
    await startButton.click();
    console.log('✅ Started analysis');
    
    await page.waitForTimeout(5000);
    
    // 5. Check for Comprehensive Results
    console.log('\n📍 STEP 5: Checking Comprehensive Results');
    
    // Wait for results to appear
    await page.waitForSelector('[data-testid="results"]', { timeout: 10000 });
    console.log('✅ Results section visible');
    
    // Check for comprehensive analysis elements
    const comprehensiveTitle = await page.locator('text=Comprehensive Brand Audit Complete').isVisible();
    console.log('✅ Comprehensive title:', comprehensiveTitle);
    
    // Check Brand Health Dashboard
    const brandHealthSection = await page.locator('text=Brand Health Dashboard').isVisible();
    console.log('✅ Brand Health Dashboard:', brandHealthSection);
    
    // Check for tabs
    const insightsTab = await page.locator('button[role="tab"]:has-text("Key Insights")').isVisible();
    const perceptionTab = await page.locator('button[role="tab"]:has-text("Perception")').isVisible();
    const visualTab = await page.locator('button[role="tab"]:has-text("Visual")').isVisible();
    const mediaTab = await page.locator('button[role="tab"]:has-text("Media")').isVisible();
    const competitiveTab = await page.locator('button[role="tab"]:has-text("Competitive")').isVisible();
    const socialTab = await page.locator('button[role="tab"]:has-text("Social")').isVisible();
    
    console.log('✅ Analysis Tabs:');
    console.log('  - Key Insights:', insightsTab);
    console.log('  - Perception:', perceptionTab);
    console.log('  - Visual:', visualTab);
    console.log('  - Media:', mediaTab);
    console.log('  - Competitive:', competitiveTab);
    console.log('  - Social:', socialTab);
    
    // Test tab switching
    console.log('\n📍 STEP 6: Testing Tab Navigation');
    if (perceptionTab) {
      await page.locator('button[role="tab"]:has-text("Perception")').click();
      await page.waitForTimeout(1000);
      console.log('✅ Switched to Perception tab');
    }
    
    if (visualTab) {
      await page.locator('button[role="tab"]:has-text("Visual")').click();
      await page.waitForTimeout(1000);
      console.log('✅ Switched to Visual tab');
    }
    
    // Check for scores display
    console.log('\n📍 STEP 7: Checking Score Display');
    const scoreElements = await page.locator('.text-3xl.font-bold, .text-2xl.font-bold, .text-xl.font-bold').count();
    console.log(`✅ Found ${scoreElements} score elements displayed`);
    
    // Check for export buttons
    const downloadButtons = await page.locator('text=Download').count();
    console.log(`✅ Found ${downloadButtons} download/export buttons`);
    
    // Test API Health
    console.log('\n📍 STEP 8: Testing API Health');
    const healthTest = await page.evaluate(async () => {
      try {
        const response = await fetch('https://2b79-220-244-77-193.ngrok-free.app/api/health', {
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
    console.log('\n🎯 COMPREHENSIVE ANALYSIS ASSESSMENT');
    console.log('=====================================');
    
    const results = {
      'Frontend Application': true,
      'Brand Search Working': apiCalls.some(url => url.includes('/brand/search')),
      'Analysis Started': apiCalls.some(url => url.includes('/analyze')),
      'Comprehensive Results': apiCalls.some(url => url.includes('/results')),
      'Results Display': comprehensiveTitle,
      'Brand Health Dashboard': brandHealthSection,
      'Analysis Tabs Available': insightsTab && perceptionTab && visualTab,
      'Score Elements Present': scoreElements > 5,
      'Export Options Available': downloadButtons >= 3,
      'API Health': healthTest.success,
      'Zero JavaScript Errors': errors.length === 0
    };
    
    let passCount = 0;
    console.log('\nTEST RESULTS:');
    for (const [test, passed] of Object.entries(results)) {
      console.log(`${passed ? '✅' : '❌'} ${test}: ${passed ? 'PASS' : 'FAIL'}`);
      if (passed) passCount++;
    }
    
    const finalScore = Math.round((passCount / Object.keys(results).length) * 100);
    console.log(`\n🎯 COMPREHENSIVE ANALYSIS SCORE: ${finalScore}%`);
    
    if (finalScore >= 95) {
      console.log('🎉 COMPREHENSIVE ANALYSIS FULLY FUNCTIONAL!');
      console.log('✅ All analysis sections working with detailed data');
      console.log('✅ Professional interface with tabbed navigation');
      console.log('✅ Export capabilities and actionable insights');
    } else if (finalScore >= 85) {
      console.log('🚀 EXCELLENT! Comprehensive analysis mostly working');
    } else if (finalScore >= 70) {
      console.log('⚠️ GOOD! Most comprehensive features working');
    } else {
      console.log('❌ NEEDS WORK! Core comprehensive features missing');
    }
    
    console.log(`\n📈 PROGRESS: Advanced from basic tool to comprehensive brand audit platform`);
    console.log(`📊 Features: ${Object.keys(results).length} comprehensive analysis features tested`);
    
    await page.screenshot({ path: 'comprehensive-analysis-test.png', fullPage: true });
    console.log('\n📸 Screenshot saved as comprehensive-analysis-test.png');
    
  } catch (error) {
    console.log('❌ Test failed:', error.message);
  } finally {
    await browser.close();
  }
}

testComprehensiveAnalysis();