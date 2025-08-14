import os
import logging
from typing import Dict, Any
from pathlib import Path
from fastapi import UploadFile

from app.config.settings import settings

logger = logging.getLogger(__name__)

def validate_file(file: UploadFile) -> Dict[str, Any]:
    """
    Validate uploaded file for resume processing.
    
    Args:
        file: Uploaded file object
        
    Returns:
        Validation result dictionary
    """
    try:
        if not file:
            return {"valid": False, "error": "No file provided"}
        
        if file.size and file.size > settings.MAX_FILE_SIZE:
            max_size_mb = settings.MAX_FILE_SIZE / (1024 * 1024)
            return {
                "valid": False, 
                "error": f"File size exceeds maximum limit of {max_size_mb}MB"
            }
        
        if file.filename:
            file_ext = Path(file.filename).suffix.lower()
            if file_ext not in settings.ALLOWED_EXTENSIONS:
                allowed_exts = ", ".join(settings.ALLOWED_EXTENSIONS)
                return {
                    "valid": False, 
                    "error": f"Invalid file type. Allowed types: {allowed_exts}"
                }
        
        if file.content_type and not file.content_type.startswith('application/pdf'):
            return {
                "valid": False, 
                "error": "Invalid content type. Only PDF files are supported"
            }
        
        return {"valid": True, "message": "File validation passed"}
        
    except Exception as e:
        logger.error(f"File validation failed: {str(e)}")
        return {"valid": False, "error": f"Validation error: {str(e)}"}

def cleanup_temp_files(file_path: str, temp_dir: str):
    """
    Clean up temporary files and directories.
    
    Args:
        file_path: Path to the temporary file
        temp_dir: Path to the temporary directory
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Removed temporary file: {file_path}")
        
        if os.path.isdir(temp_dir) and not os.listdir(temp_dir):
            os.rmdir(temp_dir)
            logger.info(f"Removed empty temporary directory: {temp_dir}")
            
    except Exception as e:
        logger.error(f"Failed to cleanup temporary files: {str(e)}")

def ensure_directory_exists(directory_path: str) -> bool:
    """
    Ensure a directory exists, create if it doesn't.
    
    Args:
        directory_path: Path to the directory
        
    Returns:
        True if directory exists or was created successfully
    """
    try:
        os.makedirs(directory_path, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Failed to create directory {directory_path}: {str(e)}")
        return False

def get_file_info(file_path: str) -> Dict[str, Any]:
    """
    Get information about a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Dictionary with file information
    """
    try:
        if not os.path.exists(file_path):
            return {"error": "File not found"}
        
        stat_info = os.stat(file_path)
        
        return {
            "filename": os.path.basename(file_path),
            "size_bytes": stat_info.st_size,
            "size_mb": round(stat_info.st_size / (1024 * 1024), 2),
            "created": stat_info.st_ctime,
            "modified": stat_info.st_mtime,
            "extension": Path(file_path).suffix.lower()
        }
        
    except Exception as e:
        logger.error(f"Failed to get file info: {str(e)}")
        return {"error": str(e)}

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe file operations.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    try:
        unsafe_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
        sanitized = filename
        
        for char in unsafe_chars:
            sanitized = sanitized.replace(char, '_')
            
        if len(sanitized) > 255:
            name, ext = os.path.splitext(sanitized)
            sanitized = name[:255-len(ext)] + ext
        
        return sanitized
        
    except Exception as e:
        logger.error(f"Filename sanitization failed: {str(e)}")
        return "sanitized_file.pdf"
