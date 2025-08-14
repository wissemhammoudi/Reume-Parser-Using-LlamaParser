import os
import json
import logging
from typing import Dict, Any, List, Optional
from groq import Groq
from deep_translator import GoogleTranslator

from app.config.settings import settings

logger = logging.getLogger(__name__)

class AIService:
    """Service for AI-powered resume analysis using Groq."""
    
    def __init__(self):
        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is required but not set")
        
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.translator = GoogleTranslator(source='auto', target='en')
    
    async def analyze_resume(self, text_content: str, images_data: List[str] = None) -> Dict[str, Any]:
        """
        Analyze resume content using AI.
        
        Args:
            text_content: Extracted text from PDF
            images_data: List of image paths (optional)
            
        Returns:
            AI-analyzed resume data
        """
        try:
            logger.info("Starting AI analysis of resume")
            
            translated_text = await self._translate_text(text_content)
            
            prompt = self._create_analysis_prompt(translated_text, images_data)
            
            ai_response = await self._get_ai_analysis(prompt)
            
            structured_data = await self._parse_ai_response(ai_response)
            
            logger.info("AI analysis completed successfully")
            return structured_data
            
        except Exception as e:
            logger.error(f"AI analysis failed: {str(e)}")
            raise
    
    def _create_analysis_prompt(self, text_content: str, images_data: List[str] = None) -> str:
        """Create the prompt for AI analysis."""
        base_prompt = """
        Analyze the following resume and extract structured information. 
        Return the result as a valid JSON object with the following structure:
        
        {
            "personal_info": {
                "name": "Full Name",
                "email": "Email Address",
                "phone": "Phone Number",
                "location": "City, Country",
                "linkedin": "LinkedIn URL (if available)"
            },
            "summary": "Professional summary or objective",
            "experience": [
                {
                    "title": "Job Title",
                    "company": "Company Name",
                    "duration": "Duration",
                    "description": "Job description and achievements"
                }
            ],
            "education": [
                {
                    "degree": "Degree Name",
                    "institution": "Institution Name",
                    "year": "Graduation Year",
                    "gpa": "GPA if mentioned"
                }
            ],
            "skills": [
                {
                    "category": "Skill Category (e.g., Programming, Tools, Languages)",
                    "skills": ["Skill 1", "Skill 2", "Skill 3"]
                }
            ],
            "certifications": ["Certification 1", "Certification 2"],
            "languages": ["Language 1", "Language 2"],
            "projects": [
                {
                    "name": "Project Name",
                    "description": "Project description",
                    "technologies": ["Tech 1", "Tech 2"],
                    "url": "Project URL if available"
                }
            ]
        }
        
        Resume Content:
        {text_content}
        
        If any field is not found in the resume, set it to null or empty array as appropriate.
        Ensure the response is valid JSON.
        """
        
        if images_data:
            base_prompt += f"\n\nImages found: {len(images_data)} images were extracted from the PDF."
        
        return base_prompt.format(text_content=text_content[:4000])  # Limit text length
    
    async def _get_ai_analysis(self, prompt: str) -> str:
        """Get analysis from Groq AI."""
        try:
            messages = [
                {"role": "system", "content": "You are an expert resume parser. Extract structured information from resumes."},
                {"role": "user", "content": prompt}
            ]
            
            completion = self.client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=messages,
                temperature=settings.GROQ_TEMPERATURE,
                max_tokens=settings.GROQ_MAX_TOKENS,
                top_p=0,
                stream=False,
                stop=None,
            )
            
            return completion.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Groq API call failed: {str(e)}")
            raise
    
    async def _parse_ai_response(self, ai_response: str) -> Dict[str, Any]:
        """Parse and validate AI response."""
        try:
            cleaned_response = self._clean_json_response(ai_response)
            
            parsed_data = json.loads(cleaned_response)
            
            validated_data = self._validate_resume_structure(parsed_data)
            
            return validated_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {str(e)}")
            return self._get_fallback_structure()
        except Exception as e:
            logger.error(f"Response parsing failed: {str(e)}")
            raise
    
    def _clean_json_response(self, response: str) -> str:
        """Clean and extract JSON from AI response."""
        try:
            start_index = response.find('{')
            end_index = response.rfind('}') + 1
            
            if start_index != -1 and end_index != -1:
                return response[start_index:end_index].strip()
            else:
                raise ValueError("No JSON content found in response")
                
        except Exception as e:
            logger.error(f"JSON cleaning failed: {str(e)}")
            raise
    
    def _validate_resume_structure(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and ensure resume data structure."""
        required_fields = ["personal_info", "experience", "education", "skills"]
        
        for field in required_fields:
            if field not in data:
                data[field] = {} if field == "personal_info" else []
        
        return data
    
    def _get_fallback_structure(self) -> Dict[str, Any]:
        """Return fallback structure if parsing fails."""
        return {
            "personal_info": {},
            "summary": "",
            "experience": [],
            "education": [],
            "skills": [],
            "certifications": [],
            "languages": [],
            "projects": [],
            "parsing_error": "AI parsing failed, using fallback structure"
        }
    
    async def _translate_text(self, text: str) -> str:
        """Translate text to English if needed."""
        try:
            if len(text) > 100:  
                translated = self.translator.translate(text[:1000])  
                return translated
            return text
        except Exception as e:
            logger.warning(f"Translation failed: {str(e)}, using original text")
            return text
    
    async def health_check(self) -> Dict[str, Any]:
        """Check AI service health."""
        try:
            test_messages = [{"role": "user", "content": "Hello"}]
            response = self.client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=test_messages,
                max_tokens=10
            )
            
            return {
                "healthy": True,
                "message": "AI service is operational",
                "model": settings.GROQ_MODEL,
                "api_status": "connected"
            }
        except Exception as e:
            return {
                "healthy": False,
                "message": f"AI service error: {str(e)}",
                "model": settings.GROQ_MODEL,
                "api_status": "disconnected"
            }
