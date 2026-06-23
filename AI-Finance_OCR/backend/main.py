from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any

from backend.config import settings
from backend.services.tax_calculator import (
    calculate_thaiesg_quota,
    TaxCalculatorRequest,
    TaxCalculatorResponse
)
from backend.services.ocr_service import parse_50_tawi_ocr, OCRResult
from backend.services.vector_service import query_tax_regulations, answer_tax_query

app = FastAPI(
    title="Personal Tax & OCR Agent API",
    description="Backend service for processing 50 Tawi documents and calculating ThaiESG quotas.",
    version="1.0.0"
)

# Enable CORS for the Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the exact Streamlit origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TaxQueryRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Question about Thai tax laws or ThaiESG rules")

class TaxQueryResponse(BaseModel):
    query: str
    answer: str
    retrieved_contexts: List[Dict[str, Any]]

@app.get("/")
def read_root():
    return {
        "status": "healthy",
        "service": "Personal Tax & OCR Agent API",
        "supported_tax_year": 2569
    }

@app.post("/api/v1/tax/ocr", response_model=OCRResult)
async def upload_50_tawi(file: UploadFile = File(...)):
    """
    Upload a 50 Tawi document image to extract assessable income, withholding tax, and other deductions.
    """
    if not (file.content_type.startswith("image/") or file.content_type == "application/pdf" or file.filename.lower().endswith(".pdf")):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only image files (JPEG, PNG, WebP) and PDF documents are supported."
        )
    
    try:
        contents = await file.read()
        ocr_result = parse_50_tawi_ocr(contents, filename=file.filename)
        return ocr_result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process image OCR: {str(e)}"
        )

@app.post("/api/v1/tax/calculate", response_model=TaxCalculatorResponse)
def calculate_quota(request: TaxCalculatorRequest):
    """
    Calculate the ThaiESG quota and remaining limit based on assessable income and already purchased amount.
    """
    try:
        return calculate_thaiesg_quota(request)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Calculation error: {str(e)}"
        )

@app.post("/api/v1/tax/query", response_model=TaxQueryResponse)
def query_tax(request: TaxQueryRequest):
    """
    Query Thai tax regulations related to ThaiESG and 50 Tawi.
    """
    try:
        answer = answer_tax_query(request.query)
        retrieved_contexts = query_tax_regulations(request.query)
        return TaxQueryResponse(
            query=request.query,
            answer=answer,
            retrieved_contexts=retrieved_contexts
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Query processor error: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
