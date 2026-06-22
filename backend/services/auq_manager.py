from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from backend.services.portfolio_allocator import DraftPortfolio

class AUQReport(BaseModel):
    confidence_score: float = Field(..., description="Overall confidence level (0.0 to 100.0)")
    uncertainty_rating: str = Field(..., description="Uncertainty level: LOW, MEDIUM, or HIGH")
    requires_override: bool = Field(..., description="True if human approval is strictly required")
    recommendation: str = Field(..., description="System recommended action")
    reasons: List[str] = Field(..., description="List of factors driving the uncertainty score")
    
    # Explainable AI (XAI) and Supervisor specific fields
    status: str = Field("APPROVED", description="Status: APPROVED, TEMPORARY_PAUSE, or ESCALATED")
    epistemic_uncertainty_score: float = Field(0.0, description="Epistemic uncertainty penalty")
    aleatoric_uncertainty_score: float = Field(0.0, description="Aleatoric uncertainty penalty")
    xai_justifications: List[str] = Field(default_factory=list, description="Explainable AI justifications")
    structured_reasoning_trace: List[str] = Field(default_factory=list, description="Reasoning steps trace")

def _compute_auq_report(
    ocr_confidence: float,
    user_profile_complete: bool,
    compliance_passed: bool,
    portfolio: Optional[DraftPortfolio],
    has_custom_instructions: bool = False
) -> AUQReport:
    confidence = 100.0
    reasons = []
    xai_justifications = []
    structured_reasoning_trace = []
    aleatoric_penalty = 0.0
    epistemic_penalty = 0.0
    
    structured_reasoning_trace.append("Step 1: Initializing AUQ verification agent.")
    structured_reasoning_trace.append(f"Step 2: Checking OCR quality parameters (OCR confidence: {ocr_confidence}).")
    
    # 1. OCR Confidence check (Aleatoric Uncertainty)
    if ocr_confidence < 0.99:
        penalty = (1.0 - ocr_confidence) * 40.0
        aleatoric_penalty += penalty
        reasons.append(f"OCR Data Extraction Confidence is {ocr_confidence * 100:.1f}% (-{penalty:.1f}%)")
        structured_reasoning_trace.append(f"Warning: Low OCR quality detected (confidence: {ocr_confidence}). Adding aleatoric uncertainty penalty of -{penalty:.1f}%.")
    else:
        reasons.append("OCR Data Extraction is verified or highly confident (+0%)")
        structured_reasoning_trace.append("OCR Quality Check: PASSED. No penalty applied.")
        
    # 2. User profile check (Epistemic Uncertainty)
    if not user_profile_complete:
        epistemic_penalty += 20.0
        reasons.append("Investor Risk Profile / Goal is incomplete (-20.0%)")
        structured_reasoning_trace.append("Epistemic Uncertainty: KYC investor profile is incomplete. Adding penalty of -20.0%.")
    else:
        reasons.append("Investor Profile (Goal & Risk) is fully specified (+0%)")
        
    # 3. Compliance check (Epistemic Uncertainty)
    if not compliance_passed:
        epistemic_penalty += 35.0
        reasons.append("Compliance checks failed! Violations detected in draft portfolio (-35.0%)")
        structured_reasoning_trace.append("System Risk: Compliance Guard flag mismatch. Adding penalty of -35.0%.")
    else:
        reasons.append("Compliance Guard verification passed (+0%)")
        
    # 4. Custom instructions (Epistemic Uncertainty)
    if has_custom_instructions:
        epistemic_penalty += 5.0
        reasons.append("Custom allocation instructions provided. Manual alignment review recommended (-5.0%)")
        structured_reasoning_trace.append("Alignment Uncertainty: Custom allocation instructions detected. Adding penalty of -5.0%.")

    # 5. JUMP+ Governance & Greenwashing Conflicts
    if portfolio:
        try:
            from backend.services.jump_db import get_fund_underlying_holdings, get_company_details
            for item in portfolio.allocations:
                holdings = get_fund_underlying_holdings(item.fund_code)
                for h in holdings:
                    ticker = h.get("ticker")
                    co = get_company_details(ticker)
                    if co:
                        # Check data conflict (greenwashing)
                        if co.has_data_conflict:
                            epistemic_penalty += 15.0
                            reasons.append(f"Greenwashing/Conflict in Fund: Fund {item.fund_code} contains stock {co.ticker} ({co.company_name}) with conflicting disclosures. (-15.0%)")
                            xai_justifications.append(f"GREENWASHING Conflict in {co.company_name} ({co.ticker}): {co.conflict_details}")
                            structured_reasoning_trace.append(f"Temporary Pause: Found data conflict between CVUP and executive statements for underlying stock {co.ticker} in fund {item.fund_code}. Escalate to HITL for review.")
                        
                        # Check CGR Score
                        if co.cgr_score < 90:
                            epistemic_penalty += 15.0
                            reasons.append(f"Downgraded Stock in Fund: Fund {item.fund_code} contains downgraded stock {co.ticker} ({co.company_name}) with CGR score {co.cgr_score} (below 90). (-15.0%)")
                            xai_justifications.append(f"CGR Score Violation in {co.company_name} ({co.ticker}): CGR score is {co.cgr_score} < 90.")
                            structured_reasoning_trace.append(f"Temporary Pause: Underlying stock {co.ticker} has non-compliant CGR score {co.cgr_score} < 90.")
                            
                        # Check SEC penalties
                        if co.sec_penalties:
                            epistemic_penalty += 15.0
                            reasons.append(f"SEC Enforcement Flag in Fund: Fund {item.fund_code} contains stock {co.ticker} ({co.company_name}) which has active civil/criminal penalties. (-15.0%)")
                            xai_justifications.append(f"SEC Penalties against {co.company_name} ({co.ticker}): {', '.join(co.sec_penalties)}")
                            structured_reasoning_trace.append(f"Temporary Pause: Underlying stock {co.ticker} has active SEC civil or criminal penalties.")
        except Exception as e:
            structured_reasoning_trace.append(f"Error checking underlying stocks: {str(e)}")

    confidence_score = round(max(0.0, min(100.0, 100.0 - aleatoric_penalty - epistemic_penalty)), 1)
    
    if confidence_score >= 85.0:
        uncertainty_rating = "LOW"
        requires_override = False
        status = "APPROVED"
        recommendation = "✅ System is highly confident. The portfolio is safe to execute."
    else:
        requires_override = True
        if confidence_score >= 70.0:
            uncertainty_rating = "MEDIUM"
            status = "TEMPORARY_PAUSE"
            recommendation = "⚠️ Moderate uncertainty. Please review the allocation weights and compliance warnings before executing."
        else:
            uncertainty_rating = "HIGH"
            status = "ESCALATED"
            recommendation = "🛑 High uncertainty or compliance violations. Human-in-the-Loop approval is REQUIRED before order dispatch."

    return AUQReport(
        confidence_score=confidence_score,
        uncertainty_rating=uncertainty_rating,
        requires_override=requires_override,
        recommendation=recommendation,
        reasons=reasons,
        status=status,
        epistemic_uncertainty_score=round(epistemic_penalty, 1),
        aleatoric_uncertainty_score=round(aleatoric_penalty, 1),
        xai_justifications=xai_justifications,
        structured_reasoning_trace=structured_reasoning_trace
    )

def evaluate_system_confidence(
    ocr_confidence: float,
    user_profile_complete: bool,
    compliance_passed: bool,
    portfolio: DraftPortfolio,
    has_custom_instructions: bool = False
) -> AUQReport:
    """
    Classic/legacy evaluator for backward compatibility.
    """
    return _compute_auq_report(
        ocr_confidence=ocr_confidence,
        user_profile_complete=user_profile_complete,
        compliance_passed=compliance_passed,
        portfolio=portfolio,
        has_custom_instructions=has_custom_instructions
    )

def evaluate_system_confidence_from_state(session_id: str) -> AUQReport:
    """
    AIQ/AUQ Agent evaluator that consumes confidence scores from all agents
    stored in the State Manager and calculates overall uncertainty.
    """
    from backend.services.state_manager import state_manager
    state = state_manager.get_or_create_state(session_id)
    
    ocr_confidence = 1.0
    if state.ocr:
        ocr_data = state.ocr.data
        if isinstance(ocr_data, dict):
            ocr_confidence = ocr_data.get("confidence", 1.0)
        else:
            ocr_confidence = getattr(ocr_data, "confidence", 1.0)
            
    user_profile_complete = True
    portfolio = None
    if state.portfolio:
        p_data = state.portfolio.data
        if isinstance(p_data, dict):
            portfolio = DraftPortfolio.model_validate(p_data)
        else:
            portfolio = p_data
        user_profile_complete = bool(portfolio.financial_goal and portfolio.risk_profile)
        
    compliance_passed = True
    if state.compliance:
        c_data = state.compliance.data
        if isinstance(c_data, dict):
            compliance_passed = c_data.get("is_compliant", True)
        else:
            compliance_passed = c_data.is_compliant
            
    # Determine custom instructions
    has_custom_instructions = False
    if portfolio and portfolio.allocations:
        # Check if any custom instructions are stored or requested
        pass
        
    report = _compute_auq_report(
        ocr_confidence=ocr_confidence,
        user_profile_complete=user_profile_complete,
        compliance_passed=compliance_passed,
        portfolio=portfolio,
        has_custom_instructions=has_custom_instructions
    )
    
    # Save the AUQ report in the state manager
    state_manager.update_auq(
        session_id=session_id,
        auq_report=report.model_dump(),
        confidence=report.confidence_score / 100.0,
        uncertainty_factors=report.reasons
    )
    
    return report
