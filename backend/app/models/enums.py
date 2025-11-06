from enum import Enum


class FinalStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    NEEDS_REVIEW = "NEEDS_REVIEW"


class StepType(str, Enum):
    DTI_RULE = "dti_rule"
    AMOUNT_POLICY = "amount_policy"
    RISK_SCORING = "risk_scoring"
    SENTIMENT_CHECK = "sentiment_check"
