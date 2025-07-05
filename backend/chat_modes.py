#!/usr/bin/env python3
"""
Chat modes module for Robotics Chatbot.
Handles Research Chat, Tutorial/How-to Chat, and Explanation Chat with specific prompts and processing.
"""

from typing import Dict, List, Optional
from datetime import datetime
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from backend.mcp_store import MCPStore

class ChatModeProcessor:
    """Base class for chat mode processing with 3-step prompt improvement."""
    
    def __init__(self, llm):
        self.llm = llm
        self.mcp_store = MCPStore()
    
    def process_3step_prompt(self, user_input: str, mode_specific_context: str = "") -> Dict:
        """3-step prompt improvement pipeline for all chat modes."""
        try:
            # Step 1: Raw user input
            raw_input = user_input
            
            # Step 2: Gemini-enhanced improved prompt
            improved_prompt = self._enhance_prompt_for_mode(raw_input, mode_specific_context)
            
            # Step 3: Final prompt sent to Gemini for response
            final_answer = self._generate_final_response(improved_prompt, mode_specific_context)
            
            return {
                "raw_input": raw_input,
                "improved_prompt": improved_prompt,
                "final_answer": final_answer,
                "success": True
            }
            
        except Exception as e:
            print(f"Error in 3-step processing: {e}")
            return {
                "raw_input": user_input,
                "improved_prompt": "Error enhancing prompt",
                "final_answer": f"Sorry, I encountered an error: {str(e)}",
                "success": False
            }
    
    def _enhance_prompt_for_mode(self, user_input: str, context: str = "") -> str:
        """Enhance prompt based on chat mode - to be overridden by subclasses."""
        raise NotImplementedError
    
    def _generate_final_response(self, improved_prompt: str, context: str = "") -> str:
        """Generate final response - to be overridden by subclasses."""
        raise NotImplementedError


class ResearchChatProcessor(ChatModeProcessor):
    """Research Chat mode processor for research questions and paper analysis."""
    
    def __init__(self, llm):
        super().__init__(llm)
        
        # Research-specific prompt templates
        self.research_enhancement_prompt = PromptTemplate(
            input_variables=["user_input", "context"],
            template="""
You are a robotics research assistant. Enhance the following research question to be more specific and comprehensive for academic analysis.

Original Question: {user_input}

Available Context: {context}

Please rewrite this as a detailed research question that:
- Specifies the robotics domain and application area
- Requests theoretical foundations and mathematical analysis
- Asks for current state-of-the-art approaches
- Requests practical implementation considerations
- Includes request for recent developments and trends

Enhanced Research Question:"""
        )
        
        self.research_synthesis_prompt = PromptTemplate(
            input_variables=["research_question", "paper_summaries", "external_context"],
            template="""
You are a robotics research expert. Synthesize the following information to provide a comprehensive research answer.

Research Question: {research_question}

Paper Summaries:
{paper_summaries}

External Context: {external_context}

Please provide a comprehensive research synthesis that includes:

## Research Overview
Brief introduction to the research area and question.

## Current State of the Art
Analysis of existing approaches and methodologies.

## Theoretical Foundations
Mathematical and theoretical background relevant to the research.

## Key Findings
Main insights from the analyzed papers and sources.

## Practical Applications
Real-world applications and implementation considerations.

## Future Directions
Emerging trends and potential research directions.

## Sources
List and briefly describe the key sources used in this synthesis.

Make this response academic yet accessible, with clear structure and comprehensive coverage.
"""
        )
    
    def _enhance_prompt_for_mode(self, user_input: str, context: str = "") -> str:
        """Enhance research question for better analysis."""
        try:
            response = self.llm.invoke(self.research_enhancement_prompt.format(
                user_input=user_input,
                context=context
            ))
            return response.content.strip()
        except Exception as e:
            print(f"Error enhancing research prompt: {e}")
            return user_input
    
    def _generate_final_response(self, improved_prompt: str, context: str = "") -> str:
        """Generate research synthesis response."""
        try:
            # For now, use a simplified response generation
            # In full implementation, this would process paper summaries and external context
            response = self.llm.invoke(f"""
You are a robotics research expert. Answer the following research question comprehensively:

{improved_prompt}

Provide a detailed, academic-level response that covers theoretical foundations, current approaches, and practical applications in robotics.
""")
            return response.content.strip()
        except Exception as e:
            print(f"Error generating research response: {e}")
            return f"Error generating research response: {str(e)}"
    
    def process_research_question(self, question: str, uploaded_papers: List[Dict] = None) -> Dict:
        """Process a research question with optional paper uploads."""
        try:
            # Step 1: Process uploaded papers if any
            paper_summaries = []
            if uploaded_papers:
                for paper in uploaded_papers:
                    summary = self._summarize_paper(paper)
                    paper_summaries.append(summary)
            
            # Step 2: Check for ArXiv papers if no uploads
            if not paper_summaries:
                from backend.arxiv_search import ArxivSearcher
                arxiv_searcher = ArxivSearcher()
                arxiv_result = arxiv_searcher.search_and_process(question, max_results=3)
                
                if arxiv_result.get("success") and arxiv_result.get("documents"):
                    for doc in arxiv_result["documents"]:
                        summary = self._summarize_paper(doc)
                        paper_summaries.append(summary)
            
            # Step 3: Generate research synthesis
            context = "\n".join(paper_summaries) if paper_summaries else ""
            result = self.process_3step_prompt(question, context)
            
            return {
                **result,
                "paper_count": len(paper_summaries),
                "source": "research_synthesis"
            }
            
        except Exception as e:
            print(f"Error processing research question: {e}")
            return {
                "raw_input": question,
                "improved_prompt": "Error processing",
                "final_answer": f"Error processing research question: {str(e)}",
                "success": False
            }
    
    def _summarize_paper(self, paper: Dict) -> str:
        """Summarize a research paper using Gemini."""
        try:
            content = paper.get("content", paper.get("summary", ""))
            title = paper.get("title", "Unknown")
            
            summary_prompt = f"""
Summarize the following research paper for robotics research analysis:

Title: {title}
Content: {content[:2000]}...

Please provide a concise summary that includes:
1. Main research contribution
2. Methodology used
3. Key findings
4. Relevance to robotics
5. Practical implications

Summary:"""
            
            response = self.llm.invoke(summary_prompt)
            return response.content.strip()
            
        except Exception as e:
            print(f"Error summarizing paper: {e}")
            return f"Error summarizing paper: {str(e)}"


class TutorialChatProcessor(ChatModeProcessor):
    """Tutorial/How-to Chat mode processor for code tutorials and documentation."""
    
    def __init__(self, llm):
        super().__init__(llm)
        
        # Tutorial-specific prompt templates
        self.tutorial_enhancement_prompt = PromptTemplate(
            input_variables=["user_input", "library_name", "context"],
            template="""
You are a robotics tutorial expert. Enhance the following tutorial request to be more specific and actionable.

Original Request: {user_input}
Library/Framework: {library_name}

Available Documentation Context: {context}

Please rewrite this as a detailed tutorial request that:
- Specifies the exact functionality or concept to be taught
- Requests step-by-step implementation guidance
- Asks for code examples and explanations
- Includes best practices and common pitfalls
- Requests practical applications in robotics

Enhanced Tutorial Request:"""
        )
        
        self.tutorial_generation_prompt = PromptTemplate(
            input_variables=["enhanced_request", "documentation_context", "output_mode"],
            template="""
You are a robotics tutorial expert. Create a comprehensive tutorial based on the following request.

Enhanced Request: {enhanced_request}

Documentation Context: {documentation_context}

Output Mode: {output_mode}

Please create a detailed tutorial that includes:

## Overview
Brief introduction to the concept or functionality.

## Prerequisites
What the user should know before starting.

## Step-by-Step Implementation
Detailed instructions with {output_mode} examples.

## Code Examples
Clear, well-commented code snippets that demonstrate the concept.

## Best Practices
Important tips and common pitfalls to avoid.

## Practical Applications
Real-world robotics applications and use cases.

## Testing and Validation
How to test and verify the implementation.

Make the tutorial educational, practical, and focused on robotics applications.
"""
        )
    
    def _enhance_prompt_for_mode(self, user_input: str, context: str = "") -> str:
        """Enhance tutorial request for better guidance."""
        try:
            # Extract library name from context if available
            library_name = context.split("Library: ")[-1].split("\n")[0] if "Library: " in context else "robotics"
            
            response = self.llm.invoke(self.tutorial_enhancement_prompt.format(
                user_input=user_input,
                library_name=library_name,
                context=context
            ))
            return response.content.strip()
        except Exception as e:
            print(f"Error enhancing tutorial prompt: {e}")
            return user_input
    
    def _generate_final_response(self, improved_prompt: str, context: str = "") -> str:
        """Generate tutorial response with code or examples."""
        try:
            # Determine output mode from context
            output_mode = "Code" if "code" in context.lower() else "Example"
            
            response = self.llm.invoke(self.tutorial_generation_prompt.format(
                enhanced_request=improved_prompt,
                documentation_context=context,
                output_mode=output_mode
            ))
            return response.content.strip()
        except Exception as e:
            print(f"Error generating tutorial response: {e}")
            return f"Error generating tutorial response: {str(e)}"
    
    def process_tutorial_request(self, request: str, library_name: str, doc_url: str, output_mode: str) -> Dict:
        """Process a tutorial request with library documentation."""
        try:
            # Step 1: Store documentation in MCP if not already cached
            topic_key = f"{library_name}_tutorial"
            
            # Check if documentation is already cached
            cached_docs = self.mcp_store.query_mcp(topic_key)
            
            if not cached_docs or not cached_docs.get("documents"):
                # In a full implementation, this would fetch and process the documentation
                # For now, we'll create a placeholder context
                context = f"Library: {library_name}\nDocumentation URL: {doc_url}\nOutput Mode: {output_mode}"
            else:
                context = self._format_documentation_context(cached_docs["documents"])
                context += f"\nOutput Mode: {output_mode}"
            
            # Step 2: Generate tutorial
            result = self.process_3step_prompt(request, context)
            
            return {
                **result,
                "library_name": library_name,
                "doc_url": doc_url,
                "output_mode": output_mode,
                "source": "tutorial_generation"
            }
            
        except Exception as e:
            print(f"Error processing tutorial request: {e}")
            return {
                "raw_input": request,
                "improved_prompt": "Error processing",
                "final_answer": f"Error processing tutorial request: {str(e)}",
                "success": False
            }
    
    def _format_documentation_context(self, documents: List[Dict]) -> str:
        """Format documentation context for tutorial generation."""
        context_parts = []
        for doc in documents:
            content = doc.get("content", "")
            title = doc.get("title", "Documentation")
            context_parts.append(f"Title: {title}\nContent: {content[:1000]}...")
        
        return "\n\n".join(context_parts)


class ExplanationChatProcessor(ChatModeProcessor):
    """Explanation Chat mode processor for concept explanations with complexity levels."""
    
    def __init__(self, llm):
        super().__init__(llm)
        
        # Explanation-specific prompt templates
        self.explanation_enhancement_prompt = PromptTemplate(
            input_variables=["user_input", "complexity_level", "context"],
            template="""
You are a robotics education expert. Enhance the following explanation request for {complexity_level} level understanding.

Original Request: {user_input}
Complexity Level: {complexity_level}

Available Context: {context}

Please rewrite this as a detailed explanation request that:
- Specifies the exact concept or mechanism to be explained
- Requests {complexity_level}-appropriate depth and detail
- Asks for relevant examples and analogies
- Includes practical applications in robotics
- Requests clear progression from basic to advanced understanding

Enhanced Explanation Request:"""
        )
        
        self.explanation_generation_prompt = PromptTemplate(
            input_variables=["enhanced_request", "complexity_level", "output_mode", "context"],
            template="""
You are a robotics education expert. Create a comprehensive explanation for {complexity_level} level understanding.

Enhanced Request: {enhanced_request}
Complexity Level: {complexity_level}
Output Mode: {output_mode}

Available Context: {context}

Please create a detailed explanation that includes:

## Concept Overview
Clear introduction to the concept at {complexity_level} level.

## Fundamental Principles
Core principles and theoretical foundations.

## Detailed Explanation
In-depth explanation with {complexity_level}-appropriate detail.

## {output_mode} Demonstrations
Practical {output_mode.lower()} that illustrate the concept.

## Applications in Robotics
Real-world robotics applications and use cases.

## Common Misconceptions
Important clarifications and common misunderstandings.

## Further Learning
Suggestions for deeper understanding and related topics.

Tailor the explanation for {complexity_level} level understanding with appropriate technical depth and practical examples.
"""
        )
    
    def _enhance_prompt_for_mode(self, user_input: str, context: str = "") -> str:
        """Enhance explanation request based on complexity level."""
        try:
            # Extract complexity level from context
            complexity_level = "Intermediate"  # Default
            if "beginner" in context.lower():
                complexity_level = "Beginner"
            elif "expert" in context.lower():
                complexity_level = "Expert"
            
            response = self.llm.invoke(self.explanation_enhancement_prompt.format(
                user_input=user_input,
                complexity_level=complexity_level,
                context=context
            ))
            return response.content.strip()
        except Exception as e:
            print(f"Error enhancing explanation prompt: {e}")
            return user_input
    
    def _generate_final_response(self, improved_prompt: str, context: str = "") -> str:
        """Generate explanation response with appropriate complexity."""
        try:
            # Extract complexity and output mode from context
            complexity_level = "Intermediate"
            output_mode = "Example"
            
            if "beginner" in context.lower():
                complexity_level = "Beginner"
            elif "expert" in context.lower():
                complexity_level = "Expert"
            
            if "code" in context.lower():
                output_mode = "Code"
            
            response = self.llm.invoke(self.explanation_generation_prompt.format(
                enhanced_request=improved_prompt,
                complexity_level=complexity_level,
                output_mode=output_mode,
                context=context
            ))
            return response.content.strip()
        except Exception as e:
            print(f"Error generating explanation response: {e}")
            return f"Error generating explanation response: {str(e)}"
    
    def process_explanation_request(self, request: str, complexity_level: str, output_mode: str) -> Dict:
        """Process an explanation request with specified complexity and output mode."""
        try:
            # Step 1: Prepare context with complexity and output mode
            context = f"Complexity Level: {complexity_level}\nOutput Mode: {output_mode}"
            
            # Step 2: Generate explanation
            result = self.process_3step_prompt(request, context)
            
            return {
                **result,
                "complexity_level": complexity_level,
                "output_mode": output_mode,
                "source": "explanation_generation"
            }
            
        except Exception as e:
            print(f"Error processing explanation request: {e}")
            return {
                "raw_input": request,
                "improved_prompt": "Error processing",
                "final_answer": f"Error processing explanation request: {str(e)}",
                "success": False
            } 