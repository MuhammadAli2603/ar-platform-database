"""
Configuration module for AR Platform.

Manages environment variables and Supabase client initialization.
"""

import os
import logging
from typing import Optional
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Configure logging
log_level = os.getenv('LOG_LEVEL', 'INFO')
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)


class Config:
    """Application configuration from environment variables."""

    # Supabase
    SUPABASE_URL: str = os.getenv('SUPABASE_URL', '')
    SUPABASE_KEY: str = os.getenv('SUPABASE_KEY', '')
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv('SUPABASE_SERVICE_ROLE_KEY', '')
    STORAGE_BUCKET: str = os.getenv('STORAGE_BUCKET', 'ar-models')

    # AR Viewer
    BASE_AR_VIEWER_URL: str = os.getenv('BASE_AR_VIEWER_URL', 'http://localhost:8000/ar_viewer')

    # Environment
    ENVIRONMENT: str = os.getenv('ENVIRONMENT', 'development')

    # File constraints
    MAX_FILE_SIZE_MB: int = 5
    MAX_FILE_SIZE_BYTES: int = MAX_FILE_SIZE_MB * 1024 * 1024

    @classmethod
    def validate(cls) -> bool:
        """
        Validate that all required configuration is present.

        Returns:
            True if valid, raises ValueError otherwise
        """
        if not cls.SUPABASE_URL:
            raise ValueError("SUPABASE_URL not set in environment")
        if not cls.SUPABASE_KEY:
            raise ValueError("SUPABASE_KEY not set in environment")

        logger.info(f"Configuration loaded for environment: {cls.ENVIRONMENT}")
        return True


def get_supabase_client() -> Client:
    """
    Create and return a Supabase client instance.

    Returns:
        Configured Supabase client

    Raises:
        ValueError: If credentials are missing
    """
    Config.validate()

    client = create_client(
        Config.SUPABASE_URL,
        Config.SUPABASE_KEY
    )

    logger.debug("Supabase client created successfully")
    return client


def get_supabase_admin_client() -> Client:
    """
    Create and return a Supabase client with service role (admin) privileges.

    This client bypasses Row Level Security (RLS) policies and should only
    be used for server-side operations like file uploads.

    Returns:
        Configured Supabase client with admin privileges

    Raises:
        ValueError: If service role key is missing
    """
    if not Config.SUPABASE_URL:
        raise ValueError("SUPABASE_URL not set in environment")
    if not Config.SUPABASE_SERVICE_ROLE_KEY:
        raise ValueError(
            "SUPABASE_SERVICE_ROLE_KEY not set in environment. "
            "Get it from: Supabase Dashboard > Settings > API > service_role key"
        )

    client = create_client(
        Config.SUPABASE_URL,
        Config.SUPABASE_SERVICE_ROLE_KEY
    )

    logger.debug("Supabase admin client created successfully")
    return client


# Export commonly used items
__all__ = ['Config', 'get_supabase_client', 'get_supabase_admin_client', 'logger']
