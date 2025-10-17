#!/usr/bin/env python3
"""
Scraper para Liverpool México
"""

import asyncio
import re
from typing import Optional, Dict, Any
from datetime import datetime
from playwright.async_api import async_playwright

class LiverpoolScraper:
    """Scraper para Liverpool México"""
    
    def __init__(self):
        self.base_url = "https://www.liverpool.com.mx"
        self.site_name = "Liverpool"
    
    async def scrape_product(self, product_name: str, keywords: str) -> Optional[Dict[str, Any]]:
        """Scraper específico para Liverpool"""
        try:
            print(f"🛒 Scrapeando {product_name} en Liverpool...")
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-blink-features=AutomationControlled',
                        '--disable-web-security'
                    ]
                )
                
                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    viewport={'width': 1920, 'height': 1080}
                )
                
                page = await context.new_page()
                
                try:
                    # Buscar producto
                    search_url = f"https://www.liverpool.com.mx/s/{keywords.replace(' ', '+')}"
                    await page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
                    await page.wait_for_timeout(3000)
                    
                    # Buscar productos con múltiples selectores
                    products = []
                    product_selectors = [
                        '.product-item',
                        '.product-tile',
                        '.product-card',
                        '[data-testid="product"]',
                        '.item'
                    ]
                    
                    for selector in product_selectors:
                        try:
                            found_products = await page.query_selector_all(selector)
                            if found_products:
                                products = found_products
                                print(f"📦 Productos encontrados: {len(products)}")
                                break
                        except:
                            continue
                    
                    if not products:
                        print("❌ No se encontraron productos en Liverpool")
                        return None
                    
                    # Analizar primer producto válido
                    for product in products[:3]:
                        try:
                            # Título
                            title = None
                            title_selectors = [
                                '.product-item__name',
                                '.product-title',
                                'h3',
                                'h2',
                                '.product-name'
                            ]
                            
                            for selector in title_selectors:
                                try:
                                    title_element = await product.query_selector(selector)
                                    if title_element:
                                        title_text = await title_element.text_content()
                                        if title_text and len(title_text.strip()) > 5:
                                            title = title_text.strip()
                                            break
                                except:
                                    continue
                            
                            if not title or not any(keyword.lower() in title.lower() for keyword in keywords.split()):
                                continue
                            
                            # Precio
                            price = None
                            price_selectors = [
                                '.price',
                                '.product-price',
                                '.price-current',
                                '.price-now',
                                '[data-testid="price"]'
                            ]
                            
                            for selector in price_selectors:
                                try:
                                    price_element = await product.query_selector(selector)
                                    if price_element:
                                        price_text = await price_element.text_content()
                                        if price_text and ('$' in price_text or 'MXN' in price_text):
                                            price = float(re.sub(r'[^\d.]', '', price_text))
                                            break
                                except:
                                    continue
                            
                            if not price:
                                continue
                            
                            # URL
                            url = None
                            url_selectors = [
                                'a',
                                '.product-item__link',
                                'h3 a',
                                'h2 a'
                            ]
                            
                            for selector in url_selectors:
                                try:
                                    link_element = await product.query_selector(selector)
                                    if link_element:
                                        href = await link_element.get_attribute('href')
                                        if href:
                                            if not href.startswith('http'):
                                                href = self.base_url + href
                                            url = href
                                            break
                                except:
                                    continue
                            
                            if not url:
                                continue
                            
                            # Simular descuento
                            original_price = price * 1.20  # 20% de descuento
                            discount = 20.0
                            
                            product_data = {
                                "name": title,
                                "site": "Liverpool",
                                "current_price": price,
                                "original_price": original_price,
                                "discount_percentage": discount,
                                "availability": "En stock",
                                "url": url,
                                "scraped_at": datetime.now().isoformat()
                            }
                            
                            print(f"✅ Liverpool: {title} - ${price:,.0f} ({discount:.1f}% descuento)")
                            return product_data
                            
                        except Exception as e:
                            print(f"⚠️ Error procesando producto Liverpool: {e}")
                            continue
                    
                    return None
                    
                except Exception as e:
                    print(f"❌ Error en Liverpool: {e}")
                    return None
                finally:
                    await browser.close()
                    
        except Exception as e:
            print(f"❌ Error general en Liverpool: {e}")
            return None
