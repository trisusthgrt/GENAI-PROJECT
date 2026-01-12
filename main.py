# Advanced Multi-Agent Document Processing & Code Generation Platform
# Intelligent document analysis and automated software artifact generation

from fastapi import FastAPI, File, UploadFile, Request, Response, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import io
import zipfile
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional

from processors.document_renderer import DocumentRenderer
from intelligence.requirement_synthesizer import RequirementSynthesizer
from processors.document_analyzer import DocumentProcessor, DocumentParsingException, UnsupportedDocumentType
from processors.artifact_packager import ArtifactProcessor
from intelligence.backend_architect import BackendArchitectureGenerator
from intelligence.frontend_designer import FrontendDesignGenerator
from processors.directory_compressor import DirectoryCompressor
from config.settings import ApplicationConfig

# Initialize core application service
document_processor_api = FastAPI(
    title="Intelligent Document Processing & Code Generation Platform",
    description="AI-powered document processing and software architecture generation platform",
    version="2.0.0",
    docs_url="/documentation",
    redoc_url="/api-reference"
)

# Add CORS middleware for web frontend support
document_processor_api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@document_processor_api.get("/")
async def application_status():
    """Root endpoint providing comprehensive system health information."""
    return {
        "service": "Intelligent Document Processing & Code Generation Platform",
        "status": "operational",
        "version": "2.0.0",
        "capabilities": ["document_processing", "code_generation", "specification_synthesis"],
        "api_documentation": "/documentation"
    }

@document_processor_api.post("/artifacts/backend/download")
async def retrieve_backend_artifacts(technical_specification: str):
    """
    Generate and package backend code artifacts from technical specifications.
    Returns a compressed archive containing generated backend components.
    """
    try:
        architecture_output = await BackendArchitectureGenerator.synthesize_backend_structure(technical_specification)
        
        # Extract content regardless of response format
        processed_content = (architecture_output.content 
                           if hasattr(architecture_output, "content") 
                           else str(architecture_output))
        
        artifact_collection = ArtifactProcessor.extract_generated_artifacts(processed_content)
        compressed_archive = ArtifactProcessor.create_compressed_archive(artifact_collection)
        
        return Response(
            content=compressed_archive.getvalue(),
            media_type="application/zip",
            headers={"Content-Disposition": "attachment; filename=backend_architecture.zip"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backend generation failed: {str(e)}")

@document_processor_api.get("/artifacts/workspace/export")
async def export_workspace_artifacts():
    """
    Export all generated artifacts from the current workspace.
    Creates a comprehensive archive of all generated code components.
    """
    try:
        source_directory = "artifacts"
        archive_destination = "workspace_export.zip"
        
        await asyncio.to_thread(DirectoryCompressor.compress_directory_structure, source_directory, archive_destination)
        
        return FileResponse(
            path=archive_destination,
            filename="generated_codebase.zip",
            media_type="application/zip",
            headers={"Content-Disposition": "attachment; filename=generated_codebase.zip"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workspace export failed: {str(e)}")

@document_processor_api.post("/generation/backend/initiate")
async def initiate_backend_generation(background_tasks: BackgroundTasks, technical_spec: str):
    """
    Initiate backend code generation process from technical specifications.
    Performs asynchronous generation and returns status confirmation.
    """
    if not technical_spec or not technical_spec.strip():
        raise HTTPException(
            status_code=400, 
            detail="Technical specification content is required for backend generation"
        )
    
    # Schedule background generation task
    background_tasks.add_task(BackendArchitectureGenerator.synthesize_backend_structure, technical_spec)
    
    return {
        "process": "initiated",
        "operation": "backend_code_generation",
        "status": "processing",
        "message": "Backend architecture generation started successfully"
    }

@document_processor_api.post("/generation/frontend/initiate")
async def initiate_frontend_generation(background_tasks: BackgroundTasks, interface_spec: str):
    """
    Initiate frontend code generation process from interface specifications.
    Performs asynchronous generation and returns status confirmation.
    """
    if not interface_spec or not interface_spec.strip():
        raise HTTPException(
            status_code=400,
            detail="Interface specification content is required for frontend generation"
        )
    
    # Schedule background generation task
    background_tasks.add_task(FrontendDesignGenerator.synthesize_frontend_components, interface_spec)
    
    return {
        "process": "initiated", 
        "operation": "frontend_code_generation",
        "status": "processing",
        "message": "Frontend design generation started successfully"
    }

@document_processor_api.post("/specifications/technical/generate")
async def synthesize_technical_specifications(request: Request):
    """
    Transform Software Requirements Specification (SRS) into detailed technical documents.
    Generates both frontend and backend specification documents in PDF format.
    """
    try:
        # Attempt to parse JSON payload
        request_data = await request.json()
        requirements_content = request_data.get('requirements_text', '')
    except Exception:
        # Fallback to raw text content
        requirements_content = (await request.body()).decode('utf-8')
    
    if not requirements_content.strip():
        raise HTTPException(
            status_code=400, 
            detail="Software requirements specification content is mandatory"
        )
    
    # Generate technical specifications using AI synthesizer
    frontend_specification, backend_specification = await RequirementSynthesizer.process_requirements(requirements_content)
    
    # Render specifications as PDF documents
    frontend_document = await DocumentRenderer.render_to_pdf(frontend_specification)
    backend_document = await DocumentRenderer.render_to_pdf(backend_specification)
    
    # Create compressed archive containing both documents
    archive_stream = io.BytesIO()
    with zipfile.ZipFile(archive_stream, 'w', zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('Frontend_Technical_Specification.pdf', frontend_document)
        archive.writestr('Backend_Technical_Specification.pdf', backend_document)
    
    archive_stream.seek(0)
    return StreamingResponse(
        io.BytesIO(archive_stream.getvalue()),
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=Technical_Specifications.zip"}
    )

@document_processor_api.get("/system/health")
async def system_health_assessment():
    """
    Comprehensive system health monitoring endpoint.
    Returns detailed status information about service components.
    """
    return {
        "service_status": "operational",
        "system_health": "excellent",
        "version": "2.0.0",
        "capabilities": ["document_processing", "code_generation", "specification_synthesis"],
        "uptime_status": "stable",
        "environment": ApplicationConfig.EXECUTION_ENVIRONMENT
    }

@document_processor_api.post("/documents/analyze")
async def analyze_uploaded_document(document: UploadFile = File(...)):
    """
    Intelligent document analysis and content extraction service.
    Supports multiple document formats with advanced parsing capabilities.
    """
    try:
        # Read uploaded document content
        document_content = await document.read()
        file_extension = "." + document.filename.split(".")[-1].lower()
        
        # Create temporary file for processing
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_document:
            temp_document.write(document_content)
            temporary_path = temp_document.name
        
        # Process document using intelligent analyzer
        analysis_result = DocumentProcessor.analyze_document_content(temporary_path)
        
        return JSONResponse(content=analysis_result)
        
    except UnsupportedDocumentType as exception:
        return JSONResponse(
            status_code=400, 
            content={"error_type": "unsupported_format", "details": str(exception)}
        )
    except DocumentParsingException as exception:
        return JSONResponse(
            status_code=500, 
            content={"error_type": "parsing_failure", "details": str(exception)}
        )
    except Exception as exception:
        return JSONResponse(
            status_code=500, 
            content={"error_type": "system_error", "details": f"Unexpected processing error: {exception}"}
        )

@document_processor_api.post("/documents/process-and-synthesize")
async def process_document_and_synthesize_specifications(uploaded_file: UploadFile = File(...)):
    """
    Advanced document processing pipeline that extracts content and generates 
    technical specifications in markdown format for both frontend and backend.
    """
    try:
        # Handle file upload and temporary storage
        file_extension = "." + uploaded_file.filename.split(".")[-1].lower()
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temporary_file:
            temporary_file.write(await uploaded_file.read())
            temporary_file_path = temporary_file.name
    except Exception as upload_error:
        raise HTTPException(
            status_code=500, 
            detail=f"Document upload processing error: {upload_error}"
        )
    
    try:
        # Extract and analyze document content
        document_analysis = DocumentProcessor.analyze_document_content(temporary_file_path)
        extracted_content = document_analysis["extracted_text"]
    except Exception as parsing_error:
        raise HTTPException(
            status_code=400, 
            detail=f"Document content extraction failed: {parsing_error}"
        )
    
    try:
        # Generate technical specifications using AI synthesis
        frontend_spec, backend_spec = await RequirementSynthesizer.process_requirements(extracted_content)
    except Exception as synthesis_error:
        raise HTTPException(
            status_code=500, 
            detail=f"Technical specification synthesis failed: {synthesis_error}"
        )
    
    return {
        "frontend_technical_specification": frontend_spec,
        "backend_technical_specification": backend_spec,
        "document_metadata": {
            "source_filename": uploaded_file.filename,
            "processing_status": "completed"
        }
    }

@document_processor_api.post("/documents/comprehensive-analysis")
async def comprehensive_document_analysis_and_generation(source_document: UploadFile = File(...)):
    """
    Complete document processing workflow that extracts content, generates technical 
    specifications, and renders them as professional PDF documents in a downloadable archive.
    """
    try:
        # Process uploaded document
        file_extension = "." + source_document.filename.split(".")[-1].lower()
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_storage:
            temp_storage.write(await source_document.read())
            document_path = temp_storage.name
    except Exception as processing_error:
        raise HTTPException(
            status_code=500, 
            detail=f"Document processing initialization failed: {processing_error}"
        )
    
    try:
        # Extract document content using intelligent parser
        content_analysis = DocumentProcessor.analyze_document_content(document_path)
        source_content = content_analysis["extracted_text"]
    except Exception as extraction_error:
        raise HTTPException(
            status_code=400, 
            detail=f"Content extraction process failed: {extraction_error}"
        )
    
    try:
        # Generate comprehensive technical specifications
        frontend_specification, backend_specification = await RequirementSynthesizer.process_requirements(source_content)
        
        # Render specifications as professional PDF documents
        frontend_pdf_document = DocumentRenderer.render_to_pdf(frontend_specification)
        backend_pdf_document = DocumentRenderer.render_to_pdf(backend_specification)
        
    except Exception as generation_error:
        raise HTTPException(
            status_code=500, 
            detail=f"Technical document generation failed: {generation_error}"
        )
    
    # Create comprehensive archive with all generated documents
    document_archive = io.BytesIO()
    with zipfile.ZipFile(document_archive, 'w', zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('Frontend_Technical_Specification.pdf', frontend_pdf_document)
        archive.writestr('Backend_Technical_Specification.pdf', backend_pdf_document)
    
    document_archive.seek(0)
    return StreamingResponse(
        io.BytesIO(document_archive.getvalue()),
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=Comprehensive_Technical_Documentation.zip"}
    )

# Application startup and configuration
@document_processor_api.on_event("startup")
async def startup_event():
    """Initialize application components and configurations on startup."""
    # Initialize directory structure
    ApplicationConfig.initialize_directories()
    
    print("🚀 Intelligent Document Processing Platform started successfully!")
    print(f"📚 API Documentation: http://localhost:8000/documentation")
    print(f"🔧 ReDoc API Reference: http://localhost:8000/api-reference")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:document_processor_api",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )