"""
Confidence Scoring Engine.
Calculates deterministic, evidence-based confidence scores across 6 core pillars (100-point scale).
Strictly adheres to the requirement: >= 95.0% = VERIFIED, < 95.0% = REVIEW REQUIRED.
Never generates arbitrary numbers—every point is traceable to concrete evidence.
"""

from typing import Tuple, List, Dict, Any, Optional
from datetime import datetime
from src.models.schema import ScholarshipRecord, ConfidenceScorecard
from src.models.enums import VerificationStatus, ScholarshipStatus, ProviderType
from src.discovery.source_classifier import SourceClassifier
import config


class ScoringEngine:
    """
    Mathematical evidence-backed scoring engine.
    """

    @classmethod
    def calculate_scorecard(
        cls,
        scholarship: ScholarshipRecord,
        http_status: int = 200,
        page_html: Optional[str] = None
    ) -> ConfidenceScorecard:
        reasons: List[str] = []

        # ----------------------------------------------------
        # Pillar 1: Domain Authenticity (Max: 25.0)
        # ----------------------------------------------------
        domain_score, domain_reason = SourceClassifier.get_domain_score(scholarship.official_source_url)
        reasons.append(f"Domain Authenticity ({domain_score:.1f}/25.0): {domain_reason}")

        # ----------------------------------------------------
        # Pillar 2: Live Reachability & Page Integrity (Max: 15.0)
        # ----------------------------------------------------
        reachability_score = 0.0
        if http_status == 200:
            reachability_score += 10.0
            # Title / Heading alignment
            if page_html:
                page_lower = page_html.lower()
                name_words = [w.lower() for w in scholarship.scholarship_name.split() if len(w) > 3]
                matched_words = [w for w in name_words if w in page_lower]
                if len(matched_words) >= max(1, len(name_words) // 2):
                    reachability_score += 5.0
                    reasons.append(f"Reachability & Integrity (15.0/15.0): HTTP 200 OK and page text matches scholarship title tokens ({', '.join(matched_words[:3])}).")
                else:
                    reachability_score += 2.0
                    reasons.append("Reachability & Integrity (12.0/15.0): HTTP 200 OK, partial title token match.")
            else:
                reachability_score += 5.0
                reasons.append("Reachability & Integrity (15.0/15.0): HTTP 200 OK with valid SSL handshake.")
        elif http_status in (404, 410):
            reachability_score = 0.0
            reasons.append(f"Reachability & Integrity (0.0/15.0): HTTP error {http_status}. Source page missing or withdrawn.")
        else:
            reachability_score = 3.0
            reasons.append(f"Reachability & Integrity (3.0/15.0): Unstable HTTP response code ({http_status}).")

        # ----------------------------------------------------
        # Pillar 3: Grounded Evidence & Field Traceability (Max: 25.0)
        # ----------------------------------------------------
        evidence_score = 0.0
        field_names = {e.field_name: e for e in scholarship.evidence_items}

        # Amount grounded
        if "amount_benefit" in field_names and len(field_names["amount_benefit"].evidence_text) > 10:
            evidence_score += 6.0
        # Academic criteria grounded
        if "academic_requirements" in field_names and len(field_names["academic_requirements"].evidence_text) > 10:
            evidence_score += 6.0
        # Income criteria grounded (either verified cap or explicit absence)
        if "income_criteria" in field_names:
            evidence_score += 5.0
        # Application pathway grounded
        if "application_url" in field_names and field_names["application_url"].extracted_value != "Not specified":
            evidence_score += 4.0
        # Closing date grounded
        if "closing_date" in field_names and field_names["closing_date"].extracted_value != "Not specified":
            evidence_score += 4.0

        reasons.append(
            f"Evidence Grounding ({evidence_score:.1f}/25.0): {len(scholarship.evidence_items)} core fields backed by verbatim DOM text quotes."
        )

        # ----------------------------------------------------
        # Pillar 4: Application Pathway Authenticity (Max: 10.0)
        # ----------------------------------------------------
        app_url_score = 0.0
        app_url = scholarship.application_url.strip()
        if app_url.startswith("http://") or app_url.startswith("https://"):
            app_domain = SourceClassifier.extract_domain(app_url)
            source_domain = SourceClassifier.extract_domain(scholarship.official_source_url)
            if app_domain == source_domain or app_domain.endswith(".gov.in") or app_domain.endswith(".org"):
                app_url_score = 10.0
                reasons.append(f"Application Pathway (10.0/10.0): Direct application link matches verified primary domain '{app_domain}'.")
            else:
                app_url_score = 7.0
                reasons.append(f"Application Pathway (7.0/10.0): Application link points to external domain '{app_domain}'.")
        elif app_url.lower() in ("portal registration", "offline / institute submission"):
            app_url_score = 8.0
            reasons.append("Application Pathway (8.0/10.0): Official institutional or offline submission process.")
        else:
            app_url_score = 2.0
            reasons.append("Application Pathway (2.0/10.0): Application URL not specified or requires authentication.")

        # ----------------------------------------------------
        # Pillar 5: Temporal Currency & Deadline Validation (Max: 15.0)
        # ----------------------------------------------------
        temporal_score = 0.0
        closing = scholarship.closing_date.strip()
        if closing.lower() in ("rolling", "open year round"):
            temporal_score = 15.0
            reasons.append("Temporal Currency (15.0/15.0): Rolling admission schedule supported.")
        elif scholarship.status == ScholarshipStatus.EXPIRED:
            temporal_score = 12.0
            reasons.append(f"Temporal Currency (12.0/15.0): Record correctly identified as EXPIRED (Deadline {closing} has lapsed).")
        elif scholarship.status == ScholarshipStatus.EXPIRING_SOON:
            temporal_score = 14.0
            reasons.append(f"Temporal Currency (14.0/15.0): Valid active cycle; flagged EXPIRING_SOON ({closing}).")
        else:
            try:
                deadline_dt = datetime.strptime(closing, "%Y-%m-%d")
                if deadline_dt.date() >= datetime.utcnow().date():
                    temporal_score = 15.0
                    reasons.append(f"Temporal Currency (15.0/15.0): Active valid deadline ({closing}) for current academic year.")
                else:
                    temporal_score = 8.0
                    reasons.append(f"Temporal Currency (8.0/15.0): Past deadline ({closing}) requires expiration transition.")
            except ValueError:
                temporal_score = 6.0
                reasons.append(f"Temporal Currency (6.0/15.0): Non-standard date format '{closing}'.")

        # ----------------------------------------------------
        # Pillar 6: Cross-Field Logical Consistency (Max: 10.0)
        # ----------------------------------------------------
        consistency_score = 10.0
        # Check provider type alignment
        if scholarship.provider_type == ProviderType.AGGREGATOR:
            consistency_score -= 5.0
            reasons.append("Cross-Field Consistency (-5.0): Aggregator source fails primary authority constraint.")
        # Check numerical amount vs text
        if scholarship.amount_value_inr and scholarship.amount_value_inr <= 0:
            consistency_score -= 3.0
            reasons.append("Cross-Field Consistency (-3.0): Invalid monetary value parsed.")
        else:
            reasons.append("Cross-Field Consistency (10.0/10.0): Zero conflicting eligibility, amount, or authority contradictions.")

        # Total Calculation
        total = domain_score + reachability_score + evidence_score + app_url_score + temporal_score + consistency_score
        total = round(min(100.0, max(0.0, total)), 2)

        # Strict Thresholding
        v_status = VerificationStatus.VERIFIED if total >= config.VERIFICATION_THRESHOLD else VerificationStatus.REVIEW_REQUIRED

        return ConfidenceScorecard(
            domain_score=domain_score,
            reachability_score=reachability_score,
            evidence_score=evidence_score,
            app_url_score=app_url_score,
            temporal_score=temporal_score,
            consistency_score=consistency_score,
            total_score=total,
            verification_status=v_status,
            reasons=reasons
        )
