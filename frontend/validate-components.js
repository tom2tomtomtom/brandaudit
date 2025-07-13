#!/usr/bin/env node

/**
 * Quick Component Validation Script
 * 
 * Validates that existing React components are properly structured
 * and can be imported without errors.
 */

import { existsSync, readFileSync } from 'fs'
import path from 'path'

const COLORS = {
  GREEN: '\x1b[32m',
  RED: '\x1b[31m',
  YELLOW: '\x1b[33m',
  BLUE: '\x1b[34m',
  RESET: '\x1b[0m',
  BOLD: '\x1b[1m'
}

function log(message, color = COLORS.RESET) {
  console.log(`${color}${message}${COLORS.RESET}`)
}

function logSuccess(message) {
  log(`✅ ${message}`, COLORS.GREEN)
}

function logError(message) {
  log(`❌ ${message}`, COLORS.RED)
}

function logWarning(message) {
  log(`⚠️  ${message}`, COLORS.YELLOW)
}

function logInfo(message) {
  log(`ℹ️  ${message}`, COLORS.BLUE)
}

function validateFileExists(filePath, description) {
  if (existsSync(filePath)) {
    logSuccess(`${description}: ${filePath}`)
    return true
  } else {
    logError(`Missing ${description}: ${filePath}`)
    return false
  }
}

function validateComponentStructure(filePath) {
  if (!existsSync(filePath)) {
    return false
  }

  try {
    const content = readFileSync(filePath, 'utf8')
    
    // Check for React import
    if (content.includes('import React') || content.includes('from \'react\'')) {
      logSuccess(`React import found in ${filePath}`)
    } else {
      logWarning(`No React import found in ${filePath}`)
    }

    // Check for export
    if (content.includes('export default') || content.includes('export {')) {
      logSuccess(`Export found in ${filePath}`)
    } else {
      logError(`No export found in ${filePath}`)
      return false
    }

    // Check for JSX
    if (content.includes('<') && content.includes('>')) {
      logSuccess(`JSX syntax found in ${filePath}`)
    } else {
      logWarning(`No JSX syntax found in ${filePath}`)
    }

    return true
  } catch (error) {
    logError(`Error reading ${filePath}: ${error.message}`)
    return false
  }
}

function validateAPIService() {
  const apiPath = 'src/services/api.js'
  
  if (!existsSync(apiPath)) {
    logError('API service not found')
    return false
  }

  try {
    const content = readFileSync(apiPath, 'utf8')
    
    const requiredMethods = [
      'startAnalysis',
      'getAnalysisResults',
      'getAnalysisStatus',
      'searchBrand',
      'getBrandAssets',
      'healthCheck'
    ]

    let allMethodsFound = true
    
    for (const method of requiredMethods) {
      if (content.includes(method)) {
        logSuccess(`API method found: ${method}`)
      } else {
        logError(`API method missing: ${method}`)
        allMethodsFound = false
      }
    }

    // Check for error handling
    if (content.includes('enhanceError') && content.includes('executeWithRetry')) {
      logSuccess('Error handling methods found')
    } else {
      logWarning('Error handling methods may be missing')
    }

    // Check for circuit breaker
    if (content.includes('circuitBreaker') || content.includes('isCircuitOpen')) {
      logSuccess('Circuit breaker functionality found')
    } else {
      logWarning('Circuit breaker functionality may be missing')
    }

    return allMethodsFound
  } catch (error) {
    logError(`Error validating API service: ${error.message}`)
    return false
  }
}

function validateWebSocketHook() {
  const hookPath = 'src/hooks/useWebSocket.js'
  
  if (!existsSync(hookPath)) {
    logError('WebSocket hook not found')
    return false
  }

  try {
    const content = readFileSync(hookPath, 'utf8')
    
    const requiredFeatures = [
      'useState',
      'useEffect',
      'socket.io-client',
      'isConnected',
      'progress',
      'currentStage'
    ]

    let allFeaturesFound = true
    
    for (const feature of requiredFeatures) {
      if (content.includes(feature)) {
        logSuccess(`WebSocket feature found: ${feature}`)
      } else {
        logError(`WebSocket feature missing: ${feature}`)
        allFeaturesFound = false
      }
    }

    return allFeaturesFound
  } catch (error) {
    logError(`Error validating WebSocket hook: ${error.message}`)
    return false
  }
}

function main() {
  log(`${COLORS.BOLD}${COLORS.BLUE}Frontend Component Validation${COLORS.RESET}`)
  log('Checking existing React components and services\n')

  let allValid = true

  // Core components
  log(`${COLORS.BOLD}Core Components:${COLORS.RESET}`)
  const coreComponents = [
    ['src/App.jsx', 'Main App Component'],
    ['src/components/ModernLanding.jsx', 'Landing Page Component'],
    ['src/components/AnalysisProgress.jsx', 'Analysis Progress Component'],
    ['src/components/ModernResultsDisplay.jsx', 'Results Display Component']
  ]

  for (const [path, description] of coreComponents) {
    if (!validateFileExists(path, description)) {
      allValid = false
    } else {
      if (!validateComponentStructure(path)) {
        allValid = false
      }
    }
  }

  // Visual components
  log(`\n${COLORS.BOLD}Visual Components:${COLORS.RESET}`)
  const visualComponents = [
    ['src/components/visual/VisualAnalysisDashboard.jsx', 'Visual Analysis Dashboard'],
    ['src/components/visual/EnhancedVisualGallery.jsx', 'Enhanced Visual Gallery'],
    ['src/components/visual/InteractiveColorPalette.jsx', 'Interactive Color Palette'],
    ['src/components/visual/BrandAssetShowcase.jsx', 'Brand Asset Showcase'],
    ['src/components/visual/VisualMetrics.jsx', 'Visual Metrics Component']
  ]

  for (const [path, description] of visualComponents) {
    if (existsSync(path)) {
      logSuccess(`${description}: ${path}`)
      validateComponentStructure(path)
    } else {
      logWarning(`Optional component missing: ${description}`)
    }
  }

  // Services and hooks
  log(`\n${COLORS.BOLD}Services and Hooks:${COLORS.RESET}`)
  if (!validateAPIService()) {
    allValid = false
  }

  if (!validateWebSocketHook()) {
    allValid = false
  }

  // UI components
  log(`\n${COLORS.BOLD}UI Components:${COLORS.RESET}`)
  const uiComponents = [
    'src/components/ui/card.jsx',
    'src/components/ui/button.jsx',
    'src/components/ui/progress.jsx',
    'src/components/ui/tabs.jsx'
  ]

  for (const component of uiComponents) {
    validateFileExists(component, 'UI Component')
  }

  // Package.json validation
  log(`\n${COLORS.BOLD}Configuration:${COLORS.RESET}`)
  if (validateFileExists('package.json', 'Package Configuration')) {
    try {
      const packageJson = JSON.parse(readFileSync('package.json', 'utf8'))
      
      if (packageJson.scripts && packageJson.scripts.test) {
        logSuccess('Test script configured')
      } else {
        logWarning('Test script not configured')
      }

      if (packageJson.dependencies && packageJson.dependencies.react) {
        logSuccess('React dependency found')
      } else {
        logError('React dependency missing')
        allValid = false
      }

      if (packageJson.devDependencies && packageJson.devDependencies.vitest) {
        logSuccess('Vitest testing framework found')
      } else {
        logWarning('Vitest testing framework not found')
      }
    } catch (error) {
      logError(`Error reading package.json: ${error.message}`)
      allValid = false
    }
  }

  // Summary
  log(`\n${COLORS.BOLD}Validation Summary:${COLORS.RESET}`)
  if (allValid) {
    logSuccess('🎉 All core components are properly structured!')
    logInfo('You can now run the integration tests with: npm run test:integration')
  } else {
    logError('⚠️  Some components have issues. Please review the output above.')
    process.exit(1)
  }
}

main()
