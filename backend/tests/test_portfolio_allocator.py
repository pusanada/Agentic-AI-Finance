import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.services.esg_analyst import get_eligible_esg_funds, query_fund_details
from backend.services.portfolio_allocator import allocate_assets, DraftPortfolio
from backend.services.compliance_guard import check_portfolio_compliance
from backend.services.auq_manager import evaluate_system_confidence

client = TestClient(app)

def test_esg_screening():
    """Verify that ESG funds are correctly registered and queryable."""
    funds = get_eligible_esg_funds()
    assert len(funds) >= 5
    
    # Test keyword matching for dividend
    dividend_funds = query_fund_details("dividend")
    assert len(dividend_funds) > 0
    assert any(f.dividend_policy for f in dividend_funds)

    # Test keyword matching for fixed income
    fi_funds = query_fund_details("ตราสารหนี้")
    assert len(fi_funds) > 0
    assert any(f.asset_class == "Fixed Income" for f in fi_funds)


def test_portfolio_allocation_by_goal():
    """Verify asset allocation weights match risk guidelines and sum to 1.0."""
    # Aggressive Growth
    growth_portfolio = allocate_assets(
        remaining_quota=100000.0,
        goal="Growth",
        risk_profile="Aggressive"
    )
    assert growth_portfolio.total_allocated == 100000.0
    assert abs(sum(item.weight for item in growth_portfolio.allocations) - 1.0) < 0.001
    
    # High risk assets should not be capped for Aggressive
    high_risk_weight = sum(item.weight for item in growth_portfolio.allocations if item.risk_level >= 6)
    assert high_risk_weight > 0.50

    # Conservative Growth (should be capped at 20% high risk)
    conservative_portfolio = allocate_assets(
        remaining_quota=100000.0,
        goal="Growth",
        risk_profile="Conservative"
    )
    high_risk_weight_cons = sum(item.weight for item in conservative_portfolio.allocations if item.risk_level >= 6)
    assert high_risk_weight_cons <= 0.201
    assert conservative_portfolio.average_risk_level <= 4.5


def test_compliance_guard():
    """Verify Compliance Guard flags limit overshoots and risk profile suitability violations."""
    # Portfolio exceeding quota
    bad_portfolio = allocate_assets(
        remaining_quota=350000.0, # Exceeds 300,000 max cap
        goal="Balanced",
        risk_profile="Moderate"
    )
    compliance = check_portfolio_compliance(
        portfolio=bad_portfolio,
        assessable_income=1200000.0,
        already_purchased=0.0,
        max_quota=300000.0
    )
    assert compliance.is_compliant is False
    assert any("Absolute Cap" in v or "Quota Overshoot" in v for v in compliance.violations)

    # Moderate portfolio but conservative user with high average risk
    risky_portfolio = allocate_assets(
        remaining_quota=50000.0,
        goal="Growth",
        risk_profile="Aggressive" # Generates risky draft
    )
    # Check compliance forcing Conservative user rules
    compliance_cons = check_portfolio_compliance(
        portfolio=risky_portfolio,
        assessable_income=1000000.0,
        already_purchased=0.0,
        max_quota=300000.0,
        client_risk_profile="Conservative"
    )
    # Should fail suitability because risky_portfolio has > 20% high risk weight
    assert compliance_cons.is_compliant is False
    assert any("Risk Mismatch" in v or "Average Risk" in v for v in compliance_cons.violations)


def test_auq_manager():
    """Verify AUQ manager flags low OCR confidence, data conflicts, and escalates to human override."""
    from backend.services.portfolio_allocator import PortfolioAllocationItem, DraftPortfolio

    # Clean portfolio holding only clean funds (B-THAIESG contains only clean SCC and CPALL)
    clean_portfolio = DraftPortfolio(
        allocations=[
            PortfolioAllocationItem(
                fund_code="B-THAIESG",
                fund_name="Bualuang Thai ESG Balanced Fund",
                esg_rating="AAA",
                risk_level=5,
                asset_class="Mixed",
                weight=1.0,
                amount=100000.0,
                units=8695.6
            )
        ],
        total_allocated=100000.0,
        average_risk_level=5.0,
        average_esg_rating="AAA",
        financial_goal="Balanced",
        risk_profile="Moderate"
    )
    
    # 1. High confidence case (no conflicts, verified OCR)
    report_high = evaluate_system_confidence(
        ocr_confidence=1.0,
        user_profile_complete=True,
        compliance_passed=True,
        portfolio=clean_portfolio
    )
    assert report_high.confidence_score >= 90.0
    assert report_high.uncertainty_rating == "LOW"
    assert report_high.status == "APPROVED"
    assert report_high.requires_override is False

    # 2. Low confidence case due to low OCR quality
    report_low_ocr = evaluate_system_confidence(
        ocr_confidence=0.60,
        user_profile_complete=True,
        compliance_passed=True,
        portfolio=clean_portfolio
    )
    assert report_low_ocr.confidence_score < 85.0
    assert report_low_ocr.requires_override is True
    assert report_low_ocr.aleatoric_uncertainty_score > 0.0

    # 3. Escalated case due to greenwashing and governance conflicts (holding EA via SCBTHAIESG)
    conflict_portfolio = DraftPortfolio(
        allocations=[
            PortfolioAllocationItem(
                fund_code="SCBTHAIESG",
                fund_name="SCB Thai ESG Equities Dividend Fund",
                esg_rating="AA",
                risk_level=6,
                asset_class="Equity",
                weight=1.0,
                amount=100000.0,
                units=9881.4
            )
        ],
        total_allocated=100000.0,
        average_risk_level=6.0,
        average_esg_rating="AA",
        financial_goal="Dividend",
        risk_profile="Moderate"
    )
    
    report_conflict = evaluate_system_confidence(
        ocr_confidence=1.0,
        user_profile_complete=True,
        compliance_passed=True,
        portfolio=conflict_portfolio
    )
    assert report_conflict.uncertainty_rating == "HIGH"
    assert report_conflict.status == "ESCALATED"
    assert report_conflict.requires_override is True
    assert len(report_conflict.xai_justifications) > 0
    assert any("GREENWASHING" in j or "CGR" in j for j in report_conflict.xai_justifications)
    assert any("Temporary Pause" in step for step in report_conflict.structured_reasoning_trace)


def test_orchestration_endpoint_and_healing_loop():
    """Verify the API orchestrator processes end-to-end allocations and handles compliance loops."""
    # Test normal request (Aggressive Balanced)
    payload = {
        "assessable_income": 1200000.0,
        "already_purchased": 50000.0,
        "financial_goal": "Balanced",
        "risk_profile": "Aggressive",
        "ocr_confidence": 0.95
    }
    
    response = client.post("/api/v1/portfolio/allocate", json=payload)
    assert response.status_code == 200
    res_data = response.json()
    
    assert "quota" in res_data
    assert "portfolio" in res_data
    assert "compliance" in res_data
    assert "auq" in res_data
    assert len(res_data["execution_trace"]) > 0
    assert res_data["compliance"]["is_compliant"] is True

    # Test request that triggers self-healing (Conservative user requests Growth goal)
    # The initial growth portfolio would be high risk, violating conservative limits.
    # The healing loop will catch this and re-allocate with conservative constraints.
    payload_heal = {
        "assessable_income": 1000000.0,
        "already_purchased": 0.0,
        "financial_goal": "Growth",
        "risk_profile": "Conservative",
        "ocr_confidence": 0.98
    }
    
    response_heal = client.post("/api/v1/portfolio/allocate", json=payload_heal)
    assert response_heal.status_code == 200
    res_data_heal = response_heal.json()
    
    assert res_data_heal["compliance"]["is_compliant"] is True
    # Verify that the trace documents the healing action
    trace_text = "".join(res_data_heal["execution_trace"])
    assert "Self-Healing Action" in trace_text
