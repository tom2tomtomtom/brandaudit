#!/usr/bin/env node

const { chromium } = require('playwright');

async function testRealFunctionality() {
  console.log('🧪 REAL FUNCTIONALITY TEST WITH API KEYS');
  console.log('==========================================');
  
  const browser = await chromium.launch({ 
    headless: false,
    slowMo: 1000  // Slow down actions so we can see what's happening
  });
  const page = await browser.newPage();
  
  const errors = [];
  const apiCalls = [];
  
  // Monitor console errors
  page.on('console', msg => {
    if (msg.type() === 'error') {
      errors.push(msg.text());
      console.log('❌ Console Error:', msg.text());
    }
  });
  
  // Monitor network requests to see which API we're calling
  page.on('request', request => {
    if (request.url().includes('/api/')) {
      apiCalls.push(request.url());
      console.log('📡 API Call:', request.url());
    }
  });
  
  try {
    // 1. Load Frontend
    console.log('\n📍 STEP 1: Loading Frontend');
    await page.goto('http://localhost:3000', { 
      waitUntil: 'networkidle',
      timeout: 30000 
    });
    console.log('✅ Frontend loaded successfully');
    
    // 2. Check UI Elements
    console.log('\n📍 STEP 2: Checking UI Elements');
    const heading = await page.locator('h1').first().textContent();
    console.log(`✅ Page heading: "${heading}"`);
    
    // 3. Test Brand Search
    console.log('\n📍 STEP 3: Testing Brand Search');
    
    // Wait for and find the search input
    await page.waitForSelector('input', { timeout: 10000 });
    const searchInput = page.locator('input').first();
    
    console.log('📝 Filling in brand search: "Apple"');
    await searchInput.fill('Apple');
    await page.waitForTimeout(1000);
    
    // Find and click search button
    const searchButton = page.locator('button').first();
    console.log('🖱️ Clicking search button');
    await searchButton.click();
    
    // Wait for API response
    console.log('⏳ Waiting for API response...');
    await page.waitForTimeout(5000);
    
    // 4. Check API Calls Made
    console.log('\n📍 STEP 4: Analyzing API Calls');
    console.log('API calls made:', apiCalls);
    
    const correctAPI = apiCalls.some(url => url.includes('207d-220-244-77-193.ngrok-free.app'));
    const wrongAPI = apiCalls.some(url => url.includes('backend-service-production-1b63.up.railway.app'));
    
    if (correctAPI) {
      console.log('✅ Using correct ngrok API:', apiCalls.find(url => url.includes('207d-220-244-77-193.ngrok-free.app')));
    }
    if (wrongAPI) {
      console.log('❌ Still using old Railway API:', apiCalls.find(url => url.includes('backend-service-production-1b63.up.railway.app')));
    }
    
    // 5. Test Direct API Call from Browser
    console.log('\n📍 STEP 5: Testing Direct API Call');
    const apiTest = await page.evaluate(async () => {
      try {
        console.log('Testing direct API call...');
        const response = await fetch('https://207d-220-244-77-193.ngrok-free.app/api/health');
        const data = await response.json();
        return { 
          success: true, 
          status: response.status,
          service: data.service,
          api_keys: data.api_keys_configured
        };
      } catch (error) {
        return { 
          success: false, 
          error: error.message 
        };
      }
    });
    
    if (apiTest.success) {
      console.log('✅ Direct API call successful');
      console.log('✅ Service:', apiTest.service);
      console.log('✅ API Keys loaded:', Object.entries(apiTest.api_keys).filter(([k,v]) => v).map(([k,v]) => k));
    } else {
      console.log('❌ Direct API call failed:', apiTest.error);
    }
    
    // 6. Test Brand Search API Call
    console.log('\n📍 STEP 6: Testing Brand Search API');
    const brandSearchTest = await page.evaluate(async () => {
      try {
        const response = await fetch('https://207d-220-244-77-193.ngrok-free.app/api/brand/search', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ query: 'Apple' })
        });
        const data = await response.json();
        return { 
          success: true, 
          brand: data.data.brand_name,
          website: data.data.website
        };
      } catch (error) {
        return { 
          success: false, 
          error: error.message 
        };
      }
    });
    
    if (brandSearchTest.success) {
      console.log('✅ Brand search API working');
      console.log('✅ Found brand:', brandSearchTest.brand);
      console.log('✅ Website:', brandSearchTest.website);
    } else {
      console.log('❌ Brand search API failed:', brandSearchTest.error);
    }
    
    // 7. Final Assessment
    console.log('\n📊 FINAL ASSESSMENT');
    console.log('====================');
    
    const assessments = {
      'Frontend Loading': true,
      'UI Elements Present': heading && heading.length > 0,
      'Using Correct API': correctAPI && !wrongAPI,
      'Direct API Works': apiTest.success,
      'Brand Search Works': brandSearchTest.success,
      'No Console Errors': errors.length === 0,
      'API Keys Loaded': apiTest.success && Object.values(apiTest.api_keys || {}).some(v => v)
    };
    
    let passCount = 0;
    for (const [check, passed] of Object.entries(assessments)) {
      console.log(`${passed ? '✅' : '❌'} ${check}: ${passed ? 'PASS' : 'FAIL'}`);
      if (passed) passCount++;
    }
    
    const readiness = Math.round((passCount / Object.keys(assessments).length) * 100);
    console.log(`\n🎯 SYSTEM READINESS: ${readiness}%`);
    
    if (readiness >= 85) {
      console.log('🎉 SYSTEM FULLY FUNCTIONAL WITH REAL DATA!');
    } else {
      console.log('⚠️ Issues found - check the details above');
    }
    
    // Show errors if any
    if (errors.length > 0) {
      console.log('\n🐛 Console Errors:');
      errors.forEach(err => console.log('  -', err));
    }
    
    // Take screenshot
    await page.screenshot({ path: 'real-functionality-test.png', fullPage: true });
    console.log('\n📸 Screenshot saved as real-functionality-test.png');
    
  } catch (error) {
    console.log('❌ Test failed:', error.message);
  } finally {
    await browser.close();
  }
}

testRealFunctionality();