import streamlit as st
import os
import random
from dotenv import load_dotenv
import base64
import re
from datetime import datetime
import tempfile
import fitz
from PIL import Image

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

# Sidebar navigation
st.sidebar.title("Navigation")
selected_page = st.sidebar.selectbox(
    "Choose a feature",
    ["Home", "Resume Builder", "Resume Analysis", "PDF Viewer & Editor", "Career Coach", "Interview Game", "Learning Playlist","AI Interviewer"]
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
    st.title("Resume Builder")
    
    # Initialize resume builder with API key from environment variable
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("⚠️ OpenAI API key not found. Please check your .env file.")
        st.stop()
    
    resume_builder = ATSResumeBuilder(api_key)
    
    # Initialize session state
    if 'pdf_content' not in st.session_state:
        st.session_state.pdf_content = None
    if 'user_name' not in st.session_state:
        st.session_state.user_name = None
    if 'basic_info' not in st.session_state:
        st.session_state.basic_info = None
    if 'generation_count' not in st.session_state:
        st.session_state.generation_count = 0
    if 'show_ats_score' not in st.session_state:
        st.session_state.show_ats_score = False
    if 'form_submitted' not in st.session_state:
        st.session_state.form_submitted = False

    # Get query parameters
    query_params = st.experimental_get_query_params()
    action = query_params.get("action", [None])[0]

    # Handle regeneration from query parameter
    if action == "regenerate" and st.session_state.basic_info:
        st.session_state.generation_count += 1
        basic_info = st.session_state.basic_info
        basic_info['generation_style'] = {
            "tone": "professional" if st.session_state.generation_count % 2 == 0 else "modern",
            "focus": "achievements" if st.session_state.generation_count % 3 == 0 else "skills",
            "variation": st.session_state.generation_count
        }
        
        with st.spinner("🔄 Regenerating your resume..."):
            try:
                pdf_content = resume_builder.generate_resume_from_basic_info(basic_info)
                st.session_state.pdf_content = pdf_content
                st.success("✅ Resume regenerated successfully!")
                # Clear the action parameter
                query_params.pop("action", None)
                st.experimental_set_query_params(**query_params)
            except Exception as e:
                st.error(f"❌ Error regenerating resume: {str(e)}")
                st.stop()

    # Form for resume building
    with st.form("resume_form"):
        st.subheader("📋 Contact Information")
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name", placeholder="John Doe")
            email = st.text_input("Email", placeholder="john@example.com")
            phone = st.text_input("Phone", placeholder="+1 (123) 456-7890")
        with col2:
            location = st.text_input("Location", placeholder="City, Country")
            github = st.text_input("GitHub Profile", placeholder="https://github.com/username")
            linkedin = st.text_input("LinkedIn Profile", placeholder="https://linkedin.com/in/username")
        
        st.subheader("🎓 Education")
        col1, col2 = st.columns(2)
        with col1:
            degree = st.text_input("Degree", placeholder="Bachelor of Technology in Computer Science")
            university = st.text_input("University", placeholder="Your University Name")
        with col2:
            gpa = st.text_input("GPA", placeholder="3.8/4.0")
            graduation_year = st.text_input("Graduation Year", placeholder="2024")
        
        st.subheader("💼 Work Experience")
        num_experiences = st.number_input("Number of work experiences", min_value=0, max_value=5, value=1)
        experiences = []
        
        for i in range(num_experiences):
            st.markdown(f"##### Experience {i+1}")
            col1, col2 = st.columns(2)
            with col1:
                company = st.text_input(f"Company Name #{i+1}", key=f"company_{i}")
                title = st.text_input(f"Job Title #{i+1}", key=f"title_{i}")
            with col2:
                start_date = st.text_input(f"Start Date #{i+1}", placeholder="MM/YYYY", key=f"start_{i}")
                end_date = st.text_input(f"End Date #{i+1}", placeholder="MM/YYYY or Present", key=f"end_{i}")
            achievements = st.text_area(f"Key Achievements #{i+1}", 
                placeholder="- Developed feature X that improved Y by Z%\n- Led team of N people\n- Reduced processing time by X%",
                height=100,
                key=f"achievements_{i}")
            experiences.append({
                "company": company,
                "title": title,
                "duration": f"{start_date} - {end_date}",
                "achievements": [ach.strip() for ach in achievements.split('\n') if ach.strip()]
            })
        
        st.subheader("🛠️ Skills & Expertise")
        col1, col2 = st.columns(2)
        with col1:
            programming_languages = st.text_input("Programming Languages", 
                placeholder="Python, Java, JavaScript, C++")
            frameworks = st.text_input("Frameworks & Libraries", 
                placeholder="React, Django, TensorFlow")
        with col2:
            tools = st.text_input("Tools & Platforms", 
                placeholder="Git, Docker, AWS, Linux")
            databases = st.text_input("Databases", 
                placeholder="PostgreSQL, MongoDB, Redis")
        
        st.subheader("🎯 Target Job")
        col1, col2 = st.columns(2)
        with col1:
            target_role = st.text_input("Target Role", placeholder="Software Engineer")
            target_company = st.text_input("Target Company (Optional)", placeholder="Company Name")
        with col2:
            job_description = st.text_area("Job Description (Optional)", 
                placeholder="Paste the job description here for better resume tailoring",
                height=100)
        
        st.subheader("🌟 Additional Information")
        col1, col2 = st.columns(2)
        with col1:
            languages = st.text_input("Languages Known", 
                placeholder="English (Native), Spanish (Intermediate)")
            certifications = st.text_area("Certifications", 
                placeholder="- AWS Certified Developer\n- Google Cloud Professional",
                height=100)
        with col2:
            hobbies = st.text_input("Hobbies & Interests", 
                placeholder="Open Source Contributing, Tech Blogging")
            achievements = st.text_area("Additional Achievements", 
                placeholder="- Won XYZ Hackathon\n- Published paper in ABC",
                height=100)
        
        submitted = st.form_submit_button("Generate Resume", type="primary")
        if submitted:
            if not name or not email:
                st.error("Please fill in at least your name and email.")
                st.stop()
                
            st.session_state.user_name = name
            st.session_state.form_submitted = True
            
            # Collect form data into basic_info
            basic_info = {
                "contact_info": {
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "location": location,
                    "linkedin": linkedin,
                    "github": github
                },
                "education": {
                    "degree": degree,
                    "university": university,
                    "duration": f"Graduating {graduation_year}" if graduation_year else "",
                    "gpa": gpa
                },
                "work_experience": experiences,
                "skills": {
                    "programming_languages": [lang.strip() for lang in programming_languages.split(',') if lang.strip()],
                    "frameworks": [fw.strip() for fw in frameworks.split(',') if fw.strip()],
                    "tools": [tool.strip() for tool in tools.split(',') if tool.strip()],
                    "databases": [db.strip() for db in databases.split(',') if db.strip()]
                },
                "languages": [lang.strip() for lang in languages.split(',') if lang.strip()],
                "certifications": [cert.strip() for cert in certifications.split('\n') if cert.strip()],
                "hobbies": [hobby.strip() for hobby in hobbies.split(',') if hobby.strip()],
                "achievements": [ach.strip() for ach in achievements.split('\n') if ach.strip()],
                "target_job": {
                    "role": target_role,
                    "company": target_company,
                    "description": job_description
                }
            }
            st.session_state.basic_info = basic_info
            
            with st.spinner("🔄 Generating your ATS-optimized resume..."):
                try:
                    pdf_content = resume_builder.generate_resume_from_basic_info(basic_info)
                    st.session_state.pdf_content = pdf_content
                    st.success("✅ Resume generated successfully!")
                except Exception as e:
                    st.error(f"❌ Error generating resume: {str(e)}")
                    st.stop()

    # Display resume and actions if we have content
    if st.session_state.pdf_content:
        # Show preview section
        st.subheader("📄 Resume Preview")
        
        # Display PDF preview using HTML embed
        preview_html = f"""
            <iframe src="data:application/pdf;base64,{base64.b64encode(st.session_state.pdf_content).decode('utf-8')}"
                    width="100%"
                    height="800"
                    style="border: 1px solid #ccc; border-radius: 5px;">
            </iframe>
        """
        st.markdown(preview_html, unsafe_allow_html=True)
        
        # Add actions column
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("⚡ Regenerate Resume"):
                # Set query parameter for regeneration
                query_params["action"] = "regenerate"
                st.experimental_set_query_params(**query_params)
                st.experimental_rerun()
        
        with col2:
            st.download_button(
                label="⬇️ Download Resume (PDF)",
                data=st.session_state.pdf_content,
                file_name=f"resume_{st.session_state.user_name if st.session_state.get('user_name') else 'untitled'}.pdf",
                mime="application/pdf"
            )
        
        with col3:
            if st.button("📋 View ATS Score"):
                st.session_state.show_ats_score = True
        
        # Show ATS score if requested
        if st.session_state.show_ats_score and st.session_state.basic_info:
            st.subheader("🎯 ATS Optimization Score")
            ats_score = resume_builder.analyze_ats_score(st.session_state.basic_info)
            
            # Display overall score
            st.metric("Overall Score", f"{ats_score['overall_score']}%")
            
            # Display section scores
            st.write("Section Scores:")
            scores_cols = st.columns(4)
            for i, (section, score) in enumerate(ats_score['section_scores'].items()):
                with scores_cols[i]:
                    st.metric(
                        label=f"{section.title()}",
                        value=f"{score}%",
                        delta=f"{'High' if score > 0.7 else 'Moderate' if score > 0.5 else 'Low'} Synergy"
                    )
            
            # Display keyword matches
            st.write("📊 Keyword Analysis")
            if isinstance(ats_score['keyword_match'], str) and ats_score['keyword_match'].endswith('%'):
                match_value = float(ats_score['keyword_match'].strip('%')) / 100
                st.progress(match_value)
            st.write(f"Keyword Match: {ats_score['keyword_match']}")
            
            # Display strengths and improvements
            col1, col2 = st.columns(2)
            with col1:
                st.write("💪 Strengths")
                for strength in ats_score['strengths']:
                    st.success(strength)
            
            with col2:
                st.write("🔄 Suggested Improvements")
                for improvement in ats_score['improvements']:
                    st.info(improvement)
            
            # Show keyword suggestions
            st.write("🔑 Keyword Suggestions")
            st.write("Consider adding these relevant keywords:")
            keyword_cols = st.columns(3)
            for i, keyword in enumerate(ats_score['keyword_suggestions']):
                with keyword_cols[i % 3]:
                    st.code(keyword)

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
            tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
                "Resume Summary", 
                "PQ Score", 
                "Team Synergy", 
                "Career Growth",
                "Skills Gap",
                "Industry Fit",
                "Interview Prep"
            ])
            
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

            # Skills gap analysis
            with tab5:
                st.subheader("Skills Gap Analysis")
                
                # Sample skills gap data
                skills_gap = {
                    'Cloud Computing': {'Required': 80, 'Current': 60},
                    'Machine Learning': {'Required': 70, 'Current': 75},
                    'DevOps': {'Required': 85, 'Current': 65},
                    'System Design': {'Required': 90, 'Current': 80}
                }
                
                for skill, scores in skills_gap.items():
                    st.write(f"**{skill}**")
                    cols = st.columns([3, 1])
                    with cols[0]:
                        # Ensure progress value is between 0 and 1
                        progress = min(scores['Current'] / scores['Required'], 1.0)
                        st.progress(progress)
                    with cols[1]:
                        st.write(f"{scores['Current']}/{scores['Required']}")

            # Industry Fit Tab
            with tab6:
                st.subheader("Industry Fit Analysis")
                
                # Industry selection
                industry = st.selectbox(
                    "Select Target Industry",
                    ["Technology", "Finance", "Healthcare", "E-commerce", "Manufacturing"]
                )
                
                # Create columns for different metrics
                col1, col2 = st.columns(2)
                
                with col1:
                    # Industry alignment chart
                    st.subheader("Industry Alignment")
                    
                    alignment_data = {
                        'Domain Knowledge': 85,
                        'Industry Tools': 75,
                        'Best Practices': 90,
                        'Industry Standards': 80
                    }
                    
                    fig = go.Figure(data=[
                        go.Bar(
                            x=list(alignment_data.keys()),
                            y=list(alignment_data.values()),
                            marker_color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
                        )
                    ])
                    
                    fig.update_layout(
                        yaxis_range=[0, 100],
                        height=400
                    )
                    
                    st.plotly_chart(fig)
                
                with col2:
                    # Industry trends matching
                    st.subheader("Industry Trends Match")
                    
                    trends = {
                        'AI/ML Integration': 90,
                        'Cloud Migration': 85,
                        'Agile Practices': 95,
                        'Security Compliance': 80
                    }
                    
                    for trend, score in trends.items():
                        st.metric(
                            label=trend,
                            value=f"{score}%",
                            delta="Aligned" if score >= 85 else "Gap"
                        )
            
            # Interview Prep Tab
            with tab7:
                st.subheader("Interview Preparation Guide")
                
                sections = st.tabs([
                    "Technical Questions",
                    "Behavioral Questions",
                    "Project Discussion",
                    "Culture Fit"
                ])
                
                with sections[0]:
                    st.subheader("Recommended Technical Questions")
                    
                    questions = [
                        "Explain your experience with cloud technologies",
                        "Describe a challenging technical problem you solved",
                        "How do you approach system design?",
                        "What's your experience with agile methodologies?"
                    ]
                    
                    for i, q in enumerate(questions, 1):
                        with st.expander(f"Question {i}: {q}"):
                            st.write("**Suggested Approach:**")
                            st.write("1. Start with a high-level overview")
                            st.write("2. Provide specific examples from your experience")
                            st.write("3. Highlight the outcomes and learnings")
                            st.write("4. Connect it to the role requirements")
                
                with sections[1]:
                    st.subheader("Behavioral Questions Preparation")
                    
                    scenarios = {
                        "Leadership": "Describe a time when you led a team through a difficult project",
                        "Conflict Resolution": "Tell me about a time you handled a disagreement with a colleague",
                        "Problem Solving": "Share an example of how you solved a complex business problem",
                        "Initiative": "Describe a situation where you went above and beyond"
                    }
                    
                    for category, question in scenarios.items():
                        with st.expander(category):
                            st.write(f"**Question:** {question}")
                            st.write("**STAR Method Approach:**")
                            st.write("- **Situation:** Set the context")
                            st.write("- **Task:** Describe your responsibility")
                            st.write("- **Action:** Explain what you did")
                            st.write("- **Result:** Share the outcome")
                
                with sections[2]:
                    st.subheader("Project Discussion Guide")
                    
                    projects = [
                        "Project 1: E-commerce Platform",
                        "Project 2: Data Analytics Dashboard",
                        "Project 3: Mobile App Development"
                    ]
                    
                    for project in projects:
                        with st.expander(project):
                            st.write("**Key Talking Points:**")
                            st.write("1. Technical challenges and solutions")
                            st.write("2. Your specific role and contributions")
                            st.write("3. Impact and results")
                            st.write("4. Technologies used")
                            st.write("5. Team collaboration aspects")
                
                with sections[3]:
                    st.subheader("Culture Fit Preparation")
                    
                    st.write("**Company Values Alignment:**")
                    values = {
                        "Innovation": 90,
                        "Teamwork": 85,
                        "Customer Focus": 95,
                        "Continuous Learning": 88
                    }
                    
                    for value, score in values.items():
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.progress(score/100)
                        with col2:
                            st.write(f"{value}: {score}%")

elif selected_page == "PDF Viewer & Editor":
    st.title("📄 PDF Viewer & Editor")
    
    # File upload
    uploaded_file = st.file_uploader("Upload a PDF file", type=['pdf'])
    
    if uploaded_file is not None:
        try:
            # Create a bytes buffer from the uploaded file
            pdf_bytes = uploaded_file.getvalue()
            
            # Open PDF directly from memory using BytesIO
            pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
            total_pages = len(pdf_document)
            
            # Sidebar for navigation and tools
            with st.sidebar:
                st.subheader("📑 Navigation & Tools")
                
                # Page navigation
                page_number = st.number_input(
                    "Go to page",
                    min_value=1,
                    max_value=total_pages,
                    value=1
                )
                
                # Editing tools
                st.subheader("🛠️ Editing Tools")
                
                tool_options = st.radio(
                    "Select Tool",
                    ["Text Edit", "Highlight", "Add Note", "Draw", "Erase"]
                )
                
                if tool_options == "Text Edit":
                    text_color = st.color_picker("Text Color", "#000000")
                    font_size = st.slider("Font Size", 8, 72, 12)
                
                elif tool_options == "Highlight":
                    highlight_color = st.color_picker("Highlight Color", "#FFFF00")
                    opacity = st.slider("Opacity", 0.1, 1.0, 0.5)
                
                elif tool_options == "Draw":
                    draw_color = st.color_picker("Draw Color", "#000000")
                    line_width = st.slider("Line Width", 1, 10, 2)
                
                # Save changes button
                if st.button("💾 Save Changes"):
                    try:
                        # Create output directory if it doesn't exist
                        os.makedirs("output", exist_ok=True)
                        
                        # Save the modified PDF
                        save_path = os.path.join("output", f"modified_{uploaded_file.name}")
                        pdf_document.save(save_path)
                        
                        # Provide download link
                        with open(save_path, "rb") as file:
                            st.download_button(
                                label="⬇️ Download Modified PDF",
                                data=file,
                                file_name=f"modified_{uploaded_file.name}",
                                mime="application/pdf"
                            )
                        st.success("Changes saved successfully!")
                    except Exception as e:
                        st.error(f"Error saving changes: {str(e)}")
            
            # Main content area
            col1, col2 = st.columns([2, 1])
            
            with col1:
                try:
                    # PDF Viewer
                    st.subheader("📄 PDF View")
                    page = pdf_document[page_number - 1]
                    
                    # Convert page to image with higher DPI for better quality
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better quality
                    
                    # Convert pixmap to PIL Image
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    
                    # Display the page
                    st.image(img, use_column_width=True)
                except Exception as e:
                    st.error(f"Error displaying page: {str(e)}")
            
            with col2:
                # Editing Panel
                st.subheader("✏️ Edit Panel")
                
                if tool_options == "Text Edit":
                    # Text editing
                    text_content = st.text_area("Enter text to add", height=100)
                    text_position = st.selectbox(
                        "Text Position",
                        ["Top Left", "Top Center", "Top Right", "Center", "Bottom Left", "Bottom Center", "Bottom Right"]
                    )
                    
                    # Define position mapping
                    position_mapping = {
                        "Top Left": (50, 50),
                        "Top Center": (page.rect.width/2, 50),
                        "Top Right": (page.rect.width-50, 50),
                        "Center": (page.rect.width/2, page.rect.height/2),
                        "Bottom Left": (50, page.rect.height-50),
                        "Bottom Center": (page.rect.width/2, page.rect.height-50),
                        "Bottom Right": (page.rect.width-50, page.rect.height-50)
                    }
                    
                    if st.button("Add Text"):
                        try:
                            # Get position coordinates
                            pos = position_mapping[text_position]
                            
                            # Add text to PDF
                            page.insert_text(
                                point=pos,
                                text=text_content,
                                fontsize=font_size,
                                color=fitz.utils.getColor(text_color)
                            )
                            st.success("Text added!")
                        except Exception as e:
                            st.error(f"Error adding text: {str(e)}")
                
                elif tool_options == "Highlight":
                    st.info("Click and drag on the PDF to highlight text")
                    # Add highlight functionality
                    
                elif tool_options == "Add Note":
                    note_text = st.text_area("Note content", height=100)
                    note_position = st.selectbox(
                        "Note Position",
                        ["Top Left", "Top Right", "Bottom Left", "Bottom Right"]
                    )
                    
                    # Define position mapping for notes
                    note_position_mapping = {
                        "Top Left": (50, 50),
                        "Top Right": (page.rect.width-50, 50),
                        "Bottom Left": (50, page.rect.height-50),
                        "Bottom Right": (page.rect.width-50, page.rect.height-50)
                    }
                    
                    if st.button("Add Note"):
                        try:
                            # Get position coordinates
                            pos = note_position_mapping[note_position]
                            
                            # Add note annotation
                            annot = page.add_text_annot(
                                point=pos,
                                text=note_text
                            )
                            # Set annotation properties
                            annot.set_colors(stroke=(1, 1, 0))  # Yellow border
                            annot.update()
                            st.success("Note added!")
                        except Exception as e:
                            st.error(f"Error adding note: {str(e)}")
                
                elif tool_options == "Draw":
                    st.info("Drawing functionality will be added in the next update")
                
                elif tool_options == "Erase":
                    st.info("Eraser functionality will be added in the next update")
                
                # Metadata Editor
                with st.expander("📝 Edit Metadata"):
                    metadata = pdf_document.metadata
                    new_title = st.text_input("Title", metadata.get("title", ""))
                    new_author = st.text_input("Author", metadata.get("author", ""))
                    new_subject = st.text_input("Subject", metadata.get("subject", ""))
                    
                    if st.button("Update Metadata"):
                        try:
                            pdf_document.set_metadata({
                                "title": new_title,
                                "author": new_author,
                                "subject": new_subject
                            })
                            st.success("Metadata updated!")
                        except Exception as e:
                            st.error(f"Error updating metadata: {str(e)}")
            
            # Close the PDF document
            pdf_document.close()
            
        except Exception as e:
            st.error(f"Error processing PDF: {str(e)}")

