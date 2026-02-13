"""
PDF Generator Utility for AI-Shark

Converts markdown content to PDF format for download.
"""

import os
import logging
import tempfile
from pathlib import Path
from typing import Optional

try:
    import markdown
    from weasyprint import HTML, CSS
    from weasyprint.text.fonts import FontConfiguration
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False
    
try:
    import pdfkit
    PDFKIT_AVAILABLE = True
except ImportError:
    PDFKIT_AVAILABLE = False

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class PDFGenerator:
    """
    Utility class for generating PDFs from markdown content
    """
    
    def __init__(self):
        """Initialize PDF generator with available backend"""
        self.backend = self._detect_backend()
        logger.info(f"PDFGenerator initialized with backend: {self.backend}")
    
    def _detect_backend(self) -> str:
        """
        Detect which PDF generation backend is available
        
        Returns:
            Backend name: 'weasyprint', 'pdfkit', or 'none'
        """
        if WEASYPRINT_AVAILABLE:
            return 'weasyprint'
        elif PDFKIT_AVAILABLE:
            return 'pdfkit'
        else:
            return 'none'
    
    def markdown_to_pdf(self, 
                       markdown_content: str, 
                       output_path: str,
                       title: Optional[str] = None) -> bool:
        """
        Convert markdown content to PDF
        
        Args:
            markdown_content: Markdown text to convert
            output_path: Path where PDF should be saved
            title: Optional title for the document
            
        Returns:
            True if successful, False otherwise
        """
        if self.backend == 'none':
            logger.error("No PDF generation backend available. Install weasyprint or pdfkit.")
            return False
        
        try:
            if self.backend == 'weasyprint':
                return self._weasyprint_convert(markdown_content, output_path, title)
            elif self.backend == 'pdfkit':
                return self._pdfkit_convert(markdown_content, output_path, title)
        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            return False
        
        return False
    
    def _weasyprint_convert(self, 
                           markdown_content: str, 
                           output_path: str,
                           title: Optional[str] = None) -> bool:
        """
        Convert using WeasyPrint backend
        
        Args:
            markdown_content: Markdown content
            output_path: Output PDF path
            title: Document title
            
        Returns:
            True if successful
        """
        try:
            # Convert markdown to HTML
            html_content = markdown.markdown(
                markdown_content,
                extensions=['extra', 'codehilite', 'toc']
            )
            
            # Create full HTML document
            full_html = self._create_html_document(html_content, title)
            
            # Generate PDF with WeasyPrint
            font_config = FontConfiguration()
            html_doc = HTML(string=full_html)
            css = CSS(string=self._get_pdf_styles())
            
            html_doc.write_pdf(output_path, stylesheets=[css], font_config=font_config)
            
            logger.info(f"PDF generated successfully with WeasyPrint: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"WeasyPrint conversion failed: {e}")
            return False
    
    def _pdfkit_convert(self, 
                       markdown_content: str, 
                       output_path: str,
                       title: Optional[str] = None) -> bool:
        """
        Convert using pdfkit backend
        
        Args:
            markdown_content: Markdown content
            output_path: Output PDF path
            title: Document title
            
        Returns:
            True if successful
        """
        try:
            # Convert markdown to HTML
            html_content = markdown.markdown(
                markdown_content,
                extensions=['extra', 'codehilite', 'toc']
            )
            
            # Create full HTML document
            full_html = self._create_html_document(html_content, title)
            
            # Configure pdfkit options
            options = {
                'page-size': 'A4',
                'margin-top': '0.75in',
                'margin-right': '0.75in',
                'margin-bottom': '0.75in',
                'margin-left': '0.75in',
                'encoding': "UTF-8",
                'no-outline': None,
                'enable-local-file-access': None
            }
            
            # Generate PDF
            pdfkit.from_string(full_html, output_path, options=options)
            
            logger.info(f"PDF generated successfully with pdfkit: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"pdfkit conversion failed: {e}")
            return False
    
    def _create_html_document(self, body_content: str, title: Optional[str] = None) -> str:
        """
        Create complete HTML document with styling
        
        Args:
            body_content: HTML body content
            title: Document title
            
        Returns:
            Complete HTML document
        """
        doc_title = title or "Investment Memo"
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{doc_title}</title>
    <style>
        {self._get_html_styles()}
    </style>
</head>
<body>
    {body_content}
</body>
</html>"""
    
    def _get_html_styles(self) -> str:
        """
        Get CSS styles for HTML document
        
        Returns:
            CSS styles as string
        """
        return """
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: white;
        }
        
        h1 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-top: 30px;
        }
        
        h2 {
            color: #34495e;
            border-bottom: 1px solid #bdc3c7;
            padding-bottom: 5px;
            margin-top: 25px;
        }
        
        h3 {
            color: #34495e;
            margin-top: 20px;
        }
        
        blockquote {
            border-left: 4px solid #3498db;
            margin: 1em 0;
            padding-left: 1em;
            color: #666;
            font-style: italic;
        }
        
        code {
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 3px;
            padding: 2px 4px;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 0.9em;
        }
        
        pre {
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 5px;
            padding: 10px;
            overflow-x: auto;
        }
        
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 1em 0;
        }
        
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        
        th {
            background-color: #f2f2f2;
            font-weight: bold;
        }
        
        ul, ol {
            padding-left: 25px;
        }
        
        li {
            margin-bottom: 5px;
        }
        
        hr {
            border: none;
            border-top: 2px solid #bdc3c7;
            margin: 30px 0;
        }
        
        .page-break {
            page-break-before: always;
        }
        
        @media print {
            body {
                margin: 0;
                padding: 15px;
            }
            
            h1 {
                page-break-after: avoid;
            }
            
            h2, h3 {
                page-break-after: avoid;
            }
        }
        """
    
    def _get_pdf_styles(self) -> str:
        """
        Get CSS styles specifically for PDF generation
        
        Returns:
            CSS styles for PDF
        """
        return """
        @page {
            margin: 2cm;
            size: A4;
        }
        
        body {
            font-family: 'DejaVu Sans', Arial, sans-serif;
            font-size: 11pt;
            line-height: 1.4;
            color: #333;
        }
        
        h1 {
            font-size: 18pt;
            color: #2c3e50;
            border-bottom: 2pt solid #3498db;
            padding-bottom: 5pt;
            margin-top: 20pt;
            margin-bottom: 15pt;
        }
        
        h2 {
            font-size: 14pt;
            color: #34495e;
            border-bottom: 1pt solid #bdc3c7;
            padding-bottom: 3pt;
            margin-top: 15pt;
            margin-bottom: 10pt;
        }
        
        h3 {
            font-size: 12pt;
            color: #34495e;
            margin-top: 12pt;
            margin-bottom: 8pt;
        }
        
        p {
            margin-bottom: 8pt;
            text-align: justify;
        }
        
        ul, ol {
            margin-bottom: 8pt;
        }
        
        li {
            margin-bottom: 3pt;
        }
        
        code {
            font-family: 'DejaVu Sans Mono', monospace;
            background-color: #f8f9fa;
            padding: 1pt 2pt;
            font-size: 10pt;
        }
        
        pre {
            background-color: #f8f9fa;
            padding: 8pt;
            margin: 8pt 0;
            font-size: 9pt;
            line-height: 1.2;
        }
        
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 8pt 0;
            font-size: 10pt;
        }
        
        th, td {
            border: 0.5pt solid #ddd;
            padding: 4pt;
        }
        
        th {
            background-color: #f2f2f2;
            font-weight: bold;
        }
        
        hr {
            border: none;
            border-top: 1pt solid #bdc3c7;
            margin: 15pt 0;
        }
        """
    
    def is_available(self) -> bool:
        """
        Check if PDF generation is available
        
        Returns:
            True if a backend is available
        """
        return self.backend != 'none'
    
    def get_backend_info(self) -> dict:
        """
        Get information about available backends
        
        Returns:
            Dictionary with backend availability information
        """
        return {
            'weasyprint_available': WEASYPRINT_AVAILABLE,
            'pdfkit_available': PDFKIT_AVAILABLE,
            'current_backend': self.backend,
            'is_available': self.is_available()
        }


# Global instance for convenience
pdf_generator = PDFGenerator()


def convert_markdown_to_pdf(markdown_content: str, 
                           output_path: str,
                           title: Optional[str] = None) -> bool:
    """
    Convenience function to convert markdown to PDF
    
    Args:
        markdown_content: Markdown text to convert
        output_path: Path where PDF should be saved
        title: Optional document title
        
    Returns:
        True if successful, False otherwise
    """
    return pdf_generator.markdown_to_pdf(markdown_content, output_path, title)


def is_pdf_generation_available() -> bool:
    """
    Check if PDF generation is available
    
    Returns:
        True if PDF generation is possible
    """
    return pdf_generator.is_available()


def get_pdf_backend_info() -> dict:
    """
    Get information about PDF generation backends
    
    Returns:
        Backend information dictionary
    """
    return pdf_generator.get_backend_info()