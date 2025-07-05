import os
from typing import List, Dict, Optional
from datetime import datetime
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.schema import Document
from config import GOOGLE_API_KEY
from backend.mcp_store import MCPStore

class RoboticsSummarizer:
    """LangChain-based summarizer for robotics documents using Google Gemini."""
    
    def __init__(self):
        """Initialize the summarizer with Google Gemini model."""
        if not GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is required. Please set it in your environment variables.")
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=GOOGLE_API_KEY,
            temperature=0.3,
            max_output_tokens=2048
        )
        
        # Define the prompt template for structured answers
        self.prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template="""
You are an robotics expert. Based on the provided context and question, provide a comprehensive, structured answer.

Context from various sources:
{context}

Question: {question}

Please structure your answer in the following format:

## Introduction
Provide a clear, concise introduction to the concept.

## Applications in Robotics
Explain how this concept is applied in robotics systems and real-world scenarios.

## Mathematical Explanation
If applicable, provide the mathematical formulas, equations, or derivations related to this concept. If not applicable, explain the theoretical foundations.

## Tuning Methods and Usage
Explain common tuning methods, parameters, or practical considerations when implementing this concept in robotics.

## Sources
List the key sources used to ground this answer (from the provided context).

Guidelines:
- Be accurate and educational
- Use clear, accessible language
- Include practical examples when possible
- Cite specific information from the provided context
- If the context doesn't contain enough information, acknowledge this and provide general knowledge
- Focus on robotics applications and relevance
"""
        )
        
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt_template)
        
        # Initialize MCP store
        self.mcp_store = MCPStore()
    
    def format_context(self, search_results: List[Dict]) -> str:
        """Format search results into a context string for the LLM."""
        if not search_results:
            return "No relevant documents found."
        
        context_parts = []
        for i, result in enumerate(search_results, 1):
            doc = result["document"]
            metadata = result["metadata"]
            score = result["score"]
            
            # Extract content
            content = doc.get("content", doc.get("summary", ""))
            if not content:
                continue
            
            # Format the context entry
            context_entry = f"Source {i} (Relevance: {score:.3f}):\n"
            context_entry += f"Title: {metadata.get('title', 'Unknown')}\n"
            context_entry += f"Source: {metadata.get('source', 'unknown')}\n"
            
            if metadata.get("authors"):
                context_entry += f"Authors: {', '.join(metadata['authors'])}\n"
            
            if metadata.get("published"):
                context_entry += f"Published: {metadata['published']}\n"
            
            if metadata.get("url"):
                context_entry += f"URL: {metadata['url']}\n"
            
            context_entry += f"Content: {content[:1000]}...\n"  # Limit content length
            context_entry += "-" * 50 + "\n"
            
            context_parts.append(context_entry)
        
        return "\n".join(context_parts)
    
    def generate_answer(self, question: str, search_results: List[Dict]) -> Dict:
        """Generate a comprehensive answer based on search results."""
        try:
            # Format the context from search results
            context = self.format_context(search_results)
            
            # Generate the answer using the LLM chain
            response = self.chain.run({
                "context": context,
                "question": question
            })
            
            # Extract sources from search results
            sources = []
            for result in search_results:
                metadata = result["metadata"]
                source_info = {
                    "title": metadata.get("title", "Unknown"),
                    "source": metadata.get("source", "unknown"),
                    "url": metadata.get("url", ""),
                    "authors": metadata.get("authors", []),
                    "published": metadata.get("published", ""),
                    "relevance_score": result["score"]
                }
                sources.append(source_info)
            
            return {
                "answer": response,
                "sources": sources,
                "num_sources": len(sources),
                "context_length": len(context)
            }
            
        except Exception as e:
            print(f"Error generating answer: {e}")
            return {
                "answer": f"Sorry, I encountered an error while generating the answer: {str(e)}",
                "sources": [],
                "num_sources": 0,
                "context_length": 0
            }
    
    def process_question_with_workflow(self, question: str, explain_concept: bool = True,
                                     include_examples: bool = True, include_code: bool = True) -> Dict:
        """Process a question using the complete workflow: MCP → arXiv → LLM."""
        try:
            # Step 1: Check MCP first with proper priority logic
            print("🔍 Checking MCP for relevant documents...")
            mcp_result = self.check_mcp_for_docs(question)
            
            # Get topic metadata to check freshness
            topic_metadata = self.mcp_store.get_topic_metadata(question)
            needs_refresh = topic_metadata.get("needs_refresh", True)
            
            # Check if MCP has relevant content and it's not stale
            if mcp_result and mcp_result.get("documents") and not needs_refresh:
                print("✅ Found fresh relevant documents in MCP")
                
                # Use MCP documents to generate answer
                context = self.format_context_from_mcp(mcp_result["documents"])
                enhanced_question = self.construct_smart_prompt(question, explain_concept, include_examples, include_code)
                
                response = self.chain.run({
                    "context": context,
                    "question": enhanced_question
                })
                
                # Format the source badge with freshness info
                source_type = topic_metadata.get("source_type", "mcp")
                age_days = topic_metadata.get("age_days", 0)
                last_updated = topic_metadata.get("last_updated", "")
                
                if last_updated:
                    try:
                        update_date = datetime.fromisoformat(last_updated).strftime("%B %d, %Y")
                        source_badge = f"[from {source_type.upper()}] (updated: {update_date})"
                    except:
                        source_badge = f"[from {source_type.upper()}]"
                else:
                    source_badge = f"[from {source_type.upper()}]"
                
                return {
                    "answer": response,
                    "source": "mcp",
                    "source_type": source_type,
                    "source_badge": source_badge,
                    "documents_used": len(mcp_result["documents"]),
                    "cache_age": f"{age_days} days ago",
                    "last_updated": last_updated,
                    "needs_refresh": needs_refresh,
                    "sources": self.extract_sources_from_mcp(mcp_result["documents"]),
                    "references": self.extract_references_from_mcp(mcp_result["documents"])
                }
            
            # Step 2: If MCP is stale or empty, refresh or fetch from arXiv
            elif mcp_result and mcp_result.get("documents") and needs_refresh:
                print("🔄 MCP data is stale, refreshing from source...")
                refresh_result = self.mcp_store.refresh_topic(question)
                
                if refresh_result.get("refreshed"):
                    print("✅ Successfully refreshed MCP data")
                    # Re-query MCP with fresh data
                    mcp_result = self.check_mcp_for_docs(question)
                    topic_metadata = self.mcp_store.get_topic_metadata(question)
                    
                    # Use refreshed MCP documents
                    context = self.format_context_from_mcp(mcp_result["documents"])
                    enhanced_question = self.construct_smart_prompt(question, explain_concept, include_examples, include_code)
                    
                    response = self.chain.run({
                        "context": context,
                        "question": enhanced_question
                    })
                    
                    return {
                        "answer": response,
                        "source": "mcp_refreshed",
                        "source_type": "arxiv",
                        "source_badge": "[from ARXIV] (freshly updated)",
                        "documents_used": len(mcp_result["documents"]),
                        "last_updated": datetime.now().isoformat(),
                        "needs_refresh": False,
                        "sources": self.extract_sources_from_mcp(mcp_result["documents"]),
                        "references": self.extract_references_from_mcp(mcp_result["documents"])
                    }
            
            # Step 3: If no MCP content or refresh failed, try arXiv
            print("📚 No MCP content found, searching arXiv...")
            source_type = self.determine_source_type(question)
            
            if source_type == "arxiv":
                print("📚 Query appears academic/technical, searching arXiv...")
                # Import here to avoid circular imports
                from backend.arxiv_search import ArxivSearcher
                arxiv_searcher = ArxivSearcher()
                
                arxiv_result = arxiv_searcher.search_and_process(question, max_results=3)
                
                if arxiv_result.get("success") and arxiv_result.get("documents"):
                    print(f"✅ Found {len(arxiv_result['documents'])} arXiv documents")
                    
                    # Save to MCP for future use with current timestamp
                    topic = question.split()[0:3]  # Use first 3 words as topic
                    topic_str = " ".join(topic)
                    self.mcp_store.save_topic_to_mcp(topic_str, arxiv_result["documents"], "arxiv")
                    
                    # Generate answer
                    context = self.format_context_from_arxiv(arxiv_result["documents"])
                    enhanced_question = self.construct_smart_prompt(question, explain_concept, include_examples, include_code)
                    
                    response = self.chain.run({
                        "context": context,
                        "question": enhanced_question
                    })
                    
                    # Format arXiv source badge with freshness info
                    current_time = datetime.now().isoformat()
                    update_date = datetime.now().strftime("%B %d, %Y")
                    source_badge = f"[from ARXIV] (updated: {update_date})"
                    
                    return {
                        "answer": response,
                        "source": "arxiv",
                        "source_type": "arxiv",
                        "source_badge": source_badge,
                        "documents_used": len(arxiv_result["documents"]),
                        "last_updated": current_time,
                        "needs_refresh": False,  # Fresh data
                        "references": arxiv_result.get("references", []),
                        "sources": self.extract_sources_from_arxiv(arxiv_result["documents"])
                    }
            
            # Step 4: Fallback to direct LLM answer
            print("🤖 No relevant documents found, using direct LLM answer...")
            enhanced_question = self.construct_smart_prompt(question, explain_concept, include_examples, include_code)
            
            response = self.llm.invoke(enhanced_question)
            
            return {
                "answer": response.content if hasattr(response, 'content') else str(response),
                "source": "gemini",
                "source_type": "llm",
                "source_badge": "[from GEMINI]",
                "documents_used": 0,
                "sources": [],
                "references": []
            }
            
        except Exception as e:
            print(f"Error in workflow: {e}")
            return {
                "answer": f"Sorry, I encountered an error: {str(e)}",
                "source_type": "error",
                "source_badge": "[error]",
                "documents_used": 0,
                "sources": []
            }
    
    def format_context_from_mcp(self, documents: List[Dict]) -> str:
        """Format MCP documents into context string."""
        context_parts = []
        for i, doc in enumerate(documents, 1):
            content = doc.get("content", "")
            title = doc.get("title", f"Document {i}")
            source = doc.get("source", "mcp")
            
            context_entry = f"Source {i} (MCP Cache):\n"
            context_entry += f"Title: {title}\n"
            context_entry += f"Source: {source}\n"
            context_entry += f"Content: {content[:1000]}...\n"
            context_entry += "-" * 50 + "\n"
            
            context_parts.append(context_entry)
        
        return "\n".join(context_parts)
    
    def format_context_from_arxiv(self, documents: List[Dict]) -> str:
        """Format arXiv documents into context string."""
        context_parts = []
        for i, doc in enumerate(documents, 1):
            content = doc.get("content", "")
            title = doc.get("title", f"Paper {i}")
            authors = doc.get("authors", [])
            arxiv_id = doc.get("arxiv_id", "")
            
            context_entry = f"Source {i} (arXiv Paper):\n"
            context_entry += f"Title: {title}\n"
            context_entry += f"Authors: {', '.join(authors)}\n"
            context_entry += f"arXiv ID: {arxiv_id}\n"
            context_entry += f"Content: {content[:1000]}...\n"
            context_entry += "-" * 50 + "\n"
            
            context_parts.append(context_entry)
        
        return "\n".join(context_parts)
    
    def extract_sources_from_mcp(self, documents: List[Dict]) -> List[Dict]:
        """Extract source information from MCP documents."""
        sources = []
        for doc in documents:
            source_info = {
                "title": doc.get("title", "Unknown"),
                "source": "mcp_cache",
                "url": doc.get("url", ""),
                "authors": doc.get("authors", []),
                "published": doc.get("published", ""),
                "relevance_score": doc.get("relevance_score", 0)
            }
            sources.append(source_info)
        return sources
    
    def extract_sources_from_arxiv(self, documents: List[Dict]) -> List[Dict]:
        """Extract source information from arXiv documents."""
        sources = []
        for doc in documents:
            source_info = {
                "title": doc.get("title", "Unknown"),
                "source": "arxiv",
                "url": doc.get("url", ""),
                "authors": doc.get("authors", []),
                "published": doc.get("published", ""),
                "arxiv_id": doc.get("arxiv_id", ""),
                "relevance_score": doc.get("relevance_score", 0)
            }
            sources.append(source_info)
        return sources
    
    def extract_references_from_mcp(self, documents: List[Dict]) -> List[Dict]:
        """Extract reference information from MCP documents."""
        references = []
        for doc in documents:
            ref_info = {
                "title": doc.get("title", "Unknown"),
                "source": doc.get("source", "mcp"),
                "url": doc.get("url", ""),
                "authors": doc.get("authors", []),
                "published": doc.get("published", ""),
                "relevance_score": doc.get("relevance_score", 0)
            }
            references.append(ref_info)
        return references
    
    def generate_topic_summary(self, topic: str, documents: List[Dict]) -> str:
        """Generate a summary of a robotics topic based on collected documents."""
        try:
            # Create a summary prompt
            summary_prompt = PromptTemplate(
                input_variables=["topic", "documents"],
                template="""
You are a robotics expert. Create a comprehensive overview of the topic "{topic}" based on the following documents:

{documents}

Please provide:
1. A clear definition and explanation of the concept
2. Key applications in robotics
3. Important principles or mathematical foundations
4. Current trends or developments
5. Practical considerations for implementation

Make it educational and accessible for robotics learners.
"""
            )
            
            # Format documents for the prompt
            doc_texts = []
            for i, doc in enumerate(documents, 1):
                content = doc.get("content", doc.get("summary", ""))
                if content:
                    doc_texts.append(f"Document {i}: {content[:500]}...")
            
            documents_text = "\n\n".join(doc_texts)
            
            # Generate summary
            summary_chain = LLMChain(llm=self.llm, prompt=summary_prompt)
            summary = summary_chain.run({
                "topic": topic,
                "documents": documents_text
            })
            
            return summary
            
        except Exception as e:
            print(f"Error generating topic summary: {e}")
            return f"Error generating summary for {topic}: {str(e)}"
    
    def check_mcp_for_docs(self, query: str) -> Optional[Dict]:
        """Check MCP store for relevant documentation using the new query_mcp method."""
        try:
            # Use the new query_mcp method
            mcp_result = self.mcp_store.query_mcp(query)
            
            if mcp_result and mcp_result.get("documents"):
                print(f"Found {len(mcp_result['documents'])} relevant documents in MCP")
                return mcp_result
            
            return None
            
        except Exception as e:
            print(f"Error checking MCP for docs: {e}")
            return None
    
    def construct_smart_prompt(self, question: str, explain_concept: bool = True, 
                             include_examples: bool = True, include_code: bool = True) -> str:
        """Construct a smart prompt based on user preferences."""
        prompt_parts = [question]
        
        # Add explanation request
        if explain_concept:
            prompt_parts.append("Please provide a clear explanation of this concept.")
        
        # Add examples request
        if include_examples:
            prompt_parts.append("Include one or more real-world examples and applications in robotics.")
        
        # Add code request
        if include_code:
            prompt_parts.append("Include runnable Python code snippets or demonstrations that show how to implement this concept.")
        
        return " ".join(prompt_parts)
    
    def determine_source_type(self, query: str) -> str:
        """Determine if a query is academic/technical and should use arXiv."""
        academic_keywords = [
            "slam", "localization", "mapping", "navigation", "control", "kinematics",
            "dynamics", "vision", "perception", "planning", "optimization", "learning",
            "neural", "deep", "reinforcement", "autonomous", "robotic", "robot"
        ]
        
        query_lower = query.lower()
        for keyword in academic_keywords:
            if keyword in query_lower:
                return "arxiv"
        
        return "general"
    
    def validate_question(self, question: str) -> bool:
        """Validate if the question is appropriate for the robotics chatbot."""
        try:
            validation_prompt = PromptTemplate(
                input_variables=["question"],
                template="""
Determine if the following question is related to robotics, engineering, or technical concepts that would be appropriate for a robotics educational chatbot.

Question: {question}

Respond with only 'YES' if the question is appropriate for a robotics chatbot, or 'NO' if it's not related to robotics, engineering, or technical topics.
"""
            )
            
            validation_chain = LLMChain(llm=self.llm, prompt=validation_prompt)
            response = validation_chain.run({"question": question})
            
            return "YES" in response.upper()
            
        except Exception as e:
            print(f"Error validating question: {e}")
            return True  # Default to accepting the question if validation fails
    
    def rewrite_prompt_with_gemini(self, user_question: str) -> str:
        """Rewrite user question into a more specific technical prompt using Gemini."""
        try:
            rewrite_prompt = f"""You are a robotics expert. Given the user's question below, rewrite it as a clear and specific prompt for Gemini.

The rewritten prompt should:
- Be more specific and technical
- Include key aspects to cover (theory, applications, examples)
- Use precise robotics terminology
- Request practical examples and code where relevant
- Focus on robotics

Original Question: "{user_question}"

Please rewrite this as a detailed technical prompt:"""

            response = self.llm.invoke(rewrite_prompt)
            return response.content.strip()
            
        except Exception as e:
            print(f"Error rewriting prompt: {e}")
            # Fallback to original question if rewriting fails
            return user_question
    
    def get_final_answer(self, refined_prompt: str, context: str = "") -> str:
        """Get final answer using the refined prompt and optional context."""
        try:
            if context:
                full_prompt = f"""Context from robotics sources:
{context}

Based on the context above, answer the following question in detail: {refined_prompt}"""
            else:
                full_prompt = f"""{refined_prompt}"""

            response = self.llm.invoke(full_prompt)
            return response.content.strip()
            
        except Exception as e:
            print(f"Error getting final answer: {e}")
            return f"Sorry, I encountered an error while processing your question: {str(e)}"
    
    def process_question_3step(self, user_question: str, context: str = "") -> Dict:
        """Process a question using the 3-step loop: Rewrite → Enhance → Answer."""
        try:
            # Step 1: Rewrite the question
            refined_prompt = self.rewrite_prompt_with_gemini(user_question)
            
            # Step 2: Get final answer
            final_answer = self.get_final_answer(refined_prompt, context)
            
            return {
                "original_question": user_question,
                "refined_prompt": refined_prompt,
                "final_answer": final_answer,
                "success": True
            }
            
        except Exception as e:
            print(f"Error in 3-step processing: {e}")
            return {
                "original_question": user_question,
                "refined_prompt": "Error rewriting prompt",
                "final_answer": f"Sorry, I encountered an error: {str(e)}",
                "success": False
            } 