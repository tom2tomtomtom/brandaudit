#!/usr/bin/env node

const { chromium } = require('playwright');

async function debugConsultingReport() {
  console.log('🔍 DEBUGGING CONSULTING REPORT - SYSTEMATIC FIX');
  console.log('=================================================');
  
  const browser = await chromium.launch({ headless: false, slowMo: 500 });
  const page = await browser.newPage();
  
  const errors = [];
  const logs = [];
  
  // Capture console output
  page.on('console', msg => {
    const text = msg.text();
    logs.push(text);
    if (msg.type() === 'error') {
      errors.push(text);
      console.log('❌ Frontend Error:', text);
    } else if (msg.type() === 'log') {
      console.log('📝 Console Log:', text);
    }
  });
  
  // Capture network failures
  page.on('requestfailed', request => {
    console.log('🌐 Network Failure:', request.url(), request.failure().errorText);
  });
  
  try {
    // Step 1: Load frontend
    console.log('\n1️⃣ Loading Frontend...');
    await page.goto('http://localhost:5173', { waitUntil: 'networkidle' });
    console.log('✅ Frontend loaded');
    
    // Step 2: Start Tesla analysis
    console.log('\n2️⃣ Starting Tesla Analysis...');
    await page.fill('[data-testid="brand-search"]', 'Tesla');
    await page.click('button:has-text("Search Brand")');
    await page.waitForTimeout(2000);
    
    await page.click('button:has-text("Skip Upload")');
    await page.waitForTimeout(1000);
    
    await page.click('button:has-text("Start Analysis")');
    console.log('✅ Analysis started');
    
    // Step 3: Wait for results
    console.log('\n3️⃣ Waiting for Results...');
    
    let resultsAppeared = false;
    for (let i = 0; i < 60; i++) {
      await page.waitForTimeout(1000);
      
      const resultsVisible = await page.locator('[data-testid="results"]').isVisible().catch(() => false);
      if (resultsVisible) {
        console.log(`✅ Results appeared after ${i + 1} seconds`);
        resultsAppeared = true;
        break;
      }
      
      if (i % 10 === 0) {
        console.log(`⏳ Still waiting... (${i + 1}s)`);
      }
    }
    
    if (!resultsAppeared) {
      console.log('❌ CRITICAL: Results never appeared after 60 seconds');
      await browser.close();
      return;
    }
    
    // Step 4: Analyze what's actually displayed
    console.log('\n4️⃣ Analyzing Results Display...');
    
    // Check if we have the new full consulting report
    const hasFullReport = await page.locator('.bg-gradient-to-r.from-blue-900').isVisible().catch(() => false);
    console.log('Full consulting report header:', hasFullReport ? '✅ Present' : '❌ Missing');
    
    // Check navigation tabs
    const navTabs = await page.locator('button').filter({ hasText: 'Executive Overview' }).count();
    const allNavButtons = await page.locator('nav button, .bg-white button, [class*="flex"] button').count();
    console.log('Executive Overview tabs found:', navTabs);
    console.log('All navigation buttons found:', allNavButtons);
    
    // Check for LLM content
    const hasExecutiveContent = await page.locator('text=Key Strategic Findings').isVisible().catch(() => false);
    console.log('Executive summary content:', hasExecutiveContent ? '✅ Present' : '❌ Missing');
    
    // Check for metrics
    const metricsCards = await page.locator('.text-3xl.font-bold').count();
    console.log('Metric cards found:', metricsCards);
    
    // Check console logs for data
    console.log('\n5️⃣ Analyzing Console Output...');
    const dataLogs = logs.filter(log => log.includes('FullConsultingReport received') || log.includes('LLM sections'));
    console.log('Data debug logs found:', dataLogs.length);
    dataLogs.forEach(log => console.log('📊', log));
    
    // Test navigation between sections
    console.log('\n6️⃣ Testing Section Navigation...');
    
    const sections = ['Executive Summary', 'Brand Health Assessment', 'Competitive Landscape', 'Market Context & Trends'];
    for (const section of sections) {
      // Use more specific selector for navigation tabs
      const sectionButton = page.locator('.bg-white .flex button').filter({ hasText: section }).first();
      if (await sectionButton.isVisible()) {
        await sectionButton.click();
        await page.waitForTimeout(500);
        
        // Check if content changed
        const sectionContent = await page.textContent('body');
        const hasContent = sectionContent.length > 1000; // Should have substantial content
        console.log(`${section}: ${hasContent ? '✅ Has content' : '❌ No content'} (${sectionContent.length} chars)`);
      } else {
        console.log(`${section}: ❌ Tab not found`);
      }
    }
    
    // Step 7: Check specific content quality
    console.log('\n7️⃣ Checking Content Quality...');
    
    // Go back to executive summary
    await page.locator('.bg-white .flex button').filter({ hasText: 'Executive Summary' }).first().click();
    await page.waitForTimeout(500);
    
    // Check for placeholder text (bad)
    const hasPlaceholder = await page.locator('text=not available').count();
    console.log('Placeholder text instances:', hasPlaceholder);
    
    // Check for real analysis content (good)
    const hasRealContent = await page.locator('text=Tesla').count();
    console.log('Tesla mentions found:', hasRealContent);
    
    // Check for McKinsey-level content
    const hasStrategicContent = await page.locator('text=strategic').count() + 
                               await page.locator('text=competitive').count() + 
                               await page.locator('text=market').count();
    console.log('Strategic/consulting keywords found:', hasStrategicContent);
    
    // Step 8: Test color display
    console.log('\n8️⃣ Testing Visual Elements...');
    
    await page.locator('.bg-white .flex button').filter({ hasText: 'Appendix & Data Sources' }).first().click();
    await page.waitForTimeout(500);
    
    const colorSwatches = await page.locator('[style*="backgroundColor"]').count();
    console.log('Color swatches found:', colorSwatches);
    
    // Step 9: Final assessment
    console.log('\n9️⃣ FINAL ASSESSMENT...');
    
    const isWorking = hasFullReport && allNavButtons >= 6 && hasPlaceholder < 5 && hasStrategicContent > 10;
    console.log('Overall Status:', isWorking ? '✅ WORKING' : '❌ STILL BROKEN');
    
    if (!isWorking) {
      console.log('\n🚨 ISSUES FOUND:');
      if (!hasFullReport) console.log('- Missing full consulting report layout');
      if (allNavButtons < 6) console.log('- Navigation tabs not working');
      if (hasPlaceholder >= 5) console.log('- Too much placeholder text');
      if (hasStrategicContent <= 10) console.log('- Insufficient real content');
      
      console.log('\n📸 Taking screenshot for analysis...');
      await page.screenshot({ path: 'consulting-report-debug.png', fullPage: true });
    }
    
    // Step 10: Get current backend data for comparison
    console.log('\n🔟 Checking Backend Data...');
    
    const response = await page.evaluate(async () => {
      try {
        const resp = await fetch('http://localhost:8000/api/analyze/analysis-1751341580/results');
        const data = await resp.json();
        return {
          success: data.success,
          sectionsCount: Object.keys(data.data?.parsed_sections || {}).length,
          metricsCount: Object.keys(data.data?.key_metrics || {}).length,
          hasExecutive: !!data.data?.parsed_sections?.executive_summary
        };
      } catch (e) {
        return { error: e.message };
      }
    });
    
    console.log('Backend data check:', response);
    
    // Final recommendation
    if (isWorking) {
      console.log('\n🎉 SUCCESS: Consulting report is working properly!');
    } else {
      console.log('\n💡 NEXT ACTIONS NEEDED:');
      console.log('1. Fix data transmission from backend to frontend');
      console.log('2. Ensure LLM sections are properly displayed');
      console.log('3. Replace any remaining placeholder text');
      console.log('4. Verify navigation and content switching');
    }
    
  } catch (error) {
    console.log('❌ Test failed:', error.message);
  } finally {
    await browser.close();
  }
}

debugConsultingReport();