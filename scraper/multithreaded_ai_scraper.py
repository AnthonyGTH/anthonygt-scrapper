#!/usr/bin/env python3
"""
Sistema de scraping multihilo con 20 productos IA y múltiples chats
"""

import asyncio
import json
import os
import sys
import random
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from playwright.async_api import async_playwright
import openai
from price_research.improved_price_checker import ImprovedPriceChecker
import requests
import concurrent.futures
from threading import Thread
import queue

# Import free API clients
from api_clients.free_apis import search_products_free

# Agregar path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar generador de productos
from scraper.ai.product_generator import ProductGenerator

# Configuración - Usar variables de entorno
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID_HIGH = os.getenv("TELEGRAM_CHAT_ID_HIGH", "-1003150179214")  # Chat para descuentos >50%
TELEGRAM_CHAT_ID_MEDIUM = os.getenv("TELEGRAM_CHAT_ID_MEDIUM", "-4871231611")  # Chat para descuentos 20-50%
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Verificar configuración de Telegram
if not TELEGRAM_BOT_TOKEN:
    print("⚠️ ADVERTENCIA: TELEGRAM_BOT_TOKEN no está configurado. Las notificaciones no funcionarán.")
    print("   Configura la variable de entorno TELEGRAM_BOT_TOKEN con tu token de bot de Telegram.")
else:
    print(f"✅ Telegram Bot Token configurado: {TELEGRAM_BOT_TOKEN[:10]}...")

class MultithreadedAIScraper:
    """Scraper multihilo con 20 productos IA y múltiples chats"""
    
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
        ]
        
        self.viewports = [
            {'width': 1920, 'height': 1080},
            {'width': 1366, 'height': 768},
            {'width': 1440, 'height': 900},
            {'width': 1536, 'height': 864},
            {'width': 1280, 'height': 720}
        ]
        
        self.high_discount_deals = []  # >50% descuento
        self.medium_discount_deals = []  # 20-50% descuento
        self.notifications_sent = 0
        self.execution_time = datetime.now()
        self.ai_products = []
        
        # Configurar OpenAI
        if OPENAI_API_KEY and OPENAI_API_KEY != "your_openai_api_key_here":
            self.openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
        else:
            print("⚠️ ADVERTENCIA: OPENAI_API_KEY no configurado. Usando productos de fallback.")
            self.openai_client = None
        
        # Configurar verificador de precios reales mejorado
        self.price_checker = ImprovedPriceChecker()
        print(f"✅ Verificador de precios reales mejorado configurado")
        
        # Queue para resultados
        self.results_queue = queue.Queue()
        self.max_workers = 3  # Reduced to prevent EPIPE errors
    
    async def generate_ai_products(self) -> List[Dict[str, Any]]:
        """Generate 20 products with AI"""
        try:
            if self.openai_client:
                print("🤖 Generando 20 productos con IA OpenAI...")
                
                generator = ProductGenerator()
                products = await generator.generate_resellable_products(20)
                
                print(f"✅ {len(products)} productos generados por IA")
                return products
            else:
                print("🔄 Usando productos de fallback (sin OpenAI)...")
                return await self._get_fallback_products()
            
        except Exception as e:
            print(f"❌ Error generando productos con IA: {e}")
            return await self._get_fallback_products()
    
    async def _get_fallback_products(self) -> List[Dict[str, Any]]:
        """Productos de respaldo si falla la IA"""
        print("🔄 Usando productos de respaldo...")
        
        fallback = [
            {"nombre_exacto": "iPhone 15 Pro 128GB", "keywords_busqueda": "iPhone 15 Pro 128GB", "categoria": "Celular", "marca": "Apple", "precio_estimado": 25000, "facilidad_reventa": 10, "demanda": "Alta"},
            {"nombre_exacto": "PlayStation 5", "keywords_busqueda": "PlayStation 5 PS5", "categoria": "Consola", "marca": "Sony", "precio_estimado": 12000, "facilidad_reventa": 9, "demanda": "Alta"},
            {"nombre_exacto": "AirPods Pro 2da generación", "keywords_busqueda": "AirPods Pro 2da generación", "categoria": "Audífonos", "marca": "Apple", "precio_estimado": 5000, "facilidad_reventa": 8, "demanda": "Alta"},
            {"nombre_exacto": "MacBook Air M2 13 pulgadas", "keywords_busqueda": "MacBook Air M2 13", "categoria": "Laptop", "marca": "Apple", "precio_estimado": 25000, "facilidad_reventa": 9, "demanda": "Alta"},
            {"nombre_exacto": "Samsung Galaxy S24 Ultra", "keywords_busqueda": "Samsung Galaxy S24 Ultra", "categoria": "Celular", "marca": "Samsung", "precio_estimado": 30000, "facilidad_reventa": 8, "demanda": "Alta"},
            {"nombre_exacto": "Nintendo Switch OLED", "keywords_busqueda": "Nintendo Switch OLED", "categoria": "Consola", "marca": "Nintendo", "precio_estimado": 8000, "facilidad_reventa": 9, "demanda": "Alta"},
            {"nombre_exacto": "iPad Pro 12.9 pulgadas", "keywords_busqueda": "iPad Pro 12.9", "categoria": "Tablet", "marca": "Apple", "precio_estimado": 20000, "facilidad_reventa": 8, "demanda": "Alta"},
            {"nombre_exacto": "Apple Watch Series 9", "keywords_busqueda": "Apple Watch Series 9", "categoria": "Smartwatch", "marca": "Apple", "precio_estimado": 8000, "facilidad_reventa": 7, "demanda": "Alta"},
            {"nombre_exacto": "Sony WH-1000XM5", "keywords_busqueda": "Sony WH-1000XM5", "categoria": "Audífonos", "marca": "Sony", "precio_estimado": 6000, "facilidad_reventa": 8, "demanda": "Alta"},
            {"nombre_exacto": "Xbox Series X", "keywords_busqueda": "Xbox Series X", "categoria": "Consola", "marca": "Microsoft", "precio_estimado": 10000, "facilidad_reventa": 9, "demanda": "Alta"}
        ]
        
        return fallback
    
    async def create_stealth_browser(self, playwright):
        """Crear navegador con configuración anti-detección"""
        user_agent = random.choice(self.user_agents)
        viewport = random.choice(self.viewports)
        
        browser = await playwright.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--disable-dev-shm-usage',
                '--no-first-run',
                '--disable-default-apps',
                '--disable-extensions',
                '--disable-plugins',
                '--disable-images',
                '--user-agent=' + user_agent
            ]
        )
        
        context = await browser.new_context(
            user_agent=user_agent,
            viewport=viewport,
            locale='es-MX',
            timezone_id='America/Mexico_City',
            geolocation={'latitude': 19.4326, 'longitude': -99.1332},
            permissions=['geolocation']
        )
        
        await context.set_extra_http_headers({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-MX,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        return browser, context
    
    async def scrape_amazon_advanced(self, page, product_name: str, keywords: str) -> List[Dict[str, Any]]:
        """Scraper avanzado para Amazon"""
        try:
            print(f"🛒 Scraping {product_name} on Amazon (multithreaded)...")
            
            search_query = str(keywords).replace(' ', '+')
            search_url = f"https://www.amazon.com.mx/s?k={search_query}&ref=sr_pg_1"
            
            await page.goto(search_url, wait_until='domcontentloaded', timeout=30000)
            await page.wait_for_timeout(random.randint(2000, 4000))
            
            # Simular comportamiento humano
            await page.evaluate(f"window.scrollTo(0, {random.randint(100, 500)})")
            await page.wait_for_timeout(random.randint(500, 1000))
            
            # Debug: Verificar si la página cargó correctamente
            page_title = await page.title()
            print(f"🔍 Amazon page title: {page_title}")
            
            # Verificar si hay elementos de productos en la página
            all_elements = await page.query_selector_all('*')
            print(f"🔍 Total elements on Amazon page: {len(all_elements)}")
            
            # Múltiples selectores para productos (actualizados)
            product_selectors = [
                '[data-component-type="s-search-result"]',
                '.s-result-item',
                '[data-asin]',
                '.s-card-container',
                '[data-index]',
                '.s-widget-container'
            ]
            
            products = []
            for selector in product_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    if elements:
                        print(f"📦 Products found with selector {selector}: {len(elements)}")
                        
                        for element in elements[:3]:  # Limitar a 3 productos por selector
                            try:
                                # Título (selectores actualizados)
                                title_selectors = [
                                    'h2 a span',
                                    'h2 span',
                                    '.s-size-mini span',
                                    'h2',
                                    '.s-title-instructions-style',
                                    '.s-link-style'
                                ]
                                
                                title = None
                                for title_sel in title_selectors:
                                    try:
                                        title_elem = await element.query_selector(title_sel)
                                        if title_elem:
                                            title = await title_elem.inner_text()
                                            if title and len(title.strip()) > 10:
                                                break
                                    except:
                                        continue
                                
                                if not title:
                                    continue
                                
                                # Precio (selectores actualizados)
                                price_selectors = [
                                    '.a-price-whole',
                                    '.a-price .a-offscreen',
                                    '.a-price-range',
                                    '.a-price-symbol',
                                    '[data-a-price-amount]',
                                    '.a-price'
                                ]
                                
                                price = None
                                for price_sel in price_selectors:
                                    try:
                                        price_elem = await element.query_selector(price_sel)
                                        if price_elem:
                                            price_text = await price_elem.inner_text()
                                            if price_text and '$' in price_text:
                                                price = price_text
                                                break
                                    except:
                                        continue
                                
                                # URL
                                url_selectors = [
                                    'h2 a',
                                    'a[href*="/dp/"]'
                                ]
                                
                                url = None
                                for url_sel in url_selectors:
                                    try:
                                        url_elem = await element.query_selector(url_sel)
                                        if url_elem:
                                            href = await url_elem.get_attribute('href')
                                            if href:
                                                if href.startswith('/'):
                                                    url = f"https://www.amazon.com.mx{href}"
                                                else:
                                                    url = href
                                                break
                                    except:
                                        continue
                                
                                if title and price and url:
                                    products.append({
                                        'name': title.strip(),
                                        'price': price.strip(),
                                        'url': url,
                                        'site': 'Amazon México'
                                    })
                                    
                            except Exception as e:
                                continue
                        
                        if products:
                            break
                            
                    await page.wait_for_timeout(random.randint(300, 800))
                    
                except Exception as e:
                    continue
            
            print(f"✅ Amazon: {len(products)} results")
            if products:
                print(f"📦 Found products: {[p['name'][:50] + '...' if len(p['name']) > 50 else p['name'] for p in products[:3]]}")
            return products
            
        except Exception as e:
            print(f"❌ Error on Amazon: {e}")
            return []
    
    async def scrape_mercadolibre_advanced(self, page, product_name: str, keywords: str) -> List[Dict[str, Any]]:
        """Scraper avanzado para MercadoLibre"""
        try:
            print(f"🛒 Scraping {product_name} on MercadoLibre (multithreaded)...")
            
            search_query = str(keywords).replace(' ', '%20')
            search_url = f"https://listado.mercadolibre.com.mx/{search_query}"
            
            await page.goto(search_url, wait_until='domcontentloaded', timeout=30000)
            await page.wait_for_timeout(random.randint(2000, 4000))
            
            # Simular comportamiento humano
            await page.evaluate(f"window.scrollTo(0, {random.randint(100, 500)})")
            await page.wait_for_timeout(random.randint(500, 1000))
            
            # Debug: Verificar si la página cargó correctamente
            page_title = await page.title()
            print(f"🔍 Amazon page title: {page_title}")
            
            # Verificar si hay elementos de productos en la página
            all_elements = await page.query_selector_all('*')
            print(f"🔍 Total elements on Amazon page: {len(all_elements)}")
            
            # Múltiples selectores para productos (actualizados)
            product_selectors = [
                '.ui-search-item',
                '.ui-search-results .ui-search-item',
                '[data-testid="product"]',
                '.item',
                '.ui-search-item__wrapper',
                '.ui-search-layout__item',
                '.ui-search-results__item'
            ]
            
            products = []
            for selector in product_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    if elements:
                        print(f"📦 Products found with selector {selector}: {len(elements)}")
                        
                        for element in elements[:3]:
                            try:
                                # Título (selectores actualizados)
                                title_selectors = [
                                    '.ui-search-item__title',
                                    'h2',
                                    '.item__title',
                                    '.ui-search-item__title-label',
                                    'a[title]'
                                ]
                                
                                title = None
                                for title_sel in title_selectors:
                                    try:
                                        title_elem = await element.query_selector(title_sel)
                                        if title_elem:
                                            title = await title_elem.inner_text()
                                            if title and len(title.strip()) > 10:
                                                break
                                    except:
                                        continue
                                
                                if not title:
                                    continue
                                
                                # Precio (selectores actualizados)
                                price_selectors = [
                                    '.price-tag-fraction',
                                    '.ui-search-price__part',
                                    '.item__price',
                                    '.ui-search-price__second-line .price-tag-amount',
                                    '.ui-search-price__second-line',
                                    '.price-tag-amount',
                                    '.ui-search-price'
                                ]
                                
                                price = None
                                for price_sel in price_selectors:
                                    try:
                                        price_elem = await element.query_selector(price_sel)
                                        if price_elem:
                                            price_text = await price_elem.inner_text()
                                            if price_text and '$' in price_text:
                                                price = price_text
                                                break
                                    except:
                                        continue
                                
                                # URL
                                url_selectors = [
                                    'a',
                                    '.ui-search-link'
                                ]
                                
                                url = None
                                for url_sel in url_selectors:
                                    try:
                                        url_elem = await element.query_selector(url_sel)
                                        if url_elem:
                                            href = await url_elem.get_attribute('href')
                                            if href:
                                                url = href
                                                break
                                    except:
                                        continue
                                
                                if title and price and url:
                                    products.append({
                                        'name': title.strip(),
                                        'price': price.strip(),
                                        'url': url,
                                        'site': 'MercadoLibre México'
                                    })
                                    
                            except Exception as e:
                                continue
                        
                        if products:
                            break
                            
                    await page.wait_for_timeout(random.randint(300, 800))
                    
                except Exception as e:
                    continue
            
            print(f"✅ MercadoLibre: {len(products)} results")
            if products:
                print(f"📦 Found products: {[p['name'][:50] + '...' if len(p['name']) > 50 else p['name'] for p in products[:3]]}")
            return products
            
        except Exception as e:
            print(f"❌ Error on MercadoLibre: {e}")
            return []
    
    async def analyze_deal_with_ai(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analizar oferta con IA usando precios reales de reventa"""
        try:
            # Obtener precios reales de reventa
            print(f"🔍 Obteniendo precios reales de reventa para: {product_data['name']}")
            resale_data = await self.price_checker.get_resale_prices(product_data['name'])
            
            # Guardar datos de reventa para usar en notificaciones
            self._last_resale_data = resale_data
            
            # Analizar oportunidad de reventa
            current_price = float(str(product_data['current_price']).replace('$', '').replace(',', ''))
            price_analysis = self.price_checker.analyze_price_opportunity(current_price, resale_data)
            
            # Obtener precio estimado del producto original
            original_product = None
            for product in self.ai_products:
                if product['nombre_exacto'].lower() in product_data['name'].lower():
                    original_product = product
                    break
            
            precio_estimado = original_product.get('precio_estimado', 0) if original_product else 0
            
            prompt = f"""
            Eres un experto en análisis de ofertas de productos electrónicos y reventa.
            Analiza esta oferta usando datos REALES de precios de reventa obtenidos de Facebook Marketplace, eBay y MercadoLibre.
            
            PRODUCTO BUSCADO: {original_product['nombre_exacto'] if original_product else 'Producto genérico'}
            PRODUCTO ENCONTRADO: {product_data['name']}
            Precio actual: {product_data['current_price']}
            Precio estimado del mercado: ${precio_estimado}
            Descuento calculado: {product_data['discount_percentage']:.1f}%
            Sitio: {product_data['site']}
            
            DATOS REALES DE REVENTA OBTENIDOS:
            - Precio promedio de reventa: ${resale_data.get('average_resale_price', 0):,.0f}
            - Rango de precios: {resale_data.get('price_range', 'No disponible')}
            - Confianza en datos: {resale_data.get('confidence', 'low')}
            - Análisis de oportunidad: {price_analysis.get('reasoning', 'No disponible')}
            - Es buena oportunidad: {price_analysis.get('is_good_deal', False)}
            - Potencial de ganancia: ${price_analysis.get('profit_potential', 0):,.0f} ({price_analysis.get('profit_percentage', 0):.1f}%)
            
            TAREA CRÍTICA:
            1. Verifica que el producto encontrado sea realmente el producto buscado (no accesorios)
            2. Usa los datos REALES de precios de reventa proporcionados arriba
            3. Considera el potencial de ganancia real calculado
            4. Determina si realmente es una buena oportunidad de reventa
            
            Proporciona análisis en JSON con:
            - confidence_score: 0-1 (confianza en la oferta, 0.8+ solo si es el producto correcto Y buen precio de reventa)
            - reasoning: explicación corta (máximo 50 palabras)
            - market_opinion: opinión del mercado (máximo 30 palabras)
            - recommendation: recomendación específica (máximo 20 palabras)
            - resell_potential: potencial de reventa 1-10
            - is_correct_product: true/false si es el producto buscado
            - real_discount: true/false si el descuento es real basado en precios de reventa REALES
            - market_price_range: rango de precios de reventa REALES obtenido
            - resell_price_estimate: precio estimado de reventa REAL obtenido
            
            Responde SOLO en formato JSON válido.
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Eres un experto en análisis de ofertas. Responde SOLO en JSON válido."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=300
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # Limpiar respuesta
            if ai_response.startswith("```json"):
                ai_response = ai_response.replace("```json", "").replace("```", "").strip()
            elif ai_response.startswith("```"):
                ai_response = ai_response.replace("```", "").strip()
            
            # Limpiar caracteres problemáticos
            ai_response = ai_response.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
            
            try:
                analysis = json.loads(ai_response)
            except json.JSONDecodeError as e:
                print(f"❌ Error parsing AI response: {e}")
                print(f"Response: {ai_response[:200]}...")
                # Intentar limpiar la respuesta
                try:
                    # Buscar el primer { y último } válido
                    start = ai_response.find('{')
                    end = ai_response.rfind('}')
                    if start != -1 and end != -1 and end > start:
                        cleaned_response = ai_response[start:end+1]
                        analysis = json.loads(cleaned_response)
                        print("✅ Respuesta limpiada exitosamente")
                    else:
                        raise ValueError("No se encontró JSON válido")
                except:
                    return {
                        'confidence_score': 0.5,
                        'reasoning': 'Error parsing AI response',
                        'market_opinion': 'No analysis available',
                        'recommendation': 'Manual review required',
                        'resell_potential': 5
                    }
            
            # Usar datos reales de reventa para ajustar la confianza
            if not price_analysis.get('is_good_deal', False):
                analysis['confidence_score'] = min(analysis.get('confidence_score', 0.5), 0.3)
                analysis['reasoning'] = f"Oportunidad de reventa limitada: {price_analysis.get('reasoning', '')}"
            
            # Si no es el producto correcto, reducir significativamente la confianza
            if not analysis.get('is_correct_product', True):
                analysis['confidence_score'] = min(analysis.get('confidence_score', 0.5), 0.2)
                analysis['reasoning'] = "Producto incorrecto o accesorio"
            
            # Filtrar productos que claramente son accesorios
            product_name = product_data['name'].lower()
            accessory_keywords = ['funda', 'carcasa', 'cargador', 'cable', 'adaptador', 'protector', 'estuche', 'case', 'cover', 'batería', 'bateria', 'lápiz', 'lapiz', 'stylus', 'correa', 'strap', 'band', 'pulsera', 'watch band', 'screen protector', 'película', 'film', 'tempered glass', 'vidrio templado']
            
            if any(keyword in product_name for keyword in accessory_keywords):
                analysis['confidence_score'] = min(analysis.get('confidence_score', 0.5), 0.1)
                analysis['reasoning'] = "Es un accesorio, no el producto principal"
                analysis['is_correct_product'] = False
            
            # Si el descuento no es real, reducir la confianza
            if not analysis.get('real_discount', True):
                analysis['confidence_score'] = min(analysis.get('confidence_score', 0.5), 0.4)
                analysis['reasoning'] = f"{analysis.get('reasoning', '')} - Descuento inflado"
            
            # Usar datos reales de reventa para validar la oportunidad
            if resale_data.get('average_resale_price', 0) > 0:
                try:
                    current_price = float(str(product_data['current_price']).replace('$', '').replace(',', ''))
                    avg_resale = resale_data.get('average_resale_price', 0)
                    if avg_resale <= current_price * 1.1:  # Si la reventa es similar al precio actual
                        analysis['confidence_score'] = min(analysis.get('confidence_score', 0.5), 0.3)
                        analysis['reasoning'] = f"{analysis.get('reasoning', '')} - Precio similar a reventa real"
                except (ValueError, TypeError):
                    pass  # Si no se puede convertir el precio, continuar
            
            return {
                'confidence_score': analysis.get('confidence_score', 0.5),
                'reasoning': analysis.get('reasoning', 'Análisis no disponible'),
                'market_opinion': analysis.get('market_opinion', 'Sin opinión'),
                'recommendation': analysis.get('recommendation', 'Sin recomendación'),
                'resell_potential': analysis.get('resell_potential', 5),
                'is_correct_product': analysis.get('is_correct_product', True),
                'real_discount': analysis.get('real_discount', True),
                'market_price_range': analysis.get('market_price_range', 'No disponible'),
                'resell_price_estimate': analysis.get('resell_price_estimate', 'No disponible')
            }
            
        except Exception as e:
            print(f"❌ Error en análisis IA: {e}")
            return {
                'confidence_score': 0.5,
                'reasoning': 'Error en análisis IA',
                'market_opinion': 'Sin opinión',
                'recommendation': 'Sin recomendación',
                'resell_potential': 5
            }
    
    async def send_telegram_notification(self, deal_data: Dict[str, Any], ai_analysis: Dict[str, Any], chat_id: str, discount_type: str):
        """Enviar notificación a Telegram con análisis IA"""
        try:
            # Verificar si el bot token está configurado
            if not TELEGRAM_BOT_TOKEN:
                print(f"⚠️ No se puede enviar notificación {discount_type}: TELEGRAM_BOT_TOKEN no configurado")
                return
            
            confidence = ai_analysis['confidence_score']
            reasoning = ai_analysis['reasoning']
            market_opinion = ai_analysis['market_opinion']
            recommendation = ai_analysis['recommendation']
            resell_potential = ai_analysis['resell_potential']
            
            emoji = "🔥" if discount_type == "high" else "💰"
            title = "Oferta EXCELENTE" if discount_type == "high" else "Oferta BUENA"
            
            # Información adicional del análisis
            product_status = "✅ Producto correcto" if ai_analysis.get('is_correct_product', True) else "❌ Accesorio/producto incorrecto"
            discount_status = "✅ Descuento real" if ai_analysis.get('real_discount', True) else "⚠️ Descuento inflado"
            market_range = ai_analysis.get('market_price_range', 'No disponible')
            resell_estimate = ai_analysis.get('resell_price_estimate', 'No disponible')
            
            # Agregar datos de precios reales si están disponibles
            real_data_info = ""
            if 'resale_data' in deal_data:
                resale_data = deal_data['resale_data']
                print(f"📊 Datos de reventa en notificación: {resale_data}")
                if resale_data.get('average_resale_price', 0) > 0:
                    real_data_info = f"\n💰 Precio reventa real: ${resale_data.get('average_resale_price', 0):,.0f}\n📊 Rango real: {resale_data.get('price_range', 'N/A')}"
                    print(f"✅ Datos de reventa válidos agregados al mensaje")
                else:
                    print(f"⚠️ Datos de reventa con precio promedio 0")
            else:
                print(f"⚠️ No hay datos de reventa en deal_data")
            
            message = f"""{emoji} {title} - Análisis IA

📱 {deal_data['name']}
🏪 {deal_data['site']}
💰 Precio: {deal_data['current_price']}
📉 DESCUENTO: {deal_data['discount_percentage']:.1f}%

🧠 Análisis IA:
💭 {reasoning}
📊 Confianza: {confidence:.0%}
💡 Recomendación: {recommendation}
📈 Opinión mercado: {market_opinion}
🔄 Potencial reventa: {resell_potential}/10

🔍 Verificación:
{product_status}
{discount_status}
💰 Rango mercado: {market_range}
💵 Precio reventa estimado: {resell_estimate}{real_data_info}"""
            
            # Crear botones de Telegram (solo si hay URL válida)
            keyboard = None
            print(f"🔗 Verificando URL para botones: {deal_data.get('url')}")
            if deal_data.get('url') and deal_data.get('url') != '#' and deal_data.get('url').startswith('http'):
                try:
                    keyboard = {
                        "inline_keyboard": [
                            [{"text": "🔗 Ver Producto", "url": deal_data.get('url')}],
                            [{"text": "📊 Comparar Precios", "url": f"https://www.google.com/search?q={deal_data['name'].replace(' ', '+')}+precio"}]
                        ]
                    }
                    print(f"✅ Botones creados exitosamente")
                except Exception as e:
                    print(f"⚠️ Error creando botones: {e}")
                    keyboard = None
            else:
                print(f"⚠️ URL no válida para botones: {deal_data.get('url')}")
            
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'Markdown'
            }
            
            # Solo agregar botones si existen
            if keyboard:
                data['reply_markup'] = json.dumps(keyboard)
                print(f"✅ Botones agregados al mensaje de Telegram")
            else:
                print(f"⚠️ No hay botones para agregar")
            
            print(f"📤 Enviando notificación {discount_type} a chat {chat_id}...")
            response = requests.post(url, data=data, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ Notificación {discount_type} enviada exitosamente")
                self.notifications_sent += 1
            else:
                print(f"❌ Error enviando notificación {discount_type}: {response.status_code}")
                print(f"   Respuesta: {response.text}")
                
        except Exception as e:
            print(f"❌ Error en notificación {discount_type}: {e}")
    
    async def send_summary_with_ai(self):
        """Enviar resumen con análisis IA"""
        try:
            total_products = len(self.ai_products)
            high_deals = len(self.high_discount_deals)
            medium_deals = len(self.medium_discount_deals)
            
            prompt = f"""
            Eres un experto en análisis de mercado de productos electrónicos.
            
            Resumen de scraping:
            - Productos revisados: {total_products}
            - Ofertas excelentes >50%: {high_deals}
            - Ofertas buenas 20-50%: {medium_deals}
            - Tiempo de ejecución: {self.execution_time.strftime('%H:%M:%S')}
            
            Proporciona un análisis profesional en JSON con:
            - market_analysis: análisis del estado del mercado
            - trends: tendencias observadas
            - recommendations: recomendaciones para el usuario
            - next_steps: próximos pasos sugeridos
            
            Responde SOLO en formato JSON válido.
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Eres un experto en análisis de mercado. Responde SOLO en JSON válido."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=300
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # Limpiar respuesta
            if ai_response.startswith("```json"):
                ai_response = ai_response.replace("```json", "").replace("```", "").strip()
            elif ai_response.startswith("```"):
                ai_response = ai_response.replace("```", "").strip()
            
            # Limpiar caracteres problemáticos
            ai_response = ai_response.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
            
            try:
                analysis = json.loads(ai_response)
            except json.JSONDecodeError as e:
                print(f"❌ Error parsing AI response: {e}")
                print(f"Response: {ai_response[:200]}...")
                # Intentar limpiar la respuesta
                try:
                    # Buscar el primer { y último } válido
                    start = ai_response.find('{')
                    end = ai_response.rfind('}')
                    if start != -1 and end != -1 and end > start:
                        cleaned_response = ai_response[start:end+1]
                        analysis = json.loads(cleaned_response)
                        print("✅ Respuesta limpiada exitosamente")
                    else:
                        raise ValueError("No se encontró JSON válido")
                except:
                    return {
                        'confidence_score': 0.5,
                        'reasoning': 'Error parsing AI response',
                        'market_opinion': 'No analysis available',
                        'recommendation': 'Manual review required',
                        'resell_potential': 5
                    }
            
            # Send to both chats (only if configured)
            chats_to_notify = []
            if TELEGRAM_CHAT_ID_HIGH:
                chats_to_notify.append((TELEGRAM_CHAT_ID_HIGH, "Chat Excelentes"))
            if TELEGRAM_CHAT_ID_MEDIUM:
                chats_to_notify.append((TELEGRAM_CHAT_ID_MEDIUM, "Chat Buenos"))
            
            for chat_id, chat_name in chats_to_notify:
                message = f"""🤖 Resumen IA - Sistema Multihilo

✅ Estado: Sistema funcionando
📊 Productos revisados: {total_products}
🔥 Ofertas excelentes >50%: {high_deals}
💰 Ofertas buenas 20-50%: {medium_deals}
⏰ Ejecutado: {self.execution_time.strftime('%H:%M:%S')}

💡 Análisis IA: {analysis.get('market_analysis', 'Sin análisis')}
📈 Tendencias: {analysis.get('trends', 'Sin tendencias')}
🔄 Recomendaciones: {analysis.get('recommendations', 'Sin recomendaciones')}
🎯 Próximos pasos: {analysis.get('next_steps', 'Continuar monitoreo')}"""
                
                url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
                data = {
                    'chat_id': chat_id,
                    'text': message,
                    'parse_mode': 'HTML'
                }
                
                response = requests.post(url, data=data, timeout=10)
                
                if response.status_code == 200:
                    print(f"✅ Summary sent to {chat_name}")
                else:
                    print(f"❌ Error sending summary to {chat_name}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error in AI summary: {e}")
    
    async def send_no_deals_notification(self):
        """Enviar notificación simple cuando no hay ofertas"""
        try:
            message = f"""🤖 Sistema de Scraping - Sin Ofertas

✅ Estado: Sistema funcionando correctamente
📊 Productos revisados: {len(self.ai_products)}
🎯 Ofertas encontradas: 0
⏰ Ejecutado: {self.execution_time.strftime('%H:%M:%S')}

💡 No se encontraron ofertas con descuento >20%
🔄 Próxima ejecución: En 1 hora
📱 Sistema monitoreando continuamente"""
            
            # Enviar a ambos chats si están configurados
            chats_to_notify = []
            if TELEGRAM_CHAT_ID_HIGH:
                chats_to_notify.append((TELEGRAM_CHAT_ID_HIGH, "Chat Excelentes"))
            if TELEGRAM_CHAT_ID_MEDIUM:
                chats_to_notify.append((TELEGRAM_CHAT_ID_MEDIUM, "Chat Buenos"))
            
            for chat_id, chat_name in chats_to_notify:
                url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
                data = {
                    'chat_id': chat_id,
                    'text': message,
                    'parse_mode': 'HTML'
                }
                
                response = requests.post(url, data=data, timeout=10)
                
                if response.status_code == 200:
                    print(f"✅ No deals notification sent to {chat_name}")
                else:
                    print(f"❌ Error sending no deals notification to {chat_name}: {response.status_code}")
                    
        except Exception as e:
            print(f"❌ Error sending no deals notification: {e}")
    
    async def scrape_product_worker_with_semaphore(self, product: Dict[str, Any], worker_id: int, semaphore: asyncio.Semaphore):
        """Worker with semaphore to limit concurrent execution"""
        async with semaphore:
            await self.scrape_product_worker(product, worker_id)
    
    async def scrape_product_worker(self, product: Dict[str, Any], worker_id: int):
        """Worker for scraping a product using APIs (multithreaded)"""
        try:
            print(f"🔄 Worker {worker_id}: Processing {product['nombre_exacto']}")
            
            # Add small delay to reduce system load
            await asyncio.sleep(worker_id * 0.5)  # Stagger requests
            
            # Use unified API client instead of scraping
            search_query = product['keywords_busqueda']
            
            # Convert list to string if needed
            if isinstance(search_query, list):
                search_query = ' '.join(search_query)
            
            print(f"🔍 Worker {worker_id}: Searching '{search_query}' via APIs...")
            
            # Search all sites using free APIs
            api_results = await search_products_free(search_query, limit_per_site=3)
            
            # Flatten results from all sites
            all_results = []
            for site, products in api_results.items():
                for product_data in products:
                    product_data['site'] = site
                    all_results.append(product_data)
            
            print(f"📊 Worker {worker_id}: Found {len(all_results)} total products via APIs")
            
            for result in all_results:
                try:
                    # Extraer precio numérico
                    price_text = result['price'].replace('$', '').replace(',', '').replace('MXN', '').strip()
                    price_value = float(price_text.split()[0])
                    
                    # Obtener precios de reventa reales para calcular descuento real
                    print(f"🔍 Worker {worker_id}: Obteniendo precios de reventa para {result['name'][:30]}...")
                    resale_data = await self.price_checker.get_resale_prices(result['name'])
                    self._last_resale_data = resale_data
                    
                    # Calcular descuento basado en precio de reventa real
                    avg_resale_price = resale_data.get('average_resale_price', 0)
                    if avg_resale_price > 0:
                        # Usar precio de reventa como referencia
                        estimated_price = avg_resale_price  # Usar precio de reventa como referencia
                        discount = ((avg_resale_price - price_value) / avg_resale_price) * 100
                        print(f"💰 Worker {worker_id}: Precio reventa: ${avg_resale_price:,.0f} - Descuento real: {discount:.1f}%")
                    else:
                        # Fallback al precio estimado si no hay datos de reventa
                        estimated_price = product.get('precio_estimado', 10000)
                        discount = ((estimated_price - price_value) / estimated_price) * 100
                        print(f"💰 Worker {worker_id}: Sin datos reventa - Usando precio estimado: ${estimated_price:,.0f} - Descuento: {discount:.1f}%")
                    
                    print(f"💰 Worker {worker_id}: Found {result['name'][:30]}... - Price: {result['price']} - Discount: {discount:.1f}%")
                    
                    if discount >= 20:  # Solo ofertas >=20% descuento
                        deal_data = {
                            'name': result['name'],
                            'current_price': result['price'],
                            'estimated_price': estimated_price,
                            'discount_percentage': discount,
                            'site': result['site'],
                            'url': result['url']
                        }
                        
                        # Análisis con IA (incluye datos de reventa reales)
                        ai_analysis = await self.analyze_deal_with_ai(deal_data)
                        
                        # Agregar datos de reventa reales al deal_data
                        if hasattr(self, '_last_resale_data'):
                            deal_data['resale_data'] = self._last_resale_data
                            print(f"💰 Worker {worker_id}: Datos de reventa agregados - Precio promedio: ${self._last_resale_data.get('average_resale_price', 0):,.0f}")
                        else:
                            print(f"⚠️ Worker {worker_id}: No hay datos de reventa disponibles")
                        
                        # Clasificar por tipo de descuento
                        if discount > 50:
                            print(f"🔥 Worker {worker_id}: EXCELLENT DEAL >50% - {result['name'][:30]}... - {discount:.1f}% off")
                            self.high_discount_deals.append(deal_data)
                            if ai_analysis['confidence_score'] >= 0.65:
                                await self.send_telegram_notification(
                                    deal_data, ai_analysis, 
                                    TELEGRAM_CHAT_ID_HIGH, "high"
                                )
                        elif discount >= 20:
                            print(f"💰 Worker {worker_id}: GOOD DEAL 20-50% - {result['name'][:30]}... - {discount:.1f}% off")
                            self.medium_discount_deals.append(deal_data)
                            if ai_analysis['confidence_score'] >= 0.6:
                                await self.send_telegram_notification(
                                    deal_data, ai_analysis, 
                                    TELEGRAM_CHAT_ID_MEDIUM, "medium"
                                )
                                
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"❌ Error in worker {worker_id}: {e}")
    
    async def run_multithreaded_scraping(self):
        """Execute multithreaded scraping with 20 AI products"""
        print("🚀 === MULTITHREADED SYSTEM WITH 20 AI PRODUCTS ===")
        print(f"⏰ Executed: {self.execution_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🧵 Parallel workers: {self.max_workers}")
        
        # Generate products with AI
        self.ai_products = await self.generate_ai_products()
        print(f"🎯 Target products: {len(self.ai_products)}")
        
        # Create semaphore to limit concurrent workers
        semaphore = asyncio.Semaphore(self.max_workers)
        
        # Create async tasks for multithreading with semaphore
        tasks = []
        for i, product in enumerate(self.ai_products):
            task = asyncio.create_task(
                self.scrape_product_worker_with_semaphore(product, i + 1, semaphore)
            )
            tasks.append(task)
        
        # Execute all tasks in parallel
        print(f"🚀 Starting {len(tasks)} workers with max {self.max_workers} concurrent...")
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # Enviar resumen con IA
        await self.send_summary_with_ai()
        
        # Enviar notificación simple si no hay ofertas
        if len(self.high_discount_deals) == 0 and len(self.medium_discount_deals) == 0:
            await self.send_no_deals_notification()
        
        print(f"\n📊 === FINAL MULTITHREADED SUMMARY ===")
        print(f"✅ Products reviewed: {len(self.ai_products)}")
        print(f"🔥 Excellent deals >50%: {len(self.high_discount_deals)}")
        print(f"💰 Good deals 20-50%: {len(self.medium_discount_deals)}")
        print(f"🧠 AI Analysis: {len(self.high_discount_deals) + len(self.medium_discount_deals)}")
        print(f"📱 Notifications sent: {self.notifications_sent}")
        print(f"🎉 Multithreaded system with 20 AI products executed successfully!")

async def main():
    """Función principal"""
    scraper = MultithreadedAIScraper()
    await scraper.run_multithreaded_scraping()

if __name__ == "__main__":
    asyncio.run(main())
