#!/usr/bin/env python3
"""
Free APIs and improved scraping without API keys
"""

import requests
import asyncio
import aiohttp
from typing import List, Dict, Any, Optional
import json
import time
from playwright.async_api import async_playwright
import random

class FreeAPIClient:
    """Free API client that doesn't require API keys"""
    
    def __init__(self):
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def search_mercadolibre_free(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search MercadoLibre using scraping (API blocked)"""
        try:
            print(f"🔍 MercadoLibre Scraping: Searching for '{query}'")
            
            async with async_playwright() as playwright:
                browser = await playwright.chromium.launch(
                    headless=True,
                    args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
                )
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    viewport={'width': 1920, 'height': 1080},
                    locale='es-MX'
                )
                page = await context.new_page()
                
                try:
                    # MercadoLibre search URL
                    search_url = f"https://listado.mercadolibre.com.mx/{query.replace(' ', '-')}"
                    print(f"🌐 Navigating to: {search_url}")
                    
                    await page.goto(search_url, wait_until='domcontentloaded', timeout=30000)
                    await page.wait_for_timeout(5000)
                    
                    # Wait for products with multiple selectors
                    product_selectors = [
                        '.ui-search-layout__item',
                        '.ui-search-item',
                        '.ui-search-results .ui-search-item',
                        '[data-testid="product"]',
                        '.item',
                        '.ui-search-item__wrapper'
                    ]
                    
                    products_found = False
                    product_elements = []
                    
                    for selector in product_selectors:
                        try:
                            await page.wait_for_selector(selector, timeout=5000)
                            product_elements = await page.query_selector_all(selector)
                            if product_elements:
                                print(f"📦 Found {len(product_elements)} products with selector: {selector}")
                                products_found = True
                                break
                        except:
                            continue
                    
                    if not products_found:
                        print("❌ No products found with any selector")
                        return []
                    
                    products = []
                    for element in product_elements[:limit]:
                        try:
                            # Extract product data with updated selectors
                            # Get name from image title or text content
                            name = None
                            
                            # Try image title first
                            img_elem = await element.query_selector('img')
                            if img_elem:
                                name = await img_elem.get_attribute('title')
                                if name and len(name.strip()) > 5:
                                    pass  # Use this name
                                else:
                                    name = await img_elem.get_attribute('alt')
                            
                            # If no name from image, try text content
                            if not name or len(name.strip()) <= 5:
                                all_text = await element.inner_text()
                                lines = all_text.split('\n')
                                for line in lines:
                                    if line.strip() and len(line.strip()) > 10 and not line.strip().startswith('$'):
                                        name = line.strip()
                                        break
                            
                            if not name or len(name.strip()) <= 5:
                                continue
                            
                            # Extract price from text content
                            price = None
                            all_text = await element.inner_text()
                            
                            # Look for price patterns
                            import re
                            price_patterns = [
                                r'\$\s*[\d,]+',
                                r'[\d,]+\s*pesos',
                                r'[\d,]+\s*MXN'
                            ]
                            
                            for pattern in price_patterns:
                                matches = re.findall(pattern, all_text)
                                if matches:
                                    price = matches[0]
                                    break
                            
                            # If no pattern match, look for $ followed by numbers
                            if not price:
                                lines = all_text.split('\n')
                                for line in lines:
                                    if '$' in line and any(char.isdigit() for char in line):
                                        price = line.strip()
                                        break
                            
                            if not price:
                                continue
                            
                            # URL extraction
                            link_selectors = ['a', '.ui-search-link', '[data-testid="product-link"]']
                            url = ''
                            for link_sel in link_selectors:
                                try:
                                    link_elem = await element.query_selector(link_sel)
                                    if link_elem:
                                        url = await link_elem.get_attribute('href')
                                        if url:
                                            break
                                except:
                                    continue
                            
                            # Image extraction
                            img_elem = await element.query_selector('img')
                            image = await img_elem.get_attribute('src') if img_elem else ''
                            
                            product = {
                                'name': name.strip(),
                                'price': price.strip(),
                                'url': url if url else '',
                                'image': image,
                                'site': 'MercadoLibre'
                            }
                            products.append(product)
                                
                        except Exception as e:
                            print(f"⚠️ Error processing MercadoLibre product: {e}")
                            continue
                    
                    print(f"✅ MercadoLibre Scraping: Found {len(products)} products")
                    return products
                    
                except Exception as e:
                    print(f"❌ MercadoLibre Scraping error: {e}")
                    return []
                finally:
                    await browser.close()
                    
        except Exception as e:
            print(f"❌ MercadoLibre Scraping error: {e}")
            return []
    
    async def search_amazon_improved_scraping(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Improved Amazon scraping with better selectors"""
        try:
            print(f"🔍 Amazon Improved: Searching for '{query}'")
            
            async with async_playwright() as playwright:
                browser = await playwright.chromium.launch(
                    headless=True,
                    args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
                )
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    viewport={'width': 1920, 'height': 1080},
                    locale='es-MX'
                )
                page = await context.new_page()
                
                try:
                    # Amazon search URL
                    search_url = f"https://www.amazon.com.mx/s?k={query.replace(' ', '+')}"
                    print(f"🌐 Navigating to: {search_url}")
                    
                    await page.goto(search_url, wait_until='domcontentloaded', timeout=30000)
                    await page.wait_for_timeout(5000)
                    
                    # Wait for products to load with multiple selectors
                    product_selectors = [
                        '[data-component-type="s-search-result"]',
                        '.s-result-item',
                        '[data-asin]',
                        '.s-card-container'
                    ]
                    
                    products_found = False
                    product_elements = []
                    
                    for selector in product_selectors:
                        try:
                            await page.wait_for_selector(selector, timeout=5000)
                            product_elements = await page.query_selector_all(selector)
                            if product_elements:
                                print(f"📦 Found {len(product_elements)} products with selector: {selector}")
                                products_found = True
                                break
                        except:
                            continue
                    
                    if not products_found:
                        print("❌ No products found with any selector")
                        return []
                    
                    products = []
                    for element in product_elements[:limit]:
                        try:
                            # Extract product data with multiple selectors
                            name_selectors = [
                                'h2 a span',
                                'h2 span',
                                '.s-size-mini span',
                                'h2',
                                '.s-link-style',
                                '[data-cy="title-recipe-title"]',
                                '.s-title-instructions-style'
                            ]
                            
                            name = None
                            for selector in name_selectors:
                                try:
                                    name_elem = await element.query_selector(selector)
                                    if name_elem:
                                        name = await name_elem.inner_text()
                                        if name and len(name.strip()) > 10:
                                            break
                                except:
                                    continue
                            
                            if not name:
                                continue
                            
                            # Price extraction with more selectors
                            price_selectors = [
                                '.a-price-whole',
                                '.a-price .a-offscreen',
                                '.a-price-range',
                                '.a-price-symbol',
                                '[data-a-price-amount]',
                                '.a-price',
                                '.a-offscreen'
                            ]
                            
                            price = None
                            for selector in price_selectors:
                                try:
                                    price_elem = await element.query_selector(selector)
                                    if price_elem:
                                        price = await price_elem.inner_text()
                                        if price and ('$' in price or 'MXN' in price or price.replace('.', '').replace(',', '').isdigit()):
                                            break
                                except:
                                    continue
                            
                            if not price:
                                continue
                            
                            # URL extraction
                            link_elem = await element.query_selector('h2 a')
                            url = await link_elem.get_attribute('href') if link_elem else ''
                            
                            # Image extraction
                            img_elem = await element.query_selector('img')
                            image = await img_elem.get_attribute('src') if img_elem else ''
                            
                            product = {
                                'name': name.strip(),
                                'price': price.strip(),
                                'url': f"https://www.amazon.com.mx{url}" if url else '',
                                'image': image,
                                'site': 'Amazon'
                            }
                            products.append(product)
                            
                        except Exception as e:
                            print(f"⚠️ Error processing Amazon product: {e}")
                            continue
                    
                    print(f"✅ Amazon Improved: Found {len(products)} products")
                    return products
                    
                except Exception as e:
                    print(f"❌ Amazon Improved error: {e}")
                    return []
                finally:
                    await browser.close()
                    
        except Exception as e:
            print(f"❌ Amazon Improved error: {e}")
            return []
    
    async def search_walmart_improved_scraping(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Improved Walmart scraping with updated selectors"""
        try:
            print(f"🔍 Walmart Improved: Searching for '{query}'")
            
            async with async_playwright() as playwright:
                browser = await playwright.chromium.launch(
                    headless=True,
                    args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
                )
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    viewport={'width': 1920, 'height': 1080},
                    locale='es-MX'
                )
                page = await context.new_page()
                
                try:
                    # Walmart search URL
                    search_url = f"https://www.walmart.com.mx/search?q={query.replace(' ', '+')}"
                    print(f"🌐 Navigating to: {search_url}")
                    
                    await page.goto(search_url, wait_until='domcontentloaded', timeout=30000)
                    await page.wait_for_timeout(5000)
                    
                    # Try to find products with multiple strategies
                    products = []
                    
                    # Strategy 1: Look for product cards
                    product_selectors = [
                        '[data-automation-id="product-title"]',
                        '.product-title',
                        '.item-title',
                        '[data-testid="product-title"]',
                        '.product-item',
                        '.item',
                        '.product',
                        '[data-testid="product"]',
                        '.product-card',
                        '.search-result-item'
                    ]
                    
                    product_elements = []
                    for selector in product_selectors:
                        try:
                            elements = await page.query_selector_all(selector)
                            if elements:
                                print(f"📦 Found {len(elements)} products with selector: {selector}")
                                product_elements = elements
                                break
                        except:
                            continue
                    
                    if not product_elements:
                        # Strategy 2: Look for any elements with product-like content
                        all_elements = await page.query_selector_all('*')
                        for element in all_elements[:100]:  # Check first 100 elements
                            try:
                                text = await element.inner_text()
                                if text and len(text) > 20 and ('$' in text or 'peso' in text.lower()):
                                    product_elements.append(element)
                                    if len(product_elements) >= 10:  # Limit to 10
                                        break
                            except:
                                continue
                    
                    if not product_elements:
                        print("❌ No products found with any strategy")
                        return []
                    
                    # Extract products
                    for element in product_elements[:limit]:
                        try:
                            # Get all text content
                            all_text = await element.inner_text()
                            
                            # Extract name (first meaningful line)
                            lines = all_text.split('\n')
                            name = None
                            for line in lines:
                                line = line.strip()
                                if line and len(line) > 10 and not line.startswith('$') and not line.startswith('peso'):
                                    name = line
                                    break
                            
                            if not name:
                                continue
                            
                            # Extract price using regex
                            import re
                            price_patterns = [
                                r'\$\s*[\d,]+',
                                r'[\d,]+\s*pesos',
                                r'[\d,]+\s*MXN'
                            ]
                            
                            price = None
                            for pattern in price_patterns:
                                matches = re.findall(pattern, all_text)
                                if matches:
                                    price = matches[0]
                                    break
                            
                            # If no pattern match, look for $ followed by numbers
                            if not price:
                                for line in lines:
                                    if '$' in line and any(char.isdigit() for char in line):
                                        price = line.strip()
                                        break
                            
                            if not price:
                                continue
                            
                            # Find URL
                            link_elem = await element.query_selector('a')
                            url = await link_elem.get_attribute('href') if link_elem else ''
                            
                            # Find image
                            img_elem = await element.query_selector('img')
                            image = await img_elem.get_attribute('src') if img_elem else ''
                            
                            product = {
                                'name': name.strip(),
                                'price': price.strip(),
                                'url': f"https://www.walmart.com.mx{url}" if url else '',
                                'image': image,
                                'site': 'Walmart'
                            }
                            products.append(product)
                                
                        except Exception as e:
                            print(f"⚠️ Error processing Walmart product: {e}")
                            continue
                    
                    print(f"✅ Walmart Improved: Found {len(products)} products")
                    return products
                    
                except Exception as e:
                    print(f"❌ Walmart Improved error: {e}")
                    return []
                finally:
                    await browser.close()
                    
        except Exception as e:
            print(f"❌ Walmart Improved error: {e}")
            return []
    
    async def search_liverpool_improved_scraping(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Improved Liverpool scraping with updated selectors"""
        try:
            print(f"🔍 Liverpool Improved: Searching for '{query}'")
            
            async with async_playwright() as playwright:
                browser = await playwright.chromium.launch(
                    headless=True,
                    args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
                )
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    viewport={'width': 1920, 'height': 1080},
                    locale='es-MX'
                )
                page = await context.new_page()
                
                try:
                    # Liverpool search URL - try different approaches
                    search_urls = [
                        f"https://www.liverpool.com.mx/tienda/home/search?text={query.replace(' ', '%20')}",
                        f"https://www.liverpool.com.mx/search?q={query.replace(' ', '+')}",
                        f"https://www.liverpool.com.mx/tienda/home/search?q={query.replace(' ', '+')}",
                        f"https://www.liverpool.com.mx/search?query={query.replace(' ', '+')}",
                        f"https://www.liverpool.com.mx/tienda/search?q={query.replace(' ', '+')}"
                    ]
                    
                    # Try each URL until one works
                    for search_url in search_urls:
                        try:
                            print(f"🌐 Trying Liverpool URL: {search_url}")
                            await page.goto(search_url, wait_until='domcontentloaded', timeout=15000)
                            await page.wait_for_timeout(8000)  # Wait longer for JS to load
                            
                            # Check if page loaded successfully
                            title = await page.title()
                            if "Liverpool" in title or "producto" in title.lower():
                                print(f"✅ Liverpool page loaded: {title}")
                                
                                # Wait for products to load dynamically
                                try:
                                    await page.wait_for_selector('.product-item, .item, .product, .product-card', timeout=10000)
                                    print("✅ Liverpool products loaded dynamically")
                                except:
                                    print("⚠️ Liverpool products not loaded dynamically, trying anyway...")
                                break
                        except Exception as e:
                            print(f"❌ Liverpool URL failed: {e}")
                            continue
                    
                    # Try to find products with multiple strategies
                    products = []
                    
                    # Strategy 1: Look for product cards with more selectors
                    product_selectors = [
                        '.product-item',
                        '.product-card',
                        '.item',
                        '[data-testid="product-item"]',
                        '.product',
                        '.product-tile',
                        '.tile-product',
                        '.product-tile-item',
                        '.product-grid-item',
                        '.grid-item',
                        '.search-result-item',
                        '.product-list-item',
                        '.item-product',
                        '.product-container'
                    ]
                    
                    product_elements = []
                    for selector in product_selectors:
                        try:
                            elements = await page.query_selector_all(selector)
                            if elements:
                                print(f"📦 Found {len(elements)} products with selector: {selector}")
                                product_elements = elements
                                break
                        except:
                            continue
                    
                    if not product_elements:
                        # Strategy 2: Look for any elements with product-like content
                        print("🔍 Liverpool trying fallback strategy...")
                        all_elements = await page.query_selector_all('*')
                        for element in all_elements[:300]:  # Check even more elements
                            try:
                                text = await element.inner_text()
                                if text and len(text) > 20 and ('$' in text or 'peso' in text.lower() or 'precio' in text.lower() or 'iPhone' in text or 'producto' in text.lower()):
                                    product_elements.append(element)
                                    if len(product_elements) >= 20:  # Even more products
                                        break
                            except:
                                continue
                    
                    if not product_elements:
                        # Strategy 3: Try to find any clickable elements that might be products
                        print("🔍 Liverpool trying clickable elements strategy...")
                        clickable_elements = await page.query_selector_all('a, button, [onclick], [data-testid]')
                        for element in clickable_elements[:100]:
                            try:
                                text = await element.inner_text()
                                if text and len(text) > 10 and ('$' in text or 'iPhone' in text or 'producto' in text.lower()):
                                    product_elements.append(element)
                                    if len(product_elements) >= 10:
                                        break
                            except:
                                continue
                    
                    if not product_elements:
                        print("❌ Liverpool: No products found with any strategy")
                        return []
                    
                    # Extract products
                    for element in product_elements[:limit]:
                        try:
                            # Get all text content
                            all_text = await element.inner_text()
                            
                            # Extract name (first meaningful line)
                            lines = all_text.split('\n')
                            name = None
                            for line in lines:
                                line = line.strip()
                                if line and len(line) > 10 and not line.startswith('$') and not line.startswith('peso'):
                                    name = line
                                    break
                            
                            if not name:
                                continue
                            
                            # Extract price using regex
                            import re
                            price_patterns = [
                                r'\$\s*[\d,]+',
                                r'[\d,]+\s*pesos',
                                r'[\d,]+\s*MXN'
                            ]
                            
                            price = None
                            for pattern in price_patterns:
                                matches = re.findall(pattern, all_text)
                                if matches:
                                    price = matches[0]
                                    break
                            
                            # If no pattern match, look for $ followed by numbers
                            if not price:
                                for line in lines:
                                    if '$' in line and any(char.isdigit() for char in line):
                                        price = line.strip()
                                        break
                            
                            if not price:
                                continue
                            
                            # Find URL
                            link_elem = await element.query_selector('a')
                            url = await link_elem.get_attribute('href') if link_elem else ''
                            
                            # Find image
                            img_elem = await element.query_selector('img')
                            image = await img_elem.get_attribute('src') if img_elem else ''
                            
                            product = {
                                'name': name.strip(),
                                'price': price.strip(),
                                'url': f"https://www.liverpool.com.mx{url}" if url else '',
                                'image': image,
                                'site': 'Liverpool'
                            }
                            products.append(product)
                                
                        except Exception as e:
                            print(f"⚠️ Error processing Liverpool product: {e}")
                            continue
                    
                    print(f"✅ Liverpool Improved: Found {len(products)} products")
                    return products
                    
                except Exception as e:
                    print(f"❌ Liverpool Improved error: {e}")
                    return []
                finally:
                    await browser.close()
                    
        except Exception as e:
            print(f"❌ Liverpool Improved error: {e}")
            return []
    
    async def search_coppel_scraping(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Coppel scraping"""
        try:
            print(f"🔍 Coppel: Searching for '{query}'")
            
            async with async_playwright() as playwright:
                browser = await playwright.chromium.launch(
                    headless=True,
                    args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
                )
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    viewport={'width': 1920, 'height': 1080},
                    locale='es-MX'
                )
                page = await context.new_page()
                
                try:
                    search_url = f"https://www.coppel.com/buscar?q={query.replace(' ', '+')}"
                    print(f"🌐 Navigating to: {search_url}")
                    
                    await page.goto(search_url, wait_until='domcontentloaded', timeout=30000)
                    await page.wait_for_timeout(5000)
                    
                    # Look for products
                    product_elements = []
                    selectors = ['.product-item', '.item', '.product', '.product-card']
                    
                    for selector in selectors:
                        try:
                            elements = await page.query_selector_all(selector)
                            if elements:
                                product_elements = elements
                                break
                        except:
                            continue
                    
                    if not product_elements:
                        # Fallback: look for elements with price content
                        all_elements = await page.query_selector_all('*')
                        for element in all_elements[:50]:
                            try:
                                text = await element.inner_text()
                                if text and len(text) > 20 and ('$' in text or 'peso' in text.lower()):
                                    product_elements.append(element)
                                    if len(product_elements) >= 10:
                                        break
                            except:
                                continue
                    
                    products = []
                    for element in product_elements[:limit]:
                        try:
                            all_text = await element.inner_text()
                            lines = all_text.split('\n')
                            
                            # Extract name
                            name = None
                            for line in lines:
                                line = line.strip()
                                if line and len(line) > 10 and not line.startswith('$'):
                                    name = line
                                    break
                            
                            if not name:
                                continue
                            
                            # Extract price
                            import re
                            price = None
                            for line in lines:
                                if '$' in line and any(char.isdigit() for char in line):
                                    price = line.strip()
                                    break
                            
                            if not price:
                                continue
                            
                            # Find URL and image
                            link_elem = await element.query_selector('a')
                            url = await link_elem.get_attribute('href') if link_elem else ''
                            
                            img_elem = await element.query_selector('img')
                            image = await img_elem.get_attribute('src') if img_elem else ''
                            
                            product = {
                                'name': name.strip(),
                                'price': price.strip(),
                                'url': f"https://www.coppel.com{url}" if url else '',
                                'image': image,
                                'site': 'Coppel'
                            }
                            products.append(product)
                                
                        except Exception as e:
                            continue
                    
                    print(f"✅ Coppel: Found {len(products)} products")
                    return products
                    
                except Exception as e:
                    print(f"❌ Coppel error: {e}")
                    return []
                finally:
                    await browser.close()
                    
        except Exception as e:
            print(f"❌ Coppel error: {e}")
            return []
    
    async def search_elektra_scraping(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Elektra scraping"""
        try:
            print(f"🔍 Elektra: Searching for '{query}'")
            
            async with async_playwright() as playwright:
                browser = await playwright.chromium.launch(
                    headless=True,
                    args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
                )
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    viewport={'width': 1920, 'height': 1080},
                    locale='es-MX'
                )
                page = await context.new_page()
                
                try:
                    search_url = f"https://www.elektra.com.mx/buscar?q={query.replace(' ', '+')}"
                    print(f"🌐 Navigating to: {search_url}")
                    
                    await page.goto(search_url, wait_until='domcontentloaded', timeout=30000)
                    await page.wait_for_timeout(5000)
                    
                    # Look for products
                    product_elements = []
                    selectors = ['.product-item', '.item', '.product', '.product-card']
                    
                    for selector in selectors:
                        try:
                            elements = await page.query_selector_all(selector)
                            if elements:
                                product_elements = elements
                                break
                        except:
                            continue
                    
                    if not product_elements:
                        # Fallback: look for elements with price content
                        all_elements = await page.query_selector_all('*')
                        for element in all_elements[:50]:
                            try:
                                text = await element.inner_text()
                                if text and len(text) > 20 and ('$' in text or 'peso' in text.lower()):
                                    product_elements.append(element)
                                    if len(product_elements) >= 10:
                                        break
                            except:
                                continue
                    
                    products = []
                    for element in product_elements[:limit]:
                        try:
                            all_text = await element.inner_text()
                            lines = all_text.split('\n')
                            
                            # Extract name
                            name = None
                            for line in lines:
                                line = line.strip()
                                if line and len(line) > 10 and not line.startswith('$'):
                                    name = line
                                    break
                            
                            if not name:
                                continue
                            
                            # Extract price
                            price = None
                            for line in lines:
                                if '$' in line and any(char.isdigit() for char in line):
                                    price = line.strip()
                                    break
                            
                            if not price:
                                continue
                            
                            # Find URL and image
                            link_elem = await element.query_selector('a')
                            url = await link_elem.get_attribute('href') if link_elem else ''
                            
                            img_elem = await element.query_selector('img')
                            image = await img_elem.get_attribute('src') if img_elem else ''
                            
                            product = {
                                'name': name.strip(),
                                'price': price.strip(),
                                'url': f"https://www.elektra.com.mx{url}" if url else '',
                                'image': image,
                                'site': 'Elektra'
                            }
                            products.append(product)
                                
                        except Exception as e:
                            continue
                    
                    print(f"✅ Elektra: Found {len(products)} products")
                    return products
                    
                except Exception as e:
                    print(f"❌ Elektra error: {e}")
                    return []
                finally:
                    await browser.close()
                    
        except Exception as e:
            print(f"❌ Elektra error: {e}")
            return []
    
    async def search_aurrera_scraping(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Aurrera scraping"""
        try:
            print(f"🔍 Aurrera: Searching for '{query}'")
            
            async with async_playwright() as playwright:
                browser = await playwright.chromium.launch(
                    headless=True,
                    args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
                )
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    viewport={'width': 1920, 'height': 1080},
                    locale='es-MX'
                )
                page = await context.new_page()
                
                try:
                    # Try different Aurrera URLs
                    search_urls = [
                        f"https://www.aurrera.com.mx/search?q={query.replace(' ', '+')}",
                        f"https://www.aurrera.com.mx/buscar?q={query.replace(' ', '+')}",
                        f"https://www.aurrera.com.mx/tienda/search?q={query.replace(' ', '+')}",
                        f"https://www.aurrera.com.mx/search?query={query.replace(' ', '+')}",
                        f"https://www.aurrera.com.mx/search?text={query.replace(' ', '+')}"
                    ]
                    
                    for search_url in search_urls:
                        try:
                            print(f"🌐 Trying Aurrera URL: {search_url}")
                            await page.goto(search_url, wait_until='domcontentloaded', timeout=15000)
                            await page.wait_for_timeout(3000)
                            
                            # Check if page loaded
                            title = await page.title()
                            if "Aurrera" in title or "Walmart" in title:
                                print(f"✅ Aurrera page loaded: {title}")
                                break
                        except Exception as e:
                            print(f"❌ Aurrera URL failed: {e}")
                            continue
                    
                    # Look for products
                    product_elements = []
                    selectors = ['.product-item', '.item', '.product', '.product-card']
                    
                    for selector in selectors:
                        try:
                            elements = await page.query_selector_all(selector)
                            if elements:
                                product_elements = elements
                                break
                        except:
                            continue
                    
                    if not product_elements:
                        # Fallback: look for elements with price content
                        all_elements = await page.query_selector_all('*')
                        for element in all_elements[:50]:
                            try:
                                text = await element.inner_text()
                                if text and len(text) > 20 and ('$' in text or 'peso' in text.lower()):
                                    product_elements.append(element)
                                    if len(product_elements) >= 10:
                                        break
                            except:
                                continue
                    
                    products = []
                    for element in product_elements[:limit]:
                        try:
                            all_text = await element.inner_text()
                            lines = all_text.split('\n')
                            
                            # Extract name
                            name = None
                            for line in lines:
                                line = line.strip()
                                if line and len(line) > 10 and not line.startswith('$'):
                                    name = line
                                    break
                            
                            if not name:
                                continue
                            
                            # Extract price
                            price = None
                            for line in lines:
                                if '$' in line and any(char.isdigit() for char in line):
                                    price = line.strip()
                                    break
                            
                            if not price:
                                continue
                            
                            # Find URL and image
                            link_elem = await element.query_selector('a')
                            url = await link_elem.get_attribute('href') if link_elem else ''
                            
                            img_elem = await element.query_selector('img')
                            image = await img_elem.get_attribute('src') if img_elem else ''
                            
                            product = {
                                'name': name.strip(),
                                'price': price.strip(),
                                'url': f"https://www.aurrera.com.mx{url}" if url else '',
                                'image': image,
                                'site': 'Aurrera'
                            }
                            products.append(product)
                                
                        except Exception as e:
                            continue
                    
                    print(f"✅ Aurrera: Found {len(products)} products")
                    return products
                    
                except Exception as e:
                    print(f"❌ Aurrera error: {e}")
                    return []
                finally:
                    await browser.close()
                    
        except Exception as e:
            print(f"❌ Aurrera error: {e}")
            return []
    
    async def search_costco_scraping(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Costco scraping"""
        try:
            print(f"🔍 Costco: Searching for '{query}'")
            
            async with async_playwright() as playwright:
                browser = await playwright.chromium.launch(
                    headless=True,
                    args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
                )
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    viewport={'width': 1920, 'height': 1080},
                    locale='es-MX'
                )
                page = await context.new_page()
                
                try:
                    # Try different Costco URLs
                    search_urls = [
                        f"https://www.costco.com.mx/search?keyword={query.replace(' ', '+')}",
                        f"https://www.costco.com.mx/search?q={query.replace(' ', '+')}",
                        f"https://www.costco.com.mx/search?text={query.replace(' ', '+')}",
                        f"https://www.costco.com.mx/search?query={query.replace(' ', '+')}",
                        f"https://www.costco.com.mx/search?search={query.replace(' ', '+')}"
                    ]
                    
                    for search_url in search_urls:
                        try:
                            print(f"🌐 Trying Costco URL: {search_url}")
                            await page.goto(search_url, wait_until='domcontentloaded', timeout=15000)
                            await page.wait_for_timeout(3000)
                            
                            # Check if page loaded
                            title = await page.title()
                            if "Costco" in title or "producto" in title.lower():
                                print(f"✅ Costco page loaded: {title}")
                                break
                        except Exception as e:
                            print(f"❌ Costco URL failed: {e}")
                            continue
                    
                    # Look for products
                    product_elements = []
                    selectors = ['.product-item', '.item', '.product', '.product-card']
                    
                    for selector in selectors:
                        try:
                            elements = await page.query_selector_all(selector)
                            if elements:
                                product_elements = elements
                                break
                        except:
                            continue
                    
                    if not product_elements:
                        # Fallback: look for elements with price content
                        all_elements = await page.query_selector_all('*')
                        for element in all_elements[:50]:
                            try:
                                text = await element.inner_text()
                                if text and len(text) > 20 and ('$' in text or 'peso' in text.lower()):
                                    product_elements.append(element)
                                    if len(product_elements) >= 10:
                                        break
                            except:
                                continue
                    
                    products = []
                    for element in product_elements[:limit]:
                        try:
                            all_text = await element.inner_text()
                            lines = all_text.split('\n')
                            
                            # Extract name
                            name = None
                            for line in lines:
                                line = line.strip()
                                if line and len(line) > 10 and not line.startswith('$'):
                                    name = line
                                    break
                            
                            if not name:
                                continue
                            
                            # Extract price
                            price = None
                            for line in lines:
                                if '$' in line and any(char.isdigit() for char in line):
                                    price = line.strip()
                                    break
                            
                            if not price:
                                continue
                            
                            # Find URL and image
                            link_elem = await element.query_selector('a')
                            url = await link_elem.get_attribute('href') if link_elem else ''
                            
                            img_elem = await element.query_selector('img')
                            image = await img_elem.get_attribute('src') if img_elem else ''
                            
                            product = {
                                'name': name.strip(),
                                'price': price.strip(),
                                'url': f"https://www.costco.com.mx{url}" if url else '',
                                'image': image,
                                'site': 'Costco'
                            }
                            products.append(product)
                                
                        except Exception as e:
                            continue
                    
                    print(f"✅ Costco: Found {len(products)} products")
                    return products
                    
                except Exception as e:
                    print(f"❌ Costco error: {e}")
                    return []
                finally:
                    await browser.close()
                    
        except Exception as e:
            print(f"❌ Costco error: {e}")
            return []
    
    async def search_sams_scraping(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Sams scraping"""
        try:
            print(f"🔍 Sams: Searching for '{query}'")
            
            async with async_playwright() as playwright:
                browser = await playwright.chromium.launch(
                    headless=True,
                    args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
                )
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    viewport={'width': 1920, 'height': 1080},
                    locale='es-MX'
                )
                page = await context.new_page()
                
                try:
                    search_url = f"https://www.sams.com.mx/search?q={query.replace(' ', '+')}"
                    print(f"🌐 Navigating to: {search_url}")
                    
                    await page.goto(search_url, wait_until='domcontentloaded', timeout=30000)
                    await page.wait_for_timeout(5000)
                    
                    # Look for products
                    product_elements = []
                    selectors = ['.product-item', '.item', '.product', '.product-card']
                    
                    for selector in selectors:
                        try:
                            elements = await page.query_selector_all(selector)
                            if elements:
                                product_elements = elements
                                break
                        except:
                            continue
                    
                    if not product_elements:
                        # Fallback: look for elements with price content
                        all_elements = await page.query_selector_all('*')
                        for element in all_elements[:50]:
                            try:
                                text = await element.inner_text()
                                if text and len(text) > 20 and ('$' in text or 'peso' in text.lower()):
                                    product_elements.append(element)
                                    if len(product_elements) >= 10:
                                        break
                            except:
                                continue
                    
                    products = []
                    for element in product_elements[:limit]:
                        try:
                            all_text = await element.inner_text()
                            lines = all_text.split('\n')
                            
                            # Extract name
                            name = None
                            for line in lines:
                                line = line.strip()
                                if line and len(line) > 10 and not line.startswith('$'):
                                    name = line
                                    break
                            
                            if not name:
                                continue
                            
                            # Extract price
                            price = None
                            for line in lines:
                                if '$' in line and any(char.isdigit() for char in line):
                                    price = line.strip()
                                    break
                            
                            if not price:
                                continue
                            
                            # Find URL and image
                            link_elem = await element.query_selector('a')
                            url = await link_elem.get_attribute('href') if link_elem else ''
                            
                            img_elem = await element.query_selector('img')
                            image = await img_elem.get_attribute('src') if img_elem else ''
                            
                            product = {
                                'name': name.strip(),
                                'price': price.strip(),
                                'url': f"https://www.sams.com.mx{url}" if url else '',
                                'image': image,
                                'site': 'Sams'
                            }
                            products.append(product)
                                
                        except Exception as e:
                            continue
                    
                    print(f"✅ Sams: Found {len(products)} products")
                    return products
                    
                except Exception as e:
                    print(f"❌ Sams error: {e}")
                    return []
                finally:
                    await browser.close()
                    
        except Exception as e:
            print(f"❌ Sams error: {e}")
            return []
    
    async def search_samsung_scraping(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Samsung scraping"""
        try:
            print(f"🔍 Samsung: Searching for '{query}'")
            
            async with async_playwright() as playwright:
                browser = await playwright.chromium.launch(
                    headless=True,
                    args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
                )
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    viewport={'width': 1920, 'height': 1080},
                    locale='es-MX'
                )
                page = await context.new_page()
                
                try:
                    # Try different Samsung URLs
                    search_urls = [
                        f"https://www.samsung.com/mx/search/?searchvalue={query.replace(' ', '+')}",
                        f"https://www.samsung.com/mx/search?q={query.replace(' ', '+')}",
                        f"https://www.samsung.com/mx/search?query={query.replace(' ', '+')}"
                    ]
                    
                    for search_url in search_urls:
                        try:
                            print(f"🌐 Trying Samsung URL: {search_url}")
                            await page.goto(search_url, wait_until='domcontentloaded', timeout=15000)
                            await page.wait_for_timeout(3000)
                            
                            # Check if page loaded
                            title = await page.title()
                            if "Samsung" in title or "producto" in title.lower():
                                print(f"✅ Samsung page loaded: {title}")
                                break
                        except Exception as e:
                            print(f"❌ Samsung URL failed: {e}")
                            continue
                    
                    # Look for products with Samsung-specific selectors
                    product_elements = []
                    selectors = [
                        '.product-item', '.item', '.product', '.product-card',
                        '.product-tile', '.tile-product', '.product-tile-item',
                        '.product-grid-item', '.grid-item', '.search-result-item',
                        '.product-list-item', '.item-product', '.product-container',
                        '.samsung-product', '.product-box', '.product-wrapper'
                    ]
                    
                    for selector in selectors:
                        try:
                            elements = await page.query_selector_all(selector)
                            if elements:
                                print(f"📦 Samsung found {len(elements)} products with selector: {selector}")
                                product_elements = elements
                                break
                        except:
                            continue
                    
                    if not product_elements:
                        # Fallback: look for elements with price content
                        print("🔍 Samsung trying fallback strategy...")
                        all_elements = await page.query_selector_all('*')
                        for element in all_elements[:200]:  # Check even more elements
                            try:
                                text = await element.inner_text()
                                if text and len(text) > 20 and ('$' in text or 'peso' in text.lower() or 'precio' in text.lower() or 'iPhone' in text or 'producto' in text.lower() or 'samsung' in text.lower()):
                                    product_elements.append(element)
                                    if len(product_elements) >= 20:  # Even more products
                                        break
                            except:
                                continue
                    
                    if not product_elements:
                        # Strategy 3: Try to find any clickable elements that might be products
                        print("🔍 Samsung trying clickable elements strategy...")
                        clickable_elements = await page.query_selector_all('a, button, [onclick], [data-testid]')
                        for element in clickable_elements[:100]:
                            try:
                                text = await element.inner_text()
                                if text and len(text) > 10 and ('$' in text or 'iPhone' in text or 'producto' in text.lower() or 'samsung' in text.lower()):
                                    product_elements.append(element)
                                    if len(product_elements) >= 10:
                                        break
                            except:
                                continue
                    
                    products = []
                    for element in product_elements[:limit]:
                        try:
                            all_text = await element.inner_text()
                            lines = all_text.split('\n')
                            
                            # Extract name
                            name = None
                            for line in lines:
                                line = line.strip()
                                if line and len(line) > 10 and not line.startswith('$'):
                                    name = line
                                    break
                            
                            if not name:
                                continue
                            
                            # Extract price
                            price = None
                            for line in lines:
                                if '$' in line and any(char.isdigit() for char in line):
                                    price = line.strip()
                                    break
                            
                            if not price:
                                continue
                            
                            # Find URL and image
                            link_elem = await element.query_selector('a')
                            url = await link_elem.get_attribute('href') if link_elem else ''
                            
                            img_elem = await element.query_selector('img')
                            image = await img_elem.get_attribute('src') if img_elem else ''
                            
                            product = {
                                'name': name.strip(),
                                'price': price.strip(),
                                'url': f"https://www.samsung.com{url}" if url else '',
                                'image': image,
                                'site': 'Samsung'
                            }
                            products.append(product)
                                
                        except Exception as e:
                            continue
                    
                    print(f"✅ Samsung: Found {len(products)} products")
                    return products
                    
                except Exception as e:
                    print(f"❌ Samsung error: {e}")
                    return []
                finally:
                    await browser.close()
                    
        except Exception as e:
            print(f"❌ Samsung error: {e}")
            return []

# Unified free client
class UnifiedFreeAPIClient:
    """Unified client using free APIs and improved scraping"""
    
    def __init__(self):
        self.free_client = FreeAPIClient()
    
    async def search_all_sites_free(self, query: str, limit_per_site: int = 5) -> Dict[str, List[Dict[str, Any]]]:
        """Search all sites using free methods"""
        print(f"🚀 Free APIs: Searching '{query}' across ALL sites...")
        
        # Create tasks for all sites
        tasks = [
            self.free_client.search_mercadolibre_free(query, limit_per_site),
            self.free_client.search_amazon_improved_scraping(query, limit_per_site),
            self.free_client.search_walmart_improved_scraping(query, limit_per_site),
            self.free_client.search_liverpool_improved_scraping(query, limit_per_site),
            self.free_client.search_coppel_scraping(query, limit_per_site),
            self.free_client.search_elektra_scraping(query, limit_per_site),
            self.free_client.search_aurrera_scraping(query, limit_per_site),
            self.free_client.search_costco_scraping(query, limit_per_site),
            self.free_client.search_sams_scraping(query, limit_per_site),
            self.free_client.search_samsung_scraping(query, limit_per_site)
        ]
        
        # Execute all tasks in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Organize results
        all_results = {
            'MercadoLibre': results[0] if not isinstance(results[0], Exception) else [],
            'Amazon': results[1] if not isinstance(results[1], Exception) else [],
            'Walmart': results[2] if not isinstance(results[2], Exception) else [],
            'Liverpool': results[3] if not isinstance(results[3], Exception) else [],
            'Coppel': results[4] if not isinstance(results[4], Exception) else [],
            'Elektra': results[5] if not isinstance(results[5], Exception) else [],
            'Aurrera': results[6] if not isinstance(results[6], Exception) else [],
            'Costco': results[7] if not isinstance(results[7], Exception) else [],
            'Sams': results[8] if not isinstance(results[8], Exception) else [],
            'Samsung': results[9] if not isinstance(results[9], Exception) else []
        }
        
        # Print summary
        total_products = sum(len(products) for products in all_results.values())
        working_sites = sum(1 for products in all_results.values() if len(products) > 0)
        
        print(f"📊 Free APIs Summary: {total_products} total products found")
        print(f"🎯 Working sites: {working_sites}/{len(all_results)}")
        for site, products in all_results.items():
            status = "✅" if len(products) > 0 else "❌"
            print(f"   {status} {site}: {len(products)} products")
        
        return all_results

# Convenience function
async def search_products_free(query: str, limit_per_site: int = 5) -> Dict[str, List[Dict[str, Any]]]:
    """Convenience function to search all sites using free methods"""
    client = UnifiedFreeAPIClient()
    async with client.free_client:
        return await client.search_all_sites_free(query, limit_per_site)

