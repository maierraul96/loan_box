from typing import Dict, Any
from app.steps.base import BaseStep, StepResult


class DTIRule(BaseStep):
    """
    Debt-to-Income Rule
    Checks whether the applicant's debt burden is reasonable.
    """

    step_type = "dti_rule"

    def execute(self, application: Dict[str, Any], params: Dict[str, Any]) -> StepResult:
        max_dti = params.get("max_dti", 0.40)

        monthly_income = application["monthly_income"]
        declared_debts = application["declared_debts"]

        # Calculate DTI ratio
        dti = declared_debts / monthly_income if monthly_income > 0 else float('inf')

        # Check if DTI is within acceptable range
        passed = dti < max_dti

        message = (
            f"DTI ratio: {dti:.2%} (max allowed: {max_dti:.2%}) - "
            f"{'PASS' if passed else 'FAIL'}"
        )

        return StepResult(
            passed=passed,
            computed_values={
                "dti": round(dti, 4),
                "max_dti": max_dti,
                "monthly_income": monthly_income,
                "declared_debts": declared_debts
            },
            message=message
        )

    @classmethod
    def get_default_params(cls) -> Dict[str, Any]:
        return {"max_dti": 0.40}
