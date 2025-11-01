"""
Configuration module for the sentiment analysis project.
Centralizes all configuration management and environment variable handling.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class that loads and validates environment variables"""

    def __init__(self):
        """Initialize configuration from environment variables"""
        # Base paths
        self.BASE_DIR = Path(__file__).parent.absolute()

        # Database configuration
        self.DB_NAME = os.getenv('DB_NAME', 'news.db')
        self.DB_PATH = self.BASE_DIR / self.DB_NAME

        # NewsAPI configuration
        self.NEWSAPI_KEY = os.getenv('NEWSAPI_KEY', '')
        self.NEWS_QUERY = os.getenv('NEWS_QUERY', 'technology')
        self.NEWS_PAGE_SIZE = int(os.getenv('NEWS_PAGE_SIZE', '20'))
        self.NEWS_DAYS_BACK = int(os.getenv('NEWS_DAYS_BACK', '1'))

        # Ollama configuration
        self.OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama3.2')
        self.OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
        self.OLLAMA_TEMPERATURE = float(os.getenv('OLLAMA_TEMPERATURE', '0.3'))

        # Logging configuration
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
        self.LOG_DIR = self.BASE_DIR / 'logs'
        self.LOG_FILE = os.getenv('LOG_FILE', 'sentiment_analysis.log')
        self.LOG_PATH = self.LOG_DIR / self.LOG_FILE
        self.LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        self.LOG_MAX_BYTES = int(os.getenv('LOG_MAX_BYTES', '10485760'))  # 10MB
        self.LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', '5'))

        # Ensure logs directory exists
        self.LOG_DIR.mkdir(exist_ok=True)

        # Sentiment analysis configuration
        self.SENTIMENT_POSITIVE_THRESHOLD = float(os.getenv('SENTIMENT_POSITIVE_THRESHOLD', '0.1'))
        self.SENTIMENT_NEGATIVE_THRESHOLD = float(os.getenv('SENTIMENT_NEGATIVE_THRESHOLD', '-0.1'))

        # Validate critical configuration
        self._validate()

    def _validate(self):
        """Validate critical configuration values"""
        errors = []

        # Validate numeric ranges
        if self.NEWS_PAGE_SIZE < 1 or self.NEWS_PAGE_SIZE > 100:
            errors.append("NEWS_PAGE_SIZE must be between 1 and 100")

        if self.NEWS_DAYS_BACK < 1 or self.NEWS_DAYS_BACK > 30:
            errors.append("NEWS_DAYS_BACK must be between 1 and 30")

        if self.OLLAMA_TEMPERATURE < 0 or self.OLLAMA_TEMPERATURE > 2:
            errors.append("OLLAMA_TEMPERATURE must be between 0 and 2")

        if self.SENTIMENT_POSITIVE_THRESHOLD <= self.SENTIMENT_NEGATIVE_THRESHOLD:
            errors.append("SENTIMENT_POSITIVE_THRESHOLD must be greater than SENTIMENT_NEGATIVE_THRESHOLD")

        if errors:
            raise ValueError(f"Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors))

    def require_newsapi_key(self):
        """
        Validate that NewsAPI key is configured.
        Raises ValueError if not found.
        """
        if not self.NEWSAPI_KEY:
            raise ValueError(
                "NEWSAPI_KEY not found in environment variables!\n\n"
                "Please do one of the following:\n"
                "1. Create a .env file with: NEWSAPI_KEY=your_api_key_here\n"
                "2. Set environment variable: export NEWSAPI_KEY=your_api_key_here\n\n"
                "Get your API key from: https://newsapi.org/"
            )
        return self.NEWSAPI_KEY

    def get_db_path(self, as_string=True):
        """
        Get the database path.

        Args:
            as_string: If True, return as string. If False, return as Path object.

        Returns:
            Database path
        """
        return str(self.DB_PATH) if as_string else self.DB_PATH

    def to_dict(self):
        """
        Convert configuration to dictionary (for logging/debugging).
        Excludes sensitive information like API keys.

        Returns:
            dict: Configuration dictionary
        """
        return {
            'BASE_DIR': str(self.BASE_DIR),
            'DB_NAME': self.DB_NAME,
            'DB_PATH': str(self.DB_PATH),
            'NEWSAPI_KEY': '***' if self.NEWSAPI_KEY else 'Not set',
            'NEWS_QUERY': self.NEWS_QUERY,
            'NEWS_PAGE_SIZE': self.NEWS_PAGE_SIZE,
            'NEWS_DAYS_BACK': self.NEWS_DAYS_BACK,
            'OLLAMA_MODEL': self.OLLAMA_MODEL,
            'OLLAMA_HOST': self.OLLAMA_HOST,
            'OLLAMA_TEMPERATURE': self.OLLAMA_TEMPERATURE,
            'LOG_LEVEL': self.LOG_LEVEL,
            'LOG_FILE': self.LOG_FILE,
            'SENTIMENT_POSITIVE_THRESHOLD': self.SENTIMENT_POSITIVE_THRESHOLD,
            'SENTIMENT_NEGATIVE_THRESHOLD': self.SENTIMENT_NEGATIVE_THRESHOLD,
        }

    def __repr__(self):
        """String representation of configuration"""
        return f"Config({self.to_dict()})"


# Global configuration instance
config = Config()


# Convenience function for getting configuration
def get_config():
    """
    Get the global configuration instance.

    Returns:
        Config: Configuration instance
    """
    return config


if __name__ == "__main__":
    # Test configuration loading
    print("Configuration loaded successfully!")
    print("\nConfiguration values:")
    for key, value in config.to_dict().items():
        print(f"  {key}: {value}")
