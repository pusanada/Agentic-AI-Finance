import logging
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from backend.services.esg_analyst import get_eligible_esg_funds, ESGFund

logger = logging.getLogger(__name__)

class PortfolioAllocationItem(BaseModel):
    fund_code: str
    fund_name: str
    esg_rating: str
    risk_level: int
    asset_class: str
    weight: float = Field(..., description="Allocation weight (0.0 to 1.0)")
    amount: float = Field(..., description="Amount allocated in THB")
    units: float = Field(..., description="Estimated number of units based on NAV")

class DraftPortfolio(BaseModel):
    allocations: List[PortfolioAllocationItem]
    total_allocated: float
    average_risk_level: float
    average_esg_rating: str
    financial_goal: str
    risk_profile: str

def allocate_assets(
    remaining_quota: float,
    goal: str,
    risk_profile: str,
    user_instructions: str = ""
) -> DraftPortfolio:
    """
    Allocates the remaining investment quota across certified ESG funds.
    
    1. Determines base asset class weights based on financial goals:
       - Growth: Equity 70%, Mixed 20%, Fixed Income 10%
       - Dividend: Equity (Dividend-focused) 60%, Mixed 20%, Fixed Income 20%
       - Balanced: Equity 40%, Mixed 40%, Fixed Income 20%
       
    2. Modifies allocations based on risk constraints (Risk Mitigation):
       - Conservative: Capped total High Risk (level >= 6) at 20%. Excess shifted to Fixed Income.
       - Moderate: Capped total High Risk (level >= 6) at 50%.
       - Aggressive: No cap.
       
    3. Handles custom text instructions:
       - Avoids/excludes specified fund codes if requested (e.g. "avoid K-THAIESG-A").
    """
    funds = get_eligible_esg_funds()
    
    # 1. Parse user instructions for excluded funds
    excluded_funds = []
    instr_lower = user_instructions.lower()
    for fund in funds:
        code_lower = fund.fund_code.lower()
        if f"avoid {code_lower}" in instr_lower or f"exclude {code_lower}" in instr_lower or f"no {code_lower}" in instr_lower or f"ไม่เอา {code_lower}" in instr_lower:
            excluded_funds.append(fund.fund_code)
            
    # Filter available funds
    available_funds = [f for f in funds if f.fund_code not in excluded_funds]
    if not available_funds:
        # Fallback if everything is excluded
        available_funds = funds
        
    # 2. Determine targeted assets by goal
    equity_funds = [f for f in available_funds if f.asset_class == "Equity"]
    mixed_funds = [f for f in available_funds if f.asset_class == "Mixed"]
    fi_funds = [f for f in available_funds if f.asset_class == "Fixed Income"]
    
    # Fallback to available funds if asset class categories are empty
    if not equity_funds: equity_funds = available_funds
    if not mixed_funds: mixed_funds = available_funds
    if not fi_funds: fi_funds = available_funds

    # Define base asset class targets
    target_equity_w = 0.0
    target_mixed_w = 0.0
    target_fi_w = 0.0
    
    goal_lower = goal.lower()
    if "growth" in goal_lower or "เติบโต" in goal_lower:
        target_equity_w = 0.70
        target_mixed_w = 0.20
        target_fi_w = 0.10
    elif "dividend" in goal_lower or "ปันผล" in goal_lower:
        target_equity_w = 0.60
        target_mixed_w = 0.20
        target_fi_w = 0.20
    else: # Balanced / General
        target_equity_w = 0.40
        target_mixed_w = 0.40
        target_fi_w = 0.20

    # 3. Apply risk profile caps
    risk_lower = risk_profile.lower()
    high_risk_cap = 1.0  # Aggressive default
    
    if "conservative" in risk_lower or "ต่ำ" in risk_lower:
        high_risk_cap = 0.20
    elif "moderate" in risk_lower or "balanced" in risk_lower or "กลาง" in risk_lower:
        high_risk_cap = 0.50

    # Find which target asset classes contain high-risk funds (risk_level >= 6)
    # The high risk funds are usually Equity.
    # If the target equity weight exceeds the risk profile cap, we transfer the excess weight to Fixed Income.
    actual_equity_w = target_equity_w
    actual_mixed_w = target_mixed_w
    actual_fi_w = target_fi_w
    
    # Assume Equity funds are high risk (>=6) and Mixed is medium risk (5) and FI is low risk (3)
    # Total high risk exposure: actual_equity_w (since K-THAIESG-A, SCBTHAIESG, T-THAIESG-D are risk level 6)
    if actual_equity_w > high_risk_cap:
        excess = actual_equity_w - high_risk_cap
        actual_equity_w = high_risk_cap
        actual_fi_w += excess  # Shift to fixed income

    # 4. Distribute weights among specific funds in each category
    # Equity distribution:
    # If Dividend goal, prefer dividend equity funds (SCBTHAIESG, T-THAIESG-D).
    # If Growth goal, prefer growth equity funds (K-THAIESG-A, T-THAIESG-D).
    selected_equity_funds = []
    if "dividend" in goal_lower:
        selected_equity_funds = [f for f in equity_funds if f.dividend_policy]
    else:
        selected_equity_funds = [f for f in equity_funds if not f.dividend_policy]
        
    if not selected_equity_funds:
        selected_equity_funds = equity_funds
        
    # Mixed distribution:
    selected_mixed_funds = mixed_funds
    
    # Fixed Income distribution:
    selected_fi_funds = fi_funds

    # Allocate final weights per fund
    weights: Dict[str, float] = {}
    
    # Distribute equity weight
    for f in selected_equity_funds:
        weights[f.fund_code] = weights.get(f.fund_code, 0.0) + (actual_equity_w / len(selected_equity_funds))
        
    # Distribute mixed weight
    for f in selected_mixed_funds:
        weights[f.fund_code] = weights.get(f.fund_code, 0.0) + (actual_mixed_w / len(selected_mixed_funds))
        
    # Distribute Fixed Income weight
    for f in selected_fi_funds:
        weights[f.fund_code] = weights.get(f.fund_code, 0.0) + (actual_fi_w / len(selected_fi_funds))

    # Normalize weights just in case of rounding errors
    total_w = sum(weights.values())
    if total_w > 0:
        weights = {k: v / total_w for k, v in weights.items()}

    # Create portfolio items
    allocations: List[PortfolioAllocationItem] = []
    weighted_risk = 0.0
    esg_score_sum = 0.0
    
    # ESG score mapping: AAA = 3, AA = 2, A = 1
    esg_map = {"AAA": 3.0, "AA": 2.0, "A": 1.0}
    
    # Fetch all details for allocated funds
    for fund in funds:
        w = weights.get(fund.fund_code, 0.0)
        if w > 0.001:
            allocated_amt = remaining_quota * w
            units_count = allocated_amt / fund.nav
            
            item = PortfolioAllocationItem(
                fund_code=fund.fund_code,
                fund_name=fund.fund_name,
                esg_rating=fund.esg_rating,
                risk_level=fund.risk_level,
                asset_class=fund.asset_class,
                weight=round(w, 4),
                amount=round(allocated_amt, 2),
                units=round(units_count, 4)
            )
            allocations.append(item)
            weighted_risk += fund.risk_level * w
            esg_score_sum += esg_map.get(fund.esg_rating, 2.0) * w

    # Calculate average ESG rating string
    avg_esg_val = esg_score_sum / sum(weights.values()) if weights else 2.0
    if avg_esg_val >= 2.5:
        avg_esg = "AAA"
    elif avg_esg_val >= 1.5:
        avg_esg = "AA"
    else:
        avg_esg = "A"

    return DraftPortfolio(
        allocations=allocations,
        total_allocated=round(remaining_quota, 2),
        average_risk_level=round(weighted_risk, 2),
        average_esg_rating=avg_esg,
        financial_goal=goal,
        risk_profile=risk_profile
    )
