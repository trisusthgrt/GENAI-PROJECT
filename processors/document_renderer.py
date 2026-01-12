# Advanced Document Rendering and PDF Generation System
"""
Professional document rendering service that converts markdown and text content
into formatted PDF documents with sophisticated layout and typography.
"""

from fpdf import FPDF
from typing import Union
import asyncio
from processors.exceptions import DocumentParsingException

class DocumentRenderer:
    """
    High-quality document rendering engine that transforms text content
    into professional PDF documents with advanced formatting capabilities.
    """
    
    # Document styling configuration
    DEFAULT_FONT_FAMILY = "Arial"
    DEFAULT_FONT_SIZE = 11
    HEADER_FONT_SIZE = 14
    LINE_SPACING = 8
    MARGIN_HORIZONTAL = 20
    MARGIN_VERTICAL = 20
    
    @classmethod
    async def render_to_pdf(cls, content: str) -> bytes:
        """
        Asynchronous PDF rendering interface that processes content in background.
        
        Args:
            content: Text content to be rendered as PDF
            
        Returns:
            PDF document as bytes for download or storage
        """
        return await asyncio.to_thread(cls._generate_pdf_document, content)
    
    @classmethod
    def _generate_pdf_document(cls, document_content: str) -> bytes:
        """
        Core PDF generation logic with advanced formatting and layout management.
        Handles multi-page documents with consistent styling.
        """
        try:
            # Initialize PDF document with professional settings
            pdf_document = FPDF()
            pdf_document.set_auto_page_break(auto=True, margin=15)
            pdf_document.add_page()
            
            # Configure document fonts and styling
            pdf_document.set_font(cls.DEFAULT_FONT_FAMILY, size=cls.DEFAULT_FONT_SIZE)
            pdf_document.set_margins(cls.MARGIN_HORIZONTAL, cls.MARGIN_VERTICAL, cls.MARGIN_HORIZONTAL)
            
            # Process content with intelligent formatting
            content_lines = document_content.split('\n')
            
            for line in content_lines:
                processed_line = line.strip()
                
                if not processed_line:
                    # Add spacing for empty lines
                    pdf_document.ln(cls.LINE_SPACING // 2)
                    continue
                
                # Detect and format headers
                if cls._is_header_line(processed_line):
                    cls._render_header(pdf_document, processed_line)
                else:
                    cls._render_paragraph(pdf_document, processed_line)
            
            # Generate PDF as bytes for response
            pdf_bytes = pdf_document.output(dest='S').encode('latin1')
            return pdf_bytes
            
        except Exception as rendering_error:
            raise DocumentParsingException(f"PDF document rendering failed: {rendering_error}")
    
    @classmethod
    def _is_header_line(cls, text_line: str) -> bool:
        """
        Intelligent header detection using multiple heuristics.
        Identifies lines that should be formatted as section headers.
        """
        # Markdown-style headers
        if text_line.startswith('#'):
            return True
        
        # ALL CAPS headers (minimum length check)
        if text_line.isupper() and len(text_line) > 10:
            return True
        
        # Numbered section headers
        import re
        if re.match(r'^\d+\.?\s+[A-Z]', text_line):
            return True
        
        return False
    
    @classmethod
    def _render_header(cls, pdf: FPDF, header_text: str) -> None:
        """
        Render section headers with enhanced typography and spacing.
        """
        # Clean markdown formatting
        clean_header = header_text.lstrip('#').strip()
        
        # Apply header styling
        pdf.ln(cls.LINE_SPACING)
        pdf.set_font(cls.DEFAULT_FONT_FAMILY, style='B', size=cls.HEADER_FONT_SIZE)
        pdf.cell(0, cls.LINE_SPACING * 1.5, clean_header, ln=True)
        pdf.set_font(cls.DEFAULT_FONT_FAMILY, size=cls.DEFAULT_FONT_SIZE)
        pdf.ln(cls.LINE_SPACING // 2)
    
    @classmethod
    def _render_paragraph(cls, pdf: FPDF, paragraph_text: str) -> None:
        """
        Render regular paragraph content with word wrapping and proper spacing.
        """
        # Handle long lines with intelligent wrapping
        try:
            pdf.multi_cell(0, cls.LINE_SPACING, paragraph_text)
            pdf.ln(2)  # Add small spacing between paragraphs
        except Exception:
            # Fallback for problematic characters
            safe_text = paragraph_text.encode('latin1', errors='ignore').decode('latin1')
            pdf.multi_cell(0, cls.LINE_SPACING, safe_text)
            pdf.ln(2)
