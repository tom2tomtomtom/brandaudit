#!/usr/bin/env node

const { spawn } = require('child_process');
const http = require('http');

// Test minimal backend locally
console.log('🧪 Testing minimal backend locally...');

// Start the minimal backend
const backendProcess = spawn('python', ['backend/app.py'], {
  stdio: 'inherit',
  env: { ...process.env, PORT: '8000' }
});

// Wait a moment for startup
setTimeout(() => {
  // Test health endpoint
  const options = {
    hostname: 'localhost',
    port: 8000,
    path: '/api/health',
    method: 'GET'
  };

  const req = http.request(options, (res) => {
    console.log(`\n✅ Status: ${res.statusCode}`);
    
    let data = '';
    res.on('data', (chunk) => {
      data += chunk;
    });
    
    res.on('end', () => {
      console.log('📊 Response:', JSON.parse(data));
      console.log('\n🎉 Minimal backend works locally!');
      
      // Kill the process
      backendProcess.kill();
      process.exit(0);
    });
  });

  req.on('error', (err) => {
    console.log('❌ Error:', err.message);
    backendProcess.kill();
    process.exit(1);
  });

  req.end();
}, 2000);

// Handle process exit
backendProcess.on('exit', (code) => {
  if (code !== 0) {
    console.log(`❌ Backend exited with code ${code}`);
  }
});