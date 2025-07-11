#!/usr/bin/env node

const { chromium } = require('playwright');

async function diagnoseFrontend() {
  console.log('🔍 FRONTEND DIAGNOSIS - Finding Why Results Are Garbage');
  console.log('=====================================================');
  
  const browser = await chromium.launch({ headless: false, slowMo: 500 });
  const page = await browser.newPage();
  
  const errors = [];
  
  // Capture all console errors
  page.on('console', msg => {
    if (msg.type() === 'error') {
      errors.push(msg.text());
      console.log('❌ Frontend Error:', msg.text());
    } else if (msg.type() === 'log') {
      console.log('📝 Console Log:', msg.text());
    }
  });
  
  // Capture network failures
  page.on('requestfailed', request => {
    console.log('🌐 Network Failure:', request.url(), request.failure().errorText);
  });
  
  try {
    // Load app
    console.log('\n1️⃣ Loading Frontend...');
    await page.goto('http://localhost:5173', { waitUntil: 'networkidle' });
    console.log('✅ Frontend loaded');
    
    // Start analysis
    console.log('\n2️⃣ Starting Tesla Analysis...');
    await page.fill('[data-testid="brand-search"]', 'Tesla');
    await page.click('button:has-text("Search Brand")');
    await page.waitForTimeout(2000);
    
    await page.click('button:has-text("Skip Upload")');
    await page.waitForTimeout(1000);
    
    await page.click('button:has-text("Start Analysis")');
    console.log('✅ Analysis started');
    
    // Wait longer and check what happens
    console.log('\n3️⃣ Waiting for Results (30 seconds)...');
    
    let resultsAppeared = false;
    for (let i = 0; i < 30; i++) {
      await page.waitForTimeout(1000);
      
      // Check if results section exists
      const resultsVisible = await page.locator('[data-testid="results"]').isVisible().catch(() => false);
      if (resultsVisible) {
        console.log(`✅ Results appeared after ${i + 1} seconds`);
        resultsAppeared = true;
        break;
      }
      
      // Check current step
      const currentContent = await page.textContent('body');
      if (currentContent.includes('Processing Analysis')) {
        console.log(`⏳ Still processing... (${i + 1}s)`);
      } else if (currentContent.includes('Analysis Options')) {
        console.log(`⚠️ Stuck on Analysis Options (${i + 1}s)`);
      } else if (currentContent.includes('error')) {
        console.log(`❌ Error detected (${i + 1}s)`);
        break;
      }
    }
    
    if (resultsAppeared) {
      console.log('\n4️⃣ Analyzing Results Display...');
      
      // Check what's actually displayed
      const resultsContent = await page.locator('[data-testid="results"]').textContent();
      console.log('Results content length:', resultsContent.length);
      
      // Check specific elements
      const overallScore = await page.locator('.text-3xl.font-bold').first().textContent().catch(() => 'NOT FOUND');
      console.log('Overall Score displayed:', overallScore);
      
      // Check tabs
      const tabs = await page.locator('button[role="tab"]').allTextContents();
      console.log('Tabs available:', tabs);
      
      // Check executive summary
      const hasExecutiveSummary = await page.locator('text=Executive Summary').isVisible().catch(() => false);
      console.log('Executive Summary visible:', hasExecutiveSummary);
      
      // Check for rich content
      const bodyText = await page.textContent('body');
      const hasRichContent = bodyText.includes('McKinsey') || bodyText.includes('EXECUTIVE SUMMARY') || bodyText.includes('COMPETITIVE INTELLIGENCE');
      console.log('Rich LLM content visible:', hasRichContent);
      
      // Test perception tab
      const perceptionTab = page.locator('button[role="tab"]:has-text("Perception")');
      if (await perceptionTab.isVisible()) {
        await perceptionTab.click();
        await page.waitForTimeout(1000);
        
        const sentimentData = await page.textContent('.bg-green-50, .bg-red-50, .bg-gray-50').catch(() => 'No sentiment data');
        console.log('Sentiment data:', sentimentData);
      }
      
      console.log('\n📸 Taking screenshot for analysis...');
      await page.screenshot({ path: 'frontend-diagnosis.png', fullPage: true });
      
    } else {
      console.log('\n❌ CRITICAL: Results never appeared');
      console.log('Frontend is completely broken');
      
      // Check what state we're stuck in
      const currentHTML = await page.innerHTML('body');
      console.log('Current page state:', currentHTML.substring(0, 500));
    }
    
    console.log('\n🐛 DIAGNOSIS SUMMARY:');
    console.log('JavaScript Errors:', errors.length);
    for (const error of errors) {
      console.log(`  - ${error}`);
    }
    
    console.log('Results Appeared:', resultsAppeared);
    
  } catch (error) {
    console.log('❌ Diagnosis failed:', error.message);
  } finally {
    await browser.close();
  }
}

diagnoseFrontend();