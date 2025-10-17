from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from models import Deal, Product, Price
from main import get_db
from typing import List, Optional
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/deals")
async def get_deals(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    site: Optional[str] = Query(None),
    min_confidence: Optional[float] = Query(None, ge=0, le=1),
    days: int = Query(7, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get deals with optional filtering"""
    try:
        # Build query
        query = db.query(Deal).join(Product)
        
        # Apply filters
        if site:
            query = query.filter(Product.site == site)
        
        if min_confidence:
            query = query.filter(Deal.confidence_score >= min_confidence)
        
        # Date filter
        start_date = datetime.utcnow() - timedelta(days=days)
        query = query.filter(Deal.created_at >= start_date)
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        deals = query.order_by(desc(Deal.created_at)).offset(skip).limit(limit).all()
        
        # Format response
        result = []
        for deal in deals:
            result.append({
                "id": deal.id,
                "product_name": deal.product.name,
                "product_url": deal.product.url,
                "site": deal.product.site,
                "original_price": deal.original_price,
                "current_price": deal.current_price,
                "discount_percentage": deal.discount_percentage,
                "confidence_score": deal.confidence_score,
                "ai_reasoning": deal.ai_reasoning,
                "telegram_sent": deal.telegram_sent,
                "created_at": deal.created_at.isoformat()
            })
        
        return {
            "deals": result,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/deals/{deal_id}")
async def get_deal_detail(deal_id: int, db: Session = Depends(get_db)):
    """Get detailed information about a specific deal"""
    try:
        deal = db.query(Deal).filter(Deal.id == deal_id).first()
        if not deal:
            raise HTTPException(status_code=404, detail="Deal not found")
        
        # Get price history for the product
        price_history = db.query(Price).filter(
            Price.product_id == deal.product_id
        ).order_by(Price.scraped_at.desc()).limit(30).all()
        
        return {
            "deal": {
                "id": deal.id,
                "product_name": deal.product.name,
                "product_url": deal.product.url,
                "site": deal.product.site,
                "category": deal.product.category,
                "original_price": deal.original_price,
                "current_price": deal.current_price,
                "discount_percentage": deal.discount_percentage,
                "confidence_score": deal.confidence_score,
                "ai_reasoning": deal.ai_reasoning,
                "telegram_sent": deal.telegram_sent,
                "created_at": deal.created_at.isoformat()
            },
            "price_history": [
                {
                    "price": price.price,
                    "currency": price.currency,
                    "availability": price.availability,
                    "scraped_at": price.scraped_at.isoformat()
                }
                for price in price_history
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
