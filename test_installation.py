#!/usr/bin/env python3
"""
Test script to verify Robotics Chatbot installation
Checks dependencies, imports, and basic functionality.
"""

import sys
import os

def test_imports():
    """Test if all required packages can be imported."""
    print("🔍 Testing package imports...")
    
    packages = [
        ("streamlit", "Streamlit"),
        ("requests", "Requests"),
        ("numpy", "NumPy"),
        ("pandas", "Pandas"),
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("pydantic", "Pydantic"),
        ("beautifulsoup4", "BeautifulSoup4"),
        ("python-dotenv", "Python-dotenv"),
        ("arxiv", "ArXiv"),
        ("pypdf", "PyPDF"),
        ("sentence-transformers", "Sentence Transformers"),
    ]
    
    failed_imports = []
    
    for package, name in packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"  ✅ {name}")
        except ImportError:
            print(f"  ❌ {name}")
            failed_imports.append(package)
    
    # Test LangChain packages
    langchain_packages = [
        ("langchain", "LangChain"),
        ("langchain_google_genai", "LangChain Google GenAI"),
        ("langchain_community", "LangChain Community"),
    ]
    
    for package, name in langchain_packages:
        try:
            __import__(package)
            print(f"  ✅ {name}")
        except ImportError:
            print(f"  ❌ {name}")
            failed_imports.append(package)
    
    # Test FAISS
    try:
        import faiss
        print(f"  ✅ FAISS (CPU)")
    except ImportError:
        print(f"  ❌ FAISS")
        failed_imports.append("faiss-cpu")
    
    return failed_imports

def test_config():
    """Test configuration loading."""
    print("\n🔧 Testing configuration...")
    
    try:
        from config import GOOGLE_API_KEY, COMMON_ROBOTICS_TOPICS
        print(f"  ✅ Configuration loaded")
        print(f"  📝 Google API Key: {'Set' if GOOGLE_API_KEY and GOOGLE_API_KEY != 'your_google_api_key_here' else 'Not set'}")
        print(f"  📚 Available topics: {len(COMMON_ROBOTICS_TOPICS)}")
        return True
    except Exception as e:
        print(f"  ❌ Configuration error: {e}")
        return False

def test_backend_modules():
    """Test backend module imports."""
    print("\n🔧 Testing backend modules...")
    
    modules = [
        ("backend.loaders", "Document Loaders"),
        ("backend.vectorstore", "Vector Store"),
        ("backend.summarizer", "Summarizer"),
        ("backend.main", "Main Backend"),
    ]
    
    failed_modules = []
    
    for module, name in modules:
        try:
            __import__(module)
            print(f"  ✅ {name}")
        except Exception as e:
            print(f"  ❌ {name}: {e}")
            failed_modules.append(module)
    
    return failed_modules

def test_frontend_modules():
    """Test frontend module imports."""
    print("\n🌐 Testing frontend modules...")
    
    try:
        import frontend.app
        print(f"  ✅ Streamlit Frontend")
        return True
    except Exception as e:
        print(f"  ❌ Frontend error: {e}")
        return False

def test_api_key():
    """Test if API key is properly configured."""
    print("\n🔑 Testing API key configuration...")
    
    try:
        from config import GOOGLE_API_KEY
        
        if not GOOGLE_API_KEY or GOOGLE_API_KEY == "your_google_api_key_here":
            print("  ⚠️  Google API key not set")
            print("  📝 Please set GOOGLE_API_KEY in your environment or .env file")
            print("  🔗 Get your key from: https://makersuite.google.com/app/apikey")
            return False
        else:
            print("  ✅ Google API key is set")
            return True
    except Exception as e:
        print(f"  ❌ API key error: {e}")
        return False

def test_directory_structure():
    """Test if all required files and directories exist."""
    print("\n📁 Testing directory structure...")
    
    required_files = [
        "requirements.txt",
        "config.py",
        "README.md",
        "backend/__init__.py",
        "backend/loaders.py",
        "backend/vectorstore.py",
        "backend/summarizer.py",
        "backend/main.py",
        "frontend/__init__.py",
        "frontend/app.py",
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path}")
            missing_files.append(file_path)
    
    return missing_files

def main():
    """Main test function."""
    print("🤖 Robotics Chatbot - Installation Test")
    print("=" * 50)
    
    all_passed = True
    
    # Test directory structure
    missing_files = test_directory_structure()
    if missing_files:
        print(f"\n❌ Missing files: {missing_files}")
        all_passed = False
    
    # Test imports
    failed_imports = test_imports()
    if failed_imports:
        print(f"\n❌ Failed imports: {failed_imports}")
        print("📦 Install missing packages with: pip install -r requirements.txt")
        all_passed = False
    
    # Test configuration
    if not test_config():
        all_passed = False
    
    # Test backend modules
    failed_backend = test_backend_modules()
    if failed_backend:
        print(f"\n❌ Failed backend modules: {failed_backend}")
        all_passed = False
    
    # Test frontend modules
    if not test_frontend_modules():
        all_passed = False
    
    # Test API key
    api_key_ok = test_api_key()
    if not api_key_ok:
        all_passed = False
    
    # Summary
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ All tests passed! Installation is complete.")
        print("\n🚀 You can now run the chatbot:")
        print("   python run.py")
        print("   or")
        print("   python backend/main.py  # Backend only")
        print("   streamlit run frontend/app.py  # Frontend only")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        print("\n📋 Common solutions:")
        print("   1. Install missing packages: pip install -r requirements.txt")
        print("   2. Set your Google API key in .env file")
        print("   3. Check that all files are present")
    
    print("\n📖 For more information, see README.md")

if __name__ == "__main__":
    main() 