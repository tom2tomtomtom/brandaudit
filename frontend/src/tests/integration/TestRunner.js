#!/usr/bin/env node

/**
 * Comprehensive Frontend Integration Test Runner
 * 
 * This script validates existing React frontend components and their integration
 * with the backend API without replacing or modifying existing functionality.
 */

import { execSync } from 'child_process'
import { existsSync } from 'fs'
import path from 'path'

const COLORS = {
  GREEN: '\x1b[32m',
  RED: '\x1b[31m',
  YELLOW: '\x1b[33m',
  BLUE: '\x1b[34m',
  RESET: '\x1b[0m',
  BOLD: '\x1b[1m'
}

class FrontendTestRunner {
  constructor() {
    this.testResults = {
      passed: 0,
      failed: 0,
      skipped: 0,
      total: 0
    }
    this.startTime = Date.now()
  }

  log(message, color = COLORS.RESET) {
    console.log(`${color}${message}${COLORS.RESET}`)
  }

  logHeader(message) {
    this.log(`\n${COLORS.BOLD}${COLORS.BLUE}=== ${message} ===${COLORS.RESET}`)
  }

  logSuccess(message) {
    this.log(`✅ ${message}`, COLORS.GREEN)
  }

  logError(message) {
    this.log(`❌ ${message}`, COLORS.RED)
  }

  logWarning(message) {
    this.log(`⚠️  ${message}`, COLORS.YELLOW)
  }

  logInfo(message) {
    this.log(`ℹ️  ${message}`, COLORS.BLUE)
  }

  async validateEnvironment() {
    this.logHeader('Environment Validation')

    // Check if we're in the frontend directory
    if (!existsSync('package.json')) {
      this.logError('package.json not found. Please run from frontend directory.')
      process.exit(1)
    }

    // Check if node_modules exists
    if (!existsSync('node_modules')) {
      this.logWarning('node_modules not found. Installing dependencies...')
      try {
        execSync('npm install', { stdio: 'inherit' })
        this.logSuccess('Dependencies installed successfully')
      } catch (error) {
        this.logError('Failed to install dependencies')
        process.exit(1)
      }
    }

    // Check if Vite config exists
    if (existsSync('vite.config.js')) {
      this.logSuccess('Vite configuration found')
    } else {
      this.logWarning('Vite configuration not found')
    }

    // Check if Vitest is configured
    try {
      execSync('npx vitest --version', { stdio: 'pipe' })
      this.logSuccess('Vitest is available')
    } catch (error) {
      this.logError('Vitest not available. Please install testing dependencies.')
      process.exit(1)
    }
  }

  async validateExistingComponents() {
    this.logHeader('Existing Component Validation')

    const requiredComponents = [
      'src/App.jsx',
      'src/components/ModernLanding.jsx',
      'src/components/AnalysisProgress.jsx',
      'src/components/ModernResultsDisplay.jsx',
      'src/services/api.js',
      'src/hooks/useWebSocket.js'
    ]

    const visualComponents = [
      'src/components/visual/VisualAnalysisDashboard.jsx',
      'src/components/visual/EnhancedVisualGallery.jsx',
      'src/components/visual/InteractiveColorPalette.jsx',
      'src/components/visual/BrandAssetShowcase.jsx',
      'src/components/visual/VisualMetrics.jsx'
    ]

    let allComponentsExist = true

    // Check core components
    for (const component of requiredComponents) {
      if (existsSync(component)) {
        this.logSuccess(`Core component found: ${component}`)
      } else {
        this.logError(`Missing core component: ${component}`)
        allComponentsExist = false
      }
    }

    // Check visual components
    for (const component of visualComponents) {
      if (existsSync(component)) {
        this.logSuccess(`Visual component found: ${component}`)
      } else {
        this.logWarning(`Visual component missing: ${component}`)
      }
    }

    if (!allComponentsExist) {
      this.logError('Some core components are missing. Please check your project structure.')
      process.exit(1)
    }

    return true
  }

  async runIntegrationTests() {
    this.logHeader('Running Integration Tests')

    const testFiles = [
      'src/tests/integration/FrontendIntegrationTest.jsx',
      'src/tests/integration/VisualComponentsTest.jsx',
      'src/tests/integration/APIConnectivityTest.jsx'
    ]

    for (const testFile of testFiles) {
      if (existsSync(testFile)) {
        this.logInfo(`Running tests from: ${testFile}`)
        try {
          execSync(`npx vitest run ${testFile}`, { stdio: 'inherit' })
          this.logSuccess(`Tests passed: ${testFile}`)
          this.testResults.passed++
        } catch (error) {
          this.logError(`Tests failed: ${testFile}`)
          this.testResults.failed++
        }
      } else {
        this.logWarning(`Test file not found: ${testFile}`)
        this.testResults.skipped++
      }
      this.testResults.total++
    }
  }

  async validateAPIConnectivity() {
    this.logHeader('API Connectivity Validation')

    try {
      // Test if backend is running
      const response = await fetch('http://localhost:8000/api/health', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'ngrok-skip-browser-warning': 'true'
        },
        timeout: 5000
      })

      if (response.ok) {
        const data = await response.json()
        this.logSuccess(`Backend is running: ${JSON.stringify(data)}`)
        return true
      } else {
        this.logWarning(`Backend returned status: ${response.status}`)
        return false
      }
    } catch (error) {
      this.logWarning(`Backend not available: ${error.message}`)
      this.logInfo('This is expected if the backend is not currently running')
      return false
    }
  }

  async validateWebSocketConnection() {
    this.logHeader('WebSocket Connection Validation')

    try {
      // Test WebSocket endpoint availability
      const response = await fetch('http://localhost:8000/socket.io/', {
        method: 'GET',
        headers: { 'ngrok-skip-browser-warning': 'true' },
        timeout: 5000
      })

      this.logInfo(`WebSocket endpoint status: ${response.status}`)
      
      if (response.status === 200 || response.status === 400) {
        this.logSuccess('WebSocket endpoint is available')
        return true
      } else {
        this.logWarning('WebSocket endpoint may not be properly configured')
        return false
      }
    } catch (error) {
      this.logWarning(`WebSocket endpoint not available: ${error.message}`)
      this.logInfo('This is expected if the backend is not currently running')
      return false
    }
  }

  async runBuildTest() {
    this.logHeader('Build Validation')

    try {
      this.logInfo('Running production build test...')
      execSync('npm run build', { stdio: 'inherit' })
      this.logSuccess('Production build completed successfully')
      
      // Check if dist directory was created
      if (existsSync('dist')) {
        this.logSuccess('Build output directory created')
        return true
      } else {
        this.logError('Build output directory not found')
        return false
      }
    } catch (error) {
      this.logError('Production build failed')
      return false
    }
  }

  generateReport() {
    this.logHeader('Test Results Summary')

    const duration = ((Date.now() - this.startTime) / 1000).toFixed(2)
    
    this.log(`\n${COLORS.BOLD}Test Execution Summary:${COLORS.RESET}`)
    this.log(`Duration: ${duration}s`)
    this.log(`Total Tests: ${this.testResults.total}`)
    this.logSuccess(`Passed: ${this.testResults.passed}`)
    this.logError(`Failed: ${this.testResults.failed}`)
    this.logWarning(`Skipped: ${this.testResults.skipped}`)

    const successRate = this.testResults.total > 0 
      ? ((this.testResults.passed / this.testResults.total) * 100).toFixed(1)
      : 0

    this.log(`\n${COLORS.BOLD}Success Rate: ${successRate}%${COLORS.RESET}`)

    if (this.testResults.failed === 0) {
      this.logSuccess('\n🎉 All tests passed! Frontend integration is working correctly.')
    } else {
      this.logError('\n⚠️  Some tests failed. Please review the output above.')
    }
  }

  async run() {
    this.log(`${COLORS.BOLD}${COLORS.BLUE}Frontend Integration Test Runner${COLORS.RESET}`)
    this.log('Validating existing React components and API integration\n')

    try {
      await this.validateEnvironment()
      await this.validateExistingComponents()
      await this.runIntegrationTests()
      await this.validateAPIConnectivity()
      await this.validateWebSocketConnection()
      await this.runBuildTest()
    } catch (error) {
      this.logError(`Test runner failed: ${error.message}`)
      process.exit(1)
    } finally {
      this.generateReport()
    }
  }
}

// Run the test runner if this file is executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  const runner = new FrontendTestRunner()
  runner.run().catch(error => {
    console.error('Test runner crashed:', error)
    process.exit(1)
  })
}

export default FrontendTestRunner
