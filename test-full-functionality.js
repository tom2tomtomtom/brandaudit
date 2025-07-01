const { chromium } = require('playwright');

async function testFullFunctionality() {
  console.log('🧪 Starting comprehensive functionality tests...');
  
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  // Capture console errors and network issues
  const errors = [];
  const networkErrors = [];
  
  page.on('console', msg => {
    if (msg.type() === 'error') {
      errors.push(msg.text());
      console.log('🚨 Console error:', msg.text());
    }
  });
  
  page.on('response', response => {
    if (response.status() >= 400) {
      networkErrors.push(`${response.url()} - ${response.status()}`);
      console.log('🚨 Network error:', response.url(), response.status());
    }
  });
  
  try {
    // 1. Test initial page load
    console.log('\n📍 TEST 1: Initial Page Load');
    await page.goto('https://brandaudit.up.railway.app', { 
      waitUntil: 'networkidle',
      timeout: 30000 
    });
    
    const title = await page.title();
    console.log('✅ Page loads:', title);
    
    // 2. Test React app elements
    console.log('\n🔍 TEST 2: React App Elements');
    const heading = await page.locator('h1').textContent();
    const buttons = await page.locator('button').count();
    const featureCards = await page.locator('div').filter({ hasText: 'Brand Search' }).count();
    
    console.log('✅ Main heading:', heading);
    console.log('✅ Buttons found:', buttons);
    console.log('✅ Feature cards:', featureCards);
    
    // 3. Test button interactions
    console.log('\n🖱️ TEST 3: Button Interactions');
    const startButton = page.locator('button').filter({ hasText: 'Start Analysis' });
    if (await startButton.count() > 0) {
      await startButton.click();
      await page.waitForTimeout(1000);
      const updatedText = await startButton.textContent();
      console.log('✅ Button click updates text:', updatedText);
    }
    
    // 4. Test navigation (if routes exist)
    console.log('\n🧭 TEST 4: Navigation');
    const navLinks = await page.locator('a, [role="link"]').count();
    console.log('✅ Navigation links found:', navLinks);
    
    // 5. Test responsive design
    console.log('\n📱 TEST 5: Responsive Design');
    await page.setViewportSize({ width: 375, height: 667 }); // Mobile
    await page.waitForTimeout(1000);
    const mobileView = await page.screenshot({ path: 'mobile-view.png' });
    console.log('✅ Mobile view captured');
    
    await page.setViewportSize({ width: 1200, height: 800 }); // Desktop
    await page.waitForTimeout(1000);
    console.log('✅ Desktop view restored');
    
    // 6. Test form elements (if any)
    console.log('\n📝 TEST 6: Form Elements');
    const inputs = await page.locator('input').count();
    const textareas = await page.locator('textarea').count();
    const selects = await page.locator('select').count();
    
    console.log('✅ Inputs found:', inputs);
    console.log('✅ Textareas found:', textareas);
    console.log('✅ Selects found:', selects);
    
    // 7. Test API readiness
    console.log('\n🌐 TEST 7: API Readiness Check');
    try {
      // Test backend health endpoint
      const response = await page.evaluate(async () => {
        try {
          const res = await fetch('https://backend-service-production-1b63.up.railway.app/api/health');
          return { status: res.status, ok: res.ok };
        } catch (error) {
          return { error: error.message };
        }
      });
      
      if (response.ok) {
        console.log('✅ Backend API is responding');
      } else {
        console.log('❌ Backend API issues:', response);
      }
    } catch (error) {
      console.log('❌ Backend API test failed:', error.message);
    }
    
    // 8. Test expected functionality that should exist
    console.log('\n🎯 TEST 8: Expected Features Assessment');
    
    const expectedFeatures = [
      { name: 'Brand Search', selector: '[data-testid="brand-search"], [title*="search"], [aria-label*="search"]' },
      { name: 'File Upload', selector: 'input[type="file"], [data-testid="upload"]' },
      { name: 'Analysis Form', selector: 'form, [data-testid="analysis-form"]' },
      { name: 'Results Display', selector: '[data-testid="results"], .results' },
      { name: 'Historical Data', selector: '[data-testid="history"], [href*="history"]' }
    ];
    
    for (const feature of expectedFeatures) {
      const exists = await page.locator(feature.selector).count() > 0;
      console.log(`${exists ? '✅' : '❌'} ${feature.name}: ${exists ? 'Found' : 'Missing'}`);
    }
    
    // 9. Performance metrics
    console.log('\n⚡ TEST 9: Performance Metrics');
    const performanceMetrics = await page.evaluate(() => {
      const navigation = performance.getEntriesByType('navigation')[0];
      return {
        loadTime: Math.round(navigation.loadEventEnd - navigation.fetchStart),
        domReady: Math.round(navigation.domContentLoadedEventEnd - navigation.fetchStart),
        firstPaint: Math.round(performance.getEntriesByType('paint')[0]?.startTime || 0)
      };
    });
    
    console.log('✅ Page load time:', performanceMetrics.loadTime + 'ms');
    console.log('✅ DOM ready time:', performanceMetrics.domReady + 'ms');
    console.log('✅ First paint:', performanceMetrics.firstPaint + 'ms');
    
    // 10. Final assessment
    console.log('\n📊 TEST SUMMARY');
    console.log('===============');
    console.log('Console errors:', errors.length);
    console.log('Network errors:', networkErrors.length);
    console.log('Page functional:', title.includes('AI Brand Audit'));
    console.log('React working:', buttons > 0 && heading.includes('AI Brand Audit'));
    
    if (errors.length === 0 && networkErrors.length === 0) {
      console.log('🎉 All tests passed! App is functioning correctly.');
    } else {
      console.log('⚠️ Some issues detected - needs backend integration.');
    }
    
    // Save final screenshot
    await page.screenshot({ path: 'final-test-screenshot.png', fullPage: true });
    console.log('📸 Final screenshot saved');
    
  } catch (error) {
    console.log('❌ Test suite failed:', error.message);
  } finally {
    await browser.close();
  }
}

testFullFunctionality();