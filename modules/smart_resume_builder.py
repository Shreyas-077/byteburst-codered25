import openai
from typing import Dict, List, Optional
import json
import os
from datetime import datetime
from .resume_builder import ATSResumeBuilder
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO

class SmartResumeBuilder(ATSResumeBuilder):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.resume_versions = {}
        self.templates = {
            "modern": {
                "font": "Helvetica",
                "colors": {"primary": "#2c3e50", "secondary": "#3498db"},
                "layout": "single-column"
            },
            "professional": {
                "font": "Times New Roman",
                "colors": {"primary": "#333333", "secondary": "#666666"},
                "layout": "two-column"
            },
            "creative": {
                "font": "Roboto",
                "colors": {"primary": "#1a237e", "secondary": "#0d47a1"},
                "layout": "modular"
            }
        }

    def quantify_achievements(self, achievements: List[str]) -> List[str]:
        """
        Use AI to quantify achievements with metrics and numbers.
        """
        try:
            prompt = f"""
            Transform these achievements into quantified, metric-driven statements:
            {json.dumps(achievements)}
            
            Follow these rules:
            1. Add specific numbers and percentages
            2. Include time frames
            3. Add business impact
            4. Use measurable metrics
            5. Keep the tone professional
            
            Return the response as a JSON array of strings.
            """

            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{
                    "role": "system",
                    "content": "You are an expert at quantifying professional achievements with specific metrics and numbers."
                }, {
                    "role": "user",
                    "content": prompt
                }],
                temperature=0.7
            )

            quantified = json.loads(response.choices[0].message.content)
            return quantified
        except Exception as e:
            print(f"Error quantifying achievements: {str(e)}")
            return achievements

    def create_role_version(self, base_resume: Dict, target_role: str, job_description: str) -> Dict:
        """
        Create a tailored version of the resume for a specific role.
        """
        try:
            prompt = f"""
            Customize this resume for a {target_role} position.
            
            Resume Content:
            {json.dumps(base_resume)}
            
            Job Description:
            {job_description}
            
            Follow these rules:
            1. Highlight relevant experience
            2. Use role-specific keywords
            3. Prioritize relevant skills
            4. Adapt achievements to match role
            5. Maintain authenticity
            
            Return the response in the same JSON format as the input resume.
            """

            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{
                    "role": "system",
                    "content": "You are an expert at customizing resumes for specific roles while maintaining authenticity."
                }, {
                    "role": "user",
                    "content": prompt
                }],
                temperature=0.7
            )

            tailored_resume = json.loads(response.choices[0].message.content)
            version_id = f"{target_role}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.resume_versions[version_id] = tailored_resume
            return tailored_resume
        except Exception as e:
            print(f"Error creating role version: {str(e)}")
            return base_resume

    def analyze_competition(self, resume: Dict, job_description: str, num_samples: int = 3) -> Dict:
        """
        Analyze resume against competitive samples for the role.
        """
        try:
            prompt = f"""
            Generate {num_samples} competitive resume samples for this job description,
            then analyze how the given resume compares to them.
            
            Job Description:
            {job_description}
            
            Resume to Compare:
            {json.dumps(resume)}
            
            Provide analysis in this JSON format:
            {{
                "competitive_analysis": {{
                    "strengths": ["string"],
                    "gaps": ["string"],
                    "recommendations": ["string"]
                }},
                "market_position": "string",
                "improvement_areas": ["string"],
                "unique_selling_points": ["string"]
            }}
            """

            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{
                    "role": "system",
                    "content": "You are an expert at competitive resume analysis and market positioning."
                }, {
                    "role": "user",
                    "content": prompt
                }],
                temperature=0.7
            )

            analysis = json.loads(response.choices[0].message.content)
            return analysis
        except Exception as e:
            print(f"Error analyzing competition: {str(e)}")
            return {
                "error": "Could not complete competitive analysis",
                "message": str(e)
            }

    def predict_ats_score(self, resume: Dict, job_description: str) -> Dict:
        """
        Predict ATS score and provide optimization recommendations.
        """
        try:
            # Extract text from resume
            resume_text = self._convert_resume_to_text(resume)
            
            # Calculate keyword matching
            vectorizer = TfidfVectorizer(stop_words='english')
            tfidf_matrix = vectorizer.fit_transform([resume_text, job_description])
            similarity_score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]

            # Get detailed analysis from GPT
            prompt = f"""
            Analyze this resume for ATS optimization:
            
            Resume:
            {resume_text}
            
            Job Description:
            {job_description}
            
            Provide analysis in this JSON format:
            {{
                "ats_score": float,
                "keyword_match_rate": float,
                "missing_keywords": ["string"],
                "format_issues": ["string"],
                "optimization_tips": ["string"],
                "section_scores": {{
                    "professional_summary": float,
                    "work_experience": float,
                    "skills": float,
                    "education": float
                }}
            }}
            """

            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{
                    "role": "system",
                    "content": "You are an expert at ATS optimization and resume scoring."
                }, {
                    "role": "user",
                    "content": prompt
                }],
                temperature=0.7
            )

            ats_analysis = json.loads(response.choices[0].message.content)
            
            # Combine ML score with GPT analysis
            ats_analysis["similarity_score"] = float(similarity_score)
            return ats_analysis
        except Exception as e:
            print(f"Error predicting ATS score: {str(e)}")
            return {
                "error": "Could not complete ATS analysis",
                "message": str(e)
            }

    def _convert_resume_to_text(self, resume: Dict) -> str:
        """
        Convert resume dictionary to plain text for analysis.
        """
        sections = []
        
        # Add contact info
        if "contact_info" in resume:
            contact = resume["contact_info"]
            sections.append(f"{contact.get('name', '')}")
            sections.append(f"{contact.get('email', '')} | {contact.get('phone', '')} | {contact.get('location', '')}")
            sections.append(f"LinkedIn: {contact.get('linkedin', '')}")

        # Add professional summary
        if "professional_summary" in resume:
            sections.append(resume["professional_summary"])

        # Add work experience
        if "work_experience" in resume:
            for exp in resume["work_experience"]:
                sections.append(f"{exp.get('title', '')} at {exp.get('company', '')}")
                sections.append(exp.get('duration', ''))
                sections.extend(exp.get('achievements', []))

        # Add education
        if "education" in resume:
            for edu in resume["education"]:
                sections.append(f"{edu.get('degree', '')} from {edu.get('school', '')}")
                sections.append(edu.get('duration', ''))
                sections.extend(edu.get('details', []))

        # Add skills and certifications
        if "skills" in resume:
            sections.extend(resume["skills"])
        if "certifications" in resume:
            sections.extend(resume["certifications"])

        return "\n".join(sections)

    def generate_pdf(self, resume_content: Dict, template_name: str = "modern") -> bytes:
        """
        Generate a PDF version of the resume using the specified template.
        """
        try:
            # Create a BytesIO buffer for the PDF
            buffer = BytesIO()
            
            # Create the PDF document
            doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
            
            # Get template settings
            template = self.templates.get(template_name, self.templates["modern"])
            
            # Create styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Title'],
                fontSize=24,
                spaceAfter=30,
                textColor=colors.HexColor(template["colors"]["primary"])
            )
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=12,
                textColor=colors.HexColor(template["colors"]["primary"])
            )
            normal_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontSize=12,
                spaceAfter=6
            )
            
            # Build the document content
            story = []
            
            # Add contact information
            contact_info = resume_content.get("contact_info", {})
            name = contact_info.get("name", "")
            story.append(Paragraph(name, title_style))
            
            contact_details = [
                f"{contact_info.get('email', '')}",
                f"{contact_info.get('phone', '')}",
                f"{contact_info.get('location', '')}"
            ]
            story.append(Paragraph(" | ".join(filter(None, contact_details)), normal_style))
            story.append(Spacer(1, 20))
            
            # Add work experience
            story.append(Paragraph("Professional Experience", heading_style))
            for exp in resume_content.get("work_experience", []):
                for achievement in exp.get("achievements", []):
                    story.append(Paragraph(f"• {achievement}", normal_style))
            story.append(Spacer(1, 20))
            
            # Add education
            if resume_content.get("education"):
                story.append(Paragraph("Education", heading_style))
                story.append(Paragraph(resume_content["education"], normal_style))
                story.append(Spacer(1, 20))
            
            # Add skills
            if resume_content.get("skills"):
                story.append(Paragraph("Skills", heading_style))
                skills_text = ", ".join(resume_content["skills"])
                story.append(Paragraph(skills_text, normal_style))
                story.append(Spacer(1, 20))
            
            # Add certifications
            if resume_content.get("certifications"):
                story.append(Paragraph("Certifications", heading_style))
                for cert in resume_content["certifications"]:
                    if cert.strip():
                        story.append(Paragraph(f"• {cert}", normal_style))
            
            # Build the PDF
            doc.build(story)
            
            # Get the value from the buffer
            pdf_content = buffer.getvalue()
            buffer.close()
            
            return pdf_content
        except Exception as e:
            print(f"Error generating PDF: {str(e)}")
            raise
