const { chromium } = require('playwright');

async function testBackend() {
  console.log('🔧 Testing backend accessibility...');
  
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  try {
    // Test direct API call from frontend
    console.log('📍 Testing API call from frontend...');
    
    const result = await page.evaluate(async () => {
      try {
        console.log('Making fetch request to backend...');
        const response = await fetch('https://backend-service-production-1b63.up.railway.app/api/health', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json'
          },
          mode: 'cors'
        });
        
        console.log('Response status:', response.status);
        console.log('Response headers:', [...response.headers.entries()]);
        
        if (response.ok) {
          const data = await response.json();
          return { success: true, data, status: response.status };
        } else {
          return { success: false, status: response.status, statusText: response.statusText };
        }
      } catch (error) {
        console.log('Fetch error:', error.message);
        return { success: false, error: error.message };
      }
    });
    
    console.log('API test result:', result);
    
    if (result.success) {
      console.log('✅ Backend API is working!');
      console.log('Health data:', result.data);
      
      // Test brand search
      console.log('\n🔍 Testing brand search...');
      await page.goto('https://brandaudit.up.railway.app');
      
      const searchInput = page.locator('input[data-testid="brand-search"]');
      await searchInput.fill('Apple');
      
      const searchButton = page.locator('button[type="submit"]');
      await searchButton.click();
      
      await page.waitForTimeout(3000);
      console.log('✅ Brand search test completed');
      
    } else {
      console.log('❌ Backend API not accessible:', result);
      
      // Check if it's a CORS issue by testing from same origin
      console.log('\n🌐 Testing CORS configuration...');
      
      const corsTest = await page.evaluate(() => {
        return fetch('https://backend-service-production-1b63.up.railway.app/api/health', { 
          mode: 'no-cors' 
        }).then(() => 'accessible').catch(e => e.message);
      });
      
      console.log('CORS test result:', corsTest);
    }
    
  } catch (error) {
    console.log('❌ Test failed:', error.message);
  } finally {
    await browser.close();
  }
}

testBackend();