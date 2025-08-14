# Resume Parser API

Extract structured information from PDF resumes using advanced AI analysis, computer vision, and intelligent skills mapping. Perfect for HR systems, recruitment platforms, and talent management applications.

##  Features

- **AI-Powered Extraction**: Uses Groq AI to intelligently parse resume content
- **Computer Vision**: Analyzes images and visual elements in resumes
- **Skills Intelligence**: Maps skills to experience periods and job contexts
- **Multi-language Support**: Automatically translates non-English resumes
- **Structured Output**: Clean, consistent JSON data for easy integration
- **Real-time Processing**: Fast analysis with comprehensive error handling

##  Quick Start

### Prerequisites
- Docker and Docker Compose
- Groq API key ([Get one here](https://console.groq.com/))
- LlamaParse API key ([Get one here](https://cloud.llamaindex.ai/))

### 1. Setup Environment
```bash
# Clone the repository
git clone https://github.com/wissemhammoudi/RH-chabot-using-RAG-Fusion
cd Reume-Parser-Using-LlamaParser

# Create environment file
cat > backend/app/.env << EOF
GROQ_API_KEY=your_groq_api_key_here
LLAMA_PARSE_API_KEY=your_llamaparse_api_key_here
EOF
```

### 2. Start Services
```bash
# Start all services
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

### 4. Access the Application
- **Frontend**: http://localhost:3000
- **API**: http://localhost:80
- **Interactive API Docs**: http://localhost:80/docs

### 5. Documentation
- **[API Documentation](./API_DOCUMENTATION.md)** - Complete API reference and usage examples
- **[Services Documentation](./SERVICES_DOCUMENTATION.md)** - Backend services architecture and configuration
- **[Interactive API Docs](http://localhost:80/docs)** - Swagger UI for testing endpoints

##  What You Get

### Extracted Data
```json
{
  "personal_info": {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1-555-0123",
    "location": "New York, USA"
  },
  "experience": [
    {
      "title": "Senior Software Engineer",
      "company": "Tech Corp",
      "duration": "2020 - Present",
      "period_months": 36
    }
  ],
  "skills": [
    {
      "category": "Programming",
      "skills": ["Python", "JavaScript"],
      "experience_months": 48
    }
  ]
}
```

### Enhanced Skills Analysis
- **Experience Mapping**: Links skills to job contexts
- **Duration Calculation**: Total months of experience per skill
- **Skills Categorization**: Organized by type and context
- **Context Awareness**: Which companies and roles used each skill

## Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Frontend  │───▶│   Backend   │───▶│  AI + CV    │
│   (React)   │    │  (FastAPI)  │    │  Services   │
└─────────────┘    └─────────────┘    └─────────────┘
                           │
                    ┌─────────────┐
                    │ PostgreSQL  │
                    │   Storage   │
                    └─────────────┘
```

##  Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Backend** | FastAPI | High-performance API framework |
| **AI Analysis** | Groq (Llama3) | Intelligent text parsing |
| **PDF Processing** | PyMuPDF | Text and image extraction |
| **Computer Vision** | OpenCV + MobileNetSSD | Image analysis |
| **Frontend** | React | User interface |
| **Containerization** | Docker | Easy deployment |

##  Project Structure

```
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── config/         # Configuration management
│   │   ├── services/       # Business logic
│   │   ├── routers/        # API endpoints
│   │   ├── models/         # Data validation
│   │   └── utils/          # Helper functions
│   ├── models/             # ML model files
│   └── requirements.txt    # Python dependencies
├── frontend/               # React application
├── docker-compose.yml      # Service orchestration
├── README.md              # This file
├── API_DOCUMENTATION.md    # Complete API reference
└── SERVICES_DOCUMENTATION.md # Backend services guide
```
