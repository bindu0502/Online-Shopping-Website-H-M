"""
Personalized Recommendation Engine

Generates personalized "For You" recommendations based on user activity:
- Cart items
- Wishlist items
- Order history

Matching priority:
1. Same category + Same color + Similar name (HIGHEST)
2. Same category + Same color
3. Same category + Similar name
4. Same category only (FALLBACK)

For each unique product in user's activity, recommends 3 similar products.
Includes randomization to avoid showing same products every time.
"""

import logging
import random
from typing import List, Set, Dict, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.db import Product, CartItem, WishlistItem, Order, OrderItem

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_keywords(text: str) -> Set[str]:
    """
    Extract meaningful keywords from product name.
    
    Args:
        text: Product name
        
    Returns:
        Set of lowercase keywords
    """
    if not text:
        return set()
    
    # Common words to ignore
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
        'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
        'would', 'should', 'could', 'may', 'might', 'must', 'can', 'this',
        'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'
    }
    
    # Split and clean
    words = text.lower().replace('-', ' ').replace('/', ' ').split()
    keywords = {w for w in words if len(w) > 2 and w not in stop_words}
    
    return keywords


def calculate_name_similarity(name1: str, name2: str) -> float:
    """
    Calculate similarity between two product names based on keyword overlap.
    
    Args:
        name1: First product name
        name2: Second product name
        
    Returns:
        Similarity score (0-5.0)
    """
    if not name1 or not name2:
        return 0.0
    
    keywords1 = extract_keywords(name1)
    keywords2 = extract_keywords(name2)
    
    if not keywords1 or not keywords2:
        return 0.0
    
    # Calculate Jaccard similarity
    intersection = len(keywords1.intersection(keywords2))
    union = len(keywords1.union(keywords2))
    
    if union == 0:
        return 0.0
    
    jaccard = intersection / union
    
    # Scale to 0-5.0 range
    return jaccard * 5.0


def get_user_activity_products(user_id: int, db: Session) -> Set[str]:
    """
    Get all unique products from user's activity (cart, wishlist, orders).
    
    Args:
        user_id: User ID
        db: Database session
        
    Returns:
        Set of unique article IDs
    """
    activity_products = set()
    
    # Get cart items
    cart_items = db.query(CartItem.article_id).filter(
        CartItem.user_id == user_id
    ).all()
    activity_products.update([item.article_id for item in cart_items])
    
    # Get wishlist items
    wishlist_items = db.query(WishlistItem.article_id).filter(
        WishlistItem.user_id == user_id
    ).all()
    activity_products.update([item.article_id for item in wishlist_items])
    
    # Get order items
    order_ids = db.query(Order.id).filter(Order.user_id == user_id).all()
    order_ids = [o.id for o in order_ids]
    
    if order_ids:
        order_items = db.query(OrderItem.article_id).filter(
            OrderItem.order_id.in_(order_ids)
        ).all()
        activity_products.update([item.article_id for item in order_items])
    
    logger.info(f"User {user_id} has {len(activity_products)} unique activity products")
    return activity_products


def calculate_similarity_score(product1: Product, product2: Product) -> float:
    """
    Calculate similarity score between two products.
    
    Scoring criteria (with name similarity):
    - Name similarity: +5.0 (NEW - HIGHEST for similar products)
    - Same primary color: +4.0
    - Same category: +3.0
    - Color overlap: +2.0 per matching color
    - Similar price (within 20%): +1.5
    
    Priority matching:
    1. Same category + Same color + Similar name = 12.0+
    2. Same category + Same color = 7.0+
    3. Same category + Similar name = 8.0+
    4. Same category only = 3.0
    
    Args:
        product1: First product
        product2: Second product
        
    Returns:
        Similarity score (higher = more similar)
    """
    score = 0.0
    
    # Name similarity (HIGHEST PRIORITY for finding similar products)
    name_sim = calculate_name_similarity(product1.name, product2.name)
    score += name_sim
    
    # Same primary color (HIGH PRIORITY)
    if product1.primary_color and product2.primary_color:
        if product1.primary_color.lower() == product2.primary_color.lower():
            score += 4.0
    
    # Same category
    if product1.product_group_name and product2.product_group_name:
        if product1.product_group_name == product2.product_group_name:
            score += 3.0
    
    # Color overlap (increased weight)
    if product1.colors and product2.colors:
        colors1 = set(c.strip().lower() for c in product1.colors.split(','))
        colors2 = set(c.strip().lower() for c in product2.colors.split(','))
        overlap = len(colors1.intersection(colors2))
        score += overlap * 2.0
    
    # Similar price (within 20%)
    if product1.price and product2.price:
        price_diff = abs(product1.price - product2.price) / max(product1.price, product2.price)
        if price_diff <= 0.2:
            score += 1.5
    
    return score


def get_similar_products_optimized(
    source_product: Product,
    db: Session,
    exclude_ids: Set[str],
    top_n: int = 5
) -> List[Tuple[Product, float]]:
    """
    Find similar products using optimized database queries.
    
    Filters:
    - MUST have image_path (no products without images)
    - Same category (highest priority)
    - Same or similar colors (high priority)
    - Similar price range (50% to 150% of source price)
    
    Args:
        source_product: Product to find similar items for
        db: Database session
        exclude_ids: Set of article IDs to exclude
        top_n: Number of similar products to return
        
    Returns:
        List of (product, score) tuples
    """
    # Calculate price range
    min_price = source_product.price * 0.5 if source_product.price else 0
    max_price = source_product.price * 1.5 if source_product.price else 999999
    
    # Base query - MUST have image
    query = db.query(Product).filter(
        Product.article_id.notin_(exclude_ids),
        Product.image_path.isnot(None),
        Product.image_path != ''
    )
    
    # Add category filter if available (most important)
    if source_product.product_group_name:
        query = query.filter(
            Product.product_group_name == source_product.product_group_name
        )
    
    # Add color filter if available (high priority)
    if source_product.primary_color:
        query = query.filter(
            Product.primary_color == source_product.primary_color
        )
    
    # Add price filter
    query = query.filter(
        Product.price >= min_price,
        Product.price <= max_price
    )
    
    # Get candidates with same color first
    candidates = query.limit(50).all()
    
    # If not enough, relax color filter but keep category
    if len(candidates) < top_n and source_product.product_group_name:
        additional_query = db.query(Product).filter(
            Product.article_id.notin_(exclude_ids),
            Product.image_path.isnot(None),
            Product.image_path != '',
            Product.product_group_name == source_product.product_group_name,
            Product.price >= min_price,
            Product.price <= max_price
        ).limit(30)
        
        additional = additional_query.all()
        
        # Merge and deduplicate
        seen = {p.article_id for p in candidates}
        for p in additional:
            if p.article_id not in seen:
                candidates.append(p)
                seen.add(p.article_id)
                if len(candidates) >= 50:
                    break
    
    # Score the candidates
    scored_products = []
    for product in candidates:
        if product.article_id == source_product.article_id:
            continue
            
        score = calculate_similarity_score(source_product, product)
        scored_products.append((product, score))
    
    # Sort by score descending
    scored_products.sort(key=lambda x: x[1], reverse=True)
    
    # Return top N
    return scored_products[:top_n]


def get_category_based_recommendations(
    user_id: int,
    db: Session,
    limit: int = 20
) -> List[Dict]:
    """
    Get recommendations based on user's preferred categories (cold-start solution).
    
    Used when user has no activity (empty cart, wishlist, orders).
    
    Args:
        user_id: User ID
        db: Database session
        limit: Maximum number of recommendations
        
    Returns:
        List of recommendation dictionaries with product details
    """
    from src.db import User
    
    # Get user's preferred categories
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user or not user.preferred_categories:
        logger.info(f"User {user_id} has no preferred categories")
        return []
    
    # Parse categories (comma-separated)
    categories = [cat.strip() for cat in user.preferred_categories.split(',') if cat.strip()]
    
    if not categories:
        logger.info(f"User {user_id} has empty preferred categories")
        return []
    
    logger.info(f"User {user_id} preferred categories: {categories}")
    
    # Query products matching preferred categories
    products = db.query(Product).filter(
        Product.product_group_name.in_(categories),
        Product.image_path.isnot(None),
        Product.image_path != ''
    ).limit(limit * 2).all()  # Get more for randomization
    
    if not products:
        logger.info(f"No products found for categories: {categories}")
        return []
    
    # Shuffle for variety
    random.shuffle(products)
    
    # Take top N
    selected_products = products[:limit]
    
    # Format recommendations
    recommendations = []
    for product in selected_products:
        recommendations.append({
            'article_id': product.article_id,
            'name': product.name,
            'price': product.price,
            'image_path': product.image_path,
            'product_group_name': product.product_group_name,
            'primary_color': product.primary_color,
            'color_description': product.color_description,
            'colors': product.colors,
            'score': 5.0,  # Base score for category match
            'reason': f'Based on your interest in {product.product_group_name}'
        })
    
    logger.info(f"Generated {len(recommendations)} category-based recommendations for user {user_id}")
    
    return recommendations


def generate_personalized_recommendations(
    user_id: int,
    db: Session,
    recommendations_per_product: int = 3
) -> List[Dict]:
    """
    Generate personalized recommendations for a user with randomization.
    
    Logic:
    1. Get all unique products from user activity (cart, wishlist, orders)
    2. IF NO ACTIVITY: Use preferred categories (cold-start solution)
    3. For each unique product, find similar products based on:
       - Name similarity (e.g., "Slim Fit Jeans" → "Straight Fit Jeans")
       - Same color
       - Same category
    4. Exclude products already in user's activity
    5. Remove duplicate recommendations
    6. Add randomization to avoid showing same products every time
    
    Args:
        user_id: User ID
        db: Database session
        recommendations_per_product: Number of recommendations per activity product
        
    Returns:
        List of recommendation dictionaries with product details
    """
    logger.info(f"[COLD-START v2] Generating personalized recommendations for user {user_id}")
    
    # Step 1: Get user activity products
    activity_products = get_user_activity_products(user_id, db)
    
    # COLD-START SOLUTION: If no activity, use preferred categories
    if not activity_products:
        logger.info(f"[COLD-START v2] No activity found for user {user_id}, using category-based recommendations")
        return get_category_based_recommendations(user_id, db, limit=20)
    
    # Step 2: Get activity product objects
    activity_product_objects = db.query(Product).filter(
        Product.article_id.in_(activity_products)
    ).all()
    
    # Shuffle activity products for variety
    random.shuffle(activity_product_objects)
    
    logger.info(f"Finding recommendations for {len(activity_product_objects)} activity products")
    
    # Step 3: Generate recommendations for each activity product
    recommendations = []
    seen_article_ids = set()
    
    for source_product in activity_product_objects:
        # Use optimized query instead of loading all products
        similar_products = get_similar_products_optimized(
            source_product,
            db,
            activity_products | seen_article_ids,  # Exclude both activity and already recommended
            top_n=recommendations_per_product * 2  # Get more candidates for randomization
        )
        
        # Add randomization: shuffle similar products before selecting
        random.shuffle(similar_products)
        
        # Take top N after shuffling
        selected = similar_products[:recommendations_per_product]
        
        for product, score in selected:
            seen_article_ids.add(product.article_id)
            
            recommendations.append({
                'article_id': product.article_id,
                'name': product.name,
                'price': product.price,
                'image_path': product.image_path,
                'product_group_name': product.product_group_name,
                'primary_color': product.primary_color,
                'color_description': product.color_description,
                'colors': product.colors,
                'score': score,
                'source_article_id': source_product.article_id,
                'reason': f'Similar to {source_product.name[:30]}...'
            })
    
    # Final shuffle for variety
    random.shuffle(recommendations)
    
    logger.info(f"Generated {len(recommendations)} personalized recommendations for user {user_id}")
    
    return recommendations


# Test snippet
if __name__ == "__main__":
    """Test personalized recommendations."""
    import sys
    from pathlib import Path
    
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    from src.db import SessionLocal, init_db, User
    
    print("=" * 60)
    print("PERSONALIZED RECOMMENDATIONS TEST")
    print("=" * 60)
    
    init_db()
    db = SessionLocal()
    
    try:
        # Get first user with activity
        user = db.query(User).first()
        
        if user:
            print(f"\nTesting for user: {user.email}")
            
            # Get activity
            activity = get_user_activity_products(user.id, db)
            print(f"Activity products: {len(activity)}")
            
            # Generate recommendations
            recommendations = generate_personalized_recommendations(user.id, db)
            
            print(f"\nGenerated {len(recommendations)} recommendations")
            print(f"Expected: {len(activity) * 3} (3 per activity product)")
            
            if recommendations:
                print("\nTop 5 recommendations:")
                for i, rec in enumerate(recommendations[:5], 1):
                    print(f"{i}. {rec['name']}")
                    print(f"   Price: ${rec['price']:.2f}")
                    print(f"   Score: {rec['score']:.2f}")
                    print(f"   Reason: {rec['reason']}")
        else:
            print("No users found in database")
        
        print("\n" + "=" * 60)
        print("✓ TEST COMPLETE")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
