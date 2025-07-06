# 🤖 Robotics Chatbot

## 🎯 Chat Modes

The Robotics Chatbot has three chat modes:

### 🔬 Research Chat
**Purpose**: Academic research questions and paper analysis

### 📚 Tutorial/How-to Chat
**Purpose**: Generate code tutorials and how-to guides

### 💡 Explanation Chat
**Purpose**: Concept explanations with adjustable complexity

## 📋 Prerequisites
- Google API Key for Gemini

## 🚀 Quick Start

1. **Start the backend server**:
   ```bash
   python backend/main.py
   ```
   The API will be available at `http://localhost:8000`

2. **Start the Streamlit frontend** (in a new terminal):
   ```bash
   streamlit run frontend/app.py
   ```
   The web interface will open at `http://localhost:8501`

## 🔧 Configuration

### Environment Variables

- `GOOGLE_API_KEY`: Required for Gemini AI model

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
