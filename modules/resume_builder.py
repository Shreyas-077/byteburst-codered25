import openai
from typing import Dict, List, Optional, Any
import json
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from io import BytesIO

class ATSResumeBuilder:
    def __init__(self, api_key: str):
        """Initialize the resume builder with OpenAI API key."""
        self.api_key = api_key
        openai.api_key = api_key
    
    def enhance_user_input(self, basic_input: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance basic user input with AI-generated content."""
        try:
            # Extract skills from input
            skills = []
            if isinstance(basic_input.get("skills"), dict):
                for skill_category, skill_list in basic_input["skills"].items():
                    if isinstance(skill_list, list):
                        skills.extend(skill_list)
            
            # Create professional summary
            work_exp = basic_input.get("work_experience", [])
            work_exp_str = json.dumps(work_exp) if work_exp else "No prior work experience"
            target_job = basic_input.get("target_job", {})
            
            prompt = f"""
            Create a powerful professional summary for a resume based on:
            Skills: {', '.join(skills)}
            Education: {json.dumps(basic_input.get('education', {}))}
            Experience: {work_exp_str}
            Target Job: {json.dumps(target_job)}
            
            Create a compelling 2-3 sentence summary that:
            1. Highlights key qualifications and achievements
            2. Aligns with the target role
            3. Demonstrates value proposition
            4. Uses strong action verbs
            5. Includes relevant keywords
            
            If target job is provided, tailor the summary specifically for that role.
            """

            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{
                    "role": "system",
                    "content": "You are an expert resume writer specializing in creating powerful professional summaries that get attention."
                }, {
                    "role": "user",
                    "content": prompt
                }],
                temperature=0.7
            )

            professional_summary = response.choices[0].message.content.strip()
            
            # Enhance achievements in work experience
            enhanced_experience = []
            for exp in work_exp:
                achievements = exp.get("achievements", [])
                if achievements:
                    prompt = f"""
                    Enhance these work achievements to be more impactful and quantifiable:
                    {json.dumps(achievements)}
                    
                    For each achievement:
                    1. Start with a powerful action verb
                    2. Include specific metrics and numbers
                    3. Highlight direct impact and results
                    4. Use industry-relevant keywords
                    5. Focus on contributions and value added
                    
                    Target Job: {json.dumps(target_job)}
                    
                    Return the enhanced achievements as a JSON array of strings.
                    """
                    
                    response = openai.ChatCompletion.create(
                        model="gpt-4",
                        messages=[{
                            "role": "system",
                            "content": "You are an expert in writing powerful resume achievements that demonstrate impact and value."
                        }, {
                            "role": "user",
                            "content": prompt
                        }],
                        temperature=0.7
                    )
                    
                    enhanced_achievements = json.loads(response.choices[0].message.content)
                    exp["achievements"] = enhanced_achievements
                
                enhanced_experience.append(exp)
            
            # Generate project suggestions if none provided
            projects = []
            if not basic_input.get("projects") and skills:
                prompt = f"""
                Suggest 2-3 impressive projects based on these skills and target job:
                Skills: {', '.join(skills)}
                Target Job: {json.dumps(target_job)}
                
                Each project should:
                1. Demonstrate technical expertise
                2. Show problem-solving abilities
                3. Align with career goals
                4. Include measurable outcomes
                
                Return as JSON array with format:
                [{{
                    "name": "Project Name",
                    "description": "Compelling description",
                    "technologies": ["tech1", "tech2"],
                    "highlights": ["achievement1", "achievement2"]
                }}]
                """
                
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[{
                        "role": "system",
                        "content": "You are an expert in creating impressive technical project portfolios."
                    }, {
                        "role": "user",
                        "content": prompt
                    }],
                    temperature=0.7
                )
                
                projects = json.loads(response.choices[0].message.content)
            
            # Create the enhanced content structure
            enhanced_content = {
                "contact_info": basic_input.get("contact_info", {}),
                "professional_summary": professional_summary,
                "education": basic_input.get("education", {}),
                "work_experience": enhanced_experience,
                "technical_skills": basic_input.get("skills", {}),
                "projects": projects,
                "languages": basic_input.get("languages", []),
                "certifications": basic_input.get("certifications", []),
                "additional_info": {
                    "hobbies": basic_input.get("hobbies", []),
                    "achievements": basic_input.get("achievements", [])
                }
            }
            
            return enhanced_content
            
        except Exception as e:
            print(f"Error enhancing user input: {str(e)}")
            raise Exception(f"Failed to enhance resume content: {str(e)}")

    def analyze_ats_score(self, basic_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the resume content for ATS optimization and provide a detailed score."""
        try:
            target_job = basic_info.get('target_job', {})
            job_description = target_job.get('description', '')
            
            if not job_description:
                return {
                    "overall_score": 85,  # Base score without job description
                    "section_scores": {
                        "format": 90,
                        "content": 85,
                        "skills": 80,
                        "experience": 85
                    },
                    "keyword_match": "N/A (No job description provided)",
                    "strengths": [
                        "Clear section organization",
                        "Professional formatting",
                        "Quantified achievements"
                    ],
                    "improvements": [
                        "Add a job description for better targeting",
                        "Include more industry-specific keywords"
                    ],
                    "keyword_suggestions": [
                        "Consider adding relevant industry keywords"
                    ]
                }
            
            # Analyze with OpenAI
            prompt = f"""
            Analyze this resume content against the job description for ATS optimization:
            
            Resume Content:
            {json.dumps(basic_info, indent=2)}
            
            Job Description:
            {job_description}
            
            Provide a detailed analysis in this JSON format:
            {{
                "overall_score": "percentage",
                "section_scores": {{
                    "format": "percentage",
                    "content": "percentage",
                    "skills": "percentage",
                    "experience": "percentage"
                }},
                "keyword_match": "percentage with % symbol",
                "strengths": ["list of 3-5 strong points"],
                "improvements": ["list of 2-4 suggested improvements"],
                "keyword_suggestions": ["list of 5-8 relevant keywords to add"]
            }}
            
            Focus on:
            1. Keyword matching and optimization
            2. Content relevance to the position
            3. Format compatibility with ATS systems
            4. Quantifiable achievements
            5. Technical skills alignment
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{
                    "role": "system",
                    "content": "You are an expert ATS system analyzer specializing in resume optimization."
                }, {
                    "role": "user",
                    "content": prompt
                }],
                temperature=0.7
            )
            
            analysis = json.loads(response.choices[0].message.content)
            return analysis
            
        except Exception as e:
            print(f"Error analyzing ATS score: {str(e)}")
            raise Exception(f"Failed to analyze ATS optimization: {str(e)}")

    def generate_resume_from_basic_info(self, basic_info: Dict[str, Any]) -> bytes:
        """Generate a complete resume PDF from basic user information."""
        try:
            # Enhance the basic info with AI-generated content
            enhanced_content = self.enhance_user_input(basic_info)
            
            # Create PDF
            buffer = BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            # Define styles
            styles = getSampleStyleSheet()
            styles.add(ParagraphStyle(
                name='SectionHeader',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=10,
                textColor=colors.HexColor('#2C3E50')
            ))
            styles.add(ParagraphStyle(
                name='SubHeader',
                parent=styles['Heading3'],
                fontSize=12,
                textColor=colors.HexColor('#34495E')
            ))
            styles.add(ParagraphStyle(
                name='NormalText',
                parent=styles['Normal'],
                fontSize=10,
                leading=14
            ))
            
            content = []
            
            # Header with contact information
            contact_info = enhanced_content.get("contact_info", {})
            header_text = f"""
            <para alignment="center">
            <font size="16" color="#1A237E"><b>{contact_info.get('name', '')}</b></font><br/>
            {contact_info.get('email', '')} | {contact_info.get('phone', '')} | {contact_info.get('location', '')}<br/>
            """
            if contact_info.get('linkedin'):
                header_text += f"LinkedIn: {contact_info['linkedin']} | "
            if contact_info.get('github'):
                header_text += f"GitHub: {contact_info['github']}"
            header_text += "</para>"
            content.append(Paragraph(header_text, styles['Normal']))
            content.append(Spacer(1, 12))
            
            # Professional Summary
            if enhanced_content.get("professional_summary"):
                content.append(Paragraph("PROFESSIONAL SUMMARY", styles['SectionHeader']))
                content.append(Paragraph(enhanced_content["professional_summary"], styles['NormalText']))
                content.append(Spacer(1, 12))
            
            # Technical Skills
            if enhanced_content.get("technical_skills"):
                content.append(Paragraph("TECHNICAL SKILLS", styles['SectionHeader']))
                skills = enhanced_content["technical_skills"]
                skills_text = ""
                for category, skill_list in skills.items():
                    if skill_list:
                        skills_text += f"<b>{category}:</b> {', '.join(skill_list)}<br/>"
                content.append(Paragraph(skills_text, styles['NormalText']))
                content.append(Spacer(1, 12))
            
            # Work Experience
            if enhanced_content.get("work_experience"):
                content.append(Paragraph("PROFESSIONAL EXPERIENCE", styles['SectionHeader']))
                for exp in enhanced_content["work_experience"]:
                    exp_header = f"<b>{exp.get('title', '')}</b> - {exp.get('company', '')}"
                    content.append(Paragraph(exp_header, styles['SubHeader']))
                    content.append(Paragraph(f"<i>{exp.get('duration', '')}</i>", styles['NormalText']))
                    if exp.get("achievements"):
                        achievements_text = ""
                        for achievement in exp["achievements"]:
                            achievements_text += f"• {achievement}<br/>"
                        content.append(Paragraph(achievements_text, styles['NormalText']))
                    content.append(Spacer(1, 8))
                content.append(Spacer(1, 4))
            
            # Education
            if enhanced_content.get("education"):
                content.append(Paragraph("EDUCATION", styles['SectionHeader']))
                edu = enhanced_content["education"]
                edu_text = f"<b>{edu.get('degree', '')}</b><br/>"
                edu_text += f"{edu.get('university', '')}<br/>"
                if edu.get("duration"):
                    edu_text += f"{edu.get('duration', '')}"
                if edu.get("gpa"):
                    edu_text += f" | GPA: {edu.get('gpa', '')}"
                content.append(Paragraph(edu_text, styles['NormalText']))
                content.append(Spacer(1, 12))
            
            # Projects
            if enhanced_content.get("projects"):
                content.append(Paragraph("TECHNICAL PROJECTS", styles['SectionHeader']))
                for project in enhanced_content["projects"]:
                    project_header = f"<b>{project.get('name', '')}</b>"
                    content.append(Paragraph(project_header, styles['SubHeader']))
                    content.append(Paragraph(project.get('description', ''), styles['NormalText']))
                    if project.get('technologies'):
                        tech_text = f"<b>Technologies:</b> {', '.join(project['technologies'])}"
                        content.append(Paragraph(tech_text, styles['NormalText']))
                    if project.get('highlights'):
                        highlights_text = ""
                        for highlight in project['highlights']:
                            highlights_text += f"• {highlight}<br/>"
                        content.append(Paragraph(highlights_text, styles['NormalText']))
                    content.append(Spacer(1, 8))
                content.append(Spacer(1, 4))
            
            # Certifications
            if enhanced_content.get("certifications"):
                content.append(Paragraph("CERTIFICATIONS", styles['SectionHeader']))
                cert_text = ""
                for cert in enhanced_content["certifications"]:
                    cert_text += f"• {cert}<br/>"
                content.append(Paragraph(cert_text, styles['NormalText']))
                content.append(Spacer(1, 12))
            
            # Languages
            if enhanced_content.get("languages"):
                content.append(Paragraph("LANGUAGES", styles['SectionHeader']))
                lang_text = ""
                for lang in enhanced_content["languages"]:
                    lang_text += f"• {lang}<br/>"
                content.append(Paragraph(lang_text, styles['NormalText']))
                content.append(Spacer(1, 12))
            
            # Additional Information
            if enhanced_content.get("additional_info"):
                content.append(Paragraph("ADDITIONAL INFORMATION", styles['SectionHeader']))
                additional_text = ""
                if enhanced_content["additional_info"].get("hobbies"):
                    additional_text += f"<b>Interests & Hobbies:</b> {', '.join(enhanced_content['additional_info']['hobbies'])}<br/>"
                if enhanced_content["additional_info"].get("achievements"):
                    additional_text += "<b>Achievements:</b><br/>"
                    for achievement in enhanced_content["additional_info"]["achievements"]:
                        additional_text += f"• {achievement}<br/>"
                content.append(Paragraph(additional_text, styles['NormalText']))
            
            # Build the PDF
            doc.build(content)
            
            # Get the value of the BytesIO buffer
            pdf = buffer.getvalue()
            buffer.close()
            
            return pdf
            
        except Exception as e:
            print(f"Error generating resume PDF: {str(e)}")
            raise e
