# Advanced Intelligent Document Processing & Code Generation Interface
# Professional web application for software architecture synthesis

import streamlit as st
import requests
import json
from pathlib import Path
from typing import Dict, Any, Optional
import time

# Configure application settings and styling
st.set_page_config(
    page_title="Intelligent Code Architecture Generator",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API endpoint configuration - Updated to match the new main.py endpoints
DOCUMENT_PROCESSING_ENDPOINT = "http://localhost:8000/documents/parse_&_generate_srd_md"
DOCUMENT_COMPREHENSIVE_ENDPOINT = "http://localhost:8000/documents/parse_&_generate_srds"
DOCUMENT_ANALYSIS_ENDPOINT = "http://localhost:8000/documents/analyze"
SYSTEM_HEALTH_ENDPOINT = "http://localhost:8000/system/health"
TECHNICAL_SPECS_ENDPOINT = "http://localhost:8000/specifications/technical/generate"
BACKEND_GENERATION_ENDPOINT = "http://localhost:8000/generation/backend/initiate"
FRONTEND_GENERATION_ENDPOINT = "http://localhost:8000/generation/frontend/initiate"
BACKEND_ARTIFACTS_ENDPOINT = "http://localhost:8000/artifacts/backend/download"
WORKSPACE_EXPORT_ENDPOINT = "http://localhost:8000/artifacts/workspace/export"

class DocumentProcessingInterface:
    """
    Advanced document processing interface providing intelligent analysis
    and technical specification generation capabilities.
    """
    
    SUPPORTED_DOCUMENT_TYPES = ["pdf", "docx", "md", "txt"]
    MAX_FILE_SIZE_MB = 50
    
    @staticmethod
    def render_application_header():
        """Render the main application header with branding and description."""
        st.markdown("""
        # 🚀 Intelligent Code Architecture Generator
        
        **Transform your software requirements into comprehensive technical specifications**
        
        Our advanced AI-powered platform analyzes your documents and generates detailed
        frontend and backend technical specifications, ready for development teams.
        """)
        
        # Add system status indicator
        DocumentProcessingInterface._render_system_status()
    
    @staticmethod
    def _render_system_status():
        """Display real-time system health status."""
        try:
            health_response = requests.get(SYSTEM_HEALTH_ENDPOINT, timeout=5)
            if health_response.status_code == 200:
                health_data = health_response.json()
                st.success(f"✅ System Status: {health_data.get('service_status', 'Unknown')}")
            else:
                st.warning("⚠️ System health check failed")
        except requests.RequestException:
            st.error("❌ Unable to connect to backend services")
    
    @staticmethod
    def render_document_upload_section():
        """Render the intelligent document upload interface."""
        st.markdown("## 📄 Document Analysis & Processing")
        
        # Create upload interface with enhanced features
        col1, col2 = st.columns([2, 1])
        
        with col1:
            uploaded_document = st.file_uploader(
                "Upload your software requirements document",
                type=DocumentProcessingInterface.SUPPORTED_DOCUMENT_TYPES,
                help=f"Supported formats: {', '.join(DocumentProcessingInterface.SUPPORTED_DOCUMENT_TYPES)}. Max size: {DocumentProcessingInterface.MAX_FILE_SIZE_MB}MB"
            )
        
        with col2:
            st.markdown("### 📋 Processing Capabilities")
            st.markdown("""
            - **Multi-format Support**: PDF, DOCX, Markdown, Text
            - **Intelligent Parsing**: Advanced content extraction
            - **AI-Powered Analysis**: Requirements synthesis
            - **Technical Specifications**: Frontend & Backend docs
            """)
        
        return uploaded_document
    
    @staticmethod
    def process_uploaded_document(document_file) -> Optional[Dict[str, Any]]:
        """
        Process uploaded document and generate technical specifications.
        
        Args:
            document_file: Streamlit uploaded file object
            
        Returns:
            Dictionary containing processed specifications or None if failed
        """
        if not document_file:
            return None
        
        # Validate file size
        file_size_mb = len(document_file.getvalue()) / (1024 * 1024)
        if file_size_mb > DocumentProcessingInterface.MAX_FILE_SIZE_MB:
            st.error(f"❌ File size ({file_size_mb:.1f}MB) exceeds maximum limit of {DocumentProcessingInterface.MAX_FILE_SIZE_MB}MB")
            return None
        
        # Process document with progress tracking
        with st.spinner("🔄 Analyzing document and generating technical specifications..."):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Simulate processing steps with progress updates
                status_text.text("📖 Extracting document content...")
                progress_bar.progress(25)
                time.sleep(1)
                
                status_text.text("🧠 AI-powered requirement analysis...")
                progress_bar.progress(50)
                
                # Send document for processing using the new endpoint
                files = {"uploaded_file": (document_file.name, document_file.getvalue())}
                processing_response = requests.post(
                    DOCUMENT_PROCESSING_ENDPOINT, 
                    files=files,
                    timeout=120  # Extended timeout for AI processing
                )
                
                progress_bar.progress(75)
                status_text.text("📝 Generating technical specifications...")
                time.sleep(1)
                
                progress_bar.progress(100)
                status_text.text("✅ Processing completed successfully!")
                
                if processing_response.status_code == 200:
                    return processing_response.json()
                else:
                    st.error(f"❌ Processing failed: {processing_response.status_code} - {processing_response.text}")
                    return None
                    
            except requests.RequestException as e:
                st.error(f"❌ Network error during processing: {str(e)}")
                return None
            except Exception as e:
                st.error(f"❌ Unexpected error: {str(e)}")
                return None
            finally:
                progress_bar.empty()
                status_text.empty()
    
    @staticmethod
    def render_specification_results(specification_data: Dict[str, Any]):
        """
        Render the generated technical specifications with advanced UI components.
        
        Args:
            specification_data: Dictionary containing frontend and backend specifications
        """
        st.markdown("## 📋 Generated Technical Specifications")
        
        # Extract specification content
        frontend_spec = specification_data.get("frontend_technical_specification", "")
        backend_spec = specification_data.get("backend_technical_specification", "")
        document_metadata = specification_data.get("document_metadata", {})
        
        # Display processing metadata
        if document_metadata:
            st.info(f"✅ Successfully processed: {document_metadata.get('source_filename', 'Unknown')}")
        
        # Create tabbed interface for specifications
        tab1, tab2, tab3 = st.tabs(["🎨 Frontend Specification", "⚙️ Backend Specification", "📊 Analysis Summary"])
        
        with tab1:
            DocumentProcessingInterface._render_frontend_specification(frontend_spec)
        
        with tab2:
            DocumentProcessingInterface._render_backend_specification(backend_spec)
        
        with tab3:
            DocumentProcessingInterface._render_analysis_summary(specification_data)
    
    @staticmethod
    def _render_frontend_specification(frontend_content: str):
        """Render the frontend specification with enhanced formatting."""
        st.markdown("### 🎨 Frontend Technical Specification")
        
        col1, col2 = st.columns([3, 1])
        
            with col1:
            if frontend_content:
                st.markdown(frontend_content)
            else:
                st.warning("No frontend specification content available")
        
        with col2:
            st.markdown("#### 📥 Download Options")
            if frontend_content:
                st.download_button(
                    label="📄 Download as Markdown",
                    data=frontend_content,
                    file_name="frontend_specification.md",
                    mime="text/markdown"
                )
    
    @staticmethod
    def _render_backend_specification(backend_content: str):
        """Render the backend specification with enhanced formatting."""
        st.markdown("### ⚙️ Backend Technical Specification")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            if backend_content:
                st.markdown(backend_content)
            else:
                st.warning("No backend specification content available")
        
            with col2:
            st.markdown("#### 📥 Download Options")
            if backend_content:
                st.download_button(
                    label="📄 Download as Markdown",
                    data=backend_content,
                    file_name="backend_specification.md",
                    mime="text/markdown"
                )
    
    @staticmethod
    def _render_analysis_summary(specification_data: Dict[str, Any]):
        """Render analysis summary and additional options."""
        st.markdown("### 📊 Analysis Summary")
        
        # Display processing statistics
        frontend_spec = specification_data.get("frontend_technical_specification", "")
        backend_spec = specification_data.get("backend_technical_specification", "")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Frontend Spec Length", f"{len(frontend_spec)} characters")
        
        with col2:
            st.metric("Backend Spec Length", f"{len(backend_spec)} characters")
        
        with col3:
            total_length = len(frontend_spec) + len(backend_spec)
            st.metric("Total Content", f"{total_length} characters")
        
        # Additional processing options
        st.markdown("### 🔧 Additional Processing Options")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Generate Comprehensive PDFs", help="Generate PDF documents with both specifications"):
                DocumentProcessingInterface._generate_comprehensive_pdfs(specification_data)
        
        with col2:
            if st.button("⚙️ Initiate Backend Code Generation", help="Start backend code generation process"):
                DocumentProcessingInterface._initiate_backend_generation(backend_spec)
    
    @staticmethod
    def _generate_comprehensive_pdfs(specification_data: Dict[str, Any]):
        """Generate comprehensive PDF documents."""
        try:
            with st.spinner("🔄 Generating comprehensive PDF documents..."):
                # This would call the comprehensive analysis endpoint
                st.info("📄 PDF generation feature would call the comprehensive analysis endpoint")
                st.info("Endpoint: /documents/parse_&_generate_srds")
        except Exception as e:
            st.error(f"❌ PDF generation failed: {str(e)}")
    
    @staticmethod
    def _initiate_backend_generation(backend_spec: str):
        """Initiate backend code generation."""
        try:
            with st.spinner("🔄 Initiating backend code generation..."):
                # Call the backend generation endpoint
                response = requests.post(
                    BACKEND_GENERATION_ENDPOINT,
                    json={"technical_spec": backend_spec},
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    st.success(f"✅ {result.get('message', 'Backend generation initiated')}")
        else:
                    st.error(f"❌ Backend generation failed: {response.status_code}")
        except Exception as e:
            st.error(f"❌ Backend generation error: {str(e)}")

def main():
    """Main application entry point."""
    # Render application header
    DocumentProcessingInterface.render_application_header()
    
    # Render document upload section
    uploaded_file = DocumentProcessingInterface.render_document_upload_section()
    
    # Process uploaded document if available
    if uploaded_file is not None:
        specification_data = DocumentProcessingInterface.process_uploaded_document(uploaded_file)
        
        if specification_data:
            # Render specification results
            DocumentProcessingInterface.render_specification_results(specification_data)
        else:
            st.warning("⚠️ No specification data generated. Please try again.")

if __name__ == "__main__":
    main()
