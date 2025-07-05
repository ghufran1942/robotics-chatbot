import os
import hashlib
from typing import List, Dict, Optional
from pathlib import Path
import tempfile
import shutil
from datetime import datetime

# PDF processing libraries
try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

try:
    from langchain_community.document_loaders import PyPDFLoader
    LANGCHAIN_PDF_AVAILABLE = True
except ImportError:
    LANGCHAIN_PDF_AVAILABLE = False

from langchain.text_splitter import RecursiveCharacterTextSplitter
from config import CHUNK_SIZE, CHUNK_OVERLAP

class PDFUploader:
    """Handles PDF upload, text extraction, and integration with vector store."""
    
    def __init__(self, upload_dir: str = "./uploads"):
        """Initialize the PDF uploader."""
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(exist_ok=True)
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len,
        )
        
        # Check available PDF libraries
        self.available_libraries = []
        if PYPDF2_AVAILABLE:
            self.available_libraries.append("PyPDF2")
        if PDFPLUMBER_AVAILABLE:
            self.available_libraries.append("pdfplumber")
        if LANGCHAIN_PDF_AVAILABLE:
            self.available_libraries.append("langchain")
    
    def save_uploaded_file(self, uploaded_file, filename: str) -> str:
        """Save uploaded file to disk and return the file path."""
        # Generate unique filename to avoid conflicts
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_hash = hashlib.md5(filename.encode()).hexdigest()[:8]
        safe_filename = f"{timestamp}_{file_hash}_{filename}"
        file_path = self.upload_dir / safe_filename
        
        # Save the file
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        return str(file_path)
    
    def extract_text_pypdf2(self, file_path: str) -> str:
        """Extract text using PyPDF2."""
        try:
            text = ""
            with open(file_path, "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n"
            return text
        except Exception as e:
            print(f"PyPDF2 extraction error: {e}")
            return ""
    
    def extract_text_pdfplumber(self, file_path: str) -> str:
        """Extract text using pdfplumber."""
        try:
            text = ""
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text
        except Exception as e:
            print(f"pdfplumber extraction error: {e}")
            return ""
    
    def extract_text_langchain(self, file_path: str) -> str:
        """Extract text using LangChain's PyPDFLoader."""
        try:
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            text = "\n".join([doc.page_content for doc in documents])
            return text
        except Exception as e:
            print(f"LangChain extraction error: {e}")
            return ""
    
    def extract_text(self, file_path: str) -> str:
        """Extract text from PDF using the best available method."""
        if not self.available_libraries:
            raise ValueError("No PDF processing libraries available. Install PyPDF2, pdfplumber, or langchain-community.")
        
        # Try different methods in order of preference
        text = ""
        
        # Try pdfplumber first (best for complex layouts)
        if PDFPLUMBER_AVAILABLE:
            text = self.extract_text_pdfplumber(file_path)
            if text.strip():
                return text
        
        # Try LangChain's PyPDFLoader
        if LANGCHAIN_PDF_AVAILABLE:
            text = self.extract_text_langchain(file_path)
            if text.strip():
                return text
        
        # Try PyPDF2 as fallback
        if PYPDF2_AVAILABLE:
            text = self.extract_text_pypdf2(file_path)
            if text.strip():
                return text
        
        if not text.strip():
            raise ValueError("Could not extract text from PDF using any available method.")
        
        return text
    
    def process_pdf(self, uploaded_file, filename: str) -> Dict:
        """Process uploaded PDF and return document chunks."""
        try:
            # Save the uploaded file
            file_path = self.save_uploaded_file(uploaded_file, filename)
            
            # Extract text
            text = self.extract_text(file_path)
            
            if not text.strip():
                raise ValueError("No text could be extracted from the PDF.")
            
            # Split text into chunks
            chunks = self.text_splitter.split_text(text)
            
            # Create document objects
            documents = []
            for i, chunk in enumerate(chunks):
                doc = {
                    "content": chunk,
                    "title": filename,
                    "source": "uploaded_pdf",
                    "url": "",
                    "authors": [],
                    "published": datetime.now().strftime("%Y-%m-%d"),
                    "file_path": file_path,
                    "chunk_id": i,
                    "total_chunks": len(chunks)
                }
                documents.append(doc)
            
            return {
                "success": True,
                "documents": documents,
                "filename": filename,
                "file_path": file_path,
                "chunk_count": len(chunks),
                "text_length": len(text)
            }
            
        except Exception as e:
            # Clean up file if processing failed
            if 'file_path' in locals() and os.path.exists(file_path):
                os.remove(file_path)
            
            return {
                "success": False,
                "error": str(e),
                "filename": filename
            }
    
    def get_uploaded_files(self) -> List[Dict]:
        """Get list of uploaded PDF files."""
        files = []
        if self.upload_dir.exists():
            for file_path in self.upload_dir.glob("*.pdf"):
                stat = file_path.stat()
                files.append({
                    "filename": file_path.name,
                    "file_path": str(file_path),
                    "size": stat.st_size,
                    "uploaded": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                })
        return files
    
    def delete_uploaded_file(self, filename: str) -> bool:
        """Delete an uploaded PDF file."""
        try:
            file_path = self.upload_dir / filename
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception as e:
            print(f"Error deleting file {filename}: {e}")
            return False
    
    def clear_all_uploads(self) -> bool:
        """Clear all uploaded PDF files."""
        try:
            if self.upload_dir.exists():
                shutil.rmtree(self.upload_dir)
                self.upload_dir.mkdir(exist_ok=True)
            return True
        except Exception as e:
            print(f"Error clearing uploads: {e}")
            return False
    
    def get_upload_stats(self) -> Dict:
        """Get statistics about uploaded files."""
        files = self.get_uploaded_files()
        total_size = sum(f["size"] for f in files)
        
        return {
            "file_count": len(files),
            "total_size": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "available_libraries": self.available_libraries
        } 