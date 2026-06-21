from typing import List, Dict, Any
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
    Computes system confidence and flags potential uncertainty risks.
    
    Factors considered:
    - OCR Confidence (Aleatoric uncertainty from image scanning)
    - Profile Completeness (Epistemic uncertainty about user goals)
    - Compliance Status (System risk)
    - Custom User Instructions (Alignment uncertainty)
    """
    confidence = 100.0
    reasons = []
    
    # 1. OCR Confidence impact
    if ocr_confidence < 0.99:
        penalty = (1.0 - ocr_confidence) * 40.0
        confidence -= penalty
        reasons.append(f"OCR Data Extraction Confidence is {ocr_confidence * 100:.1f}% (-{penalty:.1f}%)")
    else:
        reasons.append("OCR Data Extraction is verified or highly confident (+0%)")
        
    # 2. User profile completeness impact
    if not user_profile_complete:
        confidence -= 20.0
        reasons.append("Investor Risk Profile / Goal is incomplete (-20.0%)")
    else:
        reasons.append("Investor Profile (Goal & Risk) is fully specified (+0%)")
        
    # 3. Compliance checks impact
    if not compliance_passed:
        confidence -= 35.0
        reasons.append("Compliance checks failed! Violations detected in draft portfolio (-35.0%)")
    else:
        reasons.append("Compliance Guard verification passed (+0%)")
        
    # 4. Custom instruction alignment check
    if has_custom_instructions:
        # Vague constraints increase uncertainty slightly
        confidence -= 5.0
        reasons.append("Custom allocation instructions provided. Manual alignment review recommended (-5.0%)")

    # Limit bounds
    confidence = max(0.0, min(100.0, confidence))
    
    # Determine ratings and thresholds
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
