import asyncio
import re
import json
import requests
from typing import Dict, List, Any, Optional
from playwright.async_api import async_playwright
from urllib.parse import quote_plus
import time

class ImprovedPriceChecker:
    """Verificador de precios mejorado con múltiples estrategias"""
    
    def __init__(self):
        self.browser_semaphore = asyncio.Semaphore(2)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
    
    async def get_resale_prices(self, product_name: str) -> Dict[str, Any]:
        """Obtiene precios de reventa usando múltiples estrategias"""
        print(f"🔍 Investigando precios de reventa para: {product_name}")
        
        prices = {
            'facebook_marketplace': [],
            'ebay': [],
            'mercadolibre_usado': [],
            'google_shopping': [],
            'average_resale_price': 0,
            'price_range': '',
            'confidence': 'low'
        }
        
        # Estrategia 1: APIs directas
        try:
            api_prices = await self._search_with_apis(product_name)
            prices.update(api_prices)
        except Exception as e:
            print(f"⚠️ Error en APIs: {e}")
        
        # Estrategia 2: Scraping mejorado
        try:
            scraped_prices = await self._search_with_improved_scraping(product_name)
            for source, source_prices in scraped_prices.items():
                if source in prices:
                    prices[source].extend(source_prices)
        except Exception as e:
            print(f"⚠️ Error en scraping: {e}")
        
        # Estrategia 3: Google Shopping
        try:
            google_prices = await self._search_google_shopping(product_name)
            prices['google_shopping'] = google_prices
        except Exception as e:
            print(f"⚠️ Error en Google Shopping: {e}")
        
        # Calcular promedio y rango
        all_prices = []
        for source_prices in [prices['facebook_marketplace'], prices['ebay'], 
                            prices['mercadolibre_usado'], prices['google_shopping']]:
            all_prices.extend(source_prices)
        
        if all_prices:
            prices['average_resale_price'] = sum(all_prices) / len(all_prices)
            prices['price_range'] = f"${min(all_prices):,.0f} - ${max(all_prices):,.0f}"
            prices['confidence'] = 'high' if len(all_prices) >= 5 else 'medium' if len(all_prices) >= 2 else 'low'
        
        print(f"💰 Precio promedio de reventa: ${prices['average_resale_price']:,.0f}")
        return prices
    
    async def _search_with_apis(self, product_name: str) -> Dict[str, List[float]]:
        """Buscar usando APIs directas"""
        print("🌐 Buscando con APIs directas...")
        
        results = {
            'facebook_marketplace': [],
            'ebay': [],
            'mercadolibre_usado': []
        }
        
        # MercadoLibre API
        try:
            ml_url = f"https://api.mercadolibre.com/sites/MLM/search"
            params = {
                'q': f"{product_name} usado",
                'category': 'MLM1055',  # Electrónicos
                'limit': 10
            }
            response = self.session.get(ml_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                for item in data.get('results', [])[:5]:
                    price = item.get('price', 0)
                    if price and 100 <= price <= 100000:
                        results['mercadolibre_usado'].append(float(price))
                print(f"📊 MercadoLibre API: {len(results['mercadolibre_usado'])} precios")
        except Exception as e:
            print(f"❌ Error MercadoLibre API: {e}")
        
        return results
    
    async def _search_with_improved_scraping(self, product_name: str) -> Dict[str, List[float]]:
        """Scraping mejorado con mejor detección de elementos"""
        print("🌐 Buscando con scraping mejorado...")
        
        results = {
            'facebook_marketplace': [],
            'ebay': [],
            'mercadolibre_usado': []
        }
        
        async with self.browser_semaphore:
            try:
                async with async_playwright() as p:
                    browser = await p.chromium.launch(headless=True)
                    context = await browser.new_context(
                        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                    )
                    
                    # MercadoLibre mejorado
                    try:
                        page = await context.new_page()
                        search_query = f"{product_name} usado"
                        encoded_query = quote_plus(search_query)
                        url = f"https://listado.mercadolibre.com.mx/{encoded_query.replace('+', '-')}"
                        
                        print(f"🌐 MercadoLibre: {url}")
                        await page.goto(url, wait_until='domcontentloaded', timeout=15000)
                        await page.wait_for_timeout(3000)
                        
                        # Múltiples selectores para precios
                        price_selectors = [
                            '.ui-search-price__part',
                            '.price-tag-amount',
                            '.price-tag-fraction',
                            '[data-testid="price"]',
                            '.andes-money-amount__fraction'
                        ]
                        
                        for selector in price_selectors:
                            try:
                                elements = await page.query_selector_all(selector)
                                for element in elements[:5]:
                                    text = await element.text_content()
                                    if text:
                                        price_match = re.search(r'[\d,]+', text.replace('$', '').replace(',', ''))
                                        if price_match:
                                            price = float(price_match.group())
                                            if 100 <= price <= 100000:
                                                results['mercadolibre_usado'].append(price)
                            except:
                                continue
                        
                        print(f"📊 MercadoLibre scraping: {len(results['mercadolibre_usado'])} precios")
                        await page.close()
                        
                    except Exception as e:
                        print(f"❌ Error MercadoLibre scraping: {e}")
                    
                    # eBay mejorado
                    try:
                        page = await context.new_page()
                        search_query = f"{product_name} usado"
                        encoded_query = quote_plus(search_query)
                        url = f"https://www.ebay.com.mx/sch/i.html?_nkw={encoded_query}&_sacat=0&rt=nc&LH_Sold=1&LH_Complete=1"
                        
                        print(f"🌐 eBay: {url}")
                        await page.goto(url, wait_until='domcontentloaded', timeout=15000)
                        await page.wait_for_timeout(3000)
                        
                        # Múltiples selectores para eBay
                        price_selectors = [
                            '.s-item__price',
                            '.notranslate',
                            '.u-flL.condText',
                            '[data-testid="price"]'
                        ]
                        
                        for selector in price_selectors:
                            try:
                                elements = await page.query_selector_all(selector)
                                for element in elements[:5]:
                                    text = await element.text_content()
                                    if text:
                                        price_match = re.search(r'[\d,]+', text.replace('$', '').replace(',', ''))
                                        if price_match:
                                            price = float(price_match.group())
                                            if 100 <= price <= 100000:
                                                results['ebay'].append(price)
                            except:
                                continue
                        
                        print(f"📊 eBay scraping: {len(results['ebay'])} precios")
                        await page.close()
                        
                    except Exception as e:
                        print(f"❌ Error eBay scraping: {e}")
                    
                    await browser.close()
                    
            except Exception as e:
                print(f"❌ Error general en scraping: {e}")
        
        return results
    
    async def _search_google_shopping(self, product_name: str) -> List[float]:
        """Buscar en Google Shopping"""
        print("🌐 Buscando en Google Shopping...")
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                search_query = f"{product_name} usado precio"
                encoded_query = quote_plus(search_query)
                url = f"https://www.google.com/search?q={encoded_query}&tbm=shop"
                
                print(f"🌐 Google Shopping: {url}")
                await page.goto(url, wait_until='domcontentloaded', timeout=15000)
                await page.wait_for_timeout(3000)
                
                prices = []
                price_selectors = [
                    '.a8Pemb',
                    '.HlxIle',
                    '.a8Pemb',
                    '[data-testid="price"]'
                ]
                
                for selector in price_selectors:
                    try:
                        elements = await page.query_selector_all(selector)
                        for element in elements[:5]:
                            text = await element.text_content()
                            if text:
                                price_match = re.search(r'[\d,]+', text.replace('$', '').replace(',', ''))
                                if price_match:
                                    price = float(price_match.group())
                                    if 100 <= price <= 100000:
                                        prices.append(price)
                    except:
                        continue
                
                print(f"📊 Google Shopping: {len(prices)} precios")
                await browser.close()
                return prices
                
        except Exception as e:
            print(f"❌ Error Google Shopping: {e}")
            return []
    
    def analyze_price_opportunity(self, current_price: float, resale_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza si el precio actual representa una buena oportunidad de reventa"""
        avg_resale = resale_data.get('average_resale_price', 0)
        confidence = resale_data.get('confidence', 'low')
        
        if avg_resale == 0:
            return {
                'is_good_deal': False,
                'reasoning': 'No se encontraron precios de reventa',
                'profit_potential': 0,
                'confidence': 'low'
            }
        
        # Calcular potencial de ganancia
        profit_potential = avg_resale - current_price
        profit_percentage = (profit_potential / current_price) * 100 if current_price > 0 else 0
        
        # Determinar si es buena oportunidad
        is_good_deal = (
            profit_potential > 0 and 
            profit_percentage > 10 and  # Al menos 10% de ganancia
            confidence in ['high', 'medium']
        )
        
        reasoning = f"Precio actual: ${current_price:,.0f}, Reventa promedio: ${avg_resale:,.0f}, Ganancia potencial: ${profit_potential:,.0f} ({profit_percentage:.1f}%)"
        
        return {
            'is_good_deal': is_good_deal,
            'reasoning': reasoning,
            'profit_potential': profit_potential,
            'profit_percentage': profit_percentage,
            'confidence': confidence,
            'average_resale_price': avg_resale,
            'price_range': resale_data.get('price_range', 'N/A')
        }
