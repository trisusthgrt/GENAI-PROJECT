# 🚀 Intelligent Document Processing & Code Generation Platform

## 📋 Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Core Components](#core-components)
- [API Endpoints](#api-endpoints)
- [Installation & Setup](#installation--setup)
- [Usage](#usage)
- [Testing](#testing)
- [Project Structure](#project-structure)

## 🎯 Overview

This is an **Intelligent Document Processing & Code Generation Platform** that transforms software requirements documents into comprehensive technical specifications and generates code artifacts. The system uses AI-powered agents to analyze documents and synthesize detailed frontend and backend specifications.

### Key Features
- **Multi-format Document Processing**: PDF, DOCX, Markdown, Text
- **AI-Powered Analysis**: Advanced content extraction and analysis
- **Automated Code Generation**: Frontend and backend code synthesis
- **Technical Specification Generation**: Professional PDF documents
- **Artifact Management**: Organized code and documentation archives
- **Comprehensive Testing**: Full test coverage across all components

## 🏗️ Architecture

### High-Level Architecture
```
User Upload → Document Analysis → AI Synthesis → Code Generation → Artifact Delivery
```

### Technology Stack
- **Backend**: FastAPI (Python)
- **Frontend**: Streamlit (Web Interface)
- **AI Framework**: AutoGen (Multi-agent system)
- **Database**: SQLAlchemy ORM
- **Document Processing**: pdfplumber, python-docx
- **Testing**: pytest
- **Configuration**: python-dotenv

## 🔧 Core Components

### 1. Main Application (`main.py`)

#### FastAPI Application Setup
```python
app = FastAPI(
    title="Intelligent Document Processing & Code Generation Platform",
    description="AI-powered document processing and software architecture generation platform",
    version="2.0.0",
    docs_url="/documentation",
    redoc_url="/api-reference"
)
```

#### CORS Middleware Configuration
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### Key Endpoints:

**System Endpoints:**
- **`GET /`**: Application status and capabilities
- **`GET /system/health`**: Comprehensive health monitoring

**Document Processing Endpoints:**
- **`POST /documents/analyze`**: Intelligent document content extraction
- **`POST /documents/parse_&_generate_srd_md`**: Document analysis + specification generation
- **`POST /documents/parse_&_generate_srds`**: Complete workflow with PDF generation

**Code Generation Endpoints:**
- **`POST /generation/backend/initiate`**: Asynchronous backend code generation
- **`POST /generation/frontend/initiate`**: Asynchronous frontend code generation
- **`POST /specifications/technical/generate`**: Technical specification synthesis

**Artifact Management Endpoints:**
- **`POST /artifacts/backend/download`**: Backend code artifact packaging
- **`GET /artifacts/workspace/export`**: Complete workspace export

#### Application Startup
```python
@app.on_event("startup")
async def startup_event():
    """Initialize application components and configurations on startup."""
    ApplicationConfig.initialize_directories()
```

### 2. Configuration System (`config/`)

#### `ApplicationConfig` Class
```python
class ApplicationConfig:
    """Centralized configuration manager for the document processing platform."""
```

#### Configuration Categories:

**Environment Settings:**
```python
EXECUTION_ENVIRONMENT = os.getenv("EXECUTION_ENVIRONMENT", "development")
DEBUG_MODE = os.getenv("DEBUG_MODE", "true").lower() == "true"
```

**Logging Configuration:**
```python
LOG_VERBOSITY = os.getenv("LOG_VERBOSITY", "INFO")
LOG_ROTATION_SIZE = int(os.getenv("LOG_ROTATION_SIZE", "10485760"))  # 10MB
```

**Directory Management:**
```python
DOCUMENT_STORAGE_PATH = Path(os.getenv("DOCUMENT_STORAGE_PATH", "uploads"))
GENERATED_ARTIFACTS_PATH = Path(os.getenv("GENERATED_ARTIFACTS_PATH", "artifacts"))
TEMPORARY_WORKSPACE = Path(os.getenv("TEMPORARY_WORKSPACE", "temp"))
```

**Processing Configuration:**
```python
MAX_DOCUMENT_SIZE_MB = int(os.getenv("MAX_DOCUMENT_SIZE_MB", "50"))
SUPPORTED_DOCUMENT_FORMATS = ["pdf", "docx", "md", "txt"]
```

#### Configuration Methods:

**Directory Initialization:**
```python
@classmethod
def initialize_directories(cls) -> None:
    """Create necessary directories if they don't exist."""
    for directory in [cls.DOCUMENT_STORAGE_PATH, cls.GENERATED_ARTIFACTS_PATH, cls.TEMPORARY_WORKSPACE]:
        directory.mkdir(parents=True, exist_ok=True)
```

**Log File Path Generation:**
```python
@classmethod
def get_log_file_path(cls, service_name: str) -> Path:
    """Generate log file path for a specific service."""
    return Path("logs") / f"{service_name}_{cls.EXECUTION_ENVIRONMENT}.log"
```

### 3. Document Processors (`processors/`)

#### `DocumentProcessor` Class (`document_analyzer.py`)
```python
class DocumentProcessor:
    """Sophisticated document analysis engine capable of processing various document formats."""
    SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".md", ".txt"}
```

**Key Methods:**
- **`analyze_document_content()`**: Primary document analysis interface
- **`_process_pdf_document()`**: Advanced PDF content extraction
- **`_process_word_document()`**: Microsoft Word document processing
- **`_process_text_document()`**: Plain text and markdown processing
- **`_identify_content_sections()`**: Intelligent content sectioning

#### `DocumentRenderer` Class (`document_renderer.py`)
```python
class DocumentRenderer:
    """High-quality document rendering engine that transforms text content into professional PDF documents."""
```

**Key Methods:**
- **`render_to_pdf()`**: Asynchronous PDF rendering interface
- **`_generate_pdf_document()`**: Core PDF generation logic
- **`_is_header_line()`**: Intelligent header detection
- **`_render_header()`**: Render section headers with enhanced typography
- **`_render_paragraph()`**: Render regular paragraph content

#### `ArtifactProcessor` Class (`artifact_packager.py`)
```python
class ArtifactProcessor:
    """Sophisticated code artifact extraction and packaging engine."""
```

**Key Methods:**
- **`extract_generated_artifacts()`**: Advanced artifact extraction
- **`create_compressed_archive()`**: Create compressed ZIP archive
- **`_clean_generated_content()`**: Apply comprehensive content cleaning
- **`_validate_artifact()`**: Validate extracted artifacts
- **`_normalize_file_path()`**: Normalize file paths
- **`_determine_content_type()`**: Determine content type based on file extension

#### `DirectoryCompressor` Class (`directory_compressor.py`)
```python
class DirectoryCompressor:
    """Sophisticated directory compression engine that creates optimized archives."""
```

**Key Methods:**
- **`compress_directory_async()`**: Asynchronous directory compression
- **`compress_directory_structure()`**: Comprehensive directory compression
- **`get_archive_info()`**: Extract comprehensive archive information
- **`_should_exclude()`**: Check if item should be excluded
- **`_calculate_compression_ratio()`**: Calculate compression efficiency

#### `CodeArtifactManager` Class (`file_operations.py`)
```python
class CodeArtifactManager:
    """Advanced code artifact management system."""
```

**Key Methods:**
- **`save_code_artifact()`**: Intelligent code artifact storage
- **`ensure_directory_structure()`**: Create complete directory structure
- **`get_artifact_inventory()`**: Generate comprehensive artifact inventory
- **`cleanup_artifacts()`**: Clean up generated artifacts
- **`_store_artifact_metadata()`**: Store comprehensive metadata
- **`_estimate_code_complexity()`**: Estimate code complexity

#### Exception Classes (`exceptions.py`)
```python
class DocumentProcessingException(Exception):  # Base exception
class DocumentParsingException(DocumentProcessingException):  # Document parsing errors
class UnsupportedDocumentType(DocumentProcessingException):  # Unsupported formats
class ContentExtractionException(DocumentProcessingException):  # Content extraction errors
class ArtifactGenerationException(DocumentProcessingException):  # Artifact generation errors
class CompressionException(DocumentProcessingException):  # Compression errors
class ConfigurationException(DocumentProcessingException):  # Configuration errors
```

### 4. Data Models (`models/`)

#### Enums
```python
class DocumentType(str, Enum):
    PDF = "pdf"
    WORD = "docx"
    MARKDOWN = "md"
    TEXT = "txt"
    UNKNOWN = "unknown"

class ProcessingStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ArchitectureType(str, Enum):
    FRONTEND = "frontend"
    BACKEND = "backend"
    FULLSTACK = "fullstack"
    MICROSERVICES = "microservices"
```

#### SQLAlchemy ORM Models

**`DocumentEntity`:**
```python
class DocumentEntity(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False, index=True)
    document_type = Column(String(50), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    content_hash = Column(String(64), unique=True, index=True)  # SHA-256 hash
    upload_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    processing_status = Column(String(50), default=ProcessingStatus.PENDING, nullable=False)
    extracted_content = Column(Text)
    content_analysis = Column(JSON)  # Structured analysis results
```

**`SpecificationEntity`:**
```python
class SpecificationEntity(Base):
    __tablename__ = "specifications"
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    specification_type = Column(String(50), nullable=False)  # frontend/backend
    specification_content = Column(Text, nullable=False)
    generation_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    version = Column(Integer, default=1, nullable=False)
    complexity_score = Column(Integer)
    completeness_rating = Column(Integer)
```

**`CodeGenerationJob`:**
```python
class CodeGenerationJob(Base):
    __tablename__ = "code_generation_jobs"
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    architecture_type = Column(String(50), nullable=False)
    job_status = Column(String(50), default=ProcessingStatus.PENDING, nullable=False)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    progress_percentage = Column(Integer, default=0)
    generation_parameters = Column(JSON)  # AI agent configuration
    generated_artifacts = Column(JSON)    # File paths and metadata
    error_details = Column(Text)          # Error information if failed
```

#### Pydantic Request/Response Models

**Request Models:**
- **`DocumentUploadRequest`**: Request model for document upload operations
- **`SpecificationGenerationRequest`**: Request model for technical specification generation
- **`CodeGenerationRequest`**: Request model for automated code generation

**Response Models:**
- **`DocumentAnalysisResponse`**: Response model for document analysis results
- **`SpecificationResponse`**: Response model for generated technical specifications
- **`CodeGenerationResponse`**: Response model for code generation job status
- **`SystemHealthResponse`**: Response model for comprehensive system health monitoring

#### Model Registry
```python
class ModelRegistry:
    """Central registry for all data models providing intelligent model management."""
    
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
```

### 5. Frontend Interface (`frontend/`)

#### `DocumentProcessingInterface` Class (`streamlit_app.py`)
```python
class DocumentProcessingInterface:
    """Advanced document processing interface providing intelligent analysis and technical specification generation capabilities."""
    
    SUPPORTED_DOCUMENT_TYPES = ["pdf", "docx", "md", "txt"]
    MAX_FILE_SIZE_MB = 50
```

#### Key Methods:

**Application Header:**
```python
@staticmethod
def render_application_header():
    """Render the main application header with branding and description."""
```

**System Status:**
```python
@staticmethod
def _render_system_status():
    """Display real-time system health status."""
```

**Document Upload:**
```python
@staticmethod
def render_document_upload_section():
    """Render the intelligent document upload interface."""
```

**Document Processing:**
```python
@staticmethod
def process_uploaded_document(document_file) -> Optional[Dict[str, Any]]:
    """Process uploaded document and generate technical specifications."""
```

**Specification Rendering:**
```python
@staticmethod
def render_specification_results(specification_data: Dict[str, Any]):
    """Render the generated technical specifications with advanced UI components."""
```

**Frontend Specification:**
```python
@staticmethod
def _render_frontend_specification(frontend_content: str):
    """Render the frontend specification with enhanced formatting."""
```

**Backend Specification:**
```python
@staticmethod
def _render_backend_specification(backend_content: str):
    """Render the backend specification with enhanced formatting."""
```

**Analysis Summary:**
```python
@staticmethod
def _render_analysis_summary(specification_data: Dict[str, Any]):
    """Render analysis summary and additional options."""
```

**Additional Features:**
```python
@staticmethod
def _generate_comprehensive_pdfs(specification_data: Dict[str, Any]):
    """Generate comprehensive PDF documents."""

@staticmethod
def _initiate_backend_generation(backend_spec: str):
    """Initiate backend code generation."""
```

#### API Endpoint Configuration
```python
DOCUMENT_PROCESSING_ENDPOINT = "http://localhost:8000/documents/parse_&_generate_srd_md"
DOCUMENT_COMPREHENSIVE_ENDPOINT = "http://localhost:8000/documents/parse_&_generate_srds"
DOCUMENT_ANALYSIS_ENDPOINT = "http://localhost:8000/documents/analyze"
SYSTEM_HEALTH_ENDPOINT = "http://localhost:8000/system/health"
TECHNICAL_SPECS_ENDPOINT = "http://localhost:8000/specifications/technical/generate"
BACKEND_GENERATION_ENDPOINT = "http://localhost:8000/generation/backend/initiate"
FRONTEND_GENERATION_ENDPOINT = "http://localhost:8000/generation/frontend/initiate"
BACKEND_ARTIFACTS_ENDPOINT = "http://localhost:8000/artifacts/backend/download"
WORKSPACE_EXPORT_ENDPOINT = "http://localhost:8000/artifacts/workspace/export"
```

## 📡 API Endpoints

### System Endpoints
| Endpoint | Method | Purpose | Response |
|----------|--------|---------|----------|
| `/` | GET | Application status | JSON |
| `/system/health` | GET | System health | JSON |

### Document Processing
| Endpoint | Method | Purpose | Response |
|----------|--------|---------|----------|
| `/documents/analyze` | POST | Document analysis | JSON |
| `/documents/parse_&_generate_srd_md` | POST | Document processing | JSON |
| `/documents/parse_&_generate_srds` | POST | Complete workflow | ZIP |

### Code Generation
| Endpoint | Method | Purpose | Response |
|----------|--------|---------|----------|
| `/generation/backend/initiate` | POST | Backend generation | JSON |
| `/generation/frontend/initiate` | POST | Frontend generation | JSON |
| `/specifications/technical/generate` | POST | Technical specs | ZIP |

### Artifact Management
| Endpoint | Method | Purpose | Response |
|----------|--------|---------|----------|
| `/artifacts/backend/download` | POST | Backend artifacts | ZIP |
| `/artifacts/workspace/export` | GET | Workspace export | ZIP |

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- OpenAI API key
- Git

### Installation Steps

1. **Clone the repository**
```bash
git clone <repository-url>
cd test-file
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
# Create .env file
cp .env.example .env

# Configure your OpenAI API key
echo "OPENAI_API_KEY=your_openai_api_key" >> .env
```

4. **Initialize directories**
```bash
python -c "from config.settings import ApplicationConfig; ApplicationConfig.initialize_directories()"
```

### Environment Configuration
```bash
# Required
OPENAI_API_KEY=your_openai_api_key

# Optional (with defaults)
EXECUTION_ENVIRONMENT=development
DEBUG_MODE=true
LOG_VERBOSITY=INFO
DOCUMENT_STORAGE_PATH=uploads
GENERATED_ARTIFACTS_PATH=artifacts
TEMPORARY_WORKSPACE=temp
MAX_DOCUMENT_SIZE_MB=50
```

## 💻 Usage

### Starting the Application

1. **Run the FastAPI backend**
```bash
python main.py
```

2. **Run the Streamlit frontend** (optional)
```bash
streamlit run frontend/streamlit_app.py
```

3. **Access the application**
- **API Documentation**: http://localhost:8000/documentation
- **ReDoc Reference**: http://localhost:8000/api-reference
- **Frontend Interface**: http://localhost:8501

### Basic Usage Workflow

1. **Upload Document**: Upload a software requirements document (PDF, DOCX, MD, TXT)
2. **Process Document**: The system analyzes and extracts content
3. **Generate Specifications**: AI agents create technical specifications
4. **Generate Code**: Automated code generation for frontend/backend
5. **Download Artifacts**: Download generated code and documentation

### Example API Usage

#### Document Analysis
```bash
curl -X POST "http://localhost:8000/documents/analyze" \
  -H "Content-Type: multipart/form-data" \
  -F "document=@requirements.pdf"
```

#### Technical Specification Generation
```bash
curl -X POST "http://localhost:8000/specifications/technical/generate" \
  -H "Content-Type: application/json" \
  -d '{"requirements_text": "Create a user management system..."}'
```

#### Backend Code Generation
```bash
curl -X POST "http://localhost:8000/generation/backend/initiate" \
  -H "Content-Type: application/json" \
  -d '{"technical_spec": "FastAPI backend with user authentication..."}'
```

## 🧪 Testing

### Running Tests

1. **Run all tests**
```bash
pytest
```

2. **Run specific test categories**
```bash
pytest tests/test_main_endpoints.py    # API endpoint tests
pytest tests/test_processors.py        # Processor module tests
pytest tests/test_intelligence.py      # AI agent tests
pytest tests/test_integration.py       # Integration tests
```

3. **Run with coverage**
```bash
pytest --cov=. --cov-report=html
```

### Test Categories

- **Unit Tests**: Individual component functionality
- **Integration Tests**: End-to-end workflow testing
- **API Tests**: Endpoint functionality and error handling
- **Configuration Tests**: Settings and database operations

## 📁 Project Structure

```
test file/
├── main.py                    # Main FastAPI application
├── requirements.txt           # Dependencies
├── pytest.ini               # Pytest configuration
├── config/                   # Configuration management
│   ├── settings.py          # Application configuration
│   └── __init__.py
├── processors/               # Document processing modules
│   ├── document_analyzer.py  # Multi-format document parsing
│   ├── document_renderer.py  # PDF generation
│   ├── artifact_packager.py  # Code artifact extraction
│   ├── directory_compressor.py # ZIP archive creation
│   ├── file_operations.py    # File system operations
│   ├── exceptions.py         # Custom exception classes
│   └── __init__.py
├── frontend/                 # Web interface
│   ├── streamlit_app.py     # Streamlit application
│   └── __init__.py
├── models/                   # Data models
│   └── __init__.py          # ORM models and schemas
├── logs/                     # Application logs
├── output/                   # Generated outputs
└── artifacts/                # Generated code artifacts
```

## 🔄 Workflow Process

### 1. Document Upload & Analysis
```
User Upload → File Validation → Document Processor → Content Extraction
```

### 2. Requirement Synthesis
```
Extracted Content → AI Agents → Technical Specifications → PDF Generation
```

### 3. Code Generation
```
Technical Specs → Backend/Frontend Generators → Code Artifacts → ZIP Packaging
```

### 4. Artifact Delivery
```
Generated Code → Artifact Processor → Compressed Archive → Download
```

## 🎯 Key Innovations

1. **Modular Architecture**: Clear separation between processing, intelligence, and presentation layers
2. **AI-Powered Analysis**: Multi-agent system for intelligent requirement processing
3. **Multi-Format Support**: Comprehensive document format handling
4. **Asynchronous Processing**: Background tasks for long-running operations
5. **Professional Output**: PDF generation and ZIP packaging
6. **Comprehensive Testing**: Full test coverage across all components
7. **Modern UI**: Professional Streamlit interface with real-time status
8. **Error Resilience**: Robust exception handling and validation

---

**Built with ❤️ using FastAPI, Streamlit, and AutoGen**
