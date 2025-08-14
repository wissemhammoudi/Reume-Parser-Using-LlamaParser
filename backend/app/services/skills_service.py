import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class SkillsService:
    """Service for processing and enhancing skills information."""
    
    def __init__(self):
        self.skill_categories = [
            "Programming Languages", "Frameworks", "Databases", 
            "Cloud Platforms", "Tools", "Methodologies", "Languages"
        ]
    
    async def enhance_skills(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance and process skills information from resume data.
        
        Args:
            resume_data: Raw resume data from AI analysis
            
        Returns:
            Enhanced resume data with processed skills
        """
        try:
            logger.info("Starting skills enhancement")
            
            if "experience" in resume_data:
                resume_data["experience"] = self._add_period_fields(resume_data["experience"])
            
            if "skills" in resume_data:
                resume_data["skills"] = self._format_skills(resume_data["skills"])
            
            skills_periods = self._extract_skills_periods(resume_data)
            
            summed_skills = self._sum_skills_periods(skills_periods, threshold=0.8)
            
            enhanced_data = self._update_existing_skills(summed_skills, resume_data)
            
            logger.info("Skills enhancement completed")
            return enhanced_data
            
        except Exception as e:
            logger.error(f"Skills enhancement failed: {str(e)}")
            return resume_data
    
    def _add_period_fields(self, experience_list: List[Dict]) -> List[Dict]:
        """Add period fields to experience entries."""
        enhanced_experience = []
        
        for exp in experience_list:
            enhanced_exp = exp.copy()
            
            duration = exp.get("duration", "")
            if duration:
                start_date, end_date = self._parse_duration(duration)
                enhanced_exp["start_date"] = start_date
                enhanced_exp["end_date"] = end_date
                enhanced_exp["period_months"] = self._calculate_period_months(start_date, end_date)
            
            enhanced_experience.append(enhanced_exp)
        
        return enhanced_experience
    
    def _parse_duration(self, duration: str) -> tuple:
        """Parse duration string to extract start and end dates."""
        try:
            if " - " in duration:
                parts = duration.split(" - ")
                start_str = parts[0].strip()
                end_str = parts[1].strip()
                
                start_date = self._parse_date(start_str)
                end_date = self._parse_date(end_str)
                
                return start_date, end_date
            
            elif " to " in duration:
                parts = duration.split(" to ")
                start_str = parts[0].strip()
                end_str = parts[1].strip()
                
                start_date = self._parse_date(start_str)
                end_date = self._parse_date(end_str)
                
                return start_date, end_date
            
            else:
                start_date = self._parse_date(duration)
                end_date = datetime.now() if "present" in duration.lower() else None
                
                return start_date, end_date
                
        except Exception as e:
            logger.warning(f"Failed to parse duration '{duration}': {str(e)}")
            return None, None
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string to datetime object."""
        try:
            date_str = date_str.lower().strip()
            
            if "present" in date_str or "current" in date_str:
                return datetime.now()
            
            date_formats = [
                "%B %Y",      
                "%b %Y",      
                "%Y",         
                "%m/%Y",      
                "%Y-%m",      
            ]
            
            for fmt in date_formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            
            return None
            
        except Exception as e:
            logger.warning(f"Failed to parse date '{date_str}': {str(e)}")
            return None
    
    def _calculate_period_months(self, start_date: datetime, end_date: datetime) -> Optional[int]:
        """Calculate the period in months between two dates."""
        try:
            if not start_date or not end_date:
                return None
            
            if end_date > start_date:
                delta = end_date - start_date
                months = delta.days / 30.44  
                return int(months)
            else:
                return 0
                
        except Exception as e:
            logger.warning(f"Failed to calculate period: {str(e)}")
            return None
    
    def _format_skills(self, skills_data: List[Dict]) -> List[Dict]:
        """Format and categorize skills."""
        formatted_skills = []
        
        for skill_group in skills_data:
            if isinstance(skill_group, dict) and "skills" in skill_group:
                formatted_group = {
                    "category": skill_group.get("category", "Other"),
                    "skills": skill_group["skills"],
                    "count": len(skill_group["skills"])
                }
                formatted_skills.append(formatted_group)
        
        return formatted_skills
    
    def _extract_skills_periods(self, resume_data: Dict[str, Any]) -> List[Dict]:
        """Extract skills with their usage periods from experience."""
        skills_periods = []
        
        if "experience" not in resume_data:
            return skills_periods
        
        for exp in resume_data["experience"]:
            if "description" in exp:
                mentioned_skills = self._extract_skills_from_text(exp["description"])
                
                for skill in mentioned_skills:
                    skill_period = {
                        "skill": skill,
                        "start_date": exp.get("start_date"),
                        "end_date": exp.get("end_date"),
                        "period_months": exp.get("period_months"),
                        "context": exp.get("title", ""),
                        "company": exp.get("company", "")
                    }
                    skills_periods.append(skill_period)
        
        return skills_periods
    
    def _extract_skills_from_text(self, text: str) -> List[str]:
        """Extract skill mentions from text."""
        
        common_skills = [
            "Python", "Java", "JavaScript", "React", "Node.js", "SQL", "MongoDB",
            "AWS", "Docker", "Kubernetes", "Git", "Agile", "Scrum", "Machine Learning",
            "Data Analysis", "Project Management", "Leadership", "Communication"
        ]
        
        found_skills = []
        text_lower = text.lower()
        
        for skill in common_skills:
            if skill.lower() in text_lower:
                found_skills.append(skill)
        
        return found_skills
    
    def _sum_skills_periods(self, skills_periods: List[Dict], threshold: float = 0.8) -> List[Dict]:
        """Sum up skills periods to get total experience."""
        skills_summary = {}
        
        for skill_period in skills_periods:
            skill_name = skill_period["skill"]
            period_months = skill_period.get("period_months", 0) or 0
            
            if skill_name not in skills_summary:
                skills_summary[skill_name] = {
                    "skill": skill_name,
                    "total_months": 0,
                    "contexts": [],
                    "companies": []
                }
            
            skills_summary[skill_name]["total_months"] += period_months
            
            if skill_period.get("context"):
                skills_summary[skill_name]["contexts"].append(skill_period["context"])
            
            if skill_period.get("company"):
                skills_summary[skill_name]["companies"].append(skill_period["company"])
        
        result = []
        for skill_data in skills_summary.values():
            if skill_data["total_months"] >= threshold:
                result.append(skill_data)
        
        return result
    
    def _update_existing_skills(self, summed_skills: List[Dict], resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update resume data with enhanced skills information."""
        enhanced_data = resume_data.copy()
        
        enhanced_data["enhanced_skills"] = {
            "skills_with_experience": summed_skills,
            "total_skills": len(summed_skills),
            "analysis_timestamp": datetime.now().isoformat()
        }
        
        if "skills" in enhanced_data:
            for skill_group in enhanced_data["skills"]:
                if "skills" in skill_group:
                    for skill in skill_group["skills"]:
                        for enhanced_skill in summed_skills:
                            if skill.lower() == enhanced_skill["skill"].lower():
                                skill_group["experience_months"] = enhanced_skill["total_months"]
                                skill_group["contexts"] = enhanced_skill["contexts"]
                                break
        
        return enhanced_data
    
    async def health_check(self) -> Dict[str, Any]:
        """Check skills service health."""
        try:    
            test_data = {"skills": [{"category": "Test", "skills": ["Python", "Java"]}]}
            formatted = self._format_skills(test_data)
            
            return {
                "healthy": True,
                "message": "Skills service is operational",
                "skill_categories": len(self.skill_categories),
                "test_passed": len(formatted) > 0
            }
            
        except Exception as e:
            return {
                "healthy": False,
                "message": f"Skills service error: {str(e)}"
            }
