from typing import List, Dict, Any, Tuple
from pydantic import BaseModel, Field
from backend.services.portfolio_allocator import DraftPortfolio, PortfolioAllocationItem
from backend.services.esg_analyst import get_eligible_esg_funds

class ComplianceReport(BaseModel):
    is_compliant: bool
    violations: List[str]
    warnings: List[str]
    remedy_actions: List[str]
    rule_results: Dict[str, bool]

def check_portfolio_compliance(
    portfolio: DraftPortfolio,
    assessable_income: float = 0.0,
    already_purchased: float = 0.0,
    max_quota: float = 0.0,
    client_risk_profile: str = None,
    skip_tax_rules: bool = False
) -> ComplianceReport:
    """
    Validates a DraftPortfolio against ThaiESG tax rules and investor suitability criteria.
    
    1. Quota Limit Rule: Total investment (new + existing) must not exceed 30% of income, capped at 300,000 THB.
    2. Absolute Cap Rule: Total investment must not exceed 300,000 THB.
    3. Suitability Rule: Portfolio risk must align with user risk tolerance.
       - Conservative investors must not have > 20% in high-risk equity funds (risk level >= 6) and average portfolio risk <= 4.0.
       - Moderate investors must not have > 50% in high-risk equity funds and average portfolio risk <= 5.5.
    4. Approved List Rule: All funds must belong to the approved ThaiESG fund universe.
    """
    violations = []
    warnings = []
    remedy_actions = []
    
    rule_results = {
        "quota_limit_check": True,
        "absolute_cap_check": True,
        "suitability_check": True,
        "asset_approved_check": True
    }
    
    total_new_allocated = portfolio.total_allocated
    total_annual_investment = total_new_allocated + already_purchased
    
    # Rule 1 & 2: Quota and Cap checks (only check if skip_tax_rules is False)
    if not skip_tax_rules:
        if total_annual_investment > max_quota:
            overshoot = total_annual_investment - max_quota
            violations.append(
                f"Quota Overshoot: Total annual investment (฿{total_annual_investment:,.2f}) "
                f"exceeds your maximum tax limit of ฿{max_quota:,.2f} by ฿{overshoot:,.2f}."
            )
            rule_results["quota_limit_check"] = False
            remedy_actions.append(f"Reduce total allocation by ฿{overshoot:,.2f}.")

        if total_annual_investment > 300000.0:
            overshoot_cap = total_annual_investment - 300000.0
            violations.append(
                f"Absolute Cap Violation: Total annual investment (฿{total_annual_investment:,.2f}) "
                f"exceeds the statutory ThaiESG limit of ฿300,000.00 by ฿{overshoot_cap:,.2f}."
            )
            rule_results["absolute_cap_check"] = False
            remedy_actions.append(f"Cap total purchase to stay under the ฿300,000 limit.")

    # Rule 3: Risk Suitability check
    risk_profile = (client_risk_profile or portfolio.risk_profile).lower()

    high_risk_assets_weight = sum(
        item.weight for item in portfolio.allocations if item.risk_level >= 6
    )
    
    if "conservative" in risk_profile:
        if high_risk_assets_weight > 0.201:
            violations.append(
                f"Risk Mismatch: Conservative investor profile has {high_risk_assets_weight * 100:.1f}% "
                f"allocated to high-risk assets, exceeding the 20% limit."
            )
            rule_results["suitability_check"] = False
            remedy_actions.append("Reduce high-risk funds (risk level 6) weight below 20% and shift to Fixed Income.")
        if portfolio.average_risk_level > 4.0:
            violations.append(
                f"Average Risk Limit Violation: Average risk level is {portfolio.average_risk_level:.1f}, "
                f"exceeding the maximum allowed level of 4.0 for Conservative investors."
            )
            rule_results["suitability_check"] = False
            remedy_actions.append("Shift allocation to lower risk funds (e.g., Fixed Income).")
            
    elif "moderate" in risk_profile:
        if high_risk_assets_weight > 0.501:
            warnings.append(
                f"High-Risk Warning: Moderate investor profile has {high_risk_assets_weight * 100:.1f}% "
                f"allocated to high-risk assets, near or exceeding the recommended 50% threshold."
            )
            remedy_actions.append("Consider rebalancing some high-risk equities to Mixed/Balanced funds.")
        if portfolio.average_risk_level > 5.5:
            violations.append(
                f"Average Risk Limit Violation: Average risk level is {portfolio.average_risk_level:.1f}, "
                f"exceeding the maximum allowed level of 5.5 for Moderate investors."
            )
            rule_results["suitability_check"] = False
            remedy_actions.append("Reduce equity allocation and increase Mixed/Balanced funds.")

    # Rule 4: Approved List verification
    approved_funds = {f.fund_code for f in get_eligible_esg_funds()}
    for item in portfolio.allocations:
        if item.fund_code not in approved_funds:
            violations.append(
                f"Non-Approved Asset: Fund code {item.fund_code} is not a certified ThaiESG fund."
            )
            rule_results["asset_approved_check"] = False
            remedy_actions.append(f"Remove {item.fund_code} from the portfolio.")

    is_compliant = len(violations) == 0

    return ComplianceReport(
        is_compliant=is_compliant,
        violations=violations,
        warnings=warnings,
        remedy_actions=remedy_actions,
        rule_results=rule_results
    )
