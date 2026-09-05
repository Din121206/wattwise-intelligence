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

        # CASE 5 — Critical Load Protection
        # Triggered when available solar generation + battery capacity is insufficient for essential critical load
        if (state.solar_generation_kw < state.critical_load_kw and state.battery_soc <= 15.0) or (state.solar_generation_kw + (state.battery_soc / 100.0 * 2.0) < state.critical_load_kw):
            confidence = round(0.90 + min(0.08, (15.0 - state.battery_soc) * 0.02), 2) if state.battery_soc <= 15.0 else 0.92
            return EMSDecision(
                decision_id=decision_id,
                installation_id=state.installation_id,
                recommended_action=EMSAction.CRITICAL_LOAD_PROTECTION,
                target_device="Non-Critical Load Shedder",
                reason=(
                    f"Critical load protection active: available solar generation ({state.solar_generation_kw:.2f} kW) "
                    f"and battery SOC ({state.battery_soc:.1f}%) are insufficient for critical load demand of {state.critical_load_kw:.2f} kW. "
                    f"Shedding non-critical loads to preserve essential power reserve."
                ),
                confidence=confidence,
                approval_status=ApprovalState.PENDING
            )

        # CASE 4 — Low Battery
        # Triggered when battery SOC <= 20%
        if state.battery_soc <= 20.0:
            confidence = round(min(0.98, max(0.70, 0.92 - (state.battery_soc / 100.0) * 0.25)), 2)
            return EMSDecision(
                decision_id=decision_id,
                installation_id=state.installation_id,
                recommended_action=EMSAction.GRID_IMPORT,
                target_device="Main Utility Gateway",
                reason=(
                    f"Low battery detected (SOC {state.battery_soc:.1f}% <= 20.0%). "
                    f"Recommending grid import ({state.grid_import_kw:.2f} kW) to meet load demand ({state.load_consumption_kw:.2f} kW) "
                    f"and restricting battery discharge to protect battery lifespan."
                ),
                confidence=confidence,
                approval_status=ApprovalState.PENDING
            )

        # CASE 1 — Excess Solar (Battery SOC < 90%)
        if surplus_kw > 0.1 and state.battery_soc < 90.0:
            confidence = round(min(0.98, max(0.70, 0.82 + (surplus_kw / max(state.solar_generation_kw, 1.0)) * 0.18)), 2)
            return EMSDecision(
                decision_id=decision_id,
                installation_id=state.installation_id,
                recommended_action=EMSAction.BATTERY_CHARGE,
                target_device="Battery Storage Inverter",
                reason=(
                    f"Excess solar detected: generation is {state.solar_generation_kw:.2f} kW while consumption is {state.load_consumption_kw:.2f} kW, "
                    f"creating {surplus_kw:.2f} kW surplus. Battery SOC is {state.battery_soc:.1f}%, so charging the battery is recommended."
                ),
                confidence=confidence,
                approval_status=ApprovalState.PENDING
            )

        # CASE 2 — Battery Almost Full (Excess solar + battery SOC >= 90%)
        if surplus_kw > 0.1 and state.battery_soc >= 90.0:
            confidence = round(min(0.98, max(0.70, 0.85 + ((state.battery_soc - 90.0) / 10.0) * 0.10)), 2)
            return EMSDecision(
                decision_id=decision_id,
                installation_id=state.installation_id,
                recommended_action=EMSAction.GRID_EXPORT,
                target_device="Grid Tie Inverter",
                reason=(
                    f"Excess solar generation detected ({state.solar_generation_kw:.2f} kW > load {state.load_consumption_kw:.2f} kW, "
                    f"surplus {surplus_kw:.2f} kW) with battery almost full (SOC {state.battery_soc:.1f}% >= 90.0%). "
                    f"Recommending grid export because the battery should not continue charging."
                ),
                confidence=confidence,
                approval_status=ApprovalState.PENDING
            )

        # CASE 3 — Peak Consumption (Load > Solar + Battery SOC > 20%)
        if surplus_kw < -0.1 and state.battery_soc > 20.0:
            confidence = round(min(0.98, max(0.70, 0.76 + (state.battery_soc / 100.0) * 0.20)), 2)
            return EMSDecision(
                decision_id=decision_id,
                installation_id=state.installation_id,
                recommended_action=EMSAction.BATTERY_DISCHARGE,
                target_device="Battery Storage Inverter",
                reason=(
                    f"Peak consumption detected: load consumption ({state.load_consumption_kw:.2f} kW) exceeds solar generation ({state.solar_generation_kw:.2f} kW). "
                    f"Battery SOC is {state.battery_soc:.1f}%, so discharging battery is recommended to reduce grid dependency."
                ),
                confidence=confidence,
                approval_status=ApprovalState.PENDING
            )

        # CASE 6 — Normal Operation (Balanced solar/load & healthy battery)
        confidence = round(max(0.70, 0.85 - abs(surplus_kw) * 0.05), 2)
        return EMSDecision(
            decision_id=decision_id,
            installation_id=state.installation_id,
            recommended_action=EMSAction.OPTIMIZE_LOAD,
            target_device="Smart Home Energy Hub",
            reason=(
                f"Normal operation: solar generation ({state.solar_generation_kw:.2f} kW) and load consumption ({state.load_consumption_kw:.2f} kW) "
                f"are balanced (surplus {surplus_kw:.2f} kW). Battery SOC is healthy at {state.battery_soc:.1f}%. Recommending load optimization."
            ),
            confidence=confidence,
            approval_status=ApprovalState.PENDING
        )
