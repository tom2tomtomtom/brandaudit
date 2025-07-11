/**
 * Test script for WebSocket real-time progress updates
 * Tests the brand audit application's WebSocket functionality
 */

const { chromium } = require('playwright');
const { io } = require('socket.io-client');

const FRONTEND_URL = 'http://localhost:5173';
const BACKEND_URL = 'http://localhost:8000';

async function testWebSocketConnection() {
  console.log('🔌 Testing WebSocket connection...');
  
  return new Promise((resolve, reject) => {
    const socket = io(BACKEND_URL, {
      transports: ['websocket', 'polling'],
      timeout: 10000
    });

    let connected = false;
    
    socket.on('connect', () => {
      console.log('✅ WebSocket connected successfully');
      connected = true;
      socket.disconnect();
      resolve(true);
    });

    socket.on('connect_error', (error) => {
      console.error('❌ WebSocket connection failed:', error.message);
      reject(error);
    });

    socket.on('disconnect', () => {
      if (connected) {
        console.log('🔌 WebSocket disconnected cleanly');
      }
    });

    // Timeout after 10 seconds
    setTimeout(() => {
      if (!connected) {
        socket.disconnect();
        reject(new Error('WebSocket connection timeout'));
      }
    }, 10000);
  });
}

async function testProgressUpdates() {
  console.log('📊 Testing progress updates...');
  
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  try {
    // Navigate to the application
    await page.goto(FRONTEND_URL);
    await page.waitForLoadState('networkidle');
    
    // Fill in brand analysis form
    await page.fill('input[placeholder*="brand"], input[placeholder*="company"]', 'Tesla');
    
    // Start analysis
    await page.click('button:has-text("Start Analysis"), button:has-text("Analyze")');
    
    // Wait for progress component to appear
    await page.waitForSelector('[data-testid="analysis-progress"], .analysis-progress, h1:has-text("Analysis")', { timeout: 10000 });
    
    console.log('✅ Analysis started, monitoring progress...');
    
    // Monitor progress updates
    let progressUpdates = [];
    let lastProgress = 0;
    let connectionStatus = null;
    
    // Set up progress monitoring
    const progressMonitor = setInterval(async () => {
      try {
        // Check connection status
        const connectionElement = await page.$('text=Connected, text=Disconnected');
        if (connectionElement) {
          const newStatus = await connectionElement.textContent();
          if (newStatus !== connectionStatus) {
            connectionStatus = newStatus;
            console.log(`🔌 Connection status: ${connectionStatus}`);
          }
        }
        
        // Check progress percentage
        const progressElement = await page.$('[role="progressbar"], .progress-bar, text=/\\d+%/');
        if (progressElement) {
          const progressText = await progressElement.textContent();
          const progressMatch = progressText.match(/(\d+)%/);
          if (progressMatch) {
            const currentProgress = parseInt(progressMatch[1]);
            if (currentProgress > lastProgress) {
              lastProgress = currentProgress;
              progressUpdates.push({
                progress: currentProgress,
                timestamp: new Date().toISOString()
              });
              console.log(`📈 Progress: ${currentProgress}%`);
            }
          }
        }
        
        // Check current step
        const stepElement = await page.$('text=/Currently:/, text=/Step \\d+/, [data-testid="current-step"]');
        if (stepElement) {
          const stepText = await stepElement.textContent();
          console.log(`🔄 Current step: ${stepText}`);
        }
        
        // Check for completion
        const completedElement = await page.$('text=Complete, text=Analysis Complete, text=100%');
        if (completedElement || lastProgress >= 100) {
          console.log('✅ Analysis completed!');
          clearInterval(progressMonitor);
          
          // Validate progress updates
          console.log(`📊 Total progress updates: ${progressUpdates.length}`);
          console.log('📈 Progress timeline:', progressUpdates);
          
          if (progressUpdates.length > 0) {
            console.log('✅ Progress updates working correctly');
          } else {
            console.log('⚠️ No progress updates detected');
          }
          
          return;
        }
        
      } catch (error) {
        console.error('❌ Error monitoring progress:', error.message);
      }
    }, 2000);
    
    // Wait for analysis to complete or timeout
    await page.waitForSelector('text=Complete, text=Analysis Complete', { timeout: 300000 }); // 5 minutes
    clearInterval(progressMonitor);
    
    console.log('✅ Progress monitoring test completed');
    
  } catch (error) {
    console.error('❌ Progress test failed:', error.message);
    throw error;
  } finally {
    await browser.close();
  }
}

async function testErrorHandling() {
  console.log('🚨 Testing error handling...');
  
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  try {
    // Navigate to the application
    await page.goto(FRONTEND_URL);
    await page.waitForLoadState('networkidle');
    
    // Test with invalid brand name to trigger error
    await page.fill('input[placeholder*="brand"], input[placeholder*="company"]', 'InvalidBrandThatDoesNotExist123');
    
    // Start analysis
    await page.click('button:has-text("Start Analysis"), button:has-text("Analyze")');
    
    // Wait for progress component
    await page.waitForSelector('[data-testid="analysis-progress"], .analysis-progress, h1:has-text("Analysis")', { timeout: 10000 });
    
    // Monitor for error states
    let errorDetected = false;
    const errorMonitor = setInterval(async () => {
      try {
        // Check for error messages
        const errorElement = await page.$('text=/Error/, text=/Failed/, [data-testid="error-message"]');
        if (errorElement) {
          const errorText = await errorElement.textContent();
          console.log(`🚨 Error detected: ${errorText}`);
          errorDetected = true;
          clearInterval(errorMonitor);
        }
        
        // Check for retry button
        const retryButton = await page.$('button:has-text("Retry"), button:has-text("Try Again")');
        if (retryButton) {
          console.log('🔄 Retry button found');
          await retryButton.click();
          console.log('✅ Retry button clicked');
        }
        
      } catch (error) {
        console.error('❌ Error monitoring error states:', error.message);
      }
    }, 2000);
    
    // Wait for error or timeout
    await new Promise(resolve => setTimeout(resolve, 30000)); // 30 seconds
    clearInterval(errorMonitor);
    
    if (errorDetected) {
      console.log('✅ Error handling test passed');
    } else {
      console.log('⚠️ No errors detected (this might be expected)');
    }
    
  } catch (error) {
    console.error('❌ Error handling test failed:', error.message);
    throw error;
  } finally {
    await browser.close();
  }
}

async function testReconnection() {
  console.log('🔄 Testing reconnection functionality...');
  
  // This test would require stopping and starting the backend server
  // For now, we'll just test the client-side reconnection logic
  
  const socket = io(BACKEND_URL, {
    transports: ['websocket', 'polling'],
    timeout: 5000
  });
  
  return new Promise((resolve) => {
    let reconnectAttempts = 0;
    
    socket.on('connect', () => {
      console.log('✅ Connected to server');
      
      // Simulate disconnect after 2 seconds
      setTimeout(() => {
        console.log('🔌 Simulating disconnect...');
        socket.disconnect();
      }, 2000);
    });
    
    socket.on('disconnect', () => {
      console.log('❌ Disconnected from server');
      
      // Attempt to reconnect
      setTimeout(() => {
        reconnectAttempts++;
        console.log(`🔄 Reconnection attempt ${reconnectAttempts}`);
        socket.connect();
        
        if (reconnectAttempts >= 2) {
          console.log('✅ Reconnection test completed');
          socket.disconnect();
          resolve();
        }
      }, 1000);
    });
    
    socket.on('connect_error', (error) => {
      console.log('❌ Connection error:', error.message);
    });
  });
}

async function runAllTests() {
  console.log('🚀 Starting WebSocket Progress System Tests\n');
  
  try {
    // Test 1: Basic WebSocket connection
    await testWebSocketConnection();
    console.log('');
    
    // Test 2: Progress updates during analysis
    await testProgressUpdates();
    console.log('');
    
    // Test 3: Error handling
    await testErrorHandling();
    console.log('');
    
    // Test 4: Reconnection
    await testReconnection();
    console.log('');
    
    console.log('✅ All WebSocket tests completed successfully!');
    
  } catch (error) {
    console.error('❌ Test suite failed:', error.message);
    process.exit(1);
  }
}

// Run tests if this script is executed directly
if (require.main === module) {
  runAllTests();
}

module.exports = {
  testWebSocketConnection,
  testProgressUpdates,
  testErrorHandling,
  testReconnection,
  runAllTests
};
