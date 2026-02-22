"""
Shopping Cart API Router

FastAPI router implementing shopping cart functionality.
Provides cart viewing, adding items, removing items, and clearing cart.

Usage:
    from fastapi import FastAPI
    from src.api_cart import router as cart_router
    
    app = FastAPI()
    app.include_router(cart_router)
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.db import get_db, User, Product, CartItem
from src.api_auth import get_current_user


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Pydantic schemas

class CartItemOut(BaseModel):
    """
    Cart item response schema.
    
    Attributes:
        id: Cart item ID
        article_id: Product article ID
        name: Product name
        price: Product price
        quantity: Quantity in cart
        image_path: Product image path
        product_group_name: Product group/category
    """
    id: int
    article_id: str
    name: str
    price: float
    quantity: int
    image_path: Optional[str] = None
    product_group_name: Optional[str] = None
    
    model_config = {"from_attributes": True}


class CartResponse(BaseModel):
    """
    Cart response schema with items and total.
    
    Attributes:
        items: List of cart items
        total: Total price of all items
    """
    items: List[CartItemOut]
    total: float


class CartAddIn(BaseModel):
    """
    Add to cart request schema.
    
    Attributes:
        article_id: Product article ID to add
        quantity: Quantity to add (default: 1)
    """
    article_id: str
    quantity: int = 1


# Create router
router = APIRouter(prefix="/cart", tags=["cart"])


# API endpoints

@router.get("/", response_model=CartResponse)
def get_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's shopping cart.
    
    Returns all items in the user's cart with product details and total.
    Requires authentication.
    
    Args:
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Cart with items and total price
    """
    logger.info(f"Fetching cart for user {current_user.id}")
    
    # Query cart items with product information
    cart_items = db.query(CartItem).filter(
        CartItem.user_id == current_user.id
    ).all()
    
    # Build response with product details
    items = []
    total = 0.0
    
    for item in cart_items:
        product = db.query(Product).filter(
            Product.article_id == item.article_id
        ).first()
        
        if product:
            item_total = product.price * item.qty
            total += item_total
            
            items.append(CartItemOut(
                id=item.id,
                article_id=item.article_id,
                name=product.name,
                price=product.price,
                quantity=item.qty,
                image_path=product.image_path,
                product_group_name=product.product_group_name
            ))
        else:
            # Product no longer exists, log warning
            logger.warning(f"Product {item.article_id} in cart but not found in catalog")
    
    logger.info(f"Retrieved {len(items)} items from cart, total: ${total:.2f}")
    return CartResponse(items=items, total=total)


@router.post("/add")
def add_to_cart(
    cart_item: CartAddIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add item to shopping cart.
    
    If item already exists in cart, increases quantity.
    Otherwise, creates new cart item.
    Requires authentication.
    
    Args:
        cart_item: Item to add (article_id and qty)
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Success message with cart item ID
        
    Raises:
        HTTPException 404: If product not found
    """
    logger.info(f"Adding to cart: user={current_user.id}, article={cart_item.article_id}, qty={cart_item.quantity}")
    
    # Step 1: Check if product exists
    product = db.query(Product).filter(
        Product.article_id == cart_item.article_id
    ).first()
    
    if not product:
        logger.warning(f"Product not found: {cart_item.article_id}")
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Step 2: Check if item already in cart
    existing_item = db.query(CartItem).filter(
        CartItem.user_id == current_user.id,
        CartItem.article_id == cart_item.article_id
    ).first()
    
    if existing_item:
        # Step 3: Increase quantity
        existing_item.qty += cart_item.quantity
        db.commit()
        db.refresh(existing_item)
        
        logger.info(f"Updated cart item {existing_item.id}: new qty={existing_item.qty}")
        return {
            "message": "Item quantity updated",
            "cart_item_id": existing_item.id,
            "quantity": existing_item.qty
        }
    else:
        # Step 4: Create new cart item
        new_cart_item = CartItem(
            user_id=current_user.id,
            article_id=cart_item.article_id,
            qty=cart_item.quantity
        )
        db.add(new_cart_item)
        db.commit()
        db.refresh(new_cart_item)
        
        logger.info(f"Created cart item {new_cart_item.id}")
        return {
            "message": "Item added to cart",
            "cart_item_id": new_cart_item.id,
            "quantity": new_cart_item.qty
        }


@router.post("/remove/{article_id}")
def remove_from_cart(
    article_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove item from shopping cart.
    
    Removes the specified article from user's cart.
    Requires authentication.
    
    Args:
        article_id: Article ID to remove
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException 404: If item not in cart
    """
    logger.info(f"Removing from cart: user={current_user.id}, article={article_id}")
    
    # Find cart item
    cart_item = db.query(CartItem).filter(
        CartItem.user_id == current_user.id,
        CartItem.article_id == article_id
    ).first()
    
    if not cart_item:
        logger.warning(f"Cart item not found: user={current_user.id}, article={article_id}")
        raise HTTPException(status_code=404, detail="Item not in cart")
    
    # Remove item
    db.delete(cart_item)
    db.commit()
    
    logger.info(f"Removed cart item {cart_item.id}")
    return {"message": "Item removed from cart"}


@router.post("/clear")
def clear_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Clear all items from shopping cart.
    
    Removes all items from user's cart.
    Requires authentication.
    
    Args:
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Success message with count of removed items
    """
    logger.info(f"Clearing cart for user {current_user.id}")
    
    # Get all cart items for user
    cart_items = db.query(CartItem).filter(
        CartItem.user_id == current_user.id
    ).all()
    
    item_count = len(cart_items)
    
    # Delete all items
    for item in cart_items:
        db.delete(item)
    
    db.commit()
    
    logger.info(f"Cleared {item_count} items from cart")
    return {
        "message": "Cart cleared",
        "items_removed": item_count
    }


# Test snippet
if __name__ == "__main__":
    """Simple manual test of cart functionality."""
    import sys
    from pathlib import Path
    
    # Add parent directory to path for imports
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    from src.db import SessionLocal, init_db
    
    print("=" * 60)
    print("CART API TEST")
    print("=" * 60)
    
    # Initialize database
    init_db()
    
    # Create session
    db = SessionLocal()
    
    try:
        # Count cart items
        cart_count = db.query(CartItem).count()
        print(f"\nTotal cart items in database: {cart_count}")
        
        if cart_count > 0:
            # Get first cart item
            first_item = db.query(CartItem).first()
            print(f"\nFirst cart item:")
            print(f"  ID: {first_item.id}")
            print(f"  User ID: {first_item.user_id}")
            print(f"  Article ID: {first_item.article_id}")
            print(f"  Quantity: {first_item.qty}")
            
            # Get product details
            product = db.query(Product).filter(
                Product.article_id == first_item.article_id
            ).first()
            
            if product:
                print(f"  Product: {product.name}")
                print(f"  Price: ${product.price:.2f}")
        else:
            print("\n⚠ No cart items in database")
            print("Cart items will be created when users add products")
        
        print("\n" + "=" * 60)
        print("✓ CART API TEST COMPLETE")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
