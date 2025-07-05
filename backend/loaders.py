import requests
import arxiv
from bs4 import BeautifulSoup
from langchain_community.document_loaders import WebBaseLoader, ArxivLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List, Dict, Optional
import re
import time
from config import MAX_DOCUMENTS_PER_TOPIC, CHUNK_SIZE, CHUNK_OVERLAP

class RoboticsDocumentLoader:
    """Loader for robotics-related documents from various sources."""
    
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len,
        )
    
    def load_arxiv_papers(self, topic: str, max_results: int = 10) -> List[Dict]:
        """Load papers from arXiv related to the topic."""
        try:
            # Search for papers related to the topic
            search_query = f"robotics {topic}"
            search = arxiv.Search(
                query=search_query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.SubmittedDate
            )
            
            documents = []
            for result in search.results():
                # Get paper metadata and abstract
                doc = {
                    "title": result.title,
                    "authors": [author.name for author in result.authors],
                    "summary": result.summary,
                    "published": result.published.strftime("%Y-%m-%d"),
                    "arxiv_id": result.entry_id,
                    "source": "arxiv"
                }
                documents.append(doc)
                
            return documents
        except Exception as e:
            print(f"Error loading arXiv papers: {e}")
            return []
    
    def load_ros_docs(self, topic: str) -> List[Dict]:
        """Load ROS documentation related to the topic."""
        try:
            # ROS documentation URLs
            ros_urls = [
                f"https://docs.ros.org/en/humble/Tutorials.html",
                f"https://wiki.ros.org/{topic.replace(' ', '_')}",
                f"https://docs.ros.org/en/humble/Concepts.html"
            ]
            
            documents = []
            for url in ros_urls:
                try:
                    loader = WebBaseLoader(url)
                    docs = loader.load()
                    
                    for doc in docs:
                        # Clean and process the content
                        content = self._clean_html_content(doc.page_content)
                        if content and len(content) > 100:  # Filter out very short content
                            documents.append({
                                "title": f"ROS Documentation - {topic}",
                                "content": content,
                                "url": url,
                                "source": "ros_docs"
                            })
                    
                    time.sleep(1)  # Be respectful to the server
                except Exception as e:
                    print(f"Error loading from {url}: {e}")
                    continue
            
            return documents
        except Exception as e:
            print(f"Error loading ROS docs: {e}")
            return []
    
    def load_stack_exchange(self, topic: str, max_results: int = 10) -> List[Dict]:
        """Load questions and answers from Robotics Stack Exchange."""
        try:
            # Search Robotics Stack Exchange
            search_url = f"https://robotics.stackexchange.com/search?q={topic.replace(' ', '+')}"
            
            response = requests.get(search_url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find question links
                question_links = soup.find_all('a', href=re.compile(r'/questions/\d+/'))
                documents = []
                
                for link in question_links[:max_results]:
                    try:
                        question_url = f"https://robotics.stackexchange.com{link['href']}"
                        question_response = requests.get(question_url, headers={
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                        })
                        
                        if question_response.status_code == 200:
                            question_soup = BeautifulSoup(question_response.content, 'html.parser')
                            
                            # Extract question title and content
                            title_elem = question_soup.find('h1', class_='question-hyperlink')
                            content_elem = question_soup.find('div', class_='question')
                            
                            if title_elem and content_elem:
                                title = title_elem.get_text().strip()
                                content = self._clean_html_content(content_elem.get_text())
                                
                                if content and len(content) > 100:
                                    documents.append({
                                        "title": title,
                                        "content": content,
                                        "url": question_url,
                                        "source": "stack_exchange"
                                    })
                        
                        time.sleep(1)  # Be respectful to the server
                    except Exception as e:
                        print(f"Error processing question: {e}")
                        continue
                
                return documents
            else:
                return []
        except Exception as e:
            print(f"Error loading Stack Exchange: {e}")
            return []
    
    def load_web_documents(self, topic: str) -> List[Dict]:
        """Load general web documents related to the topic."""
        try:
            # Search for educational content about the topic
            search_queries = [
                f"{topic} robotics tutorial",
                f"{topic} robotics explanation",
                f"{topic} robotics applications"
            ]
            
            documents = []
            for query in search_queries:
                try:
                    # Use a simple web search approach
                    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
                    response = requests.get(search_url, headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    })
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Extract snippets from search results
                        snippets = soup.find_all('div', class_='VwiC3b')
                        for snippet in snippets[:5]:  # Limit to 5 snippets per query
                            content = snippet.get_text().strip()
                            if content and len(content) > 50:
                                documents.append({
                                    "title": f"Web Search - {query}",
                                    "content": content,
                                    "url": search_url,
                                    "source": "web_search"
                                })
                    
                    time.sleep(2)  # Be respectful to Google
                except Exception as e:
                    print(f"Error in web search for {query}: {e}")
                    continue
            
            return documents
        except Exception as e:
            print(f"Error loading web documents: {e}")
            return []
    
    def _clean_html_content(self, content: str) -> str:
        """Clean HTML content and extract meaningful text."""
        # Remove extra whitespace and newlines
        content = re.sub(r'\s+', ' ', content)
        content = content.strip()
        
        # Remove common HTML artifacts
        content = re.sub(r'\[.*?\]', '', content)
        content = re.sub(r'\(.*?\)', '', content)
        
        return content
    
    def load_all_sources(self, topic: str) -> List[Dict]:
        """Load documents from all available sources for a given topic."""
        all_documents = []
        
        print(f"Loading documents for topic: {topic}")
        
        # Load from different sources
        arxiv_docs = self.load_arxiv_papers(topic, max_results=5)
        ros_docs = self.load_ros_docs(topic)
        stack_exchange_docs = self.load_stack_exchange(topic, max_results=5)
        web_docs = self.load_web_documents(topic)
        
        # Combine all documents
        all_documents.extend(arxiv_docs)
        all_documents.extend(ros_docs)
        all_documents.extend(stack_exchange_docs)
        all_documents.extend(web_docs)
        
        # Limit total documents
        if len(all_documents) > MAX_DOCUMENTS_PER_TOPIC:
            all_documents = all_documents[:MAX_DOCUMENTS_PER_TOPIC]
        
        print(f"Loaded {len(all_documents)} documents for topic: {topic}")
        return all_documents
    
    def split_documents(self, documents: List[Dict]) -> List[Dict]:
        """Split documents into smaller chunks for better processing."""
        split_docs = []
        
        for doc in documents:
            if "content" in doc:
                # Split the content
                chunks = self.text_splitter.split_text(doc["content"])
                
                for i, chunk in enumerate(chunks):
                    split_doc = doc.copy()
                    split_doc["content"] = chunk
                    split_doc["chunk_id"] = i
                    split_docs.append(split_doc)
            else:
                # For documents without content field (like arXiv papers)
                split_docs.append(doc)
        
        return split_docs 