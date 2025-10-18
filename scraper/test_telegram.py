#!/usr/bin/env python3
"""
Script de prueba para verificar las notificaciones de Telegram
"""

import os
import requests
import asyncio
from datetime import datetime

# Configuración
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID_HIGH = os.getenv("TELEGRAM_CHAT_ID_HIGH", "-1003150179214")
TELEGRAM_CHAT_ID_MEDIUM = os.getenv("TELEGRAM_CHAT_ID_MEDIUM", "-4871231611")

async def test_telegram_connection():
    """Probar conexión con Telegram"""
    print("🧪 Probando conexión con Telegram...")
    
    if not TELEGRAM_BOT_TOKEN:
        print("❌ ERROR: TELEGRAM_BOT_TOKEN no está configurado")
        print("   Configura la variable de entorno con tu token de bot")
        return False
    
    # Probar getMe para verificar que el bot funciona
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            bot_info = response.json()
            print(f"✅ Bot conectado: {bot_info['result']['first_name']}")
            print(f"   Username: @{bot_info['result']['username']}")
        else:
            print(f"❌ Error conectando con bot: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False
    
    return True

async def test_send_message(chat_id: str, chat_name: str):
    """Probar envío de mensaje a un chat específico"""
    print(f"\n📤 Probando envío a {chat_name} (ID: {chat_id})...")
    
    try:
        message = f"""🧪 Prueba de Notificación - {datetime.now().strftime('%H:%M:%S')}

Este es un mensaje de prueba del sistema de monitoreo de precios.

✅ Si recibes este mensaje, las notificaciones están funcionando correctamente.

🤖 Sistema: Price Monitoring Bot
⏰ Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
        
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }
        
        response = requests.post(url, data=data, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Mensaje enviado exitosamente a {chat_name}")
            return True
        else:
            print(f"❌ Error enviando mensaje a {chat_name}: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error enviando mensaje a {chat_name}: {e}")
        return False

async def main():
    """Función principal de prueba"""
    print("🚀 === PRUEBA DE NOTIFICACIONES TELEGRAM ===\n")
    
    # Probar conexión
    if not await test_telegram_connection():
        return
    
    # Probar envío a ambos chats
    results = []
    
    if TELEGRAM_CHAT_ID_HIGH:
        results.append(await test_send_message(TELEGRAM_CHAT_ID_HIGH, "Chat Excelentes"))
    
    if TELEGRAM_CHAT_ID_MEDIUM:
        results.append(await test_send_message(TELEGRAM_CHAT_ID_MEDIUM, "Chat Buenos"))
    
    # Resumen
    print(f"\n📊 === RESUMEN DE PRUEBAS ===")
    successful = sum(results)
    total = len(results)
    
    if successful == total:
        print(f"✅ Todas las pruebas exitosas ({successful}/{total})")
        print("🎉 Las notificaciones de Telegram están funcionando correctamente!")
    else:
        print(f"⚠️ Pruebas parcialmente exitosas ({successful}/{total})")
        print("🔧 Revisa la configuración de los chat IDs")

if __name__ == "__main__":
    asyncio.run(main())
