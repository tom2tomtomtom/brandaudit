const { chromium } = require('playwright');

async function testProduction() {
  console.log('🧪 PRODUCTION READINESS TEST');
  console.log('===============================');
  
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
    console.log('\n📍 STEP 1: Frontend Loading');
    await page.goto('https://brandaudit.up.railway.app', { 
      waitUntil: 'networkidle',
      timeout: 30000 
    });
    console.log('✅ Frontend loads successfully');
    
    // 2. UI Components Test
    console.log('\n📍 STEP 2: UI Components');
    const heading = await page.locator('h1').textContent();
    const inputs = await page.locator('input').count();
    const buttons = await page.locator('button').count();
    const navLinks = await page.locator('a').count();
    
    console.log(`✅ Heading: "${heading}"`);
    console.log(`✅ Input fields: ${inputs}`);
    console.log(`✅ Buttons: ${buttons}`);
    console.log(`✅ Navigation links: ${navLinks}`);
    
    // 3. Form Interaction Test
    console.log('\n📍 STEP 3: Form Interaction');
    const searchInput = page.locator('input[data-testid="brand-search"]');
    if (await searchInput.count() > 0) {
      await searchInput.fill('Apple');
      console.log('✅ Can fill brand search input');
      
      const searchButton = page.locator('button[type="submit"]');
      if (await searchButton.count() > 0) {
        console.log('✅ Search button found');
        await searchButton.click();
        console.log('✅ Search button clickable');
        
        // Wait for any response or error
        await page.waitForTimeout(3000);
        
        // Check if moved to next step or got error
        const currentStep = await page.locator('[class*="w-8 h-8"]').count();
        console.log(`✅ Step indicators found: ${currentStep}`);
      }
    }
    
    // 4. Navigation Test
    console.log('\n📍 STEP 4: Navigation');
    const historyLink = page.locator('a[data-testid="history"]');
    if (await historyLink.count() > 0) {
      await historyLink.click();
      await page.waitForTimeout(2000);
      
      const currentUrl = page.url();
      console.log(`✅ Navigation works: ${currentUrl}`);
      
      // Go back to home
      await page.goto('https://brandaudit.up.railway.app');
    }
    
    // 5. API Integration Test (even if backend is down)
    console.log('\n📍 STEP 5: API Integration');
    const apiResult = await page.evaluate(async () => {
      try {
        const response = await fetch('https://backend-service-production-1b63.up.railway.app/api/health');
        return { 
          status: response.status, 
          ok: response.ok,
          accessible: true
        };
      } catch (error) {
        return { 
          error: error.message,
          accessible: false
        };
      }
    });
    
    if (apiResult.accessible && apiResult.ok) {
      console.log('✅ Backend API is working');
    } else {
      console.log('❌ Backend API not accessible:', apiResult);
    }
    
    // 6. Feature Completeness Check
    console.log('\n📍 STEP 6: Feature Completeness');
    const features = [
      { name: 'Brand Search Form', selector: '[data-testid="brand-search"]' },
      { name: 'File Upload Area', selector: '[data-testid="upload"]' },
      { name: 'Analysis Form', selector: '[data-testid="analysis-form"]' },
      { name: 'Historical Link', selector: '[data-testid="history"]' },
      { name: 'Step Indicators', selector: '[class*="w-8 h-8"]' }
    ];
    
    for (const feature of features) {
      const exists = await page.locator(feature.selector).count() > 0;
      console.log(`${exists ? '✅' : '❌'} ${feature.name}: ${exists ? 'Present' : 'Missing'}`);
    }
    
    // 7. Performance Test
    console.log('\n📍 STEP 7: Performance');
    const metrics = await page.evaluate(() => {
      const navigation = performance.getEntriesByType('navigation')[0];
      return {
        loadTime: Math.round(navigation.loadEventEnd - navigation.fetchStart),
        domReady: Math.round(navigation.domContentLoadedEventEnd - navigation.fetchStart)
      };
    });
    
    console.log(`✅ Load time: ${metrics.loadTime}ms`);
    console.log(`✅ DOM ready: ${metrics.domReady}ms`);
    
    // 8. Production Readiness Assessment
    console.log('\n📊 PRODUCTION READINESS ASSESSMENT');
    console.log('=====================================');
    
    const assessments = {
      'Frontend Deployment': true,
      'UI Components': inputs > 0 && buttons > 0,
      'Form Functionality': await searchInput.count() > 0,
      'Navigation': navLinks > 0,
      'Performance': metrics.loadTime < 5000,
      'Error Free': errors.length === 0,
      'Backend API': apiResult.accessible && apiResult.ok
    };
    
    let readyCount = 0;
    for (const [check, passed] of Object.entries(assessments)) {
      console.log(`${passed ? '✅' : '❌'} ${check}: ${passed ? 'PASS' : 'FAIL'}`);
      if (passed) readyCount++;
    }
    
    const readiness = Math.round((readyCount / Object.keys(assessments).length) * 100);
    console.log(`\n🎯 OVERALL READINESS: ${readiness}%`);
    
    if (readiness >= 85) {
      console.log('🎉 PRODUCTION READY!');
    } else if (readiness >= 70) {
      console.log('⚠️ MOSTLY READY - Minor issues to fix');
    } else {
      console.log('❌ NOT READY - Major issues need fixing');
    }
    
    // 9. Next Steps
    console.log('\n🔧 NEXT STEPS:');
    if (!assessments['Backend API']) {
      console.log('- Fix backend service deployment in Railway');
      console.log('- Check backend service logs for errors');
      console.log('- Verify environment variables are set');
    }
    if (errors.length > 0) {
      console.log('- Fix JavaScript errors:', errors.slice(0, 3));
    }
    if (readiness >= 85) {
      console.log('- Add monitoring and analytics');
      console.log('- Set up CI/CD pipeline');
      console.log('- Configure custom domain');
      console.log('- Add SSL certificate');
    }
    
    await page.screenshot({ path: 'production-test.png', fullPage: true });
    console.log('\n📸 Screenshot saved as production-test.png');
    
  } catch (error) {
    console.log('❌ Production test failed:', error.message);
  } finally {
    await browser.close();
  }
}

testProduction();