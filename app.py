import streamlit as st
import google.generativeai as genai
from googleapiclient.discovery import build
import os
from dotenv import load_dotenv

load_dotenv()
# Get environment variables
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_API_KEY_BACKUP = os.environ.get("GEMINI_API_KEY_BACKUP")
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")

# Configure primary Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# Gemini function with fallback
def get_gemini_answer(question):
    try:
        response = model.generate_content(question)
        return response.text
    except Exception as e:
        if GEMINI_API_KEY_BACKUP:
            try:
                genai.configure(api_key=GEMINI_API_KEY_BACKUP)
                backup_model = genai.GenerativeModel("gemini-1.5-flash")
                response = backup_model.generate_content(question)
                return f"(Using Backup API)\n{response.text}"
            except Exception as backup_e:
                return f"❌ Error from Gemini (Backup failed too): {backup_e}"
        return f"❌ Error from Gemini: {e}"

# YouTube function
def get_youtube_video_link(query):
    try:
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        request = youtube.search().list(
            q=query,
            part='snippet',
            maxResults=1,
            type='video'
        )
        response = request.execute()
        video = response['items'][0]
        title = video['snippet']['title']
        video_id = video['id']['videoId']
        return f"[🎬 {title}](https://www.youtube.com/watch?v={video_id})"
    except Exception as e:
        return f"❌ Error from YouTube: {e}"

# Page configuration
st.set_page_config(page_title="🎓 Gemini Study Assistant", layout="centered")

# Custom background and style
st.markdown("""
    <style>
        body {
            background: linear-gradient(to right, #fdfbfb, #ebedee);
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        .card {
            background-color: #ffffff;
            padding: 20px;
            margin: 10px 0;
            border-radius: 10px;
            box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.1);
        }
        .title {
            font-size: 2.5rem;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.markdown("## 🧠 AI Agent for Study")
st.sidebar.markdown("Ask any academic or general question and get an AI-powered answer along with a helpful YouTube video!")

# Main Title
st.markdown('<h1 class="title">🎓 Study Assistant</h1>', unsafe_allow_html=True)
st.write("Ask a question below and get answers powered by Gemini + a YouTube resource.")

# Input
question = st.text_input("📌 What do you want to learn today?")

if st.button("🔍 Get Answer"):
    if not question.strip():
        st.warning("⚠️ Please enter a question first.")
    else:
        with st.spinner("🧠 Thinking..."):
            gemini_response = get_gemini_answer(question)
            youtube_response = get_youtube_video_link(question)

        # Gemini answer
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 🤖 Gemini Answer")
        st.write(gemini_response)
        st.markdown('</div>', unsafe_allow_html=True)

        # YouTube section
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 🎥 YouTube Resource")
        st.markdown(youtube_response, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
