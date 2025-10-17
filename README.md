# 🚀 Sistema de Monitoreo de Precios con IA

Sistema avanzado de scraping multihilo que monitorea ofertas en e-commerce mexicanos, analiza precios con IA y envía notificaciones inteligentes a Telegram.

## ✨ Características

- **🤖 Análisis con IA**: OpenAI GPT-4o-mini para análisis inteligente de ofertas
- **🧵 Scraping Multihilo**: 20 productos procesados en paralelo
- **📱 Múltiples Chats**: Clasificación automática por tipo de descuento
- **🛡️ Anti-Detección**: Técnicas avanzadas para evitar bloqueos
- **⚡ Automatización**: GitHub Actions cada 10 minutos
- **🌐 API REST**: FastAPI con autenticación JWT
- **💻 Frontend**: Panel Angular con dashboard

## 🎯 Sitios Monitoreados

- Amazon México
- MercadoLibre México
- Walmart México
- Liverpool México
- Best Buy México

## 📊 Clasificación de Ofertas

- **🔥 Excelentes** (>50% descuento): Chat de ofertas premium
- **💰 Buenas** (20-50% descuento): Chat de ofertas regulares

## 🚀 Instalación

### Prerrequisitos

- Python 3.11+
- Node.js 18+
- PostgreSQL
- Cuenta de OpenAI
- Bot de Telegram

### Configuración

1. **Clona el repositorio:**
```bash
git clone https://github.com/tu-usuario/price-monitoring-system.git
cd price-monitoring-system
```

2. **Configura variables de entorno:**
```bash
cp env.example .env
# Edita .env con tus credenciales
```

3. **Instala dependencias:**
```bash
# Backend
pip install -r api/requirements.txt
pip install -r scraper/requirements.txt

# Frontend
cd frontend
npm install
```

4. **Configura base de datos:**
```bash
# Crear usuario admin
python api/scripts/create_admin.py
```

## 🔧 Configuración de GitHub Secrets

Configura estos secrets en GitHub Actions:

- `POSTGRES_HOST`: Host de PostgreSQL
- `POSTGRES_PORT`: Puerto (5432)
- `POSTGRES_DB`: Nombre de la base de datos
- `POSTGRES_USER`: Usuario de PostgreSQL
- `POSTGRES_PASSWORD`: Contraseña de PostgreSQL
- `TELEGRAM_BOT_TOKEN`: Token de tu bot
- `TELEGRAM_CHAT_ID`: Chat principal
- `TELEGRAM_CHAT_ID_HIGH`: Chat para ofertas >50%
- `TELEGRAM_CHAT_ID_MEDIUM`: Chat para ofertas 20-50%
- `OPENAI_API_KEY`: API key de OpenAI
- `API_JWT_SECRET`: Clave secreta JWT

## 🏃‍♂️ Uso

### Ejecutar Scrapers Localmente

```bash
# Sistema multihilo con 20 productos IA
python scraper/multithreaded_ai_scraper.py

# Sistema avanzado con técnicas anti-detección
python scraper/advanced_stealth_scraper.py
```

### Ejecutar API

```bash
cd api
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Ejecutar Frontend

```bash
cd frontend
ng serve
```

## 📁 Estructura del Proyecto

```
price-monitoring-system/
├── api/                    # Backend FastAPI
│   ├── routes/            # Endpoints de la API
│   ├── models.py          # Modelos de base de datos
│   └── scripts/           # Scripts de utilidad
├── scraper/               # Sistema de scraping
│   ├── ai/                # Análisis con IA
│   ├── sites/             # Scrapers por sitio
│   └── notifier/          # Notificaciones
├── frontend/              # Panel Angular
├── infra/                 # Docker y configuración
└── .github/workflows/     # GitHub Actions
```

## 🔄 Automatización

El sistema se ejecuta automáticamente cada 10 minutos via GitHub Actions:

- **Scraping**: 20 productos generados por IA
- **Análisis**: IA analiza cada oferta
- **Notificaciones**: Envío automático a chats correspondientes
- **Resúmenes**: Análisis de mercado con IA

## 🛡️ Seguridad

- Variables de entorno para credenciales
- Autenticación JWT en API
- Técnicas anti-detección en scraping
- Rate limiting en notificaciones

## 📈 Monitoreo

- Logs estructurados en JSON
- Métricas de scraping y IA
- Health checks automáticos
- Dashboard de ofertas

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT.

## 🆘 Soporte

Para soporte, abre un issue en GitHub o contacta al desarrollador.

---

**¡Sistema de monitoreo de precios con IA - Encuentra las mejores ofertas automáticamente!** 🎯