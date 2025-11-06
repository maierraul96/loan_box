import pytest
from app.steps import DTIRule, AmountPolicy, RiskScoring


class TestDTIRule:
    """Test DTI Rule step"""

    def test_dti_pass(self):
        """Test DTI rule with acceptable debt ratio"""
        step = DTIRule()
        application = {
            "monthly_income": 4000,
            "declared_debts": 500
        }
        result = step.execute(application, {"max_dti": 0.40})

        assert result.passed is True
        assert result.computed_values["dti"] == 0.125
        assert "PASS" in result.message

    def test_dti_fail(self):
        """Test DTI rule with excessive debt ratio"""
        step = DTIRule()
        application = {
            "monthly_income": 2000,
            "declared_debts": 1200
        }
        result = step.execute(application, {"max_dti": 0.40})

        assert result.passed is False
        assert result.computed_values["dti"] == 0.6
        assert "FAIL" in result.message

    def test_dti_custom_threshold(self):
        """Test DTI rule with custom threshold"""
        step = DTIRule()
        application = {
            "monthly_income": 3000,
            "declared_debts": 900
        }
        result = step.execute(application, {"max_dti": 0.25})

        assert result.passed is False  # 0.3 > 0.25


class TestAmountPolicy:
    """Test Amount Policy step"""

    def test_amount_within_limit_es(self):
        """Test amount within ES limit"""
        step = AmountPolicy()
        application = {
            "amount": 12000,
            "country": "ES"
        }
        result = step.execute(application, {})

        assert result.passed is True
        assert result.computed_values["cap"] == 30000
        assert "PASS" in result.message

    def test_amount_exceeds_limit_other(self):
        """Test amount exceeds OTHER limit"""
        step = AmountPolicy()
        application = {
            "amount": 28000,
            "country": "OTHER"
        }
        result = step.execute(application, {})

        assert result.passed is False
        assert result.computed_values["cap"] == 20000
        assert "FAIL" in result.message

    def test_amount_custom_country_cap(self):
        """Test amount with custom country cap"""
        step = AmountPolicy()
        application = {
            "amount": 40000,
            "country": "US"
        }
        result = step.execute(application, {"US": 50000})

        assert result.passed is True
        assert result.computed_values["cap"] == 50000


class TestRiskScoring:
    """Test Risk Scoring step"""

    def test_risk_low_approved(self):
        """Test low risk score - should be approved"""
        step = RiskScoring()
        application = {
            "monthly_income": 4000,
            "declared_debts": 500,
            "amount": 12000,
            "country": "ES"
        }
        result = step.execute(application, {})

        # DTI = 500/4000 = 0.125
        # Risk = (0.125 * 100) + (12000/30000 * 20) = 12.5 + 8 = 20.5
        assert result.passed is True
        assert result.computed_values["risk"] == 20.5
        assert "PASS" in result.message

    def test_risk_high_rejected(self):
        """Test high risk score - should be rejected"""
        step = RiskScoring()
        application = {
            "monthly_income": 2000,
            "declared_debts": 1200,
            "amount": 28000,
            "country": "OTHER"
        }
        result = step.execute(application, {})

        # DTI = 1200/2000 = 0.6
        # Risk = (0.6 * 100) + (28000/20000 * 20) = 60 + 28 = 88
        assert result.passed is False
        assert result.computed_values["risk"] == 88.0
        assert "FAIL" in result.message

    def test_risk_custom_threshold(self):
        """Test risk scoring with custom threshold"""
        step = RiskScoring()
        application = {
            "monthly_income": 3000,
            "declared_debts": 900,
            "amount": 20000,
            "country": "FR"
        }
        result = step.execute(application, {"approve_threshold": 50})

        # DTI = 900/3000 = 0.3
        # Risk = (0.3 * 100) + (20000/25000 * 20) = 30 + 16 = 46
        assert result.passed is True  # 46 <= 50
