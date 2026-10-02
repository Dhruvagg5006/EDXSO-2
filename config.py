"""
Configuration Module for Scholarship Intelligence Crawler.
Centralizes paths, scoring thresholds, domain classification rules, and operational constants.
"""

from pathlib import Path
import os

# Base Directories
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RAW_CRAWLED_DIR = DATA_DIR / "raw_crawled"
DATABASE_PATH = DATA_DIR / "scholarships.db"
MASTER_JSON_PATH = DATA_DIR / "scholarships_master.json"

# Ensure data directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
RAW_CRAWLED_DIR.mkdir(parents=True, exist_ok=True)

# Verification & Scoring Thresholds
VERIFICATION_THRESHOLD = 95.0  # Scores >= 95.0% are labelled VERIFIED; below are REVIEW REQUIRED
EXPIRING_SOON_DAYS = 30        # Deadlines within 30 days are flagged EXPIRING_SOON

# Crawler Configuration
CRAWLER_USER_AGENT = os.getenv(
    "CRAWLER_USER_AGENT",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 (ScholarshipIntelligence/2.0)"
)
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "15"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))

# Trusted Domain Tiers for Indian Educational Opportunities
GOVERNMENT_DOMAINS = [
    ".gov.in",
    ".nic.in",
    "scholarships.gov.in",
    "aicte-india.org",
    "ugc.ac.in",
    "online-inspire.gov.in",
    "mahadbt.maharashtra.gov.in",
    "ssp.postmatric.karnataka.gov.in",
    "svmcm.wbhed.gov.in",
    "education.gov.in",
    "socialjustice.gov.in",
    "tribal.nic.in",
    "minorityaffairs.gov.in",
    "dst.gov.in",
]

ACADEMIC_INSTITUTION_DOMAINS = [
    ".ac.in",
    ".edu.in",
    "pmrf.in",
    "iisc.ac.in",
    "iitb.ac.in",
    "iitd.ac.in",
    "iitm.ac.in",
    "iitk.ac.in",
]

CORPORATE_CSR_OFFICIAL_DOMAINS = [
    "reliancefoundation.org",
    "tatatrusts.org",
    "jntataendowment.org",
    "hdfcbank.com",
    "infosys.com",
    "loreal.com",
    "adityabirlascholars.net",
    "adityabirlacapital.com",
    "sitaramjindalfoundation.org",
    "kcmet.org",
    "nsfoundation.co.in",
    "inlaksfoundation.org",
]

AGGREGATOR_DOMAINS = [
    "buddy4study.com",
    "vidyasaarathi.co.in",
    "scholarshipsindia.com",
    "shiksha.com",
    "careers360.com",
    "collegedunia.com",
    "indembassy.gov.in",
    "jagranjosh.com",
]

# Field Weightings for 100-Point Mathematical Confidence Scoring
CONFIDENCE_WEIGHTS = {
    "domain_authenticity": 25.0,     # Official primary domain vs aggregator
    "reachability_integrity": 15.0,  # Live HTTP 200 OK + Title/H1 match
    "evidence_grounding": 25.0,      # Exact DOM text match for Amount, Eligibility, Deadline
    "application_pathway": 10.0,     # Official registration/application link valid
    "temporal_validity": 15.0,       # Active/future cycle deadline vs expired
    "schema_consistency": 10.0,      # Cross-field logical consistency, zero contradictions
}
