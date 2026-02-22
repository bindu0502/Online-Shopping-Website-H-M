"""
Main FastAPI Application

Simple FastAPI app with authentication endpoints.

Run with:
    uvicorn main:app --reload
    
Or:
    python main.py
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from src.api_auth import router as auth_router
from src.api_products import router as products_router
from src.api_cart import router as cart_router
from src.api_wishlist import router as wishlist_router
from src.api_orders import router as orders_router
from src.api_interactions import router as interactions_router
from src.api_recommend import router as recommend_router
from src.api_search import router as search_router
from src.api_color_editor import router as color_editor_router
from src.api_foryou import router as foryou_router
from src.api_categories import router as categories_router
from src.db import init_db
import os

# Initialize database
init_db()

# Create FastAPI app
app = FastAPI(
    title="Project149 API",
    description="E-Commerce API with ML-Powered Recommendations",
    version="1.0.0"
)

# Configure CORS
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
allowed_origins = [origin.strip() for origin in cors_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for product images
images_path = "Project149/datasets/images_128_128"
if os.path.exists(images_path):
    app.mount("/images", StaticFiles(directory=images_path), name="images")

# Include routers
app.include_router(auth_router)
app.include_router(products_router)
app.include_router(cart_router)
app.include_router(wishlist_router)
app.include_router(orders_router)
app.include_router(interactions_router)
app.include_router(recommend_router)
app.include_router(search_router)
app.include_router(color_editor_router)
app.include_router(foryou_router)
app.include_router(categories_router)


@app.get("/health")
@app.get("/healthz")
def health_check():
    """Health check endpoint for monitoring and load balancers."""
    from src.db import SessionLocal
    
    health_status = {
        "status": "healthy",
        "service": "project149-api",
        "version": "1.0.0"
    }
    
    # Check database
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        health_status["database"] = "connected"
    except Exception as e:
        health_status["database"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check if images directory exists
    if os.path.exists("Project149/datasets/images_128_128"):
        health_status["images"] = "available"
    else:
        health_status["images"] = "missing"
    
    return health_status


@app.get("/")
def root():
    """Root endpoint - API information."""
    return {
        "message": "Welcome to Project149 API - E-Commerce with ML Recommendations",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs",
        "features": [
            "User Authentication (JWT)",
            "Product Catalog",
            "Shopping Cart",
            "Order Management",
            "User Behavior Tracking",
            "ML-Powered Recommendations",
            "AI-Powered Search (Gemini)"
        ],
        "endpoints": {
            "auth": {
                "signup": "POST /auth/signup",
                "login": "POST /auth/login",
                "profile": "GET /auth/me"
            },
            "products": {
                "list": "GET /products",
                "detail": "GET /products/{article_id}",
                "similar": "GET /products/{article_id}/similar"
            },
            "cart": {
                "view": "GET /cart",
                "add": "POST /cart/add",
                "remove": "POST /cart/remove/{article_id}",
                "clear": "POST /cart/clear"
            },
            "orders": {
                "checkout": "POST /orders/checkout",
                "history": "GET /orders",
                "detail": "GET /orders/{order_id}"
            },
            "interactions": {
                "record": "POST /interactions/record",
                "bulk": "POST /interactions/bulk",
                "user_history": "GET /interactions/user",
                "item_top": "GET /interactions/item/{article_id}/top",
                "popular": "GET /interactions/popular"
            },
            "recommendations": {
                "personalized": "GET /recommend/me",
                "for_user": "GET /recommend/user/{user_id}",
                "health": "GET /recommend/health",
                "reload": "POST /recommend/reload"
            },
            "foryou": {
                "personalized": "GET /foryou"
            },
            "search": {
                "search": "GET /search?q=query",
                "suggestions": "GET /search/suggestions?q=partial"
            }
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
