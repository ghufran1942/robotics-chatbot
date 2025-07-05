# 🤖 Robotics Chatbot

An intelligent, interactive chatbot designed to help learners understand robotics concepts through AI-powered document retrieval and summarization.

## 🚀 Features

- **Three Distinct Chat Modes**: Research Chat, Tutorial/How-to Chat, and Explanation Chat
- **Smart 3-Step Processing**: Gemini-powered question rewriting and enhanced answer generation
- **Smart Prompt Options**: Customize answers with explanation level, examples, and code snippets
- **MCP (Memory Cache + Persistent Storage)**: Intelligent caching with freshness tracking and automatic refresh
- **Freshness Tracking**: Timestamp metadata ensures up-to-date information from all sources
- **Automatic Source Refresh**: Stale data (older than 15 days) is automatically refreshed from original sources
- **Natural Language Questions**: Ask questions about robotics concepts in plain English
- **Multi-Source Document Retrieval**: Automatically fetches relevant documents from:
  - **ArXiv Papers**: Dynamic search for recent research papers with publication dates
  - **User-Uploaded PDFs**: Upload textbooks, research papers, or notes
  - **Robotics Stack Exchange**: Community Q&A and discussions
  - **General web sources**: Educational content and tutorials
- **AI-Powered Summarization**: Uses Google Gemini to generate comprehensive, structured answers
- **Vector Search**: FAISS-based semantic search for relevant document retrieval
- **Modern Web Interface**: Beautiful Streamlit frontend with real-time chat, freshness indicators, and processing modes
- **Topic Management**: Load, save, and manage different robotics topics with refresh controls
- **Source Grounding**: All answers are grounded in retrieved documents with citations and freshness info
- **PDF Processing**: Support for multiple PDF libraries (PyPDF2, pdfplumber, LangChain)
- **Dynamic ArXiv Integration**: Real-time paper search and processing with automatic updates

## 🎯 Chat Modes

The Robotics Chatbot now features three distinct chat modes, each designed for specific use cases:

### 🔬 Research Chat
**Purpose**: Academic research questions and paper analysis
**Features**:
- Accepts research questions about robotics topics
- Upload research papers (PDF) for analysis
- Auto-fetches relevant papers from ArXiv if none uploaded
- Generates comprehensive research synthesis
- Combines user question, paper summaries, and external context
- Returns structured research answers with source citations

**Example Use Cases**:
- "What are the latest developments in PID control for autonomous vehicles?"
- "How do neural networks improve robot navigation?"
- "What are the applications of reinforcement learning in robotics?"

### 📚 Tutorial/How-to Chat
**Purpose**: Generate code tutorials and how-to guides
**Features**:
- Library/framework name input (e.g., ROS, PyTorch, TensorFlow)
- Documentation URL linking
- Code vs Example output modes
- Stores documentation in MCP cache
- Extracts context using Model Context Protocol
- Generates step-by-step tutorials with code examples

**Example Use Cases**:
- "How to implement a basic PID controller in ROS?"
- "How to train a neural network for image classification?"
- "How to create a simple robot simulation in Gazebo?"

### 💡 Explanation Chat
**Purpose**: Concept explanations with adjustable complexity
**Features**:
- Three complexity levels: Beginner, Intermediate, Expert
- Code vs Example output modes
- Level-specific explanation templates
- Tailored explanations for different expertise levels
- Practical applications and real-world examples

**Example Use Cases**:
- "What is SLAM and how does it work?" (Beginner)
- "How do PID controllers work in robotics?" (Intermediate)
- "Explain the mathematical foundations of computer vision algorithms" (Expert)

### 🔄 3-Step Processing Pipeline
All chat modes use a shared 3-step Gemini refinement pipeline:
1. **Raw User Input**: Original question or request
2. **Gemini-Enhanced Prompt**: AI rewrites for clarity, context, and specificity
3. **Final Response**: Enhanced answer generated from improved prompt

Each mode has dedicated prompt templates for step 2, ensuring optimal results for the specific use case.

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

### 4. Smart 3-Step Processing

**🚀 Enhanced Question Processing:**
The system offers two processing modes for optimal results:

**Smart 3-Step Processing (Recommended):**
1. **Step 1**: Gemini rewrites your question into a more specific technical prompt
2. **Step 2**: The refined prompt is used to generate a comprehensive answer
3. **Step 3**: Final enhanced answer is delivered with processing details

**Direct Processing:**
- Traditional workflow with customizable prompt options
- Faster processing for simple questions
- Manual control over answer customization

**Example 3-Step Workflow:**
```
Original Question: "What is the use of PID controllers in robotics?"

Step 1 - Refined Prompt: "Explain the role, tuning methods, and practical applications 
of PID controllers in robotic systems, especially for motion and position control."

Step 2 - Final Answer: Comprehensive explanation with theory, applications, 
tuning methods, and real-world examples
```

**UI Features:**
- Processing mode selection (Smart 3-Step vs Direct)
- Step-by-step progress indicators
- Expandable sections showing original question and refined prompt
- Enhanced answer quality through intelligent prompt rewriting

### 5. Smart Prompt Options (Direct Processing)

**🎯 Customize Your Answers:**
- **Explanation Level**: Choose beginner, intermediate, or advanced explanations
- **Real-world Examples**: Include practical applications and use cases
- **Code Snippets**: Get runnable Python code demonstrations
- **Dynamic Prompt Building**: The system automatically constructs optimal prompts based on your preferences

**Example Use Case:**
```
Question: "How do I create a matrix with NumPy?"
Options: 
- Explain for intermediate level ✓
- Include real-world examples ✓  
- Include code snippets ✓

Result: Comprehensive answer with NumPy matrix creation, 
robotics transformation matrix example, and Python code
```

### 5. MCP (Memory Cache + Persistent Storage) with Priority Workflow

**💾 Intelligent Caching with Priority Logic:**
- **MCP First**: System always checks MCP before calling Gemini or fetching from other sources
- **Freshness Tracking**: Tracks timestamp metadata for all cached content
- **15-day Freshness Threshold**: Automatically refreshes stale data from original sources
- **Source Priority**: MCP → ArXiv → Gemini (in order of preference)
- **Reduces API Calls**: Prioritizes cached content while ensuring up-to-date information

**🔄 Priority Workflow:**
1. **Check MCP First**: `mcp_store.query_mcp(query)` for relevant content
2. **If MCP has fresh content**: Use cached documents to generate answer
3. **If MCP is stale**: Automatically refresh from original source (ArXiv/docs)
4. **If MCP is empty**: Search ArXiv, save results to MCP for future use
5. **Fallback to Gemini**: Only if no relevant documents found anywhere

**📊 Cache Management:**
- View cache statistics in the sidebar
- Clear expired entries automatically
- Monitor cached documentation sources with age information
- Track cache age and document counts
- Manual refresh controls for specific topics

**🎯 Source Indicators:**
- **MCP Cache**: `🧠 Source: MCP Cache [from NUMPY] (updated: July 1, 2025)`
- **MCP Refreshed**: `🔄 Source: MCP (Freshly Updated) [from ARXIV] (updated: July 2, 2025)`
- **ArXiv Papers**: `📚 Source: ArXiv Papers [from ARXIV] (updated: July 2, 2025)`
- **Gemini Fallback**: `🤖 Source: Gemini AI [from GEMINI]`

**Example Priority Workflow:**
1. Ask: "What is SLAM in robotics?"
2. **Step 1**: System checks MCP for SLAM documentation
3. **Step 2**: If found and fresh: Uses MCP content, shows `🧠 Source: MCP Cache`
4. **Step 3**: If found but stale: Refreshes from ArXiv, shows `🔄 Source: MCP (Freshly Updated)`
5. **Step 4**: If not found: Searches ArXiv, saves to MCP, shows `📚 Source: ArXiv Papers`
6. **Step 5**: If no ArXiv: Uses Gemini, shows `🤖 Source: Gemini AI`

### 6. Using Document Features

**📄 PDF Upload:**
- Upload your own PDF documents (textbooks, papers, notes)
- Documents are automatically processed and indexed
- Content is included in future question answers
- View and manage uploaded files in the sidebar

**🔬 ArXiv Integration:**
- Toggle "Use ArXiv Papers" to include recent research
- Search for specific topics: "PID control robotics"
- Papers are automatically processed and added to the knowledge base
- Citations are included in answers

### 5. Understanding Answers

Each answer is structured with:
- **Introduction**: Clear explanation of the concept
- **Applications in Robotics**: Real-world use cases
- **Mathematical Explanation**: Formulas and theoretical foundations
- **Tuning Methods**: Practical implementation considerations
- **Sources**: References to the documents used (including uploaded PDFs and ArXiv papers)

## 🏗️ Architecture

```
robotics_chatbot/
├── backend/
│   ├── main.py              # FastAPI backend server with 3-step processing endpoints
│   ├── loaders.py           # Document loading from various sources
│   ├── vectorstore.py       # FAISS vector store management
│   ├── summarizer.py        # LangChain + Gemini summarization with 3-step processing
│   ├── pdf_uploader.py      # PDF processing and upload management
│   ├── arxiv_search.py      # ArXiv paper search and processing
│   └── mcp_store.py         # Memory Cache + Persistent Storage with timestamp metadata
├── frontend/
│   └── app.py              # Streamlit web interface with processing modes
├── config.py               # Configuration and constants
├── requirements.txt        # Python dependencies
├── test_freshness.py       # Test suite for freshness features
├── test_3step_processing.py # Test suite for 3-step processing
└── README.md              # This file
```

### New API Endpoints

**🔄 Refresh Management:**
- `POST /refresh_topic` - Force refresh a specific topic
- `GET /topic_freshness/{topic}` - Get freshness metadata for a topic
- `GET /mcp/stats` - Enhanced cache statistics with age information

**🧠 3-Step Processing:**
- `POST /process_question_3step` - Process question using Gemini rewrite loop
- `POST /process_question` - Traditional processing with customizable options

**📊 Freshness Features:**
- Automatic detection of stale data (> 15 days old)
- Timestamp metadata for all cached content
- Source type tracking (arxiv, web, pdf, manual)
- Manual refresh controls in the UI

**🎯 Processing Features:**
- Question rewriting with Gemini for enhanced specificity
- Step-by-step processing with progress indicators
- Original question and refined prompt display
- Enhanced answer quality through intelligent prompt engineering

### Key Components

**Smart Prompt System:**
- Dynamic prompt construction based on user preferences
- Explanation level selection (beginner/intermediate/advanced)
- Optional real-world examples and code snippets
- Enhanced question processing for better AI responses

**MCP (Memory Cache + Persistent Storage):**
- Intelligent caching of documentation from multiple sources
- Automatic expiry and cleanup (30-day default)
- Metadata tracking for cache management
- Integration with vector store for seamless document retrieval

## 🔧 Configuration

### Environment Variables

- `GOOGLE_API_KEY`: Required for Gemini AI model
- `OPENAI_API_KEY`: Optional, for alternative models
- `FAISS_INDEX_PATH`: Path for storing vector indices (default: `./vectorstore`)
- `MAX_DOCUMENTS_PER_TOPIC`: Maximum documents per topic (default: 50)
- `CHUNK_SIZE`: Document chunk size for processing (default: 1000)
- `CHUNK_OVERLAP`: Overlap between chunks (default: 200)

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

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
