# Processor Modules Tests
"""
Comprehensive test suite for processor modules including document analysis,
rendering, artifact processing, and compression functionality.
"""

import pytest
import tempfile
import io
from pathlib import Path
from unittest.mock import patch, Mock, mock_open
import zipfile
import json


class TestDocumentProcessor:
    """Test suite for DocumentProcessor class."""
    
    @patch('pdfplumber.open')
    def test_analyze_pdf_document_success(self, mock_pdfplumber):
        """Test successful PDF document analysis."""
        from processors.document_analyzer import DocumentProcessor
        
        # Mock PDF pages with text content
        mock_page = Mock()
        mock_page.extract_text.return_value = "Sample PDF content\nwith multiple lines"
        
        mock_pdf = Mock()
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__ = Mock(return_value=mock_pdf)
        mock_pdf.__exit__ = Mock(return_value=None)
        
        mock_pdfplumber.return_value = mock_pdf
        
        # Test the analysis
        with tempfile.NamedTemporaryFile(suffix='.pdf') as tmp_file:
            result = DocumentProcessor.analyze_document_content(tmp_file.name)
        
        assert "extracted_text" in result
        assert "document_sections" in result
        assert "metadata" in result
        assert result["metadata"]["document_type"] == "pdf"
        assert result["metadata"]["total_pages"] == 1
        assert "Sample PDF content" in result["extracted_text"]
    
    @patch('docx.Document')
    def test_analyze_docx_document_success(self, mock_docx):
        """Test successful DOCX document analysis."""
        from processors.document_analyzer import DocumentProcessor
        
        # Mock DOCX paragraphs
        mock_paragraph1 = Mock()
        mock_paragraph1.text = "First paragraph content"
        mock_paragraph2 = Mock()
        mock_paragraph2.text = "Second paragraph content"
        
        mock_doc = Mock()
        mock_doc.paragraphs = [mock_paragraph1, mock_paragraph2]
        mock_docx.return_value = mock_doc
        
        # Test the analysis
        with tempfile.NamedTemporaryFile(suffix='.docx') as tmp_file:
            result = DocumentProcessor.analyze_document_content(tmp_file.name)
        
        assert "extracted_text" in result
        assert "First paragraph content" in result["extracted_text"]
        assert "Second paragraph content" in result["extracted_text"]
        assert result["metadata"]["document_type"] == "word_document"
    
    def test_analyze_markdown_document_success(self):
        """Test successful Markdown document analysis."""
        from processors.document_analyzer import DocumentProcessor
        
        markdown_content = """# Test Document
        
## Section 1
This is the first section.

## Section 2
This is the second section.
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as tmp_file:
            tmp_file.write(markdown_content)
            tmp_file.flush()
            
            result = DocumentProcessor.analyze_document_content(tmp_file.name)
        
        assert "extracted_text" in result
        assert "Test Document" in result["extracted_text"]
        assert result["metadata"]["document_type"] == "text_document"
        
        # Cleanup
        Path(tmp_file.name).unlink()
    
    def test_analyze_unsupported_format(self):
        """Test analysis of unsupported file format."""
        from processors.document_analyzer import DocumentProcessor, UnsupportedDocumentType
        
        with tempfile.NamedTemporaryFile(suffix='.xyz') as tmp_file:
            with pytest.raises(UnsupportedDocumentType):
                DocumentProcessor.analyze_document_content(tmp_file.name)
    
    def test_analyze_nonexistent_file(self):
        """Test analysis of nonexistent file."""
        from processors.document_analyzer import DocumentProcessor, DocumentParsingException
        
        with pytest.raises(DocumentParsingException):
            DocumentProcessor.analyze_document_content("/nonexistent/file.pdf")
    
    @patch('pdfplumber.open')
    def test_analyze_pdf_with_empty_pages(self, mock_pdfplumber):
        """Test PDF analysis with empty pages."""
        from processors.document_analyzer import DocumentProcessor
        
        # Mock PDF with empty pages
        mock_page1 = Mock()
        mock_page1.extract_text.return_value = None
        mock_page2 = Mock()
        mock_page2.extract_text.return_value = ""
        mock_page3 = Mock()
        mock_page3.extract_text.return_value = "Only this page has content"
        
        mock_pdf = Mock()
        mock_pdf.pages = [mock_page1, mock_page2, mock_page3]
        mock_pdf.__enter__ = Mock(return_value=mock_pdf)
        mock_pdf.__exit__ = Mock(return_value=None)
        
        mock_pdfplumber.return_value = mock_pdf
        
        with tempfile.NamedTemporaryFile(suffix='.pdf') as tmp_file:
            result = DocumentProcessor.analyze_document_content(tmp_file.name)
        
        assert "Only this page has content" in result["extracted_text"]
        assert result["metadata"]["total_pages"] == 3
        assert result["metadata"]["processed_pages"] == 1


class TestDocumentRenderer:
    """Test suite for DocumentRenderer class."""
    
    @patch('fpdf.FPDF')
    def test_render_to_pdf_simple_content(self, mock_fpdf_class):
        """Test PDF rendering with simple content."""
        from processors.document_renderer import DocumentRenderer
        
        # Mock FPDF instance
        mock_pdf = Mock()
        mock_pdf.output.return_value = b"Mock PDF content"
        mock_fpdf_class.return_value = mock_pdf
        
        content = "Simple test content\nwith multiple lines"
        result = DocumentRenderer._generate_pdf_document(content)
        
        assert result == b"Mock PDF content"
        mock_pdf.add_page.assert_called_once()
        mock_pdf.set_font.assert_called()
        mock_pdf.multi_cell.assert_called()
    
    @patch('fpdf.FPDF')
    def test_render_to_pdf_with_headers(self, mock_fpdf_class):
        """Test PDF rendering with header content."""
        from processors.document_renderer import DocumentRenderer
        
        mock_pdf = Mock()
        mock_pdf.output.return_value = b"Mock PDF with headers"
        mock_fpdf_class.return_value = mock_pdf
        
        content = """# Main Header
        
This is regular content.

## Sub Header

More content here.

### Another Header

Final content.
"""
        
        result = DocumentRenderer._generate_pdf_document(content)
        
        assert result == b"Mock PDF with headers"
        # Verify PDF methods were called appropriately
        mock_pdf.add_page.assert_called_once()
        assert mock_pdf.cell.call_count >= 3  # Should be called for headers
    
    def test_is_header_line_detection(self):
        """Test header line detection logic."""
        from processors.document_renderer import DocumentRenderer
        
        # Test markdown headers
        assert DocumentRenderer._is_header_line("# Main Header")
        assert DocumentRenderer._is_header_line("## Sub Header")
        assert DocumentRenderer._is_header_line("### Another Header")
        
        # Test ALL CAPS headers
        assert DocumentRenderer._is_header_line("IMPORTANT SECTION TITLE")
        
        # Test numbered headers
        assert DocumentRenderer._is_header_line("1. Introduction Section")
        assert DocumentRenderer._is_header_line("2.1 Subsection Title")
        
        # Test non-headers
        assert not DocumentRenderer._is_header_line("Regular paragraph text")
        assert not DocumentRenderer._is_header_line("short")
        assert not DocumentRenderer._is_header_line("Mixed Case Text")
    
    @patch('fpdf.FPDF')
    def test_render_empty_content(self, mock_fpdf_class):
        """Test PDF rendering with empty content."""
        from processors.document_renderer import DocumentRenderer
        
        mock_pdf = Mock()
        mock_pdf.output.return_value = b"Empty PDF"
        mock_fpdf_class.return_value = mock_pdf
        
        result = DocumentRenderer._generate_pdf_document("")
        
        assert result == b"Empty PDF"
        mock_pdf.add_page.assert_called_once()
    
    @patch('fpdf.FPDF')
    def test_render_with_special_characters(self, mock_fpdf_class):
        """Test PDF rendering with special characters."""
        from processors.document_renderer import DocumentRenderer
        
        mock_pdf = Mock()
        mock_pdf.output.return_value = b"PDF with special chars"
        mock_fpdf_class.return_value = mock_pdf
        
        # Test content with special characters that might cause encoding issues
        content = "Content with special chars: àáâãäåæçèéêë"
        
        result = DocumentRenderer._generate_pdf_document(content)
        
        assert result == b"PDF with special chars"
        mock_pdf.multi_cell.assert_called()


class TestArtifactProcessor:
    """Test suite for ArtifactProcessor class."""
    
    def test_extract_generated_artifacts_success(self):
        """Test successful artifact extraction from AI output."""
        from processors.artifact_packager import ArtifactProcessor
        
        ai_output = """
Here are the generated files:

### File: app.py
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}
```

### File: models.py
```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    email: str
```

### File: config.json
```json
{
    "database_url": "sqlite:///app.db",
    "debug": true
}
```
"""
        
        artifacts = ArtifactProcessor.extract_generated_artifacts(ai_output)
        
        assert len(artifacts) == 3
        
        # Check first artifact
        assert artifacts[0]["file_path"] == "app.py"
        assert "from fastapi import FastAPI" in artifacts[0]["content"]
        assert artifacts[0]["content_type"] == "python"
        
        # Check second artifact
        assert artifacts[1]["file_path"] == "models.py"
        assert "from pydantic import BaseModel" in artifacts[1]["content"]
        
        # Check third artifact
        assert artifacts[2]["file_path"] == "config.json"
        assert "database_url" in artifacts[2]["content"]
        assert artifacts[2]["content_type"] == "json"
    
    def test_extract_artifacts_with_cleanup(self):
        """Test artifact extraction with content cleanup."""
        from processors.artifact_packager import ArtifactProcessor
        
        ai_output = """
### File: test.py
```python
# Code Generated by Sidekick is for learning and experimentation purposes only.
# Auto-generated content - modify with caution

def hello_world():
    return "Hello, World!"
```
"""
        
        artifacts = ArtifactProcessor.extract_generated_artifacts(ai_output)
        
        assert len(artifacts) == 1
        artifact = artifacts[0]
        
        # Verify cleanup was applied
        assert "Code Generated by Sidekick" not in artifact["content"]
        assert "Auto-generated content" not in artifact["content"]
        assert "def hello_world():" in artifact["content"]
    
    def test_extract_artifacts_no_matches(self):
        """Test artifact extraction with no matching patterns."""
        from processors.artifact_packager import ArtifactProcessor
        
        ai_output = "This is just plain text without any file patterns."
        
        artifacts = ArtifactProcessor.extract_generated_artifacts(ai_output)
        
        assert len(artifacts) == 0
    
    def test_create_compressed_archive(self):
        """Test creation of compressed archive from artifacts."""
        from processors.artifact_packager import ArtifactProcessor
        
        artifacts = [
            {
                "file_path": "main.py",
                "content": "print('Hello, World!')",
                "content_type": "python"
            },
            {
                "file_path": "config.json",
                "content": '{"debug": true}',
                "content_type": "json"
            }
        ]
        
        archive_buffer = ArtifactProcessor.create_compressed_archive(artifacts)
        
        assert isinstance(archive_buffer, io.BytesIO)
        assert archive_buffer.tell() > 0  # Should have content
        
        # Verify archive contents
        archive_buffer.seek(0)
        with zipfile.ZipFile(archive_buffer, 'r') as zip_file:
            file_list = zip_file.namelist()
            assert "main.py" in file_list
            assert "config.json" in file_list
            assert "_metadata.json" in file_list
            
            # Check file contents
            main_content = zip_file.read("main.py").decode('utf-8')
            assert "print('Hello, World!')" in main_content
    
    def test_validate_artifact_success(self):
        """Test successful artifact validation."""
        from processors.artifact_packager import ArtifactProcessor
        
        # Valid artifacts
        assert ArtifactProcessor._validate_artifact("app.py", "def main(): pass")
        assert ArtifactProcessor._validate_artifact("config.json", '{"key": "value"}')
        assert ArtifactProcessor._validate_artifact("index.html", "<html></html>")
    
    def test_validate_artifact_failure(self):
        """Test artifact validation failures."""
        from processors.artifact_packager import ArtifactProcessor
        
        # Invalid artifacts
        assert not ArtifactProcessor._validate_artifact("", "content")  # Empty path
        assert not ArtifactProcessor._validate_artifact("file.py", "")  # Empty content
        assert not ArtifactProcessor._validate_artifact("noextension", "content")  # No extension
        assert not ArtifactProcessor._validate_artifact("file.py", "x" * 5)  # Too short content
    
    def test_normalize_file_path(self):
        """Test file path normalization."""
        from processors.artifact_packager import ArtifactProcessor
        
        # Test various path formats
        assert ArtifactProcessor._normalize_file_path("  app.py  ") == "app.py"
        assert ArtifactProcessor._normalize_file_path("'app.py'") == "app.py"
        assert ArtifactProcessor._normalize_file_path('"app.py"') == "app.py"
        assert ArtifactProcessor._normalize_file_path("folder\\app.py") == "folder/app.py"
        assert ArtifactProcessor._normalize_file_path("/absolute/path.py") == "absolute/path.py"
    
    def test_determine_content_type(self):
        """Test content type determination from file extensions."""
        from processors.artifact_packager import ArtifactProcessor
        
        assert ArtifactProcessor._determine_content_type("app.py") == "python"
        assert ArtifactProcessor._determine_content_type("script.js") == "javascript"
        assert ArtifactProcessor._determine_content_type("component.ts") == "typescript"
        assert ArtifactProcessor._determine_content_type("style.css") == "css"
        assert ArtifactProcessor._determine_content_type("config.json") == "json"
        assert ArtifactProcessor._determine_content_type("readme.md") == "markdown"
        assert ArtifactProcessor._determine_content_type("unknown.xyz") == "unknown"


class TestDirectoryCompressor:
    """Test suite for DirectoryCompressor class."""
    
    def test_compress_directory_structure_success(self, mock_directory_structure):
        """Test successful directory compression."""
        from processors.directory_compressor import DirectoryCompressor
        
        output_zip = Path(mock_directory_structure) / "test_output.zip"
        
        DirectoryCompressor.compress_directory_structure(
            mock_directory_structure,
            str(output_zip)
        )
        
        assert output_zip.exists()
        
        # Verify zip contents
        with zipfile.ZipFile(output_zip, 'r') as zip_file:
            file_list = zip_file.namelist()
            assert "test1.py" in file_list
            assert "test2.js" in file_list
            assert "subfolder/test3.html" in file_list
    
    def test_compress_nonexistent_directory(self):
        """Test compression of nonexistent directory."""
        from processors.directory_compressor import DirectoryCompressor, CompressionException
        
        with pytest.raises(CompressionException):
            DirectoryCompressor.compress_directory_structure(
                "/nonexistent/directory",
                "output.zip"
            )
    
    def test_compress_with_exclusions(self, mock_directory_structure):
        """Test directory compression with file exclusions."""
        from processors.directory_compressor import DirectoryCompressor
        
        # Add some files that should be excluded
        excluded_dir = Path(mock_directory_structure) / "__pycache__"
        excluded_dir.mkdir()
        (excluded_dir / "cache.pyc").write_text("cache content")
        
        output_zip = Path(mock_directory_structure) / "test_output.zip"
        
        DirectoryCompressor.compress_directory_structure(
            mock_directory_structure,
            str(output_zip),
            exclusions=["*.pyc", "__pycache__"]
        )
        
        assert output_zip.exists()
        
        # Verify excluded files are not in zip
        with zipfile.ZipFile(output_zip, 'r') as zip_file:
            file_list = zip_file.namelist()
            assert not any("__pycache__" in f for f in file_list)
            assert not any(".pyc" in f for f in file_list)
    
    def test_get_archive_info(self, mock_directory_structure):
        """Test archive information extraction."""
        from processors.directory_compressor import DirectoryCompressor
        
        output_zip = Path(mock_directory_structure) / "test_info.zip"
        
        # Create a test zip file
        DirectoryCompressor.compress_directory_structure(
            mock_directory_structure,
            str(output_zip)
        )
        
        # Get archive info
        info = DirectoryCompressor.get_archive_info(str(output_zip))
        
        assert "archive_path" in info
        assert "total_files" in info
        assert "compressed_size" in info
        assert "uncompressed_size" in info
        assert "compression_ratio" in info
        assert "file_types" in info
        assert "directory_structure" in info
        
        assert info["total_files"] >= 3  # At least our test files
        assert info["compression_ratio"] >= 0
    
    def test_should_exclude_patterns(self):
        """Test file exclusion pattern matching."""
        from processors.directory_compressor import DirectoryCompressor
        
        exclusions = {"*.pyc", "__pycache__", "node_modules", "*.log"}
        
        # Test exact matches
        assert DirectoryCompressor._should_exclude("__pycache__", exclusions)
        assert DirectoryCompressor._should_exclude("node_modules", exclusions)
        
        # Test wildcard matches
        assert DirectoryCompressor._should_exclude("test.pyc", exclusions)
        assert DirectoryCompressor._should_exclude("app.log", exclusions)
        
        # Test non-matches
        assert not DirectoryCompressor._should_exclude("app.py", exclusions)
        assert not DirectoryCompressor._should_exclude("config.json", exclusions)
    
    def test_calculate_compression_ratio(self):
        """Test compression ratio calculation."""
        from processors.directory_compressor import DirectoryCompressor
        
        # Mock file info list
        file_info_list = [
            Mock(compress_size=100, file_size=200),
            Mock(compress_size=50, file_size=150),
            Mock(compress_size=25, file_size=100)
        ]
        
        ratio = DirectoryCompressor._calculate_compression_ratio(file_info_list)
        
        # Total compressed: 175, Total uncompressed: 450
        # Ratio should be (175/450) * 100 = 38.89%
        assert abs(ratio - 38.89) < 0.1
    
    def test_analyze_file_types(self):
        """Test file type analysis from archive."""
        from processors.directory_compressor import DirectoryCompressor
        
        # Mock file info list
        file_info_list = [
            Mock(filename="app.py", is_dir=lambda: False),
            Mock(filename="script.js", is_dir=lambda: False),
            Mock(filename="style.css", is_dir=lambda: False),
            Mock(filename="data.json", is_dir=lambda: False),
            Mock(filename="folder/", is_dir=lambda: True)  # Directory should be skipped
        ]
        
        file_types = DirectoryCompressor._analyze_file_types(file_info_list)
        
        assert file_types[".py"] == 1
        assert file_types[".js"] == 1
        assert file_types[".css"] == 1
        assert file_types[".json"] == 1
        # Directory should not be counted
        assert len(file_types) == 4
