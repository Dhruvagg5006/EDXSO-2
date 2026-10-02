"""
Verification Engine Module.
Runs comprehensive evidence audits, performs reachability tests, and attaches mathematical confidence scorecards.
"""

from typing import Optional, Tuple, Any
from src.models.schema import ScholarshipRecord
from src.verification.scoring_engine import ScoringEngine


class VerificationEngine:
    """
    Coordinates scholarship authenticity verification, HTTP validation, and score calculation.
    """

    def __init__(self, fetcher: Optional[Any] = None):
        if fetcher is None:
            from src.crawler.fetcher import PageFetcher
            self.fetcher = PageFetcher()
        else:
            self.fetcher = fetcher

    def verify_scholarship(
        self,
        scholarship: ScholarshipRecord,
        page_html: Optional[str] = None,
        mock_http_status: int = 200
    ) -> ScholarshipRecord:
        """
        Validates scholarship against primary source, attaches evidence, and generates confidence score.
        """
        # Test reachability if HTML not provided
        http_status = mock_http_status
        html_content = page_html
        if html_content is None:
            code, content, _ = self.fetcher.fetch_page(scholarship.official_source_url)
            if code == 200:
                http_status = 200
                html_content = content
            else:
                http_status = code

        # Generate Explainable Scorecard
        scorecard = ScoringEngine.calculate_scorecard(
            scholarship=scholarship,
            http_status=http_status,
            page_html=html_content
        )

        scholarship.confidence_score = scorecard.total_score
        scholarship.verification_status = scorecard.verification_status
        scholarship.score_breakdown = scorecard

        return scholarship
