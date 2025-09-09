import fitz  # PyMuPDF
import docx
import io
import re
from typing import Union, List, Tuple
import logging

logger = logging.getLogger(__name__)


class FileParser:
    """Advanced file parser with text extraction and cleaning capabilities"""

    @staticmethod
    def extract_text_from_pdf(file_bytes: bytes) -> str:
        """Extract and clean text from PDF bytes"""
        try:
            text = ""
            with fitz.open(stream=file_bytes, filetype="pdf") as doc:
                for page in doc:
                    text += page.get_text()

            # Clean text
            text = FileParser.clean_extracted_text(text)
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise

    @staticmethod
    def extract_text_from_docx(file_bytes: bytes) -> str:
        """Extract and clean text from DOCX bytes"""
        try:
            text = ""
            doc = docx.Document(io.BytesIO(file_bytes))
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"

            # Clean text
            text = FileParser.clean_extracted_text(text)
            return text
        except Exception as e:
            logger.error(f"Error extracting text from DOCX: {e}")
            raise

    @staticmethod
    def clean_extracted_text(text: str) -> str:
        """Clean and normalize extracted text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove non-printable characters but keep common symbols
        text = re.sub(r'[^\x20-\x7E\u00A0-\u024F\u0400-\u04FF]', ' ', text)

        # Normalize line breaks for better processing
        text = text.replace('\n', ' ').replace('\r', ' ')

        # Trim and return
        return text.strip()

    @staticmethod
    def extract_contact_info(text: str) -> dict:
        """Extract potential contact information from text"""
        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)

        # Phone pattern (international format)
        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}'
        phones = re.findall(phone_pattern, text)

        return {
            'emails': emails[:3],  # Limit to first 3 matches
            'phones': phones[:3]  # Limit to first 3 matches
        }

    @staticmethod
    def parse_resume(file_bytes: bytes, filename: str) -> dict:
        """Parse a resume file and return structured data"""
        file_ext = filename.split('.')[-1].lower()

        if file_ext == 'pdf':
            text = FileParser.extract_text_from_pdf(file_bytes)
        elif file_ext == 'docx':
            text = FileParser.extract_text_from_docx(file_bytes)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")

        contact_info = FileParser.extract_contact_info(text)

        return {
            'filename': filename,
            'text': text,
            'contact_info': contact_info,
            'word_count': len(text.split())
        }