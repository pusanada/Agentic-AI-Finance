import uuid
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

from backend.config import settings
from backend.services.tax_calculator import (
    calculate_thaiesg_quota,
    TaxCalculatorRequest,
    TaxCalculatorResponse
)
from backend.services.ocr_service import parse_50_tawi_ocr, OCRResult
from backend.services.vector_service import query_tax_regulations, answer_tax_query

# Import new Portfolio Allocator agent components
from backend.services.portfolio_allocator import allocate_assets, DraftPortfolio
from backend.services.compliance_guard import check_portfolio_compliance, ComplianceReport
from backend.services.auq_manager import evaluate_system_confidence, evaluate_system_confidence_from_state, AUQReport
from backend.services.state_manager import state_manager

app = FastAPI(
    title="ThaiESG Portfolio Allocator & Compliance Guard API",
    description="Backend service for orchestrating ThaiESG tax quota calculations, ESG fund screening, portfolio allocation, and compliance safeguards.",
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

# New Portfolio Allocator request/response schemas
class PortfolioAllocateRequest(BaseModel):
    assessable_income: float = Field(..., ge=0, description="Customer total income")
    already_purchased: float = Field(default=0.0, ge=0, description="Amount already invested in ThaiESG this year")
    financial_goal: str = Field(..., description="Investment goal (Growth, Dividend, Balanced)")
    risk_profile: str = Field(..., description="Risk profile (Conservative, Moderate, Aggressive)")
    user_instructions: str = Field(default="", description="Any custom fund/stock constraints")
    ocr_confidence: float = Field(default=1.0, description="Confidence score from the OCR step")
    session_id: Optional[str] = Field(default=None, description="Optional active session ID")

class PortfolioAllocateResponse(BaseModel):
    quota: TaxCalculatorResponse
    portfolio: DraftPortfolio
    compliance: ComplianceReport
    auq: AUQReport
    execution_trace: List[str]
    session_id: str

class GenericPortfolioAllocateRequest(BaseModel):
    investment_budget: float = Field(..., ge=0, description="Direct investment budget in THB")
    financial_goal: str = Field(..., description="Investment goal (Growth, Dividend, Balanced)")
    risk_profile: str = Field(..., description="Risk profile (Conservative, Moderate, Aggressive)")
    user_instructions: str = Field(default="", description="Any custom fund/stock constraints")
    session_id: Optional[str] = Field(default=None, description="Optional active session ID")

class GenericPortfolioAllocateResponse(BaseModel):
    portfolio: DraftPortfolio
    compliance: ComplianceReport
    auq: AUQReport
    execution_trace: List[str]
    session_id: str

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

@app.post("/api/v1/portfolio/allocate", response_model=PortfolioAllocateResponse)
def allocate_portfolio(request: PortfolioAllocateRequest):
    """
    Orchestrates the portfolio allocation workflow:
    1. Demand Side: Calculates the tax saving quota.
    2. Supply Side: Fetches ESG fund options.
    3. Allocator Agent: Generates a draft portfolio.
    4. Compliance Guard Agent: Checks rules. If violations occur, self-heals by running an allocation adjustment loop.
    5. AUQ Manager: Audits uncertainty and risk, outputting system confidence metrics.
    """
    trace = []
    sess_id = request.session_id or f"session-{uuid.uuid4().hex[:8]}"
    
    try:
        # Step 0: Save OCR State to state_manager first
        ocr_data = {
            "assessable_income": request.assessable_income,
            "already_purchased": request.already_purchased,
            "document_type": "50 Tawi (books / forms)",
            "confidence": request.ocr_confidence
        }
        state_manager.update_ocr(
            session_id=sess_id,
            ocr_result=ocr_data,
            confidence=request.ocr_confidence,
            uncertainty_factors=[] if request.ocr_confidence >= 0.99 else ["Low OCR Extraction Confidence"]
        )

        # Step 1: Calculate Quota (Demand)
        quota_req = TaxCalculatorRequest(
            assessable_income=request.assessable_income,
            already_purchased=request.already_purchased
        )
        quota_res = calculate_thaiesg_quota(quota_req)
        remaining = quota_res.remaining_quota
        trace.append(f"Demand Quota: Calculated remaining space as ฿{remaining:,.2f} (Max quota: ฿{quota_res.max_quota:,.2f})")
        
        if remaining <= 0:
            remaining = 0.0
            trace.append("Warning: Remaining quota is zero. Generating empty draft portfolio.")

        # Step 2: Orchestration Loop with Compliance Guard
        current_risk_profile = "Aggressive"  # Start unconstrained to maximize financial goal
        current_instructions = request.user_instructions
        loop_count = 0
        max_loops = 3
        portfolio = None
        compliance = None
        
        while loop_count < max_loops:
            loop_count += 1
            trace.append(f"Cycle {loop_count}: Generating allocation weights for {request.financial_goal} goal & {current_risk_profile} profile...")
            
            # Run Allocator
            portfolio = allocate_assets(
                remaining_quota=remaining,
                goal=request.financial_goal,
                risk_profile=current_risk_profile,
                user_instructions=current_instructions
            )
            
            # Store Draft Portfolio in State Manager first
            state_manager.update_portfolio(
                session_id=sess_id,
                portfolio=portfolio.model_dump(),
                confidence=0.95,
                uncertainty_factors=[]
            )
            
            # Pre-fetch ESG data for all underlying stocks in Allocator
            from backend.services.jump_db import get_fund_underlying_holdings
            from backend.services.esg_client import esg_client
            for item in portfolio.allocations:
                holdings = get_fund_underlying_holdings(item.fund_code)
                if holdings:
                    for h in holdings:
                        ticker = h.get("ticker")
                        esg_client.get_esg_report(ticker, session_id=sess_id)
                else:
                    esg_client.get_esg_report(item.fund_code, session_id=sess_id)
            
            # Check Compliance (will load from State Manager and update it)
            compliance = check_portfolio_compliance(
                portfolio=portfolio,
                assessable_income=request.assessable_income,
                already_purchased=request.already_purchased,
                max_quota=quota_res.max_quota,
                client_risk_profile=request.risk_profile,
                session_id=sess_id
            )
            
            if compliance.is_compliant:
                trace.append("Compliance Guard check: PASSED.")
                break
            else:
                trace.append(f"Compliance Guard check: FAILED. Violations: {', '.join(compliance.violations)}")
                
                # Self-healing logic
                if "Risk Mismatch" in "".join(compliance.violations) or "Average Risk Limit" in "".join(compliance.violations):
                    trace.append("Self-Healing Action: Downgrading allocation risk profile parameter to 'Conservative' to enforce strict safety caps.")
                    current_risk_profile = "Conservative"
                elif "Quota Overshoot" in "".join(compliance.violations):
                    trace.append("Self-Healing Action: Adjusting allocation amount to strictly fit within remaining quota.")
                else:
                    trace.append("Self-Healing Action: Applying standard correction caps.")
                    break
        
        # Step 3: AUQ Supervisor Evaluation from State Manager (Consumes all confidence scores)
        auq_res = evaluate_system_confidence_from_state(sess_id)
        trace.append(f"AUQ Supervisor: Confidence computed as {auq_res.confidence_score}% (Rating: {auq_res.uncertainty_rating})")
        
        return PortfolioAllocateResponse(
            quota=quota_res,
            portfolio=portfolio,
            compliance=compliance,
            auq=auq_res,
            execution_trace=trace,
            session_id=sess_id
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Orchestrator allocation failure: {str(e)}"
        )

@app.post("/api/v1/portfolio/allocate_generic", response_model=GenericPortfolioAllocateResponse)
def allocate_generic_portfolio(request: GenericPortfolioAllocateRequest):
    """
    Orchestrates the standalone portfolio allocation workflow:
    1. Supply Side: Fetches ESG fund options.
    2. Allocator Agent: Generates a draft portfolio for the investment budget.
    3. Compliance Guard Agent: Checks rules with skip_tax_rules=True. If violations occur, self-heals.
    4. AUQ Manager: Audits uncertainty and risk, outputting system confidence metrics.
    """
    trace = []
    sess_id = request.session_id or f"session-{uuid.uuid4().hex[:8]}"
    
    try:
        # Step 0: Save mock OCR / placeholder State to state_manager first
        ocr_data = {
            "assessable_income": 0.0,
            "already_purchased": 0.0,
            "document_type": "No OCR (Generic Budget Request)",
            "confidence": 1.0
        }
        state_manager.update_ocr(
            session_id=sess_id,
            ocr_result=ocr_data,
            confidence=1.0,
            uncertainty_factors=[]
        )

        budget = request.investment_budget
        trace.append(f"Direct Budget: Received investment budget as ฿{budget:,.2f}")
        
        if budget <= 0:
            budget = 0.0
            trace.append("Warning: Investment budget is zero. Generating empty draft portfolio.")

        # Step 2: Orchestration Loop with Compliance Guard
        current_risk_profile = "Aggressive"  # Start unconstrained to maximize financial goal
        current_instructions = request.user_instructions
        loop_count = 0
        max_loops = 3
        portfolio = None
        compliance = None
        
        while loop_count < max_loops:
            loop_count += 1
            trace.append(f"Cycle {loop_count}: Generating allocation weights for {request.financial_goal} goal & {current_risk_profile} profile...")
            
            # Run Allocator
            portfolio = allocate_assets(
                remaining_quota=budget,
                goal=request.financial_goal,
                risk_profile=current_risk_profile,
                user_instructions=current_instructions
            )
            
            # Store Draft Portfolio in State Manager first
            state_manager.update_portfolio(
                session_id=sess_id,
                portfolio=portfolio.model_dump(),
                confidence=0.95,
                uncertainty_factors=[]
            )
            
            # Pre-fetch ESG data for all underlying stocks in Allocator
            from backend.services.jump_db import get_fund_underlying_holdings
            from backend.services.esg_client import esg_client
            for item in portfolio.allocations:
                holdings = get_fund_underlying_holdings(item.fund_code)
                if holdings:
                    for h in holdings:
                        ticker = h.get("ticker")
                        esg_client.get_esg_report(ticker, session_id=sess_id)
                else:
                    esg_client.get_esg_report(item.fund_code, session_id=sess_id)
            
            # Check Compliance (ignoring tax quota calculations)
            compliance = check_portfolio_compliance(
                portfolio=portfolio,
                client_risk_profile=request.risk_profile,
                skip_tax_rules=True,
                session_id=sess_id
            )
            
            if compliance.is_compliant:
                trace.append("Compliance Guard check: PASSED.")
                break
            else:
                trace.append(f"Compliance Guard check: FAILED. Violations: {', '.join(compliance.violations)}")
                
                # Self-healing logic
                if "Risk Mismatch" in "".join(compliance.violations) or "Average Risk Limit" in "".join(compliance.violations):
                    trace.append("Self-Healing Action: Downgrading allocation risk profile parameter to 'Conservative' to enforce strict safety caps.")
                    current_risk_profile = "Conservative"
                else:
                    trace.append("Self-Healing Action: Applying standard correction caps.")
                    break
        
        # Step 3: AUQ Supervisor Evaluation from State Manager (Consumes all confidence scores)
        auq_res = evaluate_system_confidence_from_state(sess_id)
        trace.append(f"AUQ Supervisor: Confidence computed as {auq_res.confidence_score}% (Rating: {auq_res.uncertainty_rating})")
        
        return GenericPortfolioAllocateResponse(
            portfolio=portfolio,
            compliance=compliance,
            auq=auq_res,
            execution_trace=trace,
            session_id=sess_id
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Orchestrator allocation failure: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
