from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from backend.services.portfolio_allocator import DraftPortfolio

class AUQReport(BaseModel):
    confidence_score: float = Field(..., description="Overall confidence level (0.0 to 100.0)")
    uncertainty_rating: str = Field(..., description="Uncertainty level: LOW, MEDIUM, or HIGH")
    requires_override: bool = Field(..., description="True if human approval is strictly required")
    recommendation: str = Field(..., description="System recommended action")
    reasons: List[str] = Field(..., description="List of factors driving the uncertainty score")

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
    confidence = 100.0
    reasons = []
    
    if ocr_confidence < 0.99:
        penalty = (1.0 - ocr_confidence) * 40.0
        confidence -= penalty
        reasons.append(f"OCR Data Extraction Confidence is {ocr_confidence * 100:.1f}% (-{penalty:.1f}%)")
    else:
        reasons.append("OCR Data Extraction is verified or highly confident (+0%)")
        
    if not user_profile_complete:
        confidence -= 20.0
        reasons.append("Investor Risk Profile / Goal is incomplete (-20.0%)")
    else:
        reasons.append("Investor Profile (Goal & Risk) is fully specified (+0%)")
        
    if not compliance_passed:
        confidence -= 35.0
        reasons.append("Compliance checks failed! Violations detected in draft portfolio (-35.0%)")
    else:
        reasons.append("Compliance Guard verification passed (+0%)")
        
    if has_custom_instructions:
        confidence -= 5.0
        reasons.append("Custom allocation instructions provided. Manual alignment review recommended (-5.0%)")

    confidence = max(0.0, min(100.0, confidence))
    
    if confidence >= 85.0:
        uncertainty_rating = "LOW"
        requires_override = False
        recommendation = "✅ System is highly confident. The portfolio is safe to execute."
    elif confidence >= 70.0:
        uncertainty_rating = "MEDIUM"
        requires_override = True
        recommendation = "⚠️ Moderate uncertainty. Please review the allocation weights and compliance warnings before executing."
    else:
        uncertainty_rating = "HIGH"
        requires_override = True
        recommendation = "🛑 High uncertainty or compliance violations. Human-in-the-Loop approval is REQUIRED before order dispatch."

    return AUQReport(
        confidence_score=round(confidence, 1),
        uncertainty_rating=uncertainty_rating,
        requires_override=requires_override,
        recommendation=recommendation,
        reasons=reasons
    )

def evaluate_system_confidence_from_state(session_id: str) -> AUQReport:
    """
    AIQ/AUQ Agent evaluator that consumes confidence scores from all agents
    stored in the State Manager and calculates overall uncertainty.
    Triggers Human Review if overall_confidence < 0.75 or uncertainty_score > 0.30.
    """
    from backend.services.state_manager import state_manager
    state = state_manager.get_or_create_state(session_id)
    
    confidence_percentage = round(state.overall_confidence * 100.0, 1)
    uncertainty_score = state.uncertainty_score
    
    # uncertainty rating threshold mapping
    if state.overall_confidence >= 0.85:
        uncertainty_rating = "LOW"
    elif state.overall_confidence >= 0.75:
        uncertainty_rating = "MEDIUM"
    else:
        uncertainty_rating = "HIGH"
        
    # Requires Human Review (Triggered when overall_confidence < 0.75 or uncertainty_score > 0.30)
    requires_override = state.requires_human_review
    
    # Collect reasons/markers
    reasons = []
    if state.ocr:
        reasons.append(f"OCR Agent confidence: {state.ocr.metadata.confidence * 100:.1f}%")
        for f in state.ocr.metadata.uncertainty_factors:
            reasons.append(f"OCR Factor: {f}")
    if state.esg:
        for ticker, env in state.esg.items():
            reasons.append(f"ESG Agent confidence ({ticker}): {env.metadata.confidence * 100:.1f}%")
            for f in env.metadata.uncertainty_factors:
                reasons.append(f"ESG Factor ({ticker}): {f}")
    if state.portfolio:
        reasons.append(f"Portfolio Allocator confidence: {state.portfolio.metadata.confidence * 100:.1f}%")
        for f in state.portfolio.metadata.uncertainty_factors:
            reasons.append(f"Allocator Factor: {f}")
    if state.compliance:
        reasons.append(f"Compliance Guard confidence: {state.compliance.metadata.confidence * 100:.1f}%")
        for f in state.compliance.metadata.uncertainty_factors:
            reasons.append(f"Compliance Factor: {f}")

    if requires_override:
        recommendation = "🛑 High uncertainty or compliance violations. Human-in-the-Loop approval is REQUIRED before order dispatch."
    elif state.overall_confidence >= 0.85:
        recommendation = "✅ System is highly confident. The portfolio is safe to execute."
    else:
        recommendation = "⚠️ Moderate uncertainty. Please review the allocation weights and compliance warnings before executing."

    report = AUQReport(
        confidence_score=confidence_percentage,
        uncertainty_rating=uncertainty_rating,
        requires_override=requires_override,
        recommendation=recommendation,
        reasons=reasons
    )
    
    # Save the AUQ report in the state manager
    state_manager.update_auq(
        session_id=session_id,
        auq_report=report.model_dump(),
        confidence=state.overall_confidence,
        uncertainty_factors=reasons
    )
    
    return report
