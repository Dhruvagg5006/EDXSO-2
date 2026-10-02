"""
Repository Layer for SQLite operations.
Provides transactional CRUD, change tracking, evidence retrieval, and analytical queries.
"""

import json
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from src.database.connection import get_db_connection
from src.models.schema import ScholarshipRecord, EvidenceItem, ChangeLogRecord, CrawlRunRecord, ConfidenceScorecard
from src.models.enums import ScholarshipStatus, VerificationStatus, ProviderType


class ScholarshipRepository:
    def __init__(self, db_path=None):
        self.db_path = db_path

    def upsert_scholarship(
        self, scholarship: ScholarshipRecord, run_id: Optional[str] = None
    ) -> Tuple[bool, List[ChangeLogRecord]]:
        """
        Upserts a scholarship record.
        If record already exists, compares fields and logs changes in scholarship_history.
        Returns: (is_new, list_of_detected_changes)
        """
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        now = datetime.utcnow().isoformat()
        detected_changes: List[ChangeLogRecord] = []
        is_new = False

        # Check existing record
        cursor.execute("SELECT * FROM scholarships WHERE id = ?", (scholarship.id,))
        existing = cursor.fetchone()

        if existing is None:
            is_new = True
            cursor.execute("""
            INSERT INTO scholarships (
                id, scholarship_name, provider, provider_type, official_source_url,
                application_url, amount_benefit, amount_value_inr, academic_requirements,
                course_level, income_criteria, income_limit_inr, age_criteria,
                gender_criteria, category_criteria, domicile_state, institution_requirements,
                opening_date, closing_date, documents_required, selection_process,
                renewal_requirements, status, confidence_score, verification_status,
                score_breakdown, last_verified_at, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                scholarship.id,
                scholarship.scholarship_name,
                scholarship.provider,
                scholarship.provider_type.value if hasattr(scholarship.provider_type, 'value') else scholarship.provider_type,
                scholarship.official_source_url,
                scholarship.application_url,
                scholarship.amount_benefit,
                scholarship.amount_value_inr,
                scholarship.academic_requirements,
                json.dumps(scholarship.course_level),
                scholarship.income_criteria,
                scholarship.income_limit_inr,
                scholarship.age_criteria,
                scholarship.gender_criteria.value if hasattr(scholarship.gender_criteria, 'value') else scholarship.gender_criteria,
                scholarship.category_criteria,
                scholarship.domicile_state,
                scholarship.institution_requirements,
                scholarship.opening_date,
                scholarship.closing_date,
                json.dumps(scholarship.documents_required),
                scholarship.selection_process,
                scholarship.renewal_requirements,
                scholarship.status.value if hasattr(scholarship.status, 'value') else scholarship.status,
                scholarship.confidence_score,
                scholarship.verification_status.value if hasattr(scholarship.verification_status, 'value') else scholarship.verification_status,
                json.dumps(scholarship.score_breakdown.dict()) if scholarship.score_breakdown else None,
                scholarship.last_verified_at,
                now,
                now
            ))
        else:
            # Check for changes in tracked critical fields
            fields_to_track = [
                ("closing_date", existing["closing_date"], scholarship.closing_date),
                ("amount_benefit", existing["amount_benefit"], scholarship.amount_benefit),
                ("income_criteria", existing["income_criteria"], scholarship.income_criteria),
                ("academic_requirements", existing["academic_requirements"], scholarship.academic_requirements),
                ("application_url", existing["application_url"], scholarship.application_url),
                ("status", existing["status"], scholarship.status.value if hasattr(scholarship.status, 'value') else scholarship.status),
            ]

            for field_name, old_val, new_val in fields_to_track:
                if str(old_val).strip() != str(new_val).strip():
                    change_rec = ChangeLogRecord(
                        scholarship_id=scholarship.id,
                        field_name=field_name,
                        old_value=str(old_val),
                        new_value=str(new_val),
                        detected_at=now,
                        source_url=scholarship.official_source_url,
                        evidence_text=f"Detected change in {field_name} during crawl run {run_id or 'adhoc'}",
                        run_id=run_id or "RUN_MANUAL"
                    )
                    detected_changes.append(change_rec)
                    cursor.execute("""
                    INSERT INTO scholarship_history (
                        scholarship_id, field_name, old_value, new_value, detected_at, source_url, evidence_text, run_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        change_rec.scholarship_id,
                        change_rec.field_name,
                        change_rec.old_value,
                        change_rec.new_value,
                        change_rec.detected_at,
                        change_rec.source_url,
                        change_rec.evidence_text,
                        change_rec.run_id
                    ))

            # Update existing record
            cursor.execute("""
            UPDATE scholarships SET
                scholarship_name = ?,
                provider = ?,
                provider_type = ?,
                official_source_url = ?,
                application_url = ?,
                amount_benefit = ?,
                amount_value_inr = ?,
                academic_requirements = ?,
                course_level = ?,
                income_criteria = ?,
                income_limit_inr = ?,
                age_criteria = ?,
                gender_criteria = ?,
                category_criteria = ?,
                domicile_state = ?,
                institution_requirements = ?,
                opening_date = ?,
                closing_date = ?,
                documents_required = ?,
                selection_process = ?,
                renewal_requirements = ?,
                status = ?,
                confidence_score = ?,
                verification_status = ?,
                score_breakdown = ?,
                last_verified_at = ?,
                updated_at = ?
            WHERE id = ?
            """, (
                scholarship.scholarship_name,
                scholarship.provider,
                scholarship.provider_type.value if hasattr(scholarship.provider_type, 'value') else scholarship.provider_type,
                scholarship.official_source_url,
                scholarship.application_url,
                scholarship.amount_benefit,
                scholarship.amount_value_inr,
                scholarship.academic_requirements,
                json.dumps(scholarship.course_level),
                scholarship.income_criteria,
                scholarship.income_limit_inr,
                scholarship.age_criteria,
                scholarship.gender_criteria.value if hasattr(scholarship.gender_criteria, 'value') else scholarship.gender_criteria,
                scholarship.category_criteria,
                scholarship.domicile_state,
                scholarship.institution_requirements,
                scholarship.opening_date,
                scholarship.closing_date,
                json.dumps(scholarship.documents_required),
                scholarship.selection_process,
                scholarship.renewal_requirements,
                scholarship.status.value if hasattr(scholarship.status, 'value') else scholarship.status,
                scholarship.confidence_score,
                scholarship.verification_status.value if hasattr(scholarship.verification_status, 'value') else scholarship.verification_status,
                json.dumps(scholarship.score_breakdown.dict()) if scholarship.score_breakdown else None,
                scholarship.last_verified_at,
                now,
                scholarship.id
            ))

        # Refresh Evidence
        cursor.execute("DELETE FROM scholarship_evidence WHERE scholarship_id = ?", (scholarship.id,))
        for ev in scholarship.evidence_items:
            cursor.execute("""
            INSERT INTO scholarship_evidence (
                scholarship_id, field_name, extracted_value, source_url, evidence_text, match_score, verified_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                scholarship.id,
                ev.field_name,
                ev.extracted_value,
                ev.source_url,
                ev.evidence_text,
                ev.match_score,
                ev.verified_at
            ))

        conn.commit()
        conn.close()
        return is_new, detected_changes

    def get_scholarship(self, scholarship_id: str) -> Optional[ScholarshipRecord]:
        """
        Retrieves a complete scholarship record with evidence and score breakdown.
        """
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM scholarships WHERE id = ?", (scholarship_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return None

        # Fetch evidence
        cursor.execute("SELECT * FROM scholarship_evidence WHERE scholarship_id = ?", (scholarship_id,))
        evidence_rows = cursor.fetchall()
        evidence_items = [
            EvidenceItem(
                field_name=e["field_name"],
                extracted_value=e["extracted_value"],
                source_url=e["source_url"],
                evidence_text=e["evidence_text"],
                match_score=e["match_score"],
                verified_at=e["verified_at"]
            )
            for e in evidence_rows
        ]

        score_breakdown = None
        if row["score_breakdown"]:
            try:
                score_breakdown = ConfidenceScorecard(**json.loads(row["score_breakdown"]))
            except Exception:
                pass

        record = ScholarshipRecord(
            id=row["id"],
            scholarship_name=row["scholarship_name"],
            provider=row["provider"],
            provider_type=ProviderType(row["provider_type"]),
            official_source_url=row["official_source_url"],
            application_url=row["application_url"],
            amount_benefit=row["amount_benefit"],
            amount_value_inr=row["amount_value_inr"],
            academic_requirements=row["academic_requirements"],
            course_level=json.loads(row["course_level"]),
            income_criteria=row["income_criteria"],
            income_limit_inr=row["income_limit_inr"],
            age_criteria=row["age_criteria"],
            gender_criteria=row["gender_criteria"],
            category_criteria=row["category_criteria"],
            domicile_state=row["domicile_state"],
            institution_requirements=row["institution_requirements"],
            opening_date=row["opening_date"],
            closing_date=row["closing_date"],
            documents_required=json.loads(row["documents_required"]),
            selection_process=row["selection_process"],
            renewal_requirements=row["renewal_requirements"],
            status=ScholarshipStatus(row["status"]),
            confidence_score=row["confidence_score"],
            verification_status=VerificationStatus(row["verification_status"]),
            score_breakdown=score_breakdown,
            last_verified_at=row["last_verified_at"],
            evidence_items=evidence_items
        )
        conn.close()
        return record

    def list_scholarships(
        self,
        status: Optional[str] = None,
        provider_type: Optional[str] = None,
        verification_status: Optional[str] = None,
        min_confidence: Optional[float] = None,
        search_query: Optional[str] = None
    ) -> List[ScholarshipRecord]:
        """
        Lists scholarships matching filter parameters.
        """
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()

        query = "SELECT id FROM scholarships WHERE 1=1"
        params = []

        if status and status != "All":
            query += " AND status = ?"
            params.append(status)
        if provider_type and provider_type != "All":
            query += " AND provider_type = ?"
            params.append(provider_type)
        if verification_status and verification_status != "All":
            query += " AND verification_status = ?"
            params.append(verification_status)
        if min_confidence is not None:
            query += " AND confidence_score >= ?"
            params.append(min_confidence)
        if search_query:
            query += " AND (scholarship_name LIKE ? OR provider LIKE ? OR academic_requirements LIKE ?)"
            term = f"%{search_query}%"
            params.extend([term, term, term])

        query += " ORDER BY confidence_score DESC, updated_at DESC"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        records = []
        for r in rows:
            sc = self.get_scholarship(r["id"])
            if sc:
                records.append(sc)
        return records

    def get_history(self, scholarship_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieves change history records.
        """
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        if scholarship_id:
            cursor.execute("""
            SELECT h.*, s.scholarship_name
            FROM scholarship_history h
            JOIN scholarships s ON h.scholarship_id = s.id
            WHERE h.scholarship_id = ?
            ORDER BY h.detected_at DESC
            """, (scholarship_id,))
        else:
            cursor.execute("""
            SELECT h.*, s.scholarship_name
            FROM scholarship_history h
            JOIN scholarships s ON h.scholarship_id = s.id
            ORDER BY h.detected_at DESC
            """)
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def record_crawl_run(self, run: CrawlRunRecord) -> None:
        """
        Logs a completed crawl run.
        """
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
        INSERT OR REPLACE INTO crawl_runs (
            run_id, run_type, started_at, completed_at, total_discovered,
            total_verified, total_review_required, total_changes_detected,
            total_expired_detected, log_summary
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            run.run_id,
            run.run_type,
            run.started_at,
            run.completed_at,
            run.total_discovered,
            run.total_verified,
            run.total_review_required,
            run.total_changes_detected,
            run.total_expired_detected,
            run.log_summary
        ))
        conn.commit()
        conn.close()

    def get_crawl_runs(self) -> List[Dict[str, Any]]:
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM crawl_runs ORDER BY started_at DESC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_analytics_metrics(self) -> Dict[str, Any]:
        """
        Computes high-level KPI metrics for the Atlas dashboard.
        """
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM scholarships")
        total_discovered = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM scholarships WHERE verification_status = 'VERIFIED'")
        total_verified = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM scholarships WHERE verification_status = 'REVIEW REQUIRED'")
        total_review_required = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM scholarships WHERE status = 'ACTIVE'")
        total_active = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM scholarships WHERE status = 'EXPIRING_SOON'")
        total_expiring_soon = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM scholarships WHERE status = 'EXPIRED'")
        total_expired = cursor.fetchone()[0]

        cursor.execute("SELECT AVG(confidence_score) FROM scholarships")
        avg_score_row = cursor.fetchone()[0]
        avg_confidence = round(float(avg_score_row), 1) if avg_score_row else 0.0

        cursor.execute("SELECT COUNT(*) FROM scholarship_history")
        total_changes = cursor.fetchone()[0]

        cursor.execute("SELECT DISTINCT provider_type FROM scholarships")
        distinct_types = [r[0] for r in cursor.fetchall()]

        conn.close()
        return {
            "total_discovered": total_discovered,
            "total_verified": total_verified,
            "total_review_required": total_review_required,
            "total_active": total_active,
            "total_expiring_soon": total_expiring_soon,
            "total_expired": total_expired,
            "avg_confidence": avg_confidence,
            "total_changes": total_changes,
            "source_types_count": len(distinct_types),
            "source_types": distinct_types,
        }
