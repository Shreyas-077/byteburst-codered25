import streamlit as st
import requests
import os
from dotenv import load_dotenv
from googleapiclient.discovery import build
import json

# Load environment variables
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not API_KEY:
    st.error("⚠ GEMINI_API_KEY not found in environment variables")
    st.stop()

if not YOUTUBE_API_KEY:
    st.warning("⚠ YOUTUBE_API_KEY not found. YouTube features will be limited.")

if not GITHUB_TOKEN:
    st.warning("⚠ GITHUB_TOKEN not found. GitHub features will be limited.")

API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"

def analyze_project(overview: str, aim: str) -> dict:
    """
    Analyze project details using the Gemini API.
    
    Args:
        overview (str): Project overview text
        aim (str): Project aim text
    
    Returns:
        dict: Parsed response from the API
    """
    prompt = f"""
    As an expert project analyst, please provide a detailed analysis of the following project:
    
    PROJECT OVERVIEW:
    {overview}
    
    PROJECT AIM:
    {aim}
    
    Please provide a comprehensive analysis in the following format:
    
    Uniqueness Analysis:
    - Evaluate the project's unique value proposition
    - Identify key differentiators from existing solutions
    - Assess market positioning and innovation aspects
    
    Potential Improvements:
    - Technical enhancements that could strengthen the project
    - Feature suggestions to improve user experience
    - Scalability and performance optimization recommendations
    - Security and reliability considerations
    
    Development Plan:
    1. Initial Setup Phase:
       - Required technologies and frameworks
       - Development environment setup
       - Basic project structure
    
    2. Core Development Phase:
       - Key features implementation order
       - Technical architecture considerations
       - Database design and API structure
    
    3. Enhancement Phase:
       - Advanced features
       - Optimization opportunities
       - Testing and quality assurance steps
    
    4. Deployment Phase:
       - Deployment strategy
       - Monitoring and maintenance plan
       - Future scaling considerations
    
    Please provide specific, actionable insights for each section.
    """
    
    payload = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }]
    }
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    try:
        with st.spinner("🔄 Analyzing your project..."):
            response = requests.post(API_URL, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
    except requests.exceptions.Timeout:
        st.error("🕒 Request timed out. Please try again.")
    except requests.exceptions.RequestException as e:
        st.error(f"❌ API request failed: {str(e)}")
    except Exception as e:
        st.error(f"❌ An unexpected error occurred: {str(e)}")
    return None

def parse_analysis(text: str) -> dict:
    """Parse the analysis text into separate sections with better structure."""
    sections = {
        "uniqueness": "",
        "improvements": "",
        "development": ""
    }
    
    try:
        # Parse Uniqueness Analysis
        if "Uniqueness Analysis:" in text:
            parts = text.split("Uniqueness Analysis:")
            if len(parts) > 1:
                uniqueness_part = parts[1].split("Potential Improvements:")[0]
                sections["uniqueness"] = uniqueness_part.strip()
        
        # Parse Potential Improvements
        if "Potential Improvements:" in text:
            parts = text.split("Potential Improvements:")
            if len(parts) > 1:
                improvements_part = parts[1].split("Development Plan:")[0]
                sections["improvements"] = improvements_part.strip()
        
        # Parse Development Plan
        if "Development Plan:" in text:
            parts = text.split("Development Plan:")
            if len(parts) > 1:
                sections["development"] = parts[1].strip()
        
        # Convert bullet points to HTML lists
        for key in sections:
            if sections[key]:
                # Convert bullet points to HTML list items
                lines = sections[key].split('\n')
                formatted_lines = []
                for line in lines:
                    line = line.strip()
                    if line.startswith('- '):
                        formatted_lines.append(f"<li>{line[2:]}</li>")
                    elif line.startswith('1.') or line.startswith('2.') or line.startswith('3.') or line.startswith('4.'):
                        formatted_lines.append(f"<h4>{line}</h4>")
                    elif line:
                        formatted_lines.append(f"<p>{line}</p>")
                sections[key] = f"<div class='analysis-section'>" + "\n".join(formatted_lines) + "</div>"
        
        return sections
    except Exception as e:
        st.error(f"Error parsing analysis: {str(e)}")
        return {"uniqueness": "", "improvements": "", "development": ""}

def display_analysis_section(title: str, content: str, icon: str):
    """Display an analysis section with consistent styling."""
    if content:
        st.markdown(f"""
            <div class="section-header">
                {icon} {title}
            </div>
            <div class="analysis-section">
                {content}
            </div>
        """, unsafe_allow_html=True)

def extract_search_keywords(analysis_text: str) -> str:
    """
    Extract relevant keywords from Gemini's analysis for better searching.
    """
    try:
        # Create a prompt to get search keywords from Gemini
        prompt = f"""
        Based on the following project analysis, provide 3-5 most relevant search keywords or phrases for finding tutorials and code examples. 
        Format them as comma-separated values.
        
        Analysis:
        {analysis_text}
        """
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }]
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        response = requests.post(API_URL, json=payload, headers=headers)
        response.raise_for_status()
        
        keywords = response.json()["candidates"][0]["content"]["parts"][0]["text"]
        # Clean up the response to get just the keywords
        keywords = keywords.strip().split(',')
        keywords = [k.strip() for k in keywords if k.strip()]
        
        return " OR ".join([f'"{k}"' for k in keywords[:3]])  # Use top 3 keywords
    except Exception as e:
        st.error(f"Error extracting search keywords: {str(e)}")
        return None

def get_youtube_videos(query: str, analysis_text: str, max_results: int = 5):
    """
    Fetch relevant YouTube videos based on project analysis.
    """
    try:
        # Get relevant search keywords from analysis
        search_keywords = extract_search_keywords(analysis_text)
        if not search_keywords:
            search_keywords = query
            
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        
        # Search for relevant videos with refined keywords
        search_response = youtube.search().list(
            q=f"{search_keywords} tutorial",
            part='snippet',
            maxResults=max_results,
            type='video',
            relevanceLanguage='en',
            order='relevance',
            videoDuration='medium'  # Medium length tutorials
        ).execute()
        
        videos = []
        for item in search_response['items']:
            video = {
                'title': item['snippet']['title'],
                'description': item['snippet']['description'],
                'thumbnail': item['snippet']['thumbnails']['medium']['url'],
                'video_id': item['id']['videoId'],
                'url': f"https://www.youtube.com/watch?v={item['id']['videoId']}"
            }
            videos.append(video)
        
        return videos
    except Exception as e:
        st.error(f"Error fetching YouTube videos: {str(e)}")
        return []

def get_github_repos(query: str, analysis_text: str, max_results: int = 5):
    """
    Fetch relevant GitHub repositories based on project analysis.
    """
    try:
        # Get relevant search keywords from analysis
        search_keywords = extract_search_keywords(analysis_text)
        if not search_keywords:
            search_keywords = query
            
        headers = {
            'Authorization': f'token {GITHUB_TOKEN}' if GITHUB_TOKEN else None,
            'Accept': 'application/vnd.github.v3+json'
        }
        
        # Search GitHub repositories with refined keywords
        search_url = "https://api.github.com/search/repositories"
        params = {
            'q': search_keywords,
            'sort': 'stars',
            'order': 'desc',
            'per_page': max_results
        }
        
        response = requests.get(search_url, headers=headers, params=params)
        response.raise_for_status()
        
        repos = []
        for item in response.json()['items']:
            repo = {
                'name': item['name'],
                'description': item['description'],
                'url': item['html_url'],
                'stars': item['stargazers_count'],
                'language': item['language'],
                'owner': item['owner']['login']
            }
            repos.append(repo)
        
        return repos
    except Exception as e:
        st.error(f"Error fetching GitHub repositories: {str(e)}")
        return []

def display_youtube_videos(videos):
    """Display YouTube videos in a nice format."""
    if videos:
        st.markdown("""
            <div class="section-header">
                📺 Related YouTube Tutorials
            </div>
        """, unsafe_allow_html=True)
        
        for video in videos:
            st.markdown(f"""
                <div class="video-card">
                    <div class="video-thumbnail">
                        <a href="{video['url']}" target="_blank">
                            <img src="{video['thumbnail']}" alt="{video['title']}">
                        </a>
                    </div>
                    <div class="video-info">
                        <h3><a href="{video['url']}" target="_blank">{video['title']}</a></h3>
                        <p>{video['description'][:200]}...</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)

def display_github_repos(repos):
    """Display GitHub repositories in a nice format."""
    if repos:
        st.markdown("""
            <div class="section-header">
                💻 Related GitHub Repositories
            </div>
        """, unsafe_allow_html=True)
        
        for repo in repos:
            st.markdown(f"""
                <div class="repo-card">
                    <div class="repo-header">
                        <h3><a href="{repo['url']}" target="_blank">{repo['name']}</a></h3>
                        <div class="repo-stats">
                            <span class="repo-stars">⭐ {repo['stars']}</span>
                            {f'<span class="repo-language">🔵 {repo["language"]}</span>' if repo['language'] else ''}
                        </div>
                    </div>
                    <p>{repo['description'] if repo['description'] else 'No description available.'}</p>
                    <div class="repo-footer">
                        <span class="repo-owner">👤 {repo['owner']}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

# Page configuration
st.set_page_config(
    page_title="Project Idea Evaluator",
    page_icon="🚀",
    layout="wide"
)

# Update the CSS with better typography
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Poppins:wght@400;500;600;700&display=swap');
    
    /* Base typography */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* General page styling */
    .main {
        padding: 2rem;
        font-family: 'Inter', sans-serif;
        color: #2C3E50;
    }
    
    /* Header styling */
    .stTitle {
        font-family: 'Poppins', sans-serif;
        color: #1E88E5;
        font-size: 2.8rem !important;
        font-weight: 700 !important;
        margin-bottom: 2rem !important;
        text-align: center;
        letter-spacing: -0.5px;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Poppins', sans-serif;
        letter-spacing: -0.3px;
    }
    
    /* Form styling */
    .stTextArea textarea {
        font-family: 'Inter', sans-serif;
        font-size: 1rem;
        line-height: 1.6;
        border: 2px solid #E3F2FD;
        border-radius: 10px;
        padding: 15px;
        transition: border-color 0.3s ease;
    }
    .stTextArea textarea:focus {
        border-color: #2196F3;
        box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.1);
    }
    
    /* Input labels */
    .stTextInput label, .stTextArea label {
        font-family: 'Poppins', sans-serif;
        font-weight: 500;
        font-size: 1.1rem;
        color: #1E88E5;
        margin-bottom: 8px;
    }
    
    /* Button styling */
    .stButton > button {
        font-family: 'Poppins', sans-serif;
        background: linear-gradient(45deg, #2196F3, #1976D2);
        color: white;
        padding: 15px 32px;
        border-radius: 25px;
        border: none;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        font-weight: 600;
        font-size: 1.1rem;
        letter-spacing: 0.5px;
        width: 100%;
        margin-top: 1rem;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(0,0,0,0.15);
    }
    
    /* Analysis section styling */
    .analysis-section {
        background: white;
        border-radius: 15px;
        padding: 25px;
        margin: 15px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-left: 5px solid #2196F3;
        font-size: 1rem;
        line-height: 1.7;
    }
    
    /* Section headers */
    .section-header {
        font-family: 'Poppins', sans-serif;
        color: #1E88E5;
        font-size: 1.6rem;
        font-weight: 600;
        margin-bottom: 1.2rem;
        display: flex;
        align-items: center;
        gap: 12px;
        letter-spacing: -0.3px;
    }
    
    /* List styling */
    .analysis-section ul {
        list-style-type: none;
        padding-left: 0;
    }
    .analysis-section li {
        position: relative;
        padding: 8px 0 8px 25px;
        line-height: 1.7;
        margin-bottom: 12px;
        font-size: 1rem;
        color: #2C3E50;
    }
    .analysis-section li:before {
        content: "•";
        color: #2196F3;
        font-weight: bold;
        position: absolute;
        left: 0;
        font-size: 1.2rem;
    }
    
    /* Phase headers */
    .phase-header {
        font-family: 'Poppins', sans-serif;
        color: #0D47A1;
        font-size: 1.3rem;
        font-weight: 600;
        margin: 24px 0 16px 0;
        padding-bottom: 8px;
        border-bottom: 2px solid #E3F2FD;
        letter-spacing: -0.3px;
    }
    
    /* Tab styling */
    .stTabs {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .stTab {
        font-family: 'Poppins', sans-serif;
        font-weight: 500;
        background: #F5F5F5;
        padding: 10px 20px;
        border-radius: 20px;
        margin-right: 10px;
        font-size: 1rem;
        letter-spacing: 0.2px;
    }
    .stTab[aria-selected="true"] {
        background: #2196F3;
        color: white;
    }
    
    /* Summary card */
    .summary-card {
        margin-top: 2rem;
        padding: 24px;
        background: #E3F2FD;
        border-radius: 15px;
        font-family: 'Inter', sans-serif;
    }
    .summary-card h3 {
        font-family: 'Poppins', sans-serif;
        color: #1E88E5;
        font-size: 1.4rem;
        margin-bottom: 12px;
        font-weight: 600;
        letter-spacing: -0.3px;
    }
    .summary-card p {
        font-size: 1rem;
        line-height: 1.6;
        color: #2C3E50;
        margin-bottom: 0;
    }
    
    /* Error messages */
    .stError {
        font-family: 'Inter', sans-serif;
        background-color: #FFEBEE;
        color: #C62828;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 5px solid #C62828;
        font-size: 0.95rem;
        line-height: 1.5;
    }
    
    /* Paragraphs */
    p {
        font-size: 1rem;
        line-height: 1.7;
        color: #2C3E50;
        margin-bottom: 1rem;
    }
    
    /* Code blocks if any */
    code {
        font-family: 'Monaco', 'Consolas', monospace;
        font-size: 0.9rem;
        background: #F5F7F9;
        padding: 2px 6px;
        border-radius: 4px;
        color: #2C3E50;
    }
    
    /* Video card styling */
    .video-card {
        background: white;
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        display: flex;
        gap: 20px;
        transition: transform 0.2s;
    }
    .video-card:hover {
        transform: translateY(-2px);
    }
    .video-thumbnail {
        flex: 0 0 200px;
    }
    .video-thumbnail img {
        width: 100%;
        border-radius: 10px;
    }
    .video-info {
        flex: 1;
    }
    .video-info h3 {
        margin: 0 0 10px 0;
        font-size: 1.2rem;
    }
    .video-info a {
        color: #1E88E5;
        text-decoration: none;
    }
    .video-info a:hover {
        text-decoration: underline;
    }
    .video-info p {
        color: #666;
        font-size: 0.9rem;
        line-height: 1.5;
        margin: 0;
    }
    
    /* Repository card styling */
    .repo-card {
        background: white;
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    .repo-card:hover {
        transform: translateY(-2px);
    }
    .repo-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 10px;
    }
    .repo-header h3 {
        margin: 0;
        font-size: 1.2rem;
    }
    .repo-header a {
        color: #1E88E5;
        text-decoration: none;
    }
    .repo-header a:hover {
        text-decoration: underline;
    }
    .repo-stats {
        display: flex;
        gap: 15px;
        font-size: 0.9rem;
    }
    .repo-stars, .repo-language {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        color: #666;
    }
    .repo-card p {
        color: #666;
        font-size: 0.9rem;
        line-height: 1.5;
        margin: 10px 0;
    }
    .repo-footer {
        margin-top: 15px;
        font-size: 0.9rem;
    }
    .repo-owner {
        color: #666;
        display: inline-flex;
        align-items: center;
        gap: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# Main app
st.title("🚀 Project Idea Evaluator")
st.markdown("Transform your project ideas into well-structured plans with AI-powered analysis.")

# Create two columns for input
col1, col2 = st.columns(2)

with st.form("project_form"):
    overview = st.text_area(
        "Project Overview",
        placeholder="Describe your project idea in detail...",
        height=200
    )
    
    aim = st.text_input(
        "Project Aim",
        placeholder="What is the main goal of your project?"
    )
    
    submitted = st.form_submit_button("🔍 Analyze Project")

if submitted:
    if not overview.strip() or not aim.strip():
        st.warning("⚠ Please fill in all fields with meaningful content.")
    else:
        with st.spinner("🔄 Analyzing your project..."):
            result = analyze_project(overview, aim)
            
            if result and "candidates" in result and result["candidates"]:
                try:
                    analysis_text = result["candidates"][0]["content"]["parts"][0]["text"]
                    sections = parse_analysis(analysis_text)
                    
                    # After getting Gemini's analysis, fetch relevant resources
                    with st.spinner("🔍 Finding relevant tutorials and repositories..."):
                        search_query = f"{overview} {aim}"
                        videos = get_youtube_videos(search_query, analysis_text)
                        repos = get_github_repos(search_query, analysis_text)
                    
                    st.markdown("## 📊 Analysis Results", unsafe_allow_html=True)
                    
                    # Create tabs for all sections
                    tab1, tab2, tab3, tab4, tab5 = st.tabs([
                        "🎯 Uniqueness Analysis",
                        "💡 Potential Improvements",
                        "🚀 Development Plan",
                        "📺 Tutorial Videos",
                        "💻 GitHub Projects"
                    ])
                    
                    with tab1:
                        if sections["uniqueness"]:
                            display_analysis_section(
                                "Project Uniqueness",
                                sections["uniqueness"],
                                "🎯"
                            )
                    
                    with tab2:
                        if sections["improvements"]:
                            display_analysis_section(
                                "Suggested Improvements",
                                sections["improvements"],
                                "💡"
                            )
                    
                    with tab3:
                        if sections["development"]:
                            display_analysis_section(
                                "Development Roadmap",
                                sections["development"],
                                "🚀"
                            )
                    
                    with tab4:
                        display_youtube_videos(videos)
                    
                    with tab5:
                        display_github_repos(repos)
                    
                    # Add a summary card at the bottom
                    st.markdown("""
                        <div class="summary-card">
                            <h3>🎉 Analysis Complete!</h3>
                            <p>Review the tabs above for detailed insights about your project's uniqueness, potential improvements, development plan, and related resources. The tutorial videos and GitHub projects have been specifically selected based on the analysis of your project!</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                except (KeyError, IndexError) as e:
                    st.error("❌ Error processing API response. Please try again.")
                    st.error(f"Error details: {str(e)}")