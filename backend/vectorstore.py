import os
import pickle
import numpy as np
from typing import List, Dict, Optional
import faiss
from sentence_transformers import SentenceTransformer
from config import FAISS_INDEX_PATH

class RoboticsVectorStore:
    """FAISS-based vector store for robotics documents."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize the vector store with a sentence transformer model."""
        self.model_name = model_name
        self.encoder = SentenceTransformer(model_name)
        self.index = None
        self.documents = []
        self.metadata = []
        
        # Create vectorstore directory if it doesn't exist
        os.makedirs(FAISS_INDEX_PATH, exist_ok=True)
    
    def add_documents(self, documents: List[Dict]) -> None:
        """Add documents to the vector store."""
        if not documents:
            return
        
        # Extract text content for embedding
        texts = []
        valid_docs = []
        
        for doc in documents:
            if "content" in doc:
                texts.append(doc["content"])
                valid_docs.append(doc)
            elif "summary" in doc:
                texts.append(doc["summary"])
                valid_docs.append(doc)
            else:
                # Skip documents without content
                continue
        
        if not texts:
            return
        
        # Generate embeddings
        embeddings = self.encoder.encode(texts, show_progress_bar=True)
        
        # Initialize or update FAISS index
        if self.index is None:
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
        
        # Add embeddings to index
        self.index.add(embeddings.astype('float32'))
        
        # Store documents and metadata
        for doc in valid_docs:
            self.documents.append(doc)
            self.metadata.append({
                "title": doc.get("title", "Unknown"),
                "source": doc.get("source", "unknown"),
                "url": doc.get("url", ""),
                "authors": doc.get("authors", []),
                "published": doc.get("published", ""),
                "arxiv_id": doc.get("arxiv_id", ""),
                "categories": doc.get("categories", []),
                "doi": doc.get("doi", ""),
                "file_path": doc.get("file_path", ""),
                "chunk_id": doc.get("chunk_id", 0),
                "total_chunks": doc.get("total_chunks", 1)
            })
        
        print(f"Added {len(texts)} documents to vector store. Total documents: {len(self.documents)}")
    
    def get_documents_by_source(self, source: str) -> List[Dict]:
        """Get documents filtered by source."""
        filtered_docs = []
        for i, metadata in enumerate(self.metadata):
            if metadata.get("source") == source:
                if i < len(self.documents):
                    filtered_docs.append(self.documents[i])
        return filtered_docs
    
    def get_source_stats(self) -> Dict:
        """Get statistics about documents by source."""
        source_counts = {}
        for metadata in self.metadata:
            source = metadata.get("source", "unknown")
            source_counts[source] = source_counts.get(source, 0) + 1
        
        return source_counts
    
    def remove_documents_by_source(self, source: str) -> int:
        """Remove all documents from a specific source."""
        if self.index is None:
            return 0
        
        # Find indices to remove
        indices_to_remove = []
        for i, metadata in enumerate(self.metadata):
            if metadata.get("source") == source:
                indices_to_remove.append(i)
        
        if not indices_to_remove:
            return 0
        
        # Create new index without removed documents
        remaining_texts = []
        remaining_docs = []
        remaining_metadata = []
        
        for i in range(len(self.documents)):
            if i not in indices_to_remove:
                doc = self.documents[i]
                if "content" in doc:
                    remaining_texts.append(doc["content"])
                elif "summary" in doc:
                    remaining_texts.append(doc["summary"])
                else:
                    continue
                
                remaining_docs.append(doc)
                remaining_metadata.append(self.metadata[i])
        
        # Rebuild index
        if remaining_texts:
            embeddings = self.encoder.encode(remaining_texts, show_progress_bar=True)
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatIP(dimension)
            self.index.add(embeddings.astype('float32'))
        else:
            self.index = None
        
        # Update document lists
        self.documents = remaining_docs
        self.metadata = remaining_metadata
        
        removed_count = len(indices_to_remove)
        print(f"Removed {removed_count} documents from source '{source}'")
        return removed_count
    
    def search(self, query: str, k: int = 5) -> List[Dict]:
        """Search for similar documents using the query."""
        if self.index is None or len(self.documents) == 0:
            return []
        
        # Encode the query
        query_embedding = self.encoder.encode([query])
        
        # Search the index
        scores, indices = self.index.search(query_embedding.astype('float32'), k)
        
        # Return results with metadata
        results = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx < len(self.documents):
                result = {
                    "document": self.documents[idx],
                    "metadata": self.metadata[idx],
                    "score": float(score),
                    "rank": i + 1
                }
                results.append(result)
        
        return results
    
    def save_index(self, topic: str) -> None:
        """Save the FAISS index and metadata for a specific topic."""
        if self.index is None:
            return
        
        # Create topic-specific directory
        topic_dir = os.path.join(FAISS_INDEX_PATH, topic.replace(" ", "_").lower())
        os.makedirs(topic_dir, exist_ok=True)
        
        # Save FAISS index
        index_path = os.path.join(topic_dir, "index.faiss")
        faiss.write_index(self.index, index_path)
        
        # Save documents and metadata
        data_path = os.path.join(topic_dir, "data.pkl")
        with open(data_path, 'wb') as f:
            pickle.dump({
                "documents": self.documents,
                "metadata": self.metadata,
                "model_name": self.model_name
            }, f)
        
        print(f"Saved vector store for topic '{topic}' to {topic_dir}")
    
    def load_index(self, topic: str) -> bool:
        """Load the FAISS index and metadata for a specific topic."""
        topic_dir = os.path.join(FAISS_INDEX_PATH, topic.replace(" ", "_").lower())
        index_path = os.path.join(topic_dir, "index.faiss")
        data_path = os.path.join(topic_dir, "data.pkl")
        
        if not os.path.exists(index_path) or not os.path.exists(data_path):
            return False
        
        try:
            # Load FAISS index
            self.index = faiss.read_index(index_path)
            
            # Load documents and metadata
            with open(data_path, 'rb') as f:
                data = pickle.load(f)
                self.documents = data["documents"]
                self.metadata = data["metadata"]
                self.model_name = data["model_name"]
            
            # Reinitialize encoder if needed
            if self.encoder is None:
                self.encoder = SentenceTransformer(self.model_name)
            
            print(f"Loaded vector store for topic '{topic}' with {len(self.documents)} documents")
            return True
        except Exception as e:
            print(f"Error loading vector store for topic '{topic}': {e}")
            return False
    
    def index_exists(self, topic: str) -> bool:
        """Check if an index exists for the given topic."""
        topic_dir = os.path.join(FAISS_INDEX_PATH, topic.replace(" ", "_").lower())
        index_path = os.path.join(topic_dir, "index.faiss")
        data_path = os.path.join(topic_dir, "data.pkl")
        
        return os.path.exists(index_path) and os.path.exists(data_path)
    
    def get_document_count(self) -> int:
        """Get the total number of documents in the vector store."""
        return len(self.documents)
    
    def clear(self) -> None:
        """Clear the current vector store."""
        self.index = None
        self.documents = []
        self.metadata = []
    
    def get_topics(self) -> List[str]:
        """Get list of available topics in the vector store."""
        topics = []
        if os.path.exists(FAISS_INDEX_PATH):
            for item in os.listdir(FAISS_INDEX_PATH):
                item_path = os.path.join(FAISS_INDEX_PATH, item)
                if os.path.isdir(item_path):
                    # Check if it has the required files
                    if (os.path.exists(os.path.join(item_path, "index.faiss")) and 
                        os.path.exists(os.path.join(item_path, "data.pkl"))):
                        topics.append(item.replace("_", " ").title())
        return topics 