#!/usr/bin/env python3
"""
Script para configurar las notificaciones de Telegram
"""

import os
import sys

def print_banner():
    print("🤖 === CONFIGURACIÓN DE TELEGRAM BOT ===\n")

def get_telegram_token():
    """Obtener token de bot de Telegram"""
    print("📋 Para configurar las notificaciones necesitas:")
    print("1. Crear un bot en Telegram")
    print("2. Obtener el token del bot")
    print("3. Obtener los IDs de los chats donde quieres recibir notificaciones\n")
    
    print("🔧 PASOS PARA CREAR UN BOT:")
    print("1. Abre Telegram y busca @BotFather")
    print("2. Envía /newbot")
    print("3. Dale un nombre a tu bot (ej: 'Price Monitor Bot')")
    print("4. Dale un username (debe terminar en 'bot', ej: 'price_monitor_bot')")
    print("5. Copia el token que te da BotFather\n")
    
    token = input("🔑 Ingresa tu TELEGRAM_BOT_TOKEN: ").strip()
    
    if not token:
        print("❌ Token vacío. Saliendo...")
        return None
    
    if not token.count(':') == 1:
        print("⚠️ El token parece inválido. Debe tener formato: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz")
        return None
    
    return token

def get_chat_ids():
    """Obtener IDs de chats"""
    print("\n📱 PARA OBTENER CHAT IDs:")
    print("1. Agrega tu bot al chat/grupo donde quieres recibir notificaciones")
    print("2. Envía un mensaje al bot en ese chat")
    print("3. Visita: https://api.telegram.org/bot<TOKEN>/getUpdates")
    print("4. Busca 'chat':{'id': -123456789} y copia el número\n")
    
    high_chat = input("🔥 Chat ID para ofertas EXCELENTES (>50% descuento): ").strip()
    medium_chat = input("💰 Chat ID para ofertas BUENAS (20-50% descuento): ").strip()
    
    return high_chat, medium_chat

def create_env_file(token, high_chat, medium_chat):
    """Crear archivo .env con la configuración"""
    env_content = f"""# Configuración de Telegram
TELEGRAM_BOT_TOKEN={token}
TELEGRAM_CHAT_ID_HIGH={high_chat}
TELEGRAM_CHAT_ID_MEDIUM={medium_chat}

# Configuración de OpenAI
OPENAI_API_KEY=your_openai_api_key_here

# Configuración de Base de Datos
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=price_monitoring
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password

# Configuración de API
API_JWT_SECRET=your_super_secret_jwt_key_change_in_production
"""
    
    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        print("✅ Archivo .env creado exitosamente")
        return True
    except Exception as e:
        print(f"❌ Error creando archivo .env: {e}")
        return False

def show_instructions():
    """Mostrar instrucciones finales"""
    print("\n🎉 === CONFIGURACIÓN COMPLETADA ===")
    print("\n📋 PRÓXIMOS PASOS:")
    print("1. Configura tu OPENAI_API_KEY en el archivo .env")
    print("2. Ejecuta: python test_telegram.py")
    print("3. Si las pruebas son exitosas, ejecuta el scraper principal")
    print("\n🔧 COMANDOS ÚTILES:")
    print("• Probar notificaciones: python test_telegram.py")
    print("• Ejecutar scraper: python multithreaded_ai_scraper.py")
    print("• Ver logs: El scraper mostrará el estado de las notificaciones")

def main():
    """Función principal"""
    print_banner()
    
    # Obtener token
    token = get_telegram_token()
    if not token:
        return
    
    # Obtener chat IDs
    high_chat, medium_chat = get_chat_ids()
    
    # Crear archivo .env
    if create_env_file(token, high_chat, medium_chat):
        show_instructions()
    else:
        print("❌ No se pudo crear el archivo de configuración")

if __name__ == "__main__":
    main()
