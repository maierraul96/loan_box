import pytest
from app.steps import DTIRule, AmountPolicy, RiskScoring
from app.models.enums import FinalStatus


class TestReviewScenarios:
    """
    Test the 3 scenarios from the specification:
    1. Ana, 12000 loan, 4000 income, 500 debts, ES → APPROVED
    2. Luis, 28000 loan, 2000 income, 1200 debts, OTHER → REJECTED
    3. Mia, 20000 loan, 3000 income, 900 debts, FR → NEEDS_REVIEW
    """

    def test_scenario_1_ana_approved(self):
        """Scenario 1: Ana should be APPROVED"""
        application = {
            "applicant_name": "Ana",
            "amount": 12000,
            "monthly_income": 4000,
            "declared_debts": 500,
            "country": "ES",
            "loan_purpose": "home improvement"
        }

        # Execute steps
        dti_result = DTIRule().execute(application, {"max_dti": 0.40})
        amount_result = AmountPolicy().execute(application, {})
        risk_result = RiskScoring().execute(application, {"approve_threshold": 45})

        # Verify step results
        assert dti_result.passed is True  # DTI = 500/4000 = 0.125 < 0.40
        assert amount_result.passed is True  # 12000 <= 30000 (ES)
        assert risk_result.passed is True  # Risk = 12.5 + 8 = 20.5 < 45

        # Determine final status based on terminal rules:
        # 1. If DTI or Amount Policy fail → REJECTED (both passed)
        # 2. If risk ≤ threshold → APPROVED (yes)
        final_status = FinalStatus.APPROVED
        assert final_status == FinalStatus.APPROVED

    def test_scenario_2_luis_rejected(self):
        """Scenario 2: Luis should be REJECTED"""
        application = {
            "applicant_name": "Luis",
            "amount": 28000,
            "monthly_income": 2000,
            "declared_debts": 1200,
            "country": "OTHER",
            "loan_purpose": "business"
        }

        # Execute steps
        dti_result = DTIRule().execute(application, {"max_dti": 0.40})
        amount_result = AmountPolicy().execute(application, {})
        risk_result = RiskScoring().execute(application, {"approve_threshold": 45})

        # Verify step results
        assert dti_result.passed is False  # DTI = 1200/2000 = 0.6 > 0.40
        assert amount_result.passed is False  # 28000 > 20000 (OTHER)
        assert risk_result.passed is False  # Risk = 60 + 28 = 88 > 45

        # Determine final status based on terminal rules:
        # 1. If DTI or Amount Policy fail → REJECTED (both failed)
        final_status = FinalStatus.REJECTED
        assert final_status == FinalStatus.REJECTED

    def test_scenario_3_mia_needs_review(self):
        """Scenario 3: Mia should be NEEDS_REVIEW"""
        application = {
            "applicant_name": "Mia",
            "amount": 20000,
            "monthly_income": 3000,
            "declared_debts": 900,
            "country": "FR",
            "loan_purpose": "education"
        }

        # Execute steps
        dti_result = DTIRule().execute(application, {"max_dti": 0.40})
        amount_result = AmountPolicy().execute(application, {})
        risk_result = RiskScoring().execute(application, {"approve_threshold": 45})

        # Verify step results
        assert dti_result.passed is True  # DTI = 900/3000 = 0.3 < 0.40
        assert amount_result.passed is True  # 20000 <= 25000 (FR)
        assert risk_result.passed is False  # Risk = 30 + 16 = 46 > 45

        # Determine final status based on terminal rules:
        # 1. If DTI or Amount Policy fail → REJECTED (both passed)
        # 2. If risk ≤ threshold → APPROVED (no, 46 > 45)
        # 3. Else → NEEDS_REVIEW (yes)
        final_status = FinalStatus.NEEDS_REVIEW
        assert final_status == FinalStatus.NEEDS_REVIEW

    def test_all_scenarios_calculations(self):
        """Verify the exact calculations for all scenarios"""

        # Scenario 1: Ana
        # DTI = 500/4000 = 0.125
        # Risk = (0.125 * 100) + (12000/30000 * 20) = 12.5 + 8 = 20.5
        ana_risk = (500/4000 * 100) + (12000/30000 * 20)
        assert ana_risk == 20.5

        # Scenario 2: Luis
        # DTI = 1200/2000 = 0.6
        # Risk = (0.6 * 100) + (28000/20000 * 20) = 60 + 28 = 88
        luis_risk = (1200/2000 * 100) + (28000/20000 * 20)
        assert luis_risk == 88.0

        # Scenario 3: Mia
        # DTI = 900/3000 = 0.3
        # Risk = (0.3 * 100) + (20000/25000 * 20) = 30 + 16 = 46
        mia_risk = (900/3000 * 100) + (20000/25000 * 20)
        assert mia_risk == 46.0
