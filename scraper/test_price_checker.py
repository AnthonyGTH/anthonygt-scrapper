#!/usr/bin/env python3
"""
Script de prueba para el verificador de precios reales
"""

import asyncio
import sys
import os

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from price_research.real_price_checker import RealPriceChecker

async def test_price_checker():
    """Probar el verificador de precios reales"""
    print("🧪 Iniciando pruebas del verificador de precios reales...")
    
    checker = RealPriceChecker()
    
    # Productos de prueba
    test_products = [
        "iPhone 13",
        "PlayStation 5",
        "MacBook Air M2",
        "AirPods Pro",
        "Nintendo Switch"
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
            print(f"   - Precio promedio: ${resale_data.get('average_resale_price', 0):,.0f}")
            print(f"   - Rango de precios: {resale_data.get('price_range', 'N/A')}")
            print(f"   - Confianza: {resale_data.get('confidence', 'N/A')}")
            
            # Mostrar precios individuales
            if resale_data.get('facebook_marketplace'):
                print(f"   - Facebook precios: {resale_data['facebook_marketplace']}")
            if resale_data.get('ebay'):
                print(f"   - eBay precios: {resale_data['ebay']}")
            if resale_data.get('mercadolibre_usado'):
                print(f"   - MercadoLibre precios: {resale_data['mercadolibre_usado']}")
            
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
        await asyncio.sleep(2)
    
    print("\n✅ Pruebas completadas")

async def test_individual_sources():
    """Probar cada fuente individualmente"""
    print("\n🔬 Probando fuentes individuales...")
    
    checker = RealPriceChecker()
    product = "iPhone 13"
    
    print(f"\n📱 Probando {product} en cada fuente:")
    
    # Probar Facebook Marketplace
    try:
        print("\n🌐 Probando Facebook Marketplace...")
        fb_prices = await checker._search_facebook_marketplace(product)
        print(f"   Resultado: {len(fb_prices)} precios encontrados")
        if fb_prices:
            print(f"   Precios: {fb_prices}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Probar eBay
    try:
        print("\n🌐 Probando eBay...")
        ebay_prices = await checker._search_ebay(product)
        print(f"   Resultado: {len(ebay_prices)} precios encontrados")
        if ebay_prices:
            print(f"   Precios: {ebay_prices}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Probar MercadoLibre
    try:
        print("\n🌐 Probando MercadoLibre...")
        ml_prices = await checker._search_mercadolibre_usado(product)
        print(f"   Resultado: {len(ml_prices)} precios encontrados")
        if ml_prices:
            print(f"   Precios: {ml_prices}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando pruebas del verificador de precios reales...")
    
    # Ejecutar pruebas
    asyncio.run(test_price_checker())
    asyncio.run(test_individual_sources())
    
    print("\n🎉 Todas las pruebas completadas")
