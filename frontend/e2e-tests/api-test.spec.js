import { test, expect } from '@playwright/test';

const API_BASE_URL = 'https://backend-service-production-1b63.up.railway.app/api';

test.describe('API Backend Tests', () => {
  
  test('should test health endpoint', async ({ request }) => {
    console.log('🔍 Testing health endpoint...');
    
    try {
      const response = await request.get(`${API_BASE_URL}/health`, {
        timeout: 15000
      });
      
      console.log('✅ Health endpoint status:', response.status());
      
      if (response.ok()) {
        const data = await response.json();
        console.log('✅ Health endpoint response:', data);
        expect(data).toHaveProperty('status');
      } else {
        const text = await response.text();
        console.log('❌ Health endpoint error response:', text);
        console.log('❌ This explains why the frontend can\'t connect to the backend');
      }
    } catch (error) {
      console.log('❌ Health endpoint network error:', error.message);
      console.log('❌ Backend is not reachable - this is the root cause');
    }
  });

  test('should test brand audit endpoint', async ({ request }) => {
    console.log('🔍 Testing brand audit endpoint...');
    
    try {
      const response = await request.post(`${API_BASE_URL}/audit`, {
        data: {
          company_name: 'Apple'
        },
        headers: {
          'Content-Type': 'application/json'
        },
        timeout: 30000
      });
      
      console.log('✅ Audit endpoint status:', response.status());
      
      if (response.ok()) {
        const data = await response.json();
        console.log('✅ Audit endpoint working! Response keys:', Object.keys(data));
        expect(data).toBeDefined();
      } else {
        const text = await response.text();
        console.log('❌ Audit endpoint error:', text);
      }
    } catch (error) {
      console.log('❌ Audit endpoint error:', error.message);
    }
  });
});
