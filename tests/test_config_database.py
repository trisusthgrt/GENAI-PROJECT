# Configuration and Database Tests
"""
Test suite for configuration management and database functionality
including settings validation, database connections, and ORM models.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, Mock, MagicMock
import asyncio


class TestApplicationConfig:
    """Test suite for ApplicationConfig class."""
    
    @patch.dict(os.environ, {
        'EXECUTION_ENVIRONMENT': 'test',
        'DEBUG_MODE': 'true',
        'LOG_VERBOSITY': 'DEBUG',
        'DOCUMENT_STORAGE_PATH': '/tmp/test_docs',
        'GENERATED_ARTIFACTS_PATH': '/tmp/test_artifacts'
    })
    def test_config_environment_loading(self):
        """Test configuration loading from environment variables."""
        from config.settings import ApplicationConfig
        
        # Test environment variable loading
        assert ApplicationConfig.EXECUTION_ENVIRONMENT == "test"
        assert ApplicationConfig.DEBUG_MODE is True
        assert ApplicationConfig.LOG_VERBOSITY == "DEBUG"
        assert str(ApplicationConfig.DOCUMENT_STORAGE_PATH) == "/tmp/test_docs"
        assert str(ApplicationConfig.GENERATED_ARTIFACTS_PATH) == "/tmp/test_artifacts"
    
    def test_config_default_values(self):
        """Test configuration default values when environment variables are not set."""
        # Clear environment variables for this test
        env_vars_to_clear = [
            'EXECUTION_ENVIRONMENT', 'DEBUG_MODE', 'LOG_VERBOSITY',
            'DOCUMENT_STORAGE_PATH', 'GENERATED_ARTIFACTS_PATH'
        ]
        
        with patch.dict(os.environ, {}, clear=True):
            # Reimport to get fresh instance with defaults
            import importlib
            from config import settings
            importlib.reload(settings)
            
            # Test default values
            assert settings.ApplicationConfig.EXECUTION_ENVIRONMENT == "development"
            assert settings.ApplicationConfig.DEBUG_MODE is True  # Default "true" becomes True
            assert settings.ApplicationConfig.LOG_VERBOSITY == "INFO"
            assert settings.ApplicationConfig.SUPPORTED_DOCUMENT_FORMATS == ["pdf", "docx", "md", "txt"]
            assert settings.ApplicationConfig.MAX_DOCUMENT_SIZE_MB == 50
    
    def test_initialize_directories(self):
        """Test directory initialization functionality."""
        from config.settings import ApplicationConfig
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Mock the directory paths
            with patch.object(ApplicationConfig, 'DOCUMENT_STORAGE_PATH', temp_path / "docs"), \
                 patch.object(ApplicationConfig, 'GENERATED_ARTIFACTS_PATH', temp_path / "artifacts"), \
                 patch.object(ApplicationConfig, 'TEMPORARY_WORKSPACE', temp_path / "temp"):
                
                ApplicationConfig.initialize_directories()
                
                # Verify directories were created
                assert (temp_path / "docs").exists()
                assert (temp_path / "artifacts").exists()
                assert (temp_path / "temp").exists()
    
    def test_get_log_file_path(self):
        """Test log file path generation."""
        from config.settings import ApplicationConfig
        
        with patch.object(ApplicationConfig, 'EXECUTION_ENVIRONMENT', 'test'):
            log_path = ApplicationConfig.get_log_file_path("document_processor")
            
            expected_path = Path("logs") / "document_processor_test.log"
            assert log_path == expected_path
    
    def test_config_type_conversion(self):
        """Test proper type conversion for configuration values."""
        from config.settings import ApplicationConfig
        
        # Test integer conversion
        with patch.dict(os.environ, {'MAX_DOCUMENT_SIZE_MB': '100'}):
            import importlib
            from config import settings
            importlib.reload(settings)
            
            assert settings.ApplicationConfig.MAX_DOCUMENT_SIZE_MB == 100
            assert isinstance(settings.ApplicationConfig.MAX_DOCUMENT_SIZE_MB, int)
        
        # Test boolean conversion
        with patch.dict(os.environ, {'DEBUG_MODE': 'false'}):
            import importlib
            from config import settings
            importlib.reload(settings)
            
            assert settings.ApplicationConfig.DEBUG_MODE is False


class TestDatabaseArchitecture:
    """Test suite for DatabaseArchitecture class."""
    
    def test_database_initialization_default_urls(self):
        """Test database initialization with default URLs."""
        from database.db import DatabaseArchitecture
        
        db_arch = DatabaseArchitecture()
        
        assert "sqlite" in db_arch.database_url
        assert "sqlite" in db_arch.async_database_url
        assert "aiosqlite" in db_arch.async_database_url
    
    def test_database_initialization_custom_urls(self):
        """Test database initialization with custom URLs."""
        from database.db import DatabaseArchitecture
        
        custom_sync_url = "postgresql://user:pass@localhost/testdb"
        custom_async_url = "postgresql+asyncpg://user:pass@localhost/testdb"
        
        db_arch = DatabaseArchitecture(
            database_url=custom_sync_url,
            async_url=custom_async_url
        )
        
        assert db_arch.database_url == custom_sync_url
        assert db_arch.async_database_url == custom_async_url
    
    @patch('database.db.create_engine')
    @patch('database.db.sessionmaker')
    def test_initialize_synchronous_engine(self, mock_sessionmaker, mock_create_engine):
        """Test synchronous engine initialization."""
        from database.db import DatabaseArchitecture
        
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine
        mock_session_factory = Mock()
        mock_sessionmaker.return_value = mock_session_factory
        
        db_arch = DatabaseArchitecture()
        db_arch.initialize_synchronous_engine()
        
        # Verify engine creation
        mock_create_engine.assert_called_once()
        assert db_arch._sync_engine == mock_engine
        
        # Verify session factory creation
        mock_sessionmaker.assert_called_once()
        assert db_arch._session_factory == mock_session_factory
    
    @patch('database.db.create_async_engine')
    @patch('database.db.async_sessionmaker')
    def test_initialize_asynchronous_engine(self, mock_async_sessionmaker, mock_create_async_engine):
        """Test asynchronous engine initialization."""
        from database.db import DatabaseArchitecture
        
        mock_async_engine = Mock()
        mock_create_async_engine.return_value = mock_async_engine
        mock_async_session_factory = Mock()
        mock_async_sessionmaker.return_value = mock_async_session_factory
        
        db_arch = DatabaseArchitecture()
        db_arch.initialize_asynchronous_engine()
        
        # Verify async engine creation
        mock_create_async_engine.assert_called_once()
        assert db_arch._async_engine == mock_async_engine
        
        # Verify async session factory creation
        mock_async_sessionmaker.assert_called_once()
        assert db_arch._async_session_factory == mock_async_session_factory
    
    def test_get_session_context_manager(self):
        """Test synchronous session context manager."""
        from database.db import DatabaseArchitecture
        
        db_arch = DatabaseArchitecture()
        
        # Mock session factory and session
        mock_session = Mock()
        mock_session_factory = Mock(return_value=mock_session)
        db_arch._session_factory = mock_session_factory
        
        # Test successful session usage
        with db_arch.get_session() as session:
            assert session == mock_session
            assert db_arch._connection_stats["active_sessions"] == 1
        
        # Verify session was committed and closed
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()
        assert db_arch._connection_stats["active_sessions"] == 0
    
    def test_get_session_context_manager_with_exception(self):
        """Test session context manager with exception handling."""
        from database.db import DatabaseArchitecture
        
        db_arch = DatabaseArchitecture()
        
        # Mock session factory and session
        mock_session = Mock()
        mock_session_factory = Mock(return_value=mock_session)
        db_arch._session_factory = mock_session_factory
        
        # Test exception handling
        with pytest.raises(ValueError):
            with db_arch.get_session() as session:
                assert session == mock_session
                raise ValueError("Test exception")
        
        # Verify session was rolled back and closed
        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()
        assert db_arch._connection_stats["active_sessions"] == 0
    
    @pytest.mark.asyncio
    async def test_get_async_session_context_manager(self):
        """Test asynchronous session context manager."""
        from database.db import DatabaseArchitecture
        
        db_arch = DatabaseArchitecture()
        
        # Mock async session factory and session
        mock_async_session = Mock()
        mock_async_session.commit = AsyncMock()
        mock_async_session.close = AsyncMock()
        mock_async_session_factory = Mock(return_value=mock_async_session)
        db_arch._async_session_factory = mock_async_session_factory
        
        # Test successful async session usage
        async with db_arch.get_async_session() as session:
            assert session == mock_async_session
            assert db_arch._connection_stats["active_sessions"] == 1
        
        # Verify async session was committed and closed
        mock_async_session.commit.assert_called_once()
        mock_async_session.close.assert_called_once()
        assert db_arch._connection_stats["active_sessions"] == 0
    
    @pytest.mark.asyncio
    async def test_get_async_session_with_exception(self):
        """Test async session context manager with exception handling."""
        from database.db import DatabaseArchitecture
        
        db_arch = DatabaseArchitecture()
        
        # Mock async session factory and session
        mock_async_session = Mock()
        mock_async_session.rollback = AsyncMock()
        mock_async_session.close = AsyncMock()
        mock_async_session_factory = Mock(return_value=mock_async_session)
        db_arch._async_session_factory = mock_async_session_factory
        
        # Test exception handling
        with pytest.raises(ValueError):
            async with db_arch.get_async_session() as session:
                assert session == mock_async_session
                raise ValueError("Test async exception")
        
        # Verify async session was rolled back and closed
        mock_async_session.rollback.assert_called_once()
        mock_async_session.close.assert_called_once()
    
    def test_get_connection_statistics(self):
        """Test connection statistics retrieval."""
        from database.db import DatabaseArchitecture
        
        db_arch = DatabaseArchitecture()
        db_arch._connection_stats["total_connections"] = 5
        db_arch._connection_stats["active_sessions"] = 2
        
        stats = db_arch.get_connection_statistics()
        
        assert stats["total_connections"] == 5
        assert stats["active_sessions"] == 2
        assert "engine_status" in stats
        assert "configuration" in stats
        assert stats["engine_status"]["sync_engine_initialized"] is False
        assert stats["engine_status"]["async_engine_initialized"] is False
    
    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test database health check functionality."""
        from database.db import DatabaseArchitecture
        
        db_arch = DatabaseArchitecture()
        
        # Test with no engines initialized
        health_status = await db_arch.health_check()
        
        assert health_status["database_connectivity"] == "unknown"
        assert health_status["sync_engine_status"] == "not_initialized"
        assert health_status["async_engine_status"] == "not_initialized"
        
        # Test with mock engines
        mock_sync_engine = Mock()
        mock_async_engine = Mock()
        db_arch._sync_engine = mock_sync_engine
        db_arch._async_engine = mock_async_engine
        
        # Mock session managers
        mock_session = Mock()
        mock_session.execute = Mock()
        mock_session_context = Mock()
        mock_session_context.__enter__ = Mock(return_value=mock_session)
        mock_session_context.__exit__ = Mock(return_value=None)
        
        mock_async_session = Mock()
        mock_async_session.execute = AsyncMock()
        mock_async_session_context = Mock()
        mock_async_session_context.__aenter__ = AsyncMock(return_value=mock_async_session)
        mock_async_session_context.__aexit__ = AsyncMock(return_value=None)
        
        with patch.object(db_arch, 'get_session', return_value=mock_session_context), \
             patch.object(db_arch, 'get_async_session', return_value=mock_async_session_context):
            
            health_status = await db_arch.health_check()
            
            assert health_status["sync_engine_status"] == "healthy"
            assert health_status["async_engine_status"] == "healthy"
            assert health_status["database_connectivity"] == "operational"


class TestDatabaseModels:
    """Test suite for database models and schemas."""
    
    def test_document_entity_model(self):
        """Test DocumentEntity model creation and attributes."""
        from models import DocumentEntity, DocumentType, ProcessingStatus
        
        # Test model creation
        document = DocumentEntity(
            filename="test.pdf",
            document_type=DocumentType.PDF,
            file_size_bytes=1024,
            content_hash="abc123",
            processing_status=ProcessingStatus.PENDING
        )
        
        assert document.filename == "test.pdf"
        assert document.document_type == DocumentType.PDF
        assert document.file_size_bytes == 1024
        assert document.content_hash == "abc123"
        assert document.processing_status == ProcessingStatus.PENDING
        
        # Test string representation
        document.id = 1
        assert "DocumentEntity(id=1" in repr(document)
        assert "test.pdf" in repr(document)
    
    def test_specification_entity_model(self):
        """Test SpecificationEntity model creation and relationships."""
        from models import SpecificationEntity
        
        specification = SpecificationEntity(
            document_id=1,
            specification_type="frontend",
            specification_content="# Frontend Specification",
            version=1,
            complexity_score=7,
            completeness_rating=9
        )
        
        assert specification.document_id == 1
        assert specification.specification_type == "frontend"
        assert specification.specification_content == "# Frontend Specification"
        assert specification.version == 1
        assert specification.complexity_score == 7
        assert specification.completeness_rating == 9
    
    def test_code_generation_job_model(self):
        """Test CodeGenerationJob model creation and attributes."""
        from models import CodeGenerationJob, ProcessingStatus, ArchitectureType
        
        job = CodeGenerationJob(
            document_id=1,
            architecture_type=ArchitectureType.BACKEND,
            job_status=ProcessingStatus.IN_PROGRESS,
            progress_percentage=50
        )
        
        assert job.document_id == 1
        assert job.architecture_type == ArchitectureType.BACKEND
        assert job.job_status == ProcessingStatus.IN_PROGRESS
        assert job.progress_percentage == 50
    
    def test_pydantic_models_validation(self):
        """Test Pydantic model validation."""
        from models import DocumentUploadRequest, SpecificationGenerationRequest
        
        # Test valid document upload request
        upload_request = DocumentUploadRequest(
            filename="test.pdf",
            content_base64="base64encodedcontent=="
        )
        
        assert upload_request.filename == "test.pdf"
        assert upload_request.content_base64 == "base64encodedcontent=="
        
        # Test filename validation
        with pytest.raises(ValueError):
            DocumentUploadRequest(
                filename="test.xyz",  # Unsupported format
                content_base64="content"
            )
        
        # Test specification generation request
        spec_request = SpecificationGenerationRequest(
            document_id=1,
            specification_types=["frontend", "backend"]
        )
        
        assert spec_request.document_id == 1
        assert spec_request.specification_types == ["frontend", "backend"]
        
        # Test invalid specification type
        with pytest.raises(ValueError):
            SpecificationGenerationRequest(
                document_id=1,
                specification_types=["invalid_type"]
            )
    
    def test_model_registry_functionality(self):
        """Test ModelRegistry functionality."""
        from models import ModelRegistry, DocumentEntity, DocumentUploadRequest, DocumentAnalysisResponse
        
        # Test get_model functionality
        assert ModelRegistry.get_model("orm", "document") == DocumentEntity
        assert ModelRegistry.get_model("request", "document_upload") == DocumentUploadRequest
        assert ModelRegistry.get_model("response", "document_analysis") == DocumentAnalysisResponse
        
        # Test invalid category/model
        assert ModelRegistry.get_model("invalid", "model") is None
        assert ModelRegistry.get_model("orm", "invalid") is None
        
        # Test list_models functionality
        model_list = ModelRegistry.list_models()
        
        assert "orm_models" in model_list
        assert "request_models" in model_list
        assert "response_models" in model_list
        assert "document" in model_list["orm_models"]
        assert "document_upload" in model_list["request_models"]
        assert "document_analysis" in model_list["response_models"]


class TestAdvancedLogging:
    """Test suite for advanced logging functionality."""
    
    def test_intelligent_log_manager_basic_setup(self):
        """Test basic IntelligentLogManager setup."""
        from utils.advanced_logger import IntelligentLogManager
        
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            
            logger = IntelligentLogManager.configure_service_logger(
                service_name="test_service",
                log_file_path=str(log_file),
                log_level="INFO",
                enable_console=False,
                structured_logging=False
            )
            
            assert logger.name == "test_service"
            assert logger.level == 20  # INFO level
            
            # Test logging functionality
            logger.info("Test message")
            
            # Verify log file was created and has content
            assert log_file.exists()
            log_content = log_file.read_text()
            assert "Test message" in log_content
    
    def test_structured_logging_format(self):
        """Test structured JSON logging format."""
        from utils.advanced_logger import IntelligentLogManager
        import json
        
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "structured.log"
            
            logger = IntelligentLogManager.configure_service_logger(
                service_name="structured_test",
                log_file_path=str(log_file),
                log_level="INFO",
                enable_console=False,
                structured_logging=True
            )
            
            logger.info("Structured log message")
            
            # Verify structured log format
            assert log_file.exists()
            log_content = log_file.read_text()
            
            # Parse as JSON
            log_lines = [line for line in log_content.strip().split('\n') if line]
            assert len(log_lines) >= 1
            
            log_entry = json.loads(log_lines[0])
            assert log_entry["service"] == "structured_test"
            assert log_entry["level"] == "INFO"
            assert log_entry["message"] == "Structured log message"
            assert "timestamp" in log_entry
    
    def test_performance_monitoring_methods(self):
        """Test performance monitoring enhanced methods."""
        from utils.advanced_logger import IntelligentLogManager
        
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "performance.log"
            
            logger = IntelligentLogManager.configure_service_logger(
                service_name="perf_test",
                log_file_path=str(log_file),
                structured_logging=True
            )
            
            # Test performance logging
            logger.log_performance("Database query", 0.125, query_type="SELECT")
            
            # Test business event logging
            logger.log_business_event("user_registration", {"user_id": 123, "source": "web"})
            
            # Verify logs contain performance and business event data
            log_content = log_file.read_text()
            assert "Database query" in log_content
            assert "user_registration" in log_content
            assert "performance_metric" in log_content
            assert "business_event" in log_content
    
    def test_create_system_logger(self):
        """Test system logger creation with defaults."""
        from utils.advanced_logger import IntelligentLogManager
        
        logger = IntelligentLogManager.create_system_logger("test_component")
        
        assert logger.name == "system.test_component"
        assert hasattr(logger, 'log_performance')
        assert hasattr(logger, 'log_business_event')
    
    def test_legacy_setup_logger_compatibility(self):
        """Test legacy setup_logger function compatibility."""
        from utils.advanced_logger import setup_logger
        import logging
        
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "legacy.log"
            
            logger = setup_logger("legacy_test", str(log_file), logging.DEBUG)
            
            assert logger.name == "legacy_test"
            assert logger.level == logging.DEBUG
            
            logger.debug("Legacy debug message")
            
            assert log_file.exists()
            log_content = log_file.read_text()
            assert "Legacy debug message" in log_content
