#!/usr/bin/env python3
"""
Script de prueba para el verificador de precios mejorado
"""

import asyncio
import sys
import os

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from price_research.improved_price_checker import ImprovedPriceChecker

async def test_improved_price_checker():
    """Probar el verificador de precios mejorado"""
    print("🧪 Iniciando pruebas del verificador de precios mejorado...")
    
    checker = ImprovedPriceChecker()
    
    # Productos de prueba
    test_products = [
        "iPhone 13",
        "PlayStation 5",
        "MacBook Air M2"
    ]
    
    for product in test_products:
        print(f"\n🔍 Probando: {product}")
        print("=" * 50)
        
        try:
            # Obtener precios de reventa
            resale_data = await checker.get_resale_prices(product)
            
            print(f"📊 Resultados para {product}:")
            print(f"   - Facebook Marketplace: {len(resale_data.get('facebook_marketplace', []))} precios")
            print(f"   - eBay: {len(resale_data.get('ebay', []))} precios")
            print(f"   - MercadoLibre: {len(resale_data.get('mercadolibre_usado', []))} precios")
            print(f"   - Google Shopping: {len(resale_data.get('google_shopping', []))} precios")
            print(f"   - Precio promedio: ${resale_data.get('average_resale_price', 0):,.0f}")
            print(f"   - Rango de precios: {resale_data.get('price_range', 'N/A')}")
            print(f"   - Confianza: {resale_data.get('confidence', 'N/A')}")
            
            # Mostrar precios individuales
            for source in ['facebook_marketplace', 'ebay', 'mercadolibre_usado', 'google_shopping']:
                prices = resale_data.get(source, [])
                if prices:
                    print(f"   - {source} precios: {prices}")
            
            # Probar análisis de oportunidad
            test_price = 5000  # Precio de prueba
            analysis = checker.analyze_price_opportunity(test_price, resale_data)
            
            print(f"\n💰 Análisis de oportunidad (precio de prueba: ${test_price}):")
            print(f"   - Es buena oportunidad: {analysis.get('is_good_deal', False)}")
            print(f"   - Potencial de ganancia: ${analysis.get('profit_potential', 0):,.0f}")
            print(f"   - Porcentaje de ganancia: {analysis.get('profit_percentage', 0):.1f}%")
            print(f"   - Razonamiento: {analysis.get('reasoning', 'N/A')}")
            
        except Exception as e:
            print(f"❌ Error con {product}: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "="*50)
        
        # Pausa entre pruebas
        await asyncio.sleep(3)
    
    print("\n✅ Pruebas completadas")

async def test_individual_methods():
    """Probar cada método individualmente"""
    print("\n🔬 Probando métodos individuales...")
    
    checker = ImprovedPriceChecker()
    product = "iPhone 13"
    
    print(f"\n📱 Probando {product} con cada método:")
    
    # Probar APIs directas
    try:
        print("\n🌐 Probando APIs directas...")
        api_results = await checker._search_with_apis(product)
        print(f"   Resultado: {api_results}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Probar scraping mejorado
    try:
        print("\n🌐 Probando scraping mejorado...")
        scraped_results = await checker._search_with_improved_scraping(product)
        print(f"   Resultado: {scraped_results}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Probar Google Shopping
    try:
        print("\n🌐 Probando Google Shopping...")
        google_prices = await checker._search_google_shopping(product)
        print(f"   Resultado: {len(google_prices)} precios - {google_prices}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando pruebas del verificador de precios mejorado...")
    
    # Ejecutar pruebas
    asyncio.run(test_improved_price_checker())
    asyncio.run(test_individual_methods())
    
    print("\n🎉 Todas las pruebas completadas")
