#!/usr/bin/env python3
"""
Robotics Chatbot Frontend with Three Chat Modes
- Research Chat: For research questions and paper analysis
- Tutorial/How-to Chat: For code tutorials with library documentation
- Explanation Chat: For concept explanations with complexity levels
"""

import streamlit as st
import requests
import json
from typing import Dict, List, Optional
import time

# Page configuration
st.set_page_config(
    page_title="Robotics Chatbot",
    page_icon="Chat",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .chat-mode-selector {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .mode-card {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 2px solid #e0e0e0;
        margin-bottom: 1rem;
    }
    .mode-card.active {
        border-color: #1f77b4;
        background-color: #f8f9ff;
    }
    .stButton > button {
        width: 100%;
    }
    .source-badge {
        display: inline-block;
        background-color: #e3f2fd;
        color: #1976d2;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.75rem;
        margin: 0.25rem;
    }
    .reference-link {
        color: #1976d2;
        text-decoration: none;
    }
    .reference-link:hover {
        text-decoration: underline;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'current_mode' not in st.session_state:
    st.session_state.current_mode = "research"
if 'processing_state' not in st.session_state:
    st.session_state.processing_state = "idle"

def get_backend_url():
    """Get backend URL from config or default."""
    return "http://localhost:8000"

def call_backend_api(endpoint: str, data: Dict) -> Dict:
    """Make API call to backend."""
    try:
        url = f"{get_backend_url()}/{endpoint}"
        response = requests.post(url, json=data, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Backend connection error: {str(e)}")
        return {"success": False, "error": str(e)}
    except Exception as e:
        st.error(f"API call error: {str(e)}")
        return {"success": False, "error": str(e)}

def display_chat_message(message: Dict, is_user: bool = False):
    """Display a chat message with proper formatting."""
    if is_user:
        st.markdown(f"**You:** {message}")
    else:
        if isinstance(message, dict):
            # Handle structured response
            st.markdown(f"**Assistant:** {message.get('final_answer', 'No response')}")
            
            # Display source information if available
            if message.get('source'):
                st.markdown(f"<span class='source-badge'>Source: {message['source']}</span>", 
                           unsafe_allow_html=True)
            
            # Display references if available
            if message.get('references'):
                st.markdown("**References:**")
                for ref in message['references']:
                    if ref.get('url'):
                        st.markdown(f"- [{ref.get('title', 'Reference')}]({ref['url']})")
                    else:
                        st.markdown(f"- {ref.get('title', 'Reference')}")
        else:
            st.markdown(f"**Assistant:** {message}")

def research_chat_interface():
    """Research Chat interface for research questions and paper analysis."""
    st.subheader("🔬 Research Chat")
    st.markdown("Ask research questions about robotics topics. Upload papers or let the system fetch from ArXiv.")
    
    # Research question input
    question = st.text_area(
        "Research Question",
        placeholder="Enter your research question about robotics...",
        height=100
    )
    
    # Paper upload section
    st.markdown("### 📄 Research Papers")
    uploaded_files = st.file_uploader(
        "Upload research papers (PDF)",
        type=['pdf'],
        accept_multiple_files=True,
        help="Upload PDF research papers for analysis"
    )
    
    # Process research question
    if st.button("🔍 Analyze Research Question", type="primary"):
        if not question.strip():
            st.error("Please enter a research question.")
            return
        
        st.session_state.processing_state = "processing"
        
        with st.spinner("Processing research question..."):
            # Prepare uploaded papers data
            uploaded_papers = []
            if uploaded_files:
                for file in uploaded_files:
                    uploaded_papers.append({
                        "filename": file.name,
                        "content": file.read().decode('utf-8', errors='ignore')
                    })
            
            # Call research chat API
            result = call_backend_api("chat/research", {
                "question": question,
                "uploaded_papers": uploaded_papers
            })
            
            if result.get("success"):
                # Add to chat history
                st.session_state.chat_history.append({
                    "user": question,
                    "assistant": result,
                    "mode": "research",
                    "timestamp": time.time()
                })
                
                st.session_state.processing_state = "completed"
                st.success("Research analysis completed!")
                st.rerun()
            else:
                st.error(f"Error processing research question: {result.get('error', 'Unknown error')}")
                st.session_state.processing_state = "error"

def tutorial_chat_interface():
    """Tutorial/How-to Chat interface for code tutorials."""
    st.subheader("📚 Tutorial/How-to Chat")
    st.markdown("Generate tutorials and how-to guides for robotics libraries and frameworks.")
    
    # Library information
    col1, col2 = st.columns(2)
    with col1:
        library_name = st.text_input(
            "Library/Framework Name",
            placeholder="e.g., ROS, PyTorch, TensorFlow",
            help="Enter the name of the robotics library or framework"
        )
    
    with col2:
        doc_url = st.text_input(
            "Documentation URL",
            placeholder="https://docs.example.com",
            help="Link to the official documentation"
        )
    
    # Tutorial request
    request_text = st.text_area(
        "Tutorial Request",
        placeholder="What would you like to learn? e.g., 'How to implement PID control'",
        height=100
    )
    
    # Output mode selection
    output_mode = st.radio(
        "Output Mode",
        ["Code", "Example"],
        help="Choose whether to focus on code implementation or practical examples"
    )
    
    # Process tutorial request
    if st.button("📖 Generate Tutorial", type="primary"):
        if not request_text.strip() or not library_name.strip():
            st.error("Please enter both a tutorial request and library name.")
            return
        
        st.session_state.processing_state = "processing"
        
        with st.spinner("Generating tutorial..."):
            result = call_backend_api("chat/tutorial", {
                "request": request_text,
                "library_name": library_name,
                "doc_url": doc_url,
                "output_mode": output_mode
            })
            
            if result.get("success"):
                # Add to chat history
                st.session_state.chat_history.append({
                    "user": f"Tutorial: {request_text} (Library: {library_name}, Mode: {output_mode})",
                    "assistant": result,
                    "mode": "tutorial",
                    "timestamp": time.time()
                })
                
                st.session_state.processing_state = "completed"
                st.success("Tutorial generated successfully!")
                st.rerun()
            else:
                st.error(f"Error generating tutorial: {result.get('error', 'Unknown error')}")
                st.session_state.processing_state = "error"

def explanation_chat_interface():
    """Explanation Chat interface for concept explanations."""
    st.subheader("💡 Explanation Chat")
    st.markdown("Get detailed explanations of robotics concepts with adjustable complexity levels.")
    
    # Concept to explain
    request_text = st.text_area(
        "Concept to Explain",
        placeholder="What robotics concept would you like explained? e.g., 'PID control', 'SLAM', 'Computer Vision'",
        height=100
    )
    
    # Complexity and output mode selection
    col1, col2 = st.columns(2)
    with col1:
        complexity_level = st.selectbox(
            "Explanation Complexity",
            ["Beginner", "Intermediate", "Expert"],
            help="Choose the complexity level for the explanation"
        )
    
    with col2:
        output_mode = st.radio(
            "Output Mode",
            ["Example", "Code"],
            help="Choose whether to focus on examples or code implementation"
        )
    
    # Process explanation request
    if st.button("💡 Generate Explanation", type="primary"):
        if not request_text.strip():
            st.error("Please enter a concept to explain.")
            return
        
        st.session_state.processing_state = "processing"
        
        with st.spinner("Generating explanation..."):
            result = call_backend_api("chat/explanation", {
                "request": request_text,
                "complexity_level": complexity_level,
                "output_mode": output_mode
            })
            
            if result.get("success"):
                # Add to chat history
                st.session_state.chat_history.append({
                    "user": f"Explanation: {request_text} (Level: {complexity_level}, Mode: {output_mode})",
                    "assistant": result,
                    "mode": "explanation",
                    "timestamp": time.time()
                })
                
                st.session_state.processing_state = "completed"
                st.success("Explanation generated successfully!")
                st.rerun()
            else:
                st.error(f"Error generating explanation: {result.get('error', 'Unknown error')}")
                st.session_state.processing_state = "error"

def display_chat_history():
    """Display chat history with mode-specific formatting."""
    if not st.session_state.chat_history:
        return
    
    st.markdown("### 💬 Chat History")
    
    for i, chat in enumerate(st.session_state.chat_history):
        with st.expander(f"Chat {i+1} - {chat['mode'].title()} Mode", expanded=False):
            # Display user message
            st.markdown(f"**User:** {chat['user']}")
            
            # Display assistant response
            if isinstance(chat['assistant'], dict):
                # Show the 3-step process if available
                if chat['assistant'].get('raw_input') and chat['assistant'].get('improved_prompt'):
                    with st.expander("🔍 3-Step Processing Details", expanded=False):
                        st.markdown(f"**Original Input:** {chat['assistant']['raw_input']}")
                        st.markdown(f"**Enhanced Prompt:** {chat['assistant']['improved_prompt']}")
                
                # Display final answer
                st.markdown(f"**Assistant:** {chat['assistant'].get('final_answer', 'No response')}")
                
                # Display source information
                if chat['assistant'].get('source'):
                    st.markdown(f"<span class='source-badge'>Source: {chat['assistant']['source']}</span>", 
                               unsafe_allow_html=True)
                
                # Display mode-specific information
                if chat['mode'] == 'research' and chat['assistant'].get('paper_count'):
                    st.markdown(f"📄 Papers analyzed: {chat['assistant']['paper_count']}")
                elif chat['mode'] == 'tutorial' and chat['assistant'].get('library_name'):
                    st.markdown(f"📚 Library: {chat['assistant']['library_name']}")
                elif chat['mode'] == 'explanation' and chat['assistant'].get('complexity_level'):
                    st.markdown(f"🎯 Complexity: {chat['assistant']['complexity_level']}")
            else:
                st.markdown(f"**Assistant:** {chat['assistant']}")

def main():
    """Main application function."""
    st.title("🤖 Robotics Chatbot - Multi-Mode Interface")
    st.markdown("Choose your chat mode and start exploring robotics topics!")
    
    # Chat mode selector
    st.markdown("### 🎯 Select Chat Mode")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔬 Research Chat", use_container_width=True):
            st.session_state.current_mode = "research"
            st.rerun()
    
    with col2:
        if st.button("📚 Tutorial Chat", use_container_width=True):
            st.session_state.current_mode = "tutorial"
            st.rerun()
    
    with col3:
        if st.button("💡 Explanation Chat", use_container_width=True):
            st.session_state.current_mode = "explanation"
            st.rerun()
    
    # Display current mode indicator
    mode_descriptions = {
        "research": "🔬 **Research Chat**: Ask research questions and analyze papers",
        "tutorial": "📚 **Tutorial Chat**: Generate code tutorials and how-to guides",
        "explanation": "💡 **Explanation Chat**: Get concept explanations with adjustable complexity"
    }
    
    st.markdown(mode_descriptions[st.session_state.current_mode])
    st.markdown("---")
    
    # Display mode-specific interface
    if st.session_state.current_mode == "research":
        research_chat_interface()
    elif st.session_state.current_mode == "tutorial":
        tutorial_chat_interface()
    elif st.session_state.current_mode == "explanation":
        explanation_chat_interface()
    
    # Display chat history
    if st.session_state.chat_history:
        st.markdown("---")
        display_chat_history()
    
    # Clear chat history button
    if st.session_state.chat_history:
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            st.rerun()

if __name__ == "__main__":
    main() 