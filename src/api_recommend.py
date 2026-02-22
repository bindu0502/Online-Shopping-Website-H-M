"""
Recommendations API Router

Production-ready FastAPI router serving ML-powered recommendations.
Combines retrieval, feature engineering, and LightGBM prediction.

Usage:
    from fastapi import FastAPI
    from src.api_recommend import router as recommend_router
    
    app = FastAPI()
    app.include_router(recommend_router)

Example cURL:
    # Get recommendations for authenticated user
    curl -X GET "http://localhost:8000/recommend/me?k=12" \
      -H "Authorization: Bearer <token>"
    
    # Get recommendations without model (retrieval only)
    curl -X GET "http://localhost:8000/recommend/me?k=12&use_model=false" \
      -H "Authorization: Bearer <token>"
"""

import logging
import os
import time
from datetime import datetime
from typing import List, Optional

import joblib
import numpy as np
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.db import get_db, Product, User, UserInteraction
from src.api_auth import get_current_user

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Model configuration
MODEL_PATH = os.getenv("RECSYS_MODEL_PATH", "Project149/models/lgbm_v1.pkl")
model = None
model_loaded_at = None

# Try to load model on import
try:
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
        model_loaded_at = datetime.now()
        logger.info(f"✓ Model loaded successfully from {MODEL_PATH}")
    else:
        logger.warning(f"⚠ Model file not found: {MODEL_PATH}")
        logger.warning("  Recommendations will use retrieval scores only")
except Exception as e:
    logger.error(f"✗ Error loading model: {e}")
    logger.warning("  Recommendations will use retrieval scores only")


# Pydantic schemas

class RecommendationItem(BaseModel):
    """
    Single recommendation item.
    
    Attributes:
        article_id: Product article ID
        score: Recommendation score (0-1)
        product_name: Product name
        price: Product price
        image_path: Product image path
        reason: Retrieval reason/source
    """
    article_id: str
    score: float
    product_name: str
    price: float
    image_path: Optional[str] = None
    reason: Optional[str] = None


class RecommendationsOut(BaseModel):
    """
    Recommendations response.
    
    Attributes:
        user_id: User ID
        recommendations: List of recommended items
        count: Number of recommendations
        model_used: Whether ML model was used
        generation_time_ms: Time taken to generate recommendations
    """
    user_id: int
    recommendations: List[RecommendationItem]
    count: int
    model_used: bool
    generation_time_ms: float


# Create router
router = APIRouter(prefix="/recommend", tags=["recommend"])


def generate_recommendations(
    user_id: str,
    db: Session,
    k: int = 12,
    use_model: bool = True,
    record_impression: bool = False
) -> List[dict]:
    """
    Generate recommendations for a user.
    
    Pipeline:
    1. Generate candidates using retrieval
    2. Build features for candidates
    3. Predict scores using LightGBM (if available)
    4. Rank and select top-K
    5. Enrich with product metadata
    6. Optionally record impressions
    
    Args:
        user_id: User ID (string format from dataset)
        db: Database session
        k: Number of recommendations to return
        use_model: Whether to use ML model for scoring
        record_impression: Whether to record impressions
        
    Returns:
        List of recommendation dictionaries
    """
    start_time = time.time()
    
    try:
        # Import here to avoid circular dependencies
        from src.retrieval import get_candidates_for_user, load_processed_data
        from src.features import build_features_for_candidates
        
        logger.info(f"Generating recommendations for user {user_id}")
        
        # Step 1: Load processed data
        try:
            transactions, customers, articles = load_processed_data("Project149/datasets/processed")
        except Exception as e:
            logger.error(f"Error loading processed data: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error loading recommendation data"
            )
        
        # Step 2: Generate candidates
        try:
            candidates_df = get_candidates_for_user(
                user_id,
                transactions,
                customers,
                articles,
                top_n=500,
                use_cache=True
            )
            
            if candidates_df.empty:
                logger.warning(f"No candidates generated for user {user_id}")
                return []
            
            logger.info(f"Generated {len(candidates_df)} candidates")
            
        except Exception as e:
            logger.error(f"Error generating candidates: {e}")
            # Return empty list instead of failing
            return []
        
        # Step 3: Build features
        try:
            features_df = build_features_for_candidates(
                user_id,
                candidates_df,
                transactions,
                customers,
                articles
            )
            
            if features_df.empty:
                logger.warning(f"No features built for user {user_id}")
                return []
            
            logger.info(f"Built features: {features_df.shape}")
            
        except Exception as e:
            logger.error(f"Error building features: {e}")
            # Fall back to using candidates without features
            features_df = candidates_df
        
        # Step 4: Score candidates
        if use_model and model is not None:
            try:
                # Prepare feature matrix
                exclude_cols = ['user_id', 'article_id', 'score', 'reason', 'rule_scores_json', 'label']
                feature_cols = [col for col in features_df.columns if col not in exclude_cols]
                
                # Prepare features for prediction
                X = features_df[feature_cols].copy()
                
                # Keep categorical columns as category type for LightGBM
                for col in X.columns:
                    if X[col].dtype == 'object':
                        X[col] = X[col].astype('category')
                
                # Fill missing values
                for col in X.columns:
                    if X[col].isna().any():
                        if X[col].dtype.name == 'category':
                            X[col] = X[col].fillna('unknown')
                        else:
                            X[col] = X[col].fillna(0)
                
                # Predict (LightGBM handles categorical features automatically)
                predictions = model.predict(X)
                
                features_df['ml_score'] = predictions
                features_df = features_df.sort_values('ml_score', ascending=False)
                
                logger.info(f"Model predictions: min={predictions.min():.4f}, max={predictions.max():.4f}, mean={predictions.mean():.4f}")
                model_used = True
                
            except Exception as e:
                logger.error(f"Error during prediction: {e}")
                logger.warning("Falling back to retrieval scores")
                # Fall back to retrieval scores
                features_df = features_df.sort_values('score', ascending=False)
                features_df['ml_score'] = features_df['score']
                model_used = False
        else:
            # Use retrieval scores
            features_df = features_df.sort_values('score', ascending=False)
            features_df['ml_score'] = features_df['score']
            model_used = False
        
        # Step 5: Select top-K
        top_k = features_df.head(k)
        
        # Step 6: Enrich with product metadata
        recommendations = []
        for _, row in top_k.iterrows():
            article_id = row['article_id']
            
            # Get product from database
            product = db.query(Product).filter(Product.article_id == article_id).first()
            
            if product:
                recommendations.append({
                    'article_id': article_id,
                    'score': float(row['ml_score']),
                    'product_name': product.name,
                    'price': product.price,
                    'image_path': product.image_path,
                    'reason': row.get('reason', 'unknown')
                })
        
        # Step 7: Record impressions (optional)
        if record_impression and recommendations:
            try:
                # Get numeric user_id from database
                user = db.query(User).filter(User.id == int(user_id)).first()
                if user:
                    for rec in recommendations:
                        interaction = UserInteraction(
                            user_id=user.id,
                            article_id=rec['article_id'],
                            event_type='impression',
                            value=rec['score'],
                            created_at=datetime.utcnow()
                        )
                        db.add(interaction)
                    db.commit()
                    logger.info(f"Recorded {len(recommendations)} impressions")
            except Exception as e:
                logger.warning(f"Error recording impressions: {e}")
                # Don't fail the request if impression recording fails
        
        elapsed_ms = (time.time() - start_time) * 1000
        logger.info(f"Generated {len(recommendations)} recommendations in {elapsed_ms:.2f}ms")
        
        return recommendations
        
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating recommendations: {str(e)}"
        )


@router.get("/me", response_model=RecommendationsOut)
def get_recommendations_for_me(
    k: int = Query(12, ge=1, le=100, description="Number of recommendations"),
    use_model: bool = Query(True, description="Use ML model for scoring"),
    record_impression: bool = Query(False, description="Record impressions in database"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get personalized recommendations for authenticated user.
    
    Uses the complete ML pipeline:
    1. Candidate generation (retrieval)
    2. Feature engineering
    3. LightGBM prediction
    4. Product metadata enrichment
    
    Requires authentication.
    
    Args:
        k: Number of recommendations (1-100)
        use_model: Whether to use ML model (falls back to retrieval scores)
        record_impression: Whether to record impressions
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Personalized recommendations with scores and metadata
    """
    start_time = time.time()
    
    logger.info(f"Recommendation request: user={current_user.id}, k={k}, use_model={use_model}")
    
    # Generate recommendations
    recommendations = generate_recommendations(
        str(current_user.id),
        db,
        k=k,
        use_model=use_model,
        record_impression=record_impression
    )
    
    elapsed_ms = (time.time() - start_time) * 1000
    
    return RecommendationsOut(
        user_id=current_user.id,
        recommendations=[RecommendationItem(**rec) for rec in recommendations],
        count=len(recommendations),
        model_used=use_model and model is not None,
        generation_time_ms=elapsed_ms
    )


@router.get("/user/{user_id}")
def get_recommendations_for_user(
    user_id: str,
    k: int = Query(12, ge=1, le=100),
    use_model: bool = Query(True),
    force_retrieval_only: bool = Query(False, description="Force retrieval-only mode"),
    db: Session = Depends(get_db)
):
    """
    Get recommendations for specific user (admin/debug endpoint).
    
    No authentication required for testing purposes.
    In production, add authentication and admin role check.
    
    Args:
        user_id: User ID (string format)
        k: Number of recommendations
        use_model: Whether to use ML model
        force_retrieval_only: Force retrieval-only mode
        db: Database session
        
    Returns:
        Recommendations for specified user
    """
    logger.info(f"Admin recommendation request: user={user_id}, k={k}")
    
    start_time = time.time()
    
    # Generate recommendations
    recommendations = generate_recommendations(
        user_id,
        db,
        k=k,
        use_model=use_model and not force_retrieval_only,
        record_impression=False
    )
    
    elapsed_ms = (time.time() - start_time) * 1000
    
    return {
        "user_id": user_id,
        "recommendations": recommendations,
        "count": len(recommendations),
        "model_used": use_model and not force_retrieval_only and model is not None,
        "generation_time_ms": elapsed_ms
    }


@router.get("/health")
def get_recommendation_health():
    """
    Get recommendation system health status.
    
    Returns model status, paths, and timestamps.
    Useful for monitoring and debugging.
    
    Returns:
        Health status information
    """
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "model_path": MODEL_PATH,
        "model_exists": os.path.exists(MODEL_PATH),
        "model_loaded_at": model_loaded_at.isoformat() if model_loaded_at else None,
        "fallback_mode": "retrieval_only" if model is None else "ml_powered"
    }


@router.post("/reload")
def reload_model(
    current_user: User = Depends(get_current_user)
):
    """
    Reload the ML model from disk.
    
    Useful for updating the model without restarting the server.
    Requires authentication (in production, add admin role check).
    
    Args:
        current_user: Authenticated user
        
    Returns:
        Reload status
    """
    global model, model_loaded_at
    
    logger.info(f"Model reload requested by user {current_user.id}")
    
    try:
        if os.path.exists(MODEL_PATH):
            model = joblib.load(MODEL_PATH)
            model_loaded_at = datetime.now()
            logger.info(f"✓ Model reloaded successfully from {MODEL_PATH}")
            
            return {
                "status": "success",
                "message": "Model reloaded successfully",
                "model_path": MODEL_PATH,
                "loaded_at": model_loaded_at.isoformat()
            }
        else:
            return {
                "status": "error",
                "message": f"Model file not found: {MODEL_PATH}"
            }
    except Exception as e:
        logger.error(f"Error reloading model: {e}")
        return {
            "status": "error",
            "message": f"Error reloading model: {str(e)}"
        }


# Test snippet
if __name__ == "__main__":
    """Smoke test for recommendation system."""
    import sys
    from pathlib import Path
    
    # Add parent directory to path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    from src.db import SessionLocal, init_db
    
    print("=" * 60)
    print("RECOMMENDATIONS API SMOKE TEST")
    print("=" * 60)
    
    # Initialize database
    init_db()
    db = SessionLocal()
    
    try:
        # Check model status
        print(f"\nModel Status:")
        print(f"  Path: {MODEL_PATH}")
        print(f"  Loaded: {model is not None}")
        print(f"  Exists: {os.path.exists(MODEL_PATH)}")
        
        if model is not None:
            print(f"  Type: {type(model).__name__}")
        
        # Try to get a test user
        print(f"\nLooking for test user...")
        
        # Try to load processed data
        try:
            from src.retrieval import load_processed_data
            transactions, customers, articles = load_processed_data("Project149/datasets/processed")
            
            # Get a random user with transactions
            active_users = transactions['customer_id'].unique()
            if len(active_users) > 0:
                test_user = str(active_users[0])
                print(f"  Test user: {test_user}")
                
                # Generate recommendations
                print(f"\nGenerating recommendations...")
                recommendations = generate_recommendations(
                    test_user,
                    db,
                    k=5,
                    use_model=True,
                    record_impression=False
                )
                
                print(f"\nTop 5 Recommendations:")
                for i, rec in enumerate(recommendations, 1):
                    print(f"  {i}. {rec['product_name']}")
                    print(f"     Score: {rec['score']:.4f}")
                    print(f"     Price: ${rec['price']:.2f}")
                    print(f"     Reason: {rec['reason']}")
            else:
                print("  No active users found in transactions")
                
        except Exception as e:
            print(f"  Error: {e}")
        
        print("\n" + "=" * 60)
        print("✓ SMOKE TEST COMPLETE")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
