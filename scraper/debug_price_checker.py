#!/usr/bin/env python3
"""
Script de debug para el verificador de precios
"""

import asyncio
import sys
import os

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from price_research.improved_price_checker import ImprovedPriceChecker

async def debug_price_checker():
    """Debug del verificador de precios"""
    print("🔍 Debug del verificador de precios...")
    
    checker = ImprovedPriceChecker()
    
    # Probar con un producto específico
    product = "iPhone 13"
    print(f"\n📱 Probando: {product}")
    
    try:
        # Obtener precios de reventa
        print("🔍 Obteniendo precios de reventa...")
        resale_data = await checker.get_resale_prices(product)
        
        print(f"\n📊 Datos obtenidos:")
        print(f"   - Facebook Marketplace: {resale_data.get('facebook_marketplace', [])}")
        print(f"   - eBay: {resale_data.get('ebay', [])}")
        print(f"   - MercadoLibre: {resale_data.get('mercadolibre_usado', [])}")
        print(f"   - Google Shopping: {resale_data.get('google_shopping', [])}")
        print(f"   - Precio promedio: {resale_data.get('average_resale_price', 0)}")
        print(f"   - Rango: {resale_data.get('price_range', 'N/A')}")
        print(f"   - Confianza: {resale_data.get('confidence', 'N/A')}")
        
        # Probar análisis de oportunidad
        test_price = 5000
        print(f"\n💰 Análisis con precio de prueba: ${test_price}")
        analysis = checker.analyze_price_opportunity(test_price, resale_data)
        
        print(f"   - Es buena oportunidad: {analysis.get('is_good_deal', False)}")
        print(f"   - Potencial de ganancia: ${analysis.get('profit_potential', 0)}")
        print(f"   - Porcentaje de ganancia: {analysis.get('profit_percentage', 0)}%")
        print(f"   - Razonamiento: {analysis.get('reasoning', 'N/A')}")
        
        # Verificar si hay datos válidos
        all_prices = []
        for source in ['facebook_marketplace', 'ebay', 'mercadolibre_usado', 'google_shopping']:
            prices = resale_data.get(source, [])
            all_prices.extend(prices)
            print(f"   - {source}: {len(prices)} precios - {prices}")
        
        print(f"\n📈 Total de precios encontrados: {len(all_prices)}")
        print(f"📈 Precios: {all_prices}")
        
        if len(all_prices) == 0:
            print("❌ PROBLEMA: No se encontraron precios de reventa")
        else:
            print("✅ Se encontraron precios de reventa")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_price_checker())
