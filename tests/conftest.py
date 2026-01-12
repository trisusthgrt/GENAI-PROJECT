# Test Configuration and Fixtures
"""
Shared test configuration, fixtures, and utilities for the document processing platform.
Provides common setup for all test modules with proper isolation and cleanup.
"""

import pytest
import asyncio
import tempfile
import os
from pathlib import Path
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch
import io

# Import the main application
from main import document_processor_api

@pytest.fixture
def client():
    """
    Create a test client for the FastAPI application.
    Provides isolated testing environment for API endpoints.
    """
    return TestClient(document_processor_api)

@pytest.fixture
def sample_pdf_content():
    """Mock PDF file content for testing document upload."""
    return b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 12 Tf\n50 750 Td\n(Test Document) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000206 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n299\n%%EOF"

@pytest.fixture
def sample_docx_content():
    """Mock DOCX file content for testing."""
    return b"PK\x03\x04\x14\x00\x00\x00\x08\x00\x00\x00!\x00Test Document Content"

@pytest.fixture
def sample_markdown_content():
    """Sample markdown content for testing."""
    return """# Software Requirements Specification

## 1. Introduction
This document outlines the requirements for a web-based task management system.

## 2. Functional Requirements
- User authentication and authorization
- Task creation and management
- Dashboard with analytics
- Real-time notifications

## 3. Non-Functional Requirements
- Performance: Response time < 2 seconds
- Security: OAuth 2.0 authentication
- Scalability: Support 1000+ concurrent users
""".encode('utf-8')

@pytest.fixture
def sample_requirements_text():
    """Sample requirements text for specification generation."""
    return """
    Create a modern e-commerce platform with the following features:
    
    Frontend Requirements:
    - Responsive web design with mobile support
    - Product catalog with search and filtering
    - Shopping cart and checkout process
    - User account management
    - Order history and tracking
    
    Backend Requirements:
    - RESTful API with JWT authentication
    - Product management system
    - Order processing and payment integration
    - User management with role-based access
    - Inventory tracking and management
    - Email notification system
    """

@pytest.fixture
def technical_specification():
    """Sample technical specification for code generation."""
    return """
    Technical Specification: E-commerce Platform
    
    Backend Architecture:
    - FastAPI framework with Python 3.9+
    - PostgreSQL database with SQLAlchemy ORM
    - Redis for caching and session management
    - Celery for background task processing
    - JWT-based authentication system
    
    API Endpoints:
    - POST /auth/login - User authentication
    - GET /products - Product listing with pagination
    - POST /orders - Order creation
    - GET /users/profile - User profile management
    
    Frontend Architecture:
    - React.js with TypeScript
    - Redux for state management
    - Material-UI component library
    - Responsive design with CSS Grid
    """

@pytest.fixture
def mock_ai_response():
    """Mock AI agent response for testing."""
    return Mock(content="Generated code content from AI agents")

@pytest.fixture
def mock_document_analysis_result():
    """Mock document analysis result."""
    return {
        "extracted_text": "Sample extracted text from document",
        "document_sections": ["Introduction", "Requirements", "Conclusion"],
        "metadata": {
            "document_type": "pdf",
            "total_pages": 5,
            "processed_pages": 5
        }
    }

@pytest.fixture
def mock_specification_result():
    """Mock specification generation result."""
    return (
        "# Frontend Technical Specification\n\nDetailed frontend requirements...",
        "# Backend Technical Specification\n\nDetailed backend requirements..."
    )

@pytest.fixture
def temporary_file():
    """Create a temporary file for testing file operations."""
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(b"Test file content")
        tmp_file.flush()
        yield tmp_file.name
    
    # Cleanup
    try:
        os.unlink(tmp_file.name)
    except FileNotFoundError:
        pass

@pytest.fixture
def mock_directory_structure():
    """Create a mock directory structure for testing."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create some test files
        test_files = [
            "test1.py",
            "test2.js",
            "subfolder/test3.html"
        ]
        
        for file_path in test_files:
            full_path = Path(tmp_dir) / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(f"Content of {file_path}")
        
        yield tmp_dir

@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment with necessary directories and cleanup."""
    # Create test directories
    test_dirs = ["artifacts", "logs", "temp"]
    for dir_name in test_dirs:
        Path(dir_name).mkdir(exist_ok=True)
    
    yield
    
    # Cleanup after tests
    import shutil
    for dir_name in test_dirs:
        if Path(dir_name).exists():
            try:
                shutil.rmtree(dir_name)
            except PermissionError:
                pass  # Handle Windows file locking issues

# Mock patches for external dependencies
@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for AI agent testing."""
    with patch('intelligence.requirement_synthesizer.openai_api_key', 'test-api-key'):
        yield

@pytest.fixture
def mock_document_processor():
    """Mock document processor for testing."""
    with patch('processors.document_analyzer.DocumentProcessor') as mock:
        yield mock

@pytest.fixture
def mock_backend_architect():
    """Mock backend architecture generator."""
    with patch('intelligence.backend_architect.BackendArchitectureGenerator') as mock:
        yield mock

@pytest.fixture
def mock_frontend_designer():
    """Mock frontend design generator."""
    with patch('intelligence.frontend_designer.FrontendDesignGenerator') as mock:
        yield mock

# Event loop fixture for async testing
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# Test data constants
TEST_API_BASE_URL = "http://localhost:8000"
TEST_TIMEOUT = 30  # seconds
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
