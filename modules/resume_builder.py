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
        """
        Analyze the resume content and provide an ATS compatibility score and suggestions.
        """
        # Initialize scores dictionary
        scores = {
            'Keywords': 0,
            'Format': 0,
            'Content': 0,
            'Skills': 0
        }
        
        strengths = []
        improvements = []
        keyword_suggestions = []
        
        # Analyze Keywords and Skills
        tech_skills = basic_info.get('technical_skills', {})
        if tech_skills:
            skill_count = sum(len(skills) for skills in tech_skills.values())
            if skill_count >= 10:
                scores['Skills'] = 90
                strengths.append("Strong technical skills section with diverse technologies")
            elif skill_count >= 5:
                scores['Skills'] = 70
                improvements.append("Consider adding more relevant technical skills")
            else:
                scores['Skills'] = 50
                improvements.append("Technical skills section needs significant enhancement")
        
        # Analyze Content
        work_exp = basic_info.get('work_experience', [])
        if work_exp:
            achievement_count = sum(len(exp.get('achievements', [])) for exp in work_exp)
            if achievement_count >= 10:
                scores['Content'] = 90
                strengths.append("Rich work experience with quantifiable achievements")
            elif achievement_count >= 5:
                scores['Content'] = 70
                improvements.append("Add more quantifiable achievements to work experience")
            else:
                scores['Content'] = 50
                improvements.append("Work experience needs more detailed achievements")
        
        # Analyze Format
        if basic_info.get('professional_summary'):
            scores['Format'] = 90
            strengths.append("Professional summary provides a strong introduction")
        else:
            scores['Format'] = 60
            improvements.append("Add a compelling professional summary")
        
        # Common ATS Keywords Analysis
        common_keywords = [
            'developed', 'implemented', 'managed', 'led', 'created',
            'designed', 'improved', 'increased', 'reduced', 'optimized',
            'collaborated', 'team', 'project', 'analysis', 'solution',
            'strategy', 'results', 'achievement', 'success', 'innovation'
        ]
        
        content_text = str(basic_info).lower()
        keyword_count = sum(1 for keyword in common_keywords if keyword in content_text)
        
        if keyword_count >= 10:
            scores['Keywords'] = 90
            strengths.append("Strong use of action verbs and industry keywords")
        elif keyword_count >= 5:
            scores['Keywords'] = 70
            improvements.append("Incorporate more action verbs and industry keywords")
        else:
            scores['Keywords'] = 50
            improvements.append("Add more relevant keywords and action verbs")
        
        # Calculate overall score
        overall_score = sum(scores.values()) / len(scores)
        
        # Add keyword suggestions
        missing_keywords = [k for k in common_keywords if k not in content_text]
        if missing_keywords:
            keyword_suggestions = (
                "Consider incorporating these action verbs and keywords: " +
                ", ".join(missing_keywords[:10])
            )
        
        return {
            'overall_score': round(overall_score),
            'section_scores': scores,
            'strengths': strengths,
            'improvements': improvements,
            'keyword_suggestions': keyword_suggestions
        }

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

    def generate_microsoft_resume(self, basic_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a Microsoft-optimized resume with enhanced content."""
        try:
            # Add Microsoft-specific target job if not provided
            if not basic_info.get("target_job"):
                basic_info["target_job"] = {
                    "title": "Software Engineer",
                    "company": "Microsoft",
                    "description": """
                    Looking for a Software Engineer to join Microsoft's engineering team. The ideal candidate will have:
                    - Strong programming skills in multiple languages
                    - Experience with cloud computing and distributed systems
                    - Problem-solving abilities and analytical thinking
                    - Collaborative mindset and excellent communication skills
                    - Passion for innovation and continuous learning
                    """
                }
            
            # Enhance skills with Microsoft-specific categorization
            skills_prompt = f"""
            Categorize and enhance these skills for a Microsoft resume:
            {json.dumps(basic_info.get('skills', []))}
            
            Create these categories:
            1. Programming Languages
            2. Cloud & Infrastructure
            3. Development Tools & Platforms
            4. Soft Skills
            
            Add relevant Microsoft technologies if appropriate:
            - Azure Services
            - .NET Framework
            - Microsoft 365
            - Visual Studio
            - GitHub/Azure DevOps
            
            Return as JSON with categories as keys and skill arrays as values.
            """
            
            skills_response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{
                    "role": "system",
                    "content": "You are a Microsoft technical recruiter expert in organizing skills for maximum impact."
                }, {
                    "role": "user",
                    "content": skills_prompt
                }],
                temperature=0.7
            )
            
            enhanced_skills = json.loads(skills_response.choices[0].message.content)
            
            # Generate certifications suggestions
            cert_prompt = f"""
            Suggest relevant Microsoft certifications based on these skills:
            {json.dumps(enhanced_skills)}
            
            Include:
            1. Most relevant certification path
            2. Complementary certifications
            3. Future certification goals
            
            Return as JSON array of certification objects with name, status (completed/recommended), and relevance score.
            """
            
            cert_response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{
                    "role": "system",
                    "content": "You are a Microsoft certification expert."
                }, {
                    "role": "user",
                    "content": cert_prompt
                }],
                temperature=0.7
            )
            
            suggested_certs = json.loads(cert_response.choices[0].message.content)
            
            # Enhance or generate projects
            projects_prompt = f"""
            Create or enhance projects showcasing Microsoft-relevant skills:
            Skills: {json.dumps(enhanced_skills)}
            
            Each project should:
            1. Demonstrate scalability and enterprise-level thinking
            2. Show collaboration and version control
            3. Include cloud components (preferably Azure)
            4. Feature modern development practices
            5. Highlight problem-solving and innovation
            
            Return as JSON array of detailed project objects.
            """
            
            projects_response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{
                    "role": "system",
                    "content": "You are a senior Microsoft engineer who mentors candidates on project portfolios."
                }, {
                    "role": "user",
                    "content": projects_prompt
                }],
                temperature=0.7
            )
            
            enhanced_projects = json.loads(projects_response.choices[0].message.content)
            
            # Generate professional achievements
            achievements_prompt = f"""
            Create impactful professional achievements based on:
            Experience: {json.dumps(basic_info.get('work_experience', []))}
            Skills: {json.dumps(enhanced_skills)}
            
            Focus on:
            1. Leadership and initiative
            2. Technical innovation
            3. Project impact and scale
            4. Collaboration and teamwork
            5. Problem-solving
            
            Use Microsoft's leadership principles and quantify results.
            Return as JSON array of achievement strings.
            """
            
            achievements_response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{
                    "role": "system",
                    "content": "You are a Microsoft hiring manager who knows what achievements stand out."
                }, {
                    "role": "user",
                    "content": achievements_prompt
                }],
                temperature=0.7
            )
            
            enhanced_achievements = json.loads(achievements_response.choices[0].message.content)
            
            # Create final enhanced content
            enhanced_content = {
                "contact_info": basic_info.get("contact_info", {}),
                "professional_summary": self._generate_microsoft_summary(basic_info, enhanced_skills),
                "technical_skills": enhanced_skills,
                "work_experience": self._enhance_work_experience(basic_info.get("work_experience", []), enhanced_skills),
                "projects": enhanced_projects,
                "education": basic_info.get("education", {}),
                "certifications": {
                    "completed": basic_info.get("certifications", []),
                    "recommended": suggested_certs
                },
                "achievements": enhanced_achievements,
                "languages": basic_info.get("languages", []),
                "interests": self._enhance_interests(basic_info.get("hobbies", [])),
                "additional_info": {
                    "github": basic_info.get("github", ""),
                    "linkedin": basic_info.get("linkedin", ""),
                    "portfolio": basic_info.get("portfolio", "")
                }
            }
            
            return enhanced_content
            
        except Exception as e:
            print(f"Error generating Microsoft resume: {str(e)}")
            raise Exception(f"Failed to generate Microsoft-optimized resume: {str(e)}")
            
    def _generate_microsoft_summary(self, basic_info: Dict[str, Any], enhanced_skills: Dict[str, List[str]]) -> str:
        """Generate a Microsoft-focused professional summary."""
        prompt = f"""
        Create a powerful professional summary for a Microsoft resume:
        Skills: {json.dumps(enhanced_skills)}
        Experience: {json.dumps(basic_info.get('work_experience', []))}
        Education: {json.dumps(basic_info.get('education', {}))}
        
        The summary should:
        1. Show alignment with Microsoft's mission and values
        2. Highlight cloud and enterprise experience
        3. Emphasize innovation and problem-solving
        4. Demonstrate continuous learning
        5. Include collaboration and leadership
        
        Create a compelling 3-4 sentence summary.
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{
                "role": "system",
                "content": "You are a Microsoft recruiter who knows exactly what makes a summary stand out."
            }, {
                "role": "user",
                "content": prompt
            }],
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
        
    def _enhance_work_experience(self, experience: List[Dict[str, Any]], skills: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """Enhance work experience with Microsoft-relevant achievements."""
        enhanced_experience = []
        
        for exp in experience:
            prompt = f"""
            Enhance these work achievements for a Microsoft resume:
            Experience: {json.dumps(exp)}
            Skills: {json.dumps(skills)}
            
            For each achievement:
            1. Focus on scale and enterprise impact
            2. Highlight technical leadership
            3. Emphasize collaboration
            4. Include specific metrics
            5. Show innovation
            
            Return as JSON array of enhanced achievement strings.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{
                    "role": "system",
                    "content": "You are a Microsoft hiring manager who knows what achievements matter most."
                }, {
                    "role": "user",
                    "content": prompt
                }],
                temperature=0.7
            )
            
            enhanced_achievements = json.loads(response.choices[0].message.content)
            exp["achievements"] = enhanced_achievements
            enhanced_experience.append(exp)
        
        return enhanced_experience
        
    def _enhance_interests(self, interests: List[str]) -> List[str]:
        """Enhance interests to align with Microsoft culture."""
        prompt = f"""
        Enhance these interests to align with Microsoft's culture:
        {json.dumps(interests)}
        
        Focus on interests that show:
        1. Technical curiosity
        2. Continuous learning
        3. Problem-solving
        4. Creativity
        5. Community involvement
        
        Return as JSON array of enhanced interest strings.
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{
                "role": "system",
                "content": "You are a Microsoft culture expert who knows what interests resonate."
            }, {
                "role": "user",
                "content": prompt
            }],
            temperature=0.7
        )
        
        return json.loads(response.choices[0].message.content)

    def generate_universal_tech_resume(self, basic_info: Dict[str, Any], target_companies: List[str] = None) -> Dict[str, Any]:
        """Generate a resume optimized for top tech companies."""
        try:
            if not target_companies:
                target_companies = ["Google", "Amazon", "Microsoft", "Meta", "Apple"]
            
            # Enhance skills with universal categorization
            skills_prompt = f"""
            Categorize and enhance these skills for top tech companies:
            {json.dumps(basic_info.get('skills', {}))}
            
            Create these categories:
            1. Programming Languages & Frameworks
            2. Cloud & Infrastructure
            3. Tools & Technologies
            4. Soft Skills & Leadership
            
            Format the response exactly like this example:
            {{
                "Programming Languages & Frameworks": ["Python", "Java", "JavaScript"],
                "Cloud & Infrastructure": ["AWS", "Docker", "Kubernetes"],
                "Tools & Technologies": ["Git", "CI/CD", "Linux"],
                "Soft Skills & Leadership": ["Team Leadership", "Agile", "Communication"]
            }}
            """
            
            try:
                skills_response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[{
                        "role": "system",
                        "content": "You are a technical recruiter expert in organizing skills for maximum impact."
                    }, {
                        "role": "user",
                        "content": skills_prompt
                    }],
                    temperature=0.7
                )
                
                enhanced_skills = json.loads(skills_response.choices[0].message.content.strip())
            except Exception as e:
                print(f"Error enhancing skills: {str(e)}")
                enhanced_skills = basic_info.get('skills', {})
            
            # Enhance projects
            projects_prompt = f"""
            Create or enhance projects showcasing skills for top tech companies:
            Skills: {json.dumps(enhanced_skills)}
            Companies: {json.dumps(target_companies)}
            
            Format the response exactly like this example:
            [
                {{
                    "name": "Project Name",
                    "description": "Project description",
                    "technologies": ["Tech1", "Tech2"],
                    "highlights": ["Achievement 1", "Achievement 2"]
                }}
            ]
            """
            
            try:
                projects_response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[{
                        "role": "system",
                        "content": "You are a technical project expert who knows what top companies value."
                    }, {
                        "role": "user",
                        "content": projects_prompt
                    }],
                    temperature=0.7
                )
                
                enhanced_projects = json.loads(projects_response.choices[0].message.content.strip())
            except Exception as e:
                print(f"Error enhancing projects: {str(e)}")
                enhanced_projects = basic_info.get('projects', [])
            
            # Enhance achievements
            achievements_prompt = f"""
            Enhance these achievements for top tech companies:
            {json.dumps(basic_info.get('achievements', []))}
            
            Format the response exactly like this example:
            [
                "Led a team of 5 engineers to deliver a microservices architecture that reduced latency by 40%",
                "Implemented CI/CD pipeline reducing deployment time by 60%"
            ]
            """
            
            try:
                achievements_response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[{
                        "role": "system",
                        "content": "You are a career coach who helps candidates showcase their best achievements."
                    }, {
                        "role": "user",
                        "content": achievements_prompt
                    }],
                    temperature=0.7
                )
                
                enhanced_achievements = json.loads(achievements_response.choices[0].message.content.strip())
            except Exception as e:
                print(f"Error enhancing achievements: {str(e)}")
                enhanced_achievements = basic_info.get('achievements', [])
            
            # Generate certifications roadmap
            cert_prompt = f"""
            Suggest certifications valued by top tech companies:
            Skills: {json.dumps(enhanced_skills)}
            Companies: {json.dumps(target_companies)}
            
            Format the response exactly like this example:
            [
                {{
                    "name": "AWS Solutions Architect",
                    "issuer": "Amazon Web Services",
                    "difficulty": "Advanced",
                    "relevance_score": 9,
                    "target_companies": ["Amazon", "Google", "Microsoft"]
                }}
            ]
            """
            
            try:
                cert_response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[{
                        "role": "system",
                        "content": "You are a technical certification expert who knows what top companies value."
                    }, {
                        "role": "user",
                        "content": cert_prompt
                    }],
                    temperature=0.7
                )
                
                suggested_certs = json.loads(cert_response.choices[0].message.content.strip())
            except Exception as e:
                print(f"Error generating certifications: {str(e)}")
                suggested_certs = []
            
            # Create professional summary
            try:
                summary = self._generate_universal_summary(basic_info, enhanced_skills, target_companies)
            except Exception as e:
                print(f"Error generating summary: {str(e)}")
                summary = basic_info.get('professional_summary', '')
            
            # Enhance work experience
            try:
                enhanced_experience = self._enhance_universal_experience(
                    basic_info.get('work_experience', []),
                    enhanced_skills,
                    target_companies
                )
            except Exception as e:
                print(f"Error enhancing experience: {str(e)}")
                enhanced_experience = basic_info.get('work_experience', [])
            
            # Create final enhanced content
            enhanced_content = {
                "contact_info": basic_info.get("contact_info", {}),
                "professional_summary": summary,
                "technical_skills": enhanced_skills,
                "work_experience": enhanced_experience,
                "projects": enhanced_projects,
                "education": basic_info.get("education", {}),
                "certifications": {
                    "completed": basic_info.get("certifications", []),
                    "recommended": suggested_certs
                },
                "achievements": enhanced_achievements,
                "languages": basic_info.get("languages", []),
                "interests": self._enhance_universal_interests(
                    basic_info.get("hobbies", []),
                    target_companies
                ),
                "additional_info": {
                    "github": basic_info.get("github", ""),
                    "linkedin": basic_info.get("linkedin", ""),
                    "portfolio": basic_info.get("portfolio", ""),
                    "blog": basic_info.get("blog", "")
                }
            }
            
            return enhanced_content
            
        except Exception as e:
            print(f"Error generating universal tech resume: {str(e)}")
            raise Exception(f"Failed to generate tech-optimized resume: {str(e)}")
    
    def _generate_universal_summary(
        self,
        basic_info: Dict[str, Any],
        enhanced_skills: Dict[str, List[str]],
        target_companies: List[str]
    ) -> str:
        """Generate a powerful summary that appeals to all target companies."""
        prompt = f"""
        Create a compelling professional summary that appeals to:
        Companies: {json.dumps(target_companies)}
        
        Based on:
        Skills: {json.dumps(enhanced_skills)}
        Experience: {json.dumps(basic_info.get('work_experience', []))}
        Education: {json.dumps(basic_info.get('education', {}))}
        
        The summary should:
        1. Show versatility and adaptability
        2. Highlight technical excellence
        3. Demonstrate leadership and innovation
        4. Include relevant achievements
        5. Use powerful, action-oriented language
        6. Incorporate high-impact keywords
        
        Create a 3-4 sentence summary that would impress any tech company.
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{
                "role": "system",
                "content": "You are an expert resume writer who knows how to write summaries that catch any recruiter's attention."
            }, {
                "role": "user",
                "content": prompt
            }],
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
    
    def _enhance_universal_experience(
        self,
        experience: List[Dict[str, Any]],
        skills: Dict[str, List[str]],
        target_companies: List[str]
    ) -> List[Dict[str, Any]]:
        """Enhance work experience to appeal to all target companies."""
        enhanced_experience = []
        
        for exp in experience:
            prompt = f"""
            Enhance these work achievements to appeal to top tech companies:
            Companies: {json.dumps(target_companies)}
            Experience: {json.dumps(exp)}
            Skills: {json.dumps(skills)}
            
            For each achievement:
            1. Use STAR method
            2. Include metrics and impact
            3. Show technical depth
            4. Demonstrate leadership
            5. Highlight innovation
            6. Focus on scalability
            
            Return as JSON array of enhanced achievement strings.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{
                    "role": "system",
                    "content": "You are a career coach who knows how to write achievements that impress any tech company."
                }, {
                    "role": "user",
                    "content": prompt
                }],
                temperature=0.7
            )
            
            enhanced_achievements = json.loads(response.choices[0].message.content)
            exp["achievements"] = enhanced_achievements
            enhanced_experience.append(exp)
        
        return enhanced_experience
    
    def _enhance_universal_interests(
        self,
        interests: List[str],
        target_companies: List[str]
    ) -> List[str]:
        """Enhance interests to align with tech company cultures."""
        prompt = f"""
        Enhance these interests to appeal to tech companies:
        Interests: {json.dumps(interests)}
        Companies: {json.dumps(target_companies)}
        
        Focus on interests that show:
        1. Innovation and creativity
        2. Continuous learning
        3. Technical curiosity
        4. Problem-solving
        5. Leadership
        6. Community involvement
        
        Return as JSON array of enhanced interest strings.
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{
                "role": "system",
                "content": "You are a culture fit expert who knows what interests resonate with tech companies."
            }, {
                "role": "user",
                "content": prompt
            }],
            temperature=0.7
        )
        
        return json.loads(response.choices[0].message.content)

    def generate_resume_pdf(self, content: Dict[str, Any], output_path: str) -> None:
        """Generate a professional PDF resume."""
        try:
            # Create the PDF document
            doc = SimpleDocTemplate(
                output_path,
                pagesize=letter,
                rightMargin=inch/2,
                leftMargin=inch/2,
                topMargin=inch/2,
                bottomMargin=inch/2
            )
            
            # Initialize story
            story = []
            
            # Get styles
            styles = getSampleStyleSheet()
            
            # Create custom styles
            header_style = ParagraphStyle(
                'CustomHeader',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                textColor=colors.HexColor('#2C3E50')
            )
            
            section_style = ParagraphStyle(
                'CustomSection',
                parent=styles['Heading2'],
                fontSize=14,
                spaceBefore=20,
                spaceAfter=10,
                textColor=colors.HexColor('#2980B9')
            )
            
            normal_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=6
            )
            
            bullet_style = ParagraphStyle(
                'CustomBullet',
                parent=styles['Normal'],
                fontSize=10,
                leftIndent=20,
                spaceAfter=3
            )
            
            # Add contact information
            contact_info = content.get('contact_info', {})
            name = contact_info.get('name', '')
            email = contact_info.get('email', '')
            phone = contact_info.get('phone', '')
            location = contact_info.get('location', '')
            
            story.append(Paragraph(name, header_style))
            contact_text = f"{email} | {phone} | {location}"
            story.append(Paragraph(contact_text, normal_style))
            
            # Add professional summary
            if content.get('professional_summary'):
                story.append(Paragraph('Professional Summary', section_style))
                story.append(Paragraph(content['professional_summary'], normal_style))
            
            # Add technical skills
            if content.get('technical_skills'):
                story.append(Paragraph('Technical Skills', section_style))
                for category, skills in content['technical_skills'].items():
                    if skills:
                        story.append(Paragraph(f"<b>{category}:</b> {', '.join(skills)}", normal_style))
            
            # Add work experience
            if content.get('work_experience'):
                story.append(Paragraph('Professional Experience', section_style))
                for exp in content['work_experience']:
                    company = exp.get('company', '')
                    title = exp.get('title', '')
                    dates = exp.get('dates', '')
                    exp_text = f"<b>{title}</b> at <b>{company}</b> ({dates})"
                    story.append(Paragraph(exp_text, normal_style))
                    
                    for achievement in exp.get('achievements', []):
                        story.append(Paragraph(f"• {achievement}", bullet_style))
            
            # Add projects
            if content.get('projects'):
                story.append(Paragraph('Technical Projects', section_style))
                for project in content['projects']:
                    name = project.get('name', '')
                    desc = project.get('description', '')
                    tech = project.get('technologies', [])
                    highlights = project.get('highlights', [])
                    
                    story.append(Paragraph(f"<b>{name}</b>", normal_style))
                    if desc:
                        story.append(Paragraph(desc, normal_style))
                    if tech:
                        story.append(Paragraph(f"<b>Technologies:</b> {', '.join(tech)}", bullet_style))
                    for highlight in highlights:
                        story.append(Paragraph(f"• {highlight}", bullet_style))
            
            # Add education
            if content.get('education'):
                story.append(Paragraph('Education', section_style))
                edu = content['education']
                degree = edu.get('degree', '')
                major = edu.get('major', '')
                university = edu.get('university', '')
                graduation = edu.get('graduation_date', '')
                gpa = edu.get('gpa', '')
                
                edu_text = f"<b>{degree} in {major}</b>"
                if university:
                    edu_text += f" - {university}"
                if graduation:
                    edu_text += f" ({graduation})"
                if gpa:
                    edu_text += f" | GPA: {gpa}"
                    
                story.append(Paragraph(edu_text, normal_style))
                
                if edu.get('achievements'):
                    for achievement in edu['achievements']:
                        story.append(Paragraph(f"• {achievement}", bullet_style))
            
            # Add certifications
            if content.get('certifications', {}).get('completed'):
                story.append(Paragraph('Certifications', section_style))
                for cert in content['certifications']['completed']:
                    story.append(Paragraph(f"• {cert}", bullet_style))
            
            # Add languages
            if content.get('languages'):
                story.append(Paragraph('Languages', section_style))
                languages_text = ', '.join(content['languages'])
                story.append(Paragraph(languages_text, normal_style))
            
            # Add interests
            if content.get('interests'):
                story.append(Paragraph('Interests', section_style))
                interests_text = ', '.join(content['interests'])
                story.append(Paragraph(interests_text, normal_style))
            
            # Add additional info
            if content.get('additional_info'):
                links = []
                add_info = content['additional_info']
                if add_info.get('github'):
                    links.append(f"GitHub: {add_info['github']}")
                if add_info.get('linkedin'):
                    links.append(f"LinkedIn: {add_info['linkedin']}")
                if add_info.get('portfolio'):
                    links.append(f"Portfolio: {add_info['portfolio']}")
                if add_info.get('blog'):
                    links.append(f"Blog: {add_info['blog']}")
                
                if links:
                    story.append(Paragraph('Links', section_style))
                    for link in links:
                        story.append(Paragraph(link, normal_style))
            
            # Build the PDF
            doc.build(story)
            
        except Exception as e:
            print(f"Error generating resume PDF: {str(e)}")
            raise Exception(f"Failed to generate PDF resume: {str(e)}")
