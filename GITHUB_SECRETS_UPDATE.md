# GitHub Secrets - Configuración Requerida

## 🔧 **Secrets que necesitas configurar en GitHub:**

Ve a: Settings > Secrets and variables > Actions

### **Secrets requeridos:**
- `POSTGRES_HOST`: Tu host de PostgreSQL
- `POSTGRES_PORT`: Puerto de PostgreSQL (5432)
- `POSTGRES_DB`: Nombre de la base de datos
- `POSTGRES_USER`: Usuario de PostgreSQL
- `POSTGRES_PASSWORD`: Contraseña de PostgreSQL
- `TELEGRAM_BOT_TOKEN`: Token de tu bot de Telegram
- `TELEGRAM_CHAT_ID`: ID del chat principal
- `TELEGRAM_CHAT_ID_HIGH`: ID del chat para ofertas >50%
- `TELEGRAM_CHAT_ID_MEDIUM`: ID del chat para ofertas 20-50%
- `OPENAI_API_KEY`: Tu API key de OpenAI
- `API_JWT_SECRET`: Clave secreta para JWT (genera una nueva)
- `HOSTINGER_FTP_HOST`: Host FTP de Hostinger
- `HOSTINGER_FTP_USER`: Usuario FTP de Hostinger
- `HOSTINGER_FTP_PASS`: Contraseña FTP de Hostinger
- `HOSTINGER_FTP_PORT`: Puerto FTP (21)
- `HOSTINGER_DEPLOY_PATH`: Ruta de deploy (public_html)

## 🚀 **Después de configurar:**

1. Ve a: Actions
2. Ejecuta manualmente el workflow "Run Scrapers"
3. Verifica que las notificaciones lleguen a los chats correctos

## 📱 **Verificación:**

- Las notificaciones llegarán a los chats configurados
- El sistema está funcionando localmente
- Los scrapers están listos para producción

