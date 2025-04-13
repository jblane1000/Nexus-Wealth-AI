import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """
    Configuration settings for the Web UI application
    """
    # Flask settings
    SECRET_KEY = os.environ.get('WEB_UI_SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.environ.get('WEB_UI_DEBUG', 'False').lower() == 'true'
    
    # Database settings
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 
        'sqlite:///nexus_wealth.db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # API settings
    AI_CORE_URL = os.environ.get('AI_CORE_URL', 'http://ai_core:5000')
    
    # Session settings
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours
    
    # Security settings
    WTF_CSRF_ENABLED = True
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
