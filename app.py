import streamlit as st
import os
import random
from dotenv import load_dotenv
import base64
import re
import plotly.graph_objects as go
from modules.resume_parser import extract_text_from_pdf
from modules.pq_calculator import calculate_pq_with_growth, calculate_risk_reward
from modules.career_growth import CareerGrowthPredictor
from modules.team_synergy import generate_team_profile, extract_candidate_skills, calculate_synergy_score, team_synergy_analysis
from modules.growth_map import GrowthMapGenerator
from modules.resume_builder import ATSResumeBuilder
from modules.game_generator import GameGenerator
from modules.career_coach import CareerCoach
from modules.interview_game import InterviewGame
from datetime import datetime
import fitz
import zipfile
import pyperclip

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    st.error("❌ OpenAI API key not found! Please add it to your .env file.")
    st.stop()

# Configure Streamlit page
st.set_page_config(
    page_title="Future You Predictor",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize components
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    resume_builder = ATSResumeBuilder(api_key)
    game_generator = GameGenerator(api_key)
    career_coach = CareerCoach(api_key)
    interview_game = InterviewGame(api_key)
else:
    st.error("⚠️ OpenAI API key not found. Please check your .env file.")
    st.stop()

# Initialize session state variables if they don't exist
if 'pdf_path' not in st.session_state:
    st.session_state.pdf_path = None

if 'extracted_text' not in st.session_state:
    st.session_state.extracted_text = None

# Custom styling
st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #0e1117;
        border-radius: 4px;
        color: #ffffff;
        padding: 10px 20px;
    }
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        background-color: #00b4c4;
    }
    /* Make gauge chart container smaller */
    .plot-container {
        max-width: 400px;
        margin: auto;
    }
</style>
""", unsafe_allow_html=True)

# Custom CSS for cards
st.markdown("""
<style>
.game-card {
    background-color: #2b2b2b;
    border-radius: 10px;
    padding: 20px;
    margin: 10px 0;
    border: 1px solid #3c3c3c;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
    height: 200px;
}

.game-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 15px rgba(0, 0, 0, 0.2);
    background-color: #363636;
    border-color: #4c4c4c;
}

.game-card h3 {
    color: #ffffff;
    font-size: 1.5em;
    margin-bottom: 10px;
    font-weight: 600;
}

.game-card p {
    color: #e0e0e0;
    font-size: 0.9em;
    margin-bottom: 15px;
    line-height: 1.6;
}

.mode-icon {
    font-size: 2em;
    margin-bottom: 15px;
    color: #ffffff;
}

.start-button {
    background-color: #4CAF50;
    color: white;
    padding: 8px 16px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    transition: background-color 0.3s ease;
}

.start-button:hover {
    background-color: #45a049;
}
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("Navigation")
selected_page = st.sidebar.selectbox(
    "Choose a feature",
    ["Home", "Resume Builder", "Resume Analysis", "PDF Viewer", "Career Coach", "Interview Game", "Learning Playlist"]
)

# Main content
if selected_page == "Home":
    st.title("Welcome to Future You Predictor")
    st.markdown("""
    ### Your AI-Powered Career Growth Partner
    
    Welcome to Future You Predictor, your comprehensive career development platform. Here's what you can do:
    
    #### 📝 Resume Builder
    - Create ATS-friendly resumes
    - Get AI-powered content optimization
    - Professional formatting and templates
    
    #### 📊 Resume Analysis
    - Get detailed career insights
    - Calculate your Potential Quotient (PQ)
    - Receive personalized growth recommendations
    
    #### 👨‍🏫 Career Coach
    - Get personalized career guidance
    - Set and achieve career goals
    - Develop a growth mindset
    
    #### 📚 Learning Playlist
    - Access curated learning resources
    - Track your progress
    - Stay updated with industry trends
    """)

elif selected_page == "Resume Builder":
    st.title("🎯 Smart Resume Builder")
    st.write("Create an ATS-optimized resume that stands out to top tech companies")
    
    # Initialize resume builder with API key from environment variable
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("⚠️ OpenAI API key not found. Please check your .env file.")
        st.stop()
    
    resume_builder = ATSResumeBuilder(api_key)
    
    # Multi-step form
    if 'resume_step' not in st.session_state:
        st.session_state.resume_step = 1
    
    # Progress bar
    total_steps = 7
    progress = (st.session_state.resume_step - 1) / total_steps
    st.progress(progress)
    
    # Navigation buttons
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.session_state.resume_step > 1:
            if st.button("⬅️ Previous Step"):
                st.session_state.resume_step -= 1
                st.experimental_rerun()
    
    with col2:
        if st.session_state.resume_step < total_steps:
            if st.button("Next Step ➡️"):
                st.session_state.resume_step += 1
                st.experimental_rerun()
    
    # Step 1: Basic Information
    if st.session_state.resume_step == 1:
        st.subheader("📋 Basic Information")
        with st.form("basic_info_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Full Name*", key="name")
                email = st.text_input("Email*", key="email")
                phone = st.text_input("Phone Number*", key="phone")
            with col2:
                location = st.text_input("Location*", key="location")
                linkedin = st.text_input("LinkedIn URL", key="linkedin")
                github = st.text_input("GitHub URL", key="github")
            
            portfolio = st.text_input("Portfolio/Personal Website", key="portfolio")
            blog = st.text_input("Tech Blog URL", key="blog")
            
            submitted = st.form_submit_button("Save & Continue")
            if submitted:
                if not name or not email or not phone or not location:
                    st.error("Please fill in all required fields marked with *")
                else:
                    st.session_state.basic_info = {
                        "contact_info": {
                            "name": name,
                            "email": email,
                            "phone": phone,
                            "location": location
                        },
                        "additional_info": {
                            "linkedin": linkedin,
                            "github": github,
                            "portfolio": portfolio,
                            "blog": blog
                        }
                    }
                    st.session_state.resume_step += 1
                    st.experimental_rerun()
    
    # Step 2: Education
    elif st.session_state.resume_step == 2:
        st.subheader("🎓 Education")
        with st.form("education_form"):
            col1, col2 = st.columns(2)
            with col1:
                degree = st.text_input("Degree*", key="degree")
                major = st.text_input("Major/Field of Study*", key="major")
            with col2:
                university = st.text_input("University/Institution*", key="university")
                graduation_date = st.text_input("Graduation Date*", help="Format: MMM YYYY (e.g., May 2024)")
            
            gpa = st.text_input("GPA", key="gpa", help="Leave blank if not applicable")
            achievements = st.text_area("Academic Achievements", 
                                     help="List notable academic achievements, honors, or relevant coursework")
            
            submitted = st.form_submit_button("Save & Continue")
            if submitted:
                if not degree or not major or not university or not graduation_date:
                    st.error("Please fill in all required fields marked with *")
                else:
                    st.session_state.basic_info["education"] = {
                        "degree": degree,
                        "major": major,
                        "university": university,
                        "graduation_date": graduation_date,
                        "gpa": gpa if gpa else None,
                        "achievements": [ach.strip() for ach in achievements.split('\n') if ach.strip()]
                    }
                    st.session_state.resume_step += 1
                    st.experimental_rerun()
    
    # Step 3: Skills
    elif st.session_state.resume_step == 3:
        st.subheader("🛠️ Skills")
        with st.form("skills_form"):
            st.write("Group your skills by category. Add multiple skills separated by commas.")
            
            programming = st.text_area("Programming Languages", 
                                     help="E.g., Python, Java, JavaScript, C++")
            
            frameworks = st.text_area("Frameworks & Libraries",
                                    help="E.g., React, Django, TensorFlow, Spring")
            
            databases = st.text_area("Databases & Storage",
                                   help="E.g., PostgreSQL, MongoDB, Redis")
            
            cloud = st.text_area("Cloud & Infrastructure",
                               help="E.g., AWS, Azure, Docker, Kubernetes")
            
            tools = st.text_area("Development Tools",
                               help="E.g., Git, Jenkins, JIRA, VS Code")
            
            soft_skills = st.text_area("Soft Skills",
                                     help="E.g., Team Leadership, Agile Methodology, Problem Solving")
            
            other = st.text_area("Other Technical Skills",
                               help="Any other relevant technical skills")
            
            submitted = st.form_submit_button("Save & Continue")
            if submitted:
                def parse_skills(text):
                    return [skill.strip() for skill in text.split(',') if skill.strip()]
                
                st.session_state.basic_info["skills"] = {
                    "Programming Languages": parse_skills(programming),
                    "Frameworks & Libraries": parse_skills(frameworks),
                    "Databases & Storage": parse_skills(databases),
                    "Cloud & Infrastructure": parse_skills(cloud),
                    "Development Tools": parse_skills(tools),
                    "Soft Skills": parse_skills(soft_skills),
                    "Other": parse_skills(other)
                }
                st.session_state.resume_step += 1
                st.experimental_rerun()
    
    # Step 4: Work Experience
    elif st.session_state.resume_step == 4:
        st.subheader("💼 Work Experience")
        
        if 'work_experiences' not in st.session_state:
            st.session_state.work_experiences = []
        
        with st.form("work_exp_form"):
            col1, col2 = st.columns(2)
            with col1:
                title = st.text_input("Job Title*")
                company = st.text_input("Company Name*")
            with col2:
                location = st.text_input("Location*")
                start_date = st.text_input("Start Date*", help="Format: MMM YYYY")
                end_date = st.text_input("End Date", help="Format: MMM YYYY or 'Present'")
            
            responsibilities = st.text_area("Key Responsibilities*",
                                         help="List your main responsibilities and duties")
            
            achievements = st.text_area("Key Achievements*",
                                      help="Use STAR method: Situation, Task, Action, Result\n" +
                                      "Focus on quantifiable achievements and impact")
            
            tech_stack = st.text_input("Technologies Used",
                                     help="List main technologies, tools, and frameworks used")
            
            submitted = st.form_submit_button("Add Experience")
            if submitted:
                if not title or not company or not location or not start_date or not responsibilities or not achievements:
                    st.error("Please fill in all required fields marked with *")
                else:
                    experience = {
                        "title": title,
                        "company": company,
                        "location": location,
                        "start_date": start_date,
                        "end_date": end_date if end_date else "Present",
                        "responsibilities": [r.strip() for r in responsibilities.split('\n') if r.strip()],
                        "achievements": [a.strip() for a in achievements.split('\n') if a.strip()],
                        "technologies": [t.strip() for t in tech_stack.split(',') if t.strip()]
                    }
                    st.session_state.work_experiences.append(experience)
        
        # Display added experiences
        if st.session_state.work_experiences:
            st.write("### Added Experiences")
            for i, exp in enumerate(st.session_state.work_experiences):
                with st.expander(f"{exp['title']} at {exp['company']}"):
                    st.write(f"**Location:** {exp['location']}")
                    st.write(f"**Period:** {exp['start_date']} - {exp['end_date']}")
                    st.write("**Responsibilities:**")
                    for resp in exp['responsibilities']:
                        st.write(f"- {resp}")
                    st.write("**Achievements:**")
                    for ach in exp['achievements']:
                        st.write(f"- {ach}")
                    if exp['technologies']:
                        st.write(f"**Technologies:** {', '.join(exp['technologies'])}")
                    
                    if st.button(f"Remove Experience {i+1}"):
                        st.session_state.work_experiences.pop(i)
                        st.experimental_rerun()
        
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.session_state.work_experiences and st.button("Continue ➡️"):
                st.session_state.basic_info["work_experience"] = st.session_state.work_experiences
                st.session_state.resume_step += 1
                st.experimental_rerun()
    
    # Step 5: Projects
    elif st.session_state.resume_step == 5:
        st.subheader("🚀 Technical Projects")
        
        if 'projects' not in st.session_state:
            st.session_state.projects = []
        
        with st.form("project_form"):
            name = st.text_input("Project Name*")
            description = st.text_area("Project Description*",
                                    help="Brief overview of the project's purpose and scope")
            
            col1, col2 = st.columns(2)
            with col1:
                tech_stack = st.text_input("Technologies Used*",
                                         help="List main technologies separated by commas")
                role = st.text_input("Your Role",
                                   help="E.g., Lead Developer, Full Stack Engineer")
            with col2:
                github_link = st.text_input("GitHub/Source Code Link")
                live_link = st.text_input("Live Demo Link")
            
            key_features = st.text_area("Key Features*",
                                      help="List main features and functionalities")
            
            challenges = st.text_area("Technical Challenges & Solutions",
                                    help="Describe key challenges and how you solved them")
            
            impact = st.text_area("Impact & Results",
                                help="Describe the project's impact, metrics, or user feedback")
            
            submitted = st.form_submit_button("Add Project")
            if submitted:
                if not name or not description or not tech_stack or not key_features:
                    st.error("Please fill in all required fields marked with *")
                else:
                    project = {
                        "name": name,
                        "description": description,
                        "technologies": [t.strip() for t in tech_stack.split(',') if t.strip()],
                        "role": role,
                        "github_link": github_link,
                        "live_link": live_link,
                        "features": [f.strip() for f in key_features.split('\n') if f.strip()],
                        "challenges": [c.strip() for c in challenges.split('\n') if c.strip()],
                        "impact": [i.strip() for i in impact.split('\n') if i.strip()]
                    }
                    st.session_state.projects.append(project)
        
        # Display added projects
        if st.session_state.projects:
            st.write("### Added Projects")
            for i, proj in enumerate(st.session_state.projects):
                with st.expander(f"{proj['name']}"):
                    st.write(f"**Description:** {proj['description']}")
                    st.write(f"**Technologies:** {', '.join(proj['technologies'])}")
                    if proj['role']:
                        st.write(f"**Role:** {proj['role']}")
                    st.write("**Key Features:**")
                    for feat in proj['features']:
                        st.write(f"- {feat}")
                    if proj['challenges']:
                        st.write("**Challenges & Solutions:**")
                        for chal in proj['challenges']:
                            st.write(f"- {chal}")
                    if proj['impact']:
                        st.write("**Impact & Results:**")
                        for imp in proj['impact']:
                            st.write(f"- {imp}")
                    
                    if st.button(f"Remove Project {i+1}"):
                        st.session_state.projects.pop(i)
                        st.experimental_rerun()
        
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.session_state.projects and st.button("Continue ➡️"):
                st.session_state.basic_info["projects"] = st.session_state.projects
                st.session_state.resume_step += 1
                st.experimental_rerun()
    
    # Step 6: Additional Information
    elif st.session_state.resume_step == 6:
        st.subheader("✨ Additional Information")
        with st.form("additional_info_form"):
            certifications = st.text_area("Certifications",
                                        help="List relevant certifications with dates")
            
            languages = st.text_input("Languages",
                                    help="List languages and proficiency levels, separated by commas")
            
            awards = st.text_area("Awards & Recognition",
                                help="List any relevant awards or recognition")
            
            publications = st.text_area("Publications & Patents",
                                      help="List any publications, patents, or research work")
            
            volunteer = st.text_area("Volunteer Work",
                                   help="List relevant volunteer experience or community involvement")
            
            interests = st.text_area("Professional Interests",
                                   help="List technical interests, hobbies, or passion projects")
            
            submitted = st.form_submit_button("Save & Continue")
            if submitted:
                def parse_list(text):
                    return [item.strip() for item in text.split('\n') if item.strip()]
                
                st.session_state.basic_info.update({
                    "certifications": parse_list(certifications),
                    "languages": [lang.strip() for lang in languages.split(',') if lang.strip()],
                    "awards": parse_list(awards),
                    "publications": parse_list(publications),
                    "volunteer": parse_list(volunteer),
                    "hobbies": parse_list(interests)
                })
                st.session_state.resume_step += 1
                st.experimental_rerun()
    
    # Step 7: Target Companies & Generate
    elif st.session_state.resume_step == 7:
        st.subheader("🎯 Target Companies & Resume Generation")
        
        # Initialize resume generation state if not exists
        if 'resume_generated' not in st.session_state:
            st.session_state.resume_generated = False
            st.session_state.current_resume_path = None
            st.session_state.current_resume_content = None
        
        # Company selection form
        with st.form("generate_form"):
            st.write("Select target companies to optimize your resume for:")
            
            companies = {
                "FAANG+": ["Amazon", "Apple", "Google", "Meta", "Microsoft", "Netflix"],
                "Tech Giants": ["IBM", "Oracle", "Intel", "Salesforce", "Adobe"],
                "Consulting": ["Accenture", "Capgemini", "Deloitte", "TCS", "Infosys"],
                "Others": ["Twitter", "Uber", "Airbnb", "LinkedIn", "PayPal"]
            }
            
            selected_companies = []
            for category, company_list in companies.items():
                st.write(f"**{category}**")
                cols = st.columns(3)
                for i, company in enumerate(company_list):
                    with cols[i % 3]:
                        if st.checkbox(company, key=f"company_{company}"):
                            selected_companies.append(company)
            
            custom_companies = st.text_input("Add other target companies",
                                           help="Separate by commas")
            if custom_companies:
                selected_companies.extend([c.strip() for c in custom_companies.split(',') if c.strip()])
            
            st.write("---")
            st.write("**Resume Preferences**")
            
            col1, col2 = st.columns(2)
            with col1:
                style = st.selectbox("Resume Style",
                                   ["Modern", "Classic", "Minimal"],
                                   help="Choose the visual style of your resume")
            with col2:
                color = st.selectbox("Color Scheme",
                                   ["Professional Blue", "Classic Black", "Modern Gray"],
                                   help="Choose the color scheme for your resume")
            
            include_photo = st.checkbox("Include professional photo",
                                      help="Not recommended for US job applications")
            
            if include_photo:
                photo = st.file_uploader("Upload professional photo", type=['jpg', 'png'])
            
            # Additional preferences
            st.write("**Advanced Options**")
            col1, col2 = st.columns(2)
            with col1:
                emphasis = st.selectbox("Content Emphasis",
                                      ["Balanced", "Technical Skills", "Leadership", "Innovation"],
                                      help="Choose what aspects to emphasize in your resume")
            with col2:
                length = st.selectbox("Resume Length",
                                    ["Concise (1 page)", "Detailed (2 pages)"],
                                    help="Choose your preferred resume length")
            
            submitted = st.form_submit_button("Generate Resume")
        
        # Handle resume generation outside the form
        if submitted:
            if not selected_companies:
                st.error("Please select at least one target company")
            else:
                with st.spinner("🔄 Generating your optimized resume..."):
                    try:
                        # Generate resume content
                        resume_content = resume_builder.generate_universal_tech_resume(
                            st.session_state.basic_info,
                            selected_companies
                        )
                        
                        # Generate PDF
                        output_path = f"output/{st.session_state.basic_info['contact_info']['name'].replace(' ', '_')}_Resume.pdf"
                        os.makedirs("output", exist_ok=True)
                        resume_builder.generate_resume_pdf(resume_content, output_path)
                        
                        # Store the generated resume info in session state
                        st.session_state.resume_generated = True
                        st.session_state.current_resume_path = output_path
                        st.session_state.current_resume_content = resume_content
                        
                        # Show success message
                        st.success("✅ Resume generated successfully!")
                        
                    except Exception as e:
                        st.error(f"Error generating resume: {str(e)}")
        
        # Show preview and actions if resume is generated
        if st.session_state.resume_generated and st.session_state.current_resume_path:
            st.write("---")
            st.subheader("📄 Resume Preview")
            
            # Create tabs for different preview sections
            preview_tab1, preview_tab2, preview_tab3 = st.tabs(["PDF Preview", "Content Overview", "ATS Score"])
            
            with preview_tab1:
                # Display PDF preview using iframe
                with open(st.session_state.current_resume_path, "rb") as pdf_file:
                    base64_pdf = base64.b64encode(pdf_file.read()).decode('utf-8')
                    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
                    st.markdown(pdf_display, unsafe_allow_html=True)
            
            with preview_tab2:
                # Show content overview
                content = st.session_state.current_resume_content
                
                with st.expander("📝 Professional Summary", expanded=True):
                    st.write(content.get('professional_summary', ''))
                
                with st.expander("🛠️ Technical Skills"):
                    for category, skills in content.get('technical_skills', {}).items():
                        st.write(f"**{category}:**")
                        st.write(", ".join(skills))
                
                with st.expander("💼 Work Experience"):
                    for exp in content.get('work_experience', []):
                        st.write(f"**{exp.get('title')} at {exp.get('company')}**")
                        for achievement in exp.get('achievements', []):
                            st.write(f"• {achievement}")
                        st.write("---")
                
                with st.expander("🚀 Projects"):
                    for project in content.get('projects', []):
                        st.write(f"**{project.get('name')}**")
                        st.write(project.get('description', ''))
                        st.write(f"*Technologies:* {', '.join(project.get('technologies', []))}")
                        for highlight in project.get('highlights', []):
                            st.write(f"• {highlight}")
                        st.write("---")
            
            with preview_tab3:
                # Show ATS score and optimization analysis
                with st.spinner("Analyzing ATS compatibility..."):
                    ats_score = resume_builder.analyze_ats_score(st.session_state.current_resume_content)
                    
                    # Create a gauge chart for the overall score
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=ats_score['overall_score'],
                        title={"text": "ATS Score"},
                        gauge={
                            'axis': {'range': [0, 100]},
                            'bar': {'color': "#00b4c4"},
                            'steps': [
                                {'range': [0, 60], 'color': "lightgray"},
                                {'range': [60, 80], 'color': "gray"},
                                {'range': [80, 100], 'color': "darkgray"}
                            ],
                            'threshold': {
                                'line': {'color': "red", 'width': 4},
                                'thickness': 0.75,
                                'value': 80
                            }
                        }
                    ))
                    fig.update_layout(
                        height=300,
                        margin=dict(l=10, r=10, t=40, b=10)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Show section scores
                    st.write("### Section Scores")
                    cols = st.columns(4)
                    for i, (section, score) in enumerate(ats_score['section_scores'].items()):
                        with cols[i]:
                            st.metric(section.title(), f"{score}%")
                    
                    # Show analysis
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("### ✅ Strengths")
                        for strength in ats_score['strengths']:
                            st.write(f"• {strength}")
                    
                    with col2:
                        st.write("### 🔄 Improvements")
                        for improvement in ats_score['improvements']:
                            st.write(f"• {improvement}")
                    
                    st.write("### 🎯 Keyword Suggestions")
                    st.write(ats_score['keyword_suggestions'])
            
            # Action buttons
            st.write("---")
            col1, col2, col3 = st.columns([1, 1, 2])
            
            with col1:
                # Download button
                with open(st.session_state.current_resume_path, "rb") as file:
                    st.download_button(
                        label="⬇️ Download Resume",
                        data=file,
                        file_name=os.path.basename(st.session_state.current_resume_path),
                        mime="application/pdf"
                    )
            
            with col2:
                # Regenerate button
                if st.button("🔄 Regenerate Resume"):
                    st.session_state.resume_generated = False
                    st.session_state.current_resume_path = None
                    st.session_state.current_resume_content = None
                    st.experimental_rerun()
            
            with col3:
                # Show optimization tips in an expander
                with st.expander("📈 Resume Optimization Tips"):
                    st.write("""
                    ### Tips for Success
                    1. **Customize for Each Application**
                       - Adjust keywords based on job description
                       - Highlight relevant projects and skills
                    
                    2. **Keep it Concise**
                       - Limit to 1-2 pages
                       - Use bullet points for clarity
                    
                    3. **Quantify Achievements**
                       - Use metrics and numbers
                       - Show impact and results
                    
                    4. **Online Presence**
                       - Keep LinkedIn updated
                       - Maintain active GitHub
                       - Build personal portfolio
                    """)
    
elif selected_page == "Resume Analysis":
    st.title("Resume Analysis")
    uploaded_file = st.file_uploader(
        label="Upload your resume (PDF)",
        type="pdf"
    )
    
    if uploaded_file:
        with st.spinner("Analyzing your resume..."):
            # Create data directory if it doesn't exist
            os.makedirs("data", exist_ok=True)
            
            # Save and analyze the file
            file_path = os.path.join("data", uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Store the file path in session state
            st.session_state.pdf_path = file_path
            
            # Extract details from PDF
            extracted_details = extract_text_from_pdf(file_path)
            resume_text = " ".join([str(value) if isinstance(value, str) else ", ".join(value) for value in extracted_details.values()])
            
            # Store extracted text in session state
            st.session_state.extracted_text = resume_text
            
            # Create tabs for different analyses
            tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Resume Summary", "PQ Score", "Team Synergy", "Career Growth", "Skills Gap", "Industry Fit"])
            
            # Resume Summary Tab
            with tab1:
                st.write("### 📄 Resume Summary")
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Personal Details:**")
                    st.write(f"📝 Name: {extracted_details['Name']}")
                    st.write(f"📧 Email: {extracted_details['Email']}")
                    st.write(f"📱 Phone: {extracted_details['Phone']}")
                with col2:
                    st.write("**Professional Details:**")
                    st.write(f"💼 Experience: {extracted_details['Experience']}")
                    st.write(f"🎓 Year of Passing: {extracted_details['Year of Passing (YOP)']}")
                    st.write("🛠️ Skills:")
                    for skill in extracted_details['Skills']:
                        if skill != "Not Found":
                            st.write(f"  • {skill}")
                    if extracted_details['Certifications'][0] != "Not Found":
                        st.write("📜 Certifications:")
                        for cert in extracted_details['Certifications']:
                            st.write(f"  • {cert}")
            
            # PQ Score Tab
            with tab2:
                st.write("### Potential Quotient (PQ) Analysis")
                
                # Calculate metrics for PQ score
                skills_matched = len([s for s in extracted_details['Skills'] if s != "Not Found"])
                years_pattern = r"\b\d+\s+years?\b"
                years_match = re.search(years_pattern, extracted_details['Experience'])
                years_of_experience = int(years_match.group().split()[0]) if years_match else 1
                
                # Calculate PQ score
                pq_results = calculate_pq_with_growth(resume_text, skills_matched, years_of_experience)
                pq_score = pq_results["PQ Score"]
                risk_reward = calculate_risk_reward(pq_score, skills_matched, years_of_experience)
                
                # Display PQ score with a gauge chart
                col1, col2 = st.columns([2, 1])
                with col1:
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=pq_score,
                        title={"text": "PQ Score"},
                        gauge={
                            "axis": {"range": [0, 100]},
                            "bar": {"color": "#00b4c4"},
                            "steps": [
                                {"range": [0, 100], "color": "#1e2130"}
                            ],
                            "threshold": {
                                "line": {"color": "#00b4c4", "width": 4},
                                "thickness": 0.75,
                                "value": pq_score
                            }
                        }
                    ))
                    fig.update_layout(
                        height=300,
                        margin=dict(l=10, r=10, t=40, b=10)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Display risk-reward analysis
                st.write("### Risk-Reward Analysis")
                st.write(f"**Assessment:** {risk_reward['assessment']}")
                st.write(f"**Risk Level:** {risk_reward['risk_level']}")
                st.write(f"**Reward Level:** {risk_reward['reward_level']}")
                st.write("**Recommendations:**")
                for rec in risk_reward['recommendations']:
                    st.write(f"• {rec}")
            
            # Team Synergy Tab
            with tab3:
                st.write("### Team Synergy Analysis")
                
                # Get company and role information
                col1, col2 = st.columns(2)
                with col1:
                    company_name = st.text_input("Company Name", placeholder="Enter company name")
                with col2:
                    job_role = st.text_input("Job Role", placeholder="Enter job role")
                
                if company_name and job_role:
                    # Extract candidate skills and generate team profiles
                    candidate_skills = extract_candidate_skills(resume_text)
                    team_profiles = generate_team_profile(num_features=len(candidate_skills))
                    
                    try:
                        # Calculate synergy scores
                        synergy_scores = calculate_synergy_score(candidate_skills, team_profiles)
                        analysis = team_synergy_analysis(candidate_skills, team_profiles)
                        
                        # Display synergy scores with a bar chart
                        st.write(f"### Team Synergy Score for {job_role} at {company_name}")
                        
                        # Create metrics for quick view
                        cols = st.columns(3)
                        for idx, score in enumerate(synergy_scores[:3]):
                            with cols[idx]:
                                st.metric(
                                    label=f"Team {idx + 1}",
                                    value=f"{score:.0%}",
                                    delta=f"{'High' if score > 0.7 else 'Moderate' if score > 0.5 else 'Low'} Synergy"
                                )
                        
                        # Display synergy graph
                        st.write("### 📊 Team Synergy Graph")
                        fig = go.Figure()
                        
                        # Add bar chart
                        fig.add_trace(go.Bar(
                            x=[f"Team {i+1}" for i in range(len(synergy_scores))],
                            y=synergy_scores,
                            marker_color='#00b4c4',
                            hovertemplate="Team %{x}<br>Synergy Score: %{y:.0%}<extra></extra>"
                        ))
                        
                        # Add threshold lines
                        # fig.add_hline(y=0.7, line_dash="dash", line_color="#00FF00", annotation_text="High Synergy (70%)")
                        # fig.add_hline(y=0.5, line_dash="dash", line_color="#FFA500", annotation_text="Moderate Synergy (50%)")
                        
                        # Update layout
                        fig.update_layout(
                            yaxis=dict(
                                range=[0, 1],
                                tickformat=".0%",
                                title="Synergy Score"
                            ),
                            xaxis_title="Teams",
                            showlegend=False,
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            margin=dict(t=30, b=0, l=0, r=0),
                            height=300
                        )
                        
                        # Update grid
                        fig.update_yaxes(
                            showgrid=True,
                            gridwidth=1,
                            gridcolor='rgba(128,128,128,0.2)',
                            zeroline=False
                        )
                        fig.update_xaxes(
                            showgrid=False,
                            zeroline=False
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Display detailed analysis in an expander
                        with st.expander("📊 Detailed Team Analysis", expanded=True):
                            for idx, (score, insight) in enumerate(zip(synergy_scores, analysis)):
                                synergy_level = "High" if score > 0.7 else "Moderate" if score > 0.5 else "Low"
                                color = "#00b4c4" if score > 0.7 else "#FFA500" if score > 0.5 else "#FF4B4B"
                                st.markdown(f"""
                                    <div style='padding: 10px; border-radius: 5px; margin: 5px 0; border-left: 5px solid {color}'>
                                        <strong>Team {idx + 1}</strong>: {synergy_level} synergy ({score:.0%})
                                        <br>{insight}
                                    </div>
                                """, unsafe_allow_html=True)
                        
                        # Add recommendations in a clean format
                        st.write("### 💡 Team Fit Recommendations")
                        recommendations = [
                            "Focus on collaborative projects to enhance team dynamics",
                            "Share knowledge and expertise with team members",
                            "Participate in team-building activities",
                            "Develop cross-functional skills to better support the team"
                        ]
                        cols = st.columns(2)
                        for i, rec in enumerate(recommendations):
                            with cols[i % 2]:
                                st.markdown(f"""
                                    <div style='padding: 10px; border-radius: 5px; margin: 5px 0; background-color: #1E1E1E; border-left: 5px solid #00b4c4'>
                                        {rec}
                                    </div>
                                """, unsafe_allow_html=True)
                    
                    except Exception as e:
                        st.error(f"Error in team synergy analysis: {str(e)}")
                else:
                    st.info("Please enter the company name and job role to view team synergy analysis")
            
            # Career Growth Tab
            with tab4:
                st.write("### Career Growth Analysis")
                
                try:
                    # Create two columns for the main sections
                    growth_col1, growth_col2 = st.columns([3, 2])
                    
                    with growth_col1:
                        st.write("### 📈 AI-Powered Growth Map")
                        
                        # Skills Analysis
                        missing_skills = [
                            "Cloud Architecture",
                            "DevOps Practices",
                            "System Design",
                            "Team Leadership"
                        ]
                        
                        certifications = [
                            "AWS Solutions Architect",
                            "Professional Scrum Master",
                            "Cloud Security Certification"
                        ]
                        
                        soft_skills = [
                            "Strategic Planning",
                            "Team Management",
                            "Stakeholder Communication"
                        ]
                        
                        # Display skills in a modern card layout
                        st.markdown("""
                            <style>
                            .skill-card {
                                background-color: #1E1E1E;
                                padding: 15px;
                                border-radius: 5px;
                                margin: 10px 0;
                                border-left: 5px solid #00b4c4;
                            }
                            </style>
                        """, unsafe_allow_html=True)
                        
                        with st.expander("🎯 Missing Skills to Acquire", expanded=True):
                            for skill in missing_skills:
                                st.markdown(f"""
                                    <div class="skill-card">
                                        {skill}
                                    </div>
                                """, unsafe_allow_html=True)
                        
                        with st.expander("📜 Recommended Certifications", expanded=True):
                            for cert in certifications:
                                st.markdown(f"""
                                    <div class="skill-card">
                                        {cert}
                                    </div>
                                """, unsafe_allow_html=True)
                        
                        with st.expander("🤝 Soft Skills to Develop", expanded=True):
                            for skill in soft_skills:
                                st.markdown(f"""
                                    <div class="skill-card">
                                        {skill}
                                    </div>
                                """, unsafe_allow_html=True)
                    
                    with growth_col2:
                        st.write("### 🌱 Career Progression")
                        
                        # Career progression timeline
                        progression = [
                            ("Current", "Software Developer", "Present"),
                            ("Next", "Senior Developer", "1-2 years"),
                            ("Future", "Technical Lead", "2-3 years"),
                            ("Goal", "Engineering Manager", "3-5 years")
                        ]
                        
                        for stage, role, timeline in progression:
                            st.markdown(f"""
                                <div style='padding: 10px; border-radius: 5px; margin: 10px 0; background-color: #1E1E1E; border-left: 5px solid #00b4c4'>
                                    <small>{stage} ({timeline})</small><br>
                                    <strong>{role}</strong>
                                </div>
                            """, unsafe_allow_html=True)
                        
                        # Leadership and Project Recommendations
                        st.write("### 💫 Growth Opportunities")
                        opportunities = [
                            "Lead a cross-functional team project",
                            "Mentor junior developers",
                            "Drive technical architecture decisions"
                        ]
                        
                        for opp in opportunities:
                            st.markdown(f"""
                                <div style='padding: 10px; border-radius: 5px; margin: 5px 0; background-color: #1E1E1E; border-left: 5px solid #00b4c4'>
                                    {opp}
                                </div>
                            """, unsafe_allow_html=True)
                
                except Exception as e:
                    st.error(f"Error in career growth analysis: {str(e)}")
            
            # Skills Gap Tab
            with tab5:
                st.write("### 🎯 Skills Gap Analysis")
                
                try:
                    # Get job role for comparison
                    job_role = st.selectbox(
                        "Select Target Role",
                        ["Software Engineer", "Data Scientist", "DevOps Engineer", "Full Stack Developer", "Product Manager"]
                    )
                    
                    # Display skills comparison
                    st.write("### Skills Comparison")
                    
                    # Create two columns for current vs required skills
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("#### 💪 Your Current Skills")
                        current_skills = extracted_details['Skills']
                        for skill in current_skills:
                            if skill != "Not Found":
                                st.markdown(f"""
                                    <div style='padding: 10px; border-radius: 5px; margin: 5px 0; 
                                    background-color: #1E1E1E; border-left: 5px solid #00b4c4'>
                                        {skill}
                                    </div>
                                """, unsafe_allow_html=True)
                    
                    with col2:
                        st.write("#### 🎯 Required Skills")
                        # Example required skills based on role
                        required_skills = {
                            "Software Engineer": ["Python", "Java", "System Design", "Data Structures", "Algorithms"],
                            "Data Scientist": ["Python", "Machine Learning", "Statistics", "SQL", "Data Visualization"],
                            "DevOps Engineer": ["Docker", "Kubernetes", "CI/CD", "Cloud Platforms", "Shell Scripting"],
                            "Full Stack Developer": ["JavaScript", "React", "Node.js", "MongoDB", "REST APIs"],
                            "Product Manager": ["Agile", "Product Strategy", "User Research", "Analytics", "Roadmapping"]
                        }
                        
                        for skill in required_skills[job_role]:
                            status = "✅" if skill in current_skills else "❌"
                            st.markdown(f"""
                                <div style='padding: 10px; border-radius: 5px; margin: 5px 0; 
                                background-color: #1E1E1E; border-left: 5px solid {"#00b4c4" if skill in current_skills else "#FF4B4B"}'>
                                    {status} {skill}
                                </div>
                            """, unsafe_allow_html=True)
                    
                    # Skills Gap Summary
                    st.write("### 📊 Gap Analysis Summary")
                    missing_skills = [skill for skill in required_skills[job_role] if skill not in current_skills]
                    match_percentage = (len(required_skills[job_role]) - len(missing_skills)) / len(required_skills[job_role]) * 100
                    
                    # Display match percentage
                    st.metric("Skills Match", f"{match_percentage:.0f}%")
                    
                    if missing_skills:
                        st.write("#### 🎯 Skills to Acquire")
                        for skill in missing_skills:
                            st.markdown(f"""
                                <div style='padding: 10px; border-radius: 5px; margin: 5px 0; 
                                background-color: #1E1E1E; border-left: 5px solid #FFA500'>
                                    • {skill}
                                </div>
                            """, unsafe_allow_html=True)
                
                except Exception as e:
                    st.error(f"Error in skills gap analysis: {str(e)}")
            
            # Industry Fit Tab
            with tab6:
                st.write("### 🎯 Industry Fit Analysis")
                
                try:
                    # Industry selection
                    industry = st.selectbox(
                        "Select Target Industry",
                        ["Technology", "Finance", "Healthcare", "E-commerce", "Consulting"]
                    )
                    
                    # Industry fit metrics
                    st.write("### 📊 Industry Alignment")
                    
                    # Calculate industry alignment scores (example metrics)
                    metrics = {
                        "Technology": {
                            "Technical Skills": 85,
                            "Industry Knowledge": 75,
                            "Innovation Focus": 80,
                            "Scalability Experience": 70
                        },
                        "Finance": {
                            "Technical Skills": 70,
                            "Industry Knowledge": 60,
                            "Security Focus": 75,
                            "Regulatory Awareness": 65
                        },
                        "Healthcare": {
                            "Technical Skills": 75,
                            "Industry Knowledge": 55,
                            "Compliance Understanding": 60,
                            "Data Privacy": 80
                        },
                        "E-commerce": {
                            "Technical Skills": 80,
                            "Industry Knowledge": 70,
                            "User Experience": 85,
                            "Scalability": 75
                        },
                        "Consulting": {
                            "Technical Skills": 75,
                            "Industry Knowledge": 65,
                            "Client Communication": 80,
                            "Problem Solving": 85
                        }
                    }
                    
                    # Display metrics in a 2x2 grid
                    col1, col2 = st.columns(2)
                    metrics_list = list(metrics[industry].items())
                    
                    for i, (metric, score) in enumerate(metrics_list):
                        with col1 if i < 2 else col2:
                            st.metric(metric, f"{score}%")
                    
                    # Overall fit score
                    overall_score = sum(metrics[industry].values()) / len(metrics[industry])
                    st.metric("Overall Industry Fit", f"{overall_score:.0f}%")
                    
                    # Industry-specific recommendations
                    st.write("### 💡 Industry-Specific Recommendations")
                    recommendations = {
                        "Technology": [
                            "Focus on latest tech trends",
                            "Build open-source contributions",
                            "Participate in tech communities"
                        ],
                        "Finance": [
                            "Learn financial domain",
                            "Study security protocols",
                            "Understand regulatory frameworks"
                        ],
                        "Healthcare": [
                            "Study HIPAA compliance",
                            "Learn healthcare systems",
                            "Focus on data privacy"
                        ],
                        "E-commerce": [
                            "Study scalable architectures",
                            "Learn about user experience",
                            "Understand payment systems"
                        ],
                        "Consulting": [
                            "Develop presentation skills",
                            "Build domain expertise",
                            "Practice problem-solving"
                        ]
                    }
                    
                    for rec in recommendations[industry]:
                        st.markdown(f"""
                            <div style='padding: 10px; border-radius: 5px; margin: 5px 0; 
                            background-color: #1E1E1E; border-left: 5px solid #00b4c4'>
                                • {rec}
                            </div>
                        """, unsafe_allow_html=True)
                
                except Exception as e:
                    st.error(f"Error in industry fit analysis: {str(e)}")

elif selected_page == "PDF Viewer":
    st.title("PDF Viewer & Editor")
    
    # Initialize session state for PDF editing
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 0
    if 'pdf_text' not in st.session_state:
        st.session_state.pdf_text = {}
    if 'edited_pages' not in st.session_state:
        st.session_state.edited_pages = set()
    
    uploaded_file = st.file_uploader(
        label="Upload your PDF",
        type="pdf"
    )
    
    if uploaded_file:
        # Create data directory if it doesn't exist
        os.makedirs("data", exist_ok=True)
        
        # Save the file
        file_path = os.path.join("data", uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Store the file path in session state
        st.session_state.pdf_path = file_path
        
        # Create columns for the layout
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.write("### PDF Preview")
            # Display PDF preview
            with open(file_path, "rb") as pdf_file:
                base64_pdf = base64.b64encode(pdf_file.read()).decode('utf-8')
                pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
                st.markdown(pdf_display, unsafe_allow_html=True)
        
        with col2:
            st.write("### PDF Tools")
            
            # PDF Information
            try:
                pdf = fitz.open(file_path)
                st.write(f"📄 Total Pages: {len(pdf)}")
                
                # Page Navigation
                st.write("#### Navigate Pages")
                col_prev, col_curr, col_next = st.columns([1, 2, 1])
                with col_prev:
                    if st.button("◀️ Previous"):
                        st.session_state.current_page = max(0, st.session_state.current_page - 1)
                with col_curr:
                    st.session_state.current_page = st.number_input(
                        "Page", min_value=0, max_value=len(pdf)-1, 
                        value=st.session_state.current_page
                    )
                with col_next:
                    if st.button("Next ▶️"):
                        st.session_state.current_page = min(len(pdf)-1, st.session_state.current_page + 1)
                
                # PDF Operations
                st.write("#### Edit Operations")
                operation = st.selectbox(
                    "Select Operation",
                    ["Extract Text", "Add Text", "Add Image", "Rotate Page", "Delete Page"]
                )
                
                if operation == "Extract Text":
                    page = pdf[st.session_state.current_page]
                    text = page.get_text()
                    st.text_area("Extracted Text", text, height=200)
                    if st.button("Copy Text"):
                        st.write("Text copied to clipboard!")
                        pyperclip.copy(text)
                
                elif operation == "Add Text":
                    text_to_add = st.text_input("Enter text to add")
                    x = st.slider("X Position", 0, 600, 100)
                    y = st.slider("Y Position", 0, 800, 100)
                    font_size = st.slider("Font Size", 8, 72, 12)
                    if st.button("Add Text"):
                        try:
                            page = pdf[st.session_state.current_page]
                            page.insert_text((x, y), text_to_add, fontsize=font_size)
                            pdf.save(file_path)
                            st.success("Text added successfully!")
                            st.experimental_rerun()
                        except Exception as e:
                            st.error(f"Error adding text: {str(e)}")
                
                elif operation == "Add Image":
                    uploaded_image = st.file_uploader("Upload Image", type=['png', 'jpg', 'jpeg'])
                    if uploaded_image:
                        image_path = os.path.join("data", uploaded_image.name)
                        with open(image_path, "wb") as f:
                            f.write(uploaded_image.getbuffer())
                        
                        x = st.slider("X Position", 0, 600, 100)
                        y = st.slider("Y Position", 0, 800, 100)
                        width = st.slider("Width", 50, 500, 200)
                        height = st.slider("Height", 50, 500, 200)
                        
                        if st.button("Add Image"):
                            try:
                                page = pdf[st.session_state.current_page]
                                page.insert_image(
                                    rect=(x, y, x+width, y+height),
                                    filename=image_path
                                )
                                pdf.save(file_path)
                                st.success("Image added successfully!")
                                st.experimental_rerun()
                            except Exception as e:
                                st.error(f"Error adding image: {str(e)}")
                
                elif operation == "Rotate Page":
                    rotation = st.selectbox(
                        "Select Rotation",
                        [0, 90, 180, 270]
                    )
                    if st.button("Rotate"):
                        try:
                            page = pdf[st.session_state.current_page]
                            page.set_rotation(rotation)
                            pdf.save(file_path)
                            st.success("Page rotated successfully!")
                            st.experimental_rerun()
                        except Exception as e:
                            st.error(f"Error rotating page: {str(e)}")
                
                elif operation == "Delete Page":
                    if st.button("Delete Current Page"):
                        if len(pdf) > 1:
                            try:
                                pdf.delete_page(st.session_state.current_page)
                                pdf.save(file_path)
                                st.session_state.current_page = max(0, st.session_state.current_page - 1)
                                st.success("Page deleted successfully!")
                                st.experimental_rerun()
                            except Exception as e:
                                st.error(f"Error deleting page: {str(e)}")
                        else:
                            st.error("Cannot delete the last page!")
                
                # Export Options
                st.write("#### Export Options")
                export_format = st.selectbox(
                    "Export Format",
                    ["PDF", "Images"]
                )
                
                if export_format == "PDF":
                    if st.button("Export Edited PDF"):
                        try:
                            export_path = os.path.join("data", f"edited_{uploaded_file.name}")
                            pdf.save(export_path)
                            with open(export_path, "rb") as f:
                                st.download_button(
                                    label="📥 Download Edited PDF",
                                    data=f,
                                    file_name=f"edited_{uploaded_file.name}",
                                    mime="application/pdf"
                                )
                        except Exception as e:
                            st.error(f"Error exporting PDF: {str(e)}")
                
                elif export_format == "Images":
                    if st.button("Export Pages as Images"):
                        try:
                            # Create a ZIP file containing all pages as images
                            zip_path = os.path.join("data", f"{uploaded_file.name}_images.zip")
                            with zipfile.ZipFile(zip_path, 'w') as zipf:
                                for i in range(len(pdf)):
                                    page = pdf[i]
                                    pix = page.get_pixmap()
                                    img_path = os.path.join("data", f"page_{i+1}.png")
                                    pix.save(img_path)
                                    zipf.write(img_path, f"page_{i+1}.png")
                                    os.remove(img_path)
                            
                            with open(zip_path, "rb") as f:
                                st.download_button(
                                    label="📥 Download Pages as Images",
                                    data=f,
                                    file_name=f"{uploaded_file.name}_images.zip",
                                    mime="application/zip"
                                )
                        except Exception as e:
                            st.error(f"Error exporting images: {str(e)}")
                
                pdf.close()
            
            except Exception as e:
                st.error(f"Error processing PDF: {str(e)}")
    
    elif st.session_state.pdf_path and os.path.exists(st.session_state.pdf_path):
        # Display previously uploaded PDF (same code as above)
        with open(st.session_state.pdf_path, "rb") as pdf_file:
            base64_pdf = base64.b64encode(pdf_file.read()).decode('utf-8')
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)
    else:
        st.info("Please upload a PDF file to view and edit it here.")

elif selected_page == "Career Coach":
    st.title("👨‍🏫 Personal Career Coach")
    
    # Initialize user profile if not exists
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = {
            'job_role': '',
            'goals': [],
            'achievements': [],
            'improvement_areas': [],
            'skills': [],
            'skill_level': 'Beginner',
            'available_time': 5,
            'experience_level': 'Beginner',
            'preferences': {},
            'completed_games': 0,
            'total_score': 0
        }
    
    # Ensure all required fields exist
    required_fields = {
        'job_role': '',
        'goals': [],
        'achievements': [],
        'improvement_areas': [],
        'skills': [],
        'skill_level': 'Beginner',
        'available_time': 5,
        'experience_level': 'Beginner',
        'preferences': {},
        'completed_games': 0,
        'total_score': 0
    }
    
    # Add any missing fields with default values
    for field, default_value in required_fields.items():
        if field not in st.session_state.user_profile:
            st.session_state.user_profile[field] = default_value
    
    # Profile Setup
    with st.expander("🎯 Your Profile", expanded='user_profile' not in st.session_state):
        st.session_state.user_profile['job_role'] = st.text_input(
            "What's your target job role?",
            value=st.session_state.user_profile.get('job_role', '')
        )
        
        goals = st.text_area(
            "What are your career goals? (One per line)",
            value='\n'.join(st.session_state.user_profile.get('goals', []))
        )
        st.session_state.user_profile['goals'] = [g.strip() for g in goals.split('\n') if g.strip()]
        
        achievements = st.text_area(
            "Recent achievements? (One per line)",
            value='\n'.join(st.session_state.user_profile.get('achievements', []))
        )
        st.session_state.user_profile['achievements'] = [a.strip() for a in achievements.split('\n') if a.strip()]
        
        improvements = st.text_area(
            "Areas you want to improve? (One per line)",
            value='\n'.join(st.session_state.user_profile.get('improvement_areas', []))
        )
        st.session_state.user_profile['improvement_areas'] = [i.strip() for i in improvements.split('\n') if i.strip()]
        
        skills = st.text_area(
            "Your current skills? (One per line)",
            value='\n'.join(st.session_state.user_profile.get('skills', []))
        )
        st.session_state.user_profile['skills'] = [s.strip() for s in skills.split('\n') if s.strip()]
        
        st.session_state.user_profile['skill_level'] = st.select_slider(
            "Your overall skill level:",
            options=['Beginner', 'Intermediate', 'Advanced', 'Expert'],
            value=st.session_state.user_profile.get('skill_level', 'Beginner')
        )
        
        st.session_state.user_profile['available_time'] = st.slider(
            "Hours available per week for skill development:",
            min_value=1,
            max_value=40,
            value=st.session_state.user_profile.get('available_time', 5)
        )
    
    if st.session_state.user_profile['job_role']:
        # Daily Motivation
        st.subheader("🌟 Daily Motivation")
        if st.button("Get Today's Motivation"):
            with st.spinner("Generating your daily motivation..."):
                motivation = career_coach.generate_daily_motivation(st.session_state.user_profile)
                if motivation:
                    st.info(motivation['message'])
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**Today's Focus:**", motivation['focus_area'])
                        st.write("**Quick Tip:**", motivation['quick_tip'])
                    with col2:
                        st.write("**Inspiring Quote:**", motivation['quote'])
                        st.write("**Action Item:**", motivation['action_item'])
        
        # Weekly Challenge
        st.subheader("💪 Weekly Skill Challenge")
        if st.button("Get This Week's Challenge"):
            with st.spinner("Creating your weekly challenge..."):
                challenge = career_coach.generate_weekly_challenge(st.session_state.user_profile)
                if challenge:
                    st.success(f"**{challenge['challenge_name']}**")
                    st.write(challenge['description'])
                    
                    st.write("**Daily Tasks:**")
                    for task in challenge['daily_tasks']:
                        with st.expander(f"📅 {task['day']}"):
                            st.write(f"**Task:** {task['task']}")
                            st.write(f"**Time Required:** {task['time_required']}")
                            st.write(f"**Resources:** {task['resources']}")
                    
                    st.write("**Success Criteria:**", challenge['success_criteria'])
                    st.write("**Bonus Challenge:**", challenge['bonus_challenge'])
                    st.write("**Expected Outcome:**", challenge['expected_outcome'])
        
        # Monthly Review
        st.subheader("📊 Monthly Progress Review")
        if st.button("Generate Monthly Review"):
            # Simulate monthly data (in real app, this would come from user's activity)
            monthly_data = {
                'completed_challenges': ['Python Mastery', 'Communication Skills', 'Project Management'],
                'achievements': ['Completed 5 projects', 'Learned 3 new technologies'],
                'skills_improved': ['Python', 'Communication', 'Leadership'],
                'time_invested': 45
            }
            
            with st.spinner("Analyzing your monthly progress..."):
                review = career_coach.generate_monthly_review(st.session_state.user_profile, monthly_data)
                if review:
                    st.write("**Overall Summary:**", review['summary'])
                    
                    st.write("**Key Achievements:**")
                    for achievement in review['key_achievements']:
                        st.write(f"✅ {achievement}")
                    
                    st.write("**Areas of Growth:**")
                    for area in review['areas_of_growth']:
                        with st.expander(f"📈 {area['skill']}"):
                            st.write(f"**Progress:** {area['progress']}")
                            st.write(f"**Next Steps:** {area['next_steps']}")
                    
                    st.write("**Insights:**")
                    for insight in review['insights']:
                        st.write(f"💡 {insight}")
                    
                    st.write("**Next Month Focus:**")
                    st.write(f"**Primary Goal:** {review['next_month_focus']['primary_goal']}")
                    st.write("**Action Items:**")
                    for item in review['next_month_focus']['action_items']:
                        st.write(f"👉 {item}")
        
        # Action Plan
        st.subheader("📋 Custom Action Plan")
        if st.button("Create Action Plan"):
            with st.spinner("Creating your personalized action plan..."):
                plan = career_coach.generate_action_plan(
                    st.session_state.user_profile,
                    st.session_state.user_profile['goals']
                )
                if plan:
                    st.write(f"**{plan['plan_name']}**")
                    st.write(plan['overview'])
                    
                    st.write("**Milestones:**")
                    for milestone in plan['milestones']:
                        with st.expander(f"🎯 {milestone['name']} ({milestone['timeframe']})"):
                            for task in milestone['tasks']:
                                st.write(f"**Task:** {task['task']}")
                                st.write(f"**Priority:** {task['priority']}")
                                st.write(f"**Resources:** {task['resources']}")
                                st.write(f"**Success Criteria:** {task['success_criteria']}")
                    
                    st.write("**Success Metrics:**")
                    for metric in plan['success_metrics']:
                        st.write(f"📊 {metric}")
                    
                    st.write("**Potential Challenges & Solutions:**")
                    for challenge in plan['potential_challenges']:
                        with st.expander(f"🚧 {challenge['challenge']}"):
                            st.write(f"**Solution:** {challenge['solution']}")
        
        # Progress Feedback
        st.subheader("📝 Progress Feedback")
        if st.button("Get Progress Feedback"):
            # Simulate progress data (in real app, this would come from user's activity)
            progress_data = {
                'recent_progress': ['Completed Python course', 'Started team project'],
                'completed_tasks': ['Task 1', 'Task 2', 'Task 3'],
                'challenges': ['Time management', 'Technical complexity'],
                'time_spent': 20
            }
            
            with st.spinner("Analyzing your progress..."):
                feedback = career_coach.generate_progress_feedback(st.session_state.user_profile, progress_data)
                if feedback:
                    st.write("**Overall Assessment:**", feedback['overall_assessment'])
                    
                    st.write("**Key Observations:**")
                    for obs in feedback['key_observations']:
                        with st.expander(f"👀 {obs['observation']}"):
                            st.write(f"**Impact:** {obs['impact']}")
                            st.write(f"**Recommendation:** {obs['recommendation']}")
                    
                    st.write("**Strengths:**")
                    for strength in feedback['strengths']:
                        with st.expander(f"💪 {strength['strength']}"):
                            st.write(f"**How to Leverage:** {strength['how_to_leverage']}")
                    
                    st.write("**Areas to Improve:**")
                    for area in feedback['improvement_areas']:
                        with st.expander(f"📈 {area['area']}"):
                            st.write(f"**Why Important:** {area['why_important']}")
                            st.write(f"**How to Improve:** {area['how_to_improve']}")
                    
                    st.write("**Next Steps:**")
                    for step in feedback['next_steps']:
                        st.write(f"👉 {step}")
                    
                    st.info(feedback['motivation'])
    else:
        st.info("👆 Please set up your profile to get started with your personal career coach!")

elif selected_page == "Interview Game":
    st.title("🎮 Interview Preparation Game")
    st.write("Welcome to the fun and engaging way to prepare for your interviews!")
    
    # Initialize session state for game
    if 'game_state' not in st.session_state:
        st.session_state.game_state = {
            'current_mode': None,
            'current_question': 0,
            'current_challenge': 0,
            'score': 0,
            'total_questions': 5,
            'questions': None,
            'scenario': None,
            'debug': None,
            'system_design': None,
            'feedback': []
        }
    
    # Interview game setup
    st.write("### Setup Your Interview Practice")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        job_role = st.text_input("What's your target job role?", placeholder="e.g., Python Developer")
    
    with col2:
        difficulty = st.selectbox(
            "Choose difficulty level",
            list(interview_game.get_difficulty_levels().keys()),
            format_func=lambda x: interview_game.get_difficulty_levels()[x]
        )
    
    with col3:
        company = st.text_input(
            "Target Company (Optional)",
            placeholder="e.g., Google, Microsoft, etc.",
            help="Enter a company name to get company-specific interview preparation"
        )
    
    # Pass company info to game state
    if job_role:
        st.session_state.game_state = {
            'current_mode': st.session_state.game_state.get('current_mode'),
            'job_role': job_role,
            'difficulty': difficulty,
            'company': company if company.strip() else None
        }
    
    # Game mode selection
    st.write("### Choose Your Challenge Mode")
    
    # Define game modes with their details
    game_modes = [
        {
            "mode": "quiz",
            "title": "Quiz Mode",
            "icon": "📝",
            "description": "Test your knowledge with multiple-choice questions tailored to your job role and difficulty level."
        },
        {
            "mode": "rapid_fire",
            "title": "Rapid Fire",
            "icon": "⚡",
            "description": "Quick-paced questions to test your quick thinking and knowledge under time pressure."
        },
        {
            "mode": "debug",
            "title": "Debug Challenge",
            "icon": "🔍",
            "description": "Find and fix bugs in code snippets. Perfect for improving your debugging skills."
        },
        {
            "mode": "system_design",
            "title": "System Design",
            "icon": "🏗️",
            "description": "Design scalable systems and architectures. Great for senior roles and system design interviews."
        },
        {
            "mode": "coding",
            "title": "Code Challenge",
            "icon": "💻",
            "description": "Solve coding problems with our integrated code editor, test cases, and real-time feedback."
        },
        {
            "mode": "scenario",
            "title": "Scenario Challenge",
            "icon": "📋",
            "description": "Practice responding to real-world scenarios and behavioral interview questions."
        },
        {
            "mode": "practice_websites",
            "title": "Practice Websites",
            "icon": "🌐",
            "description": "Discover curated websites and platforms to enhance your skills through hands-on practice."
        }
    ]

    # Create three columns for the game mode cards
    cols = st.columns(3)
    
    # Display game modes in cards
    for i, mode in enumerate(game_modes):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="game-card">
                <div class="mode-icon">{mode['icon']}</div>
                <h3>{mode['title']}</h3>
                <p>{mode['description']}</p>
                <button class="start-button" onclick="document.getElementById('{mode['mode']}_button').click()">Start Game</button>
            </div>
            """, unsafe_allow_html=True)
            
            # Hidden button for handling clicks
            if st.button("Start Game", key=f"{mode['mode']}_button", type="primary", use_container_width=True):
                if job_role:
                    st.session_state.game_state['current_mode'] = mode['mode']
                    st.experimental_rerun()

    # Handle practice websites mode
    if st.session_state.game_state.get('current_mode') == "practice_websites":
        websites_data = interview_game.get_practice_websites(st.session_state.game_state['job_role'])
        
        if websites_data["found"]:
            st.write(f"### 🎯 Practice Websites for {websites_data['matched_role'].title()}")
        else:
            st.write(f"### 🎯 Recommended Resources for {st.session_state.game_state['job_role'].title()}")
        
        # Display all website categories
        for category, sites in websites_data["websites"].items():
            st.write(f"#### {category.replace('_', ' ').title()}")
            
            for site in sites:
                with st.expander(f"{site['name']}"):
                    st.write(f"**Description:** {site['description']}")
                    st.markdown(f"**[Visit Website]({site['url']})**", unsafe_allow_html=True)
            
            st.write("")  # Add spacing between categories
    
    # Game interface based on mode
    elif st.session_state.game_state['current_mode'] == "rapid":
        # Initialize rapid fire if not already done
        if 'questions' not in st.session_state.game_state:
            with st.spinner("Generating rapid-fire questions..."):
                st.session_state.game_state['questions'] = interview_game.generate_rapid_fire(
                    job_role=st.session_state.game_state['job_role'],
                    difficulty=st.session_state.game_state['difficulty']
                )
                st.session_state.game_state['current_question'] = 0
                st.session_state.game_state['score'] = 0
                st.session_state.game_state['submitted'] = False
        
        if 'questions' in st.session_state.game_state and st.session_state.game_state['questions']:
            current_q = st.session_state.game_state.get('current_question', 0)
            questions = st.session_state.game_state['questions']
            
            # Show progress
            st.progress(current_q / 10)
            st.write(f"Question {current_q + 1} of 10")
            
            if current_q < 10 and current_q < len(questions):
                question = questions[current_q]
                
                # Display question
                st.write("### " + question['question'])
                
                # Display timer
                time_limit = question.get('time_limit', 30)
                st.write(f"⏱️ Time Limit: {time_limit} seconds")
                
                # Answer input
                user_answer = st.text_input(
                    "Your Answer:",
                    key=f"rapid_q_{current_q}",
                    help=f"You have {time_limit} seconds to answer"
                )
                
                if not st.session_state.game_state.get('submitted', False):
                    if st.button("Submit Answer", key=f"submit_{current_q}"):
                        st.session_state.game_state['submitted'] = True
                        
                        # Check answer
                        result = interview_game.check_rapid_fire_answer(question, user_answer)
                        
                        if result:
                            if result['correct']:
                                st.success("🎯 Correct!")
                                st.session_state.game_state['score'] += result['score']
                            else:
                                st.error("❌ Not quite right")
                            
                            st.write(f"**Score:** {result['score']:.1f}/100")
                            
                            # Always show the correct answer first
                            st.write(f"**Correct Answer:** {result['correct_answer']}")
                            
                            # Then show explanation
                            st.write(f"**Explanation:** {result['explanation']}")
                            
                            # Show what was missing if applicable
                            if result['missing'] and result['missing'].lower() not in ['none', 'n/a', '']:
                                st.write(f"**What was missing:** {result['missing']}")
                
                # Next question button (only show after submitting)
                if st.session_state.game_state.get('submitted', False):
                    if st.button("Next Question", key=f"next_{current_q}"):
                        st.session_state.game_state['current_question'] += 1
                        st.session_state.game_state['submitted'] = False
                        st.cache_data.clear()
                        st.cache_resource.clear()
            
            else:
                # All questions completed
                final_score = st.session_state.game_state['score'] / 10
                st.success("🎉 Rapid Fire Round Completed!")
                st.balloons()
                st.write(f"### Final Score: {final_score:.1f}/100")
                
                # Display performance message
                if final_score >= 90:
                    st.write("🏆 Outstanding! Your rapid-fire skills are exceptional!")
                elif final_score >= 70:
                    st.write("🌟 Great job! You have solid quick-thinking abilities!")
                elif final_score >= 50:
                    st.write("👍 Good effort! Keep practicing to improve your speed and accuracy.")
                else:
                    st.write("📚 Keep learning! Focus on quick recall of core concepts.")
                
                if st.button("Try Another Round"):
                    st.session_state.game_state['questions'] = None
                    st.session_state.game_state['current_question'] = 0
                    st.session_state.game_state['score'] = 0
                    st.session_state.game_state['submitted'] = False
                    st.cache_data.clear()
                    st.cache_resource.clear()
    
    elif st.session_state.game_state['current_mode'] == "quiz":
        if 'questions' not in st.session_state.game_state:
            with st.spinner("Generating quiz questions..."):
                st.session_state.game_state['questions'] = interview_game.generate_quiz_questions(
                    job_role=st.session_state.game_state['job_role'],
                    difficulty=st.session_state.game_state['difficulty']
                )
                st.session_state.game_state['current_question'] = 0
                st.session_state.game_state['score'] = 0
                st.session_state.game_state['total_questions'] = 5
                st.session_state.game_state['submitted'] = False

        if st.session_state.game_state['questions']:
            current_q = st.session_state.game_state['current_question']
            
            # Show progress
            st.progress((current_q) / 5)
            st.write(f"Question {current_q + 1} of 5")
            
            if current_q < 5:
                question = st.session_state.game_state['questions'][current_q]
                
                st.write(f"### Question {current_q + 1}")
                st.write(question['question'])
                
                # Display options
                selected_option = st.radio(
                    "Choose your answer:",
                    question['options'],
                    key=f"quiz_q_{current_q}"
                )
                
                # Submit button
                if not st.session_state.game_state.get('submitted', False):
                    if st.button("Submit Answer", key=f"submit_{current_q}"):
                        st.session_state.game_state['submitted'] = True
                        
                        if selected_option == question['correct_answer']:
                            st.success("🎉 Correct!")
                            st.session_state.game_state['score'] += 1
                        else:
                            st.error("❌ Incorrect!")
                            st.write(f"The correct answer was: {question['correct_answer']}")
                        
                        st.write(f"**Explanation:** {question['explanation']}")
                        st.write(f"**Fun Fact:** {question['fun_fact']}")
                
                # Next question button (only show after submitting)
                if st.session_state.game_state.get('submitted', False):
                    if st.button("Next Question", key=f"next_{current_q}"):
                        st.session_state.game_state['current_question'] += 1
                        st.session_state.game_state['submitted'] = False
                        st.cache_data.clear()
                        st.cache_resource.clear()
            
            # Show final score after all questions
            if current_q >= 5:
                score_percentage = (st.session_state.game_state['score'] / 5) * 100
                st.success("🎉 Quiz Completed!")
                st.balloons()
                st.write(f"### Your Score: {score_percentage:.1f}%")
                
                # Display performance message
                if score_percentage >= 90:
                    st.write("🏆 Outstanding! You're more than ready for your interview!")
                elif score_percentage >= 70:
                    st.write("🌟 Great job! Just a bit more practice and you'll be perfect!")
                elif score_percentage >= 50:
                    st.write("👍 Good effort! Keep practicing to improve your knowledge.")
                else:
                    st.write("📚 Keep learning! Review the concepts and try again.")
                
                if st.button("Play Again"):
                    # Reset game state
                    st.session_state.game_state = {
                        'current_mode': None,
                        'job_role': st.session_state.game_state['job_role'],
                        'difficulty': st.session_state.game_state['difficulty']
                    }
                    st.cache_data.clear()
                    st.cache_resource.clear()
    
    elif st.session_state.game_state['current_mode'] == "coding":
        st.write("💻 Coding Challenge")
        
        # Initialize coding challenge if not already done
        if 'challenge' not in st.session_state.game_state:
            with st.spinner("Generating coding challenge..."):
                st.session_state.game_state['challenge'] = interview_game.generate_coding_challenge(
                    job_role=st.session_state.game_state['job_role'],
                    difficulty=st.session_state.game_state['difficulty']
                )
        
        challenge = st.session_state.game_state.get('challenge')
        if challenge:
            # Display challenge details
            st.write("### 📝 Problem Description")
            st.write(challenge['description'])
            
            # Create tabs for different sections
            info_tab, editor_tab, results_tab = st.tabs(["Problem Info", "Code Editor", "Results"])
            
            with info_tab:
                st.write("#### Input Format")
                st.info(challenge['input_format'])
                
                st.write("#### Output Format")
                st.info(challenge['output_format'])
                
                st.write("#### Constraints")
                for constraint in challenge['constraints']:
                    st.write(f"• {constraint}")
                
                st.write("#### Example Test Cases")
                for i, case in enumerate(challenge['example_cases'], 1):
                    with st.expander(f"Test Case {i}"):
                        st.write("Input:")
                        st.code(case['input'])
                        st.write("Expected Output:")
                        st.code(case['output'])
            
            with editor_tab:
                # Code editor section
                if 'current_code' not in st.session_state.game_state:
                    st.session_state.game_state['current_code'] = challenge['function_template']
                
                st.write("### 👨‍💻 Code Editor")
                
                # Add language selector
                language = st.selectbox(
                    "Select Language",
                    ["python", "javascript", "java", "cpp"],
                    key="code_language"
                )
                
                # Code editor with syntax highlighting
                user_code = st.text_area(
                    "Write your code here:",
                    value=st.session_state.game_state['current_code'],
                    height=300,
                    key="code_editor"
                )
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button("Run Code"):
                        st.session_state.game_state['current_code'] = user_code
                        st.session_state.game_state['last_run'] = interview_game.evaluate_code_solution(
                            challenge, user_code, language
                        )
                
                with col2:
                    if st.button("Reset Code"):
                        st.session_state.game_state['current_code'] = challenge['function_template']
                        st.experimental_rerun()
            
            with results_tab:
                if 'last_run' in st.session_state.game_state:
                    results = st.session_state.game_state['last_run']
                    
                    # Display test results
                    st.write("### 🎯 Test Results")
                    st.write(f"Passed: {results['passed']}/{results['total']} tests")
                    
                    # Display each test case result
                    for i, test in enumerate(results['test_results'], 1):
                        with st.expander(f"Test Case {i} - {'✅ Passed' if test['passed'] else '❌ Failed'}"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write("Input:")
                                st.code(test['input'])
                                st.write("Expected Output:")
                                st.code(test['expected'])
                            with col2:
                                st.write("Your Output:")
                                st.code(test['actual'])
                                st.write(f"Execution Time: {test['execution_time']:.3f}s")
                    
                    # Display errors if any
                    if results['errors']:
                        st.write("### ❌ Errors")
                        for error in results['errors']:
                            st.error(error)
                    
                    # Display style issues
                    if results['style_issues']:
                        st.write("### 🎨 Style Issues")
                        for issue in results['style_issues']:
                            st.warning(issue)
                    
                    # Display optimization tips
                    if results['optimization_tips']:
                        st.write("### 🚀 Optimization Tips")
                        for tip in results['optimization_tips']:
                            st.info(tip)
                    
                    # Show sample solution button
                    if results['passed'] == results['total']:
                        st.success("🎉 Congratulations! All test cases passed!")
                        if st.button("View Sample Solution"):
                            st.write("### ✨ Sample Solution")
                            st.code(challenge['sample_solution'])
    
    elif st.session_state.game_state['current_mode'] == "scenario":
        # Initialize scenario if not already done
        if 'scenario' not in st.session_state.game_state:
            with st.spinner("Generating scenario challenge..."):
                st.session_state.game_state['scenario'] = interview_game.generate_scenario_challenge(
                    job_role=st.session_state.game_state['job_role'],
                    difficulty=st.session_state.game_state['difficulty']
                )
        
        scenario = st.session_state.game_state['scenario']
        if scenario:
            # Display scenario description
            st.write("### 🌟 Real-world Scenario")
            st.info(scenario['scenario'])
            
            # Display requirements
            if 'requirements' in scenario:
                st.write("### 📋 Requirements")
                for i, req in enumerate(scenario['requirements'], 1):
                    st.write(f"{i}. {req}")
            
            # Display constraints
            if 'constraints' in scenario:
                st.write("### ⚠️ Constraints")
                for i, con in enumerate(scenario['constraints'], 1):
                    st.write(f"{i}. {con}")
            
            # Display evaluation criteria
            if 'evaluation_criteria' in scenario:
                with st.expander("📊 Evaluation Criteria"):
                    for i, crit in enumerate(scenario['evaluation_criteria'], 1):
                        st.write(f"{i}. {crit}")
            
            # Display time limit
            if 'time_limit' in scenario:
                st.info(f"⏱️ Time Limit: {scenario['time_limit']} minutes")
            
            # Solution input area
            st.write("### Your Solution")
            user_solution = st.text_area(
                "Enter your solution:",
                height=300,
                key=f"scenario_solution"
            )
            
            # Submit button
            if st.button("Submit Solution"):
                if user_solution.strip():
                    with st.spinner("Evaluating your solution..."):
                        result = interview_game.evaluate_scenario_solution(scenario, user_solution)
                        
                        if result:
                            # Display score and feedback
                            score = float(result.get('score', 0))
                            if score >= 80:
                                st.success(f"🌟 Excellent! Score: {score}/100")
                            elif score >= 60:
                                st.warning(f"👍 Good attempt! Score: {score}/100")
                            else:
                                st.error(f"Score: {score}/100")
                            
                            # Display detailed feedback
                            st.write("### 📝 Feedback")
                            st.write(result.get('feedback', ''))
                            
                            # Display strengths
                            if 'strengths' in result:
                                with st.expander("💪 Strengths"):
                                    for strength in result['strengths']:
                                        st.write(f"• {strength}")
                            
                            # Display areas for improvement
                            if 'improvements' in result:
                                with st.expander("🎯 Areas for Improvement"):
                                    for improvement in result['improvements']:
                                        st.write(f"• {improvement}")
                            
                            # Display sample solution after submission
                            if 'sample_solution' in scenario:
                                with st.expander("✨ Sample Solution"):
                                    st.write(scenario['sample_solution'])
                else:
                    st.error("Please provide a solution before submitting.")
            
            # Show restart button after submission
            if st.session_state.game_state.get('submitted', False):
                if st.button("Try Another Scenario"):
                    st.session_state.game_state['scenario'] = None
                    st.session_state.game_state['submitted'] = False
                    st.cache_data.clear()
                    st.cache_resource.clear()
    
    elif st.session_state.game_state['current_mode'] == "debug":
        # Initialize debug challenges if not already done
        if 'debug' not in st.session_state.game_state:
            with st.spinner("Generating debug challenges..."):
                debug_data = interview_game.generate_debug_challenges(
                    job_role=st.session_state.game_state['job_role'],
                    difficulty=st.session_state.game_state['difficulty']
                )
                if debug_data:
                    st.session_state.game_state['debug'] = debug_data
                    st.session_state.game_state['current_challenge'] = 0
                    st.session_state.game_state['score'] = 0
                    st.session_state.game_state['submitted'] = False
                else:
                    st.error("Failed to generate debug challenges. Please try again.")
                    st.session_state.game_state['current_mode'] = None
        
        if 'debug' in st.session_state.game_state and st.session_state.game_state['debug']:
            current_c = st.session_state.game_state.get('current_challenge', 0)
            challenges = st.session_state.game_state['debug']
            
            # Show progress
            st.progress((current_c) / 5)
            st.write(f"Challenge {current_c + 1} of 5")
            
            if current_c < 5 and current_c < len(challenges):
                challenge = challenges[current_c]
                
                # Display challenge
                st.write("### 🐛 Debug Challenge")
                st.info(challenge['description'])
                
                # Display buggy code
                st.code(challenge['buggy_code'], language='python')
                
                # Display hints in expander
                with st.expander("🔍 Hints"):
                    for hint in challenge['hints']:
                        st.write(f"- {hint}")
                
                # Solution input
                user_solution = st.text_area(
                    "Enter your corrected code:",
                    height=200,
                    key=f"debug_solution_{current_c}"
                )
                
                # Submit button
                if not st.session_state.game_state.get('submitted', False):
                    if st.button("Submit Fix", key=f"submit_debug_{current_c}"):
                        st.session_state.game_state['submitted'] = True
                        
                        # Evaluate solution
                        result = interview_game.evaluate_debug_solution(challenge, user_solution)
                        
                        if result:
                            # Display score and correctness
                            score = float(result['score'])
                            if result['is_correct']:
                                st.success(f"🎯 Great Job! Score: {score}/100")
                            else:
                                st.warning(f"Almost there! Score: {score}/100")
                            
                            st.session_state.game_state['score'] += score
                            
                            # Display feedback
                            st.write("### Feedback")
                            st.write(result['feedback'])
                            
                            # Show the user's solution with syntax highlighting
                            st.write("**Your Solution:**")
                            st.code(user_solution, language='python')
                            
                            # Show correct solution if available
                            if result.get('solution'):
                                with st.expander("✨ View Solution"):
                                    st.code(result['solution'], language='python')
                                    if result.get('explanation'):
                                        st.write("**Explanation:**")
                                        st.write(result['explanation'])
                            
                            # Show best practices
                            with st.expander("📚 Best Practices"):
                                for practice in result['best_practices']:
                                    st.write(f"- {practice}")
                
                # Next challenge button (only show after submitting)
                if st.session_state.game_state.get('submitted', False):
                    if st.button("Next Challenge", key=f"next_debug_{current_c}"):
                        st.session_state.game_state['current_challenge'] += 1
                        st.session_state.game_state['submitted'] = False
                        st.cache_data.clear()
                        st.cache_resource.clear()
            
            else:
                # All challenges completed
                st.success("🎉 Congratulations! You've completed all debug challenges!")
                final_score = st.session_state.game_state['score'] / 5  # Average score
                st.write(f"Final Score: {final_score:.2f}/100")
                
                # Display performance message
                if final_score >= 90:
                    st.write("🏆 Outstanding! You show excellent debugging skills!")
                elif final_score >= 70:
                    st.write("🌟 Great job! You have a solid grasp of debugging principles!")
                elif final_score >= 50:
                    st.write("👍 Good effort! Keep practicing your debugging skills.")
                else:
                    st.write("📚 Keep learning! Focus on understanding error handling and code optimization.")
                
                if st.button("Play Again"):
                    # Reset game state
                    st.session_state.game_state = {
                        'current_mode': None,
                        'job_role': st.session_state.game_state['job_role'],
                        'difficulty': st.session_state.game_state['difficulty']
                    }
                    st.cache_data.clear()
                    st.cache_resource.clear()
    
    elif st.session_state.game_state['current_mode'] == "system_design":
        if 'challenge' not in st.session_state.game_state:
            with st.spinner("Generating system design challenge..."):
                st.session_state.game_state['challenge'] = interview_game.generate_system_design_challenge(
                    job_role=st.session_state.game_state['job_role'],
                    difficulty=st.session_state.game_state['difficulty']
                )

        if st.session_state.game_state['challenge']:
            challenge = st.session_state.game_state['challenge']
            
            # Display challenge
            st.write("### 🏗️ System Design Challenge")
            
            # Display the challenge description
            st.write("#### Problem Statement")
            st.write(challenge['description'])
            
            # Display requirements
            if 'requirements' in challenge:
                st.write("#### 📋 Requirements")
                for i, req in enumerate(challenge['requirements'], 1):
                    st.write(f"{i}. {req}")
            
            # Display constraints
            if 'constraints' in challenge:
                st.write("#### 🔒 Constraints")
                for i, con in enumerate(challenge['constraints'], 1):
                    st.write(f"{i}. {con}")
            
            # Display evaluation criteria
            if 'evaluation_criteria' in challenge:
                with st.expander("📊 Evaluation Criteria"):
                    for i, crit in enumerate(challenge['evaluation_criteria'], 1):
                        st.write(f"{i}. {crit}")
            
            # Display time limit if specified
            if 'time_limit' in challenge:
                st.info(f"⏱️ Time Limit: {challenge['time_limit']} minutes")
            
            # Solution input area
            st.write("### Your Solution")
            user_solution = st.text_area(
                "Describe your system design solution in detail. Consider all requirements and constraints.",
                height=300
            )
            
            # Submit button
            if st.button("Submit Solution"):
                if user_solution.strip():
                    with st.spinner("Evaluating your solution..."):
                        result = interview_game.evaluate_system_design_solution(challenge, user_solution)
                        
                        if result:
                            # Display score and feedback
                            score = float(result.get('score', 0))
                            if score >= 80:
                                st.success(f"🌟 Excellent! Score: {score}/100")
                            elif score >= 60:
                                st.warning(f"👍 Good attempt! Score: {score}/100")
                            else:
                                st.error(f"Score: {score}/100")
                            
                            # Display detailed feedback
                            st.write("### 📝 Feedback")
                            st.write(result.get('feedback', ''))
                            
                            # Display strengths
                            if 'strengths' in result:
                                with st.expander("💪 Strengths"):
                                    for strength in result['strengths']:
                                        st.write(f"• {strength}")
                            
                            # Display weaknesses
                            with st.expander("🔍 Areas for Improvement"):
                                for weakness in result['weaknesses']:
                                    st.write(f"• {weakness}")
                            
                            # Display suggestions
                            with st.expander("💡 Suggestions"):
                                for suggestion in result['suggestions']:
                                    st.write(f"• {suggestion}")
                            
                            # Try another button
                            if st.button("Try Another Challenge"):
                                st.session_state.game_state['challenge'] = interview_game.generate_system_design_challenge(
                                    job_role=st.session_state.game_state['job_role'],
                                    difficulty=st.session_state.game_state['difficulty']
                                )
                                st.cache_data.clear()
                                st.cache_resource.clear()
    
    # Display game instructions if no mode selected
    if not st.session_state.game_state['current_mode']:
        st.write("### 🎮 Game Modes")
        st.write("""
        1. **Quick Quiz Challenge 🎯**
           - Multiple choice questions
           - Test your technical knowledge
           - Fun facts with each question
        
        2. **Real-world Scenario Solver 🌟**
           - Tackle realistic business scenarios
           - Practice problem-solving
           - Get detailed feedback
        
        3. **Rapid Fire Round ⚡**
           - Quick-thinking challenges
           - 30-second time limit per question
           - Test your instant recall
        
        4. **Debug Challenge 🐛**
           - Find and fix bugs
           - Real code examples
           - Learn best practices
        
        5. **System Design Adventure 🏗️**
           - Design scalable systems
           - Consider real-world constraints
           - Get architecture feedback
        """)
        
        st.info("👆 Enter your job role and select a difficulty level to start!")

elif selected_page == "Learning Playlist":
    st.title("Learning Playlist")
    st.info("🚧 Coming Soon! This feature is under development.")

elif selected_page == "Coding Challenge":
    st.title("💻 Coding Challenge")
    st.write("Welcome to the coding challenge feature!")
    
    # Initialize session state for coding challenge
    if 'coding_challenge' not in st.session_state:
        st.session_state.coding_challenge = {
            'current_mode': None,
            'job_role': None,
            'difficulty': None,
            'challenge': None,
            'current_code': None,
            'last_run': None
        }
    
    # Coding challenge setup
    col1, col2 = st.columns(2)
    with col1:
        job_role = st.text_input("What's your target job role?", placeholder="e.g., Python Developer")
    with col2:
        difficulty = st.selectbox(
            "Choose difficulty level",
            list(interview_game.get_difficulty_levels().keys()),
            format_func=lambda x: interview_game.get_difficulty_levels()[x]
        )
    
    # Coding challenge mode selection
    st.write("### Choose Your Challenge Mode")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if st.button("📝 Code Editor", use_container_width=True):
            st.session_state.coding_challenge = {
                'current_mode': "coding",
                'job_role': job_role,
                'difficulty': difficulty
            }
    
    # Coding challenge interface based on mode
    if st.session_state.coding_challenge['current_mode'] == "coding":
        st.write("💻 Coding Challenge")
        
        # Initialize coding challenge if not already done
        if 'challenge' not in st.session_state.coding_challenge:
            with st.spinner("Generating coding challenge..."):
                st.session_state.coding_challenge['challenge'] = interview_game.generate_coding_challenge(
                    job_role=st.session_state.coding_challenge['job_role'],
                    difficulty=st.session_state.coding_challenge['difficulty']
                )
        
        challenge = st.session_state.coding_challenge.get('challenge')
        if challenge:
            # Display challenge details
            st.write("### 📝 Problem Description")
            st.write(challenge['description'])
            
            # Create tabs for different sections
            info_tab, editor_tab, results_tab = st.tabs(["Problem Info", "Code Editor", "Results"])
            
            with info_tab:
                st.write("#### Input Format")
                st.info(challenge['input_format'])
                
                st.write("#### Output Format")
                st.info(challenge['output_format'])
                
                st.write("#### Constraints")
                for constraint in challenge['constraints']:
                    st.write(f"• {constraint}")
                
                st.write("#### Example Test Cases")
                for i, case in enumerate(challenge['example_cases'], 1):
                    with st.expander(f"Test Case {i}"):
                        st.write("Input:")
                        st.code(case['input'])
                        st.write("Expected Output:")
                        st.code(case['output'])
            
            with editor_tab:
                # Code editor section
                if 'current_code' not in st.session_state.coding_challenge:
                    st.session_state.coding_challenge['current_code'] = challenge['function_template']
                
                st.write("### 👨‍💻 Code Editor")
                
                # Add language selector
                language = st.selectbox(
                    "Select Language",
                    ["python", "javascript", "java", "cpp"],
                    key="code_language"
                )
                
                # Code editor with syntax highlighting
                user_code = st.text_area(
                    "Write your code here:",
                    value=st.session_state.coding_challenge['current_code'],
                    height=300,
                    key="code_editor"
                )
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button("Run Code"):
                        st.session_state.coding_challenge['current_code'] = user_code
                        st.session_state.coding_challenge['last_run'] = interview_game.evaluate_code_solution(
                            challenge, user_code, language
                        )
                
                with col2:
                    if st.button("Reset Code"):
                        st.session_state.coding_challenge['current_code'] = challenge['function_template']
                        st.experimental_rerun()
            
            with results_tab:
                if 'last_run' in st.session_state.coding_challenge:
                    results = st.session_state.coding_challenge['last_run']
                    
                    # Display test results
                    st.write("### 🎯 Test Results")
                    st.write(f"Passed: {results['passed']}/{results['total']} tests")
                    
                    # Display each test case result
                    for i, test in enumerate(results['test_results'], 1):
                        with st.expander(f"Test Case {i} - {'✅ Passed' if test['passed'] else '❌ Failed'}"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write("Input:")
                                st.code(test['input'])
                                st.write("Expected Output:")
                                st.code(test['expected'])
                            with col2:
                                st.write("Your Output:")
                                st.code(test['actual'])
                                st.write(f"Execution Time: {test['execution_time']:.3f}s")
                    
                    # Display errors if any
                    if results['errors']:
                        st.write("### ❌ Errors")
                        for error in results['errors']:
                            st.error(error)
                    
                    # Display style issues
                    if results['style_issues']:
                        st.write("### 🎨 Style Issues")
                        for issue in results['style_issues']:
                            st.warning(issue)
                    
                    # Display optimization tips
                    if results['optimization_tips']:
                        st.write("### 🚀 Optimization Tips")
                        for tip in results['optimization_tips']:
                            st.info(tip)
                    
                    # Show sample solution button
                    if results['passed'] == results['total']:
                        st.success("🎉 Congratulations! All test cases passed!")
                        if st.button("View Sample Solution"):
                            st.write("### ✨ Sample Solution")
                            st.code(challenge['sample_solution'])