from typing import Dict, Any
from app.steps.base import BaseStep, StepResult


class RiskScoring(BaseStep):
    """
    Risk Scoring
    Combine previous checks into a simple risk metric.
    """

    step_type = "risk_scoring"

    def execute(self, application: Dict[str, Any], params: Dict[str, Any]) -> StepResult:
        approve_threshold = params.get("approve_threshold", 45)

        # Get country caps for max_allowed calculation
        country_caps = params.get("country_caps", {
            "ES": 30000,
            "FR": 25000,
            "DE": 35000,
            "OTHER": 20000
        })

        monthly_income = application["monthly_income"]
        declared_debts = application["declared_debts"]
        amount = application["amount"]
        country = application["country"]

        # Calculate DTI
        dti = declared_debts / monthly_income if monthly_income > 0 else 1.0

        # Get max allowed for country
        max_allowed = country_caps.get(country, country_caps["OTHER"])

        # Calculate risk score
        # risk = (dti * 100) + (amount/max_allowed * 20)
        risk = (dti * 100) + ((amount / max_allowed) * 20)

        # Check if risk is acceptable
        passed = risk <= approve_threshold

        message = (
            f"Risk score: {risk:.2f} (threshold: {approve_threshold}) - "
            f"{'PASS' if passed else 'FAIL'}"
        )

        return StepResult(
            passed=passed,
            computed_values={
                "risk": round(risk, 2),
                "approve_threshold": approve_threshold,
                "dti": round(dti, 4),
                "amount": amount,
                "max_allowed": max_allowed
            },
            message=message
        )

    @classmethod
    def get_default_params(cls) -> Dict[str, Any]:
        return {
            "approve_threshold": 45,
            "country_caps": {
                "ES": 30000,
                "FR": 25000,
                "DE": 35000,
                "OTHER": 20000
            }
        }
