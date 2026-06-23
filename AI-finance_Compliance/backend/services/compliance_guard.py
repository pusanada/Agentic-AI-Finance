from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from backend.services.portfolio_allocator import DraftPortfolio, PortfolioAllocationItem
from backend.services.esg_analyst import get_eligible_esg_funds
from backend.services.state_manager import state_manager

# Mock database for stock CGR scores, JUMP+ status, and SEC enforcement history (past 5 years)
COMPANIES_DB = {
    "PTT": {"name": "PTT Public Company Limited", "cgr_score": 98, "jump_plus": True, "sec_clean": True},
    "CPALL": {"name": "CP ALL Public Company Limited", "cgr_score": 95, "jump_plus": True, "sec_clean": True},
    "ADVANC": {"name": "Advanced Info Service Public Company Limited", "cgr_score": 97, "jump_plus": True, "sec_clean": True},
    "SCC": {"name": "The Siam Cement Public Company Limited", "cgr_score": 96, "jump_plus": True, "sec_clean": True},
    "SCB": {"name": "SCB X Public Company Limited", "cgr_score": 95, "jump_plus": True, "sec_clean": True},
    "KBANK": {"name": "Kasikornbank Public Company Limited", "cgr_score": 96, "jump_plus": True, "sec_clean": True},
    "GULF": {"name": "Gulf Energy Development Public Company Limited", "cgr_score": 88, "jump_plus": True, "sec_clean": True},
    "AOT": {"name": "Airports of Thailand Public Company Limited", "cgr_score": 94, "jump_plus": False, "sec_clean": True},
    "BDMS": {"name": "Bangkok Dusit Medical Services Public Company Limited", "cgr_score": 92, "jump_plus": True, "sec_clean": True},
    "TRUE": {"name": "True Corporation Public Company Limited", "cgr_score": 91, "jump_plus": True, "sec_clean": True},
    "BANPU": {"name": "Banpu Public Company Limited", "cgr_score": 92, "jump_plus": True, "sec_clean": True},
    "STEC": {"name": "Sino-Thai Engineering and Construction PLC", "cgr_score": 91, "jump_plus": False, "sec_clean": True},
    "STARK": {"name": "Stark Corporation Public Company Limited", "cgr_score": 45, "jump_plus": False, "sec_clean": False},
    "MORE": {"name": "More Return Public Company Limited", "cgr_score": 50, "jump_plus": False, "sec_clean": False},
}

# Fund underlying stock holdings mapping
FUND_UNDERLYING_HOLDINGS = {
    "K-THAIESG-A": ["PTT", "CPALL", "ADVANC", "GULF"],
    "SCBTHAIESG": ["PTT", "CPALL", "SCB", "KBANK"],
    "B-THAIESG": ["ADVANC", "SCC", "BDMS"],
    "ASP-THAIESG": ["SCC", "KBANK", "TRUE"],
    "T-THAIESG-D": ["PTT", "ADVANC", "BANPU"]
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
    holding_period_years: int = 5,
    session_id: Optional[str] = None
) -> ComplianceReport:
    """
    Validates a DraftPortfolio against ThaiESG tax rules and investor suitability criteria.
    If session_id is provided, inputs are consumed from the state_manager, and the report
    is saved to the state_manager.
    """
    if session_id:
        state = state_manager.get_or_create_state(session_id)
        
        # Load portfolio from state
        if state.portfolio:
            p_data = state.portfolio.data
            if isinstance(p_data, dict):
                portfolio = DraftPortfolio.model_validate(p_data)
            else:
                portfolio = p_data

        # Load OCR results
        if state.ocr:
            ocr_data = state.ocr.data
            if isinstance(ocr_data, dict):
                assessable_income = ocr_data.get("assessable_income", assessable_income)
                already_purchased = ocr_data.get("already_purchased", already_purchased)
            else:
                assessable_income = getattr(ocr_data, "assessable_income", assessable_income)
                already_purchased = getattr(ocr_data, "already_purchased", already_purchased)

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
    
    total_new_allocated = portfolio.total_allocated if portfolio else 0.0
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
    if portfolio:
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
    if portfolio:
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
    if portfolio:
        for item in portfolio.allocations:
            # Check if mutual fund has underlying stocks mapped
            if item.fund_code in FUND_UNDERLYING_HOLDINGS:
                underlying_stocks = FUND_UNDERLYING_HOLDINGS[item.fund_code]
                for stock_ticker in underlying_stocks:
                    cgr_score = 90
                    jump_plus = True
                    sec_clean = True
                    comp_name = stock_ticker
                    
                    if session_id:
                        # Consume ONLY from state_manager
                        state = state_manager.get_or_create_state(session_id)
                        if stock_ticker.upper() not in state.esg:
                            violations.append(f"Missing ESG Data in State Manager for underlying stock: {stock_ticker}")
                            rule_results["governance_check"] = False
                            continue
                        
                        esg_env = state.esg[stock_ticker.upper()]
                        esg_data = esg_env.data
                        from backend.services.esg_client import ESGAnalysisReport
                        if isinstance(esg_data, dict):
                            report = ESGAnalysisReport.model_validate(esg_data)
                        else:
                            report = esg_data
                        
                        if report.first_stage_checks:
                            cgr_score = report.first_stage_checks.cgr_score
                            jump_plus = report.first_stage_checks.jump_plus
                            sec_clean = report.first_stage_checks.sec_clean
                        else:
                            cgr_score = 90
                            jump_plus = True
                            sec_clean = True
                        comp_name = report.company_name
                    else:
                        # Fallback to local mock COMPANIES_DB for direct unit tests
                        stock_info = COMPANIES_DB.get(stock_ticker)
                        if stock_info:
                            cgr_score = stock_info["cgr_score"]
                            jump_plus = stock_info["jump_plus"]
                            sec_clean = stock_info["sec_clean"]
                            comp_name = stock_info["name"]

                    # Check CGR Score
                    if cgr_score < 90:
                        violations.append(
                            f"Downgraded Stock in Fund: Fund {item.fund_code} contains downgraded stock "
                            f"{stock_ticker} ({comp_name}) with CGR score {cgr_score} (below 90)."
                        )
                        rule_results["governance_check"] = False
                        remedy_actions.append(f"Exclude fund {item.fund_code} from portfolio due to non-compliant stock {stock_ticker}.")
                    
                    # Check JUMP+ Membership
                    if not jump_plus:
                        violations.append(
                            f"Non-JUMP+ Stock in Fund: Fund {item.fund_code} contains stock "
                            f"{stock_ticker} ({comp_name}) which is not a participant in JUMP+."
                        )
                        rule_results["governance_check"] = False
                        remedy_actions.append(f"Exclude fund {item.fund_code} from portfolio due to non-compliant stock {stock_ticker}.")

                    # Check SEC Penalties
                    if not sec_clean:
                        violations.append(
                            f"SEC Enforcement Flag in Fund: Fund {item.fund_code} contains stock "
                            f"{stock_ticker} ({comp_name}) which has active civil/criminal penalties."
                        )
                        rule_results["governance_check"] = False
                        remedy_actions.append(f"Exclude fund {item.fund_code} from portfolio due to non-compliant stock {stock_ticker}.")
            
            # Check direct stock allocations (if any)
            else:
                if item.fund_code not in approved_funds:
                    cgr_score = 90
                    jump_plus = True
                    sec_clean = True
                    comp_name = item.fund_code
                    
                    if session_id:
                        state = state_manager.get_or_create_state(session_id)
                        if item.fund_code.upper() not in state.esg:
                            violations.append(f"Missing ESG Data in State Manager for direct stock: {item.fund_code}")
                            rule_results["governance_check"] = False
                            continue
                        
                        esg_env = state.esg[item.fund_code.upper()]
                        esg_data = esg_env.data
                        from backend.services.esg_client import ESGAnalysisReport
                        if isinstance(esg_data, dict):
                            report = ESGAnalysisReport.model_validate(esg_data)
                        else:
                            report = esg_data
                        
                        if report.first_stage_checks:
                            cgr_score = report.first_stage_checks.cgr_score
                            jump_plus = report.first_stage_checks.jump_plus
                            sec_clean = report.first_stage_checks.sec_clean
                        else:
                            cgr_score = 90
                            jump_plus = True
                            sec_clean = True
                        comp_name = report.company_name
                    else:
                        stock_info = COMPANIES_DB.get(item.fund_code)
                        if stock_info:
                            cgr_score = stock_info["cgr_score"]
                            jump_plus = stock_info["jump_plus"]
                            sec_clean = stock_info["sec_clean"]
                            comp_name = stock_info["name"]

                    if cgr_score < 90:
                        violations.append(
                            f"Downgraded Stock: Stock {item.fund_code} ({comp_name}) "
                            f"has CGR score {cgr_score} (below 90)."
                        )
                        rule_results["governance_check"] = False
                        remedy_actions.append(f"Remove stock {item.fund_code} from portfolio.")
                        
                    if not jump_plus:
                        violations.append(
                            f"Non-JUMP+ Stock: Stock {item.fund_code} ({comp_name}) "
                            f"is not a participant in JUMP+."
                        )
                        rule_results["governance_check"] = False
                        remedy_actions.append(f"Remove stock {item.fund_code} from portfolio.")

                    if not sec_clean:
                        violations.append(
                            f"SEC Enforcement Flag: Stock {item.fund_code} ({comp_name}) "
                            f"has active civil/criminal penalties."
                        )
                        rule_results["governance_check"] = False
                        remedy_actions.append(f"Remove stock {item.fund_code} from portfolio.")

    is_compliant = len(violations) == 0

    report = ComplianceReport(
        is_compliant=is_compliant,
        violations=violations,
        warnings=warnings,
        remedy_actions=remedy_actions,
        rule_results=rule_results
    )

    if session_id:
        # Save output to state_manager
        uncertainty_factors = []
        if not is_compliant:
            uncertainty_factors.extend(violations)
        state_manager.update_compliance(
            session_id=session_id,
            compliance=report.model_dump(),
            confidence=1.0,
            uncertainty_factors=uncertainty_factors
        )

    return report
