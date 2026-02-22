"""
For You API Router

FastAPI router for personalized "For You" recommendations.
Based on user activity (cart, wishlist, orders).
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.db import get_db, User
from src.api_auth import get_current_user
from src.personalized_recommend import generate_personalized_recommendations

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Pydantic schemas

class ForYouItemOut(BaseModel):
    """
    For You recommendation item response.
    
    Attributes:
        article_id: Product article ID
        name: Product name
        price: Product price
        image_path: Product image path
        product_group_name: Product category
        primary_color: Primary color
        color_description: Detailed color description
        colors: All colors (comma-separated)
        score: Similarity score
        reason: Recommendation reason
    """
    article_id: str
    name: str
    price: float
    image_path: Optional[str] = None
    product_group_name: Optional[str] = None
    primary_color: Optional[str] = None
    color_description: Optional[str] = None
    colors: Optional[str] = None
    score: float
    reason: str


class ForYouResponse(BaseModel):
    """
    For You recommendations response.
    
    Attributes:
        user_id: User ID
        recommendations: List of recommended products
        count: Number of recommendations
        activity_products_count: Number of unique products in user activity
    """
    user_id: int
    recommendations: List[ForYouItemOut]
    count: int
    activity_products_count: int


# Create router
router = APIRouter(prefix="/foryou", tags=["foryou"])


@router.get("/", response_model=ForYouResponse)
def get_for_you_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get personalized "For You" recommendations.
    
    Generates recommendations based on user's activity:
    - Products in cart
    - Products in wishlist
    - Products in order history
    
    For each unique product in activity, recommends 5 similar products.
    Total recommendations = N unique products × 5
    
    Requires authentication.
    
    Args:
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Personalized recommendations with product details
    """
    logger.info(f"For You request from user {current_user.id}")
    
    try:
        # Generate recommendations (5 per activity product for more variety)
        recommendations = generate_personalized_recommendations(
            current_user.id,
            db,
            recommendations_per_product=5
        )
        
        # Calculate activity count (unique products)
        from src.personalized_recommend import get_user_activity_products
        activity_products = get_user_activity_products(current_user.id, db)
        
        logger.info(f"Returning {len(recommendations)} recommendations for user {current_user.id}")
        
        return ForYouResponse(
            user_id=current_user.id,
            recommendations=[ForYouItemOut(**rec) for rec in recommendations],
            count=len(recommendations),
            activity_products_count=len(activity_products)
        )
        
    except Exception as e:
        logger.error(f"Error generating For You recommendations: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error generating recommendations"
        )


# Test snippet
if __name__ == "__main__":
    """Test For You API."""
    import sys
    from pathlib import Path
    
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    from src.db import SessionLocal, init_db, User
    
    print("=" * 60)
    print("FOR YOU API TEST")
    print("=" * 60)
    
    init_db()
    db = SessionLocal()
    
    try:
        user = db.query(User).first()
        
        if user:
            print(f"\nTesting for user: {user.email}")
            
            # Generate recommendations
            recommendations = generate_personalized_recommendations(user.id, db)
            
            print(f"\nGenerated {len(recommendations)} recommendations")
            
            if recommendations:
                print("\nSample recommendations:")
                for i, rec in enumerate(recommendations[:3], 1):
                    print(f"{i}. {rec['name']}")
                    print(f"   ${rec['price']:.2f}")
                    print(f"   {rec['reason']}")
        else:
            print("No users found")
        
        print("\n" + "=" * 60)
        print("✓ TEST COMPLETE")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
