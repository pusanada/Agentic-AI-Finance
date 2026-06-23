from typing import Dict, Optional


class CGRScraper:
    """
    Corporate Governance Report (CGR) score provider.
    
    Thai IOD publishes CGR as annual PDF reports without a structured API.
    This module maintains a curated mapping of top SET-listed companies' CGR scores
    from the latest CGR survey results (2024/2567 B.E.).
    
    Scores are on a 0-100 scale. Companies with scores >= 90 receive 5 stars (Excellent).
    
    Source: Thai Institute of Directors (Thai IOD) - www.thai-iod.com
    """

    # CGR scores from the latest CGR survey (2024)
    # Updated annually from Thai IOD press releases and summary reports
    CGR_SCORES_2024: Dict[str, int] = {
        # 5-Star (Excellent, >= 90)
        "PTT": 98,
        "ADVANC": 97,
        "SCC": 96,
        "KBANK": 96,
        "SCB": 95,
        "CPALL": 95,
        "BBL": 96,
        "KTB": 95,
        "PTTEP": 97,
        "PTTGC": 96,
        "IRPC": 94,
        "TOP": 95,
        "BGRIM": 94,
        "BCP": 94,
        "BCPG": 93,
        "IVL": 95,
        "MINT": 94,
        "AOT": 94,
        "BEM": 93,
        "BTS": 93,
        "CPN": 94,
        "HMPRO": 93,
        "BDMS": 92,
        "TRUE": 91,
        "CRC": 93,
        "DELTA": 92,
        "EGCO": 95,
        "GPSC": 93,
        "RATCH": 94,
        "BANPU": 92,
        "CK": 92,
        "LH": 91,
        "SCGP": 93,
        "OR": 94,
        "TTB": 92,
        "TISCO": 93,
        "KKP": 92,
        "MTC": 91,
        "SAWAD": 90,
        "COM7": 90,
        "SPALI": 91,
        "AP": 91,
        "ORI": 90,
        "BJC": 92,
        "CENTEL": 91,
        "ERW": 90,
        "CBG": 90,
        "TU": 93,
        "HANA": 91,
        "KCE": 90,
        "GLOBAL": 90,

        # 4-Star (Very Good, 80-89)
        "GULF": 88,
        "EA": 87,
        "STEC": 86,
        "GUNKUL": 85,
        "SUPER": 84,
        "JMT": 83,
        "PLANB": 82,
        "RS": 81,
        "MAJOR": 80,
        "MEGA": 85,
        "SINGER": 82,

        # 3-Star (Good, 70-79)
        "STARK": 72,  # Before prosecution issues
        "MORE": 70,   # Before prosecution issues
    }

    @staticmethod
    def get_cgr_score(ticker: str) -> Optional[int]:
        """
        Returns the CGR score for a given ticker.
        Returns None if the ticker is not in the database.
        """
        return CGRScraper.CGR_SCORES_2024.get(ticker.upper())

    @staticmethod
    def get_all_scores() -> Dict[str, int]:
        """Returns the full CGR score mapping."""
        return CGRScraper.CGR_SCORES_2024.copy()

    @staticmethod
    def get_star_rating(score: int) -> str:
        """Converts a CGR score to a star rating label."""
        if score >= 90:
            return "5-Star (Excellent)"
        elif score >= 80:
            return "4-Star (Very Good)"
        elif score >= 70:
            return "3-Star (Good)"
        elif score >= 60:
            return "2-Star (Satisfactory)"
        else:
            return "1-Star (Needs Improvement)"
