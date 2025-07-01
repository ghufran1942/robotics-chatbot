# 🤖 Robotics Chatbot

An intelligent, interactive chatbot designed to help learners understand robotics concepts through AI-powered document retrieval and summarization.

## 🚀 Features

- **Natural Language Questions**: Ask questions about robotics concepts in plain English
- **Multi-Source Document Retrieval**: Automatically fetches relevant documents from:
  - arXiv papers
  - ROS documentation
  - Robotics Stack Exchange
  - General web sources
- **AI-Powered Summarization**: Uses Google Gemini to generate comprehensive, structured answers
- **Vector Search**: FAISS-based semantic search for relevant document retrieval
- **Modern Web Interface**: Beautiful Streamlit frontend with real-time chat
- **Topic Management**: Load, save, and manage different robotics topics
- **Source Grounding**: All answers are grounded in retrieved documents with citations

## 📋 Prerequisites

- Python 3.8+
- Google API Key for Gemini
- Internet connection for document retrieval

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd robotics-chatbot
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   Create a `.env` file in the root directory:
   ```env
   GOOGLE_API_KEY=your_google_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here
   ```

4. **Get API Keys**:
   - **Google Gemini**: Visit [Google AI Studio](https://makersuite.google.com/app/apikey) to get your API key
   - **OpenAI** (optional): Visit [OpenAI Platform](https://platform.openai.com/api-keys) if you want to use OpenAI models

## 🚀 Quick Start

### Option 1: Run Both Backend and Frontend

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

### Option 2: Run Frontend Only (if backend is already running)

```bash
streamlit run frontend/app.py
```

## 📖 Usage Guide

### 1. Getting Started

1. Open the web interface in your browser
2. Select a topic from the sidebar (e.g., "PID controller")
3. Ask questions about the topic in natural language

### 2. Available Topics

The system comes with pre-configured common robotics topics:
- PID controller
- SLAM (Simultaneous Localization and Mapping)
- Robotic grippers
- Localization
- Path planning
- Computer vision
- Sensor fusion
- Kinematics
- Dynamics
- Control systems
- Machine learning in robotics
- Autonomous navigation
- Manipulation
- Human-robot interaction

### 3. Asking Questions

Examples of questions you can ask:
- "Explain how PID controllers work in robotics"
- "What are the applications of SLAM in autonomous vehicles?"
- "How do robotic grippers handle different objects?"
- "What are the mathematical foundations of path planning?"
- "Explain sensor fusion techniques for robot localization"

### 4. Understanding Answers

Each answer is structured with:
- **Introduction**: Clear explanation of the concept
- **Applications in Robotics**: Real-world use cases
- **Mathematical Explanation**: Formulas and theoretical foundations
- **Tuning Methods**: Practical implementation considerations
- **Sources**: References to the documents used

## 🏗️ Architecture

```
robotics_chatbot/
├── backend/
│   ├── main.py              # FastAPI backend server
│   ├── loaders.py           # Document loading from various sources
│   ├── vectorstore.py       # FAISS vector store management
│   └── summarizer.py        # LangChain + Gemini summarization
├── frontend/
│   └── app.py              # Streamlit web interface
├── config.py               # Configuration and constants
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

### Core Components

1. **Document Loaders** (`backend/loaders.py`):
   - arXiv paper retrieval
   - ROS documentation scraping
   - Stack Exchange Q&A extraction
   - Web search integration

2. **Vector Store** (`backend/vectorstore.py`):
   - FAISS index management
   - Document embedding and storage
   - Semantic search functionality

3. **Summarizer** (`backend/summarizer.py`):
   - Google Gemini integration
   - Structured answer generation
   - Source citation and grounding

4. **Web Interface** (`frontend/app.py`):
   - Modern Streamlit UI
   - Real-time chat interface
   - Topic management
   - Source visualization

## 🔧 Configuration

### Environment Variables

- `GOOGLE_API_KEY`: Required for Gemini AI model
- `OPENAI_API_KEY`: Optional, for alternative models
- `FAISS_INDEX_PATH`: Path for storing vector indices (default: `./vectorstore`)
- `MAX_DOCUMENTS_PER_TOPIC`: Maximum documents per topic (default: 50)
- `CHUNK_SIZE`: Document chunk size for processing (default: 1000)
- `CHUNK_OVERLAP`: Overlap between chunks (default: 200)

### API Endpoints

- `GET /`: API status
- `GET /topics`: List available topics
- `POST /load_topic`: Load documents for a topic
- `POST /ask`: Ask a question about a topic
- `GET /topic_summary/{topic}`: Get topic summary
- `POST /auto_generate_topics`: Auto-generate common topics
- `DELETE /topic/{topic}`: Delete a topic

## 🎯 Example Use Cases

### Educational Use
- **Students**: Learn robotics concepts through interactive Q&A
- **Researchers**: Quick access to relevant papers and documentation
- **Engineers**: Reference implementation details and best practices

### Research Use
- **Literature Review**: Automated paper discovery and summarization
- **Technical Documentation**: Quick access to ROS and robotics documentation
- **Problem Solving**: Get answers to specific technical questions

## 🔍 Advanced Features

### Custom Topics
You can add custom topics by:
1. Using the web interface to load a new topic
2. The system will automatically fetch relevant documents
3. Create a persistent vector index for future use

### Source Management
- All answers include source citations
- View relevance scores for each source
- Access original URLs and metadata

### Topic Summaries
- Generate comprehensive topic overviews
- Understand key concepts and applications
- Get mathematical foundations and practical considerations

## 🐛 Troubleshooting

### Common Issues

1. **API Key Errors**:
   - Ensure your Google API key is correctly set in the `.env` file
   - Verify the API key has access to Gemini models

2. **Document Loading Issues**:
   - Check internet connection
   - Some sources may have rate limits
   - Try different topics if one fails

3. **Memory Issues**:
   - Reduce `MAX_DOCUMENTS_PER_TOPIC` in config
   - Clear old topic indices if needed

4. **Performance Issues**:
   - Use smaller chunk sizes for faster processing
   - Consider using GPU-accelerated FAISS for large datasets

### Debug Mode

To enable debug logging, set the environment variable:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python -u backend/main.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **LangChain**: For the document processing and LLM integration framework
- **FAISS**: For efficient vector similarity search
- **Google Gemini**: For the AI language model
- **Streamlit**: For the beautiful web interface
- **ROS Community**: For the robotics documentation and resources