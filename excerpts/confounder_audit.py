# Excerpt from Program Learning AI (src/program_learning_ai/engine.py).
# ExperimentEngine.audit_comparison and its helper, shown on their own.
# Before two trials are compared, report context variables that changed or
# were never recorded, since either can confound the comparison.

from .models import ComparisonAudit


class ExperimentEngine:
    # ... other methods omitted ...

    def audit_comparison(
        self,
        control_trial_id: str,
        test_trial_id: str,
        required_matches: list[str] | None = None,
    ) -> ComparisonAudit:
        """Find changed or unreported context that can confound a trial comparison."""
        control = self.store.get("trials", control_trial_id)
        test = self.store.get("trials", test_trial_id)
        if control["experiment_id"] != test["experiment_id"]:
            raise ValueError("Compared trials must belong to the same experiment")
        experiment = self.store.get("experiments", control["experiment_id"])
        matches = list(required_matches or experiment.get("matching_variables", []))
        if "starting_state" not in matches:
            matches.insert(0, "starting_state")

        mismatches: dict[str, dict[str, object]] = {}
        missing: list[str] = []
        for variable in matches:
            control_found, control_value = _trial_value(control, variable)
            test_found, test_value = _trial_value(test, variable)
            if not control_found or not test_found:
                missing.append(variable)
            elif control_value != test_value:
                mismatches[variable] = {
                    "control": control_value,
                    "test": test_value,
                }
        return ComparisonAudit(
            control_trial_id=control_trial_id,
            test_trial_id=test_trial_id,
            required_matches=matches,
            mismatches=mismatches,
            missing=missing,
        )


def _trial_value(trial: dict[str, object], variable: str) -> tuple[bool, object | None]:
    if variable in trial:
        return True, trial[variable]
    context = trial.get("context", {})
    if isinstance(context, dict) and variable in context:
        return True, context[variable]
    return False, None
