import asyncio
import re
import json
from typing import Dict, List, Any, Optional
from playwright.async_api import async_playwright
import requests
from urllib.parse import quote_plus

class RealPriceChecker:
    """Obtiene precios de reventa reales de Facebook Marketplace y eBay"""
    
    def __init__(self):
        self.browser_semaphore = asyncio.Semaphore(2)  # Limitar navegadores concurrentes
    
    async def get_resale_prices(self, product_name: str) -> Dict[str, Any]:
        """Obtiene precios de reventa reales de múltiples fuentes"""
        print(f"🔍 Investigando precios de reventa para: {product_name}")
        
        prices = {
            'facebook_marketplace': [],
            'ebay': [],
            'mercadolibre_usado': [],
            'average_resale_price': 0,
            'price_range': '',
            'confidence': 'low'
        }
        
        # Ejecutar búsquedas en paralelo
        tasks = [
            self._search_facebook_marketplace(product_name),
            self._search_ebay(product_name),
            self._search_mercadolibre_usado(product_name)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Procesar resultados
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"❌ Error en búsqueda {i}: {result}")
                continue
                
            if i == 0:  # Facebook
                prices['facebook_marketplace'] = result
            elif i == 1:  # eBay
                prices['ebay'] = result
            elif i == 2:  # MercadoLibre
                prices['mercadolibre_usado'] = result
        
        # Calcular promedio y rango
        all_prices = []
        for source_prices in [prices['facebook_marketplace'], prices['ebay'], prices['mercadolibre_usado']]:
            all_prices.extend(source_prices)
        
        if all_prices:
            prices['average_resale_price'] = sum(all_prices) / len(all_prices)
            prices['price_range'] = f"${min(all_prices):,.0f} - ${max(all_prices):,.0f}"
            prices['confidence'] = 'high' if len(all_prices) >= 3 else 'medium'
        
        print(f"💰 Precio promedio de reventa: ${prices['average_resale_price']:,.0f}")
        return prices
    
    async def _search_facebook_marketplace(self, product_name: str) -> List[float]:
        """Busca precios en Facebook Marketplace"""
        async with self.browser_semaphore:
            try:
                async with async_playwright() as p:
                    browser = await p.chromium.launch(headless=True)
                    page = await browser.new_page()
                    
                    # Buscar en Facebook Marketplace
                    search_query = f"{product_name} usado"
                    encoded_query = quote_plus(search_query)
                    url = f"https://www.facebook.com/marketplace/search/?query={encoded_query}"
                    
                    print(f"🌐 Buscando en Facebook Marketplace: {search_query}")
                    await page.goto(url, wait_until='domcontentloaded', timeout=15000)
                    await page.wait_for_timeout(3000)
                    
                    # Buscar elementos de precio
                    price_elements = await page.query_selector_all('[data-testid="marketplace-listing-price"]')
                    prices = []
                    
                    for element in price_elements[:5]:  # Limitar a 5 resultados
                        try:
                            price_text = await element.text_content()
                            if price_text:
                                # Extraer número del precio
                                price_match = re.search(r'[\d,]+', price_text.replace('$', '').replace(',', ''))
                                if price_match:
                                    price = float(price_match.group())
                                    if 100 <= price <= 100000:  # Filtrar precios razonables
                                        prices.append(price)
                        except Exception as e:
                            continue
                    
                    await browser.close()
                    print(f"📊 Facebook Marketplace: {len(prices)} precios encontrados")
                    return prices
                    
            except Exception as e:
                print(f"❌ Error en Facebook Marketplace: {e}")
                return []
    
    async def _search_ebay(self, product_name: str) -> List[float]:
        """Busca precios en eBay"""
        async with self.browser_semaphore:
            try:
                async with async_playwright() as p:
                    browser = await p.chromium.launch(headless=True)
                    page = await browser.new_page()
                    
                    # Buscar en eBay México
                    search_query = f"{product_name} usado"
                    encoded_query = quote_plus(search_query)
                    url = f"https://www.ebay.com.mx/sch/i.html?_nkw={encoded_query}&_sacat=0&rt=nc&LH_Sold=1&LH_Complete=1"
                    
                    print(f"🌐 Buscando en eBay: {search_query}")
                    await page.goto(url, wait_until='domcontentloaded', timeout=15000)
                    await page.wait_for_timeout(3000)
                    
                    # Buscar elementos de precio
                    price_elements = await page.query_selector_all('.s-item__price')
                    prices = []
                    
                    for element in price_elements[:5]:  # Limitar a 5 resultados
                        try:
                            price_text = await element.text_content()
                            if price_text:
                                # Extraer número del precio
                                price_match = re.search(r'[\d,]+', price_text.replace('$', '').replace(',', ''))
                                if price_match:
                                    price = float(price_match.group())
                                    if 100 <= price <= 100000:  # Filtrar precios razonables
                                        prices.append(price)
                        except Exception as e:
                            continue
                    
                    await browser.close()
                    print(f"📊 eBay: {len(prices)} precios encontrados")
                    return prices
                    
            except Exception as e:
                print(f"❌ Error en eBay: {e}")
                return []
    
    async def _search_mercadolibre_usado(self, product_name: str) -> List[float]:
        """Busca precios en MercadoLibre (usado)"""
        async with self.browser_semaphore:
            try:
                async with async_playwright() as p:
                    browser = await p.chromium.launch(headless=True)
                    page = await browser.new_page()
                    
                    # Buscar en MercadoLibre con filtro de usado
                    search_query = f"{product_name} usado"
                    encoded_query = quote_plus(search_query)
                    url = f"https://listado.mercadolibre.com.mx/{encoded_query.replace('+', '-')}"
                    
                    print(f"🌐 Buscando en MercadoLibre: {search_query}")
                    await page.goto(url, wait_until='domcontentloaded', timeout=15000)
                    await page.wait_for_timeout(3000)
                    
                    # Buscar elementos de precio
                    price_elements = await page.query_selector_all('.ui-search-price__part')
                    prices = []
                    
                    for element in price_elements[:5]:  # Limitar a 5 resultados
                        try:
                            price_text = await element.text_content()
                            if price_text:
                                # Extraer número del precio
                                price_match = re.search(r'[\d,]+', price_text.replace('$', '').replace(',', ''))
                                if price_match:
                                    price = float(price_match.group())
                                    if 100 <= price <= 100000:  # Filtrar precios razonables
                                        prices.append(price)
                        except Exception as e:
                            continue
                    
                    await browser.close()
                    print(f"📊 MercadoLibre: {len(prices)} precios encontrados")
                    return prices
                    
            except Exception as e:
                print(f"❌ Error en MercadoLibre: {e}")
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
