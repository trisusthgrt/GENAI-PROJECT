# Integration Tests
"""
Comprehensive integration test suite for testing end-to-end workflows,
API interactions, and system behavior under realistic usage scenarios.
"""

import pytest
import asyncio
import tempfile
import io
from pathlib import Path
from unittest.mock import patch, Mock, AsyncMock
from fastapi import status
import zipfile
import json


class TestEndToEndDocumentProcessing:
    """Integration tests for complete document processing workflows."""
    
    @patch('processors.document_analyzer.DocumentProcessor.analyze_document_content')
    @patch('intelligence.requirement_synthesizer.RequirementSynthesizer.process_requirements')
    @patch('processors.document_renderer.DocumentRenderer.render_to_pdf')
    def test_complete_document_processing_workflow(self, mock_render, mock_synthesize, mock_analyze, client, sample_pdf_content):
        """Test complete document processing from upload to PDF generation."""
        
        # Mock document analysis
        mock_analyze.return_value = {
            "extracted_text": "Complete e-commerce platform requirements...",
            "document_sections": ["Introduction", "Features", "Technical Requirements"],
            "metadata": {"document_type": "pdf", "total_pages": 5}
        }
        
        # Mock specification synthesis
        mock_synthesize.return_value = (
            "# Frontend Technical Specification\n\nReact-based frontend...",
            "# Backend Technical Specification\n\nFastAPI backend..."
        )
        
        # Mock PDF rendering
        mock_render.return_value = b"Mock PDF content"
        
        # Step 1: Upload and analyze document
        files = {
            "document": ("requirements.pdf", io.BytesIO(sample_pdf_content), "application/pdf")
        }
        
        analysis_response = client.post("/documents/analyze", files=files)
        assert analysis_response.status_code == status.HTTP_200_OK
        
        # Step 2: Process document and generate specifications
        files = {
            "uploaded_file": ("requirements.pdf", io.BytesIO(sample_pdf_content), "application/pdf")
        }
        
        processing_response = client.post("/documents/process-and-synthesize", files=files)
        assert processing_response.status_code == status.HTTP_200_OK
        
        processing_data = processing_response.json()
        assert "frontend_technical_specification" in processing_data
        assert "backend_technical_specification" in processing_data
        
        # Step 3: Generate comprehensive analysis with PDFs
        files = {
            "source_document": ("requirements.pdf", io.BytesIO(sample_pdf_content), "application/pdf")
        }
        
        comprehensive_response = client.post("/documents/comprehensive-analysis", files=files)
        assert comprehensive_response.status_code == status.HTTP_200_OK
        assert comprehensive_response.headers["content-type"] == "application/zip"
        
        # Verify all processing stages were called
        assert mock_analyze.call_count >= 1
        assert mock_synthesize.call_count >= 1
        assert mock_render.call_count >= 2  # Frontend and backend PDFs
    
    @patch('processors.document_analyzer.DocumentProcessor.analyze_document_content')
    @patch('intelligence.requirement_synthesizer.RequirementSynthesizer.process_requirements')
    def test_document_processing_error_handling(self, mock_synthesize, mock_analyze, client, sample_pdf_content):
        """Test error handling throughout the document processing pipeline."""
        
        # Test 1: Document analysis failure
        mock_analyze.side_effect = Exception("Document analysis failed")
        
        files = {
            "uploaded_file": ("bad_doc.pdf", io.BytesIO(sample_pdf_content), "application/pdf")
        }
        
        response = client.post("/documents/process-and-synthesize", files=files)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Document content extraction failed" in response.json()["detail"]
        
        # Test 2: Specification synthesis failure
        mock_analyze.side_effect = None
        mock_analyze.return_value = {"extracted_text": "Valid content", "metadata": {}}
        mock_synthesize.side_effect = Exception("AI synthesis failed")
        
        response = client.post("/documents/process-and-synthesize", files=files)
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Technical specification synthesis failed" in response.json()["detail"]


class TestCodeGenerationWorkflow:
    """Integration tests for code generation workflows."""
    
    @patch('intelligence.backend_architect.BackendArchitectureGenerator.synthesize_backend_structure')
    @patch('processors.artifact_packager.ArtifactProcessor.extract_generated_artifacts')
    @patch('processors.artifact_packager.ArtifactProcessor.create_compressed_archive')
    def test_backend_code_generation_workflow(self, mock_archive, mock_extract, mock_synthesize, client):
        """Test complete backend code generation workflow."""
        
        # Mock AI response
        mock_ai_result = Mock(content="""
### File: main.py
```python
from fastapi import FastAPI
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}
```

### File: models.py
```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    email: str
```
""")
        mock_synthesize.return_value = mock_ai_result
        
        # Mock artifact extraction
        mock_artifacts = [
            {"file_path": "main.py", "content": "FastAPI code", "content_type": "python"},
            {"file_path": "models.py", "content": "Pydantic models", "content_type": "python"}
        ]
        mock_extract.return_value = mock_artifacts
        
        # Mock archive creation
        mock_zip_buffer = Mock()
        mock_zip_buffer.getvalue.return_value = b"Mock ZIP content"
        mock_archive.return_value = mock_zip_buffer
        
        # Test backend generation initiation
        technical_spec = "Create a FastAPI backend with user authentication and PostgreSQL database"
        
        initiate_response = client.post(
            "/generation/backend/initiate",
            json={"technical_spec": technical_spec}
        )
        
        assert initiate_response.status_code == status.HTTP_200_OK
        initiate_data = initiate_response.json()
        assert initiate_data["process"] == "initiated"
        assert initiate_data["operation"] == "backend_code_generation"
        
        # Test artifact download
        download_response = client.post(
            "/artifacts/backend/download",
            json={"technical_specification": technical_spec}
        )
        
        assert download_response.status_code == status.HTTP_200_OK
        assert download_response.headers["content-type"] == "application/zip"
        
        # Verify the workflow components were called
        mock_synthesize.assert_called()
        mock_extract.assert_called_once()
        mock_archive.assert_called_once()
    
    @patch('intelligence.frontend_designer.FrontendDesignGenerator.synthesize_frontend_components')
    def test_frontend_code_generation_workflow(self, mock_synthesize, client):
        """Test complete frontend code generation workflow."""
        
        # Mock AI response
        mock_ai_result = Mock(content="""
### Component: app.component.ts
```typescript
import { Component } from '@angular/core';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html'
})
export class AppComponent {
  title = 'My App';
}
```

### Component: user.service.ts
```typescript
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable()
export class UserService {
  constructor(private http: HttpClient) {}
}
```
""")
        mock_synthesize.return_value = mock_ai_result
        
        # Test frontend generation initiation
        interface_spec = "Create an Angular dashboard with user management and data visualization"
        
        response = client.post(
            "/generation/frontend/initiate",
            json={"interface_spec": interface_spec}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["process"] == "initiated"
        assert data["operation"] == "frontend_code_generation"
        assert "Frontend design generation started successfully" in data["message"]
        
        # Verify the AI generation was triggered
        # Note: In a real test, you might wait for background task completion
        mock_synthesize.assert_called()


class TestWorkspaceManagement:
    """Integration tests for workspace and artifact management."""
    
    @patch('processors.directory_compressor.DirectoryCompressor.compress_directory_structure')
    def test_workspace_export_workflow(self, mock_compress, client, mock_directory_structure):
        """Test complete workspace export workflow."""
        
        # Mock successful compression
        mock_compress.return_value = None
        
        # Create a mock zip file for response
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp_zip:
            with zipfile.ZipFile(tmp_zip.name, 'w') as zf:
                zf.writestr('test_file.py', 'print("Hello World")')
            
            # Mock file system to return our test file
            with patch('pathlib.Path.exists', return_value=True), \
                 patch('fastapi.responses.FileResponse') as mock_file_response:
                
                mock_file_response.return_value = Mock()
                
                response = client.get("/artifacts/workspace/export")
                
                # Verify compression was called
                mock_compress.assert_called_once_with("artifacts", "workspace_export.zip")
    
    @patch('processors.artifact_packager.ArtifactProcessor.extract_generated_artifacts')
    @patch('processors.artifact_packager.ArtifactProcessor.create_compressed_archive')
    def test_artifact_processing_workflow(self, mock_archive, mock_extract):
        """Test artifact processing workflow with various file types."""
        from processors.artifact_packager import ArtifactProcessor
        
        # Test with mixed file types
        ai_output = """
### File: backend/app.py
```python
from fastapi import FastAPI
app = FastAPI()
```

### File: frontend/app.component.ts
```typescript
import { Component } from '@angular/core';
@Component({})
export class AppComponent {}
```

### File: config/database.json
```json
{
  "host": "localhost",
  "port": 5432
}
```

### File: docs/README.md
```markdown
# Project Documentation
This is the project documentation.
```
"""
        
        # Test extraction
        artifacts = ArtifactProcessor.extract_generated_artifacts(ai_output)
        
        assert len(artifacts) == 4
        assert any(a["file_path"] == "backend/app.py" for a in artifacts)
        assert any(a["file_path"] == "frontend/app.component.ts" for a in artifacts)
        assert any(a["file_path"] == "config/database.json" for a in artifacts)
        assert any(a["file_path"] == "docs/README.md" for a in artifacts)
        
        # Test archive creation
        mock_zip_buffer = Mock()
        mock_zip_buffer.getvalue.return_value = b"Mock archive content"
        mock_archive.return_value = mock_zip_buffer
        
        archive = ArtifactProcessor.create_compressed_archive(artifacts)
        
        mock_archive.assert_called_once_with(artifacts)
        assert archive.getvalue() == b"Mock archive content"


class TestSystemIntegration:
    """Integration tests for system-level functionality."""
    
    def test_application_startup_sequence(self, client):
        """Test application startup and health check sequence."""
        
        # Test root endpoint
        root_response = client.get("/")
        assert root_response.status_code == status.HTTP_200_OK
        
        root_data = root_response.json()
        assert root_data["service"] == "Intelligent Document Processing & Code Generation Platform"
        assert root_data["status"] == "operational"
        assert root_data["version"] == "2.0.0"
        
        # Test health endpoint
        health_response = client.get("/system/health")
        assert health_response.status_code == status.HTTP_200_OK
        
        health_data = health_response.json()
        assert health_data["service_status"] == "operational"
        assert health_data["system_health"] == "excellent"
        assert "capabilities" in health_data
        assert "environment" in health_data
    
    def test_api_documentation_availability(self, client):
        """Test that API documentation is properly available."""
        
        # Test OpenAPI spec
        openapi_response = client.get("/openapi.json")
        assert openapi_response.status_code == status.HTTP_200_OK
        
        openapi_spec = openapi_response.json()
        assert openapi_spec["info"]["title"] == "Intelligent Document Processing & Code Generation Platform"
        assert openapi_spec["info"]["version"] == "2.0.0"
        
        # Test documentation endpoints
        docs_response = client.get("/documentation")
        assert docs_response.status_code == status.HTTP_200_OK
        
        redoc_response = client.get("/api-reference")
        assert redoc_response.status_code == status.HTTP_200_OK
    
    def test_cors_configuration(self, client):
        """Test CORS configuration for frontend integration."""
        
        # Test preflight request
        response = client.options(
            "/documents/analyze",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            }
        )
        
        # Should handle OPTIONS request
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT]


class TestPerformanceAndScalability:
    """Integration tests for performance and scalability aspects."""
    
    def test_concurrent_request_handling(self, client, sample_pdf_content):
        """Test handling of concurrent requests."""
        import concurrent.futures
        import threading
        
        def make_health_request():
            return client.get("/system/health")
        
        def make_document_request():
            files = {
                "document": ("test.pdf", io.BytesIO(sample_pdf_content), "application/pdf")
            }
            return client.post("/documents/analyze", files=files)
        
        # Submit multiple concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            # Mix of different endpoint types
            health_futures = [executor.submit(make_health_request) for _ in range(3)]
            
            # All requests should complete successfully
            for future in concurrent.futures.as_completed(health_futures):
                response = future.result()
                assert response.status_code == status.HTTP_200_OK
    
    @patch('processors.document_analyzer.DocumentProcessor.analyze_document_content')
    def test_error_recovery_and_resilience(self, mock_analyze, client, sample_pdf_content):
        """Test system resilience and error recovery."""
        
        # Test 1: Temporary failure followed by success
        mock_analyze.side_effect = [
            Exception("Temporary failure"),  # First call fails
            {"extracted_text": "Success", "metadata": {}}  # Second call succeeds
        ]
        
        files = {
            "document": ("test1.pdf", io.BytesIO(sample_pdf_content), "application/pdf")
        }
        
        # First request should fail
        response1 = client.post("/documents/analyze", files=files)
        assert response1.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        
        # Second request should succeed
        files = {
            "document": ("test2.pdf", io.BytesIO(sample_pdf_content), "application/pdf")
        }
        response2 = client.post("/documents/analyze", files=files)
        assert response2.status_code == status.HTTP_200_OK
        
        # Verify both calls were made
        assert mock_analyze.call_count == 2
    
    def test_memory_usage_with_large_operations(self, client):
        """Test memory usage during large operations."""
        import gc
        import psutil
        import os
        
        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Perform multiple operations
        for i in range(5):
            # Make health check requests (lightweight operations)
            response = client.get("/system/health")
            assert response.status_code == status.HTTP_200_OK
        
        # Force garbage collection
        gc.collect()
        
        # Check memory usage hasn't grown excessively
        final_memory = process.memory_info().rss
        memory_growth = final_memory - initial_memory
        
        # Memory growth should be reasonable (less than 50MB for these lightweight operations)
        assert memory_growth < 50 * 1024 * 1024  # 50MB threshold


class TestRealWorldScenarios:
    """Integration tests simulating real-world usage scenarios."""
    
    @patch('processors.document_analyzer.DocumentProcessor.analyze_document_content')
    @patch('intelligence.requirement_synthesizer.RequirementSynthesizer.process_requirements')
    @patch('intelligence.backend_architect.BackendArchitectureGenerator.synthesize_backend_structure')
    @patch('intelligence.frontend_designer.FrontendDesignGenerator.synthesize_frontend_components')
    def test_complete_project_generation_scenario(self, mock_frontend, mock_backend, mock_synth, mock_analyze, client, sample_pdf_content):
        """Test complete project generation from requirements to code."""
        
        # Mock document analysis
        mock_analyze.return_value = {
            "extracted_text": "Create a complete e-commerce platform with user management, product catalog, shopping cart, and payment processing.",
            "metadata": {"document_type": "pdf"}
        }
        
        # Mock specification synthesis
        mock_synth.return_value = (
            "Frontend Specification: React-based SPA with Redux",
            "Backend Specification: FastAPI with PostgreSQL"
        )
        
        # Mock code generation
        mock_backend.return_value = Mock(content="Generated backend code")
        mock_frontend.return_value = Mock(content="Generated frontend code")
        
        # Step 1: Upload requirements document
        files = {
            "uploaded_file": ("ecommerce_requirements.pdf", io.BytesIO(sample_pdf_content), "application/pdf")
        }
        
        spec_response = client.post("/documents/process-and-synthesize", files=files)
        assert spec_response.status_code == status.HTTP_200_OK
        spec_data = spec_response.json()
        
        # Step 2: Generate backend code
        backend_response = client.post(
            "/generation/backend/initiate",
            json={"technical_spec": spec_data["backend_technical_specification"]}
        )
        assert backend_response.status_code == status.HTTP_200_OK
        
        # Step 3: Generate frontend code
        frontend_response = client.post(
            "/generation/frontend/initiate",
            json={"interface_spec": spec_data["frontend_technical_specification"]}
        )
        assert frontend_response.status_code == status.HTTP_200_OK
        
        # Verify all components were called
        mock_analyze.assert_called_once()
        mock_synth.assert_called_once()
        mock_backend.assert_called_once()
        mock_frontend.assert_called_once()
    
    def test_api_versioning_and_backward_compatibility(self, client):
        """Test API versioning and backward compatibility."""
        
        # Test current API endpoints
        current_endpoints = [
            "/",
            "/system/health",
            "/documents/analyze",
            "/artifacts/workspace/export"
        ]
        
        for endpoint in current_endpoints:
            if endpoint == "/documents/analyze":
                # Skip file upload endpoints in this test
                continue
            
            response = client.get(endpoint)
            # Should return either success or method not allowed (for POST-only endpoints)
            assert response.status_code in [
                status.HTTP_200_OK,
                status.HTTP_405_METHOD_NOT_ALLOWED
            ]
    
    def test_error_logging_and_monitoring(self, client):
        """Test error logging and monitoring capabilities."""
        
        # Test various error scenarios
        error_scenarios = [
            ("/nonexistent/endpoint", status.HTTP_404_NOT_FOUND),
            ("/generation/backend/initiate", status.HTTP_422_UNPROCESSABLE_ENTITY),  # Missing body
        ]
        
        for endpoint, expected_status in error_scenarios:
            if "initiate" in endpoint:
                response = client.post(endpoint)  # POST without body
            else:
                response = client.get(endpoint)
            
            assert response.status_code == expected_status
            
            # Verify error response format
            if response.status_code >= 400:
                error_data = response.json()
                assert "detail" in error_data or "message" in error_data
