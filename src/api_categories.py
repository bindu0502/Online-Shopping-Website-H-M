"""
Categories API Router

FastAPI router for product categories.
"""

import logging
from typing import List

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct

from src.db import get_db, Product

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Pydantic schemas

class CategoryOut(BaseModel):
    """Category response schema."""
    name: str
    count: int


class CategoriesResponse(BaseModel):
    """Categories list response."""
    categories: List[CategoryOut]


# Create router
router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=CategoriesResponse)
def get_categories(db: Session = Depends(get_db)):
    """
    Get all available product categories with product counts.
    
    Returns:
        List of categories with product counts
    """
    # Get distinct categories with counts
    categories = db.query(
        Product.product_group_name,
        func.count(Product.article_id).label('count')
    ).filter(
        Product.product_group_name.isnot(None),
        Product.product_group_name != ''
    ).group_by(
        Product.product_group_name
    ).order_by(
        func.count(Product.article_id).desc()
    ).all()
    
    result = [
        CategoryOut(name=cat[0], count=cat[1])
        for cat in categories
    ]
    
    logger.info(f"Returning {len(result)} categories")
    
    return CategoriesResponse(categories=result)


@router.get("/{category_name}/products")
def get_category_products(
    category_name: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get products by category.
    
    Args:
        category_name: Category name
        skip: Number of products to skip (pagination)
        limit: Maximum number of products to return
        db: Database session
        
    Returns:
        List of products in the category
    """
    # Query products in category
    products = db.query(Product).filter(
        Product.product_group_name == category_name
    ).offset(skip).limit(limit).all()
    
    # Get total count
    total = db.query(func.count(Product.article_id)).filter(
        Product.product_group_name == category_name
    ).scalar()
    
    logger.info(f"Returning {len(products)} products for category '{category_name}'")
    
    return {
        "category": category_name,
        "products": [
            {
                "article_id": p.article_id,
                "name": p.name,
                "price": p.price,
                "image_path": p.image_path,
                "product_group_name": p.product_group_name,
                "primary_color": p.primary_color,
                "color_description": p.color_description,
                "colors": p.colors,
                "description": p.description
            }
            for p in products
        ],
        "total": total,
        "skip": skip,
        "limit": limit
    }
