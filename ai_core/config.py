import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration settings for AI Core"""
    
    # Flask configuration
    SECRET_KEY = os.environ.get('AI_CORE_SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    # Environment
    ENVIRONMENT = os.environ.get('ENVIRONMENT', 'development')
    
    # Vector database configuration
    VECTOR_DB_HOST = os.environ.get('VECTOR_DB_HOST', 'vector_db')
    VECTOR_DB_PORT = int(os.environ.get('VECTOR_DB_PORT', 6333))
    VECTOR_DB_COLLECTION = os.environ.get('VECTOR_DB_COLLECTION', 'nexus_wealth_knowledge')
    
    # Time series database configuration (InfluxDB)
    TIMESERIES_DB_HOST = os.environ.get('TIMESERIES_DB_HOST', 'timeseries_db')
    TIMESERIES_DB_PORT = int(os.environ.get('TIMESERIES_DB_PORT', 8086))
    TIMESERIES_DB_ORG = os.environ.get('TIMESERIES_DB_ORG', 'nexuswealth')
    TIMESERIES_DB_BUCKET = os.environ.get('TIMESERIES_DB_BUCKET', 'market_data')
    TIMESERIES_DB_TOKEN = os.environ.get('TIMESERIES_DB_TOKEN', '')
    
    # Relational database configuration (PostgreSQL)
    POSTGRES_HOST = os.environ.get('POSTGRES_HOST', 'relational_db')
    POSTGRES_PORT = int(os.environ.get('POSTGRES_PORT', 5432))
    POSTGRES_USER = os.environ.get('POSTGRES_USER', 'nexus')
    POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD', 'nexuspassword')
    POSTGRES_DB = os.environ.get('POSTGRES_DB', 'nexus_wealth')
    SQLALCHEMY_DATABASE_URI = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    
    # AI Model endpoints
    AI_MODEL_ENDPOINT = os.environ.get('AI_MODEL_ENDPOINT', '')
    RAG_MODEL_ENDPOINT = os.environ.get('RAG_MODEL_ENDPOINT', '')
    
    # Market data API keys (placeholders)
    ALPHA_VANTAGE_API_KEY = os.environ.get('ALPHA_VANTAGE_API_KEY', '')
    YAHOO_FINANCE_API_KEY = os.environ.get('YAHOO_FINANCE_API_KEY', '')
    COINMARKETCAP_API_KEY = os.environ.get('COINMARKETCAP_API_KEY', '')
    NEWS_API_KEY = os.environ.get('NEWS_API_KEY', '')
    
    # Brokerage APIs (placeholders)
    ALPACA_API_KEY = os.environ.get('ALPACA_API_KEY', '')
    ALPACA_API_SECRET = os.environ.get('ALPACA_API_SECRET', '')
    
    # Worker AI configuration
    WORKER_PING_INTERVAL = int(os.environ.get('WORKER_PING_INTERVAL', 30))  # seconds
    WORKER_TIMEOUT = int(os.environ.get('WORKER_TIMEOUT', 120))  # seconds
    
    # System constraints
    MAX_CONCURRENT_TASKS = int(os.environ.get('MAX_CONCURRENT_TASKS', 10))
    TASK_TIMEOUT = int(os.environ.get('TASK_TIMEOUT', 300))  # seconds
    
    # Redis configuration (for task queue)
    REDIS_HOST = os.environ.get('REDIS_HOST', 'redis')
    REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
    REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD', '')
    
    @classmethod
    def is_production(cls):
        """Check if running in production environment"""
        return cls.ENVIRONMENT.lower() == 'production'
    
    @classmethod
    def is_development(cls):
        """Check if running in development environment"""
        return cls.ENVIRONMENT.lower() == 'development'
    
    @classmethod
    def is_testing(cls):
        """Check if running in test environment"""
        return cls.ENVIRONMENT.lower() == 'testing'
