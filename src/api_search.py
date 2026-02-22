"""
Intelligent Search API Router with Gemini AI

Uses Google Gemini API to understand natural language queries
and search products intelligently.

Usage:
    from src.api_search import router as search_router
    app.include_router(search_router)
"""

import os
import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import or_, and_, and_
from sqlalchemy.orm import Session
import google.generativeai as genai

from src.db import get_db, Product


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    logger.info("Gemini API configured successfully")
else:
    logger.warning("GEMINI_API_KEY not found - AI search will be disabled")


# Color descriptions for different color variants
COLOR_DESCRIPTIONS = {
    'white': "Classic white with a clean, minimal look perfect for any occasion",
    'black': "Deep black suitable for both casual and formal wear",
    'gray': "Versatile gray that pairs well with any outfit",
    'grey': "Versatile grey that pairs well with any outfit", 
    'red': "Bold red that makes a statement and adds vibrant energy",
    'blue': "Classic blue offering timeless style and versatility",
    'navy': "Sophisticated navy blue perfect for professional and casual settings",
    'green': "Fresh green that brings natural vibrancy to your wardrobe",
    'yellow': "Bright yellow that adds sunshine and positivity to any look",
    'orange': "Energetic orange that creates a warm and confident appearance",
    'purple': "Rich purple that adds elegance and creativity to your style",
    'pink': "Soft pink that brings feminine charm and playful sophistication",
    'brown': "Warm brown offering earthy tones and natural comfort",
    'beige': "Neutral beige that provides subtle elegance and versatility",
    'tan': "Warm tan that offers casual sophistication and natural appeal",
    'burgundy': "Deep burgundy that exudes luxury and refined elegance",
    'maroon': "Rich maroon that combines sophistication with bold character",
    'teal': "Vibrant teal that brings modern freshness and unique style",
    'lime': "Bright lime that adds energetic pop and contemporary flair",
    'olive': "Sophisticated olive that offers military-inspired versatility",
    'gold': "Luxurious gold that adds glamour and premium appeal",
    'silver': "Sleek silver that provides modern metallic sophistication",
    'bronze': "Warm bronze that combines elegance with earthy richness"
}


def get_color_description(color: str) -> str:
    """Get description for a specific color."""
    return COLOR_DESCRIPTIONS.get(color.lower(), f"Beautiful {color} that adds style to your wardrobe")

# Pydantic schemas

class ProductOut(BaseModel):
    """Product response schema with guaranteed color information."""
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
        
        # If we have a matched color, use its specific description
        if matched_color:
            color_description = get_color_description(matched_color)
        
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


class SearchResponse(BaseModel):
    """Search response with results and metadata."""
    query: str
    interpreted_query: Optional[str] = None
    products: List[ProductOut]
    total: int
    search_type: str  # "ai" or "basic"
    matched_color: Optional[str] = None  # Color that was searched for


# Create router
router = APIRouter(prefix="/search", tags=["search"])


def find_matched_color(product_colors: str, search_colors: List[str]) -> Optional[str]:
    """
    Find which color from the search query matches the product colors.
    
    Args:
        product_colors: Comma-separated string of product colors
        search_colors: List of colors from search query
        
    Returns:
        The matched color name or None
    """
    if not product_colors or not search_colors:
        return None
    
    product_color_list = [c.strip().lower() for c in product_colors.split(',')]
    
    # Find the first search color that matches any product color
    for search_color in search_colors:
        search_color_lower = search_color.lower()
        for product_color in product_color_list:
            if search_color_lower in product_color or product_color in search_color_lower:
                return search_color.capitalize()
    
    return None


def enhance_products_with_color_info(products: List[Product], search_colors: List[str]) -> List[ProductOut]:
    """
    Enhance products with matched color information.
    
    Args:
        products: List of Product objects from database
        search_colors: List of colors from search query
        
    Returns:
        List of ProductOut objects with complete color information
    """
    enhanced_products = []
    
    for product in products:
        # Find matched color
        matched_color = None
        if search_colors and product.colors:
            matched_color = find_matched_color(product.colors, search_colors)
        
        # Convert to ProductOut with guaranteed color information
        product_out = ProductOut.from_product(product, matched_color)
        enhanced_products.append(product_out)
    
    return enhanced_products
    """
    Parse Gemini's response to extract search parameters.
    
    Expected format from Gemini:
    KEYWORDS: red dress, evening wear
    PRICE_MIN: 50
    PRICE_MAX: 150
    CATEGORY: dresses
    COLORS: red, black
    """
    params = {
        "keywords": [],
        "price_min": None,
        "price_max": None,
        "category": None,
        "colors": []
    }
    
    lines = gemini_text.strip().split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith("KEYWORDS:"):
            keywords_str = line.replace("KEYWORDS:", "").strip()
            params["keywords"] = [k.strip().lower() for k in keywords_str.split(',') if k.strip()]
        elif line.startswith("PRICE_MIN:"):
            try:
                params["price_min"] = float(line.replace("PRICE_MIN:", "").strip())
            except:
                pass
        elif line.startswith("PRICE_MAX:"):
            try:
                params["price_max"] = float(line.replace("PRICE_MAX:", "").strip())
            except:
                pass
        elif line.startswith("CATEGORY:"):
            params["category"] = line.replace("CATEGORY:", "").strip().lower()
        elif line.startswith("COLORS:"):
            colors_str = line.replace("COLORS:", "").strip()
            params["colors"] = [c.strip().lower() for c in colors_str.split(',') if c.strip()]
    
    return params


def search_with_gemini(query: str, db: Session) -> dict:
    """
    Use Gemini AI to understand the query and search products.
    
    Args:
        query: Natural language search query
        db: Database session
        
    Returns:
        Dictionary with search parameters extracted by Gemini
    """
    if not GEMINI_API_KEY:
        logger.warning("Gemini API key not configured, falling back to basic search")
        return None
    
    try:
        # Create the model (using free tier model - updated for v1 API)
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        
        # Create prompt for Gemini
        prompt = f"""You are a product search assistant for an e-commerce fashion store. 
Analyze this search query and extract relevant search parameters.

Search Query: "{query}"

Extract the following information and respond ONLY in this exact format:
KEYWORDS: [comma-separated relevant keywords for product names]
PRICE_MIN: [minimum price if mentioned, or leave blank]
PRICE_MAX: [maximum price if mentioned, or leave blank]
CATEGORY: [product category/type if mentioned, or leave blank]
COLORS: [comma-separated color names if mentioned, or leave blank]

Examples:
Query: "red dress under $50"
KEYWORDS: dress
PRICE_MIN: 
PRICE_MAX: 50
CATEGORY: dress
COLORS: red

Query: "blue jeans"
KEYWORDS: jeans
PRICE_MIN: 
PRICE_MAX: 
CATEGORY: jeans
COLORS: blue

Query: "black leather jacket over $100"
KEYWORDS: leather, jacket
PRICE_MIN: 100
PRICE_MAX: 
CATEGORY: jacket
COLORS: black

Now analyze: "{query}"
"""
        
        # Generate response
        response = model.generate_content(prompt)
        gemini_text = response.text
        
        logger.info(f"Gemini response: {gemini_text}")
        
        # Parse the response
        params = parse_gemini_response(gemini_text)
        
        return params
        
    except Exception as e:
        logger.error(f"Error calling Gemini API: {e}")
        return None


def basic_search(query: str, db: Session, limit: int = 50) -> List[Product]:
    """
    Basic keyword search without AI.
    
    Searches in product name, product_group_name, and colors.
    Prioritizes color matches for color-related queries.
    """
    search_term = f"%{query.lower()}%"
    
    # Check if query contains common color words
    color_words = ['red', 'blue', 'green', 'yellow', 'orange', 'purple', 'pink', 'black', 'white', 'gray', 'grey', 'brown', 'navy', 'maroon', 'burgundy', 'teal', 'lime', 'olive', 'gold', 'silver', 'bronze']
    query_lower = query.lower()
    query_words = query_lower.split()
    
    # Find color words in the query
    found_colors = [word for word in query_words if word in color_words]
    # Find non-color words (like "dress", "shirt", etc.)
    non_color_words = [word for word in query_words if word not in color_words]
    
    if found_colors and non_color_words:
        # Multi-word query with colors (e.g., "red dress")
        color_conditions = []
        for color in found_colors:
            color_term = f"%{color}%"
            color_conditions.append(
                or_(
                    Product.colors.ilike(color_term),
                    Product.primary_color.ilike(color_term)
                )
            )
        
        keyword_conditions = []
        for word in non_color_words:
            word_term = f"%{word}%"
            keyword_conditions.append(
                or_(
                    Product.name.ilike(word_term),
                    Product.product_group_name.ilike(word_term)
                )
            )
        
        # Combine color AND keyword conditions
        if color_conditions and keyword_conditions:
            products = db.query(Product).filter(
                and_(
                    or_(*color_conditions),
                    or_(*keyword_conditions)
                )
            ).limit(limit).all()
            
            if products:
                return products
    
    elif found_colors:
        # Single color query (e.g., "red")
        color_conditions = []
        for color in found_colors:
            color_term = f"%{color}%"
            color_conditions.append(
                or_(
                    Product.colors.ilike(color_term),
                    Product.primary_color.ilike(color_term)
                )
            )
        
        products = db.query(Product).filter(or_(*color_conditions)).limit(limit).all()
        if products:
            return products
    
    # Fallback to general search
    products = db.query(Product).filter(
        or_(
            Product.name.ilike(search_term),
            Product.product_group_name.ilike(search_term),
            Product.colors.ilike(search_term),
            Product.primary_color.ilike(search_term)
        )
    ).limit(limit).all()
    
    return products


def ai_search(params: dict, db: Session, limit: int = 50) -> List[Product]:
    """
    AI-powered search using Gemini-extracted parameters.
    
    Args:
        params: Dictionary with keywords, price_min, price_max, category, colors
        db: Database session
        limit: Maximum number of results
        
    Returns:
        List of matching products
    """
    query = db.query(Product)
    conditions = []
    
    # Apply price filters
    if params.get("price_min") is not None:
        query = query.filter(Product.price >= params["price_min"])
    if params.get("price_max") is not None:
        query = query.filter(Product.price <= params["price_max"])
    
    # Apply color filters (high priority)
    colors = params.get("colors", [])
    if colors:
        color_conditions = []
        for color in colors:
            color_term = f"%{color}%"
            color_conditions.append(
                or_(
                    Product.colors.ilike(color_term),
                    Product.primary_color.ilike(color_term)
                )
            )
        
        if color_conditions:
            conditions.append(or_(*color_conditions))
    
    # Apply keyword filters
    keywords = params.get("keywords", [])
    if keywords:
        keyword_conditions = []
        for keyword in keywords:
            search_term = f"%{keyword}%"
            keyword_conditions.append(
                or_(
                    Product.name.ilike(search_term),
                    Product.product_group_name.ilike(search_term)
                )
            )
        
        if keyword_conditions:
            conditions.append(or_(*keyword_conditions))
    
    # Apply category filter
    category = params.get("category")
    if category:
        category_term = f"%{category}%"
        conditions.append(Product.product_group_name.ilike(category_term))
    
    # Combine all conditions with AND
    if conditions:
        query = query.filter(and_(*conditions))
    
    products = query.limit(limit).all()
    
    return products


@router.get("/", response_model=SearchResponse)
def search_products(
    q: str = Query(..., description="Search query (natural language supported)"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of results"),
    use_ai: bool = Query(True, description="Use AI-powered search (Gemini)"),
    db: Session = Depends(get_db)
):
    """
    Search products using natural language queries.
    
    Supports both AI-powered search (using Gemini) and basic keyword search.
    
    Examples:
        - "red dress under $50"
        - "affordable shoes"
        - "luxury handbag"
        - "black jacket for winter"
        - "casual t-shirt under $30"
    
    Args:
        q: Search query
        limit: Maximum number of results
        use_ai: Whether to use AI-powered search
        db: Database session
        
    Returns:
        SearchResponse with matching products
    """
    logger.info(f"Search query: '{q}' (AI: {use_ai})")
    
    if not q or not q.strip():
        raise HTTPException(status_code=400, detail="Search query cannot be empty")
    
    products = []
    search_type = "basic"
    interpreted_query = None
    search_colors = []
    matched_color = None
    
    # Extract colors from query for basic search
    color_words = ['red', 'blue', 'green', 'yellow', 'orange', 'purple', 'pink', 'black', 'white', 'gray', 'grey', 'brown', 'navy', 'maroon', 'burgundy', 'teal', 'lime', 'olive', 'gold', 'silver', 'bronze']
    query_lower = q.lower()
    query_words = query_lower.split()
    basic_search_colors = [word for word in query_words if word in color_words]
    
    # Try AI search first if enabled
    if use_ai and GEMINI_API_KEY:
        try:
            params = search_with_gemini(q, db)
            
            if params:
                logger.info(f"Gemini extracted params: {params}")
                products = ai_search(params, db, limit)
                search_type = "ai"
                search_colors = params.get("colors", [])
                
                # Create interpreted query description
                parts = []
                if params.get("keywords"):
                    parts.append(f"Keywords: {', '.join(params['keywords'])}")
                if params.get("colors"):
                    parts.append(f"Colors: {', '.join(params['colors'])}")
                    matched_color = params['colors'][0] if params['colors'] else None
                if params.get("price_min"):
                    parts.append(f"Min price: ${params['price_min']}")
                if params.get("price_max"):
                    parts.append(f"Max price: ${params['price_max']}")
                if params.get("category"):
                    parts.append(f"Category: {params['category']}")
                
                interpreted_query = " | ".join(parts) if parts else None
        except Exception as e:
            logger.error(f"AI search failed: {e}")
    
    # Fallback to basic search if AI search didn't work or wasn't used
    if not products:
        logger.info("Using basic keyword search")
        products = basic_search(q, db, limit)
        search_type = "basic"
        search_colors = basic_search_colors
        matched_color = basic_search_colors[0] if basic_search_colors else None
    
    # Enhance products with color information
    enhanced_products = enhance_products_with_color_info(products, search_colors)
    
    logger.info(f"Found {len(enhanced_products)} products (search_type: {search_type})")
    
    return SearchResponse(
        query=q,
        interpreted_query=interpreted_query,
        products=enhanced_products,
        total=len(enhanced_products),
        search_type=search_type,
        matched_color=matched_color
    )


@router.get("/suggestions")
def get_search_suggestions(
    q: str = Query(..., min_length=2, description="Partial search query"),
    limit: int = Query(5, ge=1, le=10, description="Number of suggestions"),
    db: Session = Depends(get_db)
):
    """
    Get search suggestions based on partial query.
    
    Returns product names and categories that match the partial query.
    
    Args:
        q: Partial search query (minimum 2 characters)
        limit: Maximum number of suggestions
        db: Database session
        
    Returns:
        List of search suggestions
    """
    search_term = f"%{q.lower()}%"
    
    # Get unique product names
    products = db.query(Product.name).filter(
        Product.name.ilike(search_term)
    ).distinct().limit(limit).all()
    
    suggestions = [p.name for p in products]
    
    return {"suggestions": suggestions}


# Test snippet
if __name__ == "__main__":
    """Test the search API."""
    import sys
    from pathlib import Path
    
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    from src.db import SessionLocal, init_db
    
    print("=" * 60)
    print("INTELLIGENT SEARCH API TEST")
    print("=" * 60)
    
    init_db()
    db = SessionLocal()
    
    try:
        # Test queries
        test_queries = [
            "red dress",
            "shoes under $50",
            "luxury handbag",
            "casual t-shirt"
        ]
        
        for query in test_queries:
            print(f"\nQuery: '{query}'")
            
            # Try AI search
            if GEMINI_API_KEY:
                params = search_with_gemini(query, db)
                print(f"  AI params: {params}")
                
                if params:
                    results = ai_search(params, db, limit=5)
                    print(f"  AI results: {len(results)} products")
            else:
                print("  AI search disabled (no API key)")
            
            # Basic search
            results = basic_search(query, db, limit=5)
            print(f"  Basic results: {len(results)} products")
            
            if results:
                print(f"  Sample: {results[0].name} - ${results[0].price}")
        
        print("\n" + "=" * 60)
        print("✓ SEARCH API TEST COMPLETE")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
