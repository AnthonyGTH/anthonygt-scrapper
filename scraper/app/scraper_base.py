"""
Base scraper class with common functionality for all site scrapers.
"""

import asyncio
import time
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

@dataclass
class ScrapedProduct:
    """Data structure for scraped product information"""
    name: str
    price: float
    currency: str
    url: str
    site: str
    availability: str
    sku: Optional[str] = None
    category: Optional[str] = None
    original_price: Optional[float] = None
    discount_percentage: Optional[float] = None

class BaseScraper(ABC):
    """Abstract base class for all scrapers"""
    
    def __init__(self, site_name: str, base_url: str):
        self.site_name = site_name
        self.base_url = base_url
        self.logger = logging.getLogger(f"scraper.{site_name}")
        
    @abstractmethod
    async def scrape_product(self, url: str) -> Optional[ScrapedProduct]:
        """Scrape a single product URL"""
        pass
    
    async def scrape_products(self, urls: List[str]) -> List[ScrapedProduct]:
        """Scrape multiple product URLs with rate limiting"""
        results = []
        
        for i, url in enumerate(urls):
            try:
                self.logger.info(f"Scraping {url}")
                product = await self.scrape_product(url)
                
                if product:
                    results.append(product)
                    self.logger.info(f"Successfully scraped {product.name}")
                else:
                    self.logger.warning(f"Failed to scrape {url}")
                
                # Rate limiting - wait between requests
                if i < len(urls) - 1:
                    await asyncio.sleep(2)
                    
            except Exception as e:
                self.logger.error(f"Error scraping {url}: {e}")
                continue
        
        return results

class ScraperOrchestrator:
    """Orchestrates all scrapers and manages data flow"""
    
    def __init__(self):
        self.logger = logging.getLogger("orchestrator")
        
    async def run_all_scrapers(self) -> List[ScrapedProduct]:
        """Run all configured scrapers"""
        # This would be implemented with actual scrapers
        # For now, return empty list
        self.logger.info("Running all scrapers...")
        return []
