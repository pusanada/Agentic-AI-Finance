import requests
from typing import List, Dict, Any, Optional

from backend.config import settings
from backend.esg_analyst.scrapers.cache import ScraperCache
from backend.esg_analyst.scrapers.set_scraper import SETScraper
from backend.esg_analyst.scrapers.cgr_scraper import CGRScraper

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

# Initialize cache
_cache = ScraperCache(settings.esg_cache_dir, default_ttl_hours=settings.cache_ttl_hours)


class SETService:
    @staticmethod
    def get_all_stocks() -> List[Dict[str, Any]]:
        """
        Retrieves all stocks. Tries real scraping first, falls back to mock data.
        When scraping is enabled, downloads the official SET XLS and enriches
        with CGR scores and JUMP+ membership data.
        """
        if not settings.scraping_enabled:
            return MOCK_SET_DATABASE


        # Try cache first
        cached = _cache.get("set_listed_companies")
        if cached:
            print("[SETService] Using cached listed companies data.")
            return cached

        # Try scraping
        try:
            scraped = SETScraper.scrape_listed_companies()
            if scraped:
                # Enrich with CGR scores
                enriched = []
                for company in scraped:
                    ticker = company["ticker"]
                    cgr_score = CGRScraper.get_cgr_score(ticker)

                    enriched.append({
                        "ticker": ticker,
                        "name": company["name"],
                        "industry": company.get("industry", ""),
                        "cgr_score": cgr_score if cgr_score is not None else 0,
                        "jump_plus": company.get("jump_plus", False),
                        "price": 0.0,  # Price not available from XLS
                        "market": company.get("market", "SET"),
                        "sector": company.get("sector", ""),
                        "data_source": "scraped"
                    })

                # Cache the enriched results
                _cache.set("set_listed_companies", enriched)
                print(f"[SETService] Scraped and cached {len(enriched)} companies.")
                return enriched
        except Exception as e:
            print(f"[SETService] Scraping failed, falling back to mock: {e}")

        # Fallback to mock
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
    def get_stock_by_ticker(ticker: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a single stock details by its ticker symbol.
        Searches scraped data first, then falls back to mock.
        """
        ticker_upper = ticker.upper()
        all_stocks = SETService.get_all_stocks()

        for stock in all_stocks:
            if stock["ticker"] == ticker_upper:
                return stock

        # If not found in scraped data, check mock specifically
        for stock in MOCK_SET_DATABASE:
            if stock["ticker"] == ticker_upper:
                return stock

        return None
