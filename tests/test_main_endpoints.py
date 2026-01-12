# Main Application Endpoints Tests
"""
Comprehensive test suite for main application endpoints including health checks,
artifact management, and system status verification.
"""

import pytest
import json
from unittest.mock import patch, Mock, AsyncMock
from fastapi import status


class TestMainApplicationEndpoints:
    """Test suite for main application endpoints and system functionality."""
    
    def test_application_status_endpoint(self, client):
        """Test the root application status endpoint."""
        response = client.get("/")
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["service"] == "Intelligent Document Processing & Code Generation Platform"
        assert data["status"] == "operational"
        assert data["version"] == "2.0.0"
        assert "capabilities" in data
        assert "document_processing" in data["capabilities"]
        assert "code_generation" in data["capabilities"]
        assert "specification_synthesis" in data["capabilities"]
        assert data["api_documentation"] == "/documentation"
    
    def test_system_health_endpoint(self, client):
        """Test the system health monitoring endpoint."""
        response = client.get("/system/health")
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["service_status"] == "operational"
        assert data["system_health"] == "excellent"
        assert data["version"] == "2.0.0"
        assert "capabilities" in data
        assert "uptime_status" in data
        assert "environment" in data
        
        # Verify all expected capabilities are present
        expected_capabilities = ["document_processing", "code_generation", "specification_synthesis"]
        for capability in expected_capabilities:
            assert capability in data["capabilities"]
    
    @patch('processors.directory_compressor.DirectoryCompressor.compress_directory_structure')
    def test_export_workspace_artifacts_success(self, mock_compress, client, mock_directory_structure):
        """Test successful workspace artifacts export."""
        # Mock the compression function to avoid actual file operations
        mock_compress.return_value = None
        
        # Create a test zip file for the response
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp_zip:
            tmp_zip.write(b"Mock ZIP content")
            tmp_zip.flush()
            
            # Mock the file system to return our test file
            with patch('pathlib.Path.exists', return_value=True), \
                 patch('fastapi.responses.FileResponse') as mock_file_response:
                
                mock_file_response.return_value = Mock()
                response = client.get("/artifacts/workspace/export")
                
                # Verify the compression was called with correct parameters
                mock_compress.assert_called_once_with("artifacts", "workspace_export.zip")
    
    def test_export_workspace_artifacts_failure(self, client):
        """Test workspace export failure handling."""
        with patch('processors.directory_compressor.DirectoryCompressor.compress_directory_structure', 
                   side_effect=Exception("Compression failed")):
            
            response = client.get("/artifacts/workspace/export")
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            assert "Workspace export failed" in data["detail"]
    
    @patch('intelligence.backend_architect.BackendArchitectureGenerator.synthesize_backend_structure')
    @patch('processors.artifact_packager.ArtifactProcessor.extract_generated_artifacts')
    @patch('processors.artifact_packager.ArtifactProcessor.create_compressed_archive')
    def test_retrieve_backend_artifacts_success(self, mock_archive, mock_extract, mock_synthesize, client):
        """Test successful backend artifacts retrieval."""
        # Setup mocks
        mock_ai_response = Mock(content="Generated backend code")
        mock_synthesize.return_value = mock_ai_response
        
        mock_artifacts = [{"file_path": "app.py", "content": "# Generated code"}]
        mock_extract.return_value = mock_artifacts
        
        mock_zip_buffer = Mock()
        mock_zip_buffer.getvalue.return_value = b"Mock ZIP content"
        mock_archive.return_value = mock_zip_buffer
        
        # Test the endpoint
        test_specification = "Create a FastAPI backend with user authentication"
        response = client.post(
            "/artifacts/backend/download",
            json={"technical_specification": test_specification}
        )
        
        # Verify response
        assert response.status_code == status.HTTP_200_OK
        assert response.headers["content-type"] == "application/zip"
        assert "backend_architecture.zip" in response.headers.get("content-disposition", "")
        
        # Verify mock calls
        mock_synthesize.assert_called_once()
        mock_extract.assert_called_once_with("Generated backend code")
        mock_archive.assert_called_once_with(mock_artifacts)
    
    def test_retrieve_backend_artifacts_missing_specification(self, client):
        """Test backend artifacts retrieval with missing specification."""
        response = client.post("/artifacts/backend/download", json={})
        
        # Should handle missing specification gracefully
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY]
    
    @patch('intelligence.backend_architect.BackendArchitectureGenerator.synthesize_backend_structure')
    def test_retrieve_backend_artifacts_generation_failure(self, mock_synthesize, client):
        """Test backend artifacts retrieval with generation failure."""
        mock_synthesize.side_effect = Exception("AI generation failed")
        
        test_specification = "Create a backend system"
        response = client.post(
            "/artifacts/backend/download",
            json={"technical_specification": test_specification}
        )
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert "Backend generation failed" in data["detail"]


class TestBackgroundTaskEndpoints:
    """Test suite for background task initiation endpoints."""
    
    @patch('intelligence.backend_architect.BackendArchitectureGenerator.synthesize_backend_structure')
    def test_initiate_backend_generation_success(self, mock_synthesize, client):
        """Test successful backend generation initiation."""
        test_specification = "Create a comprehensive backend system"
        
        response = client.post(
            "/generation/backend/initiate",
            json={"technical_spec": test_specification}
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["process"] == "initiated"
        assert data["operation"] == "backend_code_generation"
        assert data["status"] == "processing"
        assert "Backend architecture generation started successfully" in data["message"]
    
    def test_initiate_backend_generation_empty_specification(self, client):
        """Test backend generation with empty specification."""
        response = client.post(
            "/generation/backend/initiate",
            json={"technical_spec": ""}
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "Technical specification content is required" in data["detail"]
    
    def test_initiate_backend_generation_missing_specification(self, client):
        """Test backend generation with missing specification parameter."""
        response = client.post("/generation/backend/initiate", json={})
        
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY]
    
    @patch('intelligence.frontend_designer.FrontendDesignGenerator.synthesize_frontend_components')
    def test_initiate_frontend_generation_success(self, mock_synthesize, client):
        """Test successful frontend generation initiation."""
        test_specification = "Create a modern React frontend"
        
        response = client.post(
            "/generation/frontend/initiate",
            json={"interface_spec": test_specification}
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["process"] == "initiated"
        assert data["operation"] == "frontend_code_generation"
        assert data["status"] == "processing"
        assert "Frontend design generation started successfully" in data["message"]
    
    def test_initiate_frontend_generation_empty_specification(self, client):
        """Test frontend generation with empty specification."""
        response = client.post(
            "/generation/frontend/initiate",
            json={"interface_spec": ""}
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "Interface specification content is required" in data["detail"]


class TestApplicationStartup:
    """Test suite for application startup and configuration."""
    
    @patch('config.settings.ApplicationConfig.initialize_directories')
    def test_startup_event_initialization(self, mock_init_dirs):
        """Test that startup event properly initializes directories."""
        from main import startup_event
        
        # Execute startup event
        import asyncio
        asyncio.run(startup_event())
        
        # Verify initialization was called
        mock_init_dirs.assert_called_once()
    
    def test_cors_middleware_configuration(self, client):
        """Test that CORS middleware is properly configured."""
        # Test preflight request
        response = client.options(
            "/",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            }
        )
        
        # Should not return 404 or 405 for OPTIONS
        assert response.status_code != status.HTTP_404_NOT_FOUND
        assert response.status_code != status.HTTP_405_METHOD_NOT_ALLOWED
    
    def test_api_documentation_access(self, client):
        """Test that API documentation endpoints are accessible."""
        # Test OpenAPI documentation
        docs_response = client.get("/documentation")
        assert docs_response.status_code == status.HTTP_200_OK
        
        # Test ReDoc documentation
        redoc_response = client.get("/api-reference")
        assert redoc_response.status_code == status.HTTP_200_OK
        
        # Test OpenAPI schema
        openapi_response = client.get("/openapi.json")
        assert openapi_response.status_code == status.HTTP_200_OK
        
        # Verify schema contains expected information
        schema = openapi_response.json()
        assert schema["info"]["title"] == "Intelligent Document Processing & Code Generation Platform"
        assert schema["info"]["version"] == "2.0.0"


class TestErrorHandling:
    """Test suite for error handling across main endpoints."""
    
    def test_404_for_nonexistent_endpoints(self, client):
        """Test that nonexistent endpoints return 404."""
        response = client.get("/nonexistent/endpoint")
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_405_for_wrong_http_methods(self, client):
        """Test that wrong HTTP methods return 405."""
        # GET on POST endpoint
        response = client.get("/generation/backend/initiate")
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        
        # POST on GET endpoint
        response = client.post("/system/health")
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    
    def test_invalid_json_handling(self, client):
        """Test handling of invalid JSON in request bodies."""
        response = client.post(
            "/generation/backend/initiate",
            data="invalid json data",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
