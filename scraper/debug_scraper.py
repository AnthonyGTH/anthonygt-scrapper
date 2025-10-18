#!/usr/bin/env python3
"""
Script de debug para identificar problemas en el scraper
"""

import asyncio
import sys
import os

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api_clients.free_apis import search_products_free

async def debug_scraper():
    """Debug del scraper para identificar problemas"""
    print("🔍 Debug del scraper...")
    
    # Probar búsqueda de productos
    test_queries = [
        "iPhone 13",
        "PlayStation 5",
        "MacBook Air M2"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Probando búsqueda: {query}")
        print("=" * 50)
        
        try:
            results = await search_products_free(query)
            print(f"📊 Resultados encontrados: {len(results)}")
            
            # Verificar si results es una lista o diccionario
            if isinstance(results, dict):
                print(f"📊 Results es un diccionario con sitios: {list(results.keys())}")
                
                # Convertir diccionario a lista como en el scraper principal
                all_results = []
                for site, site_products in results.items():
                    for product_data in site_products:
                        product_data['site'] = site
                        all_results.append(product_data)
                
                print(f"📊 Total de productos después de aplanar: {len(all_results)}")
                results = all_results
            
            for i, result in enumerate(results[:3]):  # Solo los primeros 3
                print(f"\n📱 Producto {i+1}:")
                print(f"   - Nombre: {result.get('name', 'N/A')}")
                print(f"   - Precio: {result.get('price', 'N/A')}")
                print(f"   - Sitio: {result.get('site', 'N/A')}")
                print(f"   - URL: {result.get('url', 'N/A')}")
                
                # Verificar si el nombre contiene texto extraño
                name = result.get('name', '')
                if 'Skip to content' in name or 'Skip to main content' in name:
                    print(f"   ❌ PROBLEMA: Nombre contiene 'Skip to content'")
                if len(name) < 5:
                    print(f"   ❌ PROBLEMA: Nombre muy corto")
                if name.isdigit():
                    print(f"   ❌ PROBLEMA: Nombre es solo números")
                if not name or name == 'N/A':
                    print(f"   ❌ PROBLEMA: Nombre vacío o N/A")
                
                # Verificar precio
                price = result.get('price', '')
                if not price or price == 'N/A':
                    print(f"   ❌ PROBLEMA: Precio vacío o N/A")
                elif '$' not in price and 'MXN' not in price:
                    print(f"   ❌ PROBLEMA: Precio sin formato de moneda")
                
                # Verificar URL
                url = result.get('url', '')
                if not url or url == 'N/A' or url == '#':
                    print(f"   ❌ PROBLEMA: URL vacía o inválida")
                elif not url.startswith('http'):
                    print(f"   ❌ PROBLEMA: URL no válida")
                
        except Exception as e:
            print(f"❌ Error en búsqueda: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "="*50)
        
        # Pausa entre búsquedas
        await asyncio.sleep(2)
    
    print("\n✅ Debug completado")

if __name__ == "__main__":
    asyncio.run(debug_scraper())
