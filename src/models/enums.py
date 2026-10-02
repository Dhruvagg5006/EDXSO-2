"""
Enums for the Scholarship Intelligence System.
Standardizes provider classifications, application statuses, and verification levels.
"""

from enum import Enum


class ScholarshipStatus(str, Enum):
    ACTIVE = "ACTIVE"
    EXPIRING_SOON = "EXPIRING_SOON"
    EXPIRED = "EXPIRED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    NO_LONGER_VERIFIABLE = "NO_LONGER_VERIFIABLE"


class VerificationStatus(str, Enum):
    VERIFIED = "VERIFIED"
    REVIEW_REQUIRED = "REVIEW REQUIRED"


class ProviderType(str, Enum):
    GOVERNMENT_CENTRAL = "Government (Central)"
    GOVERNMENT_STATE = "Government (State)"
    CORPORATE_CSR = "Corporate CSR"
    FOUNDATION_TRUST = "Foundation / Trust"
    UNIVERSITY_RESEARCH = "University / Institution"
    AGGREGATOR = "Aggregator / Directory"


class GenderCriteria(str, Enum):
    ALL = "All"
    FEMALE = "Female Only"
    MALE = "Male Only"
    TRANSGENDER = "Transgender Included"


class SelectionProcessType(str, Enum):
    MERIT_CUM_MEANS = "Merit-cum-Means"
    MERIT_BASED = "Merit-Based (Academic/Rank)"
    APTITUDE_TEST = "Computer-Based Aptitude Test & Interview"
    INTERVIEW_DIRECT = "Direct Screening & Interview"
    NEED_BASED = "Need-Based Financial Grant"
