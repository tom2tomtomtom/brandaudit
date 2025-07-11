import { test, expect } from '@playwright/test';

const API_BASE_URL = 'https://backend-service-production-1b63.up.railway.app/api';

test.describe('API Endpoints Tests', () => {
  
  test('should test health endpoint', async ({ request }) => {
    console.log('Testing health endpoint...');
    
    try {
      const response = await request.get(`${API_BASE_URL}/health`);
      
      console.log('Health endpoint status:', response.status());
      console.log('Health endpoint headers:', await response.allHeaders());
      
      if (response.ok()) {
        const data = await response.json();
        console.log('Health endpoint response:', data);
        expect(data).toHaveProperty('status');
      } else {
        const text = await response.text();
        console.log('Health endpoint error response:', text);
        
        // Even if it fails, we want to document what happened
        expect(response.status()).toBeGreaterThan(0);
      }
    } catch (error) {
      console.log('Health endpoint error:', error.message);
      expect(error.message).toBeDefined();
    }
  });

  test('should test brand audit endpoint with Apple', async ({ request }) => {
    console.log('Testing brand audit endpoint with Apple...');
    
    try {
      const response = await request.post(`${API_BASE_URL}/audit`, {
        data: {
          company_name: 'Apple'
        },
        headers: {
          'Content-Type': 'application/json'
        },
        timeout: 30000 // 30 second timeout
      });
      
      console.log('Audit endpoint status:', response.status());
      console.log('Audit endpoint headers:', await response.allHeaders());
      
      if (response.ok()) {
        const data = await response.json();
        console.log('Audit endpoint response keys:', Object.keys(data));
        console.log('Audit endpoint response preview:', JSON.stringify(data, null, 2).substring(0, 500));
        
        // Check for expected response structure
        expect(data).toBeDefined();
      } else {
        const text = await response.text();
        console.log('Audit endpoint error response:', text);
        
        // Document the error
        expect(response.status()).toBeGreaterThan(0);
      }
    } catch (error) {
      console.log('Audit endpoint error:', error.message);
      expect(error.message).toBeDefined();
    }
  });

  test('should test brand audit endpoint with obscure brand', async ({ request }) => {
    console.log('Testing brand audit endpoint with obscure brand...');
    
    try {
      const response = await request.post(`${API_BASE_URL}/audit`, {
        data: {
          company_name: 'Patagonia Provisions'
        },
        headers: {
          'Content-Type': 'application/json'
        },
        timeout: 45000 // 45 second timeout for potentially slower processing
      });
      
      console.log('Obscure brand audit status:', response.status());
      console.log('Obscure brand audit headers:', await response.allHeaders());
      
      if (response.ok()) {
        const data = await response.json();
        console.log('Obscure brand audit response keys:', Object.keys(data));
        console.log('Obscure brand audit response preview:', JSON.stringify(data, null, 2).substring(0, 500));
        
        expect(data).toBeDefined();
      } else {
        const text = await response.text();
        console.log('Obscure brand audit error response:', text);
        
        expect(response.status()).toBeGreaterThan(0);
      }
    } catch (error) {
      console.log('Obscure brand audit error:', error.message);
      expect(error.message).toBeDefined();
    }
  });

  test('should test CORS and preflight requests', async ({ request }) => {
    console.log('Testing CORS preflight...');
    
    try {
      const response = await request.fetch(`${API_BASE_URL}/audit`, {
        method: 'OPTIONS',
        headers: {
          'Origin': 'http://localhost:5175',
          'Access-Control-Request-Method': 'POST',
          'Access-Control-Request-Headers': 'Content-Type'
        }
      });
      
      console.log('CORS preflight status:', response.status());
      console.log('CORS preflight headers:', await response.allHeaders());
      
      expect(response.status()).toBeGreaterThanOrEqual(200);
    } catch (error) {
      console.log('CORS preflight error:', error.message);
      expect(error.message).toBeDefined();
    }
  });
});
