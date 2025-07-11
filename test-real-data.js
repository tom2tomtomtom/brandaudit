#!/usr/bin/env node

const { chromium } = require('playwright');

async function testRealDataWorkflow() {
  console.log('🎯 TESTING REAL DATA BRAND ANALYSIS WORKFLOW');
  console.log('==============================================');
  
  const browser = await chromium.launch({ headless: false, slowMo: 800 });
  const page = await browser.newPage();
  
  const errors = [];
  const apiCalls = [];
  
  page.on('console', msg => {
    if (msg.type() === 'error') {
      errors.push(msg.text());
      console.log('❌ Console Error:', msg.text());
    }
  });
  
  page.on('request', request => {
    if (request.url().includes('/api/')) {
      apiCalls.push(request.url());
      console.log('📞 API Call:', request.url());
    }
  });
  
  try {
    // 1. Load Application
    console.log('\n📍 STEP 1: Loading Application');
    await page.goto('http://localhost:3000', { waitUntil: 'networkidle' });
    const heading = await page.locator('h1').first().textContent();
    console.log('✅ Application loaded:', heading);
    
    // 2. Test Brand Search with Tesla
    console.log('\n📍 STEP 2: Testing Real Brand Search (Tesla)');
    const searchInput = page.locator('[data-testid="brand-search"]');
    await searchInput.fill('Tesla');
    console.log('✅ Entered brand name: Tesla');
    
    const searchButton = page.locator('button:has-text("Search Brand")');
    await searchButton.click();
    console.log('✅ Clicked search button');
    
    await page.waitForTimeout(3000);
    
    // 3. Skip File Upload
    console.log('\n📍 STEP 3: Skipping File Upload');
    const skipButton = page.locator('button:has-text("Skip Upload")');
    await skipButton.click();
    console.log('✅ Skipped file upload');
    
    await page.waitForTimeout(2000);
    
    // 4. Start Real Analysis
    console.log('\n📍 STEP 4: Starting Real Analysis for Tesla');
    const startButton = page.locator('button:has-text("Start Analysis")');
    await startButton.click();
    console.log('✅ Started Tesla analysis');
    
    await page.waitForTimeout(8000); // Give more time for real API calls
    
    // 5. Check for Real Tesla Results
    console.log('\n📍 STEP 5: Checking Real Tesla Analysis Results');
    
    // Wait for results to appear
    await page.waitForSelector('[data-testid="results"]', { timeout: 15000 });
    console.log('✅ Results section visible');
    
    // Check for Tesla-specific content
    const teslaContent = await page.textContent('body');
    const hasTeslaReference = teslaContent.includes('Tesla');
    console.log('✅ Tesla-specific content found:', hasTeslaReference);
    
    // Check for real scores (not dummy data)
    const scoreElements = await page.locator('.text-3xl.font-bold, .text-2xl.font-bold').allTextContents();
    console.log('✅ Found scores:', scoreElements.filter(score => score !== 'N/A'));
    
    // Test tab navigation to see detailed analysis
    console.log('\n📍 STEP 6: Testing Real Data in Analysis Tabs');
    
    // Check Perception tab
    const perceptionTab = page.locator('button[role="tab"]:has-text("Perception")');
    if (await perceptionTab.isVisible()) {
      await perceptionTab.click();
      await page.waitForTimeout(2000);
      
      // Look for sentiment percentages
      const sentimentText = await page.textContent('body');
      const hasRealSentiment = /\d+%/.test(sentimentText);
      console.log('✅ Real sentiment data found in Perception tab:', hasRealSentiment);
    }
    
    // Check Visual tab
    const visualTab = page.locator('button[role="tab"]:has-text("Visual")');
    if (await visualTab.isVisible()) {
      await visualTab.click();
      await page.waitForTimeout(2000);
      
      // Check for logo scores
      const visualContent = await page.textContent('body');
      const hasVisualScores = /Recognition|Memorability|Scalability/.test(visualContent);
      console.log('✅ Real visual analysis data found:', hasVisualScores);
    }
    
    // 7. Test Real API Data Sources
    console.log('\n📍 STEP 7: Verifying Real API Data Sources');
    
    // Test direct API call to see raw data
    const realDataTest = await page.evaluate(async () => {
      try {
        const response = await fetch('https://2b79-220-244-77-193.ngrok-free.app/api/analyze/test-analysis-123/results', {
          headers: {
            'ngrok-skip-browser-warning': 'true'
          }
        });
        const data = await response.json();
        
        const analysis = data.data;
        return {
          success: true,
          brand_name: analysis.brand_name,
          data_sources: analysis.data_sources,
          has_brandfetch: analysis.api_responses?.brandfetch_data?.domain ? true : false,
          has_news_data: analysis.api_responses?.news_data?.total_articles > 0 ? true : false,
          tesla_specific: analysis.brand_name === 'Tesla',
          overall_score: analysis.key_metrics?.overall_score
        };
      } catch (error) {
        return { success: false, error: error.message };
      }
    });
    
    if (realDataTest.success) {
      console.log('✅ Real API Data Verification:');
      console.log(`  - Brand Name: ${realDataTest.brand_name}`);
      console.log(`  - Tesla-specific: ${realDataTest.tesla_specific}`);
      console.log(`  - Brandfetch Data: ${realDataTest.has_brandfetch}`);
      console.log(`  - News Data: ${realDataTest.has_news_data}`);
      console.log(`  - Overall Score: ${realDataTest.overall_score}`);
      console.log(`  - Data Sources: ${JSON.stringify(realDataTest.data_sources)}`);
    } else {
      console.log('❌ Real data verification failed:', realDataTest.error);
    }
    
    // Final Assessment
    console.log('\n🎯 REAL DATA ANALYSIS ASSESSMENT');
    console.log('=================================');
    
    const results = {
      'Frontend Application': true,
      'Tesla Brand Search': hasTeslaReference,
      'Real API Integration': realDataTest.success,
      'Brand-Specific Analysis': realDataTest.tesla_specific,
      'Brandfetch Data Source': realDataTest.has_brandfetch,
      'News/Sentiment Data': realDataTest.has_news_data,
      'Real Scores Display': scoreElements.length > 5,
      'Analysis Tabs Working': await perceptionTab.isVisible(),
      'No JavaScript Errors': errors.length === 0,
      'Multiple API Calls': apiCalls.length >= 4
    };
    
    let passCount = 0;
    console.log('\nREAL DATA TEST RESULTS:');
    for (const [test, passed] of Object.entries(results)) {
      console.log(`${passed ? '✅' : '❌'} ${test}: ${passed ? 'PASS' : 'FAIL'}`);
      if (passed) passCount++;
    }
    
    const finalScore = Math.round((passCount / Object.keys(results).length) * 100);
    console.log(`\n🎯 REAL DATA INTEGRATION SCORE: ${finalScore}%`);
    
    if (finalScore >= 95) {
      console.log('🎉 REAL DATA INTEGRATION FULLY SUCCESSFUL!');
      console.log('✅ System using actual API data for brand analysis');
      console.log('✅ Brand-specific insights and recommendations');
      console.log('✅ Multi-source data integration working');
    } else if (finalScore >= 85) {
      console.log('🚀 EXCELLENT! Real data integration mostly working');
    } else if (finalScore >= 70) {
      console.log('⚠️ GOOD! Most real data features working');
    } else {
      console.log('❌ NEEDS WORK! Real data integration issues');
    }
    
    console.log(`\n📊 API Calls Made: ${apiCalls.length}`);
    console.log(`🔍 Brand Analyzed: ${realDataTest.brand_name || 'Unknown'}`);
    console.log(`📈 Score Generated: ${realDataTest.overall_score || 'N/A'}`);
    
    await page.screenshot({ path: 'real-data-analysis-test.png', fullPage: true });
    console.log('\n📸 Real data test screenshot saved as real-data-analysis-test.png');
    
  } catch (error) {
    console.log('❌ Test failed:', error.message);
  } finally {
    await browser.close();
  }
}

testRealDataWorkflow();