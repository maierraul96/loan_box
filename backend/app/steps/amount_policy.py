from typing import Dict, Any
from app.steps.base import BaseStep, StepResult


class AmountPolicy(BaseStep):
    """
    Amount Policy
    Enforce country-specific loan limits.
    """

    step_type = "amount_policy"

    def execute(self, application: Dict[str, Any], params: Dict[str, Any]) -> StepResult:
        # Default country caps
        default_caps = self.get_default_params()

        # Merge default caps with provided params
        country_caps = {**default_caps, **params}

        amount = application["amount"]
        country = application["country"]

        # Get cap for the country, or use OTHER as fallback
        cap = country_caps.get(country, country_caps["OTHER"])

        # Check if amount is within the cap
        passed = amount <= cap

        message = (
            f"Loan amount: {amount} {country} (max allowed: {cap}) - "
            f"{'PASS' if passed else 'FAIL'}"
        )

        return StepResult(
            passed=passed,
            computed_values={
                "amount": amount,
                "country": country,
                "cap": cap,
                "country_caps": country_caps
            },
            message=message
        )

    @classmethod
    def get_default_params(cls) -> Dict[str, Any]:
        return {
            "ES": 30000,
            "FR": 25000,
            "DE": 35000,
            "OTHER": 20000
        }
