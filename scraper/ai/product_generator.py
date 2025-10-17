#!/usr/bin/env python3
"""
Generador de productos con IA OpenAI para productos fáciles de revender
"""

import openai
import json
import os
from typing import List, Dict, Any
from datetime import datetime
import requests

class ProductGenerator:
    """Generador inteligente de productos para scraping"""
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        openai.api_key = self.openai_api_key
        
    async def generate_resellable_products(self, count: int = 20) -> List[Dict[str, Any]]:
        """Generate easy-to-resell products using AI"""
        try:
            print(f"🤖 Generating {count} products with OpenAI AI...")
            
            prompt = f"""
            Eres un experto en productos electrónicos y de tecnología que son fáciles de revender en México.
            
            Genera exactamente {count} productos que cumplan estos criterios:
            
            1. **FÁCILES DE REVENDER**: Productos con alta demanda y liquidez
            2. **CATEGORÍAS**: Consolas, celulares, audífonos, cámaras, laptops, tablets, smartwatches
            3. **MARCAS POPULARES**: Apple, Samsung, Sony, Nintendo, Xbox, PlayStation, etc.
            4. **PRECIO RANGO**: $5,000 - $50,000 MXN (productos de valor medio-alto)
            5. **MERCADO MEXICANO**: Productos disponibles en tiendas mexicanas
            
            Para cada producto incluye:
            - nombre_exacto: Nombre completo del producto
            - categoria: Consola/Celular/Audífonos/Cámara/Laptop/Tablet/Smartwatch
            - marca: Marca del producto
            - precio_estimado: Precio estimado en MXN
            - facilidad_reventa: 1-10 (10 = muy fácil de revender)
            - demanda: Alta/Media/Baja
            - keywords_busqueda: Palabras clave para buscar en tiendas
            
            Responde SOLO en formato JSON válido con un array de objetos.
            """
            
            client = openai.OpenAI(api_key=self.openai_api_key)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Eres un experto en productos electrónicos para reventa. Responde SOLO en JSON válido."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            # Parsear respuesta JSON
            ai_response = response.choices[0].message.content.strip()
            
            # Limpiar respuesta si tiene markdown
            if ai_response.startswith("```json"):
                ai_response = ai_response.replace("```json", "").replace("```", "").strip()
            elif ai_response.startswith("```"):
                ai_response = ai_response.replace("```", "").strip()
            
            products = json.loads(ai_response)
            
            # Validar que sea una lista
            if not isinstance(products, list):
                raise ValueError("La respuesta no es una lista")
            
            # Validar estructura de cada producto
            validated_products = []
            for product in products:
                if self._validate_product_structure(product):
                    validated_products.append(product)
                else:
                    print(f"⚠️ Invalid product omitted: {product}")
            
            print(f"✅ {len(validated_products)} products generated successfully")
            
            # Save generated products
            await self._save_generated_products(validated_products)
            
            return validated_products
            
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing AI JSON: {e}")
            print(f"Response received: {ai_response}")
            return await self._get_fallback_products(count)
        except Exception as e:
            print(f"❌ Error generating products with AI: {e}")
            return await self._get_fallback_products(count)
    
    def _validate_product_structure(self, product: Dict[str, Any]) -> bool:
        """Validate product structure"""
        required_fields = [
            'nombre_exacto', 'categoria', 'marca', 'precio_estimado', 
            'facilidad_reventa', 'demanda', 'keywords_busqueda'
        ]
        
        for field in required_fields:
            if field not in product or not product[field]:
                return False
        
        # Validar tipos
        try:
            int(product['precio_estimado'])
            int(product['facilidad_reventa'])
        except (ValueError, TypeError):
            return False
        
        return True
    
    async def _save_generated_products(self, products: List[Dict[str, Any]]):
        """Save generated products to file"""
        try:
            # Create directory if it doesn't exist
            os.makedirs("scraper", exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"scraper/generated_products_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(products, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Products saved in: {filename}")
        except Exception as e:
            print(f"⚠️ Error saving products: {e}")
    
    async def _get_fallback_products(self, count: int) -> List[Dict[str, Any]]:
        """Fallback products if AI fails"""
        print("🔄 Using fallback products...")
        
        fallback_products = [
            {
                "nombre_exacto": "iPhone 15 Pro 128GB",
                "categoria": "Celular",
                "marca": "Apple",
                "precio_estimado": 25000,
                "facilidad_reventa": 10,
                "demanda": "Alta",
                "keywords_busqueda": "iPhone 15 Pro 128GB"
            },
            {
                "nombre_exacto": "PlayStation 5",
                "categoria": "Consola",
                "marca": "Sony",
                "precio_estimado": 12000,
                "facilidad_reventa": 9,
                "demanda": "Alta",
                "keywords_busqueda": "PlayStation 5 PS5"
            },
            {
                "nombre_exacto": "AirPods Pro 2da generación",
                "categoria": "Audífonos",
                "marca": "Apple",
                "precio_estimado": 5000,
                "facilidad_reventa": 8,
                "demanda": "Alta",
                "keywords_busqueda": "AirPods Pro 2da generación"
            },
            {
                "nombre_exacto": "MacBook Air M2 13 pulgadas",
                "categoria": "Laptop",
                "marca": "Apple",
                "precio_estimado": 25000,
                "facilidad_reventa": 9,
                "demanda": "Alta",
                "keywords_busqueda": "MacBook Air M2 13"
            },
            {
                "nombre_exacto": "Samsung Galaxy S24 Ultra",
                "categoria": "Celular",
                "marca": "Samsung",
                "precio_estimado": 30000,
                "facilidad_reventa": 8,
                "demanda": "Alta",
                "keywords_busqueda": "Samsung Galaxy S24 Ultra"
            }
        ]
        
        return fallback_products[:count]

class ProductResearch:
    """Investigador de APIs y métodos de scraping"""
    
    def __init__(self):
        self.api_endpoints = {
            "amazon": "https://api.amazon.com/paapi5",
            "mercadolibre": "https://api.mercadolibre.com",
            "walmart": "https://developer.walmartlabs.com",
            "liverpool": "https://api.liverpool.com.mx",
            "bestbuy": "https://api.bestbuy.com"
        }
    
    async def research_apis(self) -> Dict[str, Any]:
        """Investigar APIs disponibles"""
        print("🔍 Investigando APIs disponibles...")
        
        api_info = {}
        
        # MercadoLibre API (Gratuita)
        try:
            response = requests.get("https://api.mercadolibre.com/sites/MLM/categories", timeout=5)
            if response.status_code == 200:
                api_info["mercadolibre"] = {
                    "available": True,
                    "type": "REST",
                    "rate_limit": "No limit for basic usage",
                    "authentication": "None required for public data",
                    "endpoint": "https://api.mercadolibre.com"
                }
                print("✅ MercadoLibre API disponible")
        except:
            api_info["mercadolibre"] = {"available": False}
        
        # Liverpool API (Investigar)
        try:
            response = requests.get("https://www.liverpool.com.mx", timeout=5)
            if response.status_code == 200:
                api_info["liverpool"] = {
                    "available": True,
                    "type": "Web scraping",
                    "note": "No public API found, using web scraping"
                }
                print("✅ Liverpool disponible para scraping")
        except:
            api_info["liverpool"] = {"available": False}
        
        return api_info

# Función principal para generar productos
async def generate_products_for_scraping(count: int = 20) -> List[Dict[str, Any]]:
    """Función principal para generar productos"""
    generator = ProductGenerator()
    return await generator.generate_resellable_products(count)

if __name__ == "__main__":
    import asyncio
    asyncio.run(generate_products_for_scraping(20))
