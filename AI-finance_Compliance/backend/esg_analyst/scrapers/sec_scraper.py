import re
import time
import requests
from datetime import datetime
from typing import List, Dict, Any
from bs4 import BeautifulSoup


class SECScraper:
    """
    Scrapes enforcement action data from the Thai Securities and Exchange Commission (ก.ล.ต.)
    Source: https://market.sec.or.th/public/idisc/en/ViewMore/enforce-recent
    """

    BASE_URL = "https://market.sec.or.th/public/idisc/en/ViewMore/enforce-recent"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }

    @staticmethod
    def scrape_enforcement_actions(query_type: str = "RECENT", vio_type: str = "ALL") -> List[Dict[str, Any]]:
        """
        Scrapes the SEC enforcement actions table.

        Args:
            query_type: "RECENT" for recent 3 months, or other query types.
            vio_type: "ALL" for all violation types, or specific type filters.

        Returns:
            List of enforcement action records.
        """
        url = f"{SECScraper.BASE_URL}?QueryType={query_type}&VioTypeTxt={vio_type}"

        try:
            # Respectful delay before scraping
            time.sleep(1)

            response = requests.get(url, headers=SECScraper.HEADERS, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "lxml")

            # Find the enforcement table (it has id="gPP26T02" based on research)
            table = soup.find("table", {"id": "gPP26T02"})
            if not table:
                # Fallback: find any table with striped class
                table = soup.find("table", class_="table-striped")
            if not table:
                print("[SECScraper] Could not find enforcement table in HTML.")
                return []

            rows = table.find_all("tr")
            if len(rows) < 2:
                return []

            # Parse header row to determine column order
            headers = [th.get_text(strip=True) for th in rows[0].find_all("th")]

            records = []
            for row in rows[1:]:
                cells = row.find_all("td")
                if len(cells) < 7:
                    continue

                try:
                    # Extract cell text
                    row_num = cells[0].get_text(strip=True)
                    date_str = cells[1].get_text(strip=True)
                    name = cells[2].get_text(strip=True)
                    relevant_section = cells[3].get_text(strip=True)
                    summarized_facts = cells[4].get_text(strip=True)
                    sec_news = cells[5].get_text(strip=True) if len(cells) > 5 else ""
                    enforcement_type = cells[6].get_text(strip=True) if len(cells) > 6 else ""
                    details = cells[7].get_text(strip=True) if len(cells) > 7 else ""
                    remark = cells[8].get_text(strip=True) if len(cells) > 8 else ""

                    # Parse date (format: DD/MM/YYYY)
                    parsed_date = None
                    try:
                        parsed_date = datetime.strptime(date_str, "%d/%m/%Y").strftime("%Y-%m-%d")
                    except ValueError:
                        parsed_date = date_str

                    # Try to extract ticker from the summarized facts
                    ticker = SECScraper._extract_ticker(summarized_facts, name)

                    record = {
                        "row_number": int(row_num) if row_num.isdigit() else 0,
                        "enforcement_date": parsed_date,
                        "name": name,
                        "ticker": ticker,
                        "relevant_section": relevant_section,
                        "summarized_facts": summarized_facts,
                        "enforcement_type": enforcement_type,
                        "details": details,
                        "remark": remark,
                        "severity": SECScraper._classify_severity(enforcement_type, summarized_facts),
                    }
                    records.append(record)
                except Exception as e:
                    print(f"[SECScraper] Error parsing row: {e}")
                    continue

            print(f"[SECScraper] Successfully scraped {len(records)} enforcement records.")
            return records

        except requests.RequestException as e:
            print(f"[SECScraper] Request failed: {e}")
            return []
        except Exception as e:
            print(f"[SECScraper] Unexpected error: {e}")
            return []

    @staticmethod
    def _extract_ticker(facts: str, name: str) -> str:
        """
        Tries to extract a stock ticker symbol from the enforcement record.
        Looks for patterns like "XYZ Public Company Limited" or ("XYZ") in facts text.
        """
        # Pattern 1: Look for quoted ticker in parentheses like ("VGI") or ("BYD")
        ticker_match = re.search(r'\("?([A-Z]{2,6})"?\)', facts)
        if ticker_match:
            return ticker_match.group(1)

        # Pattern 2: Look for "of XXXX Public Company"
        company_match = re.search(r'of\s+([A-Z][A-Za-z\s]+)\s+Public\s+Company', facts)
        if company_match:
            # Try to extract abbreviation
            pass

        # Pattern 3: Look for ticker directly in name field (for company enforcement)
        name_ticker = re.search(r'^([A-Z]{2,6})\s', name)
        if name_ticker:
            return name_ticker.group(1)

        return ""

    @staticmethod
    def _classify_severity(enforcement_type: str, facts: str) -> str:
        """Classifies the severity of the enforcement action."""
        enforcement_lower = enforcement_type.lower()
        facts_lower = facts.lower()

        if "criminal complaint" in enforcement_lower or "criminal prosecution" in enforcement_lower:
            return "High"
        if "civil sanction" in enforcement_lower or "market manipulation" in facts_lower:
            return "High"
        if "fraud" in facts_lower or "embezzlement" in facts_lower or "false financial" in facts_lower:
            return "High"
        if "criminal fine" in enforcement_lower:
            return "Medium"
        if "administrative" in enforcement_lower:
            return "Low"

        return "Medium"
