"""
Discovery Engine.
Discovers scholarship opportunities across government portals, corporate foundations,
universities, and resolves secondary aggregator links to primary official sources.
"""

import json
from typing import List, Dict, Any, Optional
from pathlib import Path
from src.discovery.source_classifier import SourceClassifier
from src.models.enums import ProviderType
import config


class DiscoveryEngine:
    """
    Coordinates scholarship source discovery, seed registry, and primary source resolution.
    """

    def __init__(self, seeds_file: Optional[Path] = None):
        self.seeds_file = seeds_file or (config.DATA_DIR / "seeds.json")
        self.seeds: List[Dict[str, Any]] = []
        self._load_seeds()

    def _load_seeds(self) -> None:
        if self.seeds_file.exists():
            try:
                with open(self.seeds_file, "r", encoding="utf-8") as f:
                    self.seeds = json.load(f)
                    return
            except Exception:
                pass
        self.seeds = self._get_default_seeds()
        self._save_seeds()

    def _save_seeds(self) -> None:
        self.seeds_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.seeds_file, "w", encoding="utf-8") as f:
            json.dump(self.seeds, f, indent=2)

    def _get_default_seeds(self) -> List[Dict[str, Any]]:
        return [
            # 1. Government (Central & Ministries)
            {
                "id": "nsp-central-portal",
                "name": "National Scholarship Portal (Central Ministry Schemes)",
                "url": "https://scholarships.gov.in",
                "category": "Government (Central)",
                "active": True
            },
            {
                "id": "aicte-schemes",
                "name": "AICTE Student Development Schemes Portal",
                "url": "https://www.aicte-india.org/schemes/students-development-schemes",
                "category": "Government (Central)",
                "active": True
            },
            {
                "id": "dst-inspire-portal",
                "name": "Department of Science and Technology INSPIRE Portal",
                "url": "https://online-inspire.gov.in",
                "category": "Government (Central)",
                "active": True
            },
            {
                "id": "pmrf-fellowship-portal",
                "name": "Prime Minister's Research Fellowship (PMRF) Portal",
                "url": "https://www.pmrf.in",
                "category": "Government (Central)",
                "active": True
            },
            # 2. Government (State Portals)
            {
                "id": "mahadbt-state-portal",
                "name": "MahaDBT Maharashtra State Scholarship Portal",
                "url": "https://mahadbt.maharashtra.gov.in",
                "category": "Government (State)",
                "active": True
            },
            {
                "id": "karnataka-ssp-portal",
                "name": "Karnataka State Scholarship Portal (SSP)",
                "url": "https://ssp.postmatric.karnataka.gov.in",
                "category": "Government (State)",
                "active": True
            },
            {
                "id": "wb-svmcm-portal",
                "name": "Swami Vivekananda Merit-cum-Means Portal (WB)",
                "url": "https://svmcm.wbhed.gov.in",
                "category": "Government (State)",
                "active": True
            },
            # 3. Corporate CSR Programs
            {
                "id": "reliance-foundation-scholarships",
                "name": "Reliance Foundation Scholarships Portal",
                "url": "https://www.scholarships.reliancefoundation.org",
                "category": "Corporate CSR",
                "active": True
            },
            {
                "id": "tata-trusts-grants",
                "name": "Tata Trusts Education Grants Portal",
                "url": "https://www.tatatrusts.org/our-work/individual-grants-programme/education-grants",
                "category": "Corporate CSR",
                "active": True
            },
            {
                "id": "hdfc-parivartan-portal",
                "name": "HDFC Bank Parivartan's ECSS Official Portal",
                "url": "https://www.hdfcbank.com/personal/about-us/corporate-social-responsibility/parivartan/educational-crisis-scholarship-support",
                "category": "Corporate CSR",
                "active": True
            },
            {
                "id": "infosys-stem-stars",
                "name": "Infosys Foundation STEM Stars Scholarship",
                "url": "https://www.infosys.com/infosys-foundation/initiatives/education/stem-stars.html",
                "category": "Corporate CSR",
                "active": True
            },
            {
                "id": "loreal-for-women-in-science",
                "name": "L'Oréal India For Young Women In Science",
                "url": "https://www.loreal.com/en/india/articles/commitments/for-women-in-science-india",
                "category": "Corporate CSR",
                "active": True
            },
            {
                "id": "aditya-birla-scholars",
                "name": "Aditya Birla Group Scholarship Program",
                "url": "https://www.adityabirlascholars.net",
                "category": "Corporate CSR",
                "active": True
            },
            {
                "id": "sitaram-jindal-foundation",
                "name": "Sitaram Jindal Foundation Scholarship Scheme",
                "url": "https://www.sitaramjindalfoundation.org/scholarships.php",
                "category": "Corporate CSR",
                "active": True
            },
            # 4. Foundations & Trusts
            {
                "id": "kc-mahindra-trust",
                "name": "K. C. Mahindra Education Trust Postgraduate Scholarships",
                "url": "https://www.kcmet.org/what-we-do-scholarships.aspx",
                "category": "Foundation / Trust",
                "active": True
            },
            {
                "id": "narotam-sekhsaria-foundation",
                "name": "Narotam Sekhsaria Foundation PG Scholarships",
                "url": "https://pg.nsfoundation.co.in",
                "category": "Foundation / Trust",
                "active": True
            },
            {
                "id": "inlaks-shivdasani-foundation",
                "name": "Inlaks Shivdasani Foundation Scholarships",
                "url": "https://www.inlaksfoundation.org/scholarships/opportunities",
                "category": "Foundation / Trust",
                "active": True
            },
            {
                "id": "jn-tata-endowment",
                "name": "J. N. Tata Endowment for Higher Education of Indians",
                "url": "https://www.jntataendowment.org/loan-scholarship",
                "category": "Foundation / Trust",
                "active": True
            },
            # 5. Universities / Research Institutions
            {
                "id": "iisc-fellowships",
                "name": "IISc Integrated PhD & M.Tech Research Fellowships",
                "url": "https://iisc.ac.in/admissions/financial-support",
                "category": "University / Institution",
                "active": True
            },
            {
                "id": "iitb-merit-cum-means",
                "name": "IIT Bombay Merit-cum-Means (MCM) Scholarship",
                "url": "https://www.iitb.ac.in/newacadhome/scholarship.jsp",
                "category": "University / Institution",
                "active": True
            }
        ]

    def list_seeds(self) -> List[Dict[str, Any]]:
        return self.seeds

    def resolve_aggregator_to_official(self, aggregator_url: str, page_html_or_text: str = "") -> Optional[str]:
        """
        Demonstrates aggregator link resolution:
        If an opportunity was found on Buddy4Study / Vidyasaarathi / Vikaspedia,
        inspects outbound domain references or redirect patterns to identify the authoritative primary URL.
        """
        # Look for known official domains embedded in anchor text or description
        for gov in config.GOVERNMENT_DOMAINS:
            if gov in page_html_or_text:
                return f"https://{gov}"
        for corp in config.CORPORATE_CSR_OFFICIAL_DOMAINS:
            if corp in page_html_or_text:
                return f"https://www.{corp}"
        return None
