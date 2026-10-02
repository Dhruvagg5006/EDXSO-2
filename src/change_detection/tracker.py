"""
Change Detection and Lifecycle State Machine.
Tracks changes across consecutive crawls, creates audit log records in SQLite,
and transitions lifecycle statuses (ACTIVE, EXPIRING_SOON, EXPIRED, NO_LONGER_VERIFIABLE).
"""

from typing import List, Tuple, Optional
from datetime import datetime
from src.models.schema import ScholarshipRecord, ChangeLogRecord
from src.models.enums import ScholarshipStatus
from src.database.repository import ScholarshipRepository
import config


class ChangeTracker:
    """
    Detects data field modifications and manages lifecycle status transitions.
    """

    def __init__(self, repository: Optional[ScholarshipRepository] = None):
        self.repository = repository or ScholarshipRepository()

    def evaluate_status_transition(self, scholarship: ScholarshipRecord) -> ScholarshipStatus:
        """
        Determines the current lifecycle status based on temporal deadlines and verification integrity.
        """
        if scholarship.status == ScholarshipStatus.NO_LONGER_VERIFIABLE:
            return ScholarshipStatus.NO_LONGER_VERIFIABLE

        closing = scholarship.closing_date.strip()
        if closing.lower() in ("rolling", "not specified", "open year round"):
            return ScholarshipStatus.ACTIVE

        try:
            deadline_dt = datetime.strptime(closing, "%Y-%m-%d")
            today = datetime.utcnow().date()
            days_left = (deadline_dt.date() - today).days

            if days_left < 0:
                return ScholarshipStatus.EXPIRED
            elif days_left <= config.EXPIRING_SOON_DAYS:
                return ScholarshipStatus.EXPIRING_SOON
            else:
                return ScholarshipStatus.ACTIVE
        except ValueError:
            return scholarship.status

    def process_crawl_update(
        self,
        new_record: ScholarshipRecord,
        run_id: str
    ) -> Tuple[bool, List[ChangeLogRecord]]:
        """
        Evaluates lifecycle status, upserts record, and records audit trail of any field updates.
        Returns: (is_new, list_of_detected_changes)
        """
        # Update lifecycle status dynamically
        new_record.status = self.evaluate_status_transition(new_record)

        # Upsert with change tracking
        is_new, changes = self.repository.upsert_scholarship(new_record, run_id=run_id)
        return is_new, changes
