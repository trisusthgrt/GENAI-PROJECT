# Advanced Data Models and Schema Definitions
"""
Comprehensive data modeling package providing sophisticated entity definitions,
validation schemas, and database relationship management for the intelligent
document processing and code generation platform.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from pydantic import BaseModel, Field, validator
from enum import Enum

# SQLAlchemy declarative base
Base = declarative_base()

# Enums for standardized values
class DocumentType(str, Enum):
    """Document type enumeration for classification."""
    PDF = "pdf"
    WORD = "docx"
    MARKDOWN = "md"
    TEXT = "txt"
    UNKNOWN = "unknown"

class ProcessingStatus(str, Enum):
    """Processing status enumeration for workflow tracking."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ArchitectureType(str, Enum):
    """Architecture type enumeration for code generation."""
    FRONTEND = "frontend"
    BACKEND = "backend"
    FULLSTACK = "fullstack"
    MICROSERVICES = "microservices"

# SQLAlchemy ORM Models
class DocumentEntity(Base):
    """
    Advanced document entity model with comprehensive metadata tracking.
    Stores document information, processing history, and analysis results.
    """
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False, index=True)
    document_type = Column(String(50), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    content_hash = Column(String(64), unique=True, index=True)  # SHA-256 hash
    upload_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    processing_status = Column(String(50), default=ProcessingStatus.PENDING, nullable=False)
    
    # Content and analysis
    extracted_content = Column(Text)
    content_analysis = Column(JSON)  # Structured analysis results
    
    # Relationships
    specifications = relationship("SpecificationEntity", back_populates="source_document")
    generation_jobs = relationship("CodeGenerationJob", back_populates="source_document")
    
    def __repr__(self):
        return f"<DocumentEntity(id={self.id}, filename='{self.filename}', type='{self.document_type}')>"

class SpecificationEntity(Base):
    """
    Technical specification entity storing generated requirements and design documents.
    Links to source documents and tracks specification evolution.
    """
    __tablename__ = "specifications"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    specification_type = Column(String(50), nullable=False)  # frontend/backend
    specification_content = Column(Text, nullable=False)
    generation_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    version = Column(Integer, default=1, nullable=False)
    
    # Quality metrics
    complexity_score = Column(Integer)
    completeness_rating = Column(Integer)
    
    # Relationships
    source_document = relationship("DocumentEntity", back_populates="specifications")
    
    def __repr__(self):
        return f"<SpecificationEntity(id={self.id}, type='{self.specification_type}', version={self.version})>"

class CodeGenerationJob(Base):
    """
    Code generation job tracking entity for monitoring AI-powered code synthesis.
    Stores job parameters, progress, and generated artifacts.
    """
    __tablename__ = "code_generation_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    architecture_type = Column(String(50), nullable=False)
    job_status = Column(String(50), default=ProcessingStatus.PENDING, nullable=False)
    
    # Timing and progress
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    progress_percentage = Column(Integer, default=0)
    
    # Configuration and results
    generation_parameters = Column(JSON)  # AI agent configuration
    generated_artifacts = Column(JSON)    # File paths and metadata
    error_details = Column(Text)          # Error information if failed
    
    # Relationships
    source_document = relationship("DocumentEntity", back_populates="generation_jobs")
    
    def __repr__(self):
        return f"<CodeGenerationJob(id={self.id}, type='{self.architecture_type}', status='{self.job_status}')>"

# Pydantic Request/Response Models
class DocumentUploadRequest(BaseModel):
    """Request model for document upload operations."""
    filename: str = Field(..., min_length=1, max_length=255)
    content_base64: str = Field(..., description="Base64 encoded document content")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    @validator('filename')
    def validate_filename(cls, v):
        """Validate filename format and extension."""
        if not any(v.lower().endswith(ext) for ext in ['.pdf', '.docx', '.md', '.txt']):
            raise ValueError('Unsupported file format')
        return v

class DocumentAnalysisResponse(BaseModel):
    """Response model for document analysis results."""
    document_id: int
    filename: str
    document_type: DocumentType
    processing_status: ProcessingStatus
    extracted_content: Optional[str] = None
    content_analysis: Optional[Dict[str, Any]] = None
    upload_timestamp: datetime
    
    class Config:
        from_attributes = True

class SpecificationGenerationRequest(BaseModel):
    """Request model for technical specification generation."""
    document_id: int
    specification_types: List[str] = Field(default=["frontend", "backend"])
    generation_parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    @validator('specification_types')
    def validate_specification_types(cls, v):
        """Validate specification type values."""
        valid_types = {"frontend", "backend", "fullstack"}
        for spec_type in v:
            if spec_type not in valid_types:
                raise ValueError(f"Invalid specification type: {spec_type}")
        return v

class SpecificationResponse(BaseModel):
    """Response model for generated technical specifications."""
    specification_id: int
    document_id: int
    specification_type: str
    specification_content: str
    generation_timestamp: datetime
    version: int
    complexity_score: Optional[int] = None
    completeness_rating: Optional[int] = None
    
    class Config:
        from_attributes = True

class CodeGenerationRequest(BaseModel):
    """Request model for automated code generation."""
    specification_id: int
    architecture_type: ArchitectureType
    generation_parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)
    output_preferences: Optional[Dict[str, str]] = Field(default_factory=dict)

class CodeGenerationResponse(BaseModel):
    """Response model for code generation job status and results."""
    job_id: int
    document_id: int
    architecture_type: ArchitectureType
    job_status: ProcessingStatus
    progress_percentage: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    generated_artifacts: Optional[Dict[str, Any]] = None
    error_details: Optional[str] = None
    
    class Config:
        from_attributes = True

class SystemHealthResponse(BaseModel):
    """Response model for comprehensive system health monitoring."""
    service_status: str
    system_health: str
    version: str
    components: Dict[str, str]
    capabilities: List[str]
    performance_metrics: Dict[str, str]
    database_connectivity: Optional[str] = None
    ai_service_status: Optional[str] = None

# Model Registry and Utilities
class ModelRegistry:
    """
    Central registry for all data models providing intelligent model management
    and validation capabilities across the application.
    """
    
    ORM_MODELS = {
        "document": DocumentEntity,
        "specification": SpecificationEntity,
        "generation_job": CodeGenerationJob
    }
    
    REQUEST_MODELS = {
        "document_upload": DocumentUploadRequest,
        "specification_generation": SpecificationGenerationRequest,
        "code_generation": CodeGenerationRequest
    }
    
    RESPONSE_MODELS = {
        "document_analysis": DocumentAnalysisResponse,
        "specification": SpecificationResponse,
        "code_generation": CodeGenerationResponse,
        "system_health": SystemHealthResponse
    }
    
    @classmethod
    def get_model(cls, category: str, model_name: str):
        """
        Retrieve a specific model from the registry.
        
        Args:
            category: Model category (orm, request, response)
            model_name: Specific model name
            
        Returns:
            Model class if found, None otherwise
        """
        model_maps = {
            "orm": cls.ORM_MODELS,
            "request": cls.REQUEST_MODELS,
            "response": cls.RESPONSE_MODELS
        }
        
        return model_maps.get(category, {}).get(model_name)
    
    @classmethod
    def list_models(cls) -> Dict[str, List[str]]:
        """
        List all available models by category.
        
        Returns:
            Dictionary containing model categories and their available models
        """
        return {
            "orm_models": list(cls.ORM_MODELS.keys()),
            "request_models": list(cls.REQUEST_MODELS.keys()),
            "response_models": list(cls.RESPONSE_MODELS.keys())
        }

# Package exports
__all__ = [
    "Base",
    "DocumentType", "ProcessingStatus", "ArchitectureType",
    "DocumentEntity", "SpecificationEntity", "CodeGenerationJob",
    "DocumentUploadRequest", "DocumentAnalysisResponse",
    "SpecificationGenerationRequest", "SpecificationResponse",
    "CodeGenerationRequest", "CodeGenerationResponse",
    "SystemHealthResponse", "ModelRegistry"
]
