import os
import json
import hashlib
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse
import time

from bs4 import BeautifulSoup
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from config import CHUNK_SIZE, CHUNK_OVERLAP

class MCPStore:
    """Memory Cache + Persistent Storage for documentation and content."""
    
    def __init__(self, cache_dir: str = "./mcp_cache", expiry_days: int = 30):
        """Initialize MCP store."""
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.metadata_file = self.cache_dir / "mcp_metadata.json"
        self.expiry_days = expiry_days
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len,
        )
        
        # Load or create metadata
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict:
        """Load metadata from file or create new."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading MCP metadata: {e}")
                return {}
        return {}
    
    def needs_refresh(self, topic: str, max_age_days: int = 15) -> bool:
        """Check if a topic needs to be refreshed based on its age."""
        try:
            relevant_sources = self.find_relevant_docs(topic)
            
            for topic_name, url in relevant_sources:
                cache_key = self._generate_cache_key(topic_name, url)
                
                if cache_key in self.metadata:
                    entry = self.metadata[cache_key]
                    timestamp = entry.get("timestamp", "")
                    
                    if timestamp:
                        cache_time = datetime.fromisoformat(timestamp)
                        age_days = (datetime.now() - cache_time).days
                        return age_days > max_age_days
            
            return True  # If no cached data found, needs refresh
            
        except Exception as e:
            print(f"Error checking refresh status: {e}")
            return True
    
    def get_topic_metadata(self, topic: str) -> Dict:
        """Get detailed metadata for a topic including age and source info."""
        try:
            relevant_sources = self.find_relevant_docs(topic)
            
            for topic_name, url in relevant_sources:
                cache_key = self._generate_cache_key(topic_name, url)
                
                if cache_key in self.metadata:
                    entry = self.metadata[cache_key]
                    
                    if not self._is_expired(entry.get("timestamp", "")):
                        cache_time = datetime.fromisoformat(entry.get("timestamp", ""))
                        age_days = (datetime.now() - cache_time).days
                        
                        return {
                            "cached": True,
                            "topic": topic_name,
                            "source_type": entry.get("source_type", "unknown"),
                            "last_updated": entry.get("timestamp", ""),
                            "age_days": age_days,
                            "document_count": entry.get("document_count", 0),
                            "needs_refresh": age_days > 15
                        }
            
            return {"cached": False, "needs_refresh": True}
            
        except Exception as e:
            print(f"Error getting topic metadata: {e}")
            return {"cached": False, "needs_refresh": True}
    
    def _save_metadata(self):
        """Save metadata to file."""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving MCP metadata: {e}")
    
    def _generate_cache_key(self, topic: str, source_url: str = "") -> str:
        """Generate a unique cache key for a topic and source."""
        content = f"{topic.lower().strip()}_{source_url}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _is_expired(self, timestamp: str) -> bool:
        """Check if a cached entry is expired."""
        try:
            cache_time = datetime.fromisoformat(timestamp)
            expiry_date = cache_time + timedelta(days=self.expiry_days)
            return datetime.now() > expiry_date
        except Exception:
            return True
    
    def get_cached_content(self, topic: str, source_url: str = "") -> Optional[Dict]:
        """Get cached content for a topic."""
        cache_key = self._generate_cache_key(topic, source_url)
        
        if cache_key in self.metadata:
            entry = self.metadata[cache_key]
            
            # Check if expired
            if self._is_expired(entry.get("timestamp", "")):
                print(f"MCP cache expired for {topic}")
                return None
            
            # Check if cache file exists
            cache_file = self.cache_dir / f"{cache_key}.json"
            if cache_file.exists():
                try:
                    with open(cache_file, 'r') as f:
                        cached_data = json.load(f)
                    cached_data["source"] = "mcp_cache"
                    cached_data["cache_age"] = self._get_cache_age(entry.get("timestamp", ""))
                    return cached_data
                except Exception as e:
                    print(f"Error loading cached content: {e}")
        
        return None
    
    def _get_cache_age(self, timestamp: str) -> str:
        """Get human-readable cache age."""
        try:
            cache_time = datetime.fromisoformat(timestamp)
            age = datetime.now() - cache_time
            if age.days > 0:
                return f"{age.days} days ago"
            elif age.seconds > 3600:
                return f"{age.seconds // 3600} hours ago"
            else:
                return f"{age.seconds // 60} minutes ago"
        except Exception:
            return "unknown"
    
    def cache_content(self, topic: str, documents: List[Dict], source_url: str = "", source_type: str = "web") -> str:
        """Cache content for a topic."""
        cache_key = self._generate_cache_key(topic, source_url)
        
        # Prepare cache entry
        cache_entry = {
            "topic": topic,
            "source_url": source_url,
            "source_type": source_type,
            "timestamp": datetime.now().isoformat(),
            "document_count": len(documents),
            "cache_key": cache_key
        }
        
        # Save metadata
        self.metadata[cache_key] = cache_entry
        self._save_metadata()
        
        # Save documents
        cache_file = self.cache_dir / f"{cache_key}.json"
        try:
            with open(cache_file, 'w') as f:
                json.dump({
                    "documents": documents,
                    "metadata": cache_entry
                }, f, indent=2, default=str)
            print(f"Cached {len(documents)} documents for topic '{topic}'")
            return cache_key
        except Exception as e:
            print(f"Error caching content: {e}")
            return ""
    
    def fetch_and_cache_docs(self, topic: str, source_url: str, source_type: str = "web") -> List[Dict]:
        """Fetch documentation from URL and cache it."""
        try:
            print(f"Fetching documentation for '{topic}' from {source_url}")
            
            # Fetch content
            if source_type == "web":
                documents = self._fetch_web_content(source_url)
            else:
                documents = []
            
            if documents:
                # Cache the documents
                self.cache_content(topic, documents, source_url, source_type)
                return documents
            else:
                print(f"No content found for {topic} at {source_url}")
                return []
                
        except Exception as e:
            print(f"Error fetching documentation for {topic}: {e}")
            return []
    
    def _fetch_web_content(self, url: str) -> List[Dict]:
        """Fetch content from web URL."""
        try:
            # Use LangChain's WebBaseLoader
            loader = WebBaseLoader(url)
            docs = loader.load()
            
            # Convert to our document format
            documents = []
            for doc in docs:
                # Clean the content
                content = self._clean_html_content(doc.page_content)
                if content and len(content) > 50:  # Filter out very short content
                    documents.append({
                        "content": content,
                        "title": f"Documentation from {url}",
                        "source": "mcp_web",
                        "url": url,
                        "authors": [],
                        "published": datetime.now().strftime("%Y-%m-%d"),
                        "chunk_id": len(documents),
                        "total_chunks": len(docs)
                    })
            
            return documents
            
        except Exception as e:
            print(f"Error fetching web content from {url}: {e}")
            return []
    
    def _clean_html_content(self, content: str) -> str:
        """Clean HTML content and extract meaningful text."""
        # Remove extra whitespace and newlines
        content = content.replace('\n', ' ').replace('\r', ' ')
        content = ' '.join(content.split())
        
        # Basic HTML tag removal (if any remain)
        content = content.replace('<', ' <').replace('>', '> ')
        content = ' '.join(content.split())
        
        return content.strip()
    
    def get_documentation_sources(self) -> Dict[str, List[str]]:
        """Get mapping of common topics to their documentation URLs."""
        return {
            "numpy": [
                "https://numpy.org/doc/stable/reference/",
                "https://numpy.org/doc/stable/user/",
                "https://numpy.org/doc/stable/contents.html"
            ],
            "pandas": [
                "https://pandas.pydata.org/docs/",
                "https://pandas.pydata.org/docs/reference/"
            ],
            "matplotlib": [
                "https://matplotlib.org/stable/",
                "https://matplotlib.org/stable/tutorials/"
            ],
            "scikit-learn": [
                "https://scikit-learn.org/stable/",
                "https://scikit-learn.org/stable/modules/"
            ],
            "opencv": [
                "https://docs.opencv.org/",
                "https://docs.opencv.org/master/"
            ],
            "ros": [
                "https://docs.ros.org/",
                "https://wiki.ros.org/"
            ],
            "tensorflow": [
                "https://www.tensorflow.org/guide",
                "https://www.tensorflow.org/tutorials"
            ],
            "pytorch": [
                "https://pytorch.org/docs/",
                "https://pytorch.org/tutorials/"
            ]
        }
    
    def find_relevant_docs(self, query: str) -> List[Tuple[str, str]]:
        """Find relevant documentation sources for a query."""
        query_lower = query.lower()
        relevant_sources = []
        
        doc_sources = self.get_documentation_sources()
        
        for topic, urls in doc_sources.items():
            if topic in query_lower:
                for url in urls:
                    relevant_sources.append((topic, url))
        
        return relevant_sources
    
    def query_mcp(self, query: str) -> Optional[Dict]:
        """Query MCP store for relevant documents using vector search."""
        try:
            # First check if we have any cached content that matches the query
            relevant_sources = self.find_relevant_docs(query)
            
            all_documents = []
            for topic, url in relevant_sources:
                cached_content = self.get_cached_content(topic, url)
                if cached_content:
                    all_documents.extend(cached_content.get("documents", []))
            
            if all_documents:
                # Return the most relevant documents (simple keyword matching for now)
                # In a full implementation, you'd use vector search here
                relevant_docs = []
                query_terms = query.lower().split()
                
                for doc in all_documents:
                    content = doc.get("content", "").lower()
                    relevance_score = sum(1 for term in query_terms if term in content)
                    if relevance_score > 0:
                        doc["relevance_score"] = relevance_score
                        relevant_docs.append(doc)
                
                # Sort by relevance and return top results
                relevant_docs.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
                
                return {
                    "documents": relevant_docs[:5],  # Top 5 most relevant
                    "source": "mcp_cache",
                    "cache_age": self._get_cache_age(datetime.now().isoformat()),
                    "total_found": len(relevant_docs)
                }
            
            return None
            
        except Exception as e:
            print(f"Error querying MCP: {e}")
            return None
    
    def save_topic_to_mcp(self, topic: str, documents: List[Dict], source: str = "arxiv") -> str:
        """Save a topic and its documents to MCP for future reference."""
        try:
            # Generate a cache key for the topic
            cache_key = self._generate_cache_key(topic)
            
            # Save the documents
            cache_entry = {
                "topic": topic,
                "source_url": f"source_{source}",
                "source_type": source,
                "timestamp": datetime.now().isoformat(),
                "document_count": len(documents),
                "cache_key": cache_key
            }
            
            # Save metadata
            self.metadata[cache_key] = cache_entry
            self._save_metadata()
            
            # Save documents
            cache_file = self.cache_dir / f"{cache_key}.json"
            with open(cache_file, 'w') as f:
                json.dump({
                    "documents": documents,
                    "metadata": cache_entry
                }, f, indent=2, default=str)
            
            print(f"Saved topic '{topic}' to MCP with {len(documents)} documents")
            return cache_key
            
        except Exception as e:
            print(f"Error saving topic to MCP: {e}")
            return ""
    
    def get_source_status(self, topic: str) -> Dict:
        """Check if a topic is cached and return its status."""
        try:
            relevant_sources = self.find_relevant_docs(topic)
            
            for topic_name, url in relevant_sources:
                cache_key = self._generate_cache_key(topic_name, url)
                
                if cache_key in self.metadata:
                    entry = self.metadata[cache_key]
                    
                    if not self._is_expired(entry.get("timestamp", "")):
                        return {
                            "cached": True,
                            "topic": topic_name,
                            "cache_age": self._get_cache_age(entry.get("timestamp", "")),
                            "document_count": entry.get("document_count", 0),
                            "source_type": entry.get("source_type", "unknown")
                        }
            
            return {"cached": False}
            
        except Exception as e:
            print(f"Error getting source status: {e}")
            return {"cached": False}
    
    def refresh_topic(self, topic: str, force_refresh: bool = False) -> Dict:
        """Refresh a topic by re-fetching from its source."""
        try:
            metadata = self.get_topic_metadata(topic)
            
            # Check if refresh is needed
            if not force_refresh and metadata.get("cached") and not metadata.get("needs_refresh"):
                return {
                    "refreshed": False,
                    "reason": "Topic is still fresh",
                    "metadata": metadata
                }
            
            print(f"🔄 Refreshing topic: {topic}")
            
            # Find relevant sources and re-fetch
            relevant_sources = self.find_relevant_docs(topic)
            
            for topic_name, url in relevant_sources:
                cache_key = self._generate_cache_key(topic_name, url)
                
                # Remove old cache entry
                if cache_key in self.metadata:
                    del self.metadata[cache_key]
                    
                    # Remove cache file
                    cache_file = self.cache_dir / f"{cache_key}.json"
                    if cache_file.exists():
                        cache_file.unlink()
                
                # Re-fetch from source
                documents = self.fetch_and_cache_docs(topic_name, url, "web")
                
                if documents:
                    return {
                        "refreshed": True,
                        "topic": topic_name,
                        "documents_fetched": len(documents),
                        "source_url": url,
                        "new_metadata": self.get_topic_metadata(topic)
                    }
            
            return {
                "refreshed": False,
                "reason": "No sources found for topic",
                "metadata": metadata
            }
            
        except Exception as e:
            print(f"Error refreshing topic: {e}")
            return {
                "refreshed": False,
                "reason": f"Error: {str(e)}",
                "metadata": {}
            }
    
    def get_cache_stats(self) -> Dict:
        """Get statistics about cached content."""
        total_entries = len(self.metadata)
        expired_entries = 0
        valid_entries = 0
        
        for cache_key, entry in self.metadata.items():
            if self._is_expired(entry.get("timestamp", "")):
                expired_entries += 1
            else:
                valid_entries += 1
        
        return {
            "total_entries": total_entries,
            "valid_entries": valid_entries,
            "expired_entries": expired_entries,
            "cache_dir": str(self.cache_dir),
            "expiry_days": self.expiry_days
        }
    
    def clear_expired_cache(self) -> int:
        """Clear expired cache entries."""
        expired_keys = []
        
        for cache_key, entry in self.metadata.items():
            if self._is_expired(entry.get("timestamp", "")):
                expired_keys.append(cache_key)
        
        # Remove expired entries
        for key in expired_keys:
            del self.metadata[key]
            
            # Remove cache file
            cache_file = self.cache_dir / f"{key}.json"
            if cache_file.exists():
                cache_file.unlink()
        
        self._save_metadata()
        return len(expired_keys)
    
    def clear_all_cache(self) -> int:
        """Clear all cached content."""
        count = len(self.metadata)
        
        # Remove all cache files
        for cache_file in self.cache_dir.glob("*.json"):
            if cache_file.name != "mcp_metadata.json":
                cache_file.unlink()
        
        # Clear metadata
        self.metadata = {}
        self._save_metadata()
        
        return count 