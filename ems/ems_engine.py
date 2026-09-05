"""
WattWise EMS AI Decision Engine.

Note: This engine uses explicit rule-based heuristics for demo/simulation purposes.
It models intelligent automated energy recommendations without claiming a real machine learning model.
"""

import uuid
from ems.models import (
    EnergyState,
    EMSDecision,
    EMSAction,
    ApprovalState
)


class EMSEngine:
    """
    Simulated AI Decision Engine for Energy Management System (EMS).
    Evaluates current EnergyState telemetry and produces an EMSDecision with recommendations.
    """

    def analyze(self, state: EnergyState) -> EMSDecision:
        decision_id = f"DEC-{uuid.uuid4().hex[:6].upper()}"
        surplus_kw = state.solar_generation_kw - state.load_consumption_kw

        # CASE 1 — Critical Load Protection
        # Triggered when solar generation is insufficient to meet critical load demand
        if state.solar_generation_kw < state.critical_load_kw:
            return EMSDecision(
                decision_id=decision_id,
                installation_id=state.installation_id,
                recommended_action=EMSAction.CRITICAL_LOAD_PROTECTION,
                target_device="Non-Critical Load Shedder",
                reason=(
                    f"Critical load protection active: solar generation ({state.solar_generation_kw:.2f} kW) "
                    f"is insufficient for essential critical load demand of {state.critical_load_kw:.2f} kW. "
                    f"Shedding non-critical loads to preserve essential power."
                ),
                confidence=0.96,
                approval_status=ApprovalState.PENDING
            )

        # CASE 2 — Excess Solar Generation (Grid Export)
        if surplus_kw > 0.1:
            confidence = round(min(0.98, max(0.70, 0.85 + (surplus_kw / max(state.solar_generation_kw, 1.0)) * 0.12)), 2)
            return EMSDecision(
                decision_id=decision_id,
                installation_id=state.installation_id,
                recommended_action=EMSAction.GRID_EXPORT,
                target_device="Grid Tie Inverter",
                reason=(
                    f"Excess solar detected: generation is {state.solar_generation_kw:.2f} kW while consumption is {state.load_consumption_kw:.2f} kW, "
                    f"creating {surplus_kw:.2f} kW surplus. Recommending grid export."
                ),
                confidence=confidence,
                approval_status=ApprovalState.PENDING
            )

        # CASE 3 — Grid Import Required for Power Deficit
        if surplus_kw < -0.1 and state.grid_import_kw > 0.5:
            confidence = round(min(0.98, max(0.70, 0.82 + min(0.15, state.grid_import_kw / 10.0))), 2)
            return EMSDecision(
                decision_id=decision_id,
                installation_id=state.installation_id,
                recommended_action=EMSAction.GRID_IMPORT,
                target_device="Main Utility Gateway",
                reason=(
                    f"Power deficit detected: load consumption ({state.load_consumption_kw:.2f} kW) exceeds solar generation ({state.solar_generation_kw:.2f} kW). "
                    f"Recommending grid import ({state.grid_import_kw:.2f} kW) to meet load demand."
                ),
                confidence=confidence,
                approval_status=ApprovalState.PENDING
            )

        # CASE 4 — Load Reduction for High Consumption
        if surplus_kw < -0.1:
            return EMSDecision(
                decision_id=decision_id,
                installation_id=state.installation_id,
                recommended_action=EMSAction.LOAD_REDUCE,
                target_device="HVAC & Non-Essential Load Controller",
                reason=(
                    f"High load demand ({state.load_consumption_kw:.2f} kW) exceeds solar generation ({state.solar_generation_kw:.2f} kW). "
                    f"Recommending non-critical load reduction to minimize grid dependency."
                ),
                confidence=0.88,
                approval_status=ApprovalState.PENDING
            )

        # CASE 5 — Normal Operation (Balanced solar and load)
        confidence = round(max(0.70, 0.85 - abs(surplus_kw) * 0.05), 2)
        return EMSDecision(
            decision_id=decision_id,
            installation_id=state.installation_id,
            recommended_action=EMSAction.OPTIMIZE_LOAD,
            target_device="Smart Home Energy Hub",
            reason=(
                f"Normal operation: solar generation ({state.solar_generation_kw:.2f} kW) and load consumption ({state.load_consumption_kw:.2f} kW) "
                f"are balanced (surplus {surplus_kw:.2f} kW). Recommending standard load optimization."
            ),
            confidence=confidence,
            approval_status=ApprovalState.PENDING
        )
