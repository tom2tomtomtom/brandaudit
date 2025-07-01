const { chromium } = require('playwright');

async function testSite() {
  console.log('🚀 Starting Playwright test of brandaudit.up.railway.app...');
  
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  try {
    // Navigate to the site
    console.log('📍 Navigating to site...');
    await page.goto('https://brandaudit.up.railway.app', { 
      waitUntil: 'networkidle',
      timeout: 30000 
    });
    
    // Take a screenshot
    await page.screenshot({ path: 'site-screenshot.png', fullPage: true });
    console.log('📸 Screenshot saved as site-screenshot.png');
    
    // Check page title
    const title = await page.title();
    console.log('📄 Page title:', title);
    
    // Check if React has rendered
    const rootContent = await page.locator('#root').innerHTML();
    console.log('🔍 Root element content length:', rootContent.length);
    
    if (rootContent.length < 50) {
      console.log('❌ React app not rendering - root element is empty or minimal');
      console.log('Root content:', rootContent);
    } else {
      console.log('✅ React app appears to be rendering');
    }
    
    // Check for specific elements
    const heading = await page.locator('h1').textContent().catch(() => null);
    console.log('📝 Main heading:', heading);
    
    // Check for buttons
    const buttons = await page.locator('button').count();
    console.log('🔘 Number of buttons found:', buttons);
    
    // Check for any JavaScript errors
    page.on('console', msg => {
      if (msg.type() === 'error') {
        console.log('🚨 Console error:', msg.text());
      }
    });
    
    // Check for network errors
    page.on('response', response => {
      if (response.status() >= 400) {
        console.log('🚨 Network error:', response.url(), response.status());
      }
    });
    
    // Try to click a button if it exists
    try {
      const firstButton = page.locator('button').first();
      if (await firstButton.count() > 0) {
        console.log('🖱️ Attempting to click first button...');
        await firstButton.click();
        await page.waitForTimeout(1000);
        console.log('✅ Button click successful');
      }
    } catch (error) {
      console.log('❌ Button click failed:', error.message);
    }
    
    // Check current page content
    const bodyText = await page.locator('body').textContent();
    console.log('📄 Page contains text (first 200 chars):', bodyText.substring(0, 200));
    
    // Check if it's showing React content or static HTML
    const hasReactText = bodyText.includes('React App Successfully Deployed');
    const hasGradient = await page.locator('[style*="gradient"]').count() > 0;
    const hasClickCounter = bodyText.includes('Clicked');
    
    console.log('🎨 Has gradient styling:', hasGradient);
    console.log('⚛️ Has React success text:', hasReactText);
    console.log('🔢 Has click counter:', hasClickCounter);
    
    if (hasReactText && hasGradient) {
      console.log('🎉 SUCCESS: React app is fully working!');
    } else {
      console.log('⚠️ Issues detected with React app rendering');
    }
    
  } catch (error) {
    console.log('❌ Test failed:', error.message);
  } finally {
    await browser.close();
  }
}

testSite();