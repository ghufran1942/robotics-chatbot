#!/usr/bin/env python3
"""
Example usage of the Robotics Chatbot
Demonstrates how to use the chatbot programmatically.
"""

import requests
import json
import time
from typing import Dict, List

# Configuration
API_BASE_URL = "http://localhost:8000"

def call_api(endpoint: str, method: str = "GET", data: Dict = None) -> Dict:
    """Make API calls to the backend."""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API Error: {str(e)}")
        return None

def load_topic(topic: str) -> bool:
    """Load a specific topic."""
    print(f"📚 Loading topic: {topic}")
    response = call_api("/load_topic", method="POST", data={"topic": topic})
    
    if response:
        print(f"✅ Loaded {response['document_count']} documents")
        return True
    else:
        print("❌ Failed to load topic")
        return False

def ask_question(topic: str, question: str) -> Dict:
    """Ask a question about a topic."""
    print(f"🤖 Asking: {question}")
    response = call_api("/ask", method="POST", data={
        "topic": topic,
        "question": question
    })
    
    if response:
        print(f"✅ Got answer with {response['num_sources']} sources")
        return response
    else:
        print("❌ Failed to get answer")
        return None

def get_topic_summary(topic: str) -> str:
    """Get a summary of a topic."""
    print(f"📋 Getting summary for: {topic}")
    response = call_api(f"/topic_summary/{topic}")
    
    if response:
        print("✅ Got topic summary")
        return response["summary"]
    else:
        print("❌ Failed to get summary")
        return None

def display_answer(answer_data: Dict):
    """Display the answer in a formatted way."""
    print("\n" + "="*60)
    print("🤖 ANSWER")
    print("="*60)
    print(answer_data["answer"])
    
    print("\n" + "-"*60)
    print("📚 SOURCES")
    print("-"*60)
    
    for i, source in enumerate(answer_data["sources"], 1):
        print(f"\nSource {i}:")
        print(f"  Title: {source.get('title', 'Unknown')}")
        print(f"  Source: {source.get('source', 'unknown')}")
        print(f"  Relevance: {source.get('relevance_score', 0):.3f}")
        
        if source.get('authors'):
            print(f"  Authors: {', '.join(source['authors'])}")
        
        if source.get('url'):
            print(f"  URL: {source['url']}")

def main():
    """Main example function."""
    print("🤖 Robotics Chatbot - Example Usage")
    print("="*50)
    
    # Check if API is running
    print("🔍 Checking API status...")
    status = call_api("/")
    if not status:
        print("❌ API is not running. Please start the backend server first:")
        print("   python backend/main.py")
        return
    
    print("✅ API is running!")
    
    # Example 1: Load and ask about PID controllers
    print("\n" + "="*50)
    print("EXAMPLE 1: PID Controllers")
    print("="*50)
    
    if load_topic("PID controller"):
        # Ask a question
        answer = ask_question("PID controller", "Explain how PID controllers work in robotics and what are the key parameters?")
        if answer:
            display_answer(answer)
    
    # Example 2: Load and ask about SLAM
    print("\n" + "="*50)
    print("EXAMPLE 2: SLAM")
    print("="*50)
    
    if load_topic("SLAM"):
        # Ask a question
        answer = ask_question("SLAM", "What are the main applications of SLAM in autonomous vehicles and robotics?")
        if answer:
            display_answer(answer)
    
    # Example 3: Get topic summary
    print("\n" + "="*50)
    print("EXAMPLE 3: Topic Summary")
    print("="*50)
    
    summary = get_topic_summary("PID controller")
    if summary:
        print("📖 TOPIC SUMMARY")
        print("-"*30)
        print(summary)
    
    # Example 4: List available topics
    print("\n" + "="*50)
    print("EXAMPLE 4: Available Topics")
    print("="*50)
    
    topics = call_api("/topics")
    if topics:
        print("📚 Existing Topics:")
        for topic in topics.get("existing_topics", []):
            print(f"  - {topic}")
        
        print("\n💡 Suggested Topics:")
        for topic in topics.get("suggested_topics", [])[:5]:  # Show first 5
            print(f"  - {topic}")
    
    print("\n" + "="*50)
    print("✅ Example completed!")
    print("🌐 For interactive use, run: streamlit run frontend/app.py")

if __name__ == "__main__":
    main() 