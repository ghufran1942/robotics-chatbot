import os
import sys
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, UploadFile
from pydantic import BaseModel
import uvicorn

# Path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.loaders import RoboticsDocumentLoader
from backend.vectorstore import RoboticsVectorStore
from backend.summarizer import RoboticsSummarizer
from backend.pdf_uploader import PDFUploader
from backend.arxiv_search import ArxivSearcher
from backend.mcp_store import MCPStore
from backend.chat_modes import ResearchChatProcessor, TutorialChatProcessor, ExplanationChatProcessor
from config import COMMON_ROBOTICS_TOPICS, FAISS_INDEX_PATH

# Initialize FastAPI app
app = FastAPI(title="Robotics Chatbot API", version="1.0.0")

# Models for API requests/responses
class QuestionRequest(BaseModel):
    topic: str
    question: str

class TopicRequest(BaseModel):
    topic: str

class AnswerResponse(BaseModel):
    answer: str
    sources: List[Dict]
    num_sources: int
    topic: str

class TopicResponse(BaseModel):
    topic: str
    document_count: int
    status: str

# Global instances
document_loader = RoboticsDocumentLoader()
vector_store = RoboticsVectorStore()
summarizer = RoboticsSummarizer()
pdf_uploader = PDFUploader()
arxiv_searcher = ArxivSearcher()
mcp_store = MCPStore()

# Initialize chat mode processors
chat_processors = {
    "research": ResearchChatProcessor(summarizer.llm),
    "tutorial": TutorialChatProcessor(summarizer.llm),
    "explanation": ExplanationChatProcessor(summarizer.llm)
}

@app.on_event("startup")
async def startup_event():
    """Initialize the chatbot on startup."""
    print("🚀 Starting Robotics Chatbot...")
    print(f"Available topics: {COMMON_ROBOTICS_TOPICS}")

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Robotics Chatbot API", "version": "1.0.0"}

@app.get("/topics")
async def get_available_topics():
    """Get list of available topics."""
    existing_topics = vector_store.get_topics()
    return {
        "existing_topics": existing_topics,
        "suggested_topics": COMMON_ROBOTICS_TOPICS
    }

@app.post("/load_topic", response_model=TopicResponse)
async def load_topic(request: TopicRequest):
    """Load documents for a specific topic."""
    try:
        topic = request.topic.strip()
        
        # Check if topic already exists
        if vector_store.index_exists(topic):
            vector_store.load_index(topic)
            return TopicResponse(
                topic=topic,
                document_count=vector_store.get_document_count(),
                status="loaded_from_cache"
            )
        
        # Load documents from various sources
        print(f"Loading documents for topic: {topic}")
        documents = document_loader.load_all_sources(topic)
        
        if not documents:
            raise HTTPException(
                status_code=404, 
                detail=f"No documents found for topic: {topic}"
            )
        
        # Split documents into chunks
        split_docs = document_loader.split_documents(documents)
        
        # Add to vector store
        vector_store.clear()  # Clear any existing documents
        vector_store.add_documents(split_docs)
        
        # Save the index
        vector_store.save_index(topic)
        
        return TopicResponse(
            topic=topic,
            document_count=vector_store.get_document_count(),
            status="loaded_and_indexed"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    """Ask a question about a robotics topic."""
    try:
        topic = request.topic.strip()
        question = request.question.strip()
        
        # Validate the question
        if not summarizer.validate_question(question):
            raise HTTPException(
                status_code=400,
                detail="Question is not related to robotics or technical topics."
            )
        
        # Load topic if not already loaded
        if not vector_store.index_exists(topic):
            # Try to load the topic
            await load_topic(TopicRequest(topic=topic))
        else:
            vector_store.load_index(topic)
        
        # Search for relevant documents
        search_results = vector_store.search(question, k=5)
        
        if not search_results:
            raise HTTPException(
                status_code=404,
                detail=f"No relevant documents found for the question about {topic}"
            )
        
        # Generate answer
        answer_data = summarizer.generate_answer(question, search_results)
        
        return AnswerResponse(
            answer=answer_data["answer"],
            sources=answer_data["sources"],
            num_sources=answer_data["num_sources"],
            topic=topic
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process_question")
async def process_question_with_workflow(request: dict):
    """Process a question using the complete workflow: MCP → arXiv → LLM."""
    try:
        question = request.get("question", "").strip()
        explain_concept = request.get("explain_concept", True)
        include_examples = request.get("include_examples", True)
        include_code = request.get("include_code", True)
        
        if not question:
            raise HTTPException(
                status_code=400,
                detail="Question is required"
            )
        
        # Use the new workflow method
        result = summarizer.process_question_with_workflow(
            question, explain_concept, include_examples, include_code
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/refresh_topic")
async def refresh_topic_endpoint(request: dict):
    """Refresh a topic by re-fetching from its source."""
    try:
        topic = request.get("topic", "").strip()
        force_refresh = request.get("force_refresh", False)
        
        if not topic:
            raise HTTPException(
                status_code=400,
                detail="Topic is required"
            )
        
        # Use MCP store to refresh the topic
        refresh_result = mcp_store.refresh_topic(topic, force_refresh)
        
        return refresh_result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "robotics-chatbot"}

@app.get("/topic_freshness/{topic}")
async def get_topic_freshness(topic: str):
    """Get freshness information for a topic."""
    try:
        metadata = mcp_store.get_topic_metadata(topic)
        return metadata
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process_question_3step")
async def process_question_3step(request: dict):
    """Process a question using the 3-step loop: Rewrite → Enhance → Answer."""
    try:
        question = request.get("question", "").strip()
        context = request.get("context", "")
        
        if not question:
            raise HTTPException(
                status_code=400,
                detail="Question is required"
            )
        
        # Use the new 3-step processing method
        result = summarizer.process_question_3step(question, context)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/topic_summary/{topic}")
async def get_topic_summary(topic: str):
    """Get a summary of a specific topic."""
    try:
        # Load topic if exists
        if vector_store.index_exists(topic):
            vector_store.load_index(topic)
            
            # Get all documents for summary
            all_docs = []
            for i in range(vector_store.get_document_count()):
                if i < len(vector_store.documents):
                    all_docs.append(vector_store.documents[i])
            
            # Generate summary
            summary = summarizer.generate_topic_summary(topic, all_docs)
            
            return {
                "topic": topic,
                "summary": summary,
                "document_count": len(all_docs)
            }
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Topic '{topic}' not found. Please load it first using /load_topic"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/auto_generate_topics")
async def auto_generate_topics():
    """Auto-generate document collections for common robotics topics."""
    try:
        results = []
        
        for topic in COMMON_ROBOTICS_TOPICS:
            try:
                # Check if topic already exists
                if vector_store.index_exists(topic):
                    results.append({
                        "topic": topic,
                        "status": "already_exists",
                        "document_count": 0
                    })
                    continue
                
                # Load documents for the topic
                documents = document_loader.load_all_sources(topic)
                
                if documents:
                    # Split and add to vector store
                    split_docs = document_loader.split_documents(documents)
                    vector_store.clear()
                    vector_store.add_documents(split_docs)
                    vector_store.save_index(topic)
                    
                    results.append({
                        "topic": topic,
                        "status": "generated",
                        "document_count": len(split_docs)
                    })
                else:
                    results.append({
                        "topic": topic,
                        "status": "no_documents_found",
                        "document_count": 0
                    })
                    
            except Exception as e:
                results.append({
                    "topic": topic,
                    "status": "error",
                    "error": str(e),
                    "document_count": 0
                })
        
        return {
            "message": "Auto-generation completed",
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/topic/{topic}")
async def delete_topic(topic: str):
    """Delete a topic and its associated documents."""
    try:
        import shutil
        
        topic_dir = os.path.join(FAISS_INDEX_PATH, topic.replace(" ", "_").lower())
        
        if os.path.exists(topic_dir):
            shutil.rmtree(topic_dir)
            return {"message": f"Topic '{topic}' deleted successfully"}
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Topic '{topic}' not found"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# PDF Upload endpoints
@app.post("/upload_pdf")
async def upload_pdf(file: UploadFile):
    """Upload and process a PDF file."""
    try:
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are supported"
            )
        
        # Process the PDF
        result = pdf_uploader.process_pdf(file, file.filename)
        
        if result["success"]:
            # Add documents to vector store
            vector_store.add_documents(result["documents"])
            
            return {
                "message": f"PDF '{file.filename}' processed successfully",
                "filename": file.filename,
                "chunk_count": result["chunk_count"],
                "text_length": result["text_length"]
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to process PDF: {result['error']}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/uploaded_files")
async def get_uploaded_files():
    """Get list of uploaded PDF files."""
    try:
        files = pdf_uploader.get_uploaded_files()
        stats = pdf_uploader.get_upload_stats()
        
        return {
            "files": files,
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/uploaded_file/{filename}")
async def delete_uploaded_file(filename: str):
    """Delete an uploaded PDF file."""
    try:
        # Remove from vector store first
        removed_count = vector_store.remove_documents_by_source("uploaded_pdf")
        
        # Delete the file
        success = pdf_uploader.delete_uploaded_file(filename)
        
        if success:
            return {
                "message": f"File '{filename}' deleted successfully",
                "removed_documents": removed_count
            }
        else:
            raise HTTPException(
                status_code=404,
                detail=f"File '{filename}' not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ArXiv Search endpoints
@app.post("/search_arxiv")
async def search_arxiv(request: dict):
    """Search arXiv for papers related to a topic."""
    try:
        query = request.get("query", "").strip()
        max_results = request.get("max_results", 5)
        
        if not query:
            raise HTTPException(
                status_code=400,
                detail="Query is required"
            )
        
        if not arxiv_searcher.validate_query(query):
            raise HTTPException(
                status_code=400,
                detail="Invalid query"
            )
        
        # Search and process papers
        result = arxiv_searcher.search_and_process(query, max_results)
        
        if result["success"]:
            # Add documents to vector store
            vector_store.add_documents(result["documents"])
            
            return {
                "message": f"Found {result['paper_count']} papers for '{query}'",
                "papers": result["papers"],
                "paper_count": result["paper_count"],
                "document_count": result["document_count"],
                "query": query
            }
        else:
            raise HTTPException(
                status_code=404,
                detail=f"No papers found: {result['error']}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/arxiv_stats")
async def get_arxiv_stats():
    """Get statistics about arXiv papers in the vector store."""
    try:
        arxiv_docs = vector_store.get_documents_by_source("arxiv")
        source_stats = vector_store.get_source_stats()
        
        return {
            "arxiv_document_count": len(arxiv_docs),
            "source_stats": source_stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/arxiv_papers")
async def clear_arxiv_papers():
    """Remove all arXiv papers from the vector store."""
    try:
        removed_count = vector_store.remove_documents_by_source("arxiv")
        
        return {
            "message": f"Removed {removed_count} arXiv papers",
            "removed_count": removed_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# MCP (Memory Cache + Persistent Storage) endpoints
@app.get("/mcp/stats")
async def get_mcp_stats():
    """Get MCP cache statistics."""
    try:
        stats = mcp_store.get_cache_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/mcp/fetch_docs")
async def fetch_documentation(request: dict):
    """Fetch and cache documentation for a specific topic."""
    try:
        topic = request.get("topic", "").strip()
        source_url = request.get("source_url", "").strip()
        source_type = request.get("source_type", "web")
        
        if not topic or not source_url:
            raise HTTPException(
                status_code=400,
                detail="Both topic and source_url are required"
            )
        
        # Fetch and cache documentation
        documents = mcp_store.fetch_and_cache_docs(topic, source_url, source_type)
        
        return {
            "topic": topic,
            "source_url": source_url,
            "documents_fetched": len(documents),
            "status": "cached" if documents else "failed"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/mcp/cached_topics")
async def get_cached_topics():
    """Get list of cached topics in MCP."""
    try:
        cached_topics = []
        for cache_key, entry in mcp_store.metadata.items():
            if not mcp_store._is_expired(entry.get("timestamp", "")):
                cached_topics.append({
                    "topic": entry.get("topic", ""),
                    "source_url": entry.get("source_url", ""),
                    "source_type": entry.get("source_type", ""),
                    "timestamp": entry.get("timestamp", ""),
                    "document_count": entry.get("document_count", 0),
                    "cache_age": mcp_store._get_cache_age(entry.get("timestamp", ""))
                })
        
        return {
            "cached_topics": cached_topics,
            "total_cached": len(cached_topics)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/mcp/clear_expired")
async def clear_expired_mcp_cache():
    """Clear expired cache entries from MCP."""
    try:
        cleared_count = mcp_store.clear_expired_cache()
        return {
            "message": f"Cleared {cleared_count} expired cache entries",
            "remaining_entries": len(mcp_store.metadata)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/mcp/clear_all")
async def clear_all_mcp_cache():
    """Clear all MCP cache entries."""
    try:
        cleared_count = mcp_store.clear_all_cache()
        return {
            "message": f"Cleared {cleared_count} cache entries",
            "remaining_entries": 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Chat Mode endpoints
@app.post("/chat/research")
async def research_chat(request: dict):
    """Research Chat mode - process research questions with paper analysis."""
    try:
        question = request.get("question", "").strip()
        uploaded_papers = request.get("uploaded_papers", [])
        
        if not question:
            raise HTTPException(
                status_code=400,
                detail="Question is required"
            )
        
        result = chat_processors["research"].process_research_question(question, uploaded_papers)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/tutorial")
async def tutorial_chat(request: dict):
    """Tutorial/How-to Chat mode - generate tutorials with library documentation."""
    try:
        request_text = request.get("request", "").strip()
        library_name = request.get("library_name", "").strip()
        doc_url = request.get("doc_url", "").strip()
        output_mode = request.get("output_mode", "Code")
        
        if not request_text or not library_name:
            raise HTTPException(
                status_code=400,
                detail="Request and library_name are required"
            )
        
        result = chat_processors["tutorial"].process_tutorial_request(
            request_text, library_name, doc_url, output_mode
        )
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/explanation")
async def explanation_chat(request: dict):
    """Explanation Chat mode - explain concepts with complexity levels."""
    try:
        request_text = request.get("request", "").strip()
        complexity_level = request.get("complexity_level", "Intermediate")
        output_mode = request.get("output_mode", "Example")
        
        if not request_text:
            raise HTTPException(
                status_code=400,
                detail="Request is required"
            )
        
        result = chat_processors["explanation"].process_explanation_request(
            request_text, complexity_level, output_mode
        )
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 