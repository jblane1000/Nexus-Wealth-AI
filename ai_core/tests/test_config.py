import pytest
import os
import importlib

# Import the module itself, not just the class, to facilitate reloading
import ai_core.config

# We can still import the class for convenience in tests that don't need reloading
from ai_core.config import Config 


def test_config_defaults(monkeypatch):
    """Test that Config loads default values when env vars are not set."""
    # Ensure relevant env vars are unset for this test
    monkeypatch.delenv('AI_CORE_SECRET_KEY', raising=False)
    monkeypatch.delenv('ENVIRONMENT', raising=False)
    monkeypatch.delenv('DEBUG', raising=False)
    
    # Reload the module to ensure we get defaults if env vars were set previously
    reloaded_config_module = importlib.reload(ai_core.config)
    TestConfig = reloaded_config_module.Config
    
    assert TestConfig.SECRET_KEY == 'dev-secret-key-change-in-production'
    assert TestConfig.ENVIRONMENT == 'development'
    assert TestConfig.DEBUG is False
    assert TestConfig.is_development() is True
    assert TestConfig.is_production() is False
    assert TestConfig.is_testing() is False


def test_config_env_vars(monkeypatch):
    """Test that Config loads values from environment variables."""
    test_secret = 'test-secret-from-env'
    test_env = 'production'
    
    monkeypatch.setenv('AI_CORE_SECRET_KEY', test_secret)
    monkeypatch.setenv('ENVIRONMENT', test_env)
    monkeypatch.setenv('DEBUG', 'True')
    
    # --- Reload the config module AFTER setting env vars ---
    # This forces the class variables to be re-evaluated using the patched os.environ
    reloaded_config_module = importlib.reload(ai_core.config)
    # Use the Config class from the *reloaded* module for assertions
    TestConfig = reloaded_config_module.Config 
    # --------------------------------------------------------
    
    assert TestConfig.SECRET_KEY == test_secret
    assert TestConfig.ENVIRONMENT == test_env
    assert TestConfig.DEBUG is True
    assert TestConfig.is_development() is False
    assert TestConfig.is_production() is True
    assert TestConfig.is_testing() is False

def test_config_db_urls():
    """Test database URL construction (example)"""
    # Assuming default values are used here. If env vars could affect this,
    # this test might also need monkeypatch.delenv and potentially reloading.
    reloaded_config_module = importlib.reload(ai_core.config)
    TestConfig = reloaded_config_module.Config

    expected_uri = f"postgresql://nexus:nexuspassword@relational_db:5432/nexus_wealth"
    assert TestConfig.SQLALCHEMY_DATABASE_URI == expected_uri

# Add more tests for other configurations as needed
