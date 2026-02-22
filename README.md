# 🛍️ Project149 - E-Commerce Platform with ML Recommendations

> Full-stack e-commerce platform with AI-powered personalized recommendations, built with React, FastAPI, and LightGBM.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-19-61DAFB.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🎯 Overview

Project149 is a production-ready e-commerce platform featuring three intelligent recommendation systems, AI-powered search, and a complete shopping experience. Built to handle 100k+ products with real-time personalization.

### ✨ Key Features

- **🤖 3 Recommendation Systems**
  - ML-powered (LightGBM with 50+ features)
  - Similarity-based (name, color, category matching)
  - Cold-start (category-based for new users)

- **🔍 AI-Powered Search**
  - Google Gemini integration
  - Natural language queries
  - Semantic understanding

- **🛒 Complete Shopping Experience**
  - User authentication (JWT)
  - Shopping cart & wishlist
  - Order management
  - Real-time updates

- **🎨 Advanced Features**
  - Automatic color detection
  - Infinite scrolling
  - Advanced filtering
  - Category navigation
  - Refresh functionality

---

## 📊 Project Stats

- **105,542 products** in catalog
- **19 categories** available
- **50+ ML features** engineered
- **15+ API endpoints** implemented
- **10+ frontend pages** built
- **~15,000 lines** of code

---

## 🛠️ Tech Stack

### Frontend
- **React 19** - UI library
- **Vite** - Build tool
- **TailwindCSS** - Styling
- **Axios** - HTTP client
- **React Router** - Navigation

### Backend
- **FastAPI** - Web framework
- **SQLAlchemy** - ORM
- **LightGBM** - ML model
- **Pandas/NumPy** - Data processing
- **Google Gemini AI** - Search
- **JWT** - Authentication

### Database
- **SQLite** (development)
- **PostgreSQL** (production-ready)

### DevOps
- **Docker** - Containerization
- **Docker Compose** - Orchestration
- **GitHub Actions** - CI/CD

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker (optional)

### Option 1: Docker (Recommended)

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/project149-ecommerce.git
cd project149-ecommerce

# Start with Docker Compose
docker-compose up -d

# Access application
# Frontend: http://localhost
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: Manual Setup

**Backend:**
```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your configuration

# Initialize database
python -c "from src.db import init_db; init_db()"

# Run server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Access at http://localhost:5173
```

---

## 📚 Documentation

- **[Complete Project Guide](PROJECT_COMPLETE_GUIDE.md)** - Comprehensive overview
- **[Tech Stack Details](TECH_STACK.md)** - Technology breakdown
- **[API Documentation](API_COMPLETE.md)** - API endpoints
- **[Deployment Guide](DEPLOY.md)** - Production deployment
- **[Team Presentation](TEAM_PRESENTATION_GUIDE.md)** - How to present this project

---

## 🎓 Architecture

```
┌─────────────────────────────────────────┐
│         React Frontend (Vite)           │
│  - 10+ pages                            │
│  - Reusable components                  │
│  - TailwindCSS styling                  │
└─────────────────────────────────────────┘
                  ↓ HTTP/REST
┌─────────────────────────────────────────┐
│      FastAPI Backend (Uvicorn)          │
│  - 15+ endpoints                        │
│  - JWT authentication                   │
│  - Business logic                       │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│    SQLite/PostgreSQL Database           │
│  - 7 tables                             │
│  - 105k+ products                       │
│  - User data                            │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│         ML/AI Services                  │
│  - LightGBM model                       │
│  - Google Gemini AI                     │
│  - Recommendation engines               │
└─────────────────────────────────────────┘
```

---

## 🔑 Key Endpoints

### Authentication
- `POST /auth/signup` - User registration
- `POST /auth/login` - User login
- `GET /auth/me` - Get current user

### Products
- `GET /products` - List products (with filters)
- `GET /products/{id}` - Product details
- `GET /products/{id}/similar` - Similar products

### Shopping
- `GET /cart` - View cart
- `POST /cart/add` - Add to cart
- `GET /wishlist` - View wishlist
- `POST /orders/checkout` - Create order

### Recommendations
- `GET /recommend/me` - ML-powered recommendations
- `GET /foryou` - Personalized "For You" page
- `GET /search?q=query` - AI-powered search

---

## 🧪 Testing

```bash
# Backend tests
python test_api_auth.py
python test_products_api.py
python test_cart_api.py
python test_foryou.py

# Frontend tests
cd frontend
npm run test
```

---

## 📦 Project Structure

```
Project149/
├── frontend/                 # React application
│   ├── src/
│   │   ├── pages/           # Page components
│   │   ├── components/      # Reusable components
│   │   ├── auth/            # Auth components
│   │   └── api/             # API client
│   └── package.json
│
├── src/                      # Backend source
│   ├── api_*.py             # API routers
│   ├── db.py                # Database models
│   ├── model_train.py       # ML training
│   ├── retrieval.py         # Candidate generation
│   ├── features.py          # Feature engineering
│   └── personalized_recommend.py  # For You system
│
├── models/                   # ML models
├── datasets/                 # Data files (not in git)
├── main.py                   # FastAPI app
├── requirements.txt          # Python dependencies
├── docker-compose.yml        # Docker orchestration
└── README.md                # This file
```

---

## 🎯 Features Breakdown

### Recommendation Systems

**1. ML-Powered (LightGBM)**
- 50+ engineered features
- AUC score: 0.85-0.90
- Real-time prediction
- Candidate generation + ranking

**2. Similarity-Based ("For You")**
- Name similarity (Jaccard)
- Color matching
- Category matching
- Price similarity
- Randomization for variety

**3. Cold-Start (Category-Based)**
- For new users with no activity
- Based on signup preferences
- 20 randomized products
- Solves empty state problem

### AI Search
- Google Gemini integration
- Natural language understanding
- Color/category extraction
- Fallback to traditional search

---

## 🔐 Security

- JWT token authentication
- Bcrypt password hashing
- CORS middleware
- SQL injection prevention (ORM)
- Input validation (Pydantic)

---

## 🚢 Deployment

### Docker Deployment

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Environment Variables

Create `.env` file:

```env
DATABASE_URL=sqlite:///project149.db
API_SECRET=your-secret-key-here
CORS_ORIGINS=http://localhost:5173
GEMINI_API_KEY=your-gemini-key
RECSYS_MODEL_PATH=Project149/models/lgbm_v1.pkl
```

---

## 📈 Performance

- **API Response**: 50-200ms average
- **ML Prediction**: 50-100ms for 500 candidates
- **Frontend Load**: <2 seconds
- **Database**: Optimized with indexes
- **Images**: 128x128 optimized

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Your Name**
- GitHub: [@YOUR_USERNAME](https://github.com/YOUR_USERNAME)
- LinkedIn: [Your LinkedIn](https://linkedin.com/in/your-profile)

---

## 🙏 Acknowledgments

- H&M dataset for product catalog
- FastAPI for excellent documentation
- React community for amazing tools
- LightGBM for fast ML training

---

## 📞 Support

For support, email your.email@example.com or open an issue on GitHub.

---

## 🎉 Demo

**Live Demo**: [Coming Soon]

**Screenshots**:
- Home Page
- Product Details
- For You Recommendations
- Shopping Cart
- Order History

---

**⭐ If you find this project useful, please consider giving it a star!**

---

Made with ❤️ and ☕
