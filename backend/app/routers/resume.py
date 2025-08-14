from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from fastapi.responses import JSONResponse
import os
from typing import Optional

from app.services.resume_service import ResumeService
from app.utils.file_utils import validate_file, cleanup_temp_files
from app.config.settings import settings

router = APIRouter(prefix="/resume", tags=["resume"])

@router.post("/extract", response_class=JSONResponse)
async def extract_resume_info(
    pdf_file: UploadFile = File(..., description="PDF resume file to parse")
):
    """
    Extract information from a PDF resume using AI and computer vision.
    
    Args:
        pdf_file: PDF file containing the resume
        
    Returns:
        JSON response with extracted resume data
    """
    try:
        validation_result = validate_file(pdf_file)
        if not validation_result["valid"]:
            raise HTTPException(status_code=400, detail=validation_result["error"])
        
        temp_dir = settings.TEMP_DIR
        os.makedirs(temp_dir, exist_ok=True)
        
        pdf_path = os.path.join(temp_dir, pdf_file.filename)
        try:
            content = await pdf_file.read()
            with open(pdf_path, "wb") as f:
                f.write(content)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
        
        resume_service = ResumeService()
        result = await resume_service.process_resume(pdf_path)
        
        return JSONResponse(content={"data": result})
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
    finally:
        if 'pdf_path' in locals():
            cleanup_temp_files(pdf_path, temp_dir)

@router.get("/health")
async def resume_service_health():
    """Check the health of the resume parsing service."""
    try:
        resume_service = ResumeService()
        health_status = await resume_service.health_check()
        return {"status": "healthy", "details": health_status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Service unhealthy: {str(e)}")
