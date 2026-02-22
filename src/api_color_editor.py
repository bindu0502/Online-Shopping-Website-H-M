"""
One-Time Color Editor API

Provides API endpoints for one-time manual editing of product color information.
Each product can only be edited ONCE, then it's permanently locked.
"""

import logging
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.db import get_db, Product

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/color-editor", tags=["color-editor"])


class ColorUpdateRequest(BaseModel):
    """Request model for updating product colors (one-time only)."""
    colors: Optional[str] = None
    primary_color: Optional[str] = None
    color_description: Optional[str] = None


class ProductColorInfo(BaseModel):
    """Product color information response."""
    article_id: str
    name: str
    product_group_name: Optional[str] = None
    image_path: Optional[str] = None  # Add image path
    colors: Optional[str] = None
    primary_color: Optional[str] = None
    color_description: Optional[str] = None
    color_manually_edited: bool = False  # Lock status


class SearchResult(BaseModel):
    """Search results for color editing."""
    products: List[ProductColorInfo]
    total: int
    editable_count: int
    locked_count: int


class EditStats(BaseModel):
    """Statistics about editable vs locked products."""
    total_products: int
    editable_products: int
    locked_products: int
    lock_percentage: float


@router.get("/stats", response_model=EditStats)
def get_edit_statistics(db: Session = Depends(get_db)):
    """
    Get statistics about editable vs locked products.
    
    Returns:
        Statistics about product edit status
    """
    try:
        total_products = db.query(Product).count()
        locked_products = db.query(Product).filter(Product.color_manually_edited == True).count()
        editable_products = total_products - locked_products
        
        return EditStats(
            total_products=total_products,
            editable_products=editable_products,
            locked_products=locked_products,
            lock_percentage=locked_products / total_products * 100 if total_products > 0 else 0
        )
        
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail="Error getting statistics")


@router.get("/search", response_model=SearchResult)
def search_editable_products(
    q: str,
    limit: int = 20,
    show_locked: bool = False,
    db: Session = Depends(get_db)
):
    """
    Search products for color editing.
    
    Args:
        q: Search query (product name)
        limit: Maximum number of results
        show_locked: Include locked products in results
        db: Database session
        
    Returns:
        List of products matching the search query
    """
    try:
        query = db.query(Product).filter(Product.name.ilike(f'%{q}%'))
        
        if not show_locked:
            query = query.filter(Product.color_manually_edited == False)
        
        products = query.limit(limit).all()
        
        # Get counts
        total_matching = db.query(Product).filter(Product.name.ilike(f'%{q}%')).count()
        editable_matching = db.query(Product).filter(
            Product.name.ilike(f'%{q}%'),
            Product.color_manually_edited == False
        ).count()
        locked_matching = total_matching - editable_matching
        
        product_infos = [
            ProductColorInfo(
                article_id=p.article_id,
                name=p.name,
                product_group_name=p.product_group_name,
                image_path=p.image_path,
                colors=p.colors,
                primary_color=p.primary_color,
                color_description=p.color_description,
                color_manually_edited=p.color_manually_edited
            )
            for p in products
        ]
        
        return SearchResult(
            products=product_infos,
            total=len(product_infos),
            editable_count=editable_matching,
            locked_count=locked_matching
        )
        
    except Exception as e:
        logger.error(f"Error searching products: {e}")
        raise HTTPException(status_code=500, detail="Error searching products")


@router.get("/list/editable", response_model=SearchResult)
def list_editable_products(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    List products that can still be edited (not locked).
    
    Args:
        limit: Maximum number of results
        offset: Number of results to skip
        db: Database session
        
    Returns:
        List of editable products
    """
    try:
        products = db.query(Product).filter(
            Product.color_manually_edited == False
        ).offset(offset).limit(limit).all()
        
        # Get counts
        total_editable = db.query(Product).filter(Product.color_manually_edited == False).count()
        total_locked = db.query(Product).filter(Product.color_manually_edited == True).count()
        
        product_infos = [
            ProductColorInfo(
                article_id=p.article_id,
                name=p.name,
                product_group_name=p.product_group_name,
                image_path=p.image_path,
                colors=p.colors,
                primary_color=p.primary_color,
                color_description=p.color_description,
                color_manually_edited=p.color_manually_edited
            )
            for p in products
        ]
        
        return SearchResult(
            products=product_infos,
            total=len(product_infos),
            editable_count=total_editable,
            locked_count=total_locked
        )
        
    except Exception as e:
        logger.error(f"Error listing editable products: {e}")
        raise HTTPException(status_code=500, detail="Error listing editable products")


@router.get("/{article_id}", response_model=ProductColorInfo)
def get_product_color_info(
    article_id: str,
    db: Session = Depends(get_db)
):
    """
    Get color information for a specific product.
    
    Args:
        article_id: Product article ID
        db: Database session
        
    Returns:
        Product color information with lock status
    """
    product = db.query(Product).filter(Product.article_id == article_id).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return ProductColorInfo(
        article_id=product.article_id,
        name=product.name,
        product_group_name=product.product_group_name,
        image_path=product.image_path,
        colors=product.colors,
        primary_color=product.primary_color,
        color_description=product.color_description,
        color_manually_edited=product.color_manually_edited
    )


@router.put("/{article_id}")
def update_product_colors_once(
    article_id: str,
    color_update: ColorUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    Update color information for a specific product (ONE TIME ONLY).
    
    Args:
        article_id: Product article ID
        color_update: New color information
        db: Database session
        
    Returns:
        Success message with lock confirmation
    """
    try:
        product = db.query(Product).filter(Product.article_id == article_id).first()
        
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Check if product is already locked
        if product.color_manually_edited:
            raise HTTPException(
                status_code=403, 
                detail="Product is permanently locked. Colors have already been manually edited and cannot be changed."
            )
        
        # Update fields if provided
        if color_update.colors is not None:
            product.colors = color_update.colors if color_update.colors.strip() else None
        
        if color_update.primary_color is not None:
            product.primary_color = color_update.primary_color if color_update.primary_color.strip() else None
        
        if color_update.color_description is not None:
            product.color_description = color_update.color_description if color_update.color_description.strip() else None
        
        # PERMANENTLY LOCK the product
        product.color_manually_edited = True
        
        db.commit()
        
        logger.info(f"ONE-TIME EDIT: Updated and locked colors for product {article_id}")
        
        return {
            "message": "Product colors updated successfully and PERMANENTLY LOCKED",
            "article_id": article_id,
            "colors": product.colors,
            "primary_color": product.primary_color,
            "color_description": product.color_description,
            "locked": True,
            "warning": "This product is now permanently locked and cannot be edited again"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating product colors: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error updating product colors")


@router.post("/{article_id}/generate-suggestions")
def generate_color_suggestions(
    article_id: str,
    db: Session = Depends(get_db)
):
    """
    Generate color suggestions for a product using the intelligent system.
    
    Args:
        article_id: Product article ID
        db: Database session
        
    Returns:
        Generated color suggestions (only if product is not locked)
    """
    try:
        product = db.query(Product).filter(Product.article_id == article_id).first()
        
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Check if product is locked
        if product.color_manually_edited:
            raise HTTPException(
                status_code=403, 
                detail="Product is permanently locked. Cannot generate suggestions for locked products."
            )
        
        from src.color_generator import color_generator
        
        # Generate suggestions
        color_info = color_generator.generate_color_info(
            product_name=product.name,
            product_group=product.product_group_name,
            department_name=str(product.department_no) if product.department_no else None,
            existing_colors=product.colors
        )
        
        return {
            "article_id": article_id,
            "current": {
                "colors": product.colors,
                "primary_color": product.primary_color,
                "color_description": product.color_description
            },
            "suggestions": {
                "colors": color_info.color,
                "primary_color": color_info.color,
                "color_description": color_info.color_description,
                "confidence": color_info.confidence
            },
            "editable": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating suggestions: {e}")
        raise HTTPException(status_code=500, detail="Error generating suggestions")