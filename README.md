# Nexus Wealth AI

An autonomous AI-driven financial institution for investment management and trading.

## Architecture

The system consists of the following components:

1. **Web UI**: User-facing web application for interaction with the system
2. **AI Core**: Contains the main AI agent (CEO AI), RAG system, and MCU server
3. **Worker AIs**: Specialized AI agents for specific tasks:
   - Equity Trader: Handles stock/ETF research and trading
   - Crypto Trader: Handles cryptocurrency analysis and trading
   - Risk & Compliance Monitor: Ensures portfolio compliance with rules and regulations

## System Requirements

- Docker and Docker Compose
- Python 3.9+

## Getting Started

1. Clone the repository
2. Set up environment variables (see `.env.example`)
3. Run `docker-compose up -d` to start the system
4. Access the Web UI at http://localhost:8000

## Components

### Web UI
- Flask-based web application
- User authentication and onboarding
- Dashboard for portfolio monitoring
- Goal setting and risk profiling

### AI Core
- CEO AI Agent: Central decision engine
- RAG System: Retrieval-augmented generation for information retrieval
- MCU Server: Communication hub between CEO AI and Worker AIs

### Worker AIs
- Equity Trader: Research and execute trades for stocks/ETFs
- Crypto Trader: Analyze and trade cryptocurrencies
- Risk & Compliance Monitor: Check portfolio against rules and constraints

## Communication Flow
- Web UI ↔ CEO AI: REST API calls
- CEO AI ↔ RAG: Internal communication
- CEO AI ↔ MCU: Internal communication
- CEO AI ↔ Worker AIs (via MCU): Docker networking
- Worker AIs → External APIs: Direct communication

## Security and Compliance
- HTTPS for secure communication
- Input validation and secure authentication
- PIPEDA considerations for data handling
- Compliance with Ontario/Canada trading regulations
