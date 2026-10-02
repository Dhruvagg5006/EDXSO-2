"""
Deterministic Extraction Rules and Normalization Helpers.
Standardizes Indian currency values, dates, education levels, and criteria.
Never invents data—strictly defaults to 'Not specified' when absent.
"""

import re
from typing import Optional, List, Tuple
from datetime import datetime


def parse_inr_amount(text: str) -> Tuple[str, Optional[float]]:
    """
    Extracts text description of scholarship amount and normalizes into a numeric INR value.
    Example: 'Up to ₹2,00,000 per annum' -> ('Up to ₹2,00,000 per annum', 200000.0)
    """
    if not text or text.strip().lower() in ("not specified", "none", "n/a"):
        return "Not specified", None

    cleaned = text.strip()
    lakh_match = re.search(r'(?:₹|rs\.?|inr)?\s*([0-9]+(?:\.[0-9]+)?)\s*(?:lakh|lac|lakhs)', cleaned, re.IGNORECASE)
    if lakh_match:
        val = float(lakh_match.group(1)) * 100000.0
        return cleaned, val

    direct_match = re.search(r'(?:₹|rs\.?|inr)\s*([0-9,]+)', cleaned, re.IGNORECASE)
    if direct_match:
        digits = direct_match.group(1).replace(",", "")
        try:
            return cleaned, float(digits)
        except ValueError:
            pass

    return cleaned, None


def parse_income_criteria(text: str) -> Tuple[str, Optional[float]]:
    """
    Parses family income limit into normalized text and numeric ceiling.
    Anti-hallucination: Defaults strictly to 'Not specified' and None if no income limit is found.
    """
    if not text or text.strip().lower() in ("not specified", "none", "n/a", "no income limit"):
        return "Not specified", None

    cleaned = text.strip()
    lakh_match = re.search(r'(?:₹|rs\.?|inr)?\s*([0-9]+(?:\.[0-9]+)?)\s*(?:lakh|lac|lakhs)', cleaned, re.IGNORECASE)
    if lakh_match:
        val = float(lakh_match.group(1)) * 100000.0
        return cleaned, val

    direct_match = re.search(r'(?:₹|rs\.?|inr)\s*([0-9,]+)', cleaned, re.IGNORECASE)
    if direct_match:
        digits = direct_match.group(1).replace(",", "")
        try:
            return cleaned, float(digits)
        except ValueError:
            pass

    return cleaned, None


def parse_deadline(date_str: str) -> Tuple[str, bool]:
    """
    Normalizes date string to YYYY-MM-DD format if possible.
    Returns: (normalized_date_str, is_expired)
    """
    if not date_str or date_str.lower() in ("rolling", "not specified", "open year round"):
        return date_str or "Not specified", False

    # Try common formats
    formats = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%d %B %Y",
        "%d %b %Y",
        "%B %d, %Y",
    ]
    cleaned = date_str.strip()
    # Remove ordinal suffixes like 31st, 1st, 2nd
    cleaned = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', cleaned)

    for fmt in formats:
        try:
            dt = datetime.strptime(cleaned, fmt)
            is_expired = dt.date() < datetime.utcnow().date()
            return dt.strftime("%Y-%m-%d"), is_expired
        except ValueError:
            continue

    # If YYYY-MM-DD is embedded
    iso_match = re.search(r'\b(202[4-9]-\d{2}-\d{2})\b', date_str)
    if iso_match:
        try:
            dt = datetime.strptime(iso_match.group(1), "%Y-%m-%d")
            return dt.strftime("%Y-%m-%d"), dt.date() < datetime.utcnow().date()
        except ValueError:
            pass

    return date_str, False


def classify_course_levels(text: str) -> List[str]:
    """
    Detects course levels from text: UG, PG, PhD, School.
    """
    text_lower = text.lower()
    levels = []
    if any(k in text_lower for k in ["b.tech", "b.e", "b.sc", "b.com", "bba", "undergraduate", "bachelor", "degree"]):
        levels.append("Undergraduate (UG)")
    if any(k in text_lower for k in ["m.tech", "m.e", "m.sc", "m.com", "mba", "postgraduate", "master"]):
        levels.append("Postgraduate (PG)")
    if any(k in text_lower for k in ["phd", "ph.d", "doctoral", "research fellow", "postdoc"]):
        levels.append("Doctoral (PhD)")
    if any(k in text_lower for k in ["class 11", "class 12", "intermediate", "plus two", "higher secondary"]):
        levels.append("Senior Secondary (Class 11-12)")
    if any(k in text_lower for k in ["class 1", "class 8", "class 9", "class 10", "school", "matric"]):
        levels.append("School (Class 1-10)")

    return levels or ["Undergraduate (UG)"]
