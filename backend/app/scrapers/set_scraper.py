import io
import time
import requests
import pandas as pd
from typing import List, Dict, Any, Optional


class SETScraper:
    """
    Scrapes stock listing data from the Stock Exchange of Thailand (ตลท.)
    Uses official XLS download for listed companies.
    """

    # Official SET download link for all listed companies
    LISTED_COMPANIES_XLS_URL = (
        "https://www.set.or.th/dat/eod/listedcompany/static/listedCompanies_en_US.xls"
    )
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Accept": "application/vnd.ms-excel,*/*;q=0.8",
    }

    # Known JUMP+ participating companies (extracted from SET's JUMP+ page)
    # This list is updated periodically; the JUMP+ page is JS-rendered so we maintain it here.
    KNOWN_JUMP_PLUS_TICKERS = {
        "2S", "A", "AAV", "ABPIF", "ADVANC", "AH", "AI", "AMANAH", "AMATA", "AOT",
        "AP", "ASP", "AWC", "BANPU", "BAY", "BBL", "BCH", "BCP", "BCPG", "BDMS",
        "BEM", "BGRIM", "BH", "BJC", "BLA", "BPP", "BTS", "CBG", "CENTEL", "CHG",
        "CK", "CKP", "COM7", "CPALL", "CPF", "CPN", "CRC", "DELTA", "DOHOME",
        "DTAC", "EA", "EGCO", "EPG", "ERW", "GFPT", "GGC", "GLOBAL", "GPSC", "GULF",
        "GUNKUL", "HANA", "HMPRO", "ICHI", "INTUCH", "IRPC", "IVL", "JAS", "JMT",
        "KBANK", "KCE", "KKP", "KTB", "KTC", "LH", "MAJOR", "MEGA", "MINT", "MTC",
        "NRF", "OR", "ORI", "OSP", "PCSGH", "PJW", "PLANB", "PR9", "PTTEP", "PTTGC",
        "PTT", "QH", "RATCH", "RBF", "RS", "SAWAD", "SCC", "SCB", "SCGP", "SINGER",
        "SIRI", "SPALI", "SPCG", "STA", "STEC", "SUPER", "SYNEX", "TASCO", "TCAP",
        "THAI", "THANI", "TISCO", "TKN", "TMB", "TOP", "TPIPP", "TRUE", "TTB", "TU",
        "TVO", "VGI", "WHA", "WHAUP",
    }

    @staticmethod
    def scrape_listed_companies() -> List[Dict[str, Any]]:
        """
        Downloads and parses the official SET listed companies XLS file.

        Returns:
            List of dicts with keys: ticker, name, market, industry, sector.
        """
        try:
            time.sleep(1)  # Respectful delay

            response = requests.get(
                SETScraper.LISTED_COMPANIES_XLS_URL,
                headers=SETScraper.HEADERS,
                timeout=30
            )
            response.raise_for_status()

            # Parse XLS with pandas (try HTML first since SET often returns HTML labeled as .xls)
            try:
                dfs = pd.read_html(io.BytesIO(response.content), header=1)
                df = dfs[0]
            except Exception as e:
                print(f"[SETScraper] HTML parsing failed, trying Excel: {e}")
                df = pd.read_excel(
                    io.BytesIO(response.content),
                    engine="xlrd"  # For .xls format
                )

            # Normalize column names (the XLS has varying header names)
            df.columns = [str(c).strip() for c in df.columns]

            # Map common column names
            col_map = {}
            for col in df.columns:
                col_lower = col.lower()
                if "symbol" in col_lower or "ticker" in col_lower:
                    col_map["ticker"] = col
                elif "company" in col_lower or "name" in col_lower:
                    col_map["name"] = col
                elif "market" in col_lower:
                    col_map["market"] = col
                elif "industry" in col_lower:
                    col_map["industry"] = col
                elif "sector" in col_lower:
                    col_map["sector"] = col

            if "ticker" not in col_map:
                # Fallback: assume first column is ticker, second is name
                cols = list(df.columns)
                col_map["ticker"] = cols[0] if len(cols) > 0 else None
                col_map["name"] = cols[1] if len(cols) > 1 else None

            companies = []
            for _, row in df.iterrows():
                ticker = str(row.get(col_map.get("ticker", ""), "")).strip()
                if not ticker or ticker == "nan":
                    continue

                company = {
                    "ticker": ticker.upper(),
                    "name": str(row.get(col_map.get("name", ""), "")).strip(),
                    "market": str(row.get(col_map.get("market", ""), "SET")).strip(),
                    "industry": str(row.get(col_map.get("industry", ""), "")).strip(),
                    "sector": str(row.get(col_map.get("sector", ""), "")).strip(),
                    "jump_plus": ticker.upper() in SETScraper.KNOWN_JUMP_PLUS_TICKERS,
                }
                companies.append(company)

            print(f"[SETScraper] Successfully parsed {len(companies)} listed companies from XLS.")
            return companies

        except requests.RequestException as e:
            print(f"[SETScraper] Download failed: {e}")
            return []
        except Exception as e:
            print(f"[SETScraper] Unexpected error parsing XLS: {e}")
            return []

    @staticmethod
    def is_jump_plus(ticker: str) -> bool:
        """Check if a ticker is in the known JUMP+ program list."""
        return ticker.upper() in SETScraper.KNOWN_JUMP_PLUS_TICKERS

    @staticmethod
    def get_jump_plus_tickers() -> List[str]:
        """Returns the full list of known JUMP+ tickers."""
        return sorted(list(SETScraper.KNOWN_JUMP_PLUS_TICKERS))
