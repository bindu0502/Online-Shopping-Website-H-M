# Frontend Quick Start Guide

## Prerequisites
- Node.js 16+ installed
- Backend API running on http://localhost:8000

## Environment Setup

1. **Configure API URL** (optional):
   ```bash
   cd frontend
   cp .env.example .env
   # Edit .env if backend runs on different port
   ```

   The `.env` file should contain:
   ```
   VITE_API_URL=http://localhost:8000
   ```

2. **Install Dependencies** (first time only):
   ```bash
   cd frontend
   npm install
   ```

## Start the Frontend

**Windows PowerShell:**
```powershell
cd frontend
npm run dev
```

**Command Prompt:**
```cmd
cd frontend && npm run dev
```

**Mac/Linux:**
```bash
cd frontend && npm run dev
```

The frontend will be available at: **http://localhost:5173**

## Running Full Stack

You need **two terminals** running simultaneously:

### Terminal 1 - Backend:
```bash
python main.py
```
Backend runs on: http://localhost:8000

### Terminal 2 - Frontend:
```bash
cd frontend
npm run dev
```
Frontend runs on: http://localhost:5173

## Running Smoke Tests

After starting both backend and frontend, run integration tests:

```bash
# Test authentication flow
node frontend/tests/smoke_auth.js

# Test recommendations API
node frontend/tests/smoke_recommend.js
```

These tests verify:
- ✅ User signup and login
- ✅ JWT token generation
- ✅ Protected routes
- ✅ Recommendations API

## First Time Setup

1. Open http://localhost:5173
2. Click "Sign Up" to create an account
3. Fill in your details (email, password, name, age)
4. You'll be automatically logged in
5. Browse products, add to cart, and checkout!

## Features Available

✅ User signup and login
✅ Browse products with recommendations
✅ View product details
✅ Add products to cart
✅ Checkout and place orders
✅ View order history
✅ Personalized recommendations

## API Configuration

The frontend connects to the backend via the `.env` file:

```
VITE_API_URL=http://localhost:8000
```

If your backend runs on a different port, update this file.

## Development Tools

### Recommended Browser Settings
- **Chrome/Edge**: Install React Developer Tools extension
- **Firefox**: Install React DevTools add-on
- Open DevTools (F12) to see:
  - Network requests (verify API calls)
  - Console logs (debug mode shows API requests)
  - React component tree

### Hot Reload
- Frontend: Changes auto-refresh (Vite HMR)
- Backend: Restart required after code changes

### Debug Mode
In development, axios logs all API requests to console:
```
[API] GET /products/ { hasAuth: true, data: undefined }
[API] POST /cart/add { hasAuth: true, data: {...} }
```

## Troubleshooting

**Frontend won't start:**
- Check Node.js version: `node --version` (need 16+)
- Delete `node_modules` and run `npm install` again
- Clear npm cache: `npm cache clean --force`

**Can't connect to API:**
- Ensure backend is running on port 8000
- Check `.env` file has correct `VITE_API_URL`
- Check browser console for CORS errors
- Verify backend shows: `INFO: Uvicorn running on http://0.0.0.0:8000`

**Login not working:**
- Create an account first (signup)
- Check browser console for 422 errors
- Verify token is saved: `localStorage.getItem('auth_token')`
- Check backend logs for authentication errors

**Images not loading:**
- Verify backend serves images at `/images/` endpoint
- Check image paths in database: `python -c "from src.db import *; ..."`
- Ensure `update_image_paths.py` was run

**Cart is empty after adding items:**
- Check browser console for API errors
- Verify token is attached to requests (see Network tab)
- Check backend logs for cart operations
- Run smoke tests to verify API connectivity

## Build for Production

```bash
cd frontend
npm run build
```

Output will be in `frontend/dist/` directory.

Preview production build:
```bash
npm run preview
```
