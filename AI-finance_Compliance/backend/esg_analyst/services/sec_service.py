from datetime import datetime, timedelta
from typing import Dict, Any, List

from backend.esg_analyst.config import settings
from backend.esg_analyst.scrapers.cache import ScraperCache
from backend.esg_analyst.scrapers.sec_scraper import SECScraper

# Mock database of SEC enforcement cases in Thailand (past 5 years)
MOCK_SEC_PROSECUTIONS = [
    {
        "ticker": "STARK",
        "company_name": "Stark Corporation Public Company Limited",
        "date": "2023-07-06",
        "case_type": "Criminal Prosecution",
        "details": "Filing false financial statements, corporate fraud, and embezzlement of company assets by executives.",
        "severity": "High",
        "action_taken": "Referred to Department of Special Investigation (DSI) and frozen assets."
    },
    {
        "ticker": "MORE",
        "company_name": "More Return Public Company Limited",
        "date": "2022-11-10",
        "case_type": "Market Manipulation / Civil Sanctions",
        "details": "Abnormal trading behaviors, stock price manipulation, and collusion among major shareholders.",
        "severity": "High",
        "action_taken": "Fined 10 million THB, suspended trading, and banned executives from directorship."
    },
    {
        "ticker": "SCB",
        "company_name": "SCB X Public Company Limited",
        "date": "2019-03-12",  # Older than 5 years (2026-06-21)
        "case_type": "Civil Penalty",
        "details": "Internal audit control failure in a subsidiary.",
        "severity": "Low",
        "action_taken": "Fined 500,000 THB."
    }
]

# Initialize cache
_cache = ScraperCache(settings.CACHE_DIR, default_ttl_hours=settings.CACHE_TTL_HOURS)


class SECService:
    @staticmethod
    def _get_enforcement_data() -> List[Dict[str, Any]]:
        """
        Returns enforcement data from scraping (with cache) or mock fallback.
        """
        if not settings.SCRAPING_ENABLED:
            return MOCK_SEC_PROSECUTIONS

        # Try cache first
        cached = _cache.get("sec_enforcement")
        if cached:
            print("[SECService] Using cached SEC enforcement data.")
            return cached

        # Try scraping
        try:
            scraped = SECScraper.scrape_enforcement_actions()
            if scraped:
                # Normalize scraped data to match the expected schema
                normalized = []
                for record in scraped:
                    normalized.append({
                        "ticker": record.get("ticker", ""),
                        "company_name": record.get("name", ""),
                        "date": record.get("enforcement_date", ""),
                        "case_type": record.get("enforcement_type", ""),
                        "details": record.get("summarized_facts", ""),
                        "severity": record.get("severity", "Medium"),
                        "action_taken": record.get("details", ""),
                        "remark": record.get("remark", ""),
                        "relevant_section": record.get("relevant_section", ""),
                        "data_source": "scraped"
                    })

                # Cache the results
                _cache.set("sec_enforcement", normalized)
                print(f"[SECService] Scraped and cached {len(normalized)} enforcement records.")
                return normalized
        except Exception as e:
            print(f"[SECService] Scraping failed, falling back to mock: {e}")

        return MOCK_SEC_PROSECUTIONS

    @staticmethod
    def get_prosecution_history(ticker: str) -> List[Dict[str, Any]]:
        """
        Retrieves all SEC prosecution histories matching the ticker.
        Searches both scraped data and mock data.
        """
        ticker_upper = ticker.upper()
        all_data = SECService._get_enforcement_data()

        # Direct ticker match
        results = [case for case in all_data if case.get("ticker", "").upper() == ticker_upper]

        # Also search in company name and details for the ticker symbol
        if not results:
            for case in all_data:
                details = case.get("details", "").upper()
                company = case.get("company_name", "").upper()
                if ticker_upper in details or ticker_upper in company:
                    results.append(case)

        return results

    @staticmethod
    def is_clean(ticker: str, years: int = 5) -> Dict[str, Any]:
        """
        Checks if the company has any civil/criminal prosecution in the past N years.
        Returns:
            dict: {
                "is_clean": bool,
                "cases": List[Dict],
                "message": str
            }
        """
        current_date = datetime.now()  # We are in 2026
        limit_date = current_date - timedelta(days=years * 365)

        cases = SECService.get_prosecution_history(ticker)
        recent_cases = []

        for case in cases:
            date_str = case.get("date", "")
            if not date_str:
                continue
            try:
                case_date = datetime.strptime(date_str, "%Y-%m-%d")
                if case_date >= limit_date:
                    recent_cases.append(case)
            except ValueError:
                # If date can't be parsed, include it as a precaution
                recent_cases.append(case)

        if len(recent_cases) > 0:
            return {
                "is_clean": False,
                "cases": recent_cases,
                "message": f"Fails SEC check: Has {len(recent_cases)} prosecution case(s) in the past {years} years."
            }
        else:
            return {
                "is_clean": True,
                "cases": [],
                "message": f"Passes SEC check: No prosecutions found in the past {years} years."
            }
