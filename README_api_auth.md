# Authentication API

## Overview

The `src/api_auth.py` module provides a FastAPI router implementing JWT-based authentication. It includes user signup, login, and protected endpoint functionality.

## Features

- **User Registration** - Create new user accounts with email validation
- **JWT Authentication** - Secure token-based authentication
- **Password Security** - Bcrypt password hashing
- **Protected Endpoints** - Bearer token authentication for protected routes
- **User Profile** - Retrieve current user information

## Configuration

### Environment Variables

- `API_SECRET` - Secret key for JWT signing (default: "project149_secret_key")

**Important:** Change the default secret in production!

```bash
export API_SECRET="your-super-secret-key-here"
```

### JWT Settings

- **Algorithm:** HS256
- **Token Expiry:** 24 hours
- **Token Type:** Bearer

## API Endpoints

### POST /auth/signup

Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "secure_password",
  "name": "John Doe"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "John Doe"
}
```

**Errors:**
- `400 Bad Request` - Email already registered
- `422 Unprocessable Entity` - Invalid email format

### POST /auth/login

Authenticate user and receive JWT token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "secure_password"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Errors:**
- `401 Unauthorized` - Invalid email or password

### GET /auth/me

Get current authenticated user's information (protected endpoint).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "John Doe"
}
```

**Errors:**
- `401 Unauthorized` - Missing, invalid, or expired token

## Usage

### Integration with FastAPI

```python
from fastapi import FastAPI
from src.api_auth import router as auth_router

app = FastAPI()
app.include_router(auth_router)
```

### Client Examples

#### Signup

```python
import requests

response = requests.post(
    "http://localhost:8000/auth/signup",
    json={
        "email": "user@example.com",
        "password": "secure_password",
        "name": "John Doe"
    }
)

user = response.json()
print(f"User created: {user['id']}")
```

#### Login

```python
import requests

response = requests.post(
    "http://localhost:8000/auth/login",
    json={
        "email": "user@example.com",
        "password": "secure_password"
    }
)

token_data = response.json()
access_token = token_data["access_token"]
print(f"Token: {access_token}")
```

#### Access Protected Endpoint

```python
import requests

headers = {
    "Authorization": f"Bearer {access_token}"
}

response = requests.get(
    "http://localhost:8000/auth/me",
    headers=headers
)

user_info = response.json()
print(f"User: {user_info['name']}")
```

### JavaScript/Fetch Example

```javascript
// Signup
const signupResponse = await fetch('http://localhost:8000/auth/signup', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'secure_password',
    name: 'John Doe'
  })
});
const user = await signupResponse.json();

// Login
const loginResponse = await fetch('http://localhost:8000/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'secure_password'
  })
});
const { access_token } = await loginResponse.json();

// Access protected endpoint
const meResponse = await fetch('http://localhost:8000/auth/me', {
  headers: { 'Authorization': `Bearer ${access_token}` }
});
const userInfo = await meResponse.json();
```

## Security

### Password Hashing

Passwords are hashed using bcrypt with automatic salt generation:
- **Algorithm:** bcrypt
- **Salt rounds:** 12
- **Never stored in plain text**

### JWT Tokens

JWT tokens contain:
- **Subject (sub):** User ID
- **Expiry (exp):** 24 hours from creation
- **Signed with:** HS256 algorithm

Token payload example:
```json
{
  "sub": "123",
  "exp": 1701532800
}
```

### Best Practices

1. **Use HTTPS in production** - Never send tokens over HTTP
2. **Change default secret** - Set `API_SECRET` environment variable
3. **Store tokens securely** - Use httpOnly cookies or secure storage
4. **Implement token refresh** - Add refresh token mechanism for production
5. **Rate limiting** - Add rate limiting to prevent brute force attacks
6. **CORS configuration** - Configure CORS properly for your frontend

## Testing

Run the test script to verify all functionality:

```bash
python test_api_auth.py
```

Expected output:
```
============================================================
AUTHENTICATION API TEST
============================================================

1. Testing signup...
   ✓ User created: {'id': 2, 'email': 'test_auth@example.com', ...}

2. Testing duplicate signup...
   ✓ Duplicate signup rejected: Email already registered

3. Testing login with correct credentials...
   ✓ Login successful
   Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

...

============================================================
✓ ALL AUTHENTICATION TESTS PASSED
============================================================
```

## Error Handling

All endpoints return appropriate HTTP status codes and error messages:

### 400 Bad Request
```json
{
  "detail": "Email already registered"
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid email or password"
}
```

```json
{
  "detail": "Invalid or expired token"
}
```

### 422 Unprocessable Entity
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

## Dependencies

```bash
pip install fastapi pyjwt pydantic[email] sqlalchemy bcrypt
```

## Extending the API

### Add Protected Endpoints

Use the `get_current_user` dependency to protect any endpoint:

```python
from fastapi import Depends
from src.api_auth import get_current_user
from src.db import User

@router.get("/protected-resource")
def get_protected_resource(current_user: User = Depends(get_current_user)):
    return {"message": f"Hello {current_user.name}!"}
```

### Add Refresh Tokens

For production, implement refresh tokens:

```python
@router.post("/refresh")
def refresh_token(refresh_token: str):
    # Validate refresh token
    # Generate new access token
    # Return new token
    pass
```

### Add Password Reset

Implement password reset functionality:

```python
@router.post("/forgot-password")
def forgot_password(email: EmailStr):
    # Generate reset token
    # Send email with reset link
    pass

@router.post("/reset-password")
def reset_password(token: str, new_password: str):
    # Validate reset token
    # Update password
    pass
```

## Logging

The module logs important authentication events:

- User registration
- Login attempts (successful and failed)
- Profile access
- Token validation errors

Example log output:
```
INFO:src.api_auth:New user registered: user@example.com (ID: 1)
INFO:src.api_auth:User logged in: user@example.com (ID: 1)
WARNING:src.api_auth:Failed login attempt for user: user@example.com
WARNING:src.api_auth:Invalid token
```

## Production Checklist

- [ ] Change `API_SECRET` to a strong random value
- [ ] Enable HTTPS
- [ ] Configure CORS properly
- [ ] Add rate limiting
- [ ] Implement refresh tokens
- [ ] Add password reset functionality
- [ ] Set up monitoring and alerting
- [ ] Add email verification
- [ ] Implement account lockout after failed attempts
- [ ] Add audit logging
