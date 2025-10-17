# Intelligent Price Monitoring System

A comprehensive system for monitoring e-commerce prices, detecting anomalies with AI, and sending notifications via Telegram. Features a secure Angular dashboard and automated CI/CD deployment to Hostinger.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Scrapers      │    │   AI Analysis   │    │   Telegram      │
│   (Playwright)  │───▶│   (OpenAI)      │───▶│   Notifications │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PostgreSQL Database                         │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐│
│  │  products   │ │   prices    │ │    deals    │ │    users    ││
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘│
└─────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                             │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐│
│  │   /deals    │ │  /auth/login│ │ /ai/analyze │ │   /health   ││
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘│
└─────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                 Angular Dashboard                             │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐│
│  │  Dashboard  │ │ Deal Detail │ │    Login    │ │    Jobs     ││
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL database
- Telegram Bot Token
- OpenAI API Key

### Local Development

1. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd price-monitoring-system
   cp .env.example .env
   # Edit .env with your credentials
   ```

2. **Database setup**:
   ```bash
   cd infra
   docker-compose up -d postgres
   # Wait for database to be ready
   alembic upgrade head
   ```

3. **Backend setup**:
   ```bash
   cd api
   pip install -r requirements.txt
   python scripts/create_admin.py  # Create admin user
   uvicorn main:app --reload
   ```

4. **Frontend setup**:
   ```bash
   cd web/angular
   npm install
   npm start
   ```

5. **Run scrapers**:
   ```bash
   cd scraper
   pip install -r requirements.txt
   python run-all.py
   ```

## 📁 Project Structure

```
price-monitoring-system/
├── infra/                    # Infrastructure & Database
│   ├── docker-compose.yml
│   ├── migrations/          # Alembic migrations
│   └── hostinger/           # Deployment scripts
├── scraper/                 # Web Scraping Module
│   ├── app/
│   │   ├── scraper_base.py  # Base scraper class
│   │   └── data_models.py   # Pydantic models
│   ├── sites/               # Site-specific scrapers
│   │   ├── amazon_mx.py
│   │   ├── mercadolibre.py
│   │   ├── walmart_mx.py
│   │   └── liverpool.py
│   ├── ai/                  # AI Analysis
│   │   ├── analyzer.py
│   │   ├── prompts.py
│   │   ├── cache.py
│   │   └── rules.py
│   ├── notifier/            # Telegram Notifications
│   │   ├── telegram_bot.py
│   │   └── formatter.py
│   ├── config/
│   │   └── products.json     # Products to monitor
│   ├── tests/
│   ├── run-all.py           # Main orchestrator
│   └── requirements.txt
├── api/                     # FastAPI Backend
│   ├── main.py
│   ├── auth.py
│   ├── models.py
│   ├── routes/
│   │   ├── deals.py
│   │   ├── auth.py
│   │   ├── ai.py
│   │   └── health.py
│   ├── scripts/
│   │   └── create_admin.py
│   └── requirements.txt
├── web/                     # Angular Frontend
│   └── angular/
│       ├── src/
│       │   ├── app/
│       │   │   ├── components/
│       │   │   ├── services/
│       │   │   └── guards/
│       │   └── environments/
│       └── dist/            # Build output
├── .github/workflows/       # CI/CD
│   ├── run-scrapers.yml
│   └── deploy-hostinger.yml
├── .env.example
├── .gitignore
└── README.md
```

## 🔧 Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

- **Database**: PostgreSQL connection details from Hostinger
- **Telegram**: Bot token and chat ID for notifications
- **AI**: OpenAI API key and model configuration
- **Authentication**: JWT secret (use a strong, unique secret)
- **Hostinger**: FTP credentials for deployment

### Adding Products to Monitor

Edit `scraper/config/products.json`:

```json
{
  "products": [
    {
      "url": "https://amazon.com.mx/product-url",
      "site": "amazon_mx",
      "category": "Electronics",
      "reference_price": 12999,
      "monitor": true
    }
  ]
}
```

## 🤖 AI Analysis

The system uses OpenAI's GPT-4o-mini to analyze price anomalies:

- **Input**: Product data, price history, statistics
- **Output**: Confidence score (0-1), reasoning, Telegram message
- **Tone**: Sober, factual Spanish (Mexico)
- **Fallback**: Basic heuristics if AI fails

## 📱 Telegram Notifications

- Rate limited: 1 message/minute (burst 3)
- Deduplication by product hash
- Only sends if confidence ≥ 0.65
- Messages 180-260 characters

## 🔐 Security

- JWT authentication (8h expiration)
- Password hashing with bcrypt
- CORS restricted to production domain
- All secrets in environment variables
- SQL injection prevention via SQLAlchemy

## 🚀 Deployment

### GitHub Actions

1. **Scrapers**: Runs hourly via cron schedule
2. **Deploy**: Triggers on push to main branch

### Hostinger Setup

1. Create PostgreSQL database via hPanel
2. Configure FTP credentials as GitHub Secrets
3. Deploy Angular to `public_html/`
4. API runs on separate server (VPS/cloud)

## 📊 Monitoring

- Health check endpoint: `/health`
- Structured JSON logging
- Scraper metrics and error tracking
- AI confidence statistics

## 🧪 Testing

```bash
# Run scraper tests
cd scraper
pytest tests/

# Run API tests
cd api
pytest tests/

# Run Angular tests
cd web/angular
npm test
```

## 📚 API Documentation

Once the API is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

Private project - All rights reserved.
