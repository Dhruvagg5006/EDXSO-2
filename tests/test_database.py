"""
Unit Tests for Database CRUD, Indexing, and Analytics Queries.
"""

import pytest
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.models.schema import ScholarshipRecord, EvidenceItem, CrawlRunRecord
from src.models.enums import ScholarshipStatus, VerificationStatus, ProviderType
from src.database.connection import init_db
from src.database.repository import ScholarshipRepository


@pytest.fixture
def temp_db():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
        db_path = Path(tf.name)
    init_db(db_path)
    repo = ScholarshipRepository(db_path)
    yield repo, db_path
    try:
        db_path.unlink()
    except Exception:
        pass


def test_database_upsert_and_retrieval(temp_db):
    repo, db_path = temp_db

    rec = ScholarshipRecord(
        id="db-test-sc",
        scholarship_name="DB Test Scheme",
        provider="Dept of Science",
        provider_type=ProviderType.GOVERNMENT_CENTRAL,
        official_source_url="https://dst.gov.in",
        amount_benefit="₹75,000",
        academic_requirements="B.Sc students",
        closing_date="2026-12-31",
        confidence_score=96.0,
        verification_status=VerificationStatus.VERIFIED,
        evidence_items=[
            EvidenceItem(field_name="amount_benefit", extracted_value="₹75,000", source_url="https://dst.gov.in", evidence_text="Stipend Rs 75,000")
        ]
    )

    is_new, changes = repo.upsert_scholarship(rec, run_id="TEST_RUN")
    assert is_new is True

    fetched = repo.get_scholarship("db-test-sc")
    assert fetched is not None
    assert fetched.scholarship_name == "DB Test Scheme"
    assert len(fetched.evidence_items) == 1
    assert fetched.evidence_items[0].field_name == "amount_benefit"


def test_database_analytics_metrics(temp_db):
    repo, db_path = temp_db
    metrics = repo.get_analytics_metrics()
    assert "total_discovered" in metrics
    assert "total_verified" in metrics
    assert "avg_confidence" in metrics
