import arxiv
import time
from typing import List, Dict, Optional
from datetime import datetime
from langchain.text_splitter import RecursiveCharacterTextSplitter
from config import CHUNK_SIZE, CHUNK_OVERLAP

class ArxivSearcher:
    """Enhanced arXiv search and document processing."""
    
    def __init__(self):
        """Initialize the arXiv searcher."""
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len,
        )
        
        # Robotics-related categories for better search
        self.robotics_categories = [
            "cs.RO",  # Robotics
            "cs.AI",  # Artificial Intelligence
            "cs.CV",  # Computer Vision
            "cs.LG",  # Machine Learning
            "cs.SY",  # Systems and Control
            "cs.CE",  # Computational Engineering
        ]
    
    def search_papers(self, query: str, max_results: int = 5, sort_by: str = "relevance") -> List[Dict]:
        """Search arXiv for papers related to the query."""
        try:
            # Enhance query with robotics context
            enhanced_query = f"robotics {query}"
            
            # Determine sort criterion
            if sort_by == "relevance":
                sort_criterion = arxiv.SortCriterion.Relevance
            elif sort_by == "date":
                sort_criterion = arxiv.SortCriterion.SubmittedDate
            elif sort_by == "last_updated":
                sort_criterion = arxiv.SortCriterion.LastUpdatedDate
            else:
                sort_criterion = arxiv.SortCriterion.Relevance
            
            # Create search
            search = arxiv.Search(
                query=enhanced_query,
                max_results=max_results,
                sort_by=sort_criterion,
                sort_order=arxiv.SortOrder.Descending
            )
            
            papers = []
            for result in search.results():
                paper = {
                    "title": result.title,
                    "authors": [author.name for author in result.authors],
                    "summary": result.summary,
                    "published": result.published.strftime("%Y-%m-%d"),
                    "updated": result.updated.strftime("%Y-%m-%d"),
                    "arxiv_id": result.entry_id,
                    "pdf_url": result.pdf_url,
                    "categories": result.categories,
                    "doi": result.doi,
                    "journal_ref": result.journal_ref,
                    "primary_category": result.primary_category,
                    "source": "arxiv"
                }
                papers.append(paper)
                
                # Be respectful to arXiv servers
                time.sleep(1)
            
            return papers
            
        except Exception as e:
            print(f"Error searching arXiv: {e}")
            return []
    
    def search_by_category(self, category: str, max_results: int = 5) -> List[Dict]:
        """Search papers by specific arXiv category."""
        try:
            search = arxiv.Search(
                query=f"cat:{category}",
                max_results=max_results,
                sort_by=arxiv.SortCriterion.SubmittedDate,
                sort_order=arxiv.SortOrder.Descending
            )
            
            papers = []
            for result in search.results():
                paper = {
                    "title": result.title,
                    "authors": [author.name for author in result.authors],
                    "summary": result.summary,
                    "published": result.published.strftime("%Y-%m-%d"),
                    "updated": result.updated.strftime("%Y-%m-%d"),
                    "arxiv_id": result.entry_id,
                    "pdf_url": result.pdf_url,
                    "categories": result.categories,
                    "doi": result.doi,
                    "journal_ref": result.journal_ref,
                    "primary_category": result.primary_category,
                    "source": "arxiv"
                }
                papers.append(paper)
                time.sleep(1)
            
            return papers
            
        except Exception as e:
            print(f"Error searching by category {category}: {e}")
            return []
    
    def get_recent_robotics_papers(self, max_results: int = 10) -> List[Dict]:
        """Get recent papers from robotics categories."""
        all_papers = []
        
        for category in self.robotics_categories[:3]:  # Limit to top 3 categories
            papers = self.search_by_category(category, max_results // 3)
            all_papers.extend(papers)
        
        # Sort by publication date and limit
        all_papers.sort(key=lambda x: x["published"], reverse=True)
        return all_papers[:max_results]
    
    def process_papers_to_documents(self, papers: List[Dict]) -> List[Dict]:
        """Convert arXiv papers to document format for vector store."""
        documents = []
        
        for paper in papers:
            # Combine title and abstract for better context
            content = f"Title: {paper['title']}\n\nAbstract: {paper['summary']}"
            
            # Split into chunks
            chunks = self.text_splitter.split_text(content)
            
            for i, chunk in enumerate(chunks):
                doc = {
                    "content": chunk,
                    "title": paper["title"],
                    "source": "arxiv",
                    "url": paper["pdf_url"],
                    "authors": paper["authors"],
                    "published": paper["published"],
                    "arxiv_id": paper["arxiv_id"],
                    "categories": paper["categories"],
                    "doi": paper.get("doi", ""),
                    "chunk_id": i,
                    "total_chunks": len(chunks)
                }
                documents.append(doc)
        
        return documents
    
    def search_and_process(self, query: str, max_results: int = 5) -> Dict:
        """Search arXiv and process papers into documents."""
        try:
            # Search for papers
            papers = self.search_papers(query, max_results)
            
            if not papers:
                return {
                    "success": False,
                    "error": "No papers found for the query",
                    "papers": [],
                    "documents": []
                }
            
            # Process papers into documents
            documents = self.process_papers_to_documents(papers)
            
            return {
                "success": True,
                "papers": papers,
                "documents": documents,
                "paper_count": len(papers),
                "document_count": len(documents),
                "query": query
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "papers": [],
                "documents": []
            }
    
    def get_paper_citations(self, papers: List[Dict]) -> List[str]:
        """Generate citation strings for papers."""
        citations = []
        
        for paper in papers:
            authors_str = ", ".join(paper["authors"][:3])  # First 3 authors
            if len(paper["authors"]) > 3:
                authors_str += " et al."
            
            citation = f"{authors_str}. \"{paper['title']}\". arXiv preprint {paper['arxiv_id']} ({paper['published']})."
            citations.append(citation)
        
        return citations
    
    def validate_query(self, query: str) -> bool:
        """Validate if the query is appropriate for arXiv search."""
        # Basic validation - ensure query is not too short or too long
        if len(query.strip()) < 3:
            return False
        if len(query.strip()) > 200:
            return False
        
        # Check for inappropriate content (basic filter)
        inappropriate_terms = ["porn", "adult", "xxx", "sex"]
        query_lower = query.lower()
        for term in inappropriate_terms:
            if term in query_lower:
                return False
        
        return True 