import json
from typing import Dict, Any, List, Tuple
from sqlalchemy.orm import Session
from app.db_models import LoanApplication, Pipeline, PipelineRun
from app.models import StepLog, TerminalRuleLog, FinalStatus, PipelineStepConfig, TerminalRule
from app.steps.registry import get_step_class


class PipelineExecutor:
    """
    Core orchestration logic for executing pipelines on loan applications
    """

    def __init__(self, db: Session):
        self.db = db

    def execute(self, application_id: int, pipeline_id: int) -> PipelineRun:
        """
        Execute a pipeline on a loan application

        Args:
            application_id: ID of the loan application
            pipeline_id: ID of the pipeline to execute

        Returns:
            PipelineRun with execution results

        Raises:
            ValueError: If application or pipeline not found
        """
        # 1. Load application and pipeline
        application = self.db.query(LoanApplication).filter(
            LoanApplication.id == application_id
        ).first()
        if not application:
            raise ValueError(f"Application {application_id} not found")

        pipeline = self.db.query(Pipeline).filter(
            Pipeline.id == pipeline_id
        ).first()
        if not pipeline:
            raise ValueError(f"Pipeline {pipeline_id} not found")

        # Convert application to dict for step execution
        app_data = {
            "applicant_name": application.applicant_name,
            "amount": application.amount,
            "monthly_income": application.monthly_income,
            "declared_debts": application.declared_debts,
            "country": application.country,
            "loan_purpose": application.loan_purpose,
        }

        # Parse pipeline configuration
        steps_config = json.loads(pipeline.steps_config)
        terminal_rules = json.loads(pipeline.terminal_rules)

        # Sort steps by order
        steps_config = sorted(steps_config, key=lambda x: x["order"])

        # 2. Execute steps in order
        step_logs = []
        step_results = {}  # Store results for terminal rule evaluation

        for step_config in steps_config:
            step_type = step_config["step_type"]
            params = step_config.get("params", {})
            order = step_config["order"]

            # Get step class and execute
            step_class = get_step_class(step_type)
            step_instance = step_class()
            result = step_instance.execute(app_data, params)

            # Create log entry
            log = StepLog(
                step_type=step_type,
                order=order,
                passed=result.passed,
                computed_values=result.computed_values,
                message=result.message
            )
            step_logs.append(log)

            # Store result for terminal rule evaluation
            step_results[step_type] = result

        # 3. Evaluate terminal rules to determine final status
        final_status, terminal_rule_logs = self._evaluate_terminal_rules(terminal_rules, step_results)

        # 4. Update application status
        application.status = final_status.value
        self.db.commit()

        # 5. Persist run to database
        run = PipelineRun(
            application_id=application_id,
            pipeline_id=pipeline_id,
            step_logs=json.dumps([log.model_dump() for log in step_logs]),
            terminal_rule_logs=json.dumps([log.model_dump() for log in terminal_rule_logs]),
            final_status=final_status.value
        )
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)

        return run

    def _evaluate_terminal_rules(
        self,
        terminal_rules: List[Dict[str, Any]],
        step_results: Dict[str, Any]
    ) -> Tuple[FinalStatus, List[TerminalRuleLog]]:
        """
        Evaluate terminal rules based on step results

        Args:
            terminal_rules: List of terminal rule configurations
            step_results: Dictionary of step results keyed by step_type

        Returns:
            Tuple of (Final status, Terminal rule logs)
        """
        # Sort rules by order
        sorted_rules = sorted(terminal_rules, key=lambda x: x["order"])

        terminal_rule_logs = []
        final_status = FinalStatus.NEEDS_REVIEW
        matched_rule_found = False

        # Evaluate each rule in order
        for rule in sorted_rules:
            condition = rule["condition"]
            outcome = rule["outcome"]
            order = rule["order"]

            # If a rule already matched, skip evaluation but log it
            if matched_rule_found:
                log = TerminalRuleLog(
                    condition=condition,
                    outcome=FinalStatus(outcome),
                    order=order,
                    evaluated=False,
                    matched=False,
                    reason="Not evaluated (previous rule matched)"
                )
                terminal_rule_logs.append(log)
                continue

            # Evaluate the condition
            evaluation_result, reason = self._evaluate_condition_with_reason(condition, step_results)

            # Create log entry
            if evaluation_result:
                # This rule matched!
                final_status = FinalStatus(outcome)
                matched_rule_found = True
                log = TerminalRuleLog(
                    condition=condition,
                    outcome=FinalStatus(outcome),
                    order=order,
                    evaluated=True,
                    matched=True,
                    reason=f"Rule matched: {reason}"
                )
            else:
                # Rule did not match
                log = TerminalRuleLog(
                    condition=condition,
                    outcome=FinalStatus(outcome),
                    order=order,
                    evaluated=True,
                    matched=False,
                    reason=f"Rule not matched: {reason}"
                )

            terminal_rule_logs.append(log)

        return final_status, terminal_rule_logs

    def _evaluate_condition_with_reason(
        self,
        condition: str,
        step_results: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        Evaluate a terminal rule condition and provide a reason

        Returns:
            Tuple of (evaluation result, human-readable reason)
        """
        # Handle "else" (catch-all)
        if condition.strip().lower() == "else":
            return True, "Catch-all condition (else)"

        # Handle OR conditions
        if " OR " in condition:
            parts = condition.split(" OR ")
            results = []
            for part in parts:
                result, reason = self._evaluate_condition_with_reason(part.strip(), step_results)
                results.append((result, reason))
                if result:
                    return True, f"OR condition TRUE: {reason}"
            # All were false
            failed_reasons = [reason for _, reason in results]
            return False, f"OR condition FALSE: {' AND '.join(failed_reasons)}"

        # Handle AND conditions
        if " AND " in condition:
            parts = condition.split(" AND ")
            results = []
            for part in parts:
                result, reason = self._evaluate_condition_with_reason(part.strip(), step_results)
                results.append((result, reason))
                if not result:
                    return False, f"AND condition FALSE: {reason}"
            # All were true
            passed_reasons = [reason for _, reason in results]
            return True, f"AND condition TRUE: {' AND '.join(passed_reasons)}"

        # Handle simple conditions
        if ".failed" in condition:
            step_name = condition.replace(".failed", "").strip()
            if step_name in step_results:
                result = step_results[step_name]
                if not result.passed:
                    return True, f"{step_name} failed ({result.message})"
                else:
                    return False, f"{step_name} passed ({result.message})"
            return False, f"{step_name} not found"

        if ".passed" in condition:
            step_name = condition.replace(".passed", "").strip()
            if step_name in step_results:
                result = step_results[step_name]
                if result.passed:
                    return True, f"{step_name} passed ({result.message})"
                else:
                    return False, f"{step_name} failed ({result.message})"
            return False, f"{step_name} not found"

        # Handle value comparisons (e.g., "risk_scoring.risk <= 45")
        if "<=" in condition or ">=" in condition or "<" in condition or ">" in condition or "==" in condition:
            try:
                for op in ["<=", ">=", "==", "<", ">"]:
                    if op in condition:
                        left, right = condition.split(op)
                        left = left.strip()
                        right = right.strip()

                        left_value = self._evaluate_value(left, step_results)
                        right_value = self._evaluate_value(right, step_results)

                        if op == "<=":
                            result = left_value <= right_value
                        elif op == ">=":
                            result = left_value >= right_value
                        elif op == "<":
                            result = left_value < right_value
                        elif op == ">":
                            result = left_value > right_value
                        elif op == "==":
                            result = left_value == right_value

                        reason = f"{left} ({left_value}) {op} {right} ({right_value})"
                        return result, reason
            except Exception as e:
                return False, f"Error evaluating condition: {str(e)}"

        return False, "Unknown condition format"

    def _evaluate_value(self, value_str: str, step_results: Dict[str, Any]) -> Any:
        """
        Evaluate a value string

        Supports:
        - Numbers: "45" -> 45
        - Step computed values: "risk_scoring.risk" -> step_results["risk_scoring"].computed_values["risk"]
        - Step params: "risk_scoring.params.approve_threshold" -> params value from step result
        """
        value_str = value_str.strip()

        # Try to parse as number
        try:
            if "." in value_str and value_str.replace(".", "").replace("-", "").isdigit():
                return float(value_str)
            elif value_str.replace("-", "").isdigit():
                return int(value_str)
        except ValueError:
            pass

        # Parse step reference (e.g., "risk_scoring.risk" or "risk_scoring.params.approve_threshold")
        if "." in value_str:
            parts = value_str.split(".")
            step_name = parts[0]

            if step_name in step_results:
                result = step_results[step_name]

                if len(parts) == 2:
                    # e.g., "risk_scoring.risk"
                    field_name = parts[1]
                    return result.computed_values.get(field_name)
                elif len(parts) == 3 and parts[1] == "params":
                    # e.g., "risk_scoring.params.approve_threshold"
                    param_name = parts[2]
                    return result.computed_values.get(param_name)

        return value_str
