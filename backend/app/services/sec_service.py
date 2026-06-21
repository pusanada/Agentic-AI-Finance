from datetime import datetime, timedelta
from typing import Dict, Any, List

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

class SECService:
    @staticmethod
    def get_prosecution_history(ticker: str) -> List[Dict[str, Any]]:
        """
        Retrieves all SEC prosecution histories matching the ticker.
        """
        ticker_upper = ticker.upper()
        return [case for case in MOCK_SEC_PROSECUTIONS if case["ticker"] == ticker_upper]

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
            case_date = datetime.strptime(case["date"], "%Y-%m-%d")
            if case_date >= limit_date:
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
