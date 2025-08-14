# Resume Parser API Documentation

> Extract structured information from PDF resumes using AI and computer vision

## Overview

The Resume Parser API processes PDF resumes and returns structured JSON data. Perfect for HR systems, ATS platforms, and recruitment tools.

## Base URL
```
http://localhost:80
```

## Quick Start

```bash
# Health check
curl http://localhost/health

# Extract resume
curl -X POST "http://localhost:80/api/v1/resume/extract" \
  -F "pdf_file=@resume.pdf"
```

## Endpoints

### 1. Resume Extraction

**POST** `/api/v1/resume/extract`

Extract structured information from a PDF resume.

**Request:**
- **Content-Type**: `multipart/form-data`
- **Body**: PDF file upload

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `pdf_file` | File | Yes | PDF resume file (max 10MB) |

**Response:**
```json
{
  "data": {
    "personal_info": {
      "name": "John Doe",
      "email": "john@example.com",
      "phone": "+1-555-0123",
      "location": "New York, USA",
      "linkedin": "https://linkedin.com/in/johndoe"
    },
    "summary": "Experienced software engineer...",
    "experience": [
      {
        "title": "Senior Software Engineer",
        "company": "Tech Corp",
        "duration": "2020 - Present",
        "period_months": 36
      }
    ],
    "education": [
      {
        "degree": "Bachelor of Science in Computer Science",
        "institution": "University of Technology",
        "year": "2018"
      }
    ],
    "skills": [
      {
        "category": "Programming Languages",
        "skills": ["Python", "JavaScript"],
        "experience_months": 48
      }
    ],
    "enhanced_skills": {
      "skills_with_experience": [
        {
          "skill": "Python",
          "total_months": 48,
          "contexts": ["Software Development"],
          "companies": ["Tech Corp"]
        }
      ]
    }
  }
}
```

**Status Codes:**
| Code | Description |
|------|-------------|
| `200` | Success |
| `400` | Bad Request |
| `500` | Internal Server Error |

### 2. Service Health Check

**GET** `/api/v1/resume/health`

Check the health status of all resume parsing services.

**Response:**
```json
{
  "status": "healthy",
  "details": {
    "pdf_service": {"healthy": true, "message": "PDF service operational"},
    "ai_service": {"healthy": true, "message": "AI service operational"},
    "cv_service": {"healthy": true, "message": "Computer vision operational"},
    "skills_service": {"healthy": true, "message": "Skills service operational"}
  }
}
```

### 3. Application Status

**GET** `/`

Get basic application information.

**Response:**
```json
{
  "message": "Resume Parser API",
  "version": "1.0.0",
  "docs": "/docs"
}
```

### 4. System Health

**GET** `/health`

Overall system health status.

**Response:**
```json
{
  "status": "healthy"
}
```

## Data Structure

### Resume Data Fields

- **personal_info**: Name, email, phone, location, LinkedIn
- **summary**: Professional summary
- **experience**: Job history with title, company, duration
- **education**: Academic background
- **skills**: Categorized skills with experience levels
- **enhanced_skills**: Skills mapped to job contexts and companies

## File Requirements

- **Format**: PDF only
- **Size**: Maximum 10MB
- **Content**: Text-based resumes work best

