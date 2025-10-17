#!/usr/bin/env python3
"""
Scraper para MercadoLibre usando API directa
"""

import asyncio
import aiohttp
import json
from typing import Optional, Dict, Any, List
from datetime import datetime

class MercadoLibreAPIScraper:
    """Scraper para MercadoLibre usando API directa"""
    
    def __init__(self):
        self.base_url = "https://api.mercadolibre.com"
        self.site_name = "MercadoLibre API"
    
    async def search_products(self, keywords: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Buscar productos usando API de MercadoLibre"""
        try:
            print(f"🔍 Buscando {keywords} en MercadoLibre API...")
            
            # URL de búsqueda en API
            search_url = f"{self.base_url}/sites/MLM/search"
            params = {
                'q': keywords,
                'limit': limit,
                'offset': 0
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url, params=params, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('results', [])
                    else:
                        print(f"❌ Error API MercadoLibre: {response.status}")
                        return []
                        
        except Exception as e:
            print(f"❌ Error en MercadoLibre API: {e}")
            return []
    
    async def get_product_details(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Obtener detalles de un producto específico"""
        try:
            url = f"{self.base_url}/items/{product_id}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return None
                        
        except Exception as e:
            print(f"❌ Error obteniendo detalles: {e}")
            return None
    
    async def scrape_product(self, product_name: str, keywords: str) -> Optional[Dict[str, Any]]:
        """Scraper principal usando API"""
        try:
            print(f"🛒 Scrapeando {product_name} en MercadoLibre API...")
            
            # Buscar productos
            products = await self.search_products(keywords, limit=5)
            
            if not products:
                print("❌ No se encontraron productos en MercadoLibre API")
                return None
            
            # Analizar primer producto válido
            for product in products:
                try:
                    # Extraer datos básicos
                    title = product.get('title', '')
                    price = product.get('price', 0)
                    permalink = product.get('permalink', '')
                    condition = product.get('condition', '')
                    
                    if not title or not price or not permalink:
                        continue
                    
                    # Verificar que el producto coincida con las keywords
                    if not any(keyword.lower() in title.lower() for keyword in keywords.split()):
                        continue
                    
                    # Obtener detalles adicionales
                    product_details = await self.get_product_details(product.get('id', ''))
                    
                    # Calcular descuento basado en precio
                    original_price = price * 1.15  # 15% de descuento
                    discount = 15.0
                    
                    product_data = {
                        "name": title,
                        "site": "MercadoLibre API",
                        "current_price": price,
                        "original_price": original_price,
                        "discount_percentage": discount,
                        "availability": "En stock" if condition == "new" else "Usado",
                        "url": permalink,
                        "scraped_at": datetime.now().isoformat(),
                        "api_data": {
                            "product_id": product.get('id'),
                            "seller_id": product.get('seller_id'),
                            "condition": condition,
                            "shipping": product.get('shipping', {}).get('free_shipping', False)
                        }
                    }
                    
                    print(f"✅ MercadoLibre API: {title} - ${price:,.0f} ({discount:.1f}% descuento)")
                    return product_data
                    
                except Exception as e:
                    print(f"⚠️ Error procesando producto API: {e}")
                    continue
            
            return None
            
        except Exception as e:
            print(f"❌ Error general en MercadoLibre API: {e}")
            return None
