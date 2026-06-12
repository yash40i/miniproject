"""
PDF parsing module for Resume-Insight AI.
Handles multi-column text extraction from PDF resumes using PyMuPDF.
"""

import fitz  # PyMuPDF
import re
from typing import List, Tuple
from dataclasses import dataclass


@dataclass
class ParsedResume:
    """Data class for parsed resume content."""
    text: str
    num_pages: int
    page_texts: List[str]
    metadata: dict


class PDFParser:
    """
    Handles PDF parsing with support for multi-column layouts.
    Prioritizes logical reading order over visual order.
    """
    
    def __init__(self, pdf_path: str):
        """
        Initialize PDF parser.
        
        Args:
            pdf_path: Path to the PDF file
        """
        self.pdf_path = pdf_path
        self.document = None
        
    def extract_text(self) -> ParsedResume:
        """
        Extract text from PDF, handling multi-column layouts.
        
        Returns:
            ParsedResume object with extracted text and metadata
        """
        try:
            self.document = fitz.open(self.pdf_path)
            num_pages = len(self.document)
            
            page_texts = []
            all_text = []
            
            for page_num in range(num_pages):
                page = self.document[page_num]
                
                # Extract text with layout preservation
                # Using dict_output to detect multi-column structure
                text_dict = page.get_text("dict")
                
                # Process blocks to handle multi-column layouts
                page_text = self._process_page_blocks(text_dict)
                
                page_texts.append(page_text)
                all_text.append(page_text)
            
            combined_text = "\n\n".join(all_text)
            
            metadata = {
                "filename": self.pdf_path,
                "num_pages": num_pages,
                "creation_date": self._extract_metadata(),
            }
            
            return ParsedResume(
                text=combined_text,
                num_pages=num_pages,
                page_texts=page_texts,
                metadata=metadata
            )
            
        finally:
            if self.document:
                self.document.close()
    
    def _process_page_blocks(self, text_dict: dict) -> str:
        """
        Process text blocks to preserve logical reading order.
        Handles multi-column layouts by sorting blocks by position.
        
        Args:
            text_dict: Dictionary output from PyMuPDF get_text("dict")
            
        Returns:
            Processed text with improved reading order
        """
        blocks = text_dict.get("blocks", [])
        
        # Filter and sort text blocks
        text_blocks = []
        for block in blocks:
            if block["type"] == 0:  # Text block
                bbox = block.get("bbox")
                if bbox:
                    text_content = self._extract_block_text(block)
                    if text_content.strip():
                        text_blocks.append((bbox, text_content))
        
        # Sort by vertical position (top to bottom), then horizontal (left to right)
        text_blocks.sort(key=lambda x: (x[0][1], x[0][0]))
        
        # Combine sorted blocks
        extracted_text = "\n".join(block[1] for block in text_blocks)
        
        return extracted_text
    
    def _extract_block_text(self, block: dict) -> str:
        """
        Extract text from a single block, preserving line structure.
        
        Args:
            block: Text block dictionary from PyMuPDF
            
        Returns:
            Extracted text
        """
        text = ""
        for line in block.get("lines", []):
            line_text = ""
            for span in line.get("spans", []):
                line_text += span.get("text", "")
            text += line_text + "\n"
        
        return text
    
    def _extract_metadata(self) -> str:
        """Extract PDF metadata."""
        if self.document:
            metadata = self.document.metadata
            return metadata.get("creation_date", "Unknown")
        return "Unknown"


def parse_resume(pdf_path: str) -> ParsedResume:
    """
    Convenience function to parse a resume PDF.
    
    Args:
        pdf_path: Path to the resume PDF
        
    Returns:
        ParsedResume object
    """
    parser = PDFParser(pdf_path)
    return parser.extract_text()
