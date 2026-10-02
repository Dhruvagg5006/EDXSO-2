"""
Unit Tests for Change Detection and State Transitions.
"""

import pytest
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.models.schema import ScholarshipRecord, EvidenceItem
from src.models.enums import ScholarshipStatus, VerificationStatus, ProviderType
from src.database.connection import init_db
from src.database.repository import ScholarshipRepository
from src.change_detection.tracker import ChangeTracker


@pytest.fixture
def temp_repo():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
        db_path = Path(tf.name)
    init_db(db_path)
    repo = ScholarshipRepository(db_path)
    yield repo, db_path
    try:
        db_path.unlink()
    except Exception:
        pass


def test_change_detection_on_deadline_extension(temp_repo):
    repo, db_path = temp_repo
    tracker = ChangeTracker(repo)

    # Initial crawl (Run 1)
    rec1 = ScholarshipRecord(
        id="test-change-sc",
        scholarship_name="Change Detection Test Scheme",
        provider="AICTE",
        provider_type=ProviderType.GOVERNMENT_CENTRAL,
        official_source_url="https://aicte-india.org/scheme",
        application_url="https://aicte-india.org/apply",
        amount_benefit="₹50,000 per annum",
        academic_requirements="B.Tech 1st year",
        closing_date="2026-08-31",
        confidence_score=98.0,
        verification_status=VerificationStatus.VERIFIED,
    )
    is_new, changes = tracker.process_crawl_update(rec1, run_id="RUN_1")
    assert is_new is True
    assert len(changes) == 0

    # Consecutive crawl (Run 2) with deadline extension
    rec2 = ScholarshipRecord(
        id="test-change-sc",
        scholarship_name="Change Detection Test Scheme",
        provider="AICTE",
        provider_type=ProviderType.GOVERNMENT_CENTRAL,
        official_source_url="https://aicte-india.org/scheme",
        application_url="https://aicte-india.org/apply",
        amount_benefit="₹50,000 per annum",
        academic_requirements="B.Tech 1st year",
        closing_date="2026-10-15",  # Changed!
        confidence_score=98.0,
        verification_status=VerificationStatus.VERIFIED,
    )
    is_new_2, changes_2 = tracker.process_crawl_update(rec2, run_id="RUN_2")
    assert is_new_2 is False
    assert len(changes_2) >= 1
    
    deadline_change = [c for c in changes_2 if c.field_name == "closing_date"][0]
    assert deadline_change.old_value == "2026-08-31"
    assert deadline_change.new_value == "2026-10-15"
    assert deadline_change.run_id == "RUN_2"

    # Verify history in database
    history = repo.get_history("test-change-sc")
    assert len(history) >= 1
    assert history[0]["field_name"] in ("closing_date", "status")


def test_expired_scholarship_transition(temp_repo):
    repo, db_path = temp_repo
    tracker = ChangeTracker(repo)

    rec = ScholarshipRecord(
        id="test-expired-sc",
        scholarship_name="Expired Cohort Scheme",
        provider="Trust",
        provider_type=ProviderType.FOUNDATION_TRUST,
        official_source_url="https://trust.org/scheme",
        amount_benefit="₹10,000",
        academic_requirements="Graduates",
        closing_date="2025-01-01",  # Past date
        confidence_score=95.0,
        verification_status=VerificationStatus.VERIFIED,
    )
    new_status = tracker.evaluate_status_transition(rec)
    assert new_status == ScholarshipStatus.EXPIRED
