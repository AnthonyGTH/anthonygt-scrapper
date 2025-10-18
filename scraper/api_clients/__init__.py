#!/usr/bin/env python3
"""
API Clients package for e-commerce sites
"""

from .unified_api_client import UnifiedAPIClient, search_products_unified, search_products_unified_sync
from .mercadolibre_api import MercadoLibreAPI, MercadoLibreAPISync
from .amazon_api import AmazonAPI, AmazonScrapingFallback
from .walmart_api import WalmartAPI, WalmartAPISync
from .liverpool_api import LiverpoolAPI, LiverpoolAPISync

__all__ = [
    'UnifiedAPIClient',
    'search_products_unified',
    'search_products_unified_sync',
    'MercadoLibreAPI',
    'MercadoLibreAPISync',
    'AmazonAPI',
    'AmazonScrapingFallback',
    'WalmartAPI',
    'WalmartAPISync',
    'LiverpoolAPI',
    'LiverpoolAPISync'
]
