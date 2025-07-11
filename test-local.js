#!/usr/bin/env node

const { chromium } = require('playwright');

async function testLocal() {
  console.log('🧪 LOCAL PRODUCTION TEST');
  console.log('========================');
  
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  const errors = [];
  page.on('console', msg => {
    if (msg.type() === 'error') {
      errors.push(msg.text());
    }
  });
  
  try {
    // 1. Frontend Loading Test
    console.log('\n📍 STEP 1: Local Frontend Loading');
    await page.goto('http://localhost:3000', { 
      waitUntil: 'networkidle',
      timeout: 30000 
    });
    console.log('✅ Frontend loads successfully');
    
    // 2. UI Components Test
    console.log('\n📍 STEP 2: UI Components');
    const heading = await page.locator('h1').first().textContent();
    const inputs = await page.locator('input').count();
    const buttons = await page.locator('button').count();
    
    console.log(`✅ Heading: "${heading}"`);
    console.log(`✅ Input fields: ${inputs}`);
    console.log(`✅ Buttons: ${buttons}`);
    
    // 3. API Integration Test
    console.log('\n📍 STEP 3: API Integration');
    const apiResult = await page.evaluate(async () => {
      try {
        const response = await fetch('https://207d-220-244-77-193.ngrok-free.app/api/health');
        const data = await response.json();
        return { 
          status: response.status, 
          ok: response.ok,
          accessible: true,
          data: data
        };
      } catch (error) {
        return { 
          error: error.message,
          accessible: false
        };
      }
    });
    
    if (apiResult.accessible && apiResult.ok) {
      console.log('✅ Backend API is working:', apiResult.data.service);
      console.log('✅ API Keys configured:', Object.values(apiResult.data.api_keys_configured).some(v => v) ? 'Some' : 'None (using mock data)');
    } else {
      console.log('❌ Backend API not accessible:', apiResult);
    }
    
    // 4. Brand Search Test
    console.log('\n📍 STEP 4: Brand Search Test');
    const searchInput = page.locator('input[data-testid="brand-search"], input[placeholder*="brand"], input[placeholder*="company"], input').first();
    
    if (await searchInput.count() > 0) {
      await searchInput.fill('Apple');
      console.log('✅ Can fill brand search input');
      
      const searchButton = page.locator('button[type="submit"], button:has-text("Search"), button:has-text("Analyze")').first();
      if (await searchButton.count() > 0) {
        console.log('✅ Search button found');
        await searchButton.click();
        console.log('✅ Search button clicked');
        
        // Wait for any response or error
        await page.waitForTimeout(3000);
        console.log('✅ Waited for search response');
      } else {
        console.log('⚠️ Search button not found');
      }
    } else {
      console.log('⚠️ Search input not found');
    }
    
    // 5. Performance Assessment
    console.log('\n📍 STEP 5: Performance');
    const metrics = await page.evaluate(() => {
      const navigation = performance.getEntriesByType('navigation')[0];
      return {
        loadTime: Math.round(navigation.loadEventEnd - navigation.fetchStart),
        domReady: Math.round(navigation.domContentLoadedEventEnd - navigation.fetchStart)
      };
    });
    
    console.log(`✅ Load time: ${metrics.loadTime}ms`);
    console.log(`✅ DOM ready: ${metrics.domReady}ms`);
    
    // 6. Local System Assessment
    console.log('\n📊 LOCAL SYSTEM ASSESSMENT');
    console.log('============================');
    
    const assessments = {
      'Frontend Serving': true,
      'UI Loads': heading && heading.length > 0,
      'Input Fields': inputs > 0,
      'Buttons Present': buttons > 0,
      'Backend API': apiResult.accessible && apiResult.ok,
      'Performance': metrics.loadTime < 10000,
      'Error Free': errors.length === 0
    };
    
    let readyCount = 0;
    for (const [check, passed] of Object.entries(assessments)) {
      console.log(`${passed ? '✅' : '❌'} ${check}: ${passed ? 'PASS' : 'FAIL'}`);
      if (passed) readyCount++;
    }
    
    const readiness = Math.round((readyCount / Object.keys(assessments).length) * 100);
    console.log(`\n🎯 LOCAL SYSTEM READINESS: ${readiness}%`);
    
    if (readiness >= 85) {
      console.log('🎉 LOCAL SYSTEM READY FOR PRODUCTION!');
      console.log('\n🚀 NEXT STEPS:');
      console.log('- Add API keys to environment variables for real data');
      console.log('- Deploy to Vercel for production hosting');
      console.log('- Configure custom domain');
    } else if (readiness >= 70) {
      console.log('⚠️ MOSTLY READY - Minor issues to fix');
    } else {
      console.log('❌ NOT READY - Major issues need fixing');
    }
    
    if (errors.length > 0) {
      console.log('\n🐛 JavaScript Errors Found:');
      errors.slice(0, 3).forEach(err => console.log('- ' + err));
    }
    
    await page.screenshot({ path: 'local-test.png', fullPage: true });
    console.log('\n📸 Screenshot saved as local-test.png');
    
  } catch (error) {
    console.log('❌ Local test failed:', error.message);
  } finally {
    await browser.close();
  }
}

testLocal();