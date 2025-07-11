/**
 * Comprehensive UI Integration Test for Enhanced Brand Audit System
 * Tests the complete system with real UI interactions
 */

const { chromium } = require('playwright');

async function testUIIntegration() {
    console.log('🎯 Testing Enhanced Brand Audit System - UI Integration');
    console.log('='.repeat(65));
    console.log('Testing complete system with professional quality standards');
    console.log('');

    const browser = await chromium.launch({ headless: false });
    const context = await browser.newContext();
    const page = await context.newPage();

    try {
        // Navigate to the application
        console.log('🌐 Navigating to brand audit application...');
        await page.goto('http://localhost:3000');
        await page.waitForLoadState('networkidle');

        // Test 1: Brand Search and Analysis
        console.log('\n📊 Test 1: Brand Search and Analysis');
        console.log('-'.repeat(40));

        // Search for a well-known brand
        const brandName = 'Tesla';
        console.log(`🔍 Searching for brand: ${brandName}`);
        
        await page.fill('input[placeholder*="brand"], input[placeholder*="company"]', brandName);
        await page.click('button:has-text("Search"), button:has-text("Analyze")');

        // Wait for analysis to complete
        console.log('⏳ Waiting for analysis to complete...');
        await page.waitForSelector('.analysis-results, .brand-results', { timeout: 60000 });

        // Check for key results sections
        const hasResults = await page.locator('.analysis-results, .brand-results').count() > 0;
        console.log(`📊 Analysis results displayed: ${hasResults ? '✅' : '❌'}`);

        // Test 2: Report Generation
        console.log('\n📄 Test 2: Report Generation');
        console.log('-'.repeat(40));

        // Look for report generation button
        const reportButton = page.locator('button:has-text("Generate Report"), button:has-text("Download Report")');
        const hasReportButton = await reportButton.count() > 0;
        
        if (hasReportButton) {
            console.log('📝 Generating report...');
            await reportButton.click();
            
            // Wait for report generation
            await page.waitForTimeout(5000);
            
            // Check if report was generated
            const reportGenerated = await page.locator('.report-generated, .download-link').count() > 0;
            console.log(`📊 Report generated: ${reportGenerated ? '✅' : '❌'}`);
        } else {
            console.log('⚠️ Report generation button not found');
        }

        // Test 3: Visual Elements Check
        console.log('\n🎨 Test 3: Visual Elements and Data Display');
        console.log('-'.repeat(40));

        // Check for visual elements
        const hasCharts = await page.locator('canvas, .chart, .graph').count() > 0;
        const hasTables = await page.locator('table, .table').count() > 0;
        const hasMetrics = await page.locator('.metric, .score, .percentage').count() > 0;
        const hasLogos = await page.locator('img[src*="logo"], .logo').count() > 0;

        console.log(`📊 Charts/Graphs: ${hasCharts ? '✅' : '❌'}`);
        console.log(`📋 Tables: ${hasTables ? '✅' : '❌'}`);
        console.log(`📈 Metrics/Scores: ${hasMetrics ? '✅' : '❌'}`);
        console.log(`🎯 Brand Logos: ${hasLogos ? '✅' : '❌'}`);

        // Test 4: Content Quality Assessment
        console.log('\n📝 Test 4: Content Quality Assessment');
        console.log('-'.repeat(40));

        // Check for substantial content
        const pageText = await page.textContent('body');
        const contentLength = pageText.length;
        
        console.log(`📏 Total page content: ${contentLength} characters`);
        
        // Look for key professional terms
        const professionalTerms = [
            'strategic', 'competitive', 'analysis', 'recommendations',
            'market position', 'brand equity', 'implementation',
            'executive summary', 'insights'
        ];
        
        let termsFound = 0;
        for (const term of professionalTerms) {
            if (pageText.toLowerCase().includes(term)) {
                termsFound++;
            }
        }
        
        console.log(`🎯 Professional terms found: ${termsFound}/${professionalTerms.length}`);
        
        // Content quality assessment
        let contentQuality = 'POOR';
        if (contentLength >= 5000 && termsFound >= 7) {
            contentQuality = 'EXCELLENT';
        } else if (contentLength >= 3000 && termsFound >= 5) {
            contentQuality = 'GOOD';
        } else if (contentLength >= 1500 && termsFound >= 3) {
            contentQuality = 'FAIR';
        }
        
        console.log(`📊 Content Quality: ${contentQuality}`);

        // Test 5: Error Handling and Robustness
        console.log('\n🛡️ Test 5: Error Handling and Robustness');
        console.log('-'.repeat(40));

        // Test with invalid brand name
        await page.fill('input[placeholder*="brand"], input[placeholder*="company"]', 'InvalidBrandXYZ123');
        await page.click('button:has-text("Search"), button:has-text("Analyze")');
        
        await page.waitForTimeout(3000);
        
        // Check for error handling
        const hasErrorMessage = await page.locator('.error, .alert, [class*="error"]').count() > 0;
        const hasGracefulFallback = await page.textContent('body').then(text => 
            text.includes('not found') || text.includes('error') || text.includes('try again')
        );
        
        console.log(`🚨 Error handling: ${hasErrorMessage || hasGracefulFallback ? '✅' : '❌'}`);

        // Overall Assessment
        console.log('\n' + '='.repeat(65));
        console.log('🎯 OVERALL SYSTEM ASSESSMENT');
        console.log('='.repeat(65));

        const assessmentCriteria = [
            { name: 'Analysis Results', passed: hasResults },
            { name: 'Visual Elements', passed: hasCharts || hasTables || hasMetrics },
            { name: 'Content Quality', passed: contentQuality === 'EXCELLENT' || contentQuality === 'GOOD' },
            { name: 'Professional Terms', passed: termsFound >= 5 },
            { name: 'Error Handling', passed: hasErrorMessage || hasGracefulFallback }
        ];

        const passedCriteria = assessmentCriteria.filter(c => c.passed).length;
        const totalCriteria = assessmentCriteria.length;
        const successRate = (passedCriteria / totalCriteria) * 100;

        console.log(`📊 Success Rate: ${successRate.toFixed(1)}% (${passedCriteria}/${totalCriteria} criteria met)`);
        
        assessmentCriteria.forEach(criteria => {
            console.log(`   ${criteria.passed ? '✅' : '❌'} ${criteria.name}`);
        });

        if (successRate >= 80) {
            console.log('🎉 EXCELLENT: System meets professional standards!');
        } else if (successRate >= 60) {
            console.log('✅ GOOD: System is functional with minor improvements needed');
        } else if (successRate >= 40) {
            console.log('⚠️ FAIR: System needs improvements');
        } else {
            console.log('❌ POOR: System requires significant fixes');
        }

        // Recommendations
        console.log('\n📋 RECOMMENDATIONS:');
        if (!hasResults) {
            console.log('   🔧 Fix brand analysis functionality');
        }
        if (!hasCharts && !hasTables) {
            console.log('   🎨 Add visual elements (charts, tables, graphs)');
        }
        if (contentQuality === 'POOR' || contentQuality === 'FAIR') {
            console.log('   📝 Enhance content depth and professional quality');
        }
        if (termsFound < 5) {
            console.log('   🎯 Include more professional consulting terminology');
        }
        if (!hasErrorMessage && !hasGracefulFallback) {
            console.log('   🛡️ Improve error handling and user feedback');
        }

        console.log('\n🎯 UI Integration test completed!');

    } catch (error) {
        console.error('❌ Test failed with error:', error.message);
        
        // Take screenshot for debugging
        await page.screenshot({ path: 'test-failure-screenshot.png' });
        console.log('📸 Screenshot saved as test-failure-screenshot.png');
        
    } finally {
        await browser.close();
    }
}

// Run the test
if (require.main === module) {
    testUIIntegration().catch(console.error);
}

module.exports = { testUIIntegration };
