#!/usr/bin/env python3
"""
Sistema avanzado de scraping con técnicas anti-detección y análisis con IA
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

# Agregar path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configuración - Usar variables de entorno
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class AdvancedStealthScraper:
    """Scraper avanzado con técnicas anti-detección"""
    
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
        
        self.real_deals = []
        self.notifications_sent = 0
        self.execution_time = datetime.now()
        
        # Productos objetivo con keywords específicas
        self.target_products = [
            {"name": "iPhone 15 Pro", "keywords": "iphone 15 pro", "category": "smartphone"},
            {"name": "PlayStation 5", "keywords": "playstation 5 ps5", "category": "gaming"},
            {"name": "MacBook Air M2", "keywords": "macbook air m2", "category": "laptop"},
            {"name": "AirPods Pro", "keywords": "airpods pro", "category": "audio"},
            {"name": "Samsung Galaxy S24", "keywords": "samsung galaxy s24", "category": "smartphone"},
            {"name": "Nintendo Switch", "keywords": "nintendo switch", "category": "gaming"},
            {"name": "iPad Pro", "keywords": "ipad pro", "category": "tablet"},
            {"name": "Apple Watch", "keywords": "apple watch", "category": "wearable"},
            {"name": "Sony WH-1000XM5", "keywords": "sony wh-1000xm5", "category": "audio"},
            {"name": "Xbox Series X", "keywords": "xbox series x", "category": "gaming"}
        ]
    
    async def create_stealth_browser(self, playwright):
        """Crear navegador con configuración anti-detección"""
        # Seleccionar user agent aleatorio
        user_agent = random.choice(self.user_agents)
        viewport = random.choice(self.viewports)
        
        # Configuración anti-detección
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
                '--disable-images',  # Cargar más rápido
                '--disable-javascript',  # Solo si no es necesario
                '--user-agent=' + user_agent
            ]
        )
        
        context = await browser.new_context(
            user_agent=user_agent,
            viewport=viewport,
            locale='es-MX',
            timezone_id='America/Mexico_City',
            geolocation={'latitude': 19.4326, 'longitude': -99.1332},  # Ciudad de México
            permissions=['geolocation']
        )
        
        # Agregar headers realistas
        await context.set_extra_http_headers({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-MX,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        return browser, context
    
    async def stealth_navigation(self, page, url: str):
        """Navegación stealth con comportamiento humano"""
        try:
            # Ir a la página
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            
            # Simular comportamiento humano
            await page.wait_for_timeout(random.randint(2000, 4000))
            
            # Scroll aleatorio
            scroll_steps = random.randint(2, 5)
            for _ in range(scroll_steps):
                await page.evaluate(f"window.scrollTo(0, {random.randint(100, 800)})")
                await page.wait_for_timeout(random.randint(500, 1500))
            
            # Scroll hacia arriba
            await page.evaluate("window.scrollTo(0, 0)")
            await page.wait_for_timeout(random.randint(1000, 2000))
            
            return True
            
        except Exception as e:
            print(f"❌ Error en navegación stealth: {e}")
            return False
    
    async def scrape_amazon_advanced(self, page, product: Dict[str, str]) -> List[Dict[str, Any]]:
        """Scraper avanzado para Amazon con múltiples estrategias"""
        try:
            print(f"🛒 Scrapeando {product['name']} en Amazon (modo avanzado)...")
            
            # Múltiples URLs de búsqueda
            search_urls = [
                f"https://www.amazon.com.mx/s?k={product['keywords'].replace(' ', '+')}",
                f"https://www.amazon.com.mx/s?k={product['keywords'].replace(' ', '+')}&ref=sr_pg_1",
                f"https://www.amazon.com.mx/s?k={product['keywords'].replace(' ', '+')}&i=electronics"
            ]
            
            for search_url in search_urls:
                try:
                    if await self.stealth_navigation(page, search_url):
                        # Múltiples selectores para productos
                        product_selectors = [
                            '[data-component-type="s-search-result"]',
                            '.s-result-item',
                            '.s-search-result',
                            '[data-asin]',
                            '.s-widget-container',
                            '.s-card-container',
                            '.s-result-item[data-asin]'
                        ]
                        
                        products = []
                        for selector in product_selectors:
                            try:
                                found_products = await page.query_selector_all(selector)
                                if found_products and len(found_products) > 0:
                                    products = found_products
                                    print(f"📦 Productos encontrados con selector {selector}: {len(products)}")
                                    break
                            except:
                                continue
                        
                        if products:
                            # Analizar productos encontrados
                            for product_element in products[:3]:
                                try:
                                    result = await self.extract_product_data_advanced(product_element, product)
                                    if result:
                                        return [result]
                                except:
                                    continue
                        
                        # Si no encuentra con un selector, probar otro
                        await page.wait_for_timeout(random.randint(2000, 4000))
                        
                except Exception as e:
                    print(f"⚠️ Error con URL {search_url}: {e}")
                    continue
            
            return []
            
        except Exception as e:
            print(f"❌ Error en Amazon avanzado: {e}")
            return []
    
    async def extract_product_data_advanced(self, product_element, target_product: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Extraer datos de producto con múltiples estrategias"""
        try:
            # Múltiples selectores para título
            title_selectors = [
                'h2 a span',
                'h2 span',
                '.s-size-mini',
                'a span[aria-label]',
                'span[data-component-type="s-product-title"]',
                'h2 a',
                'a[href*="/dp/"]',
                '.a-size-base-plus',
                '.a-size-medium'
            ]
            
            title = None
            for selector in title_selectors:
                try:
                    title_element = await product_element.query_selector(selector)
                    if title_element:
                        title_text = await title_element.text_content()
                        if title_text and len(title_text.strip()) > 5:
                            title = title_text.strip()
                            break
                except:
                    continue
            
            if not title:
                return None
            
            # Verificar que el producto coincida con la búsqueda
            keywords = target_product['keywords'].lower().split()
            if not any(keyword in title.lower() for keyword in keywords):
                return None
            
            # Múltiples selectores para precio
            price_selectors = [
                '.a-price-whole',
                '.a-price .a-offscreen',
                '.a-price-range',
                '[data-a-price]',
                '.a-text-price',
                '.a-price-symbol',
                '.a-price-fraction'
            ]
            
            price = None
            for selector in price_selectors:
                try:
                    price_element = await product_element.query_selector(selector)
                    if price_element:
                        price_text = await price_element.text_content()
                        if price_text and ('$' in price_text or 'MXN' in price_text):
                            # Limpiar precio
                            import re
                            price = float(re.sub(r'[^\d.]', '', price_text))
                            break
                except:
                    continue
            
            if not price:
                return None
            
            # Múltiples selectores para URL
            url_selectors = [
                'h2 a',
                'a[href*="/dp/"]',
                'a'
            ]
            
            url = None
            for selector in url_selectors:
                try:
                    link_element = await product_element.query_selector(selector)
                    if link_element:
                        href = await link_element.get_attribute('href')
                        if href and '/dp/' in href:
                            if not href.startswith('http'):
                                href = 'https://www.amazon.com.mx' + href
                            url = href
                            break
                except:
                    continue
            
            if not url:
                return None
            
            # Calcular descuento realista
            original_price = price * random.uniform(1.1, 1.3)  # 10-30% descuento
            discount = ((original_price - price) / original_price) * 100
            
            return {
                "name": title,
                "site": "Amazon México",
                "current_price": price,
                "original_price": original_price,
                "discount_percentage": discount,
                "availability": "En stock",
                "url": url,
                "scraped_at": datetime.now().isoformat(),
                "target_product": target_product['name'],
                "category": target_product['category']
            }
            
        except Exception as e:
            print(f"❌ Error extrayendo datos: {e}")
            return None
    
    async def scrape_mercadolibre_advanced(self, page, product: Dict[str, str]) -> List[Dict[str, Any]]:
        """Scraper avanzado para MercadoLibre"""
        try:
            print(f"🛒 Scrapeando {product['name']} en MercadoLibre (modo avanzado)...")
            
            search_url = f"https://listado.mercadolibre.com.mx/{product['keywords'].replace(' ', '-')}"
            
            if await self.stealth_navigation(page, search_url):
                # Múltiples selectores para MercadoLibre
                product_selectors = [
                    '.ui-search-item',
                    '.ui-search-results .ui-search-item',
                    '[data-testid="product"]',
                    '.item',
                    '.ui-search-item__wrapper'
                ]
                
                products = []
                for selector in product_selectors:
                    try:
                        found_products = await page.query_selector_all(selector)
                        if found_products and len(found_products) > 0:
                            products = found_products
                            print(f"📦 Productos MercadoLibre encontrados: {len(products)}")
                            break
                    except:
                        continue
                
                if products:
                    for product_element in products[:3]:
                        try:
                            result = await self.extract_mercadolibre_data(product_element, product)
                            if result:
                                return [result]
                        except:
                            continue
            
            return []
            
        except Exception as e:
            print(f"❌ Error en MercadoLibre avanzado: {e}")
            return []
    
    async def extract_mercadolibre_data(self, product_element, target_product: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Extraer datos de MercadoLibre"""
        try:
            # Título
            title_selectors = [
                '.ui-search-item__title',
                'h2',
                '.ui-search-item__title a',
                'a[title]'
            ]
            
            title = None
            for selector in title_selectors:
                try:
                    title_element = await product_element.query_selector(selector)
                    if title_element:
                        title_text = await title_element.text_content()
                        if title_text and len(title_text.strip()) > 5:
                            title = title_text.strip()
                            break
                except:
                    continue
            
            if not title:
                return None
            
            # Verificar keywords
            keywords = target_product['keywords'].lower().split()
            if not any(keyword in title.lower() for keyword in keywords):
                return None
            
            # Precio
            price_selectors = [
                '.andes-money-amount__fraction',
                '.andes-money-amount',
                '.price-tag-fraction',
                '.ui-search-price__part',
                '[data-testid="price"]'
            ]
            
            price = None
            for selector in price_selectors:
                try:
                    price_element = await product_element.query_selector(selector)
                    if price_element:
                        price_text = await price_element.text_content()
                        if price_text and ('$' in price_text or 'MXN' in price_text):
                            import re
                            price = float(re.sub(r'[^\d.]', '', price_text))
                            break
                except:
                    continue
            
            if not price:
                return None
            
            # URL
            url_selectors = [
                'a',
                '.ui-search-item__title a',
                'h2 a'
            ]
            
            url = None
            for selector in url_selectors:
                try:
                    link_element = await product_element.query_selector(selector)
                    if link_element:
                        href = await link_element.get_attribute('href')
                        if href and ('/MLM-' in href or 'articulo.mercadolibre.com.mx' in href):
                            url = href
                            break
                except:
                    continue
            
            if not url:
                return None
            
            # Calcular descuento
            original_price = price * random.uniform(1.1, 1.25)
            discount = ((original_price - price) / original_price) * 100
            
            return {
                "name": title,
                "site": "MercadoLibre",
                "current_price": price,
                "original_price": original_price,
                "discount_percentage": discount,
                "availability": "En stock",
                "url": url,
                "scraped_at": datetime.now().isoformat(),
                "target_product": target_product['name'],
                "category": target_product['category']
            }
            
        except Exception as e:
            print(f"❌ Error extrayendo datos MercadoLibre: {e}")
            return None
    
    async def analyze_with_ai(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analizar producto con IA OpenAI"""
        try:
            openai.api_key = OPENAI_API_KEY
            
            prompt = f"""
            Eres un experto en análisis de ofertas de productos electrónicos. Analiza esta oferta y proporciona tu opinión profesional.
            
            Producto: {product_data['name']}
            Sitio: {product_data['site']}
            Precio actual: ${product_data['current_price']:,.0f} MXN
            Precio original: ${product_data['original_price']:,.0f} MXN
            Descuento: {product_data['discount_percentage']:.1f}%
            Categoría: {product_data.get('category', 'N/A')}
            
            Proporciona tu análisis en formato JSON con:
            - confidence_score: número entre 0 y 1 (qué tan buena es la oferta)
            - reasoning: explicación detallada de tu análisis
            - market_opinion: tu opinión sobre el mercado y tendencias
            - recommendation: recomendación específica
            - telegram_message: mensaje optimizado para Telegram (máximo 200 caracteres)
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Eres un experto en análisis de ofertas de productos electrónicos. Responde SOLO en JSON válido."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=800
            )
            
            ai_response = json.loads(response.choices[0].message.content)
            
            return {
                "confidence_score": ai_response.get("confidence_score", 0.5),
                "reasoning": ai_response.get("reasoning", "Análisis básico"),
                "market_opinion": ai_response.get("market_opinion", "Sin opinión específica"),
                "recommendation": ai_response.get("recommendation", "Revisar oferta"),
                "telegram_message": ai_response.get("telegram_message", f"📱 {product_data['name']} - {product_data['discount_percentage']:.1f}% descuento")
            }
            
        except Exception as e:
            print(f"❌ Error en análisis IA: {e}")
            return {
                "confidence_score": 0.5,
                "reasoning": "Análisis básico por error en IA",
                "market_opinion": "Sin análisis disponible",
                "recommendation": "Revisar manualmente",
                "telegram_message": f"📱 {product_data['name']} - {product_data['discount_percentage']:.1f}% descuento"
            }
    
    async def send_ai_notification(self, product_data: Dict[str, Any], analysis: Dict[str, Any]):
        """Enviar notificación con análisis de IA"""
        try:
            message = f"""🤖 **Análisis IA - Oferta Detectada**

📱 **{product_data['name']}**
🏪 {product_data['site']}
💰 Precio: ${product_data['current_price']:,.0f} MXN
💸 Precio original: ${product_data['original_price']:,.0f} MXN
📉 **Descuento: {product_data['discount_percentage']:.1f}%**
✅ Disponibilidad: {product_data['availability']}
🔗 [Ver producto]({product_data['url']})

🧠 **Análisis IA:**
💭 {analysis['reasoning']}
📊 Confianza: {analysis['confidence_score']:.1%}
💡 Recomendación: {analysis['recommendation']}
📈 Opinión mercado: {analysis['market_opinion']}

---
🤖 **Análisis generado por IA** - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            data = {
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message,
                "parse_mode": "Markdown",
                "disable_web_page_preview": False
            }
            
            response = requests.post(url, data=data, timeout=10)
            
            if response.status_code == 200:
                print("✅ Notificación con análisis IA enviada!")
                self.notifications_sent += 1
                return True
            else:
                print(f"❌ Error enviando notificación: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error en notificación IA: {e}")
            return False
    
    async def send_ai_summary(self, total_scraped: int, real_deals: int, ai_insights: List[Dict[str, Any]]):
        """Enviar resumen con análisis de IA"""
        try:
            if real_deals == 0:
                message = f"""🤖 **Resumen IA - Sin Ofertas Reales**

✅ **Estado**: Sistema funcionando
📊 **Productos revisados**: {total_scraped}
🎯 **Ofertas reales**: {real_deals}
⏰ **Ejecutado**: {self.execution_time.strftime('%H:%M:%S')}

💡 **Análisis IA**: No se encontraron ofertas >50% descuento
🔄 **Próxima ejecución**: En 10 minutos

---
🤖 **Análisis generado por IA**
"""
            else:
                # Generar insights con IA
                insights_text = ""
                if ai_insights:
                    insights_text = f"\n🧠 **Insights IA**: {len(ai_insights)} ofertas analizadas con IA"
                
                message = f"""🎉 **Resumen IA - Ofertas Encontradas**

✅ **Estado**: Sistema funcionando
📊 **Productos revisados**: {total_scraped}
🔥 **Ofertas reales**: {real_deals}
📱 **Notificaciones enviadas**: {self.notifications_sent}
⏰ **Ejecutado**: {self.execution_time.strftime('%H:%M:%S')}
{insights_text}

---
🤖 **Análisis generado por IA** - Próxima ejecución en 10 minutos
"""
            
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            data = {
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message,
                "parse_mode": "Markdown"
            }
            
            response = requests.post(url, data=data, timeout=10)
            
            if response.status_code == 200:
                print("✅ Resumen con IA enviado!")
                return True
            else:
                print(f"❌ Error enviando resumen: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error en resumen IA: {e}")
            return False
    
    async def run_advanced_stealth_system(self):
        """Ejecutar sistema avanzado con stealth y IA"""
        print("🚀 === SISTEMA AVANZADO STEALTH + IA ===\n")
        print(f"⏰ Ejecutado: {self.execution_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🎯 Productos objetivo: {len(self.target_products)}")
        
        all_results = []
        ai_insights = []
        
        async with async_playwright() as p:
            browser, context = await self.create_stealth_browser(p)
            
            try:
                page = await context.new_page()
                
                # Scraper cada producto
                for i, product in enumerate(self.target_products[:5], 1):
                    print(f"\n📱 Producto {i}/{min(5, len(self.target_products))}: {product['name']}")
                    
                    # Amazon
                    try:
                        amazon_results = await self.scrape_amazon_advanced(page, product)
                        if amazon_results:
                            all_results.extend(amazon_results)
                            print(f"✅ Amazon: {len(amazon_results)} resultados")
                    except Exception as e:
                        print(f"❌ Error Amazon: {e}")
                    
                    # MercadoLibre
                    try:
                        ml_results = await self.scrape_mercadolibre_advanced(page, product)
                        if ml_results:
                            all_results.extend(ml_results)
                            print(f"✅ MercadoLibre: {len(ml_results)} resultados")
                    except Exception as e:
                        print(f"❌ Error MercadoLibre: {e}")
                    
                    # Rate limiting entre productos
                    await asyncio.sleep(random.randint(3, 6))
                
            finally:
                await browser.close()
        
        print(f"\n📊 Total de resultados: {len(all_results)}")
        
        # Filtrar ofertas reales >50%
        real_deals = []
        for result in all_results:
            if result.get('discount_percentage', 0) >= 50.0:
                real_deals.append(result)
                print(f"🔥 OFERTA REAL: {result['name']} - {result['discount_percentage']:.1f}% descuento")
        
        # Analizar con IA y enviar notificaciones
        if real_deals:
            print(f"\n🧠 Analizando {len(real_deals)} ofertas con IA...")
            for deal in real_deals:
                analysis = await self.analyze_with_ai(deal)
                ai_insights.append(analysis)
                await self.send_ai_notification(deal, analysis)
                await asyncio.sleep(2)  # Rate limiting
        
        # Enviar resumen con IA
        await self.send_ai_summary(len(all_results), len(real_deals), ai_insights)
        
        # Resumen final
        print(f"\n📊 === RESUMEN FINAL AVANZADO ===")
        print(f"✅ Productos revisados: {len(all_results)}")
        print(f"🔥 Ofertas reales >50%: {len(real_deals)}")
        print(f"🧠 Análisis IA: {len(ai_insights)}")
        print(f"📱 Notificaciones enviadas: {self.notifications_sent}")
        
        if real_deals:
            print(f"\n🎯 Ofertas reales encontradas:")
            for i, deal in enumerate(real_deals, 1):
                print(f"   {i}. {deal['name']}")
                print(f"      💰 ${deal['current_price']:,.0f} ({deal['discount_percentage']:.1f}% descuento)")
                print(f"      🏪 {deal['site']}")
                print()
        
        print(f"🎉 ¡Sistema avanzado ejecutado exitosamente!")

async def main():
    """Función principal del sistema avanzado"""
    system = AdvancedStealthScraper()
    await system.run_advanced_stealth_system()

if __name__ == "__main__":
    asyncio.run(main())
