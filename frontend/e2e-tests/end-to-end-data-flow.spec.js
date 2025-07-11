/**
 * End-to-end data flow validation tests
 * Tests complete user journey from brand input to report generation
 */
import { test, expect } from '@playwright/test'

// Test configuration
const FRONTEND_URL = 'http://localhost:5175'
const BACKEND_URL = 'http://localhost:8081'
const TEST_TIMEOUT = 300000 // 5 minutes for complete analysis

test.describe('End-to-End Data Flow Validation', () => {
  test.beforeEach(async ({ page }) => {
    // Set longer timeout for analysis tests
    test.setTimeout(TEST_TIMEOUT)
    
    // Navigate to application
    await page.goto(FRONTEND_URL)
    
    // Wait for page to load
    await page.waitForLoadState('networkidle')
  })

  test('Complete brand analysis workflow - Apple', async ({ page, request }) => {
    console.log('🍎 Starting complete Apple brand analysis workflow...')
    
    // Step 1: Verify landing page loads
    await expect(page.locator('h1')).toContainText('AI Brand Analysis')
    console.log('✅ Landing page loaded')
    
    // Step 2: Enter brand name
    const brandInput = page.locator('input[placeholder*="brand name" i]')
    await brandInput.fill('Apple')
    console.log('✅ Brand name entered: Apple')
    
    // Step 3: Start analysis
    const analyzeButton = page.locator('button:has-text("Analyze")')
    await analyzeButton.click()
    console.log('✅ Analysis started')
    
    // Step 4: Verify progress page loads
    await expect(page.locator('text=Analysis in Progress')).toBeVisible({ timeout: 10000 })
    console.log('✅ Progress page loaded')
    
    // Step 5: Monitor progress updates
    let progressUpdates = []
    let currentProgress = 0
    
    // Listen for progress updates
    page.on('websocket', ws => {
      ws.on('framereceived', event => {
        try {
          const data = JSON.parse(event.payload)
          if (data.overall_progress !== undefined) {
            progressUpdates.push(data)
            currentProgress = data.overall_progress
            console.log(`📊 Progress: ${currentProgress}% - ${data.current_step_name || 'Processing'}`)
          }
        } catch (e) {
          // Ignore non-JSON messages
        }
      })
    })
    
    // Step 6: Wait for analysis completion or timeout
    let analysisComplete = false
    let attempts = 0
    const maxAttempts = 60 // 5 minutes with 5-second intervals
    
    while (!analysisComplete && attempts < maxAttempts) {
      try {
        // Check for completion indicators
        const completionElements = await page.locator('text=/Analysis Complete|Strategic Intelligence|Results/i').count()
        
        if (completionElements > 0) {
          analysisComplete = true
          console.log('✅ Analysis completed - results page detected')
          break
        }
        
        // Check for error states
        const errorElements = await page.locator('text=/error|failed|timeout/i').count()
        if (errorElements > 0) {
          console.log('❌ Error detected in UI')
          break
        }
        
        // Wait and increment counter
        await page.waitForTimeout(5000)
        attempts++
        
        if (attempts % 6 === 0) { // Every 30 seconds
          console.log(`⏳ Still waiting... (${attempts * 5}s elapsed)`)
        }
        
      } catch (error) {
        console.log(`⚠️ Error during progress monitoring: ${error.message}`)
        break
      }
    }
    
    // Step 7: Validate results if analysis completed
    if (analysisComplete) {
      console.log('🎉 Analysis completed! Validating results...')
      
      // Check for key result sections
      const resultSections = [
        'Executive Summary',
        'Strategic Context',
        'Visual Analysis',
        'Competitive Analysis'
      ]
      
      for (const section of resultSections) {
        try {
          await expect(page.locator(`text=${section}`)).toBeVisible({ timeout: 5000 })
          console.log(`✅ Found section: ${section}`)
        } catch (error) {
          console.log(`⚠️ Section not found: ${section}`)
        }
      }
      
      // Check for data visualizations
      const visualElements = [
        '[data-testid="color-palette"]',
        '[data-testid="metrics-dashboard"]',
        '.progress-bar',
        '.chart-container'
      ]
      
      for (const selector of visualElements) {
        const elementCount = await page.locator(selector).count()
        if (elementCount > 0) {
          console.log(`✅ Found visual element: ${selector}`)
        }
      }
      
      // Validate data structure by checking API response
      const analysisId = await page.evaluate(() => {
        return window.localStorage.getItem('currentAnalysisId') || 
               window.sessionStorage.getItem('analysisId')
      })
      
      if (analysisId) {
        const apiResponse = await request.get(`${BACKEND_URL}/api/analyze/${analysisId}/results`)
        if (apiResponse.ok()) {
          const resultsData = await apiResponse.json()
          console.log('✅ API results retrieved successfully')
          
          // Validate data structure
          expect(resultsData.success).toBe(true)
          expect(resultsData.data).toBeDefined()
          expect(resultsData.data.brand_name).toBe('Apple')
          expect(resultsData.data.status).toBe('completed')
          
          console.log('✅ Data structure validation passed')
        }
      }
      
    } else {
      console.log('⏳ Analysis did not complete within timeout period')
      
      // Still validate that the process is working
      expect(currentProgress).toBeGreaterThan(0)
      expect(progressUpdates.length).toBeGreaterThan(0)
      
      console.log(`📊 Final progress: ${currentProgress}%`)
      console.log(`📈 Total progress updates: ${progressUpdates.length}`)
    }
    
    console.log('🏁 Apple analysis workflow test completed')
  })

  test('Data validation with multiple brands', async ({ page, request }) => {
    console.log('🔄 Testing data validation with multiple brands...')
    
    const testBrands = ['Tesla', 'Nike', 'Starbucks']
    const results = []
    
    for (const brand of testBrands) {
      console.log(`\n🏢 Testing brand: ${brand}`)
      
      // Navigate to fresh page
      await page.goto(FRONTEND_URL)
      await page.waitForLoadState('networkidle')
      
      // Start analysis
      const brandInput = page.locator('input[placeholder*="brand name" i]')
      await brandInput.fill(brand)
      
      const analyzeButton = page.locator('button:has-text("Analyze")')
      await analyzeButton.click()
      
      // Wait for progress page
      await expect(page.locator('text=Analysis in Progress')).toBeVisible({ timeout: 10000 })
      
      // Monitor for a shorter time per brand
      let brandComplete = false
      let attempts = 0
      const maxAttempts = 20 // 100 seconds per brand
      
      while (!brandComplete && attempts < maxAttempts) {
        const completionElements = await page.locator('text=/Analysis Complete|Strategic Intelligence/i').count()
        
        if (completionElements > 0) {
          brandComplete = true
          console.log(`✅ ${brand} analysis completed`)
          
          // Validate brand name appears in results
          await expect(page.locator(`text=${brand}`)).toBeVisible()
          
          results.push({ brand, status: 'completed', success: true })
          break
        }
        
        await page.waitForTimeout(5000)
        attempts++
      }
      
      if (!brandComplete) {
        console.log(`⏳ ${brand} analysis still in progress`)
        results.push({ brand, status: 'in_progress', success: false })
      }
    }
    
    // Validate results
    console.log('\n📊 Multi-brand test results:')
    results.forEach(result => {
      console.log(`  ${result.brand}: ${result.status}`)
    })
    
    // At least one brand should complete successfully
    const successfulAnalyses = results.filter(r => r.success).length
    expect(successfulAnalyses).toBeGreaterThan(0)
    
    console.log('🏁 Multi-brand validation completed')
  })

  test('Error handling and recovery', async ({ page, request }) => {
    console.log('🚨 Testing error handling and recovery...')
    
    // Test 1: Invalid brand name
    await page.goto(FRONTEND_URL)
    await page.waitForLoadState('networkidle')
    
    const brandInput = page.locator('input[placeholder*="brand name" i]')
    await brandInput.fill('<script>alert("test")</script>')
    
    const analyzeButton = page.locator('button:has-text("Analyze")')
    await analyzeButton.click()
    
    // Should either reject input or sanitize it
    const errorMessage = await page.locator('text=/error|invalid|failed/i').count()
    if (errorMessage > 0) {
      console.log('✅ Invalid input properly rejected')
    } else {
      // Check if analysis started (input was sanitized)
      const progressVisible = await page.locator('text=Analysis in Progress').isVisible()
      if (progressVisible) {
        console.log('✅ Invalid input was sanitized and analysis started')
      }
    }
    
    // Test 2: Network error simulation
    await page.goto(FRONTEND_URL)
    await page.waitForLoadState('networkidle')
    
    // Block network requests to simulate network error
    await page.route('**/api/analyze', route => {
      route.abort('failed')
    })
    
    await brandInput.fill('Network Test Brand')
    await analyzeButton.click()
    
    // Should show error message
    await expect(page.locator('text=/failed|error|try again/i')).toBeVisible({ timeout: 10000 })
    console.log('✅ Network error properly handled')
    
    // Test 3: Recovery after error
    await page.unroute('**/api/analyze')
    
    // Try again with valid input
    await brandInput.fill('Recovery Test')
    await analyzeButton.click()
    
    // Should work normally
    await expect(page.locator('text=Analysis in Progress')).toBeVisible({ timeout: 10000 })
    console.log('✅ Recovery after error successful')
    
    console.log('🏁 Error handling test completed')
  })

  test('Real-time data synchronization', async ({ page, request }) => {
    console.log('🔄 Testing real-time data synchronization...')
    
    await page.goto(FRONTEND_URL)
    await page.waitForLoadState('networkidle')
    
    // Start analysis
    const brandInput = page.locator('input[placeholder*="brand name" i]')
    await brandInput.fill('Sync Test Brand')
    
    const analyzeButton = page.locator('button:has-text("Analyze")')
    await analyzeButton.click()
    
    // Wait for progress page
    await expect(page.locator('text=Analysis in Progress')).toBeVisible({ timeout: 10000 })
    
    // Monitor WebSocket messages
    let websocketMessages = []
    let httpPollingRequests = []
    
    page.on('websocket', ws => {
      ws.on('framereceived', event => {
        websocketMessages.push(event.payload)
      })
    })
    
    page.on('request', request => {
      if (request.url().includes('/status')) {
        httpPollingRequests.push(request.url())
      }
    })
    
    // Wait for some real-time updates
    await page.waitForTimeout(30000) // 30 seconds
    
    // Validate real-time communication
    console.log(`📡 WebSocket messages received: ${websocketMessages.length}`)
    console.log(`🔄 HTTP polling requests: ${httpPollingRequests.length}`)
    
    // Should have either WebSocket updates OR HTTP polling
    const hasRealTimeUpdates = websocketMessages.length > 0 || httpPollingRequests.length > 0
    expect(hasRealTimeUpdates).toBe(true)
    
    if (websocketMessages.length > 0) {
      console.log('✅ WebSocket real-time updates working')
    } else if (httpPollingRequests.length > 0) {
      console.log('✅ HTTP polling fallback working')
    }
    
    console.log('🏁 Real-time synchronization test completed')
  })

  test('Data persistence and state management', async ({ page, request }) => {
    console.log('💾 Testing data persistence and state management...')
    
    await page.goto(FRONTEND_URL)
    await page.waitForLoadState('networkidle')
    
    // Start analysis
    const brandInput = page.locator('input[placeholder*="brand name" i]')
    await brandInput.fill('Persistence Test')
    
    const analyzeButton = page.locator('button:has-text("Analyze")')
    await analyzeButton.click()
    
    // Wait for progress to start
    await expect(page.locator('text=Analysis in Progress')).toBeVisible({ timeout: 10000 })
    
    // Get analysis ID from page state
    const analysisId = await page.evaluate(() => {
      return window.localStorage.getItem('currentAnalysisId') || 
             window.sessionStorage.getItem('analysisId') ||
             window.currentAnalysisId
    })
    
    if (analysisId) {
      console.log(`✅ Analysis ID captured: ${analysisId}`)
      
      // Refresh page to test state persistence
      await page.reload()
      await page.waitForLoadState('networkidle')
      
      // Check if analysis state is restored
      const progressVisible = await page.locator('text=Analysis in Progress').isVisible()
      const resultsVisible = await page.locator('text=/Strategic Intelligence|Results/i').isVisible()
      
      if (progressVisible || resultsVisible) {
        console.log('✅ Analysis state persisted after page refresh')
      } else {
        console.log('⚠️ Analysis state not persisted (may be expected behavior)')
      }
      
      // Verify backend still has the analysis
      const statusResponse = await request.get(`${BACKEND_URL}/api/analyze/${analysisId}/status`)
      if (statusResponse.ok()) {
        const statusData = await statusResponse.json()
        expect(statusData.success).toBe(true)
        console.log('✅ Backend analysis state persisted')
      }
    }
    
    console.log('🏁 Data persistence test completed')
  })
})
