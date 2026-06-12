#!/usr/bin/env python3
from src.pipeline.text_cleaner import TextCleaner, clean_text
from src.pipeline.pdf_parser import PDFParser

# Test PDF extraction
print("Testing PDF extraction...")
try:
    parser = PDFParser('sample_resume.pdf')
    result = parser.extract_text()
    print(f"Pages: {result.num_pages}")
    print(f"Text length: {len(result.text)}")
    print(f"Text preview: {result.text[:300] if result.text else 'EMPTY'}")
    
    if result.text:
        # Test text cleaning
        print("\n\nTesting text cleaning...")
        cleaned = clean_text(result.text)
        print(f"Cleaned text length: {len(cleaned)}")
        print(f"Cleaned text: {cleaned[:300]}")
    else:
        print("ERROR: No text extracted from PDF!")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
