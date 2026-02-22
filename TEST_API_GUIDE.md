# API Testing Guide

## Quick Start

### Method 1: Run the Server

1. **Start the server:**
```bash
python main.py
```

Or with uvicorn directly:
```bash
uvicorn main:app --reload
```

2. **Open your browser:**
- API Docs (Swagger UI): http://localhost:8000/docs
- Alternative Docs (ReDoc): http://localhost:8000/redoc
- Root endpoint: http://localhost:8000/

The server will be running on `http://localhost:8000`

### Method 2: Automated Tests

Run the test script (no server needed):
```bash
python test_api_auth.py
```

## Testing with Swagger UI (Interactive)

1. **Start the server:**
```bash
python main.py
```

2. **Open Swagger UI:**
```
http://localhost:8000/docs
```

3. **Test Signup:**
   - Click on `POST /auth/signup`
   - Click "Try it out"
   - Enter test data:
   ```json
   {
     "email": "test@example.com",
     "password": "mypassword123",
     "name": "Test User"
   }
   ```
   - Click "Execute"
   - You should see a 201 response with user data

4. **Test Login:**
   - Click on `POST /auth/login`
   - Click "Try it out"
   - Enter credentials:
   ```json
   {
     "email": "test@example.com",
     "password": "mypassword123"
   }
   ```
   - Click "Execute"
   - Copy the `access_token` from the response

5. **Test Protected Endpoint:**
   - Click on `GET /auth/me`
   - Click "Try it out"
   - Click the "Authorize" button (🔒) at the top
   - Enter: `Bearer <your_access_token>`
   - Click "Authorize"
   - Click "Execute" on `/auth/me`
   - You should see your user profile

## Testing with cURL

### 1. Signup
```bash
curl -X POST "http://localhost:8000/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "mypassword123",
    "name": "Test User"
  }'
```

Expected response:
```json
{
  "id": 1,
  "email": "test@example.com",
  "name": "Test User"
}
```

### 2. Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "mypassword123"
  }'
```

Expected response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 3. Get Profile (Protected)
```bash
# Replace <TOKEN> with your actual token
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer <TOKEN>"
```

Expected response:
```json
{
  "id": 1,
  "email": "test@example.com",
  "name": "Test User"
}
```

## Testing with Python Requests

Create a test file `test_manual.py`:

```python
import requests

BASE_URL = "http://localhost:8000"

# 1. Signup
print("1. Testing signup...")
signup_response = requests.post(
    f"{BASE_URL}/auth/signup",
    json={
        "email": "test@example.com",
        "password": "mypassword123",
        "name": "Test User"
    }
)
print(f"Status: {signup_response.status_code}")
print(f"Response: {signup_response.json()}\n")

# 2. Login
print("2. Testing login...")
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "email": "test@example.com",
        "password": "mypassword123"
    }
)
print(f"Status: {login_response.status_code}")
token_data = login_response.json()
print(f"Response: {token_data}\n")

# 3. Get profile
print("3. Testing protected endpoint...")
access_token = token_data["access_token"]
me_response = requests.get(
    f"{BASE_URL}/auth/me",
    headers={"Authorization": f"Bearer {access_token}"}
)
print(f"Status: {me_response.status_code}")
print(f"Response: {me_response.json()}")
```

Run it:
```bash
# Make sure server is running first!
python test_manual.py
```

## Testing with Postman

### 1. Setup

1. Open Postman
2. Create a new collection called "Project149 API"

### 2. Signup Request

- **Method:** POST
- **URL:** `http://localhost:8000/auth/signup`
- **Headers:**
  - `Content-Type: application/json`
- **Body (raw JSON):**
```json
{
  "email": "test@example.com",
  "password": "mypassword123",
  "name": "Test User"
}
```
- Click "Send"

### 3. Login Request

- **Method:** POST
- **URL:** `http://localhost:8000/auth/login`
- **Headers:**
  - `Content-Type: application/json`
- **Body (raw JSON):**
```json
{
  "email": "test@example.com",
  "password": "mypassword123"
}
```
- Click "Send"
- Copy the `access_token` from response

### 4. Get Profile Request

- **Method:** GET
- **URL:** `http://localhost:8000/auth/me`
- **Headers:**
  - `Authorization: Bearer <paste_your_token_here>`
- Click "Send"

## Testing with HTTPie

If you have HTTPie installed:

```bash
# Signup
http POST localhost:8000/auth/signup \
  email=test@example.com \
  password=mypassword123 \
  name="Test User"

# Login
http POST localhost:8000/auth/login \
  email=test@example.com \
  password=mypassword123

# Get profile (replace TOKEN)
http GET localhost:8000/auth/me \
  Authorization:"Bearer TOKEN"
```

## Common Issues

### Issue: "Connection refused"
**Solution:** Make sure the server is running:
```bash
python main.py
```

### Issue: "401 Unauthorized" on /auth/me
**Solution:** Check that you're including the Bearer token:
```bash
Authorization: Bearer <your_token>
```

### Issue: "Email already registered"
**Solution:** Either:
1. Use a different email
2. Delete the database file and restart:
```bash
rm project149.db
python main.py
```

### Issue: "Invalid token"
**Solution:** 
1. Make sure you copied the full token
2. Check if token expired (24 hours)
3. Login again to get a new token

## Automated Testing

Run the full test suite:
```bash
python test_api_auth.py
```

This will test:
- ✓ User signup
- ✓ Duplicate signup rejection
- ✓ Login with correct credentials
- ✓ Login with wrong password
- ✓ Login with non-existent email
- ✓ Protected endpoint with valid token
- ✓ Protected endpoint without token
- ✓ Protected endpoint with invalid token

## Next Steps

After testing the authentication API:

1. **Add more endpoints** - Create product endpoints, recommendation endpoints, etc.
2. **Add CORS** - If testing from a frontend:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

3. **Add rate limiting** - Prevent abuse
4. **Add logging** - Track API usage
5. **Deploy** - Deploy to production server

## Example Frontend Integration

### JavaScript/Fetch

```javascript
// Signup
const signup = async () => {
  const response = await fetch('http://localhost:8000/auth/signup', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      email: 'test@example.com',
      password: 'mypassword123',
      name: 'Test User'
    })
  });
  const user = await response.json();
  console.log('User created:', user);
};

// Login
const login = async () => {
  const response = await fetch('http://localhost:8000/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      email: 'test@example.com',
      password: 'mypassword123'
    })
  });
  const { access_token } = await response.json();
  localStorage.setItem('token', access_token);
  console.log('Logged in, token saved');
};

// Get profile
const getProfile = async () => {
  const token = localStorage.getItem('token');
  const response = await fetch('http://localhost:8000/auth/me', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  const user = await response.json();
  console.log('User profile:', user);
};
```

### React Example

```jsx
import { useState } from 'react';

function Auth() {
  const [token, setToken] = useState(null);

  const handleLogin = async (email, password) => {
    const response = await fetch('http://localhost:8000/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    const data = await response.json();
    setToken(data.access_token);
    localStorage.setItem('token', data.access_token);
  };

  const getProfile = async () => {
    const response = await fetch('http://localhost:8000/auth/me', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    const user = await response.json();
    console.log(user);
  };

  return (
    <div>
      <button onClick={() => handleLogin('test@example.com', 'password')}>
        Login
      </button>
      <button onClick={getProfile}>Get Profile</button>
    </div>
  );
}
```
