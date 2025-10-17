"""
AI-powered price analysis using OpenAI GPT-4o-mini.
"""

import os
import json
import openai
from typing import List, Dict, Any
from datetime import datetime
import logging

class AIAnalyzer:
    """AI analyzer for price anomaly detection"""
    
    def __init__(self):
        self.logger = logging.getLogger("ai.analyzer")
        openai.api_key = os.getenv("OPENAI_API_KEY")
        
    async def analyze_deals(self, scraped_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze scraped data and identify potential deals"""
        if not scraped_data:
            return []
        
        self.logger.info(f"Analyzing {len(scraped_data)} products with AI...")
        
        analyzed_deals = []
        
        for product in scraped_data:
            try:
                analysis = await self._analyze_single_product(product)
                if analysis and analysis.get("confidence_score", 0) > 0.7:
                    analyzed_deals.append(analysis)
                    
            except Exception as e:
                self.logger.error(f"Error analyzing product {product.get('name', 'Unknown')}: {e}")
                continue
        
        return analyzed_deals
    
    async def _analyze_single_product(self, product: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Analyze a single product for deal potential"""
        try:
            prompt = self._build_analysis_prompt(product)
            
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Eres un analista de precios experto. Responde solo en JSON válido."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=500
            )
            
            ai_response = json.loads(response.choices[0].message.content)
            
            return {
                "product": product,
                "confidence_score": ai_response.get("confidence_score", 0),
                "reasoning": ai_response.get("reasoning", ""),
                "telegram_message": ai_response.get("telegram_message", ""),
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"AI analysis failed: {e}")
            return None
    
    def _build_analysis_prompt(self, product: Dict[str, Any]) -> str:
        """Build analysis prompt for AI"""
        return f"""
        Analiza esta oferta de producto y determina si es una buena oportunidad de compra.
        
        Producto: {product.get('name', 'N/A')}
        Sitio: {product.get('site', 'N/A')}
        Precio actual: ${product.get('price', 0)}
        Precio original: ${product.get('original_price', product.get('price', 0))}
        Descuento: {product.get('discount_percentage', 0)}%
        Disponibilidad: {product.get('availability', 'N/A')}
        
        Responde en formato JSON con:
        - confidence_score: número entre 0 y 1
        - reasoning: explicación en español neutro
        - telegram_message: mensaje para Telegram (máximo 200 caracteres)
        """
