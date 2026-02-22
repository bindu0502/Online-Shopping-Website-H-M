"""
Database Module

SQLAlchemy ORM models and database utilities for the recommendation system.
Includes user management, product catalog, interactions, cart, and orders.

Usage:
    from src.db import init_db, SessionLocal, User, Product
    
    # Initialize database
    init_db()
    
    # Create session
    db = SessionLocal()
    
    # Query users
    users = db.query(User).all()
"""

import os
from datetime import datetime
from typing import Optional

import bcrypt
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Boolean,
    ForeignKey,
    create_engine
)
from sqlalchemy.orm import sessionmaker, relationship, declarative_base


# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///project149.db')

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={'check_same_thread': False} if 'sqlite' in DATABASE_URL else {},
    echo=False  # Set to True for SQL query logging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


class User(Base):
    """
    User model for authentication and user management.
    
    Attributes:
        id: Primary key
        email: Unique email address
        password_hash: Bcrypt hashed password
        name: User's display name
        created_at: Account creation timestamp
        
    Relationships:
        interactions: User's interaction history
        cart_items: Items in user's cart
        orders: User's order history
    """
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    preferred_categories = Column(String(500), nullable=True)  # Comma-separated categories
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    interactions = relationship('UserInteraction', back_populates='user', cascade='all, delete-orphan')
    cart_items = relationship('CartItem', back_populates='user', cascade='all, delete-orphan')
    wishlist_items = relationship('WishlistItem', back_populates='user', cascade='all, delete-orphan')
    orders = relationship('Order', back_populates='user', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', name='{self.name}')>"


class Product(Base):
    """
    Product model for the article catalog.
    
    Attributes:
        article_id: Primary key (article identifier from dataset)
        name: Product name
        price: Product price
        department_no: Department number
        product_group_name: Product group/category name
        image_path: Path to product image (optional)
        colors: Comma-separated color names (e.g., "red,blue,white")
        primary_color: Main/dominant color name
        
    Relationships:
        interactions: Interactions with this product
        cart_items: Cart items containing this product
        order_items: Order items containing this product
    """
    __tablename__ = 'products'
    
    article_id = Column(String(50), primary_key=True, index=True)
    name = Column(String(500), nullable=False)
    price = Column(Float, nullable=False)
    department_no = Column(Integer, nullable=True)
    product_group_name = Column(String(255), nullable=True)
    image_path = Column(String(500), nullable=True)
    colors = Column(String(255), nullable=True)  # Comma-separated color names
    primary_color = Column(String(50), nullable=True)  # Main/dominant color
    color_description = Column(String(500), nullable=True)  # Detailed color description
    description = Column(String(1000), nullable=True)  # Product description from articles.csv
    color_manually_edited = Column(Boolean, default=False, nullable=False)  # Lock after manual edit
    
    # Relationships
    interactions = relationship('UserInteraction', back_populates='product', cascade='all, delete-orphan')
    cart_items = relationship('CartItem', back_populates='product', cascade='all, delete-orphan')
    wishlist_items = relationship('WishlistItem', back_populates='product', cascade='all, delete-orphan')
    order_items = relationship('OrderItem', back_populates='product')
    
    def __repr__(self):
        return f"<Product(article_id='{self.article_id}', name='{self.name}', price={self.price})>"


class UserInteraction(Base):
    """
    User interaction tracking model.
    
    Tracks user behavior including views, clicks, add-to-cart, and purchases.
    Used for building user profiles and training recommendation models.
    
    Attributes:
        id: Primary key
        user_id: Foreign key to User
        article_id: Foreign key to Product
        event_type: Type of interaction (view, click, add_to_cart, purchase)
        value: Optional value associated with interaction (e.g., purchase amount)
        created_at: Timestamp of interaction
        
    Relationships:
        user: User who performed the interaction
        product: Product that was interacted with
    """
    __tablename__ = 'user_interactions'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    article_id = Column(String(50), ForeignKey('products.article_id'), nullable=False, index=True)
    event_type = Column(String(50), nullable=False, index=True)  # view, click, add_to_cart, purchase
    value = Column(Float, nullable=True)  # Optional value (e.g., purchase amount)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = relationship('User', back_populates='interactions')
    product = relationship('Product', back_populates='interactions')
    
    def __repr__(self):
        return f"<UserInteraction(id={self.id}, user_id={self.user_id}, article_id='{self.article_id}', event_type='{self.event_type}')>"


class CartItem(Base):
    """
    Shopping cart item model.
    
    Represents items in a user's shopping cart.
    
    Attributes:
        id: Primary key
        user_id: Foreign key to User
        article_id: Foreign key to Product
        qty: Quantity of items
        
    Relationships:
        user: User who owns the cart
        product: Product in the cart
    """
    __tablename__ = 'cart_items'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    article_id = Column(String(50), ForeignKey('products.article_id'), nullable=False, index=True)
    qty = Column(Integer, nullable=False, default=1)
    
    # Relationships
    user = relationship('User', back_populates='cart_items')
    product = relationship('Product', back_populates='cart_items')
    
    def __repr__(self):
        return f"<CartItem(id={self.id}, user_id={self.user_id}, article_id='{self.article_id}', qty={self.qty})>"


class WishlistItem(Base):
    """
    Wishlist item model.
    
    Represents items in a user's wishlist.
    
    Attributes:
        id: Primary key
        user_id: Foreign key to User
        article_id: Foreign key to Product
        created_at: When item was added to wishlist
        
    Relationships:
        user: User who owns the wishlist
        product: Product in the wishlist
    """
    __tablename__ = 'wishlist_items'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    article_id = Column(String(50), ForeignKey('products.article_id'), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship('User', back_populates='wishlist_items')
    product = relationship('Product', back_populates='wishlist_items')
    
    def __repr__(self):
        return f"<WishlistItem(id={self.id}, user_id={self.user_id}, article_id='{self.article_id}')>"


class Order(Base):
    """
    Order model for completed purchases.
    
    Attributes:
        id: Primary key
        user_id: Foreign key to User
        total_amount: Total order amount
        payment_method: Payment method used (e.g., 'credit_card', 'buy_now_placeholder')
        payment_status: Payment status ('paid', 'pending', 'failed')
        client_order_id: Optional client-supplied ID for idempotency
        created_at: Order creation timestamp
        
    Relationships:
        user: User who placed the order
        items: Items in the order
    """
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    total_amount = Column(Float, nullable=False)
    payment_method = Column(String(100), nullable=True, default='standard')
    payment_status = Column(String(50), nullable=True, default='paid')
    client_order_id = Column(String(255), nullable=True, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = relationship('User', back_populates='orders')
    items = relationship('OrderItem', back_populates='order', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Order(id={self.id}, user_id={self.user_id}, total_amount={self.total_amount}, payment_status='{self.payment_status}')>"


class OrderItem(Base):
    """
    Order item model for individual items in an order.
    
    Attributes:
        id: Primary key
        order_id: Foreign key to Order
        article_id: Foreign key to Product
        qty: Quantity ordered
        price: Price at time of purchase
        
    Relationships:
        order: Order containing this item
        product: Product that was ordered
    """
    __tablename__ = 'order_items'
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False, index=True)
    article_id = Column(String(50), ForeignKey('products.article_id'), nullable=False, index=True)
    qty = Column(Integer, nullable=False, default=1)
    price = Column(Float, nullable=False)
    
    # Relationships
    order = relationship('Order', back_populates='items')
    product = relationship('Product', back_populates='order_items')
    
    def __repr__(self):
        return f"<OrderItem(id={self.id}, order_id={self.order_id}, article_id='{self.article_id}', qty={self.qty})>"


# Password hashing utilities

def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        Bcrypt hashed password as string
        
    Example:
        >>> hashed = hash_password("mypassword123")
        >>> print(hashed)
        $2b$12$...
    """
    # Generate salt and hash password
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
    return password_hash.decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verify a password against a bcrypt hash.
    
    Args:
        password: Plain text password to verify
        password_hash: Bcrypt hashed password
        
    Returns:
        True if password matches, False otherwise
        
    Example:
        >>> hashed = hash_password("mypassword123")
        >>> verify_password("mypassword123", hashed)
        True
        >>> verify_password("wrongpassword", hashed)
        False
    """
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))


# Database initialization

def init_db() -> None:
    """
    Initialize the database by creating all tables.
    
    Creates all tables defined in the SQLAlchemy models if they don't exist.
    Safe to call multiple times - will not drop existing tables.
    
    Usage:
        >>> from src.db import init_db
        >>> init_db()
        Database initialized
    """
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("Database initialized")


def get_db():
    """
    Dependency function to get database session.
    
    Yields a database session and ensures it's closed after use.
    Useful for FastAPI dependency injection.
    
    Usage:
        >>> from src.db import get_db
        >>> db = next(get_db())
        >>> users = db.query(User).all()
        >>> db.close()
    
    Or with FastAPI:
        >>> @app.get("/users")
        >>> def get_users(db: Session = Depends(get_db)):
        >>>     return db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == '__main__':
    # Initialize database when run as script
    print("Initializing database...")
    print(f"Database URL: {DATABASE_URL}")
    init_db()
    print("✓ Database tables created successfully")
