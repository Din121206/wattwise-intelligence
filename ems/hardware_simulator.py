"""
WattWise ESP32 Virtual Hardware Simulator.

SIMULATED HARDWARE DISCLAIMER:
This module simulates an ESP32 microcontroller and attached IoT loads/inverters.
No physical hardware signals are emitted.
"""

from datetime import datetime, timezone
from ems.models import (
    ControlCommand,
    HardwareResponse,
    HardwareStatus,
    SafetyResult,
    EMSAction
)


class ESP32HardwareSimulator:
    """
    Simulates hardware actuation for ESP32 energy controllers and smart loads.
    Enforces that commands must have passed safety validation before execution.
    """

    def __init__(self, device_id: str = "ESP32-EMS-GW-01"):
        self.device_id = device_id
        self.execution_log = []

    def execute_command(self, command: ControlCommand, safety_check: SafetyResult) -> HardwareResponse:
        """
        Executes a control command on simulated hardware.
        """
        now = datetime.now(timezone.utc).isoformat()

        # Reject if safety validation failed
        if not safety_check.is_safe:
            response = HardwareResponse(
                device_name=command.device_name,
                command_type=command.command_type.value,
                status=HardwareStatus.BLOCKED,
                is_simulated=True,
                message=f"[SIMULATED HARDWARE - {self.device_id}] EXECUTION REJECTED. Safety check failed: {safety_check.reason}",
                timestamp=now
            )
            self.execution_log.append(response)
            return response

        # Simulate execution based on action type
        action_messages = {
            EMSAction.GRID_EXPORT: f"[SIMULATED HARDWARE - {self.device_id}] Inverter sync engaged. Exporting surplus solar power to grid.",
            EMSAction.GRID_IMPORT: f"[SIMULATED HARDWARE - {self.device_id}] Grid switch closed. Supplying load demand from utility grid.",
            EMSAction.CRITICAL_LOAD_PROTECTION: f"[SIMULATED HARDWARE - {self.device_id}] Smart Breakers tripped. Shedding non-critical circuits; isolating critical load.",
            EMSAction.OPTIMIZE_LOAD: f"[SIMULATED HARDWARE - {self.device_id}] PWM load balancer active. Optimizing consumption across circuits.",
            EMSAction.LOAD_SHIFT: f"[SIMULATED HARDWARE - {self.device_id}] Smart Plug GPIO high. Shifted flexible load (EV Charger / Pump) ON.",
            EMSAction.LOAD_REDUCE: f"[SIMULATED HARDWARE - {self.device_id}] Shedding command broadcast. PWM dimmed non-critical HVAC/Lighting load.",
            EMSAction.MAINTAIN: f"[SIMULATED HARDWARE - {self.device_id}] No relay toggles required. Maintaining baseline operating state."
        }

        msg = action_messages.get(
            command.command_type,
            f"[SIMULATED HARDWARE - {self.device_id}] Command {command.command_type} executed on {command.device_name}."
        )

        response = HardwareResponse(
            device_name=command.device_name,
            command_type=command.command_type.value,
            status=HardwareStatus.EXECUTED,
            is_simulated=True,
            message=msg,
            timestamp=now
        )

        self.execution_log.append(response)
        return response
