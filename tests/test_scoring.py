"""
Unit Tests for Mathematical Confidence Scoring Engine.
Tests the 6-pillar methodology and strict >=95.0% verification threshold.
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.models.schema import ScholarshipRecord, EvidenceItem
from src.models.enums import ScholarshipStatus, VerificationStatus, ProviderType, GenderCriteria
from src.verification.scoring_engine import ScoringEngine


def test_government_portal_full_evidence_scores_verified():
    rec = ScholarshipRecord(
        id="test-gov-scholarship",
        scholarship_name="Test National Scheme",
        provider="Ministry of Education",
        provider_type=ProviderType.GOVERNMENT_CENTRAL,
        official_source_url="https://scholarships.gov.in/scheme",
        application_url="https://scholarships.gov.in/apply",
        amount_benefit="₹50,000 per annum",
        amount_value_inr=50000.0,
        academic_requirements="Class 12 passed with 75% marks",
        course_level=["Undergraduate (UG)"],
        income_criteria="Income ≤ ₹2,50,000",
        closing_date="2026-11-30",
        confidence_score=0.0,
        verification_status=VerificationStatus.REVIEW_REQUIRED,
        evidence_items=[
            EvidenceItem(field_name="amount_benefit", extracted_value="₹50,000", source_url="https://scholarships.gov.in", evidence_text="Grant of Rs 50,000 per annum"),
            EvidenceItem(field_name="academic_requirements", extracted_value="75%", source_url="https://scholarships.gov.in", evidence_text="Class 12 with 75 percent"),
            EvidenceItem(field_name="income_criteria", extracted_value="≤ 2.5L", source_url="https://scholarships.gov.in", evidence_text="Income ceiling 2.5 Lakh"),
            EvidenceItem(field_name="closing_date", extracted_value="2026-11-30", source_url="https://scholarships.gov.in", evidence_text="Closes 30 Nov 2026"),
            EvidenceItem(field_name="application_url", extracted_value="apply", source_url="https://scholarships.gov.in", evidence_text="Apply online portal"),
        ]
    )
    scorecard = ScoringEngine.calculate_scorecard(rec, http_status=200)
    assert scorecard.total_score >= 95.0
    assert scorecard.verification_status == VerificationStatus.VERIFIED
    assert scorecard.domain_score == 25.0
    assert scorecard.reachability_score == 15.0


def test_aggregator_source_fails_verified_threshold():
    rec = ScholarshipRecord(
        id="test-aggregator-lead",
        scholarship_name="Third Party Blog Post Guide",
        provider="Aggregator Website",
        provider_type=ProviderType.AGGREGATOR,
        official_source_url="https://www.buddy4study.com/article/scholarships",
        application_url="https://www.buddy4study.com/login",
        amount_benefit="₹10,000 estimated",
        academic_requirements="General eligibility",
        closing_date="2026-12-31",
        confidence_score=0.0,
        verification_status=VerificationStatus.REVIEW_REQUIRED,
    )
    scorecard = ScoringEngine.calculate_scorecard(rec, http_status=200)
    # Aggregator domain cannot achieve >= 95%
    assert scorecard.total_score < 95.0
    assert scorecard.verification_status == VerificationStatus.REVIEW_REQUIRED
    assert scorecard.domain_score <= 10.0


def test_http_404_penalizes_reachability_score():
    rec = ScholarshipRecord(
        id="test-dead-link",
        scholarship_name="Withdrawn Scholarship",
        provider="Test Org",
        provider_type=ProviderType.FOUNDATION_TRUST,
        official_source_url="https://testfoundation.org/dead-link",
        amount_benefit="₹20,000",
        academic_requirements="UG students",
        closing_date="2026-12-31",
        confidence_score=0.0,
        verification_status=VerificationStatus.REVIEW_REQUIRED,
    )
    scorecard = ScoringEngine.calculate_scorecard(rec, http_status=404)
    assert scorecard.reachability_score == 0.0
    assert scorecard.verification_status == VerificationStatus.REVIEW_REQUIRED
