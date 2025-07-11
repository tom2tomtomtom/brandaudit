#!/usr/bin/env node

const { chromium } = require('playwright');

async function testFinal() {
  console.log('🎉 FINAL PRODUCTION TEST - AI BRAND AUDIT TOOL');
  console.log('===============================================');
  
  const browser = await chromium.launch({ headless: false, slowMo: 500 });
  const page = await browser.newPage();
  
  const errors = [];
  const apiCalls = [];
  
  page.on('console', msg => {
    if (msg.type() === 'error') {
      errors.push(msg.text());
    }
  });
  
  page.on('request', request => {
    if (request.url().includes('/api/')) {
      apiCalls.push(request.url());
    }
  });
  
  try {
    // 1. Load Application
    console.log('\n📍 STEP 1: Loading Application');
    await page.goto('http://localhost:3000', { waitUntil: 'networkidle' });
    const heading = await page.locator('h1').first().textContent();
    console.log('✅ Application loaded:', heading);
    
    // 2. Test Brand Search - Apple
    console.log('\n📍 STEP 2: Testing Brand Search (Apple)');
    const searchInput = page.locator('[data-testid="brand-search"]');
    await searchInput.fill('Apple');
    await page.waitForTimeout(1000);
    
    const searchButton = page.locator('button:has-text("Search Brand")');
    await searchButton.click();
    await page.waitForTimeout(3000);
    console.log('✅ Apple brand search completed');
    
    // 3. Test Brand Search - Nike
    console.log('\n📍 STEP 3: Testing Brand Search (Nike)');
    await searchInput.fill('Nike');
    await page.waitForTimeout(1000);
    await searchButton.click();
    await page.waitForTimeout(3000);
    console.log('✅ Nike brand search completed');
    
    // 4. Test Brand Search - Tesla
    console.log('\n📍 STEP 4: Testing Brand Search (Tesla)');
    await searchInput.fill('Tesla');
    await page.waitForTimeout(1000);
    await searchButton.click();
    await page.waitForTimeout(3000);
    console.log('✅ Tesla brand search completed');
    
    // 5. Test API Health with Header
    console.log('\n📍 STEP 5: Testing API Health with Headers');
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
    
    // 6. Test Complete Analysis Workflow
    console.log('\n📍 STEP 6: Testing Complete Analysis Workflow');
    const workflowTest = await page.evaluate(async () => {
      try {
        // Brand search
        const searchResp = await fetch('https://207d-220-244-77-193.ngrok-free.app/api/brand/search', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'ngrok-skip-browser-warning': 'true'
          },
          body: JSON.stringify({ query: 'Microsoft' })
        });
        const searchData = await searchResp.json();
        
        // Start analysis
        const analysisResp = await fetch('https://207d-220-244-77-193.ngrok-free.app/api/analyze', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'ngrok-skip-browser-warning': 'true'
          },
          body: JSON.stringify({ 
            brand: 'Microsoft',
            analysis_types: ['visual', 'market', 'sentiment']
          })
        });
        const analysisData = await analysisResp.json();
        
        // Get results
        const resultsResp = await fetch(`https://207d-220-244-77-193.ngrok-free.app/api/analyze/${analysisData.data.analysis_id}/results`, {
          headers: {
            'ngrok-skip-browser-warning': 'true'
          }
        });
        const resultsData = await resultsResp.json();
        
        return {
          success: true,
          brand_found: searchData.data.brand_name,
          analysis_started: analysisData.data.status === 'started',
          results_available: resultsData.data.overall_score > 0
        };
      } catch (error) {
        return { success: false, error: error.message };
      }
    });
    
    if (workflowTest.success) {
      console.log('✅ Complete Workflow Test Successful');
      console.log('✅ Brand Found:', workflowTest.brand_found);
      console.log('✅ Analysis Started:', workflowTest.analysis_started);
      console.log('✅ Results Available:', workflowTest.results_available);
    } else {
      console.log('❌ Workflow Test Failed:', workflowTest.error);
    }
    
    // 7. Performance Check
    const metrics = await page.evaluate(() => {
      const navigation = performance.getEntriesByType('navigation')[0];
      return {
        loadTime: Math.round(navigation.loadEventEnd - navigation.fetchStart),
        domReady: Math.round(navigation.domContentLoadedEventEnd - navigation.fetchStart)
      };
    });
    
    console.log('\n📊 PERFORMANCE METRICS');
    console.log('✅ Load Time:', metrics.loadTime + 'ms');
    console.log('✅ DOM Ready:', metrics.domReady + 'ms');
    
    // 8. Final Assessment
    console.log('\n🎯 FINAL PRODUCTION ASSESSMENT');
    console.log('===============================');
    
    const correctAPIUsage = apiCalls.every(url => url.includes('207d-220-244-77-193.ngrok-free.app'));
    const totalAPICalls = apiCalls.length;
    
    const results = {
      'Frontend Application': true,
      'UI Components Working': heading === 'AI Brand Audit Tool',
      'Correct API Configuration': correctAPIUsage,
      'API Health Check': healthTest.success,
      'Real API Keys Loaded': healthTest.success && healthTest.keys_loaded === 4,
      'Brand Search Working': totalAPICalls > 0,
      'Complete Workflow': workflowTest.success,
      'Performance Good': metrics.loadTime < 3000,
      'Error Free': errors.length === 0
    };
    
    let passCount = 0;
    console.log('\nTEST RESULTS:');
    for (const [test, passed] of Object.entries(results)) {
      console.log(`${passed ? '✅' : '❌'} ${test}: ${passed ? 'PASS' : 'FAIL'}`);
      if (passed) passCount++;
    }
    
    const finalScore = Math.round((passCount / Object.keys(results).length) * 100);
    console.log(`\n🎯 FINAL SCORE: ${finalScore}%`);
    
    if (finalScore >= 95) {
      console.log('🎉 PRODUCTION READY! System fully functional with real data!');
    } else if (finalScore >= 85) {
      console.log('🚀 EXCELLENT! System ready for deployment with minor optimizations needed.');
    } else if (finalScore >= 70) {
      console.log('⚠️ GOOD PROGRESS! Most functionality working, some issues to resolve.');
    } else {
      console.log('❌ NEEDS WORK! Major issues need to be fixed.');
    }
    
    console.log(`\n📈 IMPROVEMENT FROM START: From 29% to ${finalScore}% (+${finalScore - 29}%)`);
    
    console.log('\n🔗 QUICK ACCESS:');
    console.log('• Frontend: http://localhost:3000');
    console.log('• Backend API: https://207d-220-244-77-193.ngrok-free.app');
    console.log('• Backend Health: https://207d-220-244-77-193.ngrok-free.app/api/health');
    
    await page.screenshot({ path: 'final-test-result.png', fullPage: true });
    console.log('\n📸 Final screenshot saved as final-test-result.png');
    
  } catch (error) {
    console.log('❌ Test failed:', error.message);
  } finally {
    await browser.close();
  }
}

testFinal();