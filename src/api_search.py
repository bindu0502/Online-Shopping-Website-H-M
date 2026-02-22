"""
Intelligent Search API Router with Gemini AI
"""

import os
import logging
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, and_
from sqlalchemy.orm import Session
import google.generativeai as genai

from src.db import get_db, Product


# --------------------------------------------------
# Logging
# --------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# --------------------------------------------------
# Gemini Configuration
# --------------------------------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    logger.info("Gemini API configured successfully")
else:
    logger.warning("GEMINI_API_KEY not found - AI search disabled")


# --------------------------------------------------
# Router
# --------------------------------------------------
router = APIRouter(prefix="/search", tags=["search"])


# --------------------------------------------------
# Gemini Response Parser
# --------------------------------------------------
def parse_gemini_response(gemini_text: str) -> Dict[str, Any]:
    """
    Parse Gemini response text into structured search parameters.
    """

    params: Dict[str, Any] = {
        "keywords": [],
        "price_min": None,
        "price_max": None,
        "category": None,
        "colors": [],
    }

    if not gemini_text:
        return params

    lines = gemini_text.strip().split("\n")

    for raw_line in lines:
        line = raw_line.strip()

        if line.startswith("KEYWORDS:"):
            keywords_str = line.replace("KEYWORDS:", "").strip()
            params["keywords"] = [
                k.strip().lower()
                for k in keywords_str.split(",")
                if k.strip()
            ]

        elif line.startswith("PRICE_MIN:"):
            value = line.replace("PRICE_MIN:", "").strip()
            if value:
                try:
                    params["price_min"] = float(value)
                except ValueError:
                    logger.warning("Invalid PRICE_MIN value from Gemini")

        elif line.startswith("PRICE_MAX:"):
            value = line.replace("PRICE_MAX:", "").strip()
            if value:
                try:
                    params["price_max"] = float(value)
                except ValueError:
                    logger.warning("Invalid PRICE_MAX value from Gemini")

        elif line.startswith("CATEGORY:"):
            category = line.replace("CATEGORY:", "").strip()
            if category:
                params["category"] = category.lower()

        elif line.startswith("COLORS:"):
            colors_str = line.replace("COLORS:", "").strip()
            params["colors"] = [
                c.strip().lower()
                for c in colors_str.split(",")
                if c.strip()
            ]

    return params


# --------------------------------------------------
# Gemini AI Search
# --------------------------------------------------
def search_with_gemini(query: str) -> Optional[Dict[str, Any]]:
    """
    Use Gemini AI to interpret a natural language query.
    """

    if not GEMINI_API_KEY:
        return None

    try:
        model = genai.GenerativeModel("gemini-1.5-flash-latest")

        prompt = f"""
You are an e-commerce product search assistant.

Extract and respond ONLY in this format:

KEYWORDS:
PRICE_MIN:
PRICE_MAX:
CATEGORY:
COLORS:

Query: "{query}"
"""

        response = model.generate_content(prompt)

        gemini_text = response.text if response else ""

        logger.info("Gemini response received")

        return parse_gemini_response(gemini_text)

    except Exception as exc:
        logger.error("Gemini API error: %s", exc)
        return None


# --------------------------------------------------
# Basic Keyword Search
# --------------------------------------------------
def basic_search(query: str, db: Session, limit: int = 50) -> List[Product]:
    """
    Perform simple keyword search.
    """

    search_term = f"%{query.lower()}%"

    return (
        db.query(Product)
        .filter(
            or_(
                Product.name.ilike(search_term),
                Product.product_group_name.ilike(search_term),
                Product.colors.ilike(search_term),
                Product.primary_color.ilike(search_term),
            )
        )
        .limit(limit)
        .all()
    )


# --------------------------------------------------
# AI Structured Search
# --------------------------------------------------
def ai_search(
    params: Dict[str, Any],
    db: Session,
    limit: int = 50
) -> List[Product]:
    """
    Apply structured filters extracted by Gemini.
    """

    query_builder = db.query(Product)

    # Price filters
    if params.get("price_min") is not None:
        query_builder = query_builder.filter(
            Product.price >= params["price_min"]
        )

    if params.get("price_max") is not None:
        query_builder = query_builder.filter(
            Product.price <= params["price_max"]
        )

    conditions = []

    # Color filters
    for color in params.get("colors", []):
        color_term = f"%{color}%"
        conditions.append(
            or_(
                Product.colors.ilike(color_term),
                Product.primary_color.ilike(color_term),
            )
        )

    # Keyword filters
    for keyword in params.get("keywords", []):
        keyword_term = f"%{keyword}%"
        conditions.append(
            or_(
                Product.name.ilike(keyword_term),
                Product.product_group_name.ilike(keyword_term),
            )
        )

    # Category filter
    if params.get("category"):
        category_term = f"%{params['category']}%"
        conditions.append(
            Product.product_group_name.ilike(category_term)
        )

    if conditions:
        query_builder = query_builder.filter(and_(*conditions))

    return query_builder.limit(limit).all()

# --------------------------------------------------
# Search Endpoint
# --------------------------------------------------
@router.get("/")
def search_products(
    q: str = Query(..., description="Search query"),
    limit: int = Query(50, ge=1, le=100),
    use_ai: bool = Query(True),
    db: Session = Depends(get_db),
):
    """
    Main search endpoint.
    """

    if not q.strip():
        raise HTTPException(
            status_code=400,
            detail="Search query cannot be empty",
        )

    products: List[Product] = []
    search_type = "basic"

    # Try AI search
    if use_ai:
        params = search_with_gemini(q)
        if params:
            products = ai_search(params, db, limit)
            search_type = "ai"

    # Fallback to basic search
    if not products:
        products = basic_search(q, db, limit)

    return {
        "query": q,
        "total": len(products),
        "search_type": search_type,
        "products": products,
    }
