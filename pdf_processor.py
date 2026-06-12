import PyPDF2
import pdfplumber
import re
from typing import List, Dict
import hashlib

class PDFProcessor:
    def __init__(self, use_chunking: bool = True, chunk_size: int = 1000):
        self.use_chunking = use_chunking
        self.chunk_size = chunk_size
        
    def extract_text(self, pdf_path: str) -> Dict:
        print(f"📖 Processing PDF: {pdf_path}")
        
        full_text = ""
        pages_text = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text:
                        full_text += text + "\n"
                        pages_text.append({
                            "page": page_num + 1,
                            "text": text,
                            "section": self._detect_section(text)
                        })
        except:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    if text:
                        full_text += text + "\n"
                        pages_text.append({
                            "page": page_num + 1,
                            "text": text,
                            "section": self._detect_section(text)
                        })
        
        if self.use_chunking:
            chunks = self._create_semantic_chunks(full_text)
        else:
            chunks = [{"content": full_text, "type": "full", "hash": hashlib.md5(full_text.encode()).hexdigest()[:8]}]
        
        return {
            "total_pages": len(pages_text),
            "full_text": full_text,
            "pages": pages_text,
            "chunks": chunks,
            "metadata": {
                "source": pdf_path,
                "chunk_strategy": "semantic" if self.use_chunking else "full",
                "total_chunks": len(chunks)
            }
        }
    
    def _detect_section(self, text: str) -> str:
        lines = text.strip().split('\n')
        for line in lines[:5]:
            line = line.strip()
            patterns = [
                r'^(Chapter\s+\d+[.:])',
                r'^(\d+\.\d+\s+)',
                r'^(Section\s+\d+)',
                r'^([A-Z][A-Z\s]{5,})$',
                r'^(\d+\.\s+[A-Z])',
            ]
            for pattern in patterns:
                if re.match(pattern, line):
                    return line
        return "Content"
    
    def _create_semantic_chunks(self, text: str) -> List[Dict]:
        chunks = []
        paragraphs = re.split(r'\n\s*\n', text)
        
        current_chunk = ""
        current_paragraphs = []
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            if len(current_chunk) + len(para) > self.chunk_size and current_chunk:
                chunks.append({
                    "content": current_chunk,
                    "type": "semantic",
                    "paragraph_count": len(current_paragraphs),
                    "hash": hashlib.md5(current_chunk.encode()).hexdigest()[:8]
                })
                current_chunk = para
                current_paragraphs = [para]
            else:
                current_chunk += "\n\n" + para if current_chunk else para
                current_paragraphs.append(para)
        
        if current_chunk:
            chunks.append({
                "content": current_chunk,
                "type": "semantic",
                "paragraph_count": len(current_paragraphs),
                "hash": hashlib.md5(current_chunk.encode()).hexdigest()[:8]
            })
        
        return chunks
