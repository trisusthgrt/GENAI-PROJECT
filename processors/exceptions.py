# Advanced Exception Handling for Document Processing System
"""
Comprehensive exception hierarchy for robust error handling across
the document processing and code generation pipeline.
"""

class DocumentProcessingException(Exception):
    """Base exception for all document processing related errors."""
    
    def __init__(self, message: str, error_code: str = None):
        super().__init__(message)
        self.error_code = error_code or "GENERIC_PROCESSING_ERROR"
        self.message = message

class DocumentParsingException(DocumentProcessingException):
    """Raised when document content extraction fails."""
    
    def __init__(self, message: str):
        super().__init__(message, "DOCUMENT_PARSING_FAILED")

class UnsupportedDocumentType(DocumentProcessingException):
    """Raised when attempting to process unsupported file formats."""
    
    def __init__(self, message: str):
        super().__init__(message, "UNSUPPORTED_DOCUMENT_FORMAT")

class ContentExtractionException(DocumentProcessingException):
    """Raised when content extraction algorithms fail."""
    
    def __init__(self, message: str):
        super().__init__(message, "CONTENT_EXTRACTION_FAILED")

class ArtifactGenerationException(DocumentProcessingException):
    """Raised when code artifact generation encounters errors."""
    
    def __init__(self, message: str):
        super().__init__(message, "ARTIFACT_GENERATION_FAILED")

class CompressionException(DocumentProcessingException):
    """Raised when archive creation or compression fails."""
    
    def __init__(self, message: str):
        super().__init__(message, "COMPRESSION_OPERATION_FAILED")

class ConfigurationException(DocumentProcessingException):
    """Raised when system configuration is invalid or incomplete."""
    
    def __init__(self, message: str):
        super().__init__(message, "CONFIGURATION_ERROR")
