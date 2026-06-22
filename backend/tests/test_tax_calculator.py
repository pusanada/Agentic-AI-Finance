import pytest
from backend.services.tax_calculator import (
    calculate_thaiesg_quota,
    TaxCalculatorRequest
)

def test_income_under_cap():
    # Income = 500k, 30% is 150k. Already purchased = 50k. Remaining room = 100k.
    req = TaxCalculatorRequest(assessable_income=500000.0, already_purchased=50000.0)
    res = calculate_thaiesg_quota(req)
    
    assert res.assessable_income == 500000.0
    assert res.already_purchased == 50000.0
    assert res.max_quota == 150000.0
    assert res.remaining_quota == 100000.0
    assert res.holding_period_years == 5

def test_income_over_cap():
    # Income = 1.5M, 30% is 450k (which is capped at 300k). Already purchased = 100k. Remaining room = 200k.
    req = TaxCalculatorRequest(assessable_income=1500000.0, already_purchased=100000.0)
    res = calculate_thaiesg_quota(req)
    
    assert res.assessable_income == 1500000.0
    assert res.already_purchased == 100000.0
    assert res.max_quota == 300000.0
    assert res.remaining_quota == 200000.0

def test_already_exceeds_cap():
    # Income = 1.5M, cap = 300k. Already purchased = 320k. Remaining room should be 0.
    req = TaxCalculatorRequest(assessable_income=1500000.0, already_purchased=320000.0)
    res = calculate_thaiesg_quota(req)
    
    assert res.max_quota == 300000.0
    assert res.remaining_quota == 0.0

def test_zero_income():
    # Income = 0, cap = 0. Already purchased = 10k. Remaining room = 0.
    req = TaxCalculatorRequest(assessable_income=0.0, already_purchased=10000.0)
    res = calculate_thaiesg_quota(req)
    
    assert res.max_quota == 0.0
    assert res.remaining_quota == 0.0

def test_exact_cap():
    # Income = 1,000,000, 30% is exactly 300k. Already purchased = 0. Remaining room = 300k.
    req = TaxCalculatorRequest(assessable_income=1000000.0, already_purchased=0.0)
    res = calculate_thaiesg_quota(req)
    
    assert res.max_quota == 300000.0
    assert res.remaining_quota == 300000.0
