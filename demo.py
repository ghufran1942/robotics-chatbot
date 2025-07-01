#!/usr/bin/env python3
"""
Demo script for Robotics Chatbot
Shows the system in action with sample questions and answers.
"""

import os
import sys
import time
from typing import Dict, List

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def demo_without_api():
    """Demo the system structure without requiring API keys."""
    print("🤖 Robotics Chatbot - Demo Mode")
    print("=" * 50)
    
    print("📁 Project Structure:")
    print("robotics_chatbot/")
    print("├── backend/")
    print("│   ├── main.py              # FastAPI backend server")
    print("│   ├── loaders.py           # Document loading from various sources")
    print("│   ├── vectorstore.py       # FAISS vector store management")
    print("│   └── summarizer.py        # LangChain + Gemini summarization")
    print("├── frontend/")
    print("│   └── app.py              # Streamlit web interface")
    print("├── config.py               # Configuration and constants")
    print("├── requirements.txt        # Python dependencies")
    print("└── README.md              # Documentation")
    
    print("\n🔧 Core Components:")
    print("1. Document Loaders - Fetch from arXiv, ROS docs, Stack Exchange")
    print("2. Vector Store - FAISS-based semantic search")
    print("3. Summarizer - Google Gemini-powered answer generation")
    print("4. Web Interface - Modern Streamlit UI")
    
    print("\n📚 Available Topics:")
    topics = [
        "PID controller", "SLAM", "robotic grippers", "localization",
        "path planning", "computer vision", "sensor fusion", "kinematics",
        "dynamics", "control systems", "machine learning in robotics",
        "autonomous navigation", "manipulation", "human-robot interaction"
    ]
    
    for i, topic in enumerate(topics, 1):
        print(f"   {i:2d}. {topic}")
    
    print("\n💬 Sample Questions:")
    questions = [
        "Explain how PID controllers work in robotics and what are the key parameters?",
        "What are the main applications of SLAM in autonomous vehicles?",
        "How do robotic grippers handle different objects?",
        "What are the mathematical foundations of path planning?",
        "Explain sensor fusion techniques for robot localization"
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"   {i}. {question}")
    
    print("\n🎯 Answer Structure:")
    print("Each answer includes:")
    print("   • Introduction to the concept")
    print("   • Applications in robotics")
    print("   • Mathematical explanation or formulas")
    print("   • Tuning methods and practical considerations")
    print("   • Sources used for grounding")
    
    print("\n🚀 Getting Started:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Set up API keys in .env file")
    print("3. Run the system: python run.py")
    print("4. Open browser to: http://localhost:8501")
    
    print("\n🔗 API Endpoints:")
    endpoints = [
        ("GET /", "API status"),
        ("GET /topics", "List available topics"),
        ("POST /load_topic", "Load documents for a topic"),
        ("POST /ask", "Ask a question about a topic"),
        ("GET /topic_summary/{topic}", "Get topic summary"),
        ("POST /auto_generate_topics", "Auto-generate common topics"),
        ("DELETE /topic/{topic}", "Delete a topic")
    ]
    
    for endpoint, description in endpoints:
        print(f"   {endpoint:<25} - {description}")
    
    print("\n📊 Features:")
    features = [
        "Natural language question processing",
        "Multi-source document retrieval",
        "AI-powered answer generation",
        "Vector-based semantic search",
        "Source citation and grounding",
        "Topic management and persistence",
        "Modern web interface",
        "Real-time chat experience"
    ]
    
    for feature in features:
        print(f"   ✅ {feature}")
    
    print("\n🎓 Educational Benefits:")
    benefits = [
        "Learn robotics concepts interactively",
        "Access to academic papers and documentation",
        "Structured, comprehensive answers",
        "Practical implementation guidance",
        "Mathematical foundations explained",
        "Real-world applications highlighted"
    ]
    
    for benefit in benefits:
        print(f"   📚 {benefit}")

def demo_with_api():
    """Demo with actual API calls (requires running backend)."""
    try:
        import requests
        
        print("🤖 Robotics Chatbot - Live Demo")
        print("=" * 50)
        
        # Check if API is running
        try:
            response = requests.get("http://localhost:8000/", timeout=5)
            if response.status_code == 200:
                print("✅ Backend API is running!")
                
                # Get available topics
                topics_response = requests.get("http://localhost:8000/tics")
                if topics_response.status_code == 200:
                    topics_data = topics_response.json()
                    print(f"📚 Found {len(topics_data.get('existing_topics', []))} existing topics")
                    print(f"💡 {len(topics_data.get('suggested_topics', []))} suggested topics available")
                
                # Demo loading a topic
                print("\n📚 Loading 'PID controller' topic...")
                load_response = requests.post("http://localhost:8000/load_topic", 
                                           json={"topic": "PID controller"})
                if load_response.status_code == 200:
                    load_data = load_response.json()
                    print(f"✅ Loaded {load_data['document_count']} documents")
                    
                    # Demo asking a question
                    print("\n🤖 Asking: 'Explain PID controllers in robotics'")
                    ask_response = requests.post("http://localhost:8000/ask",
                                              json={
                                                  "topic": "PID controller",
                                                  "question": "Explain PID controllers in robotics"
                                              })
                    if ask_response.status_code == 200:
                        answer_data = ask_response.json()
                        print(f"✅ Got answer with {answer_data['num_sources']} sources")
                        print("\n📝 Answer preview:")
                        print(answer_data['answer'][:200] + "...")
                    else:
                        print("❌ Failed to get answer")
                else:
                    print("❌ Failed to load topic")
            else:
                print("❌ Backend API is not responding correctly")
                
        except requests.exceptions.ConnectionError:
            print("❌ Backend API is not running")
            print("💡 Start it with: python backend/main.py")
            
    except ImportError:
        print("❌ Requests library not available")
        print("💡 Install with: pip install requests")

def main():
    """Main demo function."""
    print("🤖 Robotics Chatbot Demo")
    print("=" * 50)
    
    # Check if we can import the modules
    try:
        from config import COMMON_ROBOTICS_TOPICS
        print("✅ Configuration loaded successfully")
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return
    
    # Show demo without API
    demo_without_api()
    
    # Try to show live demo if possible
    print("\n" + "=" * 50)
    print("🌐 Live Demo (if backend is running)")
    print("=" * 50)
    
    try:
        demo_with_api()
    except Exception as e:
        print(f"⚠️  Live demo not available: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Demo completed!")
    print("📖 For full functionality, see README.md")
    print("🚀 To run the system: python run.py")

if __name__ == "__main__":
    main() 