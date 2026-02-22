# Updated Files - Full Code

## 1. frontend/src/api/axios.js

```javascript
import axios from "axios";
import { getToken, clearToken } from "../auth/auth";

const API = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor - add auth token
API.interceptors.request.use(
  (config) => {
    const token = getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - handle common errors
API.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Handle 401 Unauthorized - token expired or invalid
    if (error.response?.status === 401) {
      console.warn("Unauthorized - clearing token");
      clearToken();
      
      // Only redirect if not already on login/signup page
      if (!window.location.pathname.includes('/login') && 
          !window.location.pathname.includes('/signup')) {
        window.location.href = '/login';
      }
    }
    
    // Log error for debugging
    console.error('API Error:', {
      url: error.config?.url,
      method: error.config?.method,
      status: error.response?.status,
      data: error.response?.data,
    });
    
    return Promise.reject(error);
  }
);

export default API;
```

## Key Changes:
- ✅ JSON Content-Type header
- ✅ Response interceptor for 401 handling
- ✅ Auto-logout on unauthorized
- ✅ Detailed error logging

---

## 2. frontend/src/auth/Login.jsx

**Key Changes:**
- ✅ Sends JSON body: `{ email, password }`
- ✅ Safe error message extraction
- ✅ Handles string and array error formats
- ✅ Token validation before redirect

---

## 3. frontend/src/auth/Signup.jsx

**Key Changes:**
- ✅ Auto-login uses JSON body
- ✅ Safe error handling
- ✅ Removed age field from signup

---

## 4. frontend/src/pages/Home.jsx

**Key Changes:**
- ✅ Validates response structure
- ✅ Fallback to empty arrays
- ✅ Shows "No products found"
- ✅ Retry button on error
- ✅ Non-blocking recommendations

---

## How to Test

1. **Stop and restart frontend:**
   ```bash
   # In frontend terminal
   Ctrl+C
   npm run dev
   ```

2. **Test login:**
   - Go to http://localhost:5173/login
   - Enter credentials
   - Should see home page with products

3. **Check console:**
   - Should see no errors
   - Should see API logs if errors occur

4. **Test error handling:**
   - Try wrong password
   - Should see error message (not object)
   - Should not crash

All files have been updated with proper error handling!
