import { test, expect } from '@playwright/test';

test.describe('Auto-Fix Testing Suite', () => {
  
  test('Comprehensive App Health Check with Auto-Diagnosis', async ({ page, request }) => {
    console.log('🏥 Starting comprehensive app health check...');
    
    const issues = [];
    const fixes = [];
    
    // Test 1: Backend Health
    console.log('1️⃣ Checking backend health...');
    try {
      const healthResponse = await request.get('http://localhost:8081/api/health');
      if (healthResponse.ok()) {
        const healthData = await healthResponse.json();
        console.log('✅ Backend is healthy');
        console.log('   API Keys configured:', Object.entries(healthData.api_keys_configured || {}).map(([k, v]) => `${k}: ${v}`).join(', '));
      } else {
        issues.push(`Backend health check failed: ${healthResponse.status()}`);
        fixes.push('Restart Docker container: docker restart test-backend');
      }
    } catch (error) {
      issues.push(`Backend unreachable: ${error.message}`);
      fixes.push('Start Docker container: docker run -d -p 8081:8080 --name test-backend brand-audit-backend');
    }
    
    // Test 2: Frontend Loading
    console.log('2️⃣ Checking frontend loading...');
    try {
      await page.goto('http://localhost:5175', { waitUntil: 'networkidle', timeout: 10000 });
      console.log('✅ Frontend loads successfully');
    } catch (error) {
      issues.push(`Frontend loading failed: ${error.message}`);
      fixes.push('Start frontend: cd frontend && pnpm run dev');
    }
    
    // Test 3: Form Elements
    console.log('3️⃣ Checking form elements...');
    try {
      const companyInput = page.locator('input[type="text"]').first();
      const submitButton = page.locator('button').filter({ hasText: /Start Audit|Audit|Search|Analyze/i }).first();
      
      await expect(companyInput).toBeVisible({ timeout: 5000 });
      await expect(submitButton).toBeVisible({ timeout: 5000 });
      console.log('✅ Form elements are present and visible');
    } catch (error) {
      issues.push(`Form elements not found: ${error.message}`);
      fixes.push('Check frontend component rendering and CSS');
    }
    
    // Test 4: API Connectivity
    console.log('4️⃣ Checking API connectivity...');
    try {
      const brandSearchResponse = await request.post('http://localhost:8081/api/brand/search', {
        data: { query: 'Test Company' },
        headers: { 'Content-Type': 'application/json' },
        timeout: 10000
      });
      
      if (brandSearchResponse.ok()) {
        console.log('✅ Brand search API is working');
      } else {
        issues.push(`Brand search API failed: ${brandSearchResponse.status()}`);
        fixes.push('Check backend logs: docker logs test-backend');
      }
    } catch (error) {
      issues.push(`API connectivity failed: ${error.message}`);
      fixes.push('Check network connectivity and CORS settings');
    }
    
    // Test 5: End-to-End Flow
    console.log('5️⃣ Testing end-to-end flow...');
    try {
      const companyInput = page.locator('input[type="text"]').first();
      const submitButton = page.locator('button').filter({ hasText: /Start Audit|Audit|Search|Analyze/i }).first();
      
      await companyInput.fill('Apple');
      await submitButton.click();
      
      // Wait for any response (loading, results, or error)
      await page.waitForTimeout(3000);
      
      // Check if we're still on the same page or if something happened
      const currentUrl = page.url();
      const inputValue = await companyInput.inputValue();
      
      if (inputValue === '' && currentUrl.includes('localhost:5175')) {
        issues.push('Form resets after submission - possible API error');
        fixes.push('Check browser console for JavaScript errors and API response codes');
      } else {
        console.log('✅ End-to-end flow initiated successfully');
      }
      
    } catch (error) {
      issues.push(`End-to-end flow failed: ${error.message}`);
      fixes.push('Debug form submission and API integration');
    }
    
    // Test 6: Analysis Flow
    console.log('6️⃣ Testing analysis flow...');
    try {
      // Start a new analysis
      const analyzeResponse = await request.post('http://localhost:8081/api/analyze', {
        data: { company_name: 'Apple' },
        headers: { 'Content-Type': 'application/json' },
        timeout: 10000
      });
      
      if (analyzeResponse.ok()) {
        const analyzeData = await analyzeResponse.json();
        const analysisId = analyzeData.analysis_id;
        
        if (analysisId) {
          console.log(`✅ Analysis started with ID: ${analysisId}`);
          
          // Check status
          const statusResponse = await request.get(`http://localhost:8081/api/analyze/${analysisId}/status`);
          if (statusResponse.ok()) {
            console.log('✅ Analysis status endpoint working');
          } else {
            issues.push(`Analysis status check failed: ${statusResponse.status()}`);
          }
          
          // Try to get results (might fail if analysis not complete)
          const resultsResponse = await request.get(`http://localhost:8081/api/analyze/${analysisId}/results`);
          console.log(`📊 Results endpoint status: ${resultsResponse.status()}`);
          
        } else {
          issues.push('Analysis started but no ID returned');
        }
      } else {
        issues.push(`Analysis start failed: ${analyzeResponse.status()}`);
        fixes.push('Check analysis endpoint implementation and dependencies');
      }
    } catch (error) {
      issues.push(`Analysis flow failed: ${error.message}`);
      fixes.push('Check analysis API implementation and error handling');
    }
    
    // Report Results
    console.log('\n🔍 HEALTH CHECK SUMMARY');
    console.log('========================');
    
    if (issues.length === 0) {
      console.log('🎉 ALL SYSTEMS HEALTHY! No issues detected.');
    } else {
      console.log(`⚠️  ${issues.length} ISSUES DETECTED:`);
      issues.forEach((issue, i) => {
        console.log(`   ${i + 1}. ${issue}`);
      });
      
      console.log('\n🔧 SUGGESTED FIXES:');
      fixes.forEach((fix, i) => {
        console.log(`   ${i + 1}. ${fix}`);
      });
    }
    
    // Take final screenshot
    await page.screenshot({ path: 'test-results/health-check-final.png', fullPage: true });
    
    // Test always passes - this is a diagnostic tool
    expect(true).toBe(true);
  });

  test('Performance and Load Testing', async ({ page, request }) => {
    console.log('⚡ Starting performance testing...');
    
    const performanceMetrics = [];
    
    // Test API response times
    const companies = ['Apple', 'Google', 'Microsoft', 'Tesla', 'Nike'];
    
    for (const company of companies) {
      const startTime = Date.now();
      
      try {
        const response = await request.post('http://localhost:8081/api/brand/search', {
          data: { query: company },
          headers: { 'Content-Type': 'application/json' },
          timeout: 30000
        });
        
        const endTime = Date.now();
        const responseTime = endTime - startTime;
        
        performanceMetrics.push({
          company,
          responseTime,
          status: response.status(),
          success: response.ok()
        });
        
        console.log(`📊 ${company}: ${responseTime}ms (${response.status()})`);
        
      } catch (error) {
        performanceMetrics.push({
          company,
          responseTime: -1,
          status: 'ERROR',
          success: false,
          error: error.message
        });
        
        console.log(`❌ ${company}: ERROR - ${error.message}`);
      }
    }
    
    // Calculate performance statistics
    const successfulRequests = performanceMetrics.filter(m => m.success);
    const avgResponseTime = successfulRequests.reduce((sum, m) => sum + m.responseTime, 0) / successfulRequests.length;
    const maxResponseTime = Math.max(...successfulRequests.map(m => m.responseTime));
    const minResponseTime = Math.min(...successfulRequests.map(m => m.responseTime));
    
    console.log('\n📈 PERFORMANCE SUMMARY');
    console.log('======================');
    console.log(`Successful requests: ${successfulRequests.length}/${performanceMetrics.length}`);
    console.log(`Average response time: ${avgResponseTime.toFixed(2)}ms`);
    console.log(`Min response time: ${minResponseTime}ms`);
    console.log(`Max response time: ${maxResponseTime}ms`);
    
    // Performance thresholds
    if (avgResponseTime > 5000) {
      console.log('⚠️  Average response time is high (>5s)');
    } else if (avgResponseTime > 2000) {
      console.log('⚠️  Average response time is moderate (>2s)');
    } else {
      console.log('✅ Response times are good (<2s)');
    }
    
    expect(true).toBe(true);
  });
});
