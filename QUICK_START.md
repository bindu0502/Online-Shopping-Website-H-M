# Quick Start Guide - Project149 API

## 🚀 Start the API Server

```bash
python main.py
```

The server will start on `http://localhost:8000`

## 📚 View API Documentation

Once the server is running, open your browser:

- **Swagger UI (Interactive):** http://localhost:8000/docs
- **ReDoc (Alternative):** http://localhost:8000/redoc
- **Root Endpoint:** http://localhost:8000/

## ✅ Test the API

### Option 1: Automated Test (Recommended)

```bash
python test_live_api.py
```

This will test all endpoints automatically.

### Option 2: Interactive Testing (Swagger UI)

1. Open http://localhost:8000/docs
2. Click on any endpoint (e.g., `POST /auth/signup`)
3. Click "Try it out"
4. Enter test data
5. Click "Execute"

### Option 3: Manual Testing with cURL

```bash
# Signup
curl -X POST "http://localhost:8000/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"pass123","name":"Test User"}'

# Login
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"pass123"}'

# Get Profile (replace TOKEN with your actual token)
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer TOKEN"
```

## 📋 Available Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/` | API health check | No |
| POST | `/auth/signup` | Register new user | No |
| POST | `/auth/login` | Login and get token | No |
| GET | `/auth/me` | Get user profile | Yes (Bearer token) |

## 🔑 Authentication Flow

1. **Signup:** Create a new account
   ```json
   POST /auth/signup
   {
     "email": "user@example.com",
     "password": "secure_password",
     "name": "John Doe"
   }
   ```

2. **Login:** Get your access token
   ```json
   POST /auth/login
   {
     "email": "user@example.com",
     "password": "secure_password"
   }
   ```
   Response:
   ```json
   {
     "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
     "token_type": "bearer"
   }
   ```

3. **Use Token:** Include in Authorization header
   ```
   Authorization: Bearer <your_access_token>
   ```

## 🛠️ Project Structure

```
Project149_Main/
├── main.py                    # FastAPI application entry point
├── src/
│   ├── db.py                  # Database models (SQLAlchemy)
│   ├── api_auth.py            # Authentication endpoints
│   ├── data_loader.py         # Data loading utilities
│   ├── preprocess_short.py    # Data preprocessing
│   ├── retrieval.py           # Candidate generation
│   ├── features.py            # Feature engineering
│   ├── create_training_data.py # Training data creation
│   └── model_train.py         # LightGBM model training
├── datasets/                  # Data files
├── models/                    # Trained models
├── outputs/                   # Model outputs
└── project149.db             # SQLite database
```

## 📖 Documentation Files

- `README_database.md` - Database schema and usage
- `README_api_auth.md` - Authentication API documentation
- `TEST_API_GUIDE.md` - Comprehensive testing guide
- `README_retrieval.md` - Candidate generation
- `README_features.md` - Feature engineering
- `README_training_data.md` - Training data creation
- `README_model_training.md` - Model training

## 🧪 Run All Tests

```bash
# Database tests
python test_db.py

# Authentication API tests (no server needed)
python test_api_auth.py

# Live API tests (server must be running)
python test_live_api.py
```

## 🔧 Configuration

### Environment Variables

```bash
# Database connection (optional, defaults to SQLite)
export DATABASE_URL="sqlite:///project149.db"

# JWT secret key (change in production!)
export API_SECRET="your-super-secret-key-here"
```

### Default Settings

- **Database:** SQLite (`project149.db`)
- **JWT Secret:** `project149_secret_key` (⚠️ Change in production!)
- **Token Expiry:** 24 hours
- **Server Port:** 8000

## 🎯 Next Steps

1. **Explore the API:**
   - Open http://localhost:8000/docs
   - Try the endpoints interactively

2. **Build a Frontend:**
   - Use the authentication endpoints
   - Store JWT token in localStorage
   - Include token in API requests

3. **Add More Endpoints:**
   - Product catalog endpoints
   - Recommendation endpoints
   - User interaction tracking

4. **Deploy to Production:**
   - Change `API_SECRET` environment variable
   - Use PostgreSQL instead of SQLite
   - Enable HTTPS
   - Add rate limiting

## 💡 Tips

- **Reset Database:** Delete `project149.db` and restart server
- **View Logs:** Check terminal output for request logs
- **Debug:** Set `echo=True` in `src/db.py` to see SQL queries
- **CORS:** Add CORS middleware if testing from frontend

## 🆘 Troubleshooting

**Server won't start:**
```bash
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Use different port
uvicorn main:app --port 8001
```

**Database errors:**
```bash
# Delete and recreate database
rm project149.db
python main.py
```

**Import errors:**
```bash
# Install dependencies
pip install fastapi uvicorn sqlalchemy bcrypt pyjwt pydantic[email]
```

## 📞 Support

For more detailed information, see:
- `TEST_API_GUIDE.md` - Complete testing guide
- `README_api_auth.md` - Authentication documentation
- Swagger UI: http://localhost:8000/docs (when server is running)
