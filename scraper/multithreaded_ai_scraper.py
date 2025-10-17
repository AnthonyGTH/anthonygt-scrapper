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
import requests
import concurrent.futures
from threading import Thread
import queue

# Agregar path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar generador de productos
from scraper.ai.product_generator import ProductGenerator

# Configuración - Usar variables de entorno
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID_HIGH = os.getenv("TELEGRAM_CHAT_ID_HIGH", "-1003150179214")  # Chat para descuentos >50%
TELEGRAM_CHAT_ID_MEDIUM = os.getenv("TELEGRAM_CHAT_ID_MEDIUM", "-4871231611")  # Chat para descuentos 20-50%
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

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
        self.openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        # Queue para resultados
        self.results_queue = queue.Queue()
        self.max_workers = 5  # Número de hilos paralelos
    
    async def generate_ai_products(self) -> List[Dict[str, Any]]:
        """Generate 20 products with AI"""
        try:
            print("🤖 Generando 20 productos con IA OpenAI...")
            
            generator = ProductGenerator()
            products = await generator.generate_resellable_products(20)
            
            print(f"✅ {len(products)} productos generados por IA")
            return products
            
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
            
            search_query = keywords.replace(' ', '+')
            search_url = f"https://www.amazon.com.mx/s?k={search_query}&ref=sr_pg_1"
            
            await page.goto(search_url, wait_until='domcontentloaded', timeout=15000)
            await page.wait_for_timeout(random.randint(1000, 2000))
            
            # Simular comportamiento humano
            await page.evaluate(f"window.scrollTo(0, {random.randint(100, 500)})")
            await page.wait_for_timeout(random.randint(500, 1000))
            
            # Múltiples selectores para productos
            product_selectors = [
                '[data-component-type="s-search-result"]',
                '.s-result-item',
                '[data-asin]'
            ]
            
            products = []
            for selector in product_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    if elements:
                        print(f"📦 Products found with selector {selector}: {len(elements)}")
                        
                        for element in elements[:3]:  # Limitar a 3 productos por selector
                            try:
                                # Título
                                title_selectors = [
                                    'h2 a span',
                                    'h2 span',
                                    '.s-size-mini span'
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
                                
                                # Precio
                                price_selectors = [
                                    '.a-price-whole',
                                    '.a-price .a-offscreen',
                                    '.a-price-range'
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
            return products
            
        except Exception as e:
            print(f"❌ Error on Amazon: {e}")
            return []
    
    async def scrape_mercadolibre_advanced(self, page, product_name: str, keywords: str) -> List[Dict[str, Any]]:
        """Scraper avanzado para MercadoLibre"""
        try:
            print(f"🛒 Scraping {product_name} on MercadoLibre (multithreaded)...")
            
            search_query = keywords.replace(' ', '%20')
            search_url = f"https://listado.mercadolibre.com.mx/{search_query}"
            
            await page.goto(search_url, wait_until='domcontentloaded', timeout=15000)
            await page.wait_for_timeout(random.randint(1000, 2000))
            
            # Simular comportamiento humano
            await page.evaluate(f"window.scrollTo(0, {random.randint(100, 500)})")
            await page.wait_for_timeout(random.randint(500, 1000))
            
            # Múltiples selectores para productos
            product_selectors = [
                '.ui-search-item',
                '.item',
                '[data-testid="product-item"]'
            ]
            
            products = []
            for selector in product_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    if elements:
                        print(f"📦 Products found with selector {selector}: {len(elements)}")
                        
                        for element in elements[:3]:
                            try:
                                # Título
                                title_selectors = [
                                    '.ui-search-item__title',
                                    'h2',
                                    '.item__title'
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
                                
                                # Precio
                                price_selectors = [
                                    '.price-tag-fraction',
                                    '.ui-search-price__part',
                                    '.item__price'
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
            return products
            
        except Exception as e:
            print(f"❌ Error on MercadoLibre: {e}")
            return []
    
    async def analyze_deal_with_ai(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analizar oferta con IA"""
        try:
            prompt = f"""
            Eres un experto en análisis de ofertas de productos electrónicos.
            Analiza esta oferta y proporciona tu opinión profesional.
            
            Producto: {product_data['name']}
            Precio: {product_data['current_price']}
            Descuento: {product_data['discount_percentage']:.1f}%
            Sitio: {product_data['site']}
            
            Proporciona análisis en JSON con:
            - confidence_score: 0-1 (confianza en la oferta)
            - reasoning: explicación detallada del análisis
            - market_opinion: opinión sobre el mercado y tendencias
            - recommendation: recomendación específica (comprar/no comprar/esperar)
            - resell_potential: potencial de reventa 1-10
            
            Responde SOLO en formato JSON válido.
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Eres un experto en análisis de ofertas. Responde SOLO en JSON válido."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # Limpiar respuesta
            if ai_response.startswith("```json"):
                ai_response = ai_response.replace("```json", "").replace("```", "").strip()
            elif ai_response.startswith("```"):
                ai_response = ai_response.replace("```", "").strip()
            
            # Limpiar caracteres problemáticos
            ai_response = ai_response.replace('\n', ' ').replace('\r', ' ')
            
            try:
                analysis = json.loads(ai_response)
            except json.JSONDecodeError as e:
                print(f"❌ Error parsing AI response: {e}")
                print(f"Response: {ai_response[:200]}...")
                return {
                    'confidence_score': 0.5,
                    'reasoning': 'Error parsing AI response',
                    'market_opinion': 'No analysis available',
                    'recommendation': 'Manual review required',
                    'resell_potential': 5
                }
            
            return {
                'confidence_score': analysis.get('confidence_score', 0.5),
                'reasoning': analysis.get('reasoning', 'Análisis no disponible'),
                'market_opinion': analysis.get('market_opinion', 'Sin opinión'),
                'recommendation': analysis.get('recommendation', 'Sin recomendación'),
                'resell_potential': analysis.get('resell_potential', 5)
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
            confidence = ai_analysis['confidence_score']
            reasoning = ai_analysis['reasoning']
            market_opinion = ai_analysis['market_opinion']
            recommendation = ai_analysis['recommendation']
            resell_potential = ai_analysis['resell_potential']
            
            emoji = "🔥" if discount_type == "high" else "💰"
            title = "Oferta EXCELENTE" if discount_type == "high" else "Oferta BUENA"
            
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
🔄 Potencial reventa: {resell_potential}/10"""
            
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, data=data, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ {discount_type} notification sent with AI analysis")
                self.notifications_sent += 1
            else:
                print(f"❌ Error sending {discount_type} notification: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error in {discount_type} notification: {e}")
    
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
            ai_response = ai_response.replace('\n', ' ').replace('\r', ' ')
            
            try:
                analysis = json.loads(ai_response)
            except json.JSONDecodeError as e:
                print(f"❌ Error parsing AI response: {e}")
                print(f"Response: {ai_response[:200]}...")
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
    
    async def scrape_product_worker(self, product: Dict[str, Any], worker_id: int):
        """Worker for scraping a product (multithreaded)"""
        try:
            print(f"🔄 Worker {worker_id}: Processing {product['nombre_exacto']}")
            
            async with async_playwright() as playwright:
                browser, context = await self.create_stealth_browser(playwright)
                page = await context.new_page()
                
                try:
                    # Scraping en Amazon
                    amazon_results = await self.scrape_amazon_advanced(
                        page, 
                        product['nombre_exacto'], 
                        product['keywords_busqueda']
                    )
                    
                    # Scraping en MercadoLibre
                    mercadolibre_results = await self.scrape_mercadolibre_advanced(
                        page, 
                        product['nombre_exacto'], 
                        product['keywords_busqueda']
                    )
                    
                    # Procesar resultados
                    all_results = amazon_results + mercadolibre_results
                    
                    for result in all_results:
                        try:
                            # Extraer precio numérico
                            price_text = result['price'].replace('$', '').replace(',', '').replace('MXN', '').strip()
                            price_value = float(price_text.split()[0])
                            
                            # Calcular descuento
                            estimated_price = product.get('precio_estimado', 10000)
                            discount = ((estimated_price - price_value) / estimated_price) * 100
                            
                            if discount >= 20:  # Solo ofertas >=20% descuento
                                deal_data = {
                                    'name': result['name'],
                                    'current_price': result['price'],
                                    'estimated_price': estimated_price,
                                    'discount_percentage': discount,
                                    'site': result['site'],
                                    'url': result['url']
                                }
                                
                                # Análisis con IA
                                ai_analysis = await self.analyze_deal_with_ai(deal_data)
                                
                                # Clasificar por tipo de descuento
                                if discount > 50:
                                    self.high_discount_deals.append(deal_data)
                                    if ai_analysis['confidence_score'] >= 0.65:
                                        await self.send_telegram_notification(
                                            deal_data, ai_analysis, 
                                            TELEGRAM_CHAT_ID_HIGH, "high"
                                        )
                                elif discount >= 20:
                                    self.medium_discount_deals.append(deal_data)
                                    if ai_analysis['confidence_score'] >= 0.6:
                                        await self.send_telegram_notification(
                                            deal_data, ai_analysis, 
                                            TELEGRAM_CHAT_ID_MEDIUM, "medium"
                                        )
                                    
                        except Exception as e:
                            continue
                    
                finally:
                    await browser.close()
                    
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
        
        # Create async tasks for multithreading
        tasks = []
        for i, product in enumerate(self.ai_products):
            task = asyncio.create_task(
                self.scrape_product_worker(product, i + 1)
            )
            tasks.append(task)
        
        # Execute all tasks in parallel
        print(f"🚀 Starting {len(tasks)} workers in parallel...")
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # Enviar resumen con IA
        await self.send_summary_with_ai()
        
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
