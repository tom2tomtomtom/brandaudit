import { chromium } from 'playwright';

async function debugUITest() {
  console.log('🧪 REAL DATA UI TEST - NO FAKE DATA ALLOWED');
  console.log('=' * 60);

  // Test with completely random brands NOT in any suggested list
  const randomBrands = [
    'Patagonia',      // Outdoor clothing
    'Warby Parker',   // Eyewear
    'Allbirds',       // Sustainable shoes
    'Glossier',       // Beauty
    'Peloton',        // Fitness
    'Stripe',         // Payments
    'Notion',         // Productivity
    'Figma'           // Design tools
  ];

  const testBrand = randomBrands[Math.floor(Math.random() * randomBrands.length)];
  console.log(`🎯 Testing with random brand: ${testBrand}`);
  
  const browser = await chromium.launch({ 
    headless: false,
    slowMo: 1000 // Slow down for debugging
  });
  
  const page = await browser.newPage();
  
  // Enable console logging
  page.on('console', msg => console.log('BROWSER:', msg.text()));
  page.on('pageerror', error => console.log('PAGE ERROR:', error.message));
  page.on('requestfailed', request => console.log('REQUEST FAILED:', request.url(), request.failure().errorText));
  
  try {
    console.log('1️⃣ Loading homepage...');
    await page.goto('http://localhost:5173', { waitUntil: 'networkidle' });
    
    // Take screenshot of initial state
    await page.screenshot({ path: 'debug-1-homepage.png', fullPage: true });
    console.log('📸 Screenshot saved: debug-1-homepage.png');
    
    // Check what's actually on the page
    const title = await page.title();
    console.log('📄 Page title:', title);
    
    const bodyText = await page.locator('body').textContent();
    console.log('📝 Page content preview:', bodyText.substring(0, 200) + '...');
    
    // Look for input field
    console.log('2️⃣ Looking for input field...');
    const inputs = await page.locator('input').count();
    console.log('🔍 Found', inputs, 'input fields');
    
    if (inputs > 0) {
      const inputPlaceholder = await page.locator('input').first().getAttribute('placeholder');
      console.log('📝 First input placeholder:', inputPlaceholder);
      
      // Try to enter brand name
      console.log(`3️⃣ Entering random brand name: ${testBrand}...`);
      await page.locator('input').first().fill(testBrand);
      await page.screenshot({ path: 'debug-2-input-filled.png', fullPage: true });
      console.log('📸 Screenshot saved: debug-2-input-filled.png');
      
      // Look for button
      console.log('4️⃣ Looking for analyze button...');
      const buttons = await page.locator('button').count();
      console.log('🔍 Found', buttons, 'buttons');
      
      if (buttons > 0) {
        const buttonText = await page.locator('button').first().textContent();
        console.log('🔘 First button text:', buttonText);
        
        // Monitor network requests and responses for REAL DATA validation
        const requests = [];
        const responses = [];

        page.on('request', request => {
          requests.push({
            url: request.url(),
            method: request.method(),
            postData: request.postData()
          });
        });

        page.on('response', async response => {
          if (response.url().includes('/api/')) {
            try {
              const responseData = await response.json();
              responses.push({
                url: response.url(),
                status: response.status(),
                data: responseData
              });
            } catch (e) {
              responses.push({
                url: response.url(),
                status: response.status(),
                error: 'Could not parse JSON'
              });
            }
          }
        });
        
        // Click the button
        console.log('5️⃣ Clicking analyze button...');
        await page.locator('button').first().click();
        
        // Wait and see what happens
        await page.waitForTimeout(5000);
        await page.screenshot({ path: 'debug-3-after-click.png', fullPage: true });
        console.log('📸 Screenshot saved: debug-3-after-click.png');
        
        console.log('🌐 Network requests made:');
        requests.forEach((req, i) => {
          console.log(`  ${i + 1}. ${req.method} ${req.url}`);
          if (req.postData) {
            console.log(`     POST data: ${req.postData}`);
          }
        });

        console.log('\n📡 API Responses received:');
        responses.forEach((resp, i) => {
          console.log(`  ${i + 1}. ${resp.status} ${resp.url}`);
          if (resp.data) {
            console.log(`     Data keys: ${Object.keys(resp.data).join(', ')}`);
            if (resp.data.data) {
              console.log(`     Nested data keys: ${Object.keys(resp.data.data).join(', ')}`);
            }
          }
        });
        
        // Check for any results or error messages
        const pageContent = await page.locator('body').textContent();
        console.log('📄 Page content after click:', pageContent.substring(0, 500) + '...');
        
        // Look for specific elements that should appear
        const hasResults = await page.locator('text=Analysis').count() > 0;
        const hasError = await page.locator('text=error').count() > 0;
        const hasLoading = await page.locator('text=Loading').count() > 0;
        
        console.log('🔍 Results found:', hasResults);
        console.log('❌ Error found:', hasError);
        console.log('⏳ Loading found:', hasLoading);
        
        // Wait longer to see if anything loads
        console.log('6️⃣ Waiting for analysis to complete...');
        await page.waitForTimeout(30000); // Wait longer for real analysis
        await page.screenshot({ path: 'debug-4-final-state.png', fullPage: true });
        console.log('📸 Screenshot saved: debug-4-final-state.png');

        // CRITICAL: Validate NO FAKE DATA
        console.log('\n🚨 VALIDATING NO FAKE DATA:');

        // Check for fake data indicators in responses
        let hasFakeData = false;
        responses.forEach(resp => {
          if (resp.data && typeof resp.data === 'object') {
            const dataStr = JSON.stringify(resp.data).toLowerCase();
            const fakeIndicators = [
              'lorem ipsum', 'placeholder', 'example', 'sample', 'dummy',
              'fake', 'mock', 'test data', 'coming soon', 'not available',
              'default', 'generic', 'template'
            ];

            fakeIndicators.forEach(indicator => {
              if (dataStr.includes(indicator)) {
                console.log(`❌ FAKE DATA DETECTED: "${indicator}" found in response`);
                hasFakeData = true;
              }
            });
          }
        });

        // Check if brand name appears in results (real data should reference the actual brand)
        const finalContent = await page.locator('body').textContent();
        const brandInResults = finalContent.toLowerCase().includes(testBrand.toLowerCase());
        console.log(`🎯 Brand "${testBrand}" found in results: ${brandInResults}`);

        if (!brandInResults) {
          console.log('❌ POTENTIAL FAKE DATA: Brand name not found in results');
          hasFakeData = true;
        }

        // Final validation
        if (hasFakeData) {
          console.log('\n🚨 CRITICAL FAILURE: FAKE DATA DETECTED!');
          console.log('❌ The application is returning fake/fallback data');
        } else {
          console.log('\n✅ VALIDATION PASSED: No fake data detected');
          console.log('✅ Real data analysis appears to be working');
        }

      } else {
        console.log('❌ No buttons found!');
      }
    } else {
      console.log('❌ No input fields found!');
    }

    console.log('\n✅ Real data UI test completed');
    
  } catch (error) {
    console.error('❌ Debug test failed:', error);
    await page.screenshot({ path: 'debug-error.png', fullPage: true });
  } finally {
    await browser.close();
  }
}

// Run the debug test
debugUITest().catch(console.error);
