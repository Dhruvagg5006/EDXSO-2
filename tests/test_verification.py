"""
Unit Tests for Anti-Hallucination and Verification Engine.
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.extraction.extractor import ScholarshipExtractor
from src.extraction.rules import parse_inr_amount, parse_income_criteria, parse_deadline


def test_anti_hallucination_income_defaults_to_not_specified():
    html_without_income = """
    <html>
        <body>
            <h1>National Merit Science Fellowship</h1>
            <p>Eligibility: Students pursuing B.Sc. with minimum 85% marks.</p>
            <p>Scholarship Benefit: ₹60,000 per annum</p>
            <p>Last date to apply: 30 November 2026</p>
        </body>
    </html>
    """
    rec = ScholarshipExtractor.extract_from_html(
        html_content=html_without_income,
        source_url="https://dst.gov.in/fellowship",
        slug_id="dst-merit-fellowship"
    )
    # Must never hallucinate an arbitrary income ceiling!
    assert rec.income_criteria == "Not specified"
    assert rec.income_limit_inr is None


def test_amount_parsing_and_normalization():
    text1, val1 = parse_inr_amount("Grant of ₹2,50,000 per annum")
    assert val1 == 250000.0

    text2, val2 = parse_inr_amount("Scholarship of 5 Lakhs over 4 years")
    assert val2 == 500000.0

    text3, val3 = parse_inr_amount("Not specified")
    assert val3 is None


def test_income_parsing_and_normalization():
    text1, val1 = parse_income_criteria("Family income less than Rs. 8,00,000/- per annum")
    assert val1 == 800000.0

    text2, val2 = parse_income_criteria("No income limit specified")
    assert val2 is None
