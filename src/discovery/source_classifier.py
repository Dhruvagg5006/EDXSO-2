"""
Source Classification Engine.
Determines domain authority, official status, and provider categories.
Distinguishes between official primary sources and secondary aggregators.
"""

from urllib.parse import urlparse
from typing import Tuple, Dict, Any
from src.models.enums import ProviderType
import config


class SourceClassifier:
    """
    Classifies web URLs into trusted source tiers and validates primary authenticity.
    """

    @staticmethod
    def extract_domain(url: str) -> str:
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            if domain.startswith("www."):
                domain = domain[4:]
            return domain
        except Exception:
            return ""

    @classmethod
    def classify_source(cls, url: str, provider_hint: str = "") -> Tuple[ProviderType, bool, str]:
        """
        Classifies URL into ProviderType, whether it is an official primary source, and an explanation.
        Returns: (ProviderType, is_official, justification)
        """
        domain = cls.extract_domain(url)
        url_lower = url.lower()
        provider_lower = provider_hint.lower()

        # 1. Check Aggregators first
        for agg in config.AGGREGATOR_DOMAINS:
            if agg in domain:
                return (
                    ProviderType.AGGREGATOR,
                    False,
                    f"Secondary aggregator / directory domain '{domain}'. Must be resolved to primary official source."
                )

        # 2. State Government Portals
        state_gov_signatures = [
            "mahadbt", "karnataka.gov.in", "wbhed.gov.in", "up.gov.in",
            "kerala.gov.in", "rajasthan.gov.in", "gujarat.gov.in", "bihar.gov.in"
        ]
        if any(sig in domain for sig in state_gov_signatures):
            return (
                ProviderType.GOVERNMENT_STATE,
                True,
                f"Authoritative State Government portal on official domain '{domain}'."
            )

        # 3. Central Government Portals & Statutory Bodies
        if any(gov in domain for gov in config.GOVERNMENT_DOMAINS):
            return (
                ProviderType.GOVERNMENT_CENTRAL,
                True,
                f"Authoritative Central Government / Statutory body domain '{domain}'."
            )

        # 4. Academic & Research Institutions
        if any(acad in domain for acad in config.ACADEMIC_INSTITUTION_DOMAINS):
            return (
                ProviderType.UNIVERSITY_RESEARCH,
                True,
                f"Accredited Higher Education / Research Institution domain '{domain}'."
            )

        # 5. Corporate CSR Portals
        corporate_csr_keywords = [
            "reliancefoundation", "tatatrusts", "hdfcbank", "infosys",
            "loreal", "adityabirla", "sitaramjindal"
        ]
        if any(corp in domain for corp in corporate_csr_keywords):
            return (
                ProviderType.CORPORATE_CSR,
                True,
                f"Verified Corporate CSR official organization domain '{domain}'."
            )

        # 6. Foundations & Philanthropic Trusts
        foundation_keywords = ["kcmet", "nsfoundation", "inlaks", "jntata", "azimpremjifoundation"]
        if any(fnd in domain for fnd in foundation_keywords):
            return (
                ProviderType.FOUNDATION_TRUST,
                True,
                f"Registered Philanthropic Foundation / Trust official domain '{domain}'."
            )

        # Fallback heuristic
        if domain.endswith(".org") or domain.endswith(".org.in") or domain.endswith(".in"):
            if "trust" in provider_lower or "foundation" in provider_lower:
                return (
                    ProviderType.FOUNDATION_TRUST,
                    True,
                    f"Official organizational domain '{domain}' for registered trust/foundation."
                )
            if "university" in provider_lower or "institute" in provider_lower:
                return (
                    ProviderType.UNIVERSITY_RESEARCH,
                    True,
                    f"Academic institution domain '{domain}'."
                )

        return (
            ProviderType.AGGREGATOR,
            False,
            f"Unverified external domain '{domain}'. Manual verification recommended."
        )

    @classmethod
    def get_domain_score(cls, url: str) -> Tuple[float, str]:
        """
        Calculates the domain authenticity score (0 to 25 points) for the confidence scorecard.
        """
        provider_type, is_official, reason = cls.classify_source(url)
        if not is_official:
            return 5.0, f"Third-party aggregator domain ({reason}). Max score capped."

        domain = cls.extract_domain(url)
        if ".gov.in" in domain or ".nic.in" in domain or domain in config.GOVERNMENT_DOMAINS:
            return 25.0, f"Premier tier official government domain ({domain}). Authentic primary source."
        elif domain in config.ACADEMIC_INSTITUTION_DOMAINS or ".ac.in" in domain:
            return 25.0, f"Accredited academic university/institute domain ({domain}). Official primary source."
        elif provider_type in (ProviderType.CORPORATE_CSR, ProviderType.FOUNDATION_TRUST):
            return 25.0, f"Verified official corporate CSR/foundation organizational domain ({domain})."
        else:
            return 20.0, f"Recognized organizational portal ({domain})."
