import streamlit as st
import requests
import json
import os
from dotenv import load_dotenv
from googleapiclient.discovery import build

# Load environment variables
load_dotenv()
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Page config
st.set_page_config(page_title="Course Finder", page_icon="📚", layout="wide")

# Styling
st.markdown("""
<style>
    .resource-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #ddd;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    .resource-card:hover {
        transform: translateY(-5px);
    }
    .button {
        display: inline-block;
        padding: 10px 20px;
        background-color: #FF0000;
        color: white !important;
        text-decoration: none;
        border-radius: 5px;
        margin-top: 10px;
        transition: all 0.3s;
    }
    .button:hover {
        background-color: #CC0000;
    }
    .title { color: #1E1E1E; font-size: 1.2em; margin-bottom: 10px; }
    .stats { color: #666; font-size: 0.9em; margin: 5px 0; }
</style>
""", unsafe_allow_html=True)

def clean_response(text):
    """Clean and extract JSON from response text."""
    try:
        start = text.find('{')
        end = text.rfind('}') + 1
        if start >= 0 and end > start:
            json_str = text[start:end]
            # Validate JSON structure
            data = json.loads(json_str)
            if 'courses' in data:
                return data
    except:
        pass
    return None

def get_youtube_courses(search_query):
    try:
        # Create YouTube API client
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        
        # Search for playlists related to the query
        search_response = youtube.search().list(
            q=f"{search_query} course tutorial",
            type='playlist',
            part='id,snippet',
            maxResults=6,
            relevanceLanguage='en'
        ).execute()
        
        courses = []
        for item in search_response.get('items', []):
            if 'id' in item and 'playlistId' in item['id']:
                # Get playlist details including video count
                playlist_response = youtube.playlists().list(
                    part='snippet,contentDetails',
                    id=item['id']['playlistId']
                ).execute()
                
                if playlist_response['items']:
                    playlist = playlist_response['items'][0]
                    video_count = playlist['contentDetails']['itemCount']
                    
                    courses.append({
                        'title': item['snippet']['title'],
                        'url': f"https://youtube.com/playlist?list={item['id']['playlistId']}",
                        'instructor': item['snippet']['channelTitle'],
                        'duration': f"{video_count} videos",
                        'description': item['snippet']['description'][:200] + '...' if len(item['snippet']['description']) > 200 else item['snippet']['description']
                    })
        
        return courses
    except Exception as e:
        st.error(f"Error fetching playlists: {str(e)}")
        return None

def display_courses(courses):
    if not courses:
        st.warning("No courses found. Please try another search.")
        return

    col1, col2 = st.columns(2)
    for i, course in enumerate(courses):
        with col1 if i % 2 == 0 else col2:
            st.markdown(f"""
            <div class="resource-card">
                <h3 class="title">{course['title']}</h3>
                <p class="stats">👨‍🏫 {course['instructor']}</p>
                <p class="stats">⏱️ {course['duration']}</p>
                <p>{course['description']}</p>
                <a href="{course['url']}" target="_blank" class="button">
                    Watch Course 📺
                </a>
            </div>
            """, unsafe_allow_html=True)

# Main UI
st.title("📚 Course Finder")
st.markdown("Find the best YouTube courses for any skill")

# Search input
search_query = st.text_input(
    "Enter skill or job role:",
    placeholder="e.g., Python, Web Development, Data Science",
    key="search_input"
)

# Search button
if st.button("🔍 Find Courses", type="primary"):
    if search_query:
        with st.spinner(f"Searching for {search_query} courses..."):
            courses = get_youtube_courses(search_query)
            display_courses(courses)
    else:
        st.warning("Please enter a search query")