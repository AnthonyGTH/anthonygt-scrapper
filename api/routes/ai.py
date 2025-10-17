from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Deal, Product, Price
from main import get_db
from datetime import datetime
from pydantic import BaseModel
from typing import Optional
import openai
import os
import json

router = APIRouter()

class AIAnalysisRequest(BaseModel):
    deal_id: int
    force_analysis: bool = False

class AIAnalysisResponse(BaseModel):
    deal_id: int
    confidence_score: float
    reasoning: str
    telegram_message: str
    analysis_timestamp: str

@router.post("/ai/analyze-deal", response_model=AIAnalysisResponse)
async def analyze_deal(
    request: AIAnalysisRequest,
    db: Session = Depends(get_db)
):
    """Trigger AI analysis for a specific deal"""
    try:
        # Get deal
        deal = db.query(Deal).filter(Deal.id == request.deal_id).first()
        if not deal:
            raise HTTPException(status_code=404, detail="Deal not found")
        
        # Get product and price history
        product = deal.product
        price_history = db.query(Price).filter(
            Price.product_id == product.id
        ).order_by(Price.scraped_at.desc()).limit(10).all()
        
        # Prepare data for AI analysis
        analysis_data = {
            "product_name": product.name,
            "site": product.site,
            "category": product.category,
            "current_price": deal.current_price,
            "original_price": deal.original_price,
            "discount_percentage": deal.discount_percentage,
            "price_history": [
                {
                    "price": price.price,
                    "date": price.scraped_at.isoformat(),
                    "availability": price.availability
                }
                for price in price_history
            ]
        }
        
        # Call OpenAI API
        openai.api_key = os.getenv("OPENAI_API_KEY")
        
        prompt = f"""
        Analiza esta oferta de producto y determina si es una buena oportunidad de compra.
        
        Producto: {analysis_data['product_name']}
        Sitio: {analysis_data['site']}
        Categoría: {analysis_data['category']}
        Precio actual: ${analysis_data['current_price']}
        Precio original: ${analysis_data['original_price']}
        Descuento: {analysis_data['discount_percentage']}%
        
        Historial de precios:
        {json.dumps(analysis_data['price_history'], indent=2)}
        
        Responde en formato JSON con:
        - confidence_score: número entre 0 y 1
        - reasoning: explicación en español neutro
        - telegram_message: mensaje para Telegram (máximo 200 caracteres)
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Eres un analista de precios experto. Responde solo en JSON válido."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=500
        )
        
        # Parse AI response
        ai_response = json.loads(response.choices[0].message.content)
        
        # Update deal with new analysis
        deal.confidence_score = ai_response["confidence_score"]
        deal.ai_reasoning = ai_response["reasoning"]
        db.commit()
        
        return AIAnalysisResponse(
            deal_id=deal.id,
            confidence_score=ai_response["confidence_score"],
            reasoning=ai_response["reasoning"],
            telegram_message=ai_response["telegram_message"],
            analysis_timestamp=datetime.utcnow().isoformat()
        )
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid AI response format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
