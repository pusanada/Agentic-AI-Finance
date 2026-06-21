import sys
from pathlib import Path

# Add backend to path for testing
sys.path.append(str(Path(__file__).resolve().parent.parent / "backend"))

from app.services.set_service import SETService

def test_get_all_stocks():
    stocks = SETService.get_all_stocks()
    assert len(stocks) > 0
    assert any(s["ticker"] == "PTT" for s in stocks)

def test_get_screened_stocks():
    screened = SETService.get_screened_stocks()
    assert len(screened) > 0
    # Every screened stock must be JUMP+ and CGR >= 90
    for stock in screened:
        assert stock["jump_plus"] is True
        assert stock["cgr_score"] >= 90

def test_get_stock_by_ticker():
    stock = SETService.get_stock_by_ticker("PTT")
    assert stock is not None
    assert stock["name"] == "PTT Public Company Limited"
    
    none_stock = SETService.get_stock_by_ticker("NONEXISTENT")
    assert none_stock is None
