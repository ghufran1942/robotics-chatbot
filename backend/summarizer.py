import os
from typing import List, Dict, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.schema import Document
from config import GOOGLE_API_KEY

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
You are an expert robotics educator. Based on the provided context and question, provide a comprehensive, structured answer about the robotics concept.

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