"""Document Parsers Package."""

from episteme.retrieval.parsers.html_parser import ParsedHTMLResult, parse_html_content
from episteme.retrieval.parsers.pdf_parser import ParsedPDFResult, parse_pdf_content

__all__ = [
    "ParsedHTMLResult",
    "ParsedPDFResult",
    "parse_html_content",
    "parse_pdf_content",
]
