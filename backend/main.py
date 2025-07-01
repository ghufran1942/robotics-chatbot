import os
import sys
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# Add the parent directory to the path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.loaders import RoboticsDocumentLoader
from backend.vectorstore import RoboticsVectorStore
from backend.summarizer import RoboticsSummarizer
from config import COMMON_ROBOTICS_TOPICS

# Initialize FastAPI app
app = FastAPI(title="Robotics Chatbot API", version="1.0.0")

# Pydantic models for API requests/responses
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
        
        topic_dir = os.path.join(vector_store.FAISS_INDEX_PATH, topic.replace(" ", "_").lower())
        
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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 