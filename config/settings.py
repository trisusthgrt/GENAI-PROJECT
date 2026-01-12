# Advanced Configuration Management System
"""
Environment-aware configuration orchestrator for document processing platform.
Implements dynamic configuration loading with validation and defaults.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class ApplicationConfig:
    """
    Centralized configuration manager providing environment-specific settings
    for the document processing and code generation platform.
    """
    
    # Environment Settings
    EXECUTION_ENVIRONMENT = os.getenv("EXECUTION_ENVIRONMENT", "development")
    DEBUG_MODE = os.getenv("DEBUG_MODE", "true").lower() == "true"
    
    # Logging Configuration
    LOG_VERBOSITY = os.getenv("LOG_VERBOSITY", "INFO")
    LOG_ROTATION_SIZE = int(os.getenv("LOG_ROTATION_SIZE", "10485760"))  # 10MB
    
    # Directory Management
    DOCUMENT_STORAGE_PATH = Path(os.getenv("DOCUMENT_STORAGE_PATH", "uploads"))
    GENERATED_ARTIFACTS_PATH = Path(os.getenv("GENERATED_ARTIFACTS_PATH", "artifacts"))
    TEMPORARY_WORKSPACE = Path(os.getenv("TEMPORARY_WORKSPACE", "temp"))
    
    # Processing Configuration
    MAX_DOCUMENT_SIZE_MB = int(os.getenv("MAX_DOCUMENT_SIZE_MB", "50"))
    SUPPORTED_DOCUMENT_FORMATS = ["pdf", "docx", "md", "txt"]
    
    @classmethod
    def initialize_directories(cls) -> None:
        """Create necessary directories if they don't exist."""
        for directory in [cls.DOCUMENT_STORAGE_PATH, cls.GENERATED_ARTIFACTS_PATH, cls.TEMPORARY_WORKSPACE]:
            directory.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_log_file_path(cls, service_name: str) -> Path:
        """Generate log file path for a specific service."""
        return Path("logs") / f"{service_name}_{cls.EXECUTION_ENVIRONMENT}.log"