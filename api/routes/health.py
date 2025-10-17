from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api.models import Product, Price, Deal
from sqlalchemy import func
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """System health check endpoint"""
    try:
        # Check database connection
        db.execute("SELECT 1")
        
        # Get basic statistics
        total_products = db.query(Product).count()
        total_prices = db.query(Price).count()
        total_deals = db.query(Deal).count()
        
        # Get recent activity (last 24 hours)
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_prices = db.query(Price).filter(Price.scraped_at >= yesterday).count()
        recent_deals = db.query(Deal).filter(Deal.created_at >= yesterday).count()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "database": "connected",
            "statistics": {
                "total_products": total_products,
                "total_prices": total_prices,
                "total_deals": total_deals,
                "recent_prices_24h": recent_prices,
                "recent_deals_24h": recent_deals
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }
