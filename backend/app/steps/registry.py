from typing import Dict, Type
from app.steps.base import BaseStep
from app.steps.dti_rule import DTIRule
from app.steps.amount_policy import AmountPolicy
from app.steps.risk_scoring import RiskScoring


# Registry mapping step_type to step class
STEP_REGISTRY: Dict[str, Type[BaseStep]] = {
    "dti_rule": DTIRule,
    "amount_policy": AmountPolicy,
    "risk_scoring": RiskScoring,
}


def get_step_class(step_type: str) -> Type[BaseStep]:
    """Get step class by step_type"""
    if step_type not in STEP_REGISTRY:
        raise ValueError(f"Unknown step type: {step_type}")
    return STEP_REGISTRY[step_type]


def get_step_catalog():
    """Get catalog of all available steps with their default params"""
    catalog = []
    for step_type, step_class in STEP_REGISTRY.items():
        catalog.append({
            "step_type": step_type,
            "default_params": step_class.get_default_params()
        })
    return catalog
