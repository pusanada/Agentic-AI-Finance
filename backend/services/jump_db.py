from typing import List, Dict, Any
from pydantic import BaseModel, Field

class JUMPCompany(BaseModel):
    ticker: str = Field(..., description="Stock ticker symbol")
    company_name: str = Field(..., description="Full name of the company")
    cgr_score: int = Field(..., description="Corporate Governance Rating score (0-100)")
    sec_penalties: List[str] = Field(default_factory=list, description="Recent SEC civil or criminal penalties")
    cvup_emission_plan: str = Field(..., description="Official Corporate Value Up Plan statement")
    opp_day_statement: str = Field(..., description="Opportunity Day executive transcript snippet")
    has_data_conflict: bool = Field(..., description="True if there is an epistemic mismatch/conflict between CVUP and executive statements")
    conflict_details: str = Field(default="", description="Explainable details of the conflict/ambiguity")

# Seed JUMP+ Company database
JUMP_COMPANIES_DB: Dict[str, JUMPCompany] = {
    "PTT": JUMPCompany(
        ticker="PTT",
        company_name="PTT Public Company Limited",
        cgr_score=95,
        sec_penalties=[],
        cvup_emission_plan="Official CVUP: Commitment to reduce carbon emissions by 50% by 2030 and achieve Net Zero by 2050.",
        opp_day_statement="Opportunity Day Transcript: 'Our carbon neutrality target by 2030 is highly dependent on external government subsidies and carbon tax policies; without them, we may have to push the timeline to 2040.'",
        has_data_conflict=True,
        conflict_details="The executive statement from Opportunity Day casts severe doubt on the feasibility of the official CVUP target, introducing high greenwashing risk and epistemic uncertainty."
    ),
    "CPALL": JUMPCompany(
        ticker="CPALL",
        company_name="CP ALL Public Company Limited",
        cgr_score=92,
        sec_penalties=[],
        cvup_emission_plan="Official CVUP: Enforce a sustainable supply chain with 100% ESG-audited tier-1 suppliers by 2569.",
        opp_day_statement="Opportunity Day Transcript: 'We are fully on track to achieve our target. As of last quarter, 98% of our tier-1 suppliers have completed comprehensive ESG audits.'",
        has_data_conflict=False,
        conflict_details=""
    ),
    "EA": JUMPCompany(
        ticker="EA",
        company_name="Energy Absolute Public Company Limited",
        cgr_score=88,
        sec_penalties=["SEC civil sanction and fine against top executives for misrepresentation of financial transaction status in 2024."],
        cvup_emission_plan="Official CVUP: Realignment of corporate governance structures to meet international transparency standards.",
        opp_day_statement="Opportunity Day Transcript: 'We are currently investigating governance issues internally, but the impact on our ongoing green energy expansion projects is still uncertain and subject to change.'",
        has_data_conflict=True,
        conflict_details="The company is penalized by the SEC (CGR is also below the 90 minimum threshold), and the executive's statements reveal high ambiguity regarding project impacts and internal governance."
    ),
    "SCC": JUMPCompany(
        ticker="SCC",
        company_name="Siam Cement Public Company Limited",
        cgr_score=94,
        sec_penalties=[],
        cvup_emission_plan="Official CVUP: Accelerate transition to low-carbon cement technologies to reduce Scope 1 emissions by 30% by 2030.",
        opp_day_statement="Opportunity Day Transcript: 'Economic slowdown may temporarily reduce our capital expenditure on green cement tech in 2569, but our long-term targets remain firm.'",
        has_data_conflict=False,
        conflict_details=""
    ),
    "ADVANC": JUMPCompany(
        ticker="ADVANC",
        company_name="Advanced Info Service Public Company Limited",
        cgr_score=96,
        sec_penalties=[],
        cvup_emission_plan="Official CVUP: 100% renewable energy utilization in all core data centers and cellular network towers by 2027.",
        opp_day_statement="Opportunity Day Transcript: 'We are pacing ahead of schedule. Core data centers have hit 85% green power usage, and cellular base stations are rapidly transitioning.'",
        has_data_conflict=False,
        conflict_details=""
    )
}

# Underlying stock weights mapping for ThaiESG funds
FUND_HOLDINGS: Dict[str, List[Dict[str, Any]]] = {
    "K-THAIESG-A": [
        {"ticker": "PTT", "weight": 0.40},
        {"ticker": "SCC", "weight": 0.35},
        {"ticker": "CPALL", "weight": 0.25}
    ],
    "SCBTHAIESG": [
        {"ticker": "PTT", "weight": 0.30},
        {"ticker": "EA", "weight": 0.40},     # Note: SCBTHAIESG holds EA (CGR < 90, SEC penalty, high conflict)
        {"ticker": "CPALL", "weight": 0.30}
    ],
    "B-THAIESG": [
        {"ticker": "SCC", "weight": 0.50},
        {"ticker": "CPALL", "weight": 0.50}
    ],
    "ASP-THAIESG": [
        # Debt securities / green bonds of these companies
        {"ticker": "PTT", "weight": 0.60},
        {"ticker": "SCC", "weight": 0.40}
    ],
    "T-THAIESG-D": [
        {"ticker": "CPALL", "weight": 0.50},
        {"ticker": "ADVANC", "weight": 0.50}
    ]
}

def get_company_details(ticker: str) -> JUMPCompany:
    """Returns JUMP+ company metadata for the given ticker, or None if not found."""
    return JUMP_COMPANIES_DB.get(ticker)

def get_fund_underlying_holdings(fund_code: str) -> List[Dict[str, Any]]:
    """Returns the underlying stock holdings of a given ThaiESG fund."""
    return FUND_HOLDINGS.get(fund_code, [])
