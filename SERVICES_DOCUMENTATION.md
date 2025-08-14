# Resume Parser Services Documentation


## Overview

The Resume Parser backend is built using a modular service-oriented architecture. Each service handles a specific responsibility, making the system maintainable, testable, and scalable.

##  Service Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   ResumeService │───▶│  PDFService     │───▶│  PyMuPDF        │
│   (Orchestrator)│    │  (Text/Image    │    │  (PDF Processing)│
│                 │    │   Extraction)   │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│  AIService      │    │ ComputerVision  │
│  (Groq AI)     │    │ Service         │
│                 │    │ (OpenCV)        │
└─────────────────┘    └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│ SkillsService   │    │  Image Analysis │
│ (Enhancement)   │    │  Results        │
└─────────────────┘    └─────────────────┘
```

##  Core Services

### 1. ResumeService (Main Orchestrator)

**Location**: `app/services/resume_service.py`

**Purpose**: Coordinates the entire resume processing pipeline by orchestrating all other services.

**Key Methods**:
- `process_resume(pdf_path)`: Main processing method
- `health_check()`: Service health monitoring

**Dependencies**:
- PDFService
- AIService
- ComputerVisionService
- SkillsService

**Processing Flow**:
1. **Content Extraction**: Calls PDFService to extract text and images
2. **Computer Vision**: Processes images using ComputerVisionService
3. **AI Analysis**: Analyzes text using AIService
4. **Skills Enhancement**: Enhances data using SkillsService
5. **Result Assembly**: Combines all results into final output

### 2. PDFService (PDF Processing)

**Location**: `app/services/pdf_service.py`

**Purpose**: Handles PDF file processing, text extraction, and image extraction.

**Key Methods**:
- `extract_content(pdf_path)`: Extract text and images from PDF
- `_extract_text(pdf_path)`: Extract text content
- `_extract_images(pdf_path)`: Extract and save images
- `health_check()`: Service health monitoring

**Features**:
- **Text Extraction**: Clean text extraction with page separation
- **Image Extraction**: Automatic image detection and saving
- **File Validation**: PDF format and size validation
- **Error Handling**: Comprehensive error handling for corrupted files

**Output Format**:
```json
{
  "text": "Extracted text content...",
  "images": ["img/page_0_img_0.png", "img/page_1_img_0.png"],
  "pages": 2
}
```

**Configuration**:
- **Supported Formats**: PDF only (`.pdf`)
- **Max File Size**: 10MB (`MAX_FILE_SIZE = 10 * 1024 * 1024`)
- **Output Directory**: `./img` (`OUTPUT_DIR = "./img"`)
- **Temp Directory**: `./tmp` (`TEMP_DIR = "./tmp"`)
- **Image Format**: PNG

### 3. AIService (AI Analysis)

**Location**: `app/services/ai_service.py`

**Purpose**: Provides AI-powered resume analysis using Groq AI and language translation.

**Key Methods**:
- `analyze_resume(text_content, images_data)`: Main analysis method
- `_get_ai_analysis(prompt)`: Groq AI API interaction
- `_parse_ai_response(ai_response)`: Response parsing and validation
- `_translate_text(text)`: Language translation
- `health_check()`: Service health monitoring

**Features**:
- **Groq AI Integration**: Uses Llama3-8b-8192 model
- **Structured Prompts**: Consistent extraction prompts
- **Multi-language Support**: Automatic translation to English
- **Response Validation**: JSON structure validation
- **Fallback Handling**: Graceful degradation on AI failures

**AI Prompt Structure**:
```json
{
  "personal_info": {
    "name": "Full Name",
    "email": "Email Address",
    "phone": "Phone Number",
    "location": "City, Country",
    "linkedin": "LinkedIn URL"
  },
  "experience": [
    {
      "title": "Job Title",
      "company": "Company Name",
      "duration": "Duration",
      "description": "Job description"
    }
  ],
  "skills": [
    {
      "category": "Skill Category",
      "skills": ["Skill 1", "Skill 2"]
    }
  ]
}
```

**Configuration**:
- **AI Model**: llama3-8b-8192 (`GROQ_MODEL = "llama3-8b-8192"`)
- **Temperature**: 0.0 (deterministic) (`GROQ_TEMPERATURE = 0.0`)
- **Max Tokens**: 8192 (`GROQ_MAX_TOKENS = 8192`)
- **API Keys**: GROQ (`GROQ_API_KEY`) and LlamaParse (`LLAMA_PARSE_API_KEY`)
- **Translation**: Deep Translator API

### 4. ComputerVisionService (Image Analysis)

**Location**: `app/services/cv_service.py`

**Purpose**: Analyzes images extracted from resumes using OpenCV and MobileNetSSD.

**Key Methods**:
- `process_images(image_paths)`: Process multiple images
- `_analyze_image(image_path)`: Analyze single image
- `_extract_image_features(image)`: Extract image characteristics
- `health_check()`: Service health monitoring

**Features**:
- **Object Detection**: MobileNetSSD model for 21 object classes
- **Image Analysis**: Edge detection, texture analysis, intensity analysis
- **Feature Extraction**: Comprehensive image feature extraction
- **Summary Generation**: Human-readable analysis summaries

**Supported Object Classes**:
```
background, aeroplane, bicycle, bird, boat, bottle, bus, car, cat, 
chair, cow, diningtable, dog, horse, motorbike, person, pottedplant, 
sheep, sofa, train, tvmonitor
```

**Output Format**:
```json
{
  "file_path": "img/page_0_img_0.png",
  "file_name": "page_0_img_0.png",
  "dimensions": {"width": 800, "height": 600},
  "objects_detected": [
    {
      "class": "person",
      "confidence": 0.95,
      "bbox": [100, 150, 300, 450]
    }
  ],
  "features": {
    "mean_intensity": 127.5,
    "edge_density": 0.15,
    "texture_score": 45.2
  },
  "analysis_summary": "Detected objects: 1 person; Image appears bright"
}
```

**Configuration**:
- **Model Files**: 
  - Prototxt: `../models/MobileNetSSD_deploy.prototxt` (`CV_MODEL_PROTO`)
  - Caffe Model: `../models/MobileNetSSD_deploy.caffemodel` (`CV_MODEL_CAFFE`)
- **Confidence Threshold**: 0.5 (hardcoded in service)
- **Image Processing**: 300x300 input size
- **Feature Extraction**: Edge detection, texture analysis, intensity analysis

### 5. SkillsService (Skills Enhancement)

**Location**: `app/services/skills_service.py`

**Purpose**: Enhances skills information by mapping experience periods and categorizing skills.

**Key Methods**:
- `enhance_skills(resume_data)`: Main enhancement method
- `_add_period_fields(experience_list)`: Add date fields to experience
- `_extract_skills_periods(resume_data)`: Extract skills with periods
- `_sum_skills_periods(skills_periods, threshold)`: Aggregate skills experience
- `health_check()`: Service health monitoring

**Features**:
- **Period Analysis**: Parse duration strings into dates
- **Skills Mapping**: Link skills to job contexts and companies
- **Experience Calculation**: Calculate total months of experience
- **Skills Categorization**: Organized by type and context
- **Context Awareness**: Track where skills were used


**Skills Categories**:
- Programming Languages
- Frameworks
- Databases
- Cloud Platforms
- Tools
- Methodologies
- Languages

**Output Enhancement**:
```json
{
  "enhanced_skills": {
    "skills_with_experience": [
      {
        "skill": "Python",
        "total_months": 48,
        "contexts": ["Software Development", "Data Analysis"],
        "companies": ["Tech Corp", "Startup Inc"]
      }
    ],
    "total_skills": 1,
    "analysis_timestamp": "2024-01-15T14:30:00"
  }
}
```

**Configuration**:
- **Experience Threshold**: 0.8 months minimum
- **Date Formats**: Multiple format support
- **Skill Extraction**: Common skills dictionary
- **Skills Validation**: Confirm skills mentioned in job descriptions


## Data Flow Between Services

1. **ResumeService → PDFService**
   - Input: PDF file path
   - Output: Text content and image paths

2. **ResumeService → ComputerVisionService**
   - Input: List of image paths
   - Output: Image analysis results

3. **ResumeService → AIService**
   - Input: Text content and image data
   - Output: Structured resume data

4. **ResumeService → SkillsService**
   - Input: AI-analyzed resume data
   - Output: Enhanced resume data with skills analysis
