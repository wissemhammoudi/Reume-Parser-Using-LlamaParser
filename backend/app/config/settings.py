import os
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    """Application settings and configuration."""
    
    API_V1_STR: str = Field(
        default="/api/v1",
        description="API version string for endpoints"
    )
    PROJECT_NAME: str = Field(
        default="Resume Parser API",
        description="Name of the project"
    )
    VERSION: str = Field(
        default="1.0.0",
        description="API version number"
    )
    
    HOST: str = Field(
        default="0.0.0.0",
        description="Host address to bind the server to"
    )
    PORT: int = Field(
        default=8080,
        description="Port number for the server",
        ge=1024,
        le=65535
    )
    DEBUG: bool = Field(
        default=True,
        description="Enable debug mode for development"
    )
    
    ALLOWED_ORIGINS: list = Field(
        default=["http://localhost:3000", "http://localhost:80"],
        description="List of allowed CORS origins"
    )
    
    GROQ_API_KEY: str = Field(
        default=os.getenv("GROQ_API_KEY", ""),
        description="API key for Groq AI service"
    )
    LLAMA_PARSE_API_KEY: str = Field(
        default=os.getenv("LLAMA_PARSE_API_KEY", ""),
        description="API key for LlamaParse service"
    )
    
    MAX_FILE_SIZE: int = Field(
        default=10 * 1024 * 1024,  
        description="Maximum file size in bytes",
        ge=1024 * 1024,  
        le=50 * 1024 * 1024  
    )
    ALLOWED_EXTENSIONS: list = Field(
        default=[".pdf"],
        description="List of allowed file extensions"
    )
    TEMP_DIR: str = Field(
        default="./tmp",
        description="Directory for temporary files"
    )
    OUTPUT_DIR: str = Field(
        default="./img",
        description="Directory for output images"
    )
    
    GROQ_MODEL: str = Field(
        default="llama3-8b-8192",
        description="Groq AI model to use for analysis"
    )
    GROQ_TEMPERATURE: float = Field(
        default=0.0,
        description="Temperature for AI model responses",
        ge=0.0,
        le=2.0
    )
    GROQ_MAX_TOKENS: int = Field(
        default=8192,
        description="Maximum tokens for AI responses",
        ge=1000,
        le=32768
    )
    CV_MODEL_PROTO: str = Field(
        default="../models/MobileNetSSD_deploy.prototxt",
        description="Path to MobileNetSSD prototxt file"
    )
    CV_MODEL_CAFFE: str = Field(
        default="../models/MobileNetSSD_deploy.caffemodel",
        description="Path to MobileNetSSD caffemodel file"
    )
    
    class Config:
        env_file = ".env"

settings = Settings()
