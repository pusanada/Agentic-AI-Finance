import requests
from typing import List, Dict, Any

# Mock database of SET stocks for realistic demo and fallback
MOCK_SET_DATABASE = [
    {"ticker": "PTT", "name": "PTT Public Company Limited", "industry": "Resources", "cgr_score": 98, "jump_plus": True, "price": 34.25},
    {"ticker": "CPALL", "name": "CP ALL Public Company Limited", "industry": "Services", "cgr_score": 95, "jump_plus": True, "price": 57.50},
    {"ticker": "ADVANC", "name": "Advanced Info Service Public Company Limited", "industry": "Technology", "cgr_score": 97, "jump_plus": True, "price": 208.00},
    {"ticker": "SCC", "name": "The Siam Cement Public Company Limited", "industry": "Industrials", "cgr_score": 96, "jump_plus": True, "price": 255.00},
    {"ticker": "SCB", "name": "SCB X Public Company Limited", "industry": "Financials", "cgr_score": 95, "jump_plus": True, "price": 112.50},
    {"ticker": "KBANK", "name": "Kasikornbank Public Company Limited", "industry": "Financials", "cgr_score": 96, "jump_plus": True, "price": 128.00},
    {"ticker": "GULF", "name": "Gulf Energy Development Public Company Limited", "industry": "Resources", "cgr_score": 88, "jump_plus": True, "price": 42.50},  # Fails CGR >= 90
    {"ticker": "AOT", "name": "Airports of Thailand Public Company Limited", "industry": "Services", "cgr_score": 94, "jump_plus": False, "price": 61.25}, # Fails JUMP+
    {"ticker": "BDMS", "name": "Bangkok Dusit Medical Services Public Company Limited", "industry": "Services", "cgr_score": 92, "jump_plus": True, "price": 28.00},
    {"ticker": "TRUE", "name": "True Corporation Public Company Limited", "industry": "Technology", "cgr_score": 91, "jump_plus": True, "price": 8.45},
    {"ticker": "BANPU", "name": "Banpu Public Company Limited", "industry": "Resources", "cgr_score": 92, "jump_plus": True, "price": 5.30},
    {"ticker": "STEC", "name": "Sino-Thai Engineering and Construction PLC", "industry": "Property & Construction", "cgr_score": 91, "jump_plus": False, "price": 9.10} # Fails JUMP+
]

class SETService:
    @staticmethod
    def get_all_stocks() -> List[Dict[str, Any]]:
        """
        Retrieves all stocks from the SET database.
        """
        return MOCK_SET_DATABASE

    @staticmethod
    def get_screened_stocks(min_cgr_score: int = 90) -> List[Dict[str, Any]]:
        """
        Filter stocks that are participating in JUMP+ and have a CGR score >= min_cgr_score.
        """
        all_stocks = SETService.get_all_stocks()
        screened = [
            stock for stock in all_stocks
            if stock["jump_plus"] and stock["cgr_score"] >= min_cgr_score
        ]
        return screened

    @staticmethod
    def get_stock_by_ticker(ticker: str) -> Dict[str, Any]:
        """
        Retrieves a single stock details by its ticker symbol.
        """
        ticker_upper = ticker.upper()
        for stock in MOCK_SET_DATABASE:
            if stock["ticker"] == ticker_upper:
                return stock
        return None
