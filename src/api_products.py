"""
Products API Router

FastAPI router implementing product catalog endpoints.
Provides product listing, detail view, and similarity recommendations.

Usage:
    from fastapi import FastAPI
    from src.api_products import router as products_router
    
    app = FastAPI()
    app.include_router(products_router)
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.db import get_db, Product


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Pydantic schemas

class ProductOut(BaseModel):
    """
    Product response schema with guaranteed color information.
    
    Attributes:
        article_id: Unique article identifier
        name: Product name
        price: Product price
        department_no: Department number (optional)
        product_group_name: Product group/category (optional)
        image_path: Path to product image (optional)
        colors: Comma-separated color names (always present)
        primary_color: Main color name (always present)
        color_description: Natural language color description (always present)
        description: Product description from articles.csv (optional)
        matched_color: Color that matched search query (optional)
    """
    model_config = {"from_attributes": True}
    
    article_id: str
    name: str
    price: float
    department_no: Optional[int] = None
    product_group_name: Optional[str] = None
    image_path: Optional[str] = None
    colors: str  # Always present - comma-separated color names
    primary_color: str  # Always present
    color_description: str  # Always present - natural language color description
    description: Optional[str] = None  # Product description from articles.csv
    matched_color: Optional[str] = None  # Color that matched the search query
    
    @classmethod
    def from_product(cls, product: Product, matched_color: str = None) -> 'ProductOut':
        """
        Create ProductOut from Product with guaranteed color information.
        
        Args:
            product: Database Product object
            matched_color: Color that matched search query (optional)
            
        Returns:
            ProductOut with complete color information
        """
        from src.color_generator import color_generator
        
        # Ensure we have color information
        colors = product.colors
        primary_color = product.primary_color
        color_description = product.color_description
        
        # Generate missing color information if needed
        if not colors or not primary_color or not color_description:
            color_info = color_generator.generate_color_info(
                product_name=product.name,
                product_group=product.product_group_name,
                department_name=str(product.department_no) if product.department_no else None,
                existing_colors=product.colors
            )
            
            if not colors:
                colors = color_info.color
            if not primary_color:
                primary_color = color_info.color
            if not color_description:
                color_description = color_info.color_description
        
        return cls(
            article_id=product.article_id,
            name=product.name,
            price=product.price,
            department_no=product.department_no,
            product_group_name=product.product_group_name,
            image_path=product.image_path,
            colors=colors,
            primary_color=primary_color,
            color_description=color_description,
            description=product.description,
            matched_color=matched_color
        )
    
    @property
    def color_list(self) -> List[str]:
        """Return colors as a list."""
        if self.colors:
            return [c.strip() for c in self.colors.split(',')]
        return []


# Create router
router = APIRouter(prefix="/products", tags=["products"])


# API endpoints

class ProductListResponse(BaseModel):
    """
    Product list response with pagination info.
    
    Attributes:
        products: List of products
        total: Total number of products in database
        page: Current page number
        limit: Number of products per page
        total_pages: Total number of pages
    """
    products: List[ProductOut]
    total: int
    page: int
    limit: int
    total_pages: int


@router.get("/", response_model=ProductListResponse)
def get_products(
    page: int = Query(1, ge=1, description="Page number (starts at 1)"),
    limit: int = Query(20, ge=1, le=100, description="Number of products per page"),
    skip: Optional[int] = Query(None, ge=0, description="Number of products to skip (alternative to page)"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price filter"),
    department: Optional[int] = Query(None, description="Department number filter"),
    sort: Optional[str] = Query(None, description="Sort by: price_asc, price_desc, popular, random"),
    randomize: bool = Query(False, description="Randomize product order"),
    db: Session = Depends(get_db)
):
    """
    Get list of products with pagination.
    
    Returns products with optional randomization for dynamic ordering.
    Supports both page-based and skip-based pagination.
    
    Args:
        page: Page number (starts at 1). Ignored if skip is provided.
        limit: Number of products per page (max 100)
        skip: Number of products to skip (alternative to page parameter)
        randomize: If True, randomize product order (optimized for large datasets)
        sort: Sort order (random, price_asc, price_desc, popular)
        db: Database session
        
    Returns:
        ProductListResponse with products and pagination info
        
    Examples:
        GET /products?page=1&limit=20&randomize=true  # Random first 20 products
        GET /products?sort=random&limit=20            # Random products via sort
    """
    import random
    
    # Calculate skip from page if not provided
    if skip is None:
        skip = (page - 1) * limit
    else:
        # If skip is provided, calculate the page number
        page = (skip // limit) + 1
    
    logger.info(f"Fetching products: page={page}, skip={skip}, limit={limit}, randomize={randomize}, filters: min_price={min_price}, max_price={max_price}, dept={department}, sort={sort}")
    
    try:
        # Build query with filters
        query = db.query(Product)
        
        # Apply price filters
        if min_price is not None:
            query = query.filter(Product.price >= min_price)
        if max_price is not None:
            query = query.filter(Product.price <= max_price)
        
        # Apply department filter
        if department is not None:
            query = query.filter(Product.department_no == department)
        
        # Get total count with filters
        total = query.count()
        
        # Handle randomization (optimized for large datasets)
        if randomize or sort == "random":
            if total > 1000:  # For large datasets, use random offset (faster)
                # Calculate safe random offset
                max_offset = max(0, total - limit)
                random_offset = random.randint(0, max_offset) if max_offset > 0 else 0
                
                # Use the random offset instead of skip for randomization
                products = query.offset(random_offset).limit(limit).all()
                
                # For randomized queries, we don't use traditional pagination
                # Return as if it's page 1 with total available
                page = 1
                total_pages = 1  # Randomized view doesn't have meaningful pagination
                
                logger.info(f"Used random offset {random_offset} for large dataset")
            else:
                # For smaller datasets, use ORDER BY RANDOM()
                query = query.order_by(func.random())
                products = query.offset(skip).limit(limit).all()
                total_pages = (total + limit - 1) // limit
        else:
            # Apply sorting for non-randomized queries
            if sort == "price_asc":
                query = query.order_by(Product.price.asc())
            elif sort == "price_desc":
                query = query.order_by(Product.price.desc())
            elif sort == "popular":
                # For now, random order (can be enhanced with interaction data)
                query = query.order_by(func.random())
            else:
                query = query.order_by(Product.article_id)
            
            # Get products for current page
            products = query.offset(skip).limit(limit).all()
            
            # Calculate total pages
            total_pages = (total + limit - 1) // limit  # Ceiling division
        
        logger.info(f"Retrieved {len(products)} products (page {page}/{total_pages}, total: {total})")
        
        return ProductListResponse(
            products=[ProductOut.from_product(p) for p in products],
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages
        )
        
    except Exception as e:
        logger.error(f"Error fetching products: {e}")
        raise HTTPException(status_code=500, detail="Error fetching products")


@router.get("/{article_id}", response_model=ProductOut)
def get_product(article_id: str, db: Session = Depends(get_db)):
    """
    Get product details by article ID.
    
    Args:
        article_id: Article identifier
        db: Database session
        
    Returns:
        Product details
        
    Raises:
        HTTPException 404: If product not found
    """
    logger.info(f"Fetching product: {article_id}")
    
    product = db.query(Product).filter(Product.article_id == article_id).first()
    
    if not product:
        logger.warning(f"Product not found: {article_id}")
        raise HTTPException(status_code=404, detail="Product not found")
    
    logger.info(f"Retrieved product: {product.name}")
    return ProductOut.from_product(product)


@router.get("/{article_id}/similar", response_model=List[ProductOut])
def get_similar_products(article_id: str, db: Session = Depends(get_db)):
    """
    Get similar products based on department and product group.
    
    Similarity logic:
    1. Products from same department (excluding the queried product)
    2. If less than 10, add products from same product group
    3. If still less than 10, fill with random products
    
    Args:
        article_id: Article identifier to find similar products for
        db: Database session
        
    Returns:
        List of up to 10 similar products
        
    Raises:
        HTTPException 404: If product not found
    """
    logger.info(f"Fetching similar products for: {article_id}")
    
    # Get the source product
    source_product = db.query(Product).filter(Product.article_id == article_id).first()
    
    if not source_product:
        logger.warning(f"Product not found: {article_id}")
        raise HTTPException(status_code=404, detail="Product not found")
    
    similar_products = []
    seen_ids = {article_id}  # Track seen article IDs to avoid duplicates
    
    # Step 1: Get products from same department
    if source_product.department_no is not None:
        logger.debug(f"Finding products in department: {source_product.department_no}")
        
        dept_products = db.query(Product).filter(
            Product.department_no == source_product.department_no,
            Product.article_id != article_id
        ).limit(10).all()
        
        for product in dept_products:
            if product.article_id not in seen_ids:
                similar_products.append(product)
                seen_ids.add(product.article_id)
        
        logger.debug(f"Found {len(similar_products)} products from same department")
    
    # Step 2: If less than 10, add products from same product group
    if len(similar_products) < 10 and source_product.product_group_name:
        logger.debug(f"Finding products in group: {source_product.product_group_name}")
        
        remaining = 10 - len(similar_products)
        
        group_products = db.query(Product).filter(
            Product.product_group_name == source_product.product_group_name,
            Product.article_id != article_id
        ).limit(remaining * 2).all()  # Get more to filter out duplicates
        
        for product in group_products:
            if product.article_id not in seen_ids:
                similar_products.append(product)
                seen_ids.add(product.article_id)
                if len(similar_products) >= 10:
                    break
        
        logger.debug(f"Now have {len(similar_products)} products after adding from same group")
    
    # Step 3: If still less than 10, fill with random products
    if len(similar_products) < 10:
        logger.debug("Filling remaining slots with random products")
        
        remaining = 10 - len(similar_products)
        
        # Get random products (SQLite uses RANDOM(), PostgreSQL uses RANDOM())
        random_products = db.query(Product).filter(
            Product.article_id != article_id
        ).order_by(func.random()).limit(remaining * 2).all()
        
        for product in random_products:
            if product.article_id not in seen_ids:
                similar_products.append(product)
                seen_ids.add(product.article_id)
                if len(similar_products) >= 10:
                    break
        
        logger.debug(f"Final count: {len(similar_products)} similar products")
    
    # Limit to 10 products
    similar_products = similar_products[:10]
    
    logger.info(f"Retrieved {len(similar_products)} similar products for {article_id}")
    return [ProductOut.from_product(p) for p in similar_products]


# Test snippet
if __name__ == "__main__":
    """Test the products API with database queries."""
    import sys
    from pathlib import Path
    
    # Add parent directory to path for imports
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    from src.db import SessionLocal, init_db
    
    print("=" * 60)
    print("PRODUCTS API TEST")
    print("=" * 60)
    
    # Initialize database
    init_db()
    
    # Create session
    db = SessionLocal()
    
    try:
        # Count products
        product_count = db.query(Product).count()
        print(f"\nTotal products in database: {product_count}")
        
        if product_count > 0:
            # Get first product
            first_product = db.query(Product).first()
            print(f"\nFirst product:")
            print(f"  Article ID: {first_product.article_id}")
            print(f"  Name: {first_product.name}")
            print(f"  Price: ${first_product.price:.2f}")
            print(f"  Department: {first_product.department_no}")
            print(f"  Group: {first_product.product_group_name}")
            
            # Test similar products query
            print(f"\nTesting similar products for: {first_product.article_id}")
            
            similar = []
            seen_ids = {first_product.article_id}
            
            # Same department
            if first_product.department_no:
                dept_products = db.query(Product).filter(
                    Product.department_no == first_product.department_no,
                    Product.article_id != first_product.article_id
                ).limit(5).all()
                similar.extend(dept_products)
                print(f"  Found {len(dept_products)} from same department")
            
            # Same group
            if len(similar) < 10 and first_product.product_group_name:
                group_products = db.query(Product).filter(
                    Product.product_group_name == first_product.product_group_name,
                    Product.article_id != first_product.article_id
                ).limit(5).all()
                
                for p in group_products:
                    if p.article_id not in seen_ids:
                        similar.append(p)
                        seen_ids.add(p.article_id)
                
                print(f"  Total similar products: {len(similar)}")
            
            if similar:
                print(f"\nSample similar product:")
                print(f"  Article ID: {similar[0].article_id}")
                print(f"  Name: {similar[0].name}")
                print(f"  Price: ${similar[0].price:.2f}")
        else:
            print("\n⚠ No products in database")
            print("Add products using the database module or import from dataset")
        
        print("\n" + "=" * 60)
        print("✓ PRODUCTS API TEST COMPLETE")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
