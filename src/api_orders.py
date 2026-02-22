"""
Orders API Router

FastAPI router implementing order management functionality.
Provides checkout (cart to order conversion) and order history.

Usage:
    from fastapi import FastAPI
    from src.api_orders import router as orders_router
    
    app = FastAPI()
    app.include_router(orders_router)
"""

import logging
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.db import get_db, User, Order, OrderItem, CartItem, Product, UserInteraction
from src.api_auth import get_current_user


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Pydantic schemas

class CheckoutIn(BaseModel):
    """
    Checkout request schema.
    
    Attributes:
        address: Delivery address
        payment_method: Payment method (e.g., 'credit_card', 'paypal')
    """
    address: str
    payment_method: str


class BuyNowIn(BaseModel):
    """
    Buy Now request schema.
    
    Attributes:
        article_id: Product article ID to purchase
        qty: Quantity to purchase (default: 1)
        client_order_id: Optional client-supplied ID for idempotency
    """
    article_id: str
    qty: int = 1
    client_order_id: str = None


class OrderItemOut(BaseModel):
    """
    Order item response schema.
    
    Attributes:
        article_id: Product article ID
        qty: Quantity ordered
        price: Price at time of purchase
        name: Product name
        image_path: Product image path
        product_group_name: Product category
    """
    article_id: str
    qty: int
    price: float
    name: str = None
    image_path: str = None
    product_group_name: str = None
    
    model_config = {"from_attributes": True}


class OrderOut(BaseModel):
    """
    Order response schema.
    
    Attributes:
        order_id: Order ID
        created_at: Order creation timestamp
        total_amount: Total order amount
        payment_method: Payment method used
        payment_status: Payment status
        items: List of order items
    """
    order_id: int
    created_at: str
    total_amount: float
    payment_method: str = "standard"
    payment_status: str = "paid"
    items: List[OrderItemOut]


class OrderListOut(BaseModel):
    """
    Order list response schema.
    
    Attributes:
        orders: List of orders
    """
    orders: List[OrderOut]


# Create router
router = APIRouter(prefix="/orders", tags=["orders"])


# API endpoints

@router.post("/checkout")
def checkout(
    checkout_data: CheckoutIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Checkout - Convert cart to order.
    
    Creates an order from the user's cart items, calculates total,
    creates order items, and clears the cart.
    Requires authentication.
    
    Args:
        checkout_data: Checkout information (address, payment_method)
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Order confirmation with order ID, total, and items
        
    Raises:
        HTTPException 400: If cart is empty
        HTTPException 404: If product not found
        HTTPException 500: If database error occurs
    """
    logger.info(f"Checkout initiated for user {current_user.id}")
    
    try:
        # Step 1: Get all cart items for user
        cart_items = db.query(CartItem).filter(
            CartItem.user_id == current_user.id
        ).all()
        
        if not cart_items:
            logger.warning(f"Checkout failed: empty cart for user {current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cart is empty"
            )
        
        # Step 2: Calculate total amount
        total_amount = 0.0
        order_items_data = []
        
        for cart_item in cart_items:
            # Get product to fetch current price
            product = db.query(Product).filter(
                Product.article_id == cart_item.article_id
            ).first()
            
            if not product:
                logger.error(f"Product not found: {cart_item.article_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product {cart_item.article_id} not found"
                )
            
            item_total = product.price * cart_item.qty
            total_amount += item_total
            
            order_items_data.append({
                'article_id': cart_item.article_id,
                'qty': cart_item.qty,
                'price': product.price
            })
        
        logger.info(f"Order total calculated: ${total_amount:.2f}")
        
        # Step 3: Create Order
        new_order = Order(
            user_id=current_user.id,
            total_amount=total_amount,
            payment_method=checkout_data.payment_method,
            payment_status="paid",
            created_at=datetime.utcnow()
        )
        db.add(new_order)
        db.flush()  # Get order ID without committing
        
        # Step 4: Create OrderItems
        order_items = []
        for item_data in order_items_data:
            order_item = OrderItem(
                order_id=new_order.id,
                article_id=item_data['article_id'],
                qty=item_data['qty'],
                price=item_data['price']
            )
            db.add(order_item)
            order_items.append(order_item)
        
        # Step 5: Commit transaction
        db.commit()
        db.refresh(new_order)
        
        logger.info(f"Order created: ID={new_order.id}, Total=${total_amount:.2f}")
        
        # Step 6: Clear cart
        for cart_item in cart_items:
            db.delete(cart_item)
        db.commit()
        
        logger.info(f"Cart cleared for user {current_user.id}")
        
        # Step 7: Return response
        return {
            "order_id": new_order.id,
            "total_amount": total_amount,
            "items": [
                {
                    "article_id": item['article_id'],
                    "qty": item['qty'],
                    "price": item['price']
                }
                for item in order_items_data
            ],
            "message": "Order placed successfully"
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Checkout error for user {current_user.id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing checkout"
        )


@router.post("/buy_now", status_code=status.HTTP_201_CREATED)
def buy_now(
    buy_data: BuyNowIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Buy Now - Instant checkout for a single product.
    
    Creates an order immediately for the specified product without using cart.
    Records purchase interaction for ML tracking.
    Optionally removes product from cart if present.
    Requires authentication.
    
    Args:
        buy_data: Buy now data (article_id, qty, optional client_order_id)
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Order confirmation with order ID, total, and items
        
    Raises:
        HTTPException 400: If qty invalid or insufficient stock
        HTTPException 404: If product not found
        HTTPException 409: If duplicate client_order_id (idempotency)
        HTTPException 500: If database error occurs
    """
    logger.info(f"Buy Now initiated: user={current_user.id}, article={buy_data.article_id}, qty={buy_data.qty}")
    
    try:
        # Step 1: Validate quantity
        if buy_data.qty < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Quantity must be at least 1"
            )
        
        # Step 2: Check for duplicate client_order_id (idempotency)
        if buy_data.client_order_id:
            existing_order = db.query(Order).filter(
                Order.client_order_id == buy_data.client_order_id,
                Order.user_id == current_user.id
            ).first()
            
            if existing_order:
                logger.info(f"Returning existing order for client_order_id: {buy_data.client_order_id}")
                # Return existing order (idempotent)
                order_items = db.query(OrderItem).filter(
                    OrderItem.order_id == existing_order.id
                ).all()
                
                return {
                    "order_id": existing_order.id,
                    "user_id": existing_order.user_id,
                    "total_amount": existing_order.total_amount,
                    "payment_status": existing_order.payment_status,
                    "payment_method": existing_order.payment_method,
                    "items": [
                        {
                            "article_id": item.article_id,
                            "qty": item.qty,
                            "price": item.price
                        }
                        for item in order_items
                    ],
                    "created_at": existing_order.created_at.isoformat(),
                    "message": "Order already exists (idempotent)"
                }
        
        # Step 3: Get product and validate
        product = db.query(Product).filter(
            Product.article_id == buy_data.article_id
        ).first()
        
        if not product:
            logger.warning(f"Product not found: {buy_data.article_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product {buy_data.article_id} not found"
            )
        
        # Step 4: Calculate total
        total_amount = product.price * buy_data.qty
        logger.info(f"Order total calculated: ${total_amount:.2f}")
        
        # Step 5: Create Order
        new_order = Order(
            user_id=current_user.id,
            total_amount=total_amount,
            payment_method="buy_now_placeholder",
            payment_status="paid",
            client_order_id=buy_data.client_order_id,
            created_at=datetime.utcnow()
        )
        db.add(new_order)
        db.flush()  # Get order ID without committing
        
        # Step 6: Create OrderItem
        order_item = OrderItem(
            order_id=new_order.id,
            article_id=buy_data.article_id,
            qty=buy_data.qty,
            price=product.price
        )
        db.add(order_item)
        
        # Step 7: Record purchase interaction for ML
        interaction = UserInteraction(
            user_id=current_user.id,
            article_id=buy_data.article_id,
            event_type="purchase",
            value=total_amount,
            created_at=datetime.utcnow()
        )
        db.add(interaction)
        
        # Step 8: Remove from cart if present
        cart_item = db.query(CartItem).filter(
            CartItem.user_id == current_user.id,
            CartItem.article_id == buy_data.article_id
        ).first()
        
        if cart_item:
            if cart_item.qty <= buy_data.qty:
                # Remove entirely
                db.delete(cart_item)
                logger.info(f"Removed product from cart (bought all)")
            else:
                # Decrement quantity
                cart_item.qty -= buy_data.qty
                logger.info(f"Decremented cart quantity by {buy_data.qty}")
        
        # Step 9: Commit transaction
        db.commit()
        db.refresh(new_order)
        
        logger.info(f"Buy Now order created: ID={new_order.id}, Total=${total_amount:.2f}")
        
        # Step 10: Return response
        return {
            "order_id": new_order.id,
            "user_id": new_order.user_id,
            "total_amount": total_amount,
            "payment_status": "paid",
            "payment_method": "buy_now_placeholder",
            "items": [
                {
                    "article_id": buy_data.article_id,
                    "qty": buy_data.qty,
                    "price": product.price
                }
            ],
            "created_at": new_order.created_at.isoformat(),
            "message": "Order placed successfully"
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Buy Now error for user {current_user.id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing buy now order"
        )


@router.get("/", response_model=OrderListOut)
def get_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get order history for current user.
    
    Returns all orders placed by the authenticated user,
    including order items with product details.
    Requires authentication.
    
    Args:
        current_user: Authenticated user
        db: Database session
        
    Returns:
        List of orders with items and product details
    """
    logger.info(f"Fetching orders for user {current_user.id}")
    
    # Get all orders for user
    orders = db.query(Order).filter(
        Order.user_id == current_user.id
    ).order_by(Order.created_at.desc()).all()
    
    # Build response
    orders_response = []
    for order in orders:
        # Get order items with product details
        order_items = db.query(OrderItem).filter(
            OrderItem.order_id == order.id
        ).all()
        
        items_with_details = []
        for item in order_items:
            # Get product details
            product = db.query(Product).filter(
                Product.article_id == item.article_id
            ).first()
            
            items_with_details.append(OrderItemOut(
                article_id=item.article_id,
                qty=item.qty,
                price=item.price,
                name=product.name if product else None,
                image_path=product.image_path if product else None,
                product_group_name=product.product_group_name if product else None
            ))
        
        orders_response.append(OrderOut(
            order_id=order.id,
            created_at=order.created_at.isoformat(),
            total_amount=order.total_amount,
            payment_method=order.payment_method or "standard",
            payment_status=order.payment_status or "paid",
            items=items_with_details
        ))
    
    logger.info(f"Retrieved {len(orders_response)} orders for user {current_user.id}")
    
    return OrderListOut(orders=orders_response)


@router.get("/{order_id}", response_model=OrderOut)
def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get specific order details.
    
    Returns details of a specific order including all items.
    User can only access their own orders.
    Requires authentication.
    
    Args:
        order_id: Order ID
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Order details with items
        
    Raises:
        HTTPException 404: If order not found
        HTTPException 403: If order belongs to different user
    """
    logger.info(f"Fetching order {order_id} for user {current_user.id}")
    
    # Get order
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        logger.warning(f"Order not found: {order_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Check ownership
    if order.user_id != current_user.id:
        logger.warning(f"Unauthorized access attempt: user {current_user.id} tried to access order {order_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this order"
        )
    
    # Get order items
    order_items = db.query(OrderItem).filter(
        OrderItem.order_id == order.id
    ).all()
    
    logger.info(f"Retrieved order {order_id} with {len(order_items)} items")
    
    return OrderOut(
        order_id=order.id,
        created_at=order.created_at.isoformat(),
        total_amount=order.total_amount,
        payment_method=order.payment_method or "standard",
        payment_status=order.payment_status or "paid",
        items=[
            OrderItemOut(
                article_id=item.article_id,
                qty=item.qty,
                price=item.price
            )
            for item in order_items
        ]
    )


# Test snippet
if __name__ == "__main__":
    """Simple manual test of orders functionality."""
    import sys
    from pathlib import Path
    
    # Add parent directory to path for imports
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    from src.db import SessionLocal, init_db
    
    print("=" * 60)
    print("ORDERS API TEST")
    print("=" * 60)
    
    # Initialize database
    init_db()
    
    # Create session
    db = SessionLocal()
    
    try:
        # Count orders
        order_count = db.query(Order).count()
        print(f"\nTotal orders in database: {order_count}")
        
        if order_count > 0:
            # Get first order
            first_order = db.query(Order).first()
            print(f"\nFirst order:")
            print(f"  Order ID: {first_order.id}")
            print(f"  User ID: {first_order.user_id}")
            print(f"  Total: ${first_order.total_amount:.2f}")
            print(f"  Created: {first_order.created_at}")
            
            # Get order items
            order_items = db.query(OrderItem).filter(
                OrderItem.order_id == first_order.id
            ).all()
            
            print(f"  Items: {len(order_items)}")
            for item in order_items:
                print(f"    - Article {item.article_id}: {item.qty}x @ ${item.price:.2f}")
        else:
            print("\n⚠ No orders in database")
            print("Orders will be created when users checkout")
        
        print("\n" + "=" * 60)
        print("✓ ORDERS API TEST COMPLETE")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
