#!/usr/bin/env python3
"""
Robotics Chatbot Startup Script
Runs both the backend API server and the Streamlit frontend.
"""

import subprocess
import sys
import time
import os
import signal
from threading import Thread

def run_backend():
    """Run the backend FastAPI server."""
    print("🚀 Starting backend server...")
    try:
        subprocess.run([sys.executable, "backend/main.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Backend server stopped.")
    except Exception as e:
        print(f"❌ Error starting backend: {e}")

def run_frontend():
    """Run the Streamlit frontend."""
    print("🌐 Starting Streamlit frontend...")
    try:
        # Wait a bit for backend to start
        time.sleep(3)
        subprocess.run([sys.executable, "-m", "streamlit", "run", "frontend/app.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Frontend stopped.")
    except Exception as e:
        print(f"❌ Error starting frontend: {e}")

def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = [
        "streamlit", "fastapi", "uvicorn", "langchain", 
        "faiss-cpu", "sentence-transformers", "requests"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n📦 Install them with: pip install -r requirements.txt")
        return False
    
    return True

def check_api_key():
    """Check if Google API key is set."""
    from config import GOOGLE_API_KEY
    
    if not GOOGLE_API_KEY or GOOGLE_API_KEY == "your_google_api_key_here":
        print("❌ Google API key not set!")
        print("📝 Please set your GOOGLE_API_KEY in the .env file")
        print("🔑 Get your API key from: https://makersuite.google.com/app/apikey")
        return False
    
    return True

def main():
    """Main startup function."""
    print("🤖 Robotics Chatbot Startup")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check API key
    if not check_api_key():
        sys.exit(1)
    
    print("✅ All checks passed!")
    print("\n🚀 Starting Robotics Chatbot...")
    print("📖 Backend API: http://localhost:8000")
    print("🌐 Frontend UI: http://localhost:8501")
    print("⏹️  Press Ctrl+C to stop both servers")
    print("-" * 40)
    
    # Start backend in a separate thread
    backend_thread = Thread(target=run_backend, daemon=True)
    backend_thread.start()
    
    # Start frontend in main thread
    try:
        run_frontend()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Robotics Chatbot...")
    finally:
        print("👋 Goodbye!")

if __name__ == "__main__":
    main() 