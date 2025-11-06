from abc import ABC, abstractmethod
from typing import Dict, Any
from pydantic import BaseModel


class StepResult(BaseModel):
    passed: bool
    computed_values: Dict[str, Any]
    message: str


class BaseStep(ABC):
    """Base class for all pipeline steps"""

    step_type: str

    @abstractmethod
    def execute(self, application: Dict[str, Any], params: Dict[str, Any]) -> StepResult:
        """
        Execute the step logic

        Args:
            application: Dictionary containing loan application data
            params: Step-specific parameters

        Returns:
            StepResult with pass/fail status, computed values, and message
        """
        pass

    @classmethod
    def get_default_params(cls) -> Dict[str, Any]:
        """Return default parameters for this step"""
        return {}
