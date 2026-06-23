import re
from typing import List, Dict, Any
from pydantic import BaseModel, Field

class ESGFund(BaseModel):
    fund_code: str = Field(..., description="Unique ticker code for the fund")
    fund_name: str = Field(..., description="Full name of the mutual fund")
    esg_rating: str = Field(..., description="ESG rating grade, e.g. AAA, AA, A")
    risk_level: int = Field(..., description="Risk level rating from 1 (lowest) to 8 (highest)")
    asset_class: str = Field(..., description="Asset class: Equity, Fixed Income, or Mixed")
    dividend_policy: bool = Field(..., description="True if the fund pays dividends, False for reinvestment")
    expected_return: float = Field(..., description="Annualized expected rate of return (e.g. 0.08 for 8%)")
    nav: float = Field(..., description="Current Net Asset Value per unit in THB")
    description: str = Field(..., description="Brief description of the fund's strategy and composition")

# Seed ThaiESG Fund Database
ESG_FUNDS_DB = [
    ESGFund(
        fund_code="K-THAIESG-A",
        fund_name="Kasikorn Thai ESG Active Equity Fund",
        esg_rating="AAA",
        risk_level=6,
        asset_class="Equity",
        dividend_policy=False,
        expected_return=0.095,
        nav=12.45,
        description="Active equity fund investing in high-quality Thai companies with top-tier ESG ratings (AAA). Focused on long-term capital growth."
    ),
    ESGFund(
        fund_code="SCBTHAIESG",
        fund_name="SCB Thai ESG Equities Dividend Fund",
        esg_rating="AA",
        risk_level=6,
        asset_class="Equity",
        dividend_policy=True,
        expected_return=0.082,
        nav=10.12,
        description="Equity fund focusing on dividend-paying stocks listed on SET that meet sustainability criteria. Good for regular income."
    ),
    ESGFund(
        fund_code="B-THAIESG",
        fund_name="Bualuang Thai ESG Balanced Fund",
        esg_rating="AAA",
        risk_level=5,
        asset_class="Mixed",
        dividend_policy=False,
        expected_return=0.070,
        nav=11.50,
        description="Balanced fund investing in a mix of Thai equities and corporate bonds with strong sustainability policies. Medium risk, moderate growth."
    ),
    ESGFund(
        fund_code="ASP-THAIESG",
        fund_name="Asset Plus Thai ESG Fixed Income Fund",
        esg_rating="AA",
        risk_level=3,
        asset_class="Fixed Income",
        dividend_policy=False,
        expected_return=0.038,
        nav=10.25,
        description="Conservative fixed income fund investing in green bonds, social bonds, and sustainability-linked debt issued by Thai corporations."
    ),
    ESGFund(
        fund_code="T-THAIESG-D",
        fund_name="Thanachart Thai ESG Growth Dividend Fund",
        esg_rating="AAA",
        risk_level=6,
        dividend_policy=True,
        asset_class="Equity",
        expected_return=0.088,
        nav=9.80,
        description="Large-cap equity fund emphasizing high ESG performance and regular dividend distributions. Targets growth with dividend cushion."
    )
]

def get_eligible_esg_funds() -> List[ESGFund]:
    """Returns all eligible ThaiESG funds."""
    return ESG_FUNDS_DB

def query_fund_details(query_text: str) -> List[ESGFund]:
    """
    Screens and filters funds based on a text query.
    Looks for keywords such as 'dividend', 'fixed income', 'growth', 'mixed', 'equity', 'low risk', 'high risk'.
    """
    query_lower = query_text.lower()
    results = []
    
    # Keyword based matching for local search
    for fund in ESG_FUNDS_DB:
        match = False
        
        # Check explicit keywords
        if "dividend" in query_lower or "ปันผล" in query_lower:
            if fund.dividend_policy:
                match = True
        if "growth" in query_lower or "เติบโต" in query_lower:
            if "growth" in fund.description.lower() or fund.asset_class == "Equity":
                match = True
        if "fixed income" in query_lower or "bond" in query_lower or "ตราสารหนี้" in query_lower:
            if fund.asset_class == "Fixed Income":
                match = True
        if "mixed" in query_lower or "balanced" in query_lower or "ผสม" in query_lower:
            if fund.asset_class == "Mixed":
                match = True
        if "low risk" in query_lower or "เสี่ยงต่ำ" in query_lower:
            if fund.risk_level <= 4:
                match = True
        if "high risk" in query_lower or "เสี่ยงสูง" in query_lower:
            if fund.risk_level >= 6:
                match = True
                
        # String match on code or description
        if (query_lower in fund.fund_code.lower() or 
            query_lower in fund.fund_name.lower() or 
            query_lower in fund.description.lower()):
            match = True
            
        if match:
            results.append(fund)
            
    # If no specific matches, return all funds as fallback
    if not results:
        return ESG_FUNDS_DB
        
    return results
