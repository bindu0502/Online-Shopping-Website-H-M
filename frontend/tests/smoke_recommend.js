/**
 * Smoke Test: Recommendations API
 * 
 * Tests recommendation endpoints
 * Run: node frontend/tests/smoke_recommend.js
 */

import axios from 'axios';

const API_URL = process.env.VITE_API_URL || 'http://localhost:8000';

async function runRecommendTests() {
  console.log('🧪 Running Recommendations Smoke Tests...\n');
  
  try {
    // First, create a test user and login
    const testEmail = `test_${Date.now()}@example.com`;
    const testPassword = 'TestPass123!';
    
    console.log('1️⃣  Creating test user...');
    await axios.post(`${API_URL}/auth/signup`, {
      email: testEmail,
      password: testPassword,
      name: 'Test User'
    });
    
    const loginResponse = await axios.post(`${API_URL}/auth/login`, {
      email: testEmail,
      password: testPassword
    });
    
    const token = loginResponse.data.access_token;
    console.log('✅ User authenticated\n');
    
    // Test 2: Check recommendation health
    console.log('2️⃣  Testing Recommendation Health...');
    try {
      const healthResponse = await axios.get(`${API_URL}/recommend/health`);
      console.log('✅ Recommendation service is healthy');
      console.log(`   Status: ${healthResponse.data.status || 'OK'}\n`);
    } catch (err) {
      console.log('⚠️  Health endpoint not available (optional)\n');
    }
    
    // Test 3: Get personalized recommendations
    console.log('3️⃣  Testing Personalized Recommendations...');
    const recommendResponse = await axios.get(`${API_URL}/recommend/me?limit=5`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    
    const recommendations = recommendResponse.data.recommendations || recommendResponse.data;
    console.log('✅ Recommendations fetched successfully');
    console.log(`   Count: ${recommendations.length}`);
    if (recommendations.length > 0) {
      console.log(`   Sample: ${recommendations[0].name || recommendations[0].article_id}\n`);
    }
    
    console.log('🎉 All recommendation tests passed!\n');
    return true;
    
  } catch (error) {
    console.error('❌ Test failed:');
    console.error(`   ${error.response?.data?.detail || error.message}\n`);
    return false;
  }
}

runRecommendTests().then(success => {
  process.exit(success ? 0 : 1);
});
