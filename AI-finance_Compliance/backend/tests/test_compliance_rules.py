import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.services.compliance_guard import check_portfolio_compliance, ComplianceReport
from backend.services.portfolio_allocator import DraftPortfolio, PortfolioAllocationItem

client = TestClient(app)

def test_compliance_guard_holding_period():
    """Verify that a holding period of less than 5 years fails compliance check."""
    # Create a draft portfolio
    portfolio = DraftPortfolio(
        allocations=[
            PortfolioAllocationItem(
                fund_code="SCBTHAIESG",
                fund_name="SCB Thai ESG Equities Dividend Fund",
                esg_rating="AA",
                risk_level=6,
                asset_class="Equity",
                weight=1.0,
                amount=100000.0,
                units=9881.42
            )
        ],
        total_allocated=100000.0,
        average_risk_level=6.0,
        average_esg_rating="AA",
        financial_goal="Dividend",
        risk_profile="Aggressive"
    )
    
    # Check compliance with 5 years (compliant)
    report_ok = check_portfolio_compliance(portfolio, holding_period_years=5, skip_tax_rules=True)
    assert report_ok.is_compliant is True
    assert len(report_ok.violations) == 0

    # Check compliance with 3 years (non-compliant)
    report_fail = check_portfolio_compliance(portfolio, holding_period_years=3, skip_tax_rules=True)
    assert report_fail.is_compliant is False
    assert any("Holding Period Violation" in v for v in report_fail.violations)

def test_compliance_guard_governance_failure():
    """Verify that a fund containing a downgraded stock (CGR < 90) fails compliance check."""
    # K-THAIESG-A holds GULF (CGR 88)
    portfolio = DraftPortfolio(
        allocations=[
            PortfolioAllocationItem(
                fund_code="K-THAIESG-A",
                fund_name="Kasikorn Thai ESG Active Equity Fund",
                esg_rating="AAA",
                risk_level=6,
                asset_class="Equity",
                weight=1.0,
                amount=100000.0,
                units=8032.12
            )
        ],
        total_allocated=100000.0,
        average_risk_level=6.0,
        average_esg_rating="AAA",
        financial_goal="Growth",
        risk_profile="Aggressive"
    )
    
    report = check_portfolio_compliance(portfolio, holding_period_years=5, skip_tax_rules=True)
    assert report.is_compliant is False
    assert any("Downgraded Stock in Fund" in v for v in report.violations)
    assert any("K-THAIESG-A" in v for v in report.violations)
    assert any("GULF" in v for v in report.violations)

def test_api_self_healing_for_downgraded_stock():
    """Verify that the API self-heals by excluding K-THAIESG-A because it holds downgraded stock GULF."""
    payload = {
        "investment_budget": 100000.0,
        "financial_goal": "Growth",
        "risk_profile": "Aggressive",
        "holding_period_years": 5
    }
    
    response = client.post("/api/v1/portfolio/allocate_generic", json=payload)
    assert response.status_code == 200
    res_data = response.json()
    
    # Portfolio must be compliant
    assert res_data["compliance"]["is_compliant"] is True
    
    # Portfolio should not contain K-THAIESG-A
    portfolio = res_data["portfolio"]
    allocated_funds = [item["fund_code"] for item in portfolio["allocations"]]
    assert "K-THAIESG-A" not in allocated_funds
    
    # Trace should list self-healing action excluding K-THAIESG-A
    trace = res_data["execution_trace"]
    trace_text = "".join(trace)
    assert "Excluding non-compliant fund K-THAIESG-A" in trace_text

def test_api_holding_period_violation():
    """Verify that the API flags a violation if intended holding period is < 5 years and does not self-heal."""
    payload = {
        "investment_budget": 100000.0,
        "financial_goal": "Growth",
        "risk_profile": "Aggressive",
        "holding_period_years": 3
    }
    
    response = client.post("/api/v1/portfolio/allocate_generic", json=payload)
    assert response.status_code == 200
    res_data = response.json()
    
    # Portfolio should NOT be compliant (holding period cannot self-heal by changing assets)
    assert res_data["compliance"]["is_compliant"] is False
    assert any("Holding Period Violation" in v for v in res_data["compliance"]["violations"])
