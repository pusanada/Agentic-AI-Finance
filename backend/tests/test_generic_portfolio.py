import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_generic_portfolio_allocation_success():
    """Verify that generic portfolio allocation generates correct outputs and passes suitability check."""
    payload = {
        "investment_budget": 150000.0,
        "financial_goal": "Dividend",
        "risk_profile": "Moderate",
        "user_instructions": ""
    }
    response = client.post("/api/v1/portfolio/allocate_generic", json=payload)
    assert response.status_code == 200
    res_data = response.json()

    assert "portfolio" in res_data
    assert "compliance" in res_data
    assert "auq" in res_data
    assert "execution_trace" in res_data
    
    portfolio = res_data["portfolio"]
    assert portfolio["total_allocated"] == 150000.0
    assert portfolio["financial_goal"] == "Dividend"
    assert portfolio["risk_profile"] in ["Aggressive", "Moderate"]
    
    # Assert compliance passes for skip_tax_rules=True
    compliance = res_data["compliance"]
    assert compliance["is_compliant"] is True
    assert len(compliance["violations"]) == 0
    
    # Assert AUQ reports status, reasoning traces, and correct uncertainty
    auq = res_data["auq"]
    assert "confidence_score" in auq
    assert auq["status"] == "ESCALATED"
    assert auq["uncertainty_rating"] == "HIGH"
    assert auq["requires_override"] is True


def test_generic_portfolio_allocation_zero_budget():
    """Verify that allocation with a zero budget completes safely and logs a warning."""
    payload = {
        "investment_budget": 0.0,
        "financial_goal": "Balanced",
        "risk_profile": "Conservative"
    }
    response = client.post("/api/v1/portfolio/allocate_generic", json=payload)
    assert response.status_code == 200
    res_data = response.json()
    
    portfolio = res_data["portfolio"]
    assert portfolio["total_allocated"] == 0.0
    assert all(item["amount"] == 0.0 for item in portfolio["allocations"])
    
    # Assert trace shows warning
    trace = res_data["execution_trace"]
    assert any("zero" in step.lower() for step in trace)


def test_generic_portfolio_self_healing():
    """Verify that self-healing loop runs when conservative investor requests a growth goal."""
    payload = {
        "investment_budget": 200000.0,
        "financial_goal": "Growth",
        "risk_profile": "Conservative"
    }
    response = client.post("/api/v1/portfolio/allocate_generic", json=payload)
    assert response.status_code == 200
    res_data = response.json()
    
    # The portfolio should heal to be compliant (Conservative caps)
    assert res_data["compliance"]["is_compliant"] is True
    
    # Trace should list self healing steps
    trace = res_data["execution_trace"]
    trace_text = "".join(trace)
    assert "Self-Healing Action" in trace_text
    
    # Check that high risk assets weight in final portfolio is <= 20%
    portfolio = res_data["portfolio"]
    high_risk_weight = sum(item["weight"] for item in portfolio["allocations"] if item["risk_level"] >= 6)
    assert high_risk_weight <= 0.201


def test_generic_portfolio_user_instructions():
    """Verify custom instructions to avoid specific funds are followed."""
    payload = {
        "investment_budget": 100000.0,
        "financial_goal": "Growth",
        "risk_profile": "Aggressive",
        "user_instructions": "avoid K-THAIESG-A"
    }
    response = client.post("/api/v1/portfolio/allocate_generic", json=payload)
    assert response.status_code == 200
    res_data = response.json()
    
    portfolio = res_data["portfolio"]
    # Verify that K-THAIESG-A is not in the allocations
    allocated_funds = [item["fund_code"] for item in portfolio["allocations"]]
    assert "K-THAIESG-A" not in allocated_funds
