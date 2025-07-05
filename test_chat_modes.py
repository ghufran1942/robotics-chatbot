#!/usr/bin/env python3
"""
Test script for the three chat modes:
- Research Chat
- Tutorial/How-to Chat  
- Explanation Chat
"""

import requests
import json
import time
from typing import Dict, List

# Configuration
BACKEND_URL = "http://localhost:8000"

def test_backend_health():
    """Test if backend is running."""
    try:
        response = requests.get(f"{BACKEND_URL}/health")
        if response.status_code == 200:
            print("✅ Backend is running")
            return True
        else:
            print("❌ Backend health check failed")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Make sure it's running on localhost:8000")
        return False

def test_research_chat():
    """Test Research Chat mode."""
    print("\n🔬 Testing Research Chat Mode")
    print("=" * 50)
    
    # Test 1: Basic research question
    print("Test 1: Basic research question about PID control")
    research_data = {
        "question": "What are the latest developments in PID control for autonomous vehicles?",
        "uploaded_papers": []
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/chat/research", json=research_data, timeout=60)
        if response.status_code == 200:
            result = response.json()
            print("✅ Research chat API call successful")
            print(f"   Success: {result.get('success', False)}")
            print(f"   Raw input: {result.get('raw_input', 'N/A')}")
            print(f"   Improved prompt: {result.get('improved_prompt', 'N/A')[:100]}...")
            print(f"   Final answer length: {len(result.get('final_answer', ''))}")
            print(f"   Source: {result.get('source', 'N/A')}")
            print(f"   Paper count: {result.get('paper_count', 0)}")
        else:
            print(f"❌ Research chat failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Research chat error: {e}")
    
    # Test 2: Research question with uploaded papers (simulated)
    print("\nTest 2: Research question with simulated uploaded papers")
    research_data_with_papers = {
        "question": "How do neural networks improve robot navigation?",
        "uploaded_papers": [
            {
                "filename": "sample_paper.pdf",
                "content": "This is a sample research paper about neural networks in robotics navigation. The paper discusses various approaches including deep reinforcement learning, convolutional neural networks, and their applications in autonomous robot navigation systems."
            }
        ]
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/chat/research", json=research_data_with_papers, timeout=60)
        if response.status_code == 200:
            result = response.json()
            print("✅ Research chat with papers successful")
            print(f"   Success: {result.get('success', False)}")
            print(f"   Paper count: {result.get('paper_count', 0)}")
        else:
            print(f"❌ Research chat with papers failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Research chat with papers error: {e}")

def test_tutorial_chat():
    """Test Tutorial/How-to Chat mode."""
    print("\n📚 Testing Tutorial/How-to Chat Mode")
    print("=" * 50)
    
    # Test 1: Code mode tutorial
    print("Test 1: Code mode tutorial for ROS")
    tutorial_data_code = {
        "request": "How to implement a basic PID controller in ROS?",
        "library_name": "ROS",
        "doc_url": "https://docs.ros.org/",
        "output_mode": "Code"
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/chat/tutorial", json=tutorial_data_code, timeout=60)
        if response.status_code == 200:
            result = response.json()
            print("✅ Tutorial chat (Code mode) successful")
            print(f"   Success: {result.get('success', False)}")
            print(f"   Library: {result.get('library_name', 'N/A')}")
            print(f"   Output mode: {result.get('output_mode', 'N/A')}")
            print(f"   Final answer length: {len(result.get('final_answer', ''))}")
        else:
            print(f"❌ Tutorial chat (Code mode) failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Tutorial chat (Code mode) error: {e}")
    
    # Test 2: Example mode tutorial
    print("\nTest 2: Example mode tutorial for PyTorch")
    tutorial_data_example = {
        "request": "How to train a neural network for image classification?",
        "library_name": "PyTorch",
        "doc_url": "https://pytorch.org/docs/",
        "output_mode": "Example"
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/chat/tutorial", json=tutorial_data_example, timeout=60)
        if response.status_code == 200:
            result = response.json()
            print("✅ Tutorial chat (Example mode) successful")
            print(f"   Success: {result.get('success', False)}")
            print(f"   Library: {result.get('library_name', 'N/A')}")
            print(f"   Output mode: {result.get('output_mode', 'N/A')}")
            print(f"   Final answer length: {len(result.get('final_answer', ''))}")
        else:
            print(f"❌ Tutorial chat (Example mode) failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Tutorial chat (Example mode) error: {e}")

def test_explanation_chat():
    """Test Explanation Chat mode."""
    print("\n💡 Testing Explanation Chat Mode")
    print("=" * 50)
    
    # Test 1: Beginner level explanation
    print("Test 1: Beginner level explanation of SLAM")
    explanation_data_beginner = {
        "request": "What is SLAM and how does it work?",
        "complexity_level": "Beginner",
        "output_mode": "Example"
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/chat/explanation", json=explanation_data_beginner, timeout=60)
        if response.status_code == 200:
            result = response.json()
            print("✅ Explanation chat (Beginner) successful")
            print(f"   Success: {result.get('success', False)}")
            print(f"   Complexity: {result.get('complexity_level', 'N/A')}")
            print(f"   Output mode: {result.get('output_mode', 'N/A')}")
            print(f"   Final answer length: {len(result.get('final_answer', ''))}")
        else:
            print(f"❌ Explanation chat (Beginner) failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Explanation chat (Beginner) error: {e}")
    
    # Test 2: Expert level explanation with code
    print("\nTest 2: Expert level explanation of computer vision with code")
    explanation_data_expert = {
        "request": "Explain the mathematical foundations of computer vision algorithms",
        "complexity_level": "Expert",
        "output_mode": "Code"
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/chat/explanation", json=explanation_data_expert, timeout=60)
        if response.status_code == 200:
            result = response.json()
            print("✅ Explanation chat (Expert) successful")
            print(f"   Success: {result.get('success', False)}")
            print(f"   Complexity: {result.get('complexity_level', 'N/A')}")
            print(f"   Output mode: {result.get('output_mode', 'N/A')}")
            print(f"   Final answer length: {len(result.get('final_answer', ''))}")
        else:
            print(f"❌ Explanation chat (Expert) failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Explanation chat (Expert) error: {e}")
    
    # Test 3: Intermediate level explanation
    print("\nTest 3: Intermediate level explanation of PID control")
    explanation_data_intermediate = {
        "request": "How do PID controllers work in robotics?",
        "complexity_level": "Intermediate",
        "output_mode": "Example"
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/chat/explanation", json=explanation_data_intermediate, timeout=60)
        if response.status_code == 200:
            result = response.json()
            print("✅ Explanation chat (Intermediate) successful")
            print(f"   Success: {result.get('success', False)}")
            print(f"   Complexity: {result.get('complexity_level', 'N/A')}")
            print(f"   Output mode: {result.get('output_mode', 'N/A')}")
            print(f"   Final answer length: {len(result.get('final_answer', ''))}")
        else:
            print(f"❌ Explanation chat (Intermediate) failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Explanation chat (Intermediate) error: {e}")

def test_error_handling():
    """Test error handling for invalid requests."""
    print("\n⚠️ Testing Error Handling")
    print("=" * 50)
    
    # Test 1: Missing required fields
    print("Test 1: Missing required fields")
    invalid_data = {
        "question": "",  # Empty question
        "uploaded_papers": []
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/chat/research", json=invalid_data, timeout=30)
        if response.status_code == 400:
            print("✅ Properly handled empty question")
        else:
            print(f"❌ Expected 400, got {response.status_code}")
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
    
    # Test 2: Invalid tutorial request
    print("\nTest 2: Invalid tutorial request (missing library name)")
    invalid_tutorial = {
        "request": "How to implement something?",
        "library_name": "",  # Empty library name
        "doc_url": "https://example.com",
        "output_mode": "Code"
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/chat/tutorial", json=invalid_tutorial, timeout=30)
        if response.status_code == 400:
            print("✅ Properly handled missing library name")
        else:
            print(f"❌ Expected 400, got {response.status_code}")
    except Exception as e:
        print(f"❌ Tutorial error handling test failed: {e}")

def test_3step_processing():
    """Test that all modes use the 3-step processing pipeline."""
    print("\n🔄 Testing 3-Step Processing Pipeline")
    print("=" * 50)
    
    test_cases = [
        {
            "mode": "research",
            "data": {
                "question": "What are the applications of machine learning in robotics?",
                "uploaded_papers": []
            }
        },
        {
            "mode": "tutorial",
            "data": {
                "request": "How to create a simple robot simulation?",
                "library_name": "Gazebo",
                "doc_url": "https://gazebosim.org/docs",
                "output_mode": "Code"
            }
        },
        {
            "mode": "explanation",
            "data": {
                "request": "What is reinforcement learning?",
                "complexity_level": "Intermediate",
                "output_mode": "Example"
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['mode'].title()} mode 3-step processing")
        
        try:
            response = requests.post(f"{BACKEND_URL}/chat/{test_case['mode']}", 
                                  json=test_case['data'], timeout=60)
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"   ✅ {test_case['mode'].title()} mode successful")
                    print(f"   Raw input: {result.get('raw_input', 'N/A')}")
                    print(f"   Improved prompt: {result.get('improved_prompt', 'N/A')[:50]}...")
                    print(f"   Final answer: {result.get('final_answer', 'N/A')[:50]}...")
                else:
                    print(f"   ❌ {test_case['mode'].title()} mode failed")
            else:
                print(f"   ❌ {test_case['mode'].title()} mode API error: {response.status_code}")
        except Exception as e:
            print(f"   ❌ {test_case['mode'].title()} mode error: {e}")

def main():
    """Run all tests."""
    print("🤖 Robotics Chatbot - Multi-Mode Testing")
    print("=" * 60)
    
    # Check backend health first
    if not test_backend_health():
        print("\n❌ Backend is not available. Please start the backend first.")
        return
    
    # Run all tests
    test_research_chat()
    test_tutorial_chat()
    test_explanation_chat()
    test_error_handling()
    test_3step_processing()
    
    print("\n" + "=" * 60)
    print("🎉 All tests completed!")
    print("\nTo run the frontend:")
    print("cd frontend && streamlit run app.py")
    print("\nTo run the backend:")
    print("cd backend && python main.py")

if __name__ == "__main__":
    main() 