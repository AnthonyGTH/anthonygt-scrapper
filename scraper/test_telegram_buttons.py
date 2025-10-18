#!/usr/bin/env python3
"""
Script de prueba para botones de Telegram
"""

import os
import requests
import json

# Configurar variables de entorno
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID_HIGH = os.getenv("TELEGRAM_CHAT_ID_HIGH")

def test_telegram_buttons():
    """Probar botones de Telegram"""
    print("🧪 Probando botones de Telegram...")
    
    if not TELEGRAM_BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN no configurado")
        return
    
    if not TELEGRAM_CHAT_ID_HIGH:
        print("❌ TELEGRAM_CHAT_ID_HIGH no configurado")
        return
    
    # Crear mensaje de prueba
    message = """🔥 Oferta EXCELENTE - Análisis IA

📱 iPhone 13 128GB
🏪 MercadoLibre
💰 Precio: $4,500
📉 DESCUENTO: 25.0%

🧠 Análisis IA:
💭 Precio actual $4,500 vs reventa $3,369
📊 Confianza: 70%
💡 Recomendación: Considerar compra si es el producto correcto
📈 Opinión mercado: Oportunidad moderada de reventa
🔄 Potencial reventa: 7/10

🔍 Verificación:
✅ Producto correcto
⚠️ Descuento inflado
💰 Rango mercado: $133 - $8,500
💵 Precio reventa estimado: 3369.2

💰 Precio reventa real: $3,369
📊 Rango real: $133 - $8,500"""
    
    # Crear botones
    keyboard = {
        "inline_keyboard": [
            [{"text": "🔗 Ver Producto", "url": "https://articulo.mercadolibre.com.mx/MLM-1234567890"}],
            [{"text": "📊 Comparar Precios", "url": "https://www.google.com/search?q=iPhone+13+128GB+precio"}]
        ]
    }
    
    # Enviar mensaje
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        'chat_id': TELEGRAM_CHAT_ID_HIGH,
        'text': message,
        'parse_mode': 'Markdown',
        'reply_markup': json.dumps(keyboard)
    }
    
    print(f"📤 Enviando mensaje de prueba con botones...")
    print(f"🔗 URL del botón: {keyboard['inline_keyboard'][0][0]['url']}")
    print(f"📊 URL de comparación: {keyboard['inline_keyboard'][1][0]['url']}")
    
    try:
        response = requests.post(url, data=data, timeout=10)
        
        if response.status_code == 200:
            print("✅ Mensaje con botones enviado exitosamente")
            result = response.json()
            print(f"📊 Respuesta: {result}")
        else:
            print(f"❌ Error enviando mensaje: {response.status_code}")
            print(f"📄 Respuesta: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_telegram_buttons()
