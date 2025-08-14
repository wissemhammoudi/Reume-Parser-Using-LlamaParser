import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from app.services.pdf_service import PDFService
from app.services.ai_service import AIService
from app.services.cv_service import ComputerVisionService
from app.services.skills_service import SkillsService
from app.config.settings import settings

logger = logging.getLogger(__name__)

class ResumeService:
    """Main service for processing resumes."""
    
    def __init__(self):
        self.pdf_service = PDFService()
        self.ai_service = AIService()
        self.cv_service = ComputerVisionService()
        self.skills_service = SkillsService()
        
    async def process_resume(self, pdf_path: str) -> Dict[str, Any]:
        """
        Process a resume PDF through the complete pipeline.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Processed resume data
        """
        try:
            logger.info(f"Starting resume processing for: {pdf_path}")
            
            pdf_data = await self.pdf_service.extract_content(pdf_path)
            if not pdf_data:
                raise Exception("Failed to extract content from PDF")
            
            
            images_data = await self.cv_service.process_images(pdf_data.get("images", []))
            
            
            ai_analysis = await self.ai_service.analyze_resume(
                pdf_data["text"], 
                images_data
            )
            
            enhanced_data = await self.skills_service.enhance_skills(ai_analysis)
            
            final_result = {
                "resume_data": enhanced_data,
                "images_analyzed": len(images_data),
                "processing_status": "completed",
                "metadata": {
                    "file_name": os.path.basename(pdf_path),
                    "file_size": os.path.getsize(pdf_path),
                    "processing_time": "calculated_later"  
                }
            }
            
            logger.info(f"Resume processing completed successfully")
            return final_result
            
        except Exception as e:
            logger.error(f"Resume processing failed: {str(e)}")
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """Check the health of all services."""
        health_status = {
            "pdf_service": await self.pdf_service.health_check(),
            "ai_service": await self.ai_service.health_check(),
            "cv_service": await self.cv_service.health_check(),
            "skills_service": await self.skills_service.health_check()
        }
        
        overall_healthy = all(
            status.get("healthy", False) 
            for status in health_status.values()
        )
        
        return {
            "healthy": overall_healthy,
            "services": health_status
        }
