#!/usr/bin/env python3
"""
Script de prueba para el flujo completo del scraper
"""

import asyncio
import sys
import os

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from price_research.improved_price_checker import ImprovedPriceChecker

async def test_full_flow():
    """Probar el flujo completo como en el scraper"""
    print("🧪 Probando flujo completo del scraper...")
    
    # Simular datos de producto como en el scraper
    product_data = {
        'name': 'iPhone 13 128GB',
        'current_price': '$4,500',
        'discount_percentage': 25.0,
        'site': 'MercadoLibre',
        'url': 'https://example.com'
    }
    
    print(f"📱 Producto de prueba: {product_data['name']}")
    print(f"💰 Precio: {product_data['current_price']}")
    print(f"📉 Descuento: {product_data['discount_percentage']}%")
    
    # Inicializar verificador de precios
    price_checker = ImprovedPriceChecker()
    
    try:
        # Paso 1: Obtener precios de reventa
        print(f"\n🔍 Paso 1: Obteniendo precios de reventa...")
        resale_data = await price_checker.get_resale_prices(product_data['name'])
        
        print(f"📊 Datos de reventa obtenidos:")
        print(f"   - Precio promedio: ${resale_data.get('average_resale_price', 0):,.0f}")
        print(f"   - Rango: {resale_data.get('price_range', 'N/A')}")
        print(f"   - Confianza: {resale_data.get('confidence', 'N/A')}")
        
        # Paso 2: Analizar oportunidad de reventa
        print(f"\n💰 Paso 2: Analizando oportunidad de reventa...")
        current_price = float(str(product_data['current_price']).replace('$', '').replace(',', ''))
        price_analysis = price_checker.analyze_price_opportunity(current_price, resale_data)
        
        print(f"📈 Análisis de oportunidad:")
        print(f"   - Es buena oportunidad: {price_analysis.get('is_good_deal', False)}")
        print(f"   - Potencial de ganancia: ${price_analysis.get('profit_potential', 0):,.0f}")
        print(f"   - Porcentaje de ganancia: {price_analysis.get('profit_percentage', 0):.1f}%")
        print(f"   - Razonamiento: {price_analysis.get('reasoning', 'N/A')}")
        
        # Paso 3: Simular análisis de IA
        print(f"\n🤖 Paso 3: Simulando análisis de IA...")
        
        # Crear prompt como en el scraper
        prompt = f"""
        Eres un experto en análisis de ofertas de productos electrónicos y reventa.
        Analiza esta oferta usando datos REALES de precios de reventa obtenidos de Facebook Marketplace, eBay y MercadoLibre.
        
        PRODUCTO BUSCADO: iPhone 13
        PRODUCTO ENCONTRADO: {product_data['name']}
        Precio actual: {product_data['current_price']}
        Precio estimado del mercado: $6000
        Descuento calculado: {product_data['discount_percentage']:.1f}%
        Sitio: {product_data['site']}
        
        DATOS REALES DE REVENTA OBTENIDOS:
        - Precio promedio de reventa: ${resale_data.get('average_resale_price', 0):,.0f}
        - Rango de precios: {resale_data.get('price_range', 'No disponible')}
        - Confianza en datos: {resale_data.get('confidence', 'low')}
        - Análisis de oportunidad: {price_analysis.get('reasoning', 'No disponible')}
        - Es buena oportunidad: {price_analysis.get('is_good_deal', False)}
        - Potencial de ganancia: ${price_analysis.get('profit_potential', 0):,.0f} ({price_analysis.get('profit_percentage', 0):.1f}%)
        
        TAREA CRÍTICA:
        1. Verifica que el producto encontrado sea realmente el producto buscado (no accesorios)
        2. Usa los datos REALES de precios de reventa proporcionados arriba
        3. Considera el potencial de ganancia real calculado
        4. Determina si realmente es una buena oportunidad de reventa
        
        Proporciona análisis en JSON con:
        - confidence_score: 0-1 (confianza en la oferta, 0.8+ solo si es el producto correcto Y buen precio de reventa)
        - reasoning: explicación corta (máximo 50 palabras)
        - market_opinion: opinión del mercado (máximo 30 palabras)
        - recommendation: recomendación específica (máximo 20 palabras)
        - resell_potential: potencial de reventa 1-10
        - is_correct_product: true/false si es el producto buscado
        - real_discount: true/false si el descuento es real basado en precios de reventa REALES
        - market_price_range: rango de precios de reventa REALES obtenido
        - resell_price_estimate: precio estimado de reventa REAL obtenido
        
        Responde SOLO en formato JSON válido.
        """
        
        print(f"📝 Prompt generado (primeros 200 caracteres):")
        print(f"   {prompt[:200]}...")
        
        # Simular respuesta de IA
        print(f"\n🤖 Simulando respuesta de IA...")
        
        # Crear análisis simulado
        simulated_analysis = {
            'confidence_score': 0.7 if price_analysis.get('is_good_deal', False) else 0.3,
            'reasoning': f"Precio actual ${current_price:,.0f} vs reventa ${resale_data.get('average_resale_price', 0):,.0f}",
            'market_opinion': "Oportunidad moderada de reventa",
            'recommendation': "Considerar compra si es el producto correcto",
            'resell_potential': 7 if price_analysis.get('is_good_deal', False) else 3,
            'is_correct_product': True,
            'real_discount': price_analysis.get('is_good_deal', False),
            'market_price_range': resale_data.get('price_range', 'N/A'),
            'resell_price_estimate': resale_data.get('average_resale_price', 0)
        }
        
        print(f"📊 Análisis simulado:")
        for key, value in simulated_analysis.items():
            print(f"   - {key}: {value}")
        
        # Verificar si los datos están llegando correctamente
        print(f"\n✅ Verificación de datos:")
        print(f"   - Datos de reventa válidos: {resale_data.get('average_resale_price', 0) > 0}")
        print(f"   - Análisis de oportunidad válido: {price_analysis.get('is_good_deal') is not None}")
        print(f"   - Precio actual válido: {current_price > 0}")
        
        if resale_data.get('average_resale_price', 0) == 0:
            print("❌ PROBLEMA: Precio promedio de reventa es 0")
        else:
            print("✅ Datos de reventa válidos")
            
    except Exception as e:
        print(f"❌ Error en el flujo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_full_flow())
