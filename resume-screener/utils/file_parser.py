import fitz  # PyMuPDF
import docx
import io
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FileParser:

    @staticmethod
    def extract_text_from_pdf(file_bytes: bytes) -> str:
        """Extract text from PDF bytes"""
        try:
            text = ""
            with fitz.open(stream=file_bytes, filetype="pdf") as doc:
                for page in doc:
                    text += page.get_text("text") + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"PDF parsing failed: {e}")
            return ""

    @staticmethod
    def extract_text_from_docx(file_bytes: bytes) -> str:
        """Extract text from DOCX bytes"""
        try:
            doc = docx.Document(io.BytesIO(file_bytes))
            return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
        except Exception as e:
            logger.error(f"DOCX parsing failed: {e}")
            return ""

    @staticmethod
    def clean_text(text: str) -> str:
        return re.sub(r'\n{2,}', '\n', text).strip()

    @staticmethod
    def extract_contact_info(text: str) -> dict:
        emails = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
        phones = re.findall(
            r"(?:\+?\d{1,3}[\s-]?)?(?:\(?\d{2,4}\)?[\s-]?)?\d{6,10}", text
        )
        phones = [p.strip() for p in phones if len(re.sub(r"\D", "", p)) >= 7]
        urls = {}
        if re.search(r"(http|www\.|linkedin|github|bit|coding|leetcode|gfg|codefroces\.ly|tinyurl)", text, re.IGNORECASE):
            urls["message"] = "Links found – please check manually"

        return {"emails": emails, "phones": phones, "urls": urls}

    @staticmethod
    def split_sections(text: str) -> dict:
        """Split resume into sections using headings"""
        sections = {}
        try:
            lines = text.split("\n")
            current_header = "General"
            sections[current_header] = []

            for line in lines:
                if re.match(r"^[A-Z][A-Za-z\s&]+$", line.strip()) and len(line.strip()) < 40:
                    current_header = line.strip()
                    sections[current_header] = []
                else:
                    sections[current_header].append(line.strip())

            # Clean up
            return {k: " ".join(v).strip() for k, v in sections.items() if v}
        except Exception as e:
            logger.error(f"Section splitting failed: {e}")
            return {"General": text}

    @staticmethod
    def parse_file(file_path: str) -> dict:
        try:
            with open(file_path, "rb") as f:
                file_bytes = f.read()

            if file_path.lower().endswith(".pdf"):
                raw_text = FileParser.extract_text_from_pdf(file_bytes)
            elif file_path.lower().endswith(".docx"):
                raw_text = FileParser.extract_text_from_docx(file_bytes)
            else:
                raise ValueError("Unsupported file format (only PDF/DOCX supported)")

            text = FileParser.clean_text(raw_text)
            contact = FileParser.extract_contact_info(text)
            sections = FileParser.split_sections(text)

            return {
                "filename": file_path.split("/")[-1],
                "word_count": len(text.split()),
                "contact_info": contact,
                "sections": sections,
                "text": text
            }

        except Exception as e:
            logger.error(f"Resume parsing failed: {e}")
            return {}
