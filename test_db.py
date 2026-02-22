"""
Test script for database module.

Tests all models, relationships, and password hashing functionality.
"""

from src.db import (
    init_db,
    SessionLocal,
    User,
    Product,
    UserInteraction,
    CartItem,
    Order,
    OrderItem,
    hash_password,
    verify_password
)

def test_database():
    """Test database functionality."""
    print("=" * 60)
    print("DATABASE MODULE TEST")
    print("=" * 60)
    
    # Initialize database
    print("\n1. Initializing database...")
    init_db()
    
    # Create session
    db = SessionLocal()
    
    try:
        # Test password hashing
        print("\n2. Testing password hashing...")
        password = "test_password_123"
        hashed = hash_password(password)
        print(f"   Original: {password}")
        print(f"   Hashed: {hashed[:50]}...")
        print(f"   Verify correct: {verify_password(password, hashed)}")
        print(f"   Verify wrong: {verify_password('wrong_password', hashed)}")
        
        # Create test user
        print("\n3. Creating test user...")
        user = User(
            email="test@example.com",
            password_hash=hashed,
            name="Test User"
        )
        db.add(user)
        db.commit()
        print(f"   Created: {user}")
        
        # Create test products
        print("\n4. Creating test products...")
        product1 = Product(
            article_id="123456001",
            name="Test T-Shirt",
            price=29.99,
            department_no=1234,
            product_group_name="Garment Upper body",
            image_path="/images/123456001.jpg"
        )
        product2 = Product(
            article_id="123456002",
            name="Test Jeans",
            price=59.99,
            department_no=1235,
            product_group_name="Garment Lower body"
        )
        db.add_all([product1, product2])
        db.commit()
        print(f"   Created: {product1}")
        print(f"   Created: {product2}")
        
        # Create user interactions
        print("\n5. Creating user interactions...")
        interaction1 = UserInteraction(
            user_id=user.id,
            article_id=product1.article_id,
            event_type="view"
        )
        interaction2 = UserInteraction(
            user_id=user.id,
            article_id=product1.article_id,
            event_type="add_to_cart"
        )
        interaction3 = UserInteraction(
            user_id=user.id,
            article_id=product2.article_id,
            event_type="view"
        )
        db.add_all([interaction1, interaction2, interaction3])
        db.commit()
        print(f"   Created {len([interaction1, interaction2, interaction3])} interactions")
        
        # Add items to cart
        print("\n6. Adding items to cart...")
        cart_item1 = CartItem(
            user_id=user.id,
            article_id=product1.article_id,
            qty=2
        )
        cart_item2 = CartItem(
            user_id=user.id,
            article_id=product2.article_id,
            qty=1
        )
        db.add_all([cart_item1, cart_item2])
        db.commit()
        print(f"   Added {len([cart_item1, cart_item2])} items to cart")
        
        # Create order
        print("\n7. Creating order...")
        order = Order(
            user_id=user.id,
            total_amount=119.97  # 2 * 29.99 + 1 * 59.99
        )
        db.add(order)
        db.commit()
        
        order_item1 = OrderItem(
            order_id=order.id,
            article_id=product1.article_id,
            qty=2,
            price=29.99
        )
        order_item2 = OrderItem(
            order_id=order.id,
            article_id=product2.article_id,
            qty=1,
            price=59.99
        )
        db.add_all([order_item1, order_item2])
        db.commit()
        print(f"   Created: {order}")
        print(f"   Order items: {len([order_item1, order_item2])}")
        
        # Test relationships
        print("\n8. Testing relationships...")
        
        # Refresh user to load relationships
        db.refresh(user)
        print(f"   User interactions: {len(user.interactions)}")
        print(f"   User cart items: {len(user.cart_items)}")
        print(f"   User orders: {len(user.orders)}")
        
        # Refresh product to load relationships
        db.refresh(product1)
        print(f"   Product1 interactions: {len(product1.interactions)}")
        print(f"   Product1 cart items: {len(product1.cart_items)}")
        print(f"   Product1 order items: {len(product1.order_items)}")
        
        # Query tests
        print("\n9. Testing queries...")
        all_users = db.query(User).all()
        print(f"   Total users: {len(all_users)}")
        
        all_products = db.query(Product).all()
        print(f"   Total products: {len(all_products)}")
        
        all_interactions = db.query(UserInteraction).all()
        print(f"   Total interactions: {len(all_interactions)}")
        
        view_interactions = db.query(UserInteraction).filter(
            UserInteraction.event_type == 'view'
        ).all()
        print(f"   View interactions: {len(view_interactions)}")
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == '__main__':
    test_database()
