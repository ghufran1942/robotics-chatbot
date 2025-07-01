#!/usr/bin/env python3
"""
Setup script for Robotics Chatbot
Helps users install dependencies and configure the environment.
"""

import os
import sys
import subprocess
import shutil

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version}")
    return True

def install_dependencies():
    """Install required dependencies."""
    print("📦 Installing dependencies...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_environment():
    """Set up environment file."""
    print("🔧 Setting up environment...")
    
    if os.path.exists(".env"):
        print("⚠️  .env file already exists")
        response = input("Do you want to overwrite it? (y/N): ")
        if response.lower() != 'y':
            print("Skipping environment setup")
            return True
    
    # Copy template to .env
    if os.path.exists("env_template.txt"):
        shutil.copy("env_template.txt", ".env")
        print("✅ Created .env file from template")
        print("📝 Please edit .env file and add your API keys")
        return True
    else:
        print("❌ env_template.txt not found")
        return False

def get_api_key():
    """Get API key from user."""
    print("\n🔑 Google API Key Setup")
    print("You need a Google API key to use Gemini AI")
    print("Get your key from: https://makersuite.google.com/app/apikey")
    
    api_key = input("Enter your Google API key (or press Enter to skip): ").strip()
    
    if api_key:
        # Update .env file
        if os.path.exists(".env"):
            with open(".env", "r") as f:
                content = f.read()
            
            content = content.replace("your_google_api_key_here", api_key)
            
            with open(".env", "w") as f:
                f.write(content)
            
            print("✅ API key saved to .env file")
            return True
        else:
            print("❌ .env file not found")
            return False
    else:
        print("⚠️  Skipping API key setup")
        return True

def run_tests():
    """Run installation tests."""
    print("\n🧪 Running installation tests...")
    
    try:
        result = subprocess.run([sys.executable, "test_installation.py"], 
                              capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Failed to run tests: {e}")
        return False

def main():
    """Main setup function."""
    print("🤖 Robotics Chatbot Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Setup failed at dependency installation")
        sys.exit(1)
    
    # Setup environment
    if not setup_environment():
        print("❌ Setup failed at environment setup")
        sys.exit(1)
    
    # Get API key
    get_api_key()
    
    # Run tests
    if run_tests():
        print("\n✅ Setup completed successfully!")
        print("\n🚀 You can now run the chatbot:")
        print("   python run.py")
        print("   or")
        print("   python backend/main.py  # Backend only")
        print("   streamlit run frontend/app.py  # Frontend only")
    else:
        print("\n⚠️  Setup completed with warnings")
        print("Please check the test output above and fix any issues")
    
    print("\n📖 For more information, see README.md")

if __name__ == "__main__":
    main() 