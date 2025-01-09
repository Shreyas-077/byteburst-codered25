import openai
import re
from typing import Dict, List, Optional
import json

def calculate_ats_compatibility(resume_text: str, job_description: str) -> Dict:
    """
    Calculate ATS compatibility score and identify keyword matches.
    """
    try:
        prompt = f"""
        Analyze this resume against the job description for ATS compatibility.
        
        Resume: {resume_text}
        Job Description: {job_description}
        
        Return a JSON object with:
        - score (number): 0-100 ATS compatibility score
        - matched_keywords (array): Keywords found in both resume and job description
        - missing_keywords (array): Important keywords from job description missing in resume
        
        Example:
        {{
            "score": 85,
            "matched_keywords": ["Python", "Machine Learning"],
            "missing_keywords": ["Docker", "Kubernetes"]
        }}
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are an ATS expert. Always respond with valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.5
        )
        
        content = response.choices[0].message.content.strip()
        content = content.replace("```json", "").replace("```", "").strip()
        return json.loads(content)
    except Exception as e:
        print(f"Error calculating ATS compatibility: {str(e)}")
        return {
            "score": 70,
            "matched_keywords": ["Unable to analyze keywords"],
            "missing_keywords": []
        }

def analyze_technical_skills(resume_text: str, job_description: Optional[str] = None) -> Dict:
    """
    Analyze technical skills from resume and provide detailed assessment.
    """
    try:
        prompt = f"""
        Analyze the technical skills in this resume.
        
        Resume: {resume_text}
        Job Description: {job_description if job_description else "Not provided"}
        
        Return a JSON object with these categories:
        - programming_languages: Dictionary of languages with proficiency (as integer 0-100), experience, and related projects
        - frameworks: Dictionary of frameworks/tools with same details
        - soft_skills: Dictionary of soft skills with proficiency and evidence
        - domain_knowledge: Dictionary of domain expertise with proficiency and applications
        
        Example:
        {{
            "programming_languages": {{
                "Python": {{
                    "proficiency": 85,
                    "experience": "3+ years",
                    "projects": ["ML Pipeline", "Data Analysis Tool"]
                }}
            }},
            "frameworks": {{
                "React": {{
                    "proficiency": 75,
                    "experience": "2 years",
                    "projects": ["E-commerce UI", "Dashboard"]
                }}
            }},
            "soft_skills": {{
                "Leadership": {{
                    "proficiency": 90,
                    "experience": "Team Lead for 2 years",
                    "projects": ["Led 5-person team", "Mentored juniors"]
                }}
            }},
            "domain_knowledge": {{
                "Machine Learning": {{
                    "proficiency": 80,
                    "experience": "3 years",
                    "projects": ["Predictive Analytics", "NLP Models"]
                }}
            }}
        }}
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are a technical skills analyst. Always respond with valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.5
        )
        
        content = response.choices[0].message.content.strip()
        content = content.replace("```json", "").replace("```", "").strip()
        return json.loads(content)
    except Exception as e:
        print(f"Error analyzing technical skills: {str(e)}")
        return {
            "programming_languages": {},
            "frameworks": {},
            "soft_skills": {},
            "domain_knowledge": {}
        }

def analyze_skill_gaps(tech_analysis: Dict, job_description: str) -> Dict:
    """
    Analyze skill gaps between resume and job requirements.
    """
    try:
        # Convert tech_analysis to a simpler format for the prompt
        skills_summary = {
            "programming_languages": list(tech_analysis['programming_languages'].keys()),
            "frameworks": list(tech_analysis['frameworks'].keys()),
            "soft_skills": list(tech_analysis['soft_skills'].keys()),
            "domain_knowledge": list(tech_analysis['domain_knowledge'].keys())
        }
        
        prompt = f"""
        Analyze the skill gaps between the candidate's skills and job requirements.
        
        Candidate Skills: {json.dumps(skills_summary)}
        Job Description: {job_description}
        
        Return a JSON object with:
        - strong_matches: Array of skills that strongly match job requirements
        - gaps: Dictionary of missing skills with importance level (high/medium/low)
        - learning_resources: Dictionary of skills with array of learning resources
        
        Example:
        {{
            "strong_matches": ["Python", "Machine Learning"],
            "gaps": {{
                "Docker": "high",
                "AWS": "medium"
            }},
            "learning_resources": {{
                "Docker": [
                    "Docker Official Documentation",
                    "Docker for Beginners Course on Udemy"
                ]
            }}
        }}
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are a career development expert. Always respond with valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.5
        )
        
        content = response.choices[0].message.content.strip()
        content = content.replace("```json", "").replace("```", "").strip()
        return json.loads(content)
    except Exception as e:
        print(f"Error analyzing skill gaps: {str(e)}")
        return {
            "strong_matches": [],
            "gaps": {},
            "learning_resources": {}
        }

def analyze_industry_trends(domains: List[str]) -> List[Dict]:
    """
    Analyze industry trends related to the candidate's domain knowledge.
    """
    try:
        prompt = f"""
        Analyze current industry trends related to these domains: {', '.join(domains)}
        
        Return a JSON array of trend objects with:
        - name: Trend name
        - impact: Impact description
        - adoption_rate: Current adoption rate
        - required_skills: Array of skills needed
        
        Example:
        [
            {{
                "name": "Edge Computing in AI",
                "impact": "High impact on real-time processing",
                "adoption_rate": "Growing rapidly, 45% adoption",
                "required_skills": ["TensorFlow Lite", "Edge ML"]
            }}
        ]
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are an industry trends analyst. Always respond with valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.5
        )
        
        content = response.choices[0].message.content.strip()
        content = content.replace("```json", "").replace("```", "").strip()
        return json.loads(content)
    except Exception as e:
        print(f"Error analyzing industry trends: {str(e)}")
        return [
            {
                "name": "Unable to analyze trends",
                "impact": "N/A",
                "adoption_rate": "N/A",
                "required_skills": []
            }
        ]
