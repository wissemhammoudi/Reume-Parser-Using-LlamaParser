import os
import logging
import fitz  
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class PDFService:
    """Service for extracting content from PDF files."""
    
    def __init__(self):
        self.supported_extensions = ['.pdf']
    
    async def extract_content(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract text and images from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary containing extracted text and image paths
        """
        try:
            if not os.path.exists(pdf_path):
                raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
            if not self._is_valid_pdf(pdf_path):
                raise ValueError("Invalid file format. Only PDF files are supported.")
            
            logger.info(f"Extracting content from: {pdf_path}")
            
            text_content = await self._extract_text(pdf_path)
            
            images = await self._extract_images(pdf_path)
            
            return {
                "text": text_content,
                "images": images,
                "pages": len(text_content.split('\n\n')) if text_content else 0
            }
            
        except Exception as e:
            logger.error(f"PDF extraction failed: {str(e)}")
            raise
    
    async def _extract_text(self, pdf_path: str) -> str:
        """Extract text content from PDF."""
        try:
            doc = fitz.open(pdf_path)
            text_content = ""
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text_content += page.get_text()
                text_content += "\n\n"  # Page separator
            
            doc.close()
            return text_content.strip()
            
        except Exception as e:
            logger.error(f"Text extraction failed: {str(e)}")
            raise
    
    async def _extract_images(self, pdf_path: str) -> List[str]:
        """Extract images from PDF."""
        try:
            doc = fitz.open(pdf_path)
            image_paths = []
            output_dir = "img"
            
            os.makedirs(output_dir, exist_ok=True)
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                image_list = page.get_images()
                
                for img_index, img in enumerate(image_list):
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    
                    image_filename = f"page_{page_num}_img_{img_index}.png"
                    image_path = os.path.join(output_dir, image_filename)
                    
                    with open(image_path, "wb") as image_file:
                        image_file.write(image_bytes)
                    
                    image_paths.append(image_path)
            
            doc.close()
            return image_paths
            
        except Exception as e:
            logger.error(f"Image extraction failed: {str(e)}")
            return []
    
    def _is_valid_pdf(self, file_path: str) -> bool:
        """Check if file is a valid PDF."""
        file_ext = Path(file_path).suffix.lower()
        return file_ext in self.supported_extensions
    
    async def health_check(self) -> Dict[str, Any]:
        """Check PDF service health."""
        try:
            test_doc = fitz.open()
            test_doc.close()
            
            return {
                "healthy": True,
                "message": "PDF service is operational",
                "supported_formats": self.supported_extensions
            }
        except Exception as e:
            return {
                "healthy": False,
                "message": f"PDF service error: {str(e)}",
                "supported_formats": self.supported_extensions
            }
