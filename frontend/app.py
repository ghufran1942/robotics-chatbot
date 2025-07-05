import streamlit as st
import requests
import json
import time
from typing import List, Dict
import os
import sys

# Add the parent directory to the path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import COMMON_ROBOTICS_TOPICS

# Configuration
API_BASE_URL = "http://localhost:8000"

def init_session_state():
    """Initialize session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "current_topic" not in st.session_state:
        st.session_state.current_topic = ""
    if "available_topics" not in st.session_state:
        st.session_state.available_topics = []

def call_api(endpoint: str, method: str = "GET", data: Dict = None) -> Dict:
    """Make API calls to the backend."""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        return None

def load_available_topics():
    """Load available topics from the API."""
    try:
        response = call_api("/topics")
        if response:
            st.session_state.available_topics = response.get("existing_topics", [])
            return response
    except Exception as e:
        st.error(f"Error loading topics: {e}")
    return None

def load_topic(topic: str):
    """Load a specific topic."""
    try:
        with st.spinner(f"Loading documents for '{topic}'..."):
            response = call_api("/load_topic", method="POST", data={"topic": topic})
            if response:
                st.session_state.current_topic = topic
                st.success(f"✅ Loaded {response['document_count']} documents for '{topic}'")
                return True
    except Exception as e:
        st.error(f"Error loading topic: {e}")
    return False

def ask_question(topic: str, question: str):
    """Ask a question about a topic."""
    try:
        with st.spinner("Generating answer..."):
            response = call_api("/ask", method="POST", data={
                "topic": topic,
                "question": question
            })
            if response:
                return response
    except Exception as e:
        st.error(f"Error asking question: {e}")
    return None

def auto_generate_topics():
    """Auto-generate common robotics topics."""
    try:
        with st.spinner("Auto-generating common robotics topics..."):
            response = call_api("/auto_generate_topics", method="POST")
            if response:
                st.success("✅ Auto-generation completed!")
                load_available_topics()  # Refresh the topic list
                return response
    except Exception as e:
        st.error(f"Error auto-generating topics: {e}")
    return None

def display_sources(sources: List[Dict]):
    """Display sources used in the answer."""
    if not sources:
        return
    
    st.subheader("📚 Sources Used")
    
    for i, source in enumerate(sources, 1):
        with st.expander(f"Source {i}: {source.get('title', 'Unknown')}"):
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.write("**Source Type:**")
                st.write(f"📄 {source.get('source', 'unknown')}")
                
                if source.get('authors'):
                    st.write("**Authors:**")
                    st.write(", ".join(source['authors']))
                
                if source.get('published'):
                    st.write("**Published:**")
                    st.write(source['published'])
                
                st.write("**Relevance Score:**")
                st.write(f"{source.get('relevance_score', 0):.3f}")
            
            with col2:
                if source.get('url'):
                    st.write("**URL:**")
                    st.write(f"[Link]({source['url']})")

def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="🤖 Robotics Chatbot",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    init_session_state()
    
    # Add new session state variables for new features
    if "use_arxiv" not in st.session_state:
        st.session_state.use_arxiv = True
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
        color: black;
    }
    .bot-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
        color: black;
    }
    .stButton > button {
        width: 100%;
        border-radius: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<h1 class="main-header">🤖 Robotics Chatbot</h1>', unsafe_allow_html=True)
    st.markdown("### Your AI-powered guide to robotics concepts and applications")
    
    # Sidebar
    with st.sidebar:
        st.header("🎯 Topic Management")
        
        # Load available topics
        if st.button("🔄 Refresh Topics"):
            load_available_topics()
        
        # Display available topics
        if st.session_state.available_topics:
            st.subheader("📚 Available Topics")
            for topic in st.session_state.available_topics:
                if st.button(f"📖 {topic}", key=f"topic_{topic}"):
                    if load_topic(topic):
                        st.rerun()
        
        # Suggested topics
        st.subheader("💡 Suggested Topics")
        for topic in COMMON_ROBOTICS_TOPICS[:10]:  # Show first 10
            if st.button(f"➕ {topic}", key=f"suggest_{topic}"):
                if load_topic(topic):
                    st.rerun()
        
        # Auto-generate topics
        st.subheader("⚡ Quick Setup")
        if st.button("🚀 Auto-Generate Common Topics"):
            result = auto_generate_topics()
            if result:
                st.rerun()
        
        # PDF Upload Section
        st.subheader("📄 PDF Upload")
        uploaded_file = st.file_uploader(
            "Upload a PDF document",
            type=['pdf'],
            help="Upload textbooks, research papers, or notes to include in answers"
        )
        
        if uploaded_file is not None:
            if st.button("📤 Process PDF"):
                with st.spinner("Processing PDF..."):
                    try:
                        # Upload file to backend
                        files = {"file": uploaded_file}
                        response = requests.post(f"{API_BASE_URL}/upload_pdf", files=files)
                        
                        if response.status_code == 200:
                            result = response.json()
                            st.success(f"✅ {result['message']}")
                            st.info(f"📊 {result['chunk_count']} chunks created")
                            st.rerun()
                        else:
                            st.error(f"❌ Error: {response.json().get('detail', 'Unknown error')}")
                    except Exception as e:
                        st.error(f"❌ Upload failed: {e}")
        
        # ArXiv Integration
        st.subheader("🔬 ArXiv Papers")
        use_arxiv = st.checkbox(
            "Use ArXiv Papers 🔎",
            value=st.session_state.use_arxiv,
            help="Include recent arXiv papers in search results"
        )
        st.session_state.use_arxiv = use_arxiv
        
        if use_arxiv:
            arxiv_query = st.text_input(
                "Search arXiv for papers:",
                placeholder="e.g., 'PID control robotics'",
                help="Search for recent papers on this topic"
            )
            
            if st.button("🔍 Search ArXiv"):
                if arxiv_query:
                    with st.spinner("Searching arXiv..."):
                        try:
                            response = requests.post(f"{API_BASE_URL}/search_arxiv", 
                                                  json={"query": arxiv_query, "max_results": 5})
                            
                            if response.status_code == 200:
                                result = response.json()
                                st.success(f"✅ Found {result['paper_count']} papers")
                                
                                # Show paper titles
                                for i, paper in enumerate(result['papers'], 1):
                                    st.write(f"{i}. **{paper['title']}**")
                                    st.write(f"   Authors: {', '.join(paper['authors'][:3])}")
                                    st.write(f"   Published: {paper['published']}")
                                st.rerun()
                            else:
                                st.error(f"❌ Error: {response.json().get('detail', 'Unknown error')}")
                        except Exception as e:
                            st.error(f"❌ Search failed: {e}")
        
        # Current topic display
        if st.session_state.current_topic:
            st.subheader("🎯 Current Topic")
            st.info(f"**{st.session_state.current_topic}**")
            
            if st.button("🗑️ Clear Topic"):
                st.session_state.current_topic = ""
                st.session_state.messages = []
                st.rerun()
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Chat interface
        st.subheader("💬 Ask Questions")
        
        # Topic selection
        if not st.session_state.current_topic:
            st.info("👈 Please select a topic from the sidebar to start asking questions!")
        else:
            # Question input
            question = st.text_input(
                "Ask a question about robotics:",
                placeholder=f"e.g., 'Explain how {st.session_state.current_topic} works in robotics'",
                key="question_input"
            )
            
            if st.button("🚀 Ask Question", disabled=not question):
                if question:
                    # Add user message
                    st.session_state.messages.append({
                        "role": "user",
                        "content": question,
                        "timestamp": time.time()
                    })
                    
                    # Get answer
                    answer_data = ask_question(st.session_state.current_topic, question)
                    
                    if answer_data:
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": answer_data["answer"],
                            "sources": answer_data["sources"],
                            "timestamp": time.time()
                        })
                    
                    st.rerun()
            
            # Display chat messages
            if st.session_state.messages:
                st.subheader("💭 Conversation History")
                
                for message in st.session_state.messages:
                    if message["role"] == "user":
                        st.markdown(f"""
                        <div class="chat-message user-message">
                            <strong>👤 You:</strong><br>
                            {message["content"]}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="chat-message bot-message">
                            <strong>🤖 Assistant:</strong><br>
                            {message["content"]}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Display sources if available
                        if "sources" in message and message["sources"]:
                            display_sources(message["sources"])
    
    with col2:
        # Information panel
        st.subheader("ℹ️ Information")
        
        if st.session_state.current_topic:
            st.info(f"**Current Topic:** {st.session_state.current_topic}")
            
            # Get topic summary
            if st.button("📋 Get Topic Summary"):
                try:
                    with st.spinner("Generating summary..."):
                        response = call_api(f"/topic_summary/{st.session_state.current_topic}")
                        if response:
                            st.subheader("📖 Topic Summary")
                            st.write(response["summary"])
                except Exception as e:
                    st.error(f"Error getting summary: {e}")
        else:
            st.info("No topic selected")
        
        # Document Sources
        st.subheader("📚 Document Sources")
        
        # Get source statistics
        try:
            response = call_api("/arxiv_stats")
            if response:
                source_stats = response.get("source_stats", {})
                
                # Display statistics
                col_stats1, col_stats2 = st.columns(2)
                with col_stats1:
                    st.metric("ArXiv Papers", source_stats.get("arxiv", 0))
                    st.metric("Uploaded PDFs", source_stats.get("uploaded_pdf", 0))
                with col_stats2:
                    st.metric("Web Sources", source_stats.get("web_search", 0))
                    st.metric("Stack Exchange", source_stats.get("stack_exchange", 0))
                
                # Show uploaded files
                uploaded_response = call_api("/uploaded_files")
                if uploaded_response and uploaded_response.get("files"):
                    st.write("**📄 Uploaded Files:**")
                    for file_info in uploaded_response["files"]:
                        with st.expander(f"📄 {file_info['filename']}"):
                            st.write(f"**Size:** {file_info['size']} bytes")
                            st.write(f"**Uploaded:** {file_info['uploaded']}")
                            if st.button(f"🗑️ Delete {file_info['filename']}", key=f"del_{file_info['filename']}"):
                                try:
                                    delete_response = requests.delete(f"{API_BASE_URL}/uploaded_file/{file_info['filename']}")
                                    if delete_response.status_code == 200:
                                        st.success("File deleted!")
                                        st.rerun()
                                    else:
                                        st.error("Failed to delete file")
                                except Exception as e:
                                    st.error(f"Error: {e}")
        except Exception as e:
            st.info("No document sources available")
        
        # Management buttons
        st.subheader("⚙️ Management")
        
        col_mgmt1, col_mgmt2 = st.columns(2)
        
        with col_mgmt1:
            if st.button("🗑️ Clear ArXiv Papers"):
                try:
                    response = requests.delete(f"{API_BASE_URL}/arxiv_papers")
                    if response.status_code == 200:
                        result = response.json()
                        st.success(f"✅ {result['message']}")
                        st.rerun()
                    else:
                        st.error("Failed to clear papers")
                except Exception as e:
                    st.error(f"Error: {e}")
        
        with col_mgmt2:
            if st.button("🔄 Refresh Sources"):
                st.rerun()
        
        # Quick actions
        st.subheader("⚡ Quick Actions")
        
        if st.button("🔍 Load Sample Topics"):
            sample_topics = ["PID controller", "SLAM", "robotic grippers"]
            for topic in sample_topics:
                if load_topic(topic):
                    break
            st.rerun()
        
        if st.button("📊 View API Status"):
            try:
                response = call_api("/")
                if response:
                    st.json(response)
            except Exception as e:
                st.error(f"API not available: {e}")
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
            <p>🤖 Robotics Chatbot - Powered by LangChain, FAISS, and Google Gemini</p>
            <p>Built for educational purposes in robotics and AI</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main() 