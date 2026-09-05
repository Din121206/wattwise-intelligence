"""
WattWise EMS Safety Validation Engine.
Performs deterministic safety checks on decisions and control commands before hardware execution.
"""

from typing import List
from ems.models import (
    EMSDecision,
    EnergyState,
    SafetyResult,
    EMSAction,
    ApprovalState
)


from ems.config import config


class EMSSafetyEngine:
    """
    Safety Intercept Layer.
    Validates control decisions against physical power constraints,
    critical load protection, and approval flags.
    """

    def __init__(self, max_system_load_kw: float = None):
        self.max_system_load_kw = max_system_load_kw or config.MAX_SYSTEM_LOAD_KW

    def validate(self, decision: EMSDecision, state: EnergyState) -> SafetyResult:
        violations: List[str] = []

        # 1. Approval Check: Decision MUST be APPROVED
        if decision.approval_status != ApprovalState.APPROVED:
            violations.append(
                f"User approval check failed: Decision status is {decision.approval_status.value}, expected APPROVED."
            )

        # 2. System Load Safety Limits
        if state.load_consumption_kw > self.max_system_load_kw:
            violations.append(
                f"Excessive system load detected ({state.load_consumption_kw:.2f} kW > max safe limit {self.max_system_load_kw:.2f} kW)."
            )

        # 4. Critical Load Protection Check
        # Disallow actions that attempt to disable critical loads
        if "Critical Load" in decision.target_device and decision.recommended_action == EMSAction.LOAD_REDUCE:
            if state.critical_load_kw <= 0.0:
                violations.append("Cannot shed critical loads when critical load allocation is undefined.")

        # 5. Invalid / Unknown Action Protection
        valid_actions = set(EMSAction)
        if decision.recommended_action not in valid_actions:
            violations.append(f"Invalid or unrecognized control action: {decision.recommended_action}")

        # Summary Result
        is_safe = len(violations) == 0
        if is_safe:
            reason = f"Safety validation PASSED for decision {decision.decision_id}. All operational parameters within nominal ranges."
        else:
            reason = f"Safety validation FAILED with {len(violations)} violation(s)."

        return SafetyResult(
            decision_id=decision.decision_id,
            is_safe=is_safe,
            reason=reason,
            violations=violations
        )
