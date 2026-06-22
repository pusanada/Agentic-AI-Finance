from typing import List, Dict, Any, Tuple
from pydantic import BaseModel, Field
from backend.services.portfolio_allocator import DraftPortfolio, PortfolioAllocationItem
from backend.services.esg_analyst import get_eligible_esg_funds

# Mock database for stock CGR scores, JUMP+ status, and SEC enforcement history (past 5 years)
# JUMP+ requirements: CGR Score >= 90, zero SEC civil/criminal penalties in the past 5 years.
COMPANIES_DB = {
    "PTT": {"name": "PTT Public Company Limited", "cgr_score": 98, "jump_plus": True, "sec_clean": True},
    "CPALL": {"name": "CP ALL Public Company Limited", "cgr_score": 95, "jump_plus": True, "sec_clean": True},
    "ADVANC": {"name": "Advanced Info Service Public Company Limited", "cgr_score": 97, "jump_plus": True, "sec_clean": True},
    "SCC": {"name": "The Siam Cement Public Company Limited", "cgr_score": 96, "jump_plus": True, "sec_clean": True},
    "SCB": {"name": "SCB X Public Company Limited", "cgr_score": 95, "jump_plus": True, "sec_clean": True},  # Penalty in 2019 is older than 5 years (relative to 2026)
    "KBANK": {"name": "Kasikornbank Public Company Limited", "cgr_score": 96, "jump_plus": True, "sec_clean": True},
    "GULF": {"name": "Gulf Energy Development Public Company Limited", "cgr_score": 88, "jump_plus": True, "sec_clean": True},  # Downgraded (CGR < 90)
    "AOT": {"name": "Airports of Thailand Public Company Limited", "cgr_score": 94, "jump_plus": False, "sec_clean": True},  # Not in JUMP+
    "BDMS": {"name": "Bangkok Dusit Medical Services Public Company Limited", "cgr_score": 92, "jump_plus": True, "sec_clean": True},
    "TRUE": {"name": "True Corporation Public Company Limited", "cgr_score": 91, "jump_plus": True, "sec_clean": True},
    "BANPU": {"name": "Banpu Public Company Limited", "cgr_score": 92, "jump_plus": True, "sec_clean": True},
    "STEC": {"name": "Sino-Thai Engineering and Construction PLC", "cgr_score": 91, "jump_plus": False, "sec_clean": True},  # Not in JUMP+
    "STARK": {"name": "Stark Corporation Public Company Limited", "cgr_score": 45, "jump_plus": False, "sec_clean": False},  # Criminal penalty in 2023
    "MORE": {"name": "More Return Public Company Limited", "cgr_score": 50, "jump_plus": False, "sec_clean": False},  # Penalty in 2022
}

# Fund underlying stock holdings mapping
FUND_UNDERLYING_HOLDINGS = {
    "K-THAIESG-A": ["PTT", "CPALL", "ADVANC", "GULF"],   # Non-compliant due to GULF (CGR 88 < 90)
    "SCBTHAIESG": ["PTT", "CPALL", "SCB", "KBANK"],       # Compliant
    "B-THAIESG": ["ADVANC", "SCC", "BDMS"],               # Compliant
    "ASP-THAIESG": ["SCC", "KBANK", "TRUE"],              # Compliant
    "T-THAIESG-D": ["PTT", "ADVANC", "BANPU"]             # Compliant
}

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
    skip_tax_rules: bool = False,
    holding_period_years: int = 5
) -> ComplianceReport:
    """
    Validates a DraftPortfolio against ThaiESG tax rules and investor suitability criteria.
    
    1. Quota Limit Rule: Total investment (new + existing) must not exceed 30% of income, capped at 300,000 THB.
    2. Absolute Cap Rule: Total investment must not exceed 300,000 THB.
    3. Suitability Rule: Portfolio risk must align with user risk tolerance.
       - Conservative investors: max 20% in high-risk equity funds (risk level >= 6) and average portfolio risk <= 4.0.
       - Moderate investors: max 50% in high-risk equity funds and average portfolio risk <= 5.5.
    4. Approved List Rule: All funds must belong to the approved ThaiESG fund universe.
    5. Holding Period Rule: The intended holding period must be at least 5 years.
    6. JUMP+ and CGR Governance Rule: Underlying stocks must have CGR >= 90, be JUMP+ participants, and have no SEC penalties.
    """
    violations = []
    warnings = []
    remedy_actions = []
    
    rule_results = {
        "quota_limit_check": True,
        "absolute_cap_check": True,
        "suitability_check": True,
        "asset_approved_check": True,
        "holding_period_check": True,
        "governance_check": True
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

    # Rule 5: Holding Period Check
    if holding_period_years < 5:
        violations.append(
            f"Holding Period Violation: Intended holding period is {holding_period_years} years, "
            f"which is less than the statutory 5-year requirement for ThaiESG tax deductions."
        )
        rule_results["holding_period_check"] = False
        remedy_actions.append("Increase intended holding period to at least 5 years.")

    # Rule 6: JUMP+ & Corporate Governance Screening
    for item in portfolio.allocations:
        # Check if mutual fund has underlying stocks mapped
        if item.fund_code in FUND_UNDERLYING_HOLDINGS:
            underlying_stocks = FUND_UNDERLYING_HOLDINGS[item.fund_code]
            for stock_ticker in underlying_stocks:
                stock_info = COMPANIES_DB.get(stock_ticker)
                if stock_info:
                    # Check CGR Score
                    if stock_info["cgr_score"] < 90:
                        violations.append(
                            f"Downgraded Stock in Fund: Fund {item.fund_code} contains downgraded stock "
                            f"{stock_ticker} ({stock_info['name']}) with CGR score {stock_info['cgr_score']} (below 90)."
                        )
                        rule_results["governance_check"] = False
                        remedy_actions.append(f"Exclude fund {item.fund_code} from portfolio due to non-compliant stock {stock_ticker}.")
                    
                    # Check JUMP+ Membership
                    if not stock_info["jump_plus"]:
                        violations.append(
                            f"Non-JUMP+ Stock in Fund: Fund {item.fund_code} contains stock "
                            f"{stock_ticker} ({stock_info['name']}) which is not a participant in JUMP+."
                        )
                        rule_results["governance_check"] = False
                        remedy_actions.append(f"Exclude fund {item.fund_code} from portfolio due to non-compliant stock {stock_ticker}.")

                    # Check SEC Penalties (last 5 years)
                    if not stock_info["sec_clean"]:
                        violations.append(
                            f"SEC Enforcement Flag in Fund: Fund {item.fund_code} contains stock "
                            f"{stock_ticker} ({stock_info['name']}) which has active civil/criminal penalties."
                        )
                        rule_results["governance_check"] = False
                        remedy_actions.append(f"Exclude fund {item.fund_code} from portfolio due to non-compliant stock {stock_ticker}.")
        
        # Check direct stock allocations (if any)
        elif item.fund_code in COMPANIES_DB:
            stock_info = COMPANIES_DB[item.fund_code]
            if stock_info["cgr_score"] < 90:
                violations.append(
                    f"Downgraded Stock: Stock {item.fund_code} ({stock_info['name']}) "
                    f"has CGR score {stock_info['cgr_score']} (below 90)."
                )
                rule_results["governance_check"] = False
                remedy_actions.append(f"Remove stock {item.fund_code} from portfolio.")
                
            if not stock_info["jump_plus"]:
                violations.append(
                    f"Non-JUMP+ Stock: Stock {item.fund_code} ({stock_info['name']}) "
                    f"is not a participant in JUMP+."
                )
                rule_results["governance_check"] = False
                remedy_actions.append(f"Remove stock {item.fund_code} from portfolio.")

            if not stock_info["sec_clean"]:
                violations.append(
                    f"SEC Enforcement Flag: Stock {item.fund_code} ({stock_info['name']}) "
                    f"has active civil/criminal penalties."
                )
                rule_results["governance_check"] = False
                remedy_actions.append(f"Remove stock {item.fund_code} from portfolio.")

    is_compliant = len(violations) == 0

    return ComplianceReport(
        is_compliant=is_compliant,
        violations=violations,
        warnings=warnings,
        remedy_actions=remedy_actions,
        rule_results=rule_results
    )
