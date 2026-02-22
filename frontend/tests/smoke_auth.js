/**
 * Smoke Test: Authentication Flow
 * 
 * Tests signup and login endpoints
 * Run: node frontend/tests/smoke_auth.js
 */

import axios from 'axios';

const API_URL = process.env.VITE_API_URL || 'http://localhost:8000';
const testEmail = `test_${Date.now()}@example.com`;
const testPassword = 'TestPass123!';

async function runAuthTests() {
  console.log('🧪 Running Authentication Smoke Tests...\n');
  
  try {
    // Test 1: Signup
    console.log('1️⃣  Testing Signup...');
    const signupResponse = await axios.post(`${API_URL}/auth/signup`, {
      email: testEmail,
      password: testPassword,
      name: 'Test User'
    });
    
    console.log('✅ Signup successful');
    console.log(`   User ID: ${signupResponse.data.id}`);
    console.log(`   Email: ${signupResponse.data.email}\n`);
    
    // Test 2: Login
    console.log('2️⃣  Testing Login...');
    const loginResponse = await axios.post(`${API_URL}/auth/login`, {
      email: testEmail,
      password: testPassword
    });
    
    const token = loginResponse.data.access_token;
    console.log('✅ Login successful');
    console.log(`   Token: ${token.substring(0, 20)}...\n`);
    
    // Test 3: Get Profile
    console.log('3️⃣  Testing Profile Fetch...');
    const profileResponse = await axios.get(`${API_URL}/auth/me`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    
    console.log('✅ Profile fetch successful');
    console.log(`   Name: ${profileResponse.data.name}`);
    console.log(`   Email: ${profileResponse.data.email}\n`);
    
    console.log('🎉 All authentication tests passed!\n');
    return true;
    
  } catch (error) {
    console.error('❌ Test failed:');
    console.error(`   ${error.response?.data?.detail || error.message}\n`);
    return false;
  }
}

runAuthTests().then(success => {
  process.exit(success ? 0 : 1);
});
