import re
import math
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple
from pypdf import PdfReader

class SimpleVectorDB:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_file = db_path / "documents.json"
        self.documents: Dict[str, List[Dict[str, Any]]] = {}  # Ticker -> List of chunks
        self.load()

    def load(self):
        """Loads index from file if it exists."""
        if self.db_file.exists():
            try:
                with open(self.db_file, "r", encoding="utf-8") as f:
                    self.documents = json.load(f)
            except Exception:
                self.documents = {}

    def save(self):
        """Saves index to file."""
        with open(self.db_file, "w", encoding="utf-8") as f:
            json.dump(self.documents, f, ensure_ascii=False, indent=2)

    def _preprocess(self, text: str) -> List[str]:
        """Simple tokenizer that works for English and Thai (using character/ngram fallback)."""
        # Convert to lowercase
        text = text.lower()
        # Find English words and Thai chunks
        words = re.findall(r'[a-zA-Z0-9]+|[\u0e00-\u0e7f]+', text)
        
        tokens = []
        for word in words:
            # If it's Thai text (contains Thai characters), generate bigrams/trigrams since there are no spaces
            if any('\u0e00' <= char <= '\u0e7f' for char in word):
                # Thai character-level split for finer matching
                tokens.extend([word[i:i+3] for i in range(len(word)-2)])
                tokens.extend([word[i:i+2] for i in range(len(word)-1)])
            else:
                tokens.append(word)
        return [t for t in tokens if len(t) > 1]

    def add_pdf(self, ticker: str, pdf_path: Path):
        """Parses a PDF file, splits it into chunks, and indexes it."""
        ticker = ticker.upper()
        if not pdf_path.exists():
            return
        
        reader = PdfReader(pdf_path)
        full_text = ""
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                full_text += f"\n--- Page {i+1} ---\n{page_text}"

        # Split text into chunks of approx 1000 characters with 200 character overlap
        chunk_size = 1000
        overlap = 200
        chunks = []
        
        start = 0
        while start < len(full_text):
            end = min(start + chunk_size, len(full_text))
            chunk_content = full_text[start:end]
            chunks.append({
                "source": pdf_path.name,
                "text": chunk_content,
                "start_char": start,
                "end_char": end
            })
            start += chunk_size - overlap

        self.documents[ticker] = chunks
        self.save()

    def search(self, ticker: str, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Performs a TF-IDF similarity search over the indexed chunks of a ticker.
        """
        ticker = ticker.upper()
        if ticker not in self.documents or not self.documents[ticker]:
            return []

        chunks = self.documents[ticker]
        query_tokens = self._preprocess(query)
        if not query_tokens:
            return chunks[:top_k]

        # Calculate TF-IDF vectors
        # Document frequencies of terms in the ticker corpus
        doc_counts = {}
        for chunk in chunks:
            seen_tokens = set(self._preprocess(chunk["text"]))
            for t in seen_tokens:
                doc_counts[t] = doc_counts.get(t, 0) + 1

        num_docs = len(chunks)
        idf = {term: math.log((1 + num_docs) / (1 + count)) + 1 for term, count in doc_counts.items()}

        # Compute TF-IDF for query
        query_tf = {}
        for t in query_tokens:
            query_tf[t] = query_tf.get(t, 0) + 1
        
        query_tfidf = {t: tf * idf.get(t, 0) for t, tf in query_tf.items() if t in idf}
        query_norm = math.sqrt(sum(val**2 for val in query_tfidf.values()))

        results: List[Tuple[float, Dict[str, Any]]] = []
        
        for chunk in chunks:
            chunk_tokens = self._preprocess(chunk["text"])
            if not chunk_tokens:
                continue
                
            chunk_tf = {}
            for t in chunk_tokens:
                chunk_tf[t] = chunk_tf.get(t, 0) + 1
                
            chunk_tfidf = {t: tf * idf.get(t, 0) for t, tf in chunk_tf.items() if t in idf}
            chunk_norm = math.sqrt(sum(val**2 for val in chunk_tfidf.values()))
            
            # Compute dot product
            dot_product = sum(query_tfidf.get(t, 0) * chunk_tfidf.get(t, 0) for t in query_tokens)
            
            # Cosine similarity
            similarity = 0.0
            if query_norm > 0 and chunk_norm > 0:
                similarity = dot_product / (query_norm * chunk_norm)
                
            results.append((similarity, chunk))

        # Sort by similarity descending
        results.sort(key=lambda x: x[0], reverse=True)
        
        # Return top_k
        return [
            {**chunk, "score": float(score)} 
            for score, chunk in results[:top_k]
        ]
