"""
Unit Tests for Pydantic Scholarship Models and Schemas.
"""

import pytest
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.models.schema import ScholarshipRecord, EvidenceItem, ChangeLogRecord, ConfidenceScorecard
from src.models.enums import ScholarshipStatus, VerificationStatus, ProviderType, GenderCriteria


def test_scholarship_schema_valid_instantiation():
    record = ScholarshipRecord(
        id="test-scholarship-id",
        scholarship_name="Test Scholarship for Engineers",
        provider="Test Foundation",
        provider_type=ProviderType.CORPORATE_CSR,
        official_source_url="https://testfoundation.org/scholarship",
        application_url="https://testfoundation.org/apply",
        amount_benefit="₹50,000 per annum",
        amount_value_inr=50000.0,
        academic_requirements="Minimum 60% in Class 12",
        course_level=["Undergraduate (UG)"],
        income_criteria="Annual income ≤ ₹2,50,000",
        income_limit_inr=250000.0,
        closing_date="2026-11-30",
        confidence_score=97.5,
        verification_status=VerificationStatus.VERIFIED,
    )
    assert record.id == "test-scholarship-id"
    assert record.confidence_score == 97.5
    assert record.verification_status == VerificationStatus.VERIFIED
    assert record.status == ScholarshipStatus.ACTIVE


def test_confidence_score_range_validation():
    with pytest.raises(Exception):
        ScholarshipRecord(
            id="invalid-score",
            scholarship_name="Invalid Score Record",
            provider="Provider",
            provider_type=ProviderType.CORPORATE_CSR,
            official_source_url="https://test.org",
            amount_benefit="₹10,000",
            academic_requirements="None",
            closing_date="2026-12-31",
            confidence_score=105.0,  # Invalid: > 100
            verification_status=VerificationStatus.VERIFIED,
        )


def test_evidence_item_creation():
    ev = EvidenceItem(
        field_name="closing_date",
        extracted_value="2026-10-31",
        source_url="https://scholarships.gov.in",
        evidence_text="Online portal applications close on 31 October 2026.",
        match_score=99.0
    )
    assert ev.field_name == "closing_date"
    assert ev.match_score == 99.0
    assert "31 October 2026" in ev.evidence_text
