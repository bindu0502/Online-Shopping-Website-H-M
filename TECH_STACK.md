# 🛠️ Tech Stack - Project149

Complete technology stack for the E-Commerce Recommendation System.

---

## 🎯 Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                              │
│  React 19 + Vite + TailwindCSS + React Router               │
└─────────────────────────────────────────────────────────────┘
                            ↓ HTTP/REST
┌─────────────────────────────────────────────────────────────┐
│                        BACKEND API                           │
│  FastAPI + Uvicorn + SQLAlchemy + JWT Auth                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                        DATABASE                              │
│  SQLite (Development) / PostgreSQL (Production)              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    ML/AI SERVICES                            │
│  LightGBM + scikit-learn + Google Gemini AI                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎨 Frontend Stack

### Core Framework
- **React 19.2.0** - UI library
- **React Router DOM 7.9.6** - Client-side routing
- **Vite 7.2.4** - Build tool and dev server

### Styling
- **TailwindCSS 4.1.17** - Utility-first CSS framework
- **PostCSS 8.5.6** - CSS processing
- **Autoprefixer 10.4.22** - CSS vendor prefixing

### HTTP Client
- **Axios 1.13.2** - HTTP requests to backend API

### Utilities
- **Day.js 1.11.19** - Date/time manipulation

### Development Tools
- **ESLint 9.39.1** - Code linting
- **Vite Plugin React SWC 4.2.2** - Fast React refresh

---

## 🔧 Backend Stack

### Web Framework
- **FastAPI 0.104.1** - Modern Python web framework
- **Uvicorn 0.24.0** - ASGI server
- **Python Multipart 0.0.6** - File upload support

### Database & ORM
- **SQLAlchemy 2.0.23** - SQL toolkit and ORM
- **SQLite** - Development database
- **PostgreSQL** - Production database (optional)

### Authentication & Security
- **Python-JOSE 3.3.0** - JWT token handling
- **PyJWT 2.8.0** - JSON Web Tokens
- **Bcrypt 4.1.1** - Password hashing

### Data Processing
- **Pandas 2.1.3** - Data manipulation and analysis
- **NumPy 1.26.2** - Numerical computing

### Machine Learning
- **LightGBM** - Gradient boosting framework (for ranking model)
- **scikit-learn 1.3.2** - ML utilities and preprocessing
- **Joblib** - Model serialization

### AI/Search
- **Google Generative AI 0.3.2** - Gemini AI for semantic search

### Caching (Optional)
- **Redis 5.0.1** - In-memory data store for caching

### Utilities
- **Python-dotenv 1.0.0** - Environment variable management
- **Requests 2.31.0** - HTTP library

---

## 🗄️ Database Schema

### Tables
1. **users** - User accounts and authentication
2. **products** - Product catalog (105k+ items)
3. **cart_items** - Shopping cart
4. **wishlist_items** - User wishlists
5. **orders** - Order history
6. **order_items** - Order line items
7. **user_interactions** - Behavioral tracking

### Database Features
- SQLAlchemy ORM models
- Relationship mapping
- Migration support
- Bcrypt password hashing

---

## 🤖 Machine Learning Stack

### Recommendation System

**1. LightGBM Ranking Model**
- **Purpose**: Score candidate products for personalized recommendations
- **Algorithm**: Gradient Boosting Decision Trees (GBDT)
- **Objective**: Binary classification (purchase probability)
- **Features**: 50+ behavioral and product features
- **Training**: Offline training with temporal validation
- **Serving**: Real-time prediction via FastAPI

**2. Retrieval System**
- **Candidate Generation**: Rule-based retrieval
  - Recent purchases (time decay)
  - Popular by age group
  - Co-purchased items (market basket)
- **Feature Engineering**: User-item interaction features
- **Ranking**: LightGBM model scoring

**3. Personalized "For You" System**
- **Cold-Start**: Category-based recommendations
- **Warm-Start**: Similarity-based recommendations
  - Name similarity (Jaccard)
  - Color matching
  - Category matching
  - Price similarity

### AI-Powered Search
- **Google Gemini AI** - Semantic search and query understanding
- **Fallback**: Traditional text search

### ML Libraries
- **LightGBM** - Gradient boosting
- **scikit-learn** - Preprocessing, metrics, transformers
- **Pandas/NumPy** - Data manipulation
- **Matplotlib** - Visualization (training)

---

## 🐳 DevOps & Deployment

### Containerization
- **Docker** - Container platform
- **Docker Compose** - Multi-container orchestration

### Services
```yaml
services:
  - backend (FastAPI + Uvicorn)
  - frontend (Nginx + React)
  - redis (Optional caching)
```

### CI/CD
- **GitHub Actions** - Automated workflows
- **Health Checks** - Service monitoring
- **Auto-restart** - Service recovery

### Environment Management
- **.env files** - Configuration
- **Environment variables** - Secrets management

---

## 📦 Project Structure

```
Project149/
├── frontend/                 # React frontend
│   ├── src/
│   │   ├── pages/           # Page components
│   │   ├── components/      # Reusable components
│   │   ├── auth/            # Auth components
│   │   └── api/             # API client (Axios)
│   ├── package.json
│   └── vite.config.js
│
├── src/                      # Backend source
│   ├── api_*.py             # API routers
│   ├── db.py                # Database models
│   ├── model_train.py       # ML training
│   ├── retrieval.py         # Candidate generation
│   ├── features.py          # Feature engineering
│   └── personalized_recommend.py  # For You system
│
├── datasets/                 # Data files
│   ├── processed/           # Processed data
│   └── images_128_128/      # Product images
│
├── models/                   # Trained ML models
│   └── lgbm_v1.pkl          # LightGBM model
│
├── main.py                   # FastAPI app
├── requirements.txt          # Python dependencies
├── docker-compose.yml        # Docker orchestration
└── project149.db            # SQLite database
```

---

## 🔌 API Architecture

### REST API Endpoints

**Authentication**
- `POST /auth/signup` - User registration
- `POST /auth/login` - User login (JWT)
- `GET /auth/me` - Get current user

**Products**
- `GET /products` - List products (with filters)
- `GET /products/{id}` - Product details
- `GET /products/{id}/similar` - Similar products

**Shopping**
- `GET /cart` - View cart
- `POST /cart/add` - Add to cart
- `POST /cart/remove/{id}` - Remove from cart
- `GET /wishlist` - View wishlist
- `POST /wishlist/add` - Add to wishlist

**Orders**
- `POST /orders/checkout` - Create order
- `GET /orders` - Order history
- `GET /orders/{id}` - Order details

**Recommendations**
- `GET /recommend/me` - ML-powered recommendations
- `GET /foryou` - Personalized "For You" page
- `GET /search?q=query` - AI-powered search

**Admin**
- `GET /health` - Health check
- `POST /recommend/reload` - Reload ML model

---

## 🔐 Security Features

### Authentication
- JWT (JSON Web Tokens)
- Bcrypt password hashing
- Token-based authorization
- Secure HTTP-only cookies (optional)

### API Security
- CORS middleware
- Request validation (Pydantic)
- SQL injection prevention (SQLAlchemy ORM)
- Rate limiting (optional with Redis)

---

## 📊 Data Pipeline

### Offline Pipeline (Training)
```
Raw Data → Preprocessing → Feature Engineering → Model Training → Model Export
```

### Online Pipeline (Serving)
```
User Request → Candidate Generation → Feature Engineering → 
Model Scoring → Ranking → Response
```

---

## 🚀 Performance Optimizations

### Backend
- Async/await with FastAPI
- Database query optimization
- Connection pooling
- Model caching (loaded once)
- Optional Redis caching

### Frontend
- Vite for fast builds
- Code splitting
- Lazy loading
- Image optimization (128x128)
- React 19 optimizations

### ML
- Candidate pre-filtering (retrieval)
- Feature caching
- Batch prediction
- Model quantization (optional)

---

## 📈 Monitoring & Observability

### Health Checks
- `/health` endpoint
- Database connectivity check
- Service status monitoring

### Logging
- Python logging module
- Request/response logging
- Error tracking
- Performance metrics

---

## 🔄 Development Workflow

### Local Development
```bash
# Backend
uvicorn main:app --reload

# Frontend
cd frontend && npm run dev

# Full stack
docker-compose up
```

### Testing
- Unit tests (Python)
- Integration tests
- API smoke tests
- Frontend component tests

---

## 📚 Key Technologies Summary

| Category | Technologies |
|----------|-------------|
| **Frontend** | React 19, Vite, TailwindCSS, Axios |
| **Backend** | FastAPI, Uvicorn, SQLAlchemy, JWT |
| **Database** | SQLite, PostgreSQL |
| **ML/AI** | LightGBM, scikit-learn, Google Gemini |
| **Caching** | Redis (optional) |
| **DevOps** | Docker, Docker Compose, GitHub Actions |
| **Languages** | Python 3.11+, JavaScript (ES6+) |

---

## 🎯 Production Considerations

### Scalability
- Horizontal scaling with load balancer
- Database replication
- Redis for distributed caching
- CDN for static assets

### Reliability
- Health checks
- Auto-restart policies
- Database backups
- Model versioning

### Security
- HTTPS/TLS
- Environment secrets
- API rate limiting
- Input validation

---

**Tech Stack Version**: 1.0.0  
**Last Updated**: 2026-02-20  
**Python Version**: 3.11+  
**Node Version**: 18+
