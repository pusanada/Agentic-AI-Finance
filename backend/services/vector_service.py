import re
import math
import logging
from typing import List, Dict, Any, Tuple
from backend.config import settings

logger = logging.getLogger(__name__)

# Fallback Pure Python Vector Store to ensure Windows compatibility
class SimpleTaxVectorStore:
    def __init__(self):
        self.documents: List[str] = []
        self.metadatas: List[Dict[str, Any]] = []

    def add_documents(self, documents: List[str], metadatas: List[Dict[str, Any]]):
        self.documents.extend(documents)
        self.metadatas.extend(metadatas)

    def _tokenize(self, text: str) -> List[str]:
        # Simple word tokenization supporting English and some Thai split cues (basic spacing)
        # In a real environment, we'd use PyThaiNLP, but basic string split works for search
        return re.findall(r'\w+', text.lower())

    def _cosine_similarity(self, query: str, doc: str) -> float:
        q_tokens = self._tokenize(query)
        d_tokens = self._tokenize(doc)
        
        if not q_tokens or not d_tokens:
            return 0.0

        # Term frequencies
        q_tf = {}
        for token in q_tokens:
            q_tf[token] = q_tf.get(token, 0) + 1

        d_tf = {}
        for token in d_tokens:
            d_tf[token] = d_tf.get(token, 0) + 1

        # Cosine similarity calculations
        dot_product = 0.0
        for token in q_tf:
            if token in d_tf:
                dot_product += q_tf[token] * d_tf[token]

        q_norm = math.sqrt(sum(val ** 2 for val in q_tf.values()))
        d_norm = math.sqrt(sum(val ** 2 for val in d_tf.values()))

        if q_norm == 0 or d_norm == 0:
            return 0.0
            
        return dot_product / (q_norm * d_norm)

    def query(self, query_text: str, n_results: int = 3) -> List[Tuple[str, Dict[str, Any], float]]:
        scores = []
        for idx, doc in enumerate(self.documents):
            score = self._cosine_similarity(query_text, doc)
            # Add small weight to keywords overlap
            scores.append((doc, self.metadatas[idx], score))
        
        # Sort by score descending
        scores.sort(key=lambda x: x[2], reverse=True)
        return scores[:n_results]

# Seed Tax Regulations Data
TAX_REGULATIONS = [
    {
        "text": "ThaiESG (Thailand ESG Fund) is a tax-saving mutual fund established to promote sustainable investment in Thailand. Taxpayers can deduct their investments in ThaiESG to reduce their personal income tax liability.",
        "metadata": {"topic": "ThaiESG Definition", "section": "General Rules"}
    },
    {
        "text": "For Tax Year 2569 (2026), the maximum tax deduction limit for ThaiESG is 30% of assessable income (เงินได้พึงประเมิน), capped at 300,000 THB per year.",
        "metadata": {"topic": "ThaiESG Limit", "section": "Quota Limits"}
    },
    {
        "text": "The mandatory holding period for ThaiESG units is 5 full years from the purchase date (calculated day-to-day, not calendar years). No minimum investment is required.",
        "metadata": {"topic": "ThaiESG Holding Period", "section": "Holding Rules"}
    },
    {
        "text": "The 50 Tawi (หนังสือรับรองการหักภาษี ณ ที่จ่าย) document is a withholding tax certificate issued by employers. Section 40(1) represents salary/bonus income, and 40(2) represents general services/freelance income.",
        "metadata": {"topic": "50 Tawi", "section": "Assessable Income Sources"}
    },
    {
        "text": "ThaiESG investment quota is separate and NOT shared with the 500,000 THB retirement fund pool (which includes RMF, SSF, Provident Fund, and Pension Life Insurance). This means you get an extra 300,000 THB limit specifically for ThaiESG.",
        "metadata": {"topic": "ThaiESG vs Other Funds", "section": "Exemptions"}
    },
    {
        "text": "If a taxpayer sells ThaiESG units before the 5-year holding period, they must return all tax benefits received plus a surcharge (fine) to the Revenue Department.",
        "metadata": {"topic": "Breach of Conditions", "section": "Penalties"}
    }
]

# Initialize and seed the database
vector_store = SimpleTaxVectorStore()
for item in TAX_REGULATIONS:
    vector_store.add_documents([item["text"]], [item["metadata"]])

def query_tax_regulations(query_text: str) -> List[Dict[str, Any]]:
    """Queries the local store and returns matching regulations."""
    results = vector_store.query(query_text, n_results=3)
    formatted_results = []
    for doc, meta, score in results:
        formatted_results.append({
            "content": doc,
            "metadata": meta,
            "relevance_score": round(score, 4)
        })
    return formatted_results

def answer_tax_query(query_text: str) -> str:
    """
    Answers a tax query using context from the vector store.
    Uses Typhoon instruct LLM if configured, otherwise returns a structured retrieval response.
    """
    retrieved = query_tax_regulations(query_text)
    context = "\n\n".join([f"- {r['content']}" for r in retrieved if r['relevance_score'] > 0.05])
    
    if not context:
        context = "No highly relevant tax regulation documents found in the database. Please refer to the general ThaiESG guidelines."

    if settings.typhoon_api_key == "mock_key" or not settings.typhoon_api_key:
        # Fallback structured answer (local logic)
        answer = f"**Retrieved Context:**\n{context}\n\n**Answer:**\nBased on Thai ESG rules, you can deduct up to 30% of your assessable income (up to 300,000 THB) with a holding period of 5 years. Please refer to the specific sections above for details."
        return answer

    try:
        from openai import OpenAI
        client = OpenAI(
            api_key=settings.typhoon_api_key,
            base_url=settings.typhoon_api_base
        )
        
        prompt = f"""
        You are a professional Thai tax planning advisor.
        Answer the user's question using the provided context. If the context doesn't contain the answer, use your knowledge about Thai tax laws but state that it is general advice.
        
        Context:
        {context}
        
        Question:
        {query_text}
        
        Provide a concise, helpful answer in Thai or English depending on the question's language.
        """
        
        response = client.chat.completions.create(
            model=settings.typhoon_model_text,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error calling Typhoon text model: {str(e)}")
        return f"**Retrieved Context:**\n{context}\n\n**Answer (API Fallback):**\nCould not call Typhoon Text API. Please refer to the retrieved regulations above."
