# Document Processing Endpoints Tests
"""
Comprehensive test suite for document processing endpoints including upload,
analysis, processing, and technical specification generation.
"""

import pytest
import json
import io
from unittest.mock import patch, Mock, AsyncMock
from fastapi import status, UploadFile


class TestDocumentAnalysisEndpoint:
    """Test suite for document analysis endpoint."""
    
    @patch('processors.document_analyzer.DocumentProcessor.analyze_document_content')
    def test_analyze_document_success_pdf(self, mock_analyze, client, sample_pdf_content, mock_document_analysis_result):
        """Test successful PDF document analysis."""
        mock_analyze.return_value = mock_document_analysis_result
        
        # Create file upload
        files = {
            "document": ("test.pdf", io.BytesIO(sample_pdf_content), "application/pdf")
        }
        
        response = client.post("/documents/analyze", files=files)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["extracted_text"] == "Sample extracted text from document"
        assert "document_sections" in data
        assert "metadata" in data
        assert data["metadata"]["document_type"] == "pdf"
        
        # Verify the analyzer was called
        mock_analyze.assert_called_once()
    
    @patch('processors.document_analyzer.DocumentProcessor.analyze_document_content')
    def test_analyze_document_success_docx(self, mock_analyze, client, sample_docx_content, mock_document_analysis_result):
        """Test successful DOCX document analysis."""
        mock_analyze.return_value = mock_document_analysis_result
        
        files = {
            "document": ("test.docx", io.BytesIO(sample_docx_content), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        }
        
        response = client.post("/documents/analyze", files=files)
        
        assert response.status_code == status.HTTP_200_OK
        mock_analyze.assert_called_once()
    
    @patch('processors.document_analyzer.DocumentProcessor.analyze_document_content')
    def test_analyze_document_success_markdown(self, mock_analyze, client, sample_markdown_content, mock_document_analysis_result):
        """Test successful Markdown document analysis."""
        mock_analyze.return_value = mock_document_analysis_result
        
        files = {
            "document": ("test.md", io.BytesIO(sample_markdown_content), "text/markdown")
        }
        
        response = client.post("/documents/analyze", files=files)
        
        assert response.status_code == status.HTTP_200_OK
        mock_analyze.assert_called_once()
    
    def test_analyze_document_no_file(self, client):
        """Test document analysis without file upload."""
        response = client.post("/documents/analyze")
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @patch('processors.document_analyzer.DocumentProcessor.analyze_document_content')
    def test_analyze_document_unsupported_format(self, mock_analyze, client):
        """Test document analysis with unsupported file format."""
        from processors.document_analyzer import UnsupportedDocumentType
        mock_analyze.side_effect = UnsupportedDocumentType("Unsupported file format: .txt")
        
        files = {
            "document": ("test.txt", io.BytesIO(b"Plain text content"), "text/plain")
        }
        
        response = client.post("/documents/analyze", files=files)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data["error_type"] == "unsupported_format"
        assert "Unsupported file format" in data["details"]
    
    @patch('processors.document_analyzer.DocumentProcessor.analyze_document_content')
    def test_analyze_document_parsing_error(self, mock_analyze, client, sample_pdf_content):
        """Test document analysis with parsing error."""
        from processors.document_analyzer import DocumentParsingException
        mock_analyze.side_effect = DocumentParsingException("Failed to extract content")
        
        files = {
            "document": ("test.pdf", io.BytesIO(sample_pdf_content), "application/pdf")
        }
        
        response = client.post("/documents/analyze", files=files)
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert data["error_type"] == "parsing_failure"
        assert "Failed to extract content" in data["details"]
    
    @patch('processors.document_analyzer.DocumentProcessor.analyze_document_content')
    def test_analyze_document_unexpected_error(self, mock_analyze, client, sample_pdf_content):
        """Test document analysis with unexpected error."""
        mock_analyze.side_effect = Exception("Unexpected system error")
        
        files = {
            "document": ("test.pdf", io.BytesIO(sample_pdf_content), "application/pdf")
        }
        
        response = client.post("/documents/analyze", files=files)
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert data["error_type"] == "system_error"
        assert "Unexpected processing error" in data["details"]


class TestDocumentProcessAndSynthesizeEndpoint:
    """Test suite for document processing and specification synthesis endpoint."""
    
    @patch('processors.document_analyzer.DocumentProcessor.analyze_document_content')
    @patch('intelligence.requirement_synthesizer.RequirementSynthesizer.process_requirements')
    def test_process_and_synthesize_success(self, mock_synthesize, mock_analyze, client, sample_pdf_content, mock_document_analysis_result, mock_specification_result):
        """Test successful document processing and specification synthesis."""
        mock_analyze.return_value = mock_document_analysis_result
        mock_synthesize.return_value = mock_specification_result
        
        files = {
            "uploaded_file": ("requirements.pdf", io.BytesIO(sample_pdf_content), "application/pdf")
        }
        
        response = client.post("/documents/process-and-synthesize", files=files)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "frontend_technical_specification" in data
        assert "backend_technical_specification" in data
        assert "document_metadata" in data
        assert data["document_metadata"]["source_filename"] == "requirements.pdf"
        assert data["document_metadata"]["processing_status"] == "completed"
        
        # Verify method calls
        mock_analyze.assert_called_once()
        mock_synthesize.assert_called_once_with("Sample extracted text from document")
    
    @patch('processors.document_analyzer.DocumentProcessor.analyze_document_content')
    def test_process_and_synthesize_upload_error(self, mock_analyze, client):
        """Test document processing with file upload error."""
        # Simulate file upload error by providing invalid file data
        files = {
            "uploaded_file": ("test.pdf", None, "application/pdf")  # None content causes error
        }
        
        response = client.post("/documents/process-and-synthesize", files=files)
        
        # Should return 500 for upload processing error
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert "Document upload processing error" in data["detail"]
    
    @patch('processors.document_analyzer.DocumentProcessor.analyze_document_content')
    def test_process_and_synthesize_parsing_error(self, mock_analyze, client, sample_pdf_content):
        """Test document processing with content extraction failure."""
        mock_analyze.side_effect = Exception("Content extraction failed")
        
        files = {
            "uploaded_file": ("test.pdf", io.BytesIO(sample_pdf_content), "application/pdf")
        }
        
        response = client.post("/documents/process-and-synthesize", files=files)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "Document content extraction failed" in data["detail"]
    
    @patch('processors.document_analyzer.DocumentProcessor.analyze_document_content')
    @patch('intelligence.requirement_synthesizer.RequirementSynthesizer.process_requirements')
    def test_process_and_synthesize_synthesis_error(self, mock_synthesize, mock_analyze, client, sample_pdf_content, mock_document_analysis_result):
        """Test document processing with specification synthesis failure."""
        mock_analyze.return_value = mock_document_analysis_result
        mock_synthesize.side_effect = Exception("AI synthesis failed")
        
        files = {
            "uploaded_file": ("test.pdf", io.BytesIO(sample_pdf_content), "application/pdf")
        }
        
        response = client.post("/documents/process-and-synthesize", files=files)
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert "Technical specification synthesis failed" in data["detail"]


class TestDocumentComprehensiveAnalysisEndpoint:
    """Test suite for comprehensive document analysis endpoint."""
    
    @patch('processors.document_analyzer.DocumentProcessor.analyze_document_content')
    @patch('intelligence.requirement_synthesizer.RequirementSynthesizer.process_requirements')
    @patch('processors.document_renderer.DocumentRenderer.render_to_pdf')
    def test_comprehensive_analysis_success(self, mock_render, mock_synthesize, mock_analyze, client, sample_pdf_content, mock_document_analysis_result, mock_specification_result):
        """Test successful comprehensive document analysis and PDF generation."""
        mock_analyze.return_value = mock_document_analysis_result
        mock_synthesize.return_value = mock_specification_result
        mock_render.return_value = b"Mock PDF content"
        
        files = {
            "source_document": ("requirements.pdf", io.BytesIO(sample_pdf_content), "application/pdf")
        }
        
        response = client.post("/documents/comprehensive-analysis", files=files)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.headers["content-type"] == "application/zip"
        assert "Comprehensive_Technical_Documentation.zip" in response.headers.get("content-disposition", "")
        
        # Verify all components were called
        mock_analyze.assert_called_once()
        mock_synthesize.assert_called_once()
        assert mock_render.call_count == 2  # Called for both frontend and backend PDFs
    
    @patch('processors.document_analyzer.DocumentProcessor.analyze_document_content')
    def test_comprehensive_analysis_processing_error(self, mock_analyze, client):
        """Test comprehensive analysis with document processing error."""
        files = {
            "source_document": ("test.pdf", None, "application/pdf")  # None content causes error
        }
        
        response = client.post("/documents/comprehensive-analysis", files=files)
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert "Document processing initialization failed" in data["detail"]
    
    @patch('processors.document_analyzer.DocumentProcessor.analyze_document_content')
    def test_comprehensive_analysis_extraction_error(self, mock_analyze, client, sample_pdf_content):
        """Test comprehensive analysis with content extraction error."""
        mock_analyze.side_effect = Exception("Content extraction failed")
        
        files = {
            "source_document": ("test.pdf", io.BytesIO(sample_pdf_content), "application/pdf")
        }
        
        response = client.post("/documents/comprehensive-analysis", files=files)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "Content extraction process failed" in data["detail"]
    
    @patch('processors.document_analyzer.DocumentProcessor.analyze_document_content')
    @patch('intelligence.requirement_synthesizer.RequirementSynthesizer.process_requirements')
    @patch('processors.document_renderer.DocumentRenderer.render_to_pdf')
    def test_comprehensive_analysis_generation_error(self, mock_render, mock_synthesize, mock_analyze, client, sample_pdf_content, mock_document_analysis_result):
        """Test comprehensive analysis with document generation error."""
        mock_analyze.return_value = mock_document_analysis_result
        mock_synthesize.side_effect = Exception("Specification generation failed")
        
        files = {
            "source_document": ("test.pdf", io.BytesIO(sample_pdf_content), "application/pdf")
        }
        
        response = client.post("/documents/comprehensive-analysis", files=files)
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert "Technical document generation failed" in data["detail"]


class TestTechnicalSpecificationGenerationEndpoint:
    """Test suite for technical specification generation endpoint."""
    
    @patch('intelligence.requirement_synthesizer.RequirementSynthesizer.process_requirements')
    @patch('processors.document_renderer.DocumentRenderer.render_to_pdf')
    def test_generate_technical_specifications_json_input(self, mock_render, mock_synthesize, client, mock_specification_result, sample_requirements_text):
        """Test technical specification generation with JSON input."""
        mock_synthesize.return_value = mock_specification_result
        mock_render.return_value = b"Mock PDF content"
        
        payload = {"requirements_text": sample_requirements_text}
        response = client.post("/specifications/technical/generate", json=payload)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.headers["content-type"] == "application/zip"
        assert "Technical_Specifications.zip" in response.headers.get("content-disposition", "")
        
        mock_synthesize.assert_called_once_with(sample_requirements_text)
        assert mock_render.call_count == 2  # Called for both frontend and backend
    
    @patch('intelligence.requirement_synthesizer.RequirementSynthesizer.process_requirements')
    @patch('processors.document_renderer.DocumentRenderer.render_to_pdf')
    def test_generate_technical_specifications_raw_text_input(self, mock_render, mock_synthesize, client, mock_specification_result, sample_requirements_text):
        """Test technical specification generation with raw text input."""
        mock_synthesize.return_value = mock_specification_result
        mock_render.return_value = b"Mock PDF content"
        
        response = client.post(
            "/specifications/technical/generate",
            data=sample_requirements_text,
            headers={"Content-Type": "text/plain"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        mock_synthesize.assert_called_once_with(sample_requirements_text)
    
    def test_generate_technical_specifications_empty_content(self, client):
        """Test technical specification generation with empty content."""
        payload = {"requirements_text": ""}
        response = client.post("/specifications/technical/generate", json=payload)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "Software requirements specification content is mandatory" in data["detail"]
    
    def test_generate_technical_specifications_missing_content(self, client):
        """Test technical specification generation with missing content."""
        response = client.post("/specifications/technical/generate", json={})
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "Software requirements specification content is mandatory" in data["detail"]
    
    @patch('intelligence.requirement_synthesizer.RequirementSynthesizer.process_requirements')
    def test_generate_technical_specifications_synthesis_error(self, mock_synthesize, client, sample_requirements_text):
        """Test technical specification generation with synthesis error."""
        mock_synthesize.side_effect = Exception("AI synthesis failed")
        
        payload = {"requirements_text": sample_requirements_text}
        response = client.post("/specifications/technical/generate", json=payload)
        
        # Should handle the error gracefully
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


class TestDocumentEndpointEdgeCases:
    """Test suite for edge cases and boundary conditions in document endpoints."""
    
    def test_large_file_upload_handling(self, client):
        """Test handling of large file uploads."""
        # Create a large file content (simulate beyond normal limits)
        large_content = b"x" * (10 * 1024 * 1024)  # 10MB
        
        files = {
            "document": ("large_file.pdf", io.BytesIO(large_content), "application/pdf")
        }
        
        response = client.post("/documents/analyze", files=files)
        
        # Should either process successfully or return appropriate error
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            status.HTTP_422_UNPROCESSABLE_ENTITY
        ]
    
    def test_malformed_file_content(self, client):
        """Test handling of malformed file content."""
        malformed_content = b"This is not a valid PDF file"
        
        files = {
            "document": ("fake.pdf", io.BytesIO(malformed_content), "application/pdf")
        }
        
        response = client.post("/documents/analyze", files=files)
        
        # Should return error for malformed content
        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_500_INTERNAL_SERVER_ERROR
        ]
    
    def test_empty_file_upload(self, client):
        """Test handling of empty file uploads."""
        files = {
            "document": ("empty.pdf", io.BytesIO(b""), "application/pdf")
        }
        
        response = client.post("/documents/analyze", files=files)
        
        # Should handle empty files gracefully
        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_500_INTERNAL_SERVER_ERROR
        ]
    
    def test_concurrent_document_processing(self, client, sample_pdf_content):
        """Test concurrent document processing requests."""
        import concurrent.futures
        
        def make_request():
            files = {
                "document": ("test.pdf", io.BytesIO(sample_pdf_content), "application/pdf")
            }
            return client.post("/documents/analyze", files=files)
        
        # Submit multiple concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(make_request) for _ in range(3)]
            responses = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # All requests should complete (success or graceful failure)
        for response in responses:
            assert response.status_code in [
                status.HTTP_200_OK,
                status.HTTP_400_BAD_REQUEST,
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ]
