"""
User Interactions API Router

FastAPI router for recording and querying user interactions.
Tracks user behavior (views, clicks, add-to-cart, purchases) for analytics and recommendations.

Usage:
    from fastapi import FastAPI
    from src.api_interactions import router as interactions_router
    
    app = FastAPI()
    app.include_router(interactions_router)
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.db import get_db, User, UserInteraction, Product
from src.api_auth import get_current_user


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Allowed event types
ALLOWED_EVENT_TYPES = {"view", "click", "add_to_cart", "purchase"}


# Pydantic schemas

class InteractionIn(BaseModel):
    """
    User interaction input schema.
    
    Attributes:
        article_id: Product article ID
        event_type: Type of interaction (view, click, add_to_cart, purchase)
        value: Optional numeric value (e.g., price or weight)
        timestamp: Optional timestamp (defaults to current time)
    """
    article_id: str
    event_type: str
    value: Optional[float] = 1.0
    timestamp: Optional[datetime] = None


class InteractionOut(BaseModel):
    """
    User interaction output schema.
    
    Attributes:
        id: Interaction ID
        user_id: User ID
        article_id: Product article ID
        event_type: Type of interaction
        value: Numeric value
        created_at: Timestamp
    """
    id: int
    user_id: int
    article_id: str
    event_type: str
    value: float
    created_at: datetime
    
    model_config = {"from_attributes": True}


# Create router
router = APIRouter(prefix="/interactions", tags=["interactions"])


# API endpoints

@router.post("/record", response_model=InteractionOut)
def record_interaction(
    interaction: InteractionIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Record a single user interaction.
    
    Tracks user behavior such as product views, clicks, add-to-cart, and purchases.
    Requires authentication.
    
    Args:
        interaction: Interaction data
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Created interaction
        
    Raises:
        HTTPException 400: If event_type is invalid
        HTTPException 404: If product not found
    """
    # Validate event type
    if interaction.event_type not in ALLOWED_EVENT_TYPES:
        logger.warning(f"Invalid event type: {interaction.event_type}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid event_type. Must be one of: {', '.join(ALLOWED_EVENT_TYPES)}"
        )
    
    # Validate product exists
    product = db.query(Product).filter(
        Product.article_id == interaction.article_id
    ).first()
    
    if not product:
        logger.warning(f"Product not found: {interaction.article_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Use provided timestamp or current time
    timestamp = interaction.timestamp if interaction.timestamp else datetime.utcnow()
    
    # Create interaction
    new_interaction = UserInteraction(
        user_id=current_user.id,
        article_id=interaction.article_id,
        event_type=interaction.event_type,
        value=interaction.value,
        created_at=timestamp
    )
    
    db.add(new_interaction)
    db.commit()
    db.refresh(new_interaction)
    
    logger.info(
        f"Interaction recorded: user={current_user.id}, "
        f"article={interaction.article_id}, event={interaction.event_type}"
    )
    
    return new_interaction


@router.post("/bulk")
def record_bulk_interactions(
    interactions: List[InteractionIn],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Record multiple user interactions in bulk.
    
    Efficiently inserts multiple interactions in a single transaction.
    Requires authentication.
    
    Args:
        interactions: List of interactions to record
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Count of inserted interactions
        
    Raises:
        HTTPException 400: If any event_type is invalid
        HTTPException 404: If any product not found
    """
    logger.info(f"Bulk insert: {len(interactions)} interactions for user {current_user.id}")
    
    try:
        # Validate all interactions first
        for interaction in interactions:
            if interaction.event_type not in ALLOWED_EVENT_TYPES:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid event_type: {interaction.event_type}"
                )
            
            # Check product exists
            product = db.query(Product).filter(
                Product.article_id == interaction.article_id
            ).first()
            
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product not found: {interaction.article_id}"
                )
        
        # Insert all interactions
        new_interactions = []
        for interaction in interactions:
            timestamp = interaction.timestamp if interaction.timestamp else datetime.utcnow()
            
            new_interaction = UserInteraction(
                user_id=current_user.id,
                article_id=interaction.article_id,
                event_type=interaction.event_type,
                value=interaction.value,
                created_at=timestamp
            )
            new_interactions.append(new_interaction)
        
        db.bulk_save_objects(new_interactions)
        db.commit()
        
        logger.info(f"Bulk insert completed: {len(new_interactions)} interactions")
        
        return {"inserted": len(new_interactions)}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Bulk insert error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error inserting interactions"
        )


@router.get("/user", response_model=List[InteractionOut])
def get_user_interactions(
    limit: int = Query(50, ge=1, le=1000, description="Maximum number of interactions to return"),
    since_hours: int = Query(168, ge=1, description="Hours to look back (default: 168 = 7 days)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get recent interactions for current user.
    
    Returns user's interaction history ordered by most recent first.
    Requires authentication.
    
    Args:
        limit: Maximum number of interactions to return
        since_hours: Hours to look back (default: 168 = 7 days)
        current_user: Authenticated user
        db: Database session
        
    Returns:
        List of user interactions
    """
    logger.info(f"Fetching interactions for user {current_user.id}: limit={limit}, since_hours={since_hours}")
    
    # Calculate cutoff time
    cutoff_time = datetime.utcnow() - timedelta(hours=since_hours)
    
    # Query interactions
    interactions = db.query(UserInteraction).filter(
        UserInteraction.user_id == current_user.id,
        UserInteraction.created_at >= cutoff_time
    ).order_by(UserInteraction.created_at.desc()).limit(limit).all()
    
    logger.info(f"Retrieved {len(interactions)} interactions")
    
    return interactions


@router.get("/item/{article_id}/top")
def get_item_top_interactions(
    article_id: str,
    last_days: int = Query(30, ge=1, le=365, description="Days to look back"),
    top_k: int = Query(10, ge=1, le=100, description="Number of top users to return"),
    db: Session = Depends(get_db)
):
    """
    Get top users who interacted with a specific item.
    
    Returns users who interacted most with the given article,
    useful for collaborative filtering and bought-together recommendations.
    Public endpoint (no authentication required).
    
    Args:
        article_id: Product article ID
        last_days: Days to look back (default: 30)
        top_k: Number of top users to return (default: 10)
        db: Database session
        
    Returns:
        List of top users with interaction counts
    """
    logger.info(f"Fetching top interactions for article {article_id}: last_days={last_days}, top_k={top_k}")
    
    # Calculate cutoff time
    cutoff_time = datetime.utcnow() - timedelta(days=last_days)
    
    # Aggregate interactions by user
    top_users = db.query(
        UserInteraction.user_id,
        func.count(UserInteraction.id).label('event_count'),
        func.max(UserInteraction.created_at).label('last_interaction')
    ).filter(
        UserInteraction.article_id == article_id,
        UserInteraction.created_at >= cutoff_time
    ).group_by(
        UserInteraction.user_id
    ).order_by(
        func.count(UserInteraction.id).desc()
    ).limit(top_k).all()
    
    # Format response
    result = [
        {
            "user_id": user_id,
            "event_count": event_count,
            "last_interaction": last_interaction.isoformat()
        }
        for user_id, event_count, last_interaction in top_users
    ]
    
    logger.info(f"Retrieved {len(result)} top users for article {article_id}")
    
    return result


@router.get("/popular")
def get_popular_items(
    last_days: int = Query(7, ge=1, le=365, description="Days to look back"),
    top_k: int = Query(20, ge=1, le=100, description="Number of top items to return"),
    event_type: Optional[str] = Query(None, description="Filter by event type (view, click, add_to_cart, purchase)"),
    db: Session = Depends(get_db)
):
    """
    Get most popular items based on interactions.
    
    Returns top items by interaction count, optionally filtered by event type.
    Useful for trending products and recommendations.
    Public endpoint (no authentication required).
    
    Args:
        last_days: Days to look back (default: 7)
        top_k: Number of top items to return (default: 20)
        event_type: Optional filter by event type
        db: Database session
        
    Returns:
        List of popular items with interaction counts
        
    Raises:
        HTTPException 400: If event_type is invalid
    """
    logger.info(f"Fetching popular items: last_days={last_days}, top_k={top_k}, event_type={event_type}")
    
    # Validate event type if provided
    if event_type and event_type not in ALLOWED_EVENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid event_type. Must be one of: {', '.join(ALLOWED_EVENT_TYPES)}"
        )
    
    # Calculate cutoff time
    cutoff_time = datetime.utcnow() - timedelta(days=last_days)
    
    # Build query
    query = db.query(
        UserInteraction.article_id,
        func.count(UserInteraction.id).label('interaction_count'),
        func.count(func.distinct(UserInteraction.user_id)).label('unique_users')
    ).filter(
        UserInteraction.created_at >= cutoff_time
    )
    
    # Apply event type filter if provided
    if event_type:
        query = query.filter(UserInteraction.event_type == event_type)
    
    # Group and order
    popular_items = query.group_by(
        UserInteraction.article_id
    ).order_by(
        func.count(UserInteraction.id).desc()
    ).limit(top_k).all()
    
    # Format response
    result = [
        {
            "article_id": article_id,
            "interaction_count": interaction_count,
            "unique_users": unique_users
        }
        for article_id, interaction_count, unique_users in popular_items
    ]
    
    logger.info(f"Retrieved {len(result)} popular items")
    
    return result


# Test snippet
if __name__ == "__main__":
    """Simple manual test of interactions functionality."""
    import sys
    from pathlib import Path
    
    # Add parent directory to path for imports
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    from src.db import SessionLocal, init_db
    
    print("=" * 60)
    print("INTERACTIONS API TEST")
    print("=" * 60)
    
    # Initialize database
    init_db()
    
    # Create session
    db = SessionLocal()
    
    try:
        # Count interactions
        interaction_count = db.query(UserInteraction).count()
        print(f"\nTotal interactions in database: {interaction_count}")
        
        if interaction_count > 0:
            # Get last 3 interactions
            recent_interactions = db.query(UserInteraction).order_by(
                UserInteraction.created_at.desc()
            ).limit(3).all()
            
            print(f"\nLast 3 interactions:")
            for i, interaction in enumerate(recent_interactions, 1):
                print(f"  {i}. User {interaction.user_id} - {interaction.event_type}")
                print(f"     Article: {interaction.article_id}")
                print(f"     Value: {interaction.value}")
                print(f"     Time: {interaction.created_at}")
            
            # Get event type distribution
            print(f"\nEvent type distribution:")
            event_counts = db.query(
                UserInteraction.event_type,
                func.count(UserInteraction.id).label('count')
            ).group_by(UserInteraction.event_type).all()
            
            for event_type, count in event_counts:
                print(f"  {event_type}: {count}")
        else:
            print("\n⚠ No interactions in database")
            print("Interactions will be created when users interact with products")
        
        print("\n" + "=" * 60)
        print("✓ INTERACTIONS API TEST COMPLETE")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
