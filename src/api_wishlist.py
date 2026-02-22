"""
Wishlist API Router

FastAPI router implementing wishlist functionality.
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.db import get_db, User, Product, WishlistItem
from src.api_auth import get_current_user

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Pydantic schemas

class WishlistItemOut(BaseModel):
    """Wishlist item response schema."""
    id: int
    article_id: str
    name: str
    price: float
    image_path: Optional[str] = None
    product_group_name: Optional[str] = None
    
    model_config = {"from_attributes": True}


class WishlistResponse(BaseModel):
    """Wishlist response with items."""
    items: List[WishlistItemOut]


class WishlistAddIn(BaseModel):
    """Add to wishlist request schema."""
    article_id: str


# Create router
router = APIRouter(prefix="/wishlist", tags=["wishlist"])


@router.get("/", response_model=WishlistResponse)
def get_wishlist(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's wishlist."""
    logger.info(f"Fetching wishlist for user {current_user.id}")
    
    wishlist_items = db.query(WishlistItem).filter(
        WishlistItem.user_id == current_user.id
    ).all()
    
    items = []
    for item in wishlist_items:
        product = db.query(Product).filter(
            Product.article_id == item.article_id
        ).first()
        
        if product:
            items.append(WishlistItemOut(
                id=item.id,
                article_id=item.article_id,
                name=product.name,
                price=product.price,
                image_path=product.image_path,
                product_group_name=product.product_group_name
            ))
    
    logger.info(f"Retrieved {len(items)} items from wishlist")
    return WishlistResponse(items=items)


@router.post("/add")
def add_to_wishlist(
    wishlist_item: WishlistAddIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add item to wishlist."""
    logger.info(f"Adding to wishlist: user={current_user.id}, article={wishlist_item.article_id}")
    
    # Check if product exists
    product = db.query(Product).filter(
        Product.article_id == wishlist_item.article_id
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check if already in wishlist
    existing = db.query(WishlistItem).filter(
        WishlistItem.user_id == current_user.id,
        WishlistItem.article_id == wishlist_item.article_id
    ).first()
    
    if existing:
        return {"message": "Already in wishlist", "wishlist_item_id": existing.id}
    
    # Add to wishlist
    new_item = WishlistItem(
        user_id=current_user.id,
        article_id=wishlist_item.article_id
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    
    logger.info(f"Added to wishlist: {new_item.id}")
    return {"message": "Added to wishlist", "wishlist_item_id": new_item.id}


@router.post("/remove/{article_id}")
def remove_from_wishlist(
    article_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove item from wishlist."""
    logger.info(f"Removing from wishlist: user={current_user.id}, article={article_id}")
    
    item = db.query(WishlistItem).filter(
        WishlistItem.user_id == current_user.id,
        WishlistItem.article_id == article_id
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not in wishlist")
    
    db.delete(item)
    db.commit()
    
    logger.info(f"Removed from wishlist: {item.id}")
    return {"message": "Removed from wishlist"}
