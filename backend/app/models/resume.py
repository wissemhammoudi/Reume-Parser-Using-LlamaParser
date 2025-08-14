from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime

class PersonalInfo(BaseModel):
    """Personal information model."""
    name: Optional[str] = Field(None, description="Full name")
    email: Optional[EmailStr] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    location: Optional[str] = Field(None, description="City, Country")
    linkedin: Optional[str] = Field(None, description="LinkedIn URL")

class Experience(BaseModel):
    """Work experience model."""
    title: str = Field(..., description="Job title")
    company: str = Field(..., description="Company name")
    duration: Optional[str] = Field(None, description="Duration of employment")
    description: Optional[str] = Field(None, description="Job description and achievements")
    start_date: Optional[datetime] = Field(None, description="Start date")
    end_date: Optional[datetime] = Field(None, description="End date")
    period_months: Optional[int] = Field(None, description="Duration in months")

class Education(BaseModel):
    """Education model."""
    degree: str = Field(..., description="Degree name")
    institution: str = Field(..., description="Institution name")
    year: Optional[str] = Field(None, description="Graduation year")
    gpa: Optional[float] = Field(None, description="GPA if mentioned")

class SkillGroup(BaseModel):
    """Skills group model."""
    category: str = Field(..., description="Skill category")
    skills: List[str] = Field(..., description="List of skills")
    count: Optional[int] = Field(None, description="Number of skills")
    level: Optional[str] = Field(None, description="Skill level assessment")
    experience_months: Optional[int] = Field(None, description="Total experience in months")
    contexts: Optional[List[str]] = Field(None, description="Contexts where skills were used")

class Project(BaseModel):
    """Project model."""
    name: str = Field(..., description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    technologies: Optional[List[str]] = Field(None, description="Technologies used")
    url: Optional[str] = Field(None, description="Project URL")

class EnhancedSkill(BaseModel):
    """Enhanced skill with experience information."""
    skill: str = Field(..., description="Skill name")
    total_months: int = Field(..., description="Total experience in months")
    contexts: List[str] = Field(default_factory=list, description="Job contexts")
    companies: List[str] = Field(default_factory=list, description="Companies where used")

class EnhancedSkills(BaseModel):
    """Enhanced skills summary."""
    skills_with_experience: List[EnhancedSkill] = Field(default_factory=list)
    total_skills: int = Field(0, description="Total number of skills")
    analysis_timestamp: str = Field(..., description="Analysis timestamp")

class ResumeData(BaseModel):
    """Complete resume data model."""
    personal_info: Optional[PersonalInfo] = Field(None, description="Personal information")
    summary: Optional[str] = Field(None, description="Professional summary")
    experience: List[Experience] = Field(default_factory=list, description="Work experience")
    education: List[Education] = Field(default_factory=list, description="Education")
    skills: List[SkillGroup] = Field(default_factory=list, description="Skills")
    certifications: List[str] = Field(default_factory=list, description="Certifications")
    languages: List[str] = Field(default_factory=list, description="Languages")
    projects: List[Project] = Field(default_factory=list, description="Projects")
    enhanced_skills: Optional[EnhancedSkills] = Field(None, description="Enhanced skills analysis")

class ResumeResponse(BaseModel):
    """API response model."""
    data: ResumeData = Field(..., description="Parsed resume data")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Processing metadata")

class ResumeUploadRequest(BaseModel):
    """Resume upload request model."""
    filename: str = Field(..., description="Uploaded file name")
    file_size: int = Field(..., description="File size in bytes")
    content_type: str = Field(..., description="File content type")

class HealthCheckResponse(BaseModel):
    """Health check response model."""
    status: str = Field(..., description="Service status")
    details: Dict[str, Any] = Field(default_factory=dict, description="Service details")
