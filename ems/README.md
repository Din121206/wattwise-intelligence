# WattWise Energy Management System (EMS) Module

The **WattWise Energy Management System (EMS)** module is an isolated, software-only decision and control loop built for the WattWise AI platform. It provides rule-based AI recommendations, human-in-the-loop approval, deterministic safety boundary verification, and virtual ESP32 hardware actuation.

---

## 🏗️ Architecture & Decision Flow

The EMS module enforces a strict 5-stage pipeline to ensure zero unauthorized or dangerous commands reach simulated hardware:

```
+------------------+
|  Energy State    |  (Telemetry: Solar kW, Battery SOC %, Load kW, Grid kW)
+--------+---------+
         |
         v
+------------------+
|  AI EMS Engine   |  (Rule-based AI heuristic recommendation generation)
+--------+---------+
         |
         v  [ Status: PENDING ]
+------------------+
| User Confirmation|  (Human-in-the-loop: APPROVED or REJECTED)
+--------+---------+
         |
         |  [ Only APPROVED decisions proceed ]
         v
+------------------+
|   Safety Engine  |  (Interception checks: SOC boundaries, Max Load, Critical Load protection)
+--------+---------+
         |
         |  [ Only SAFE commands proceed ]
         v
+--------------------+
| Hardware Simulator |  (Virtual ESP32 Microcontroller & Load Controller)
+--------------------+
```

---

## 🛡️ Safety Engine Rules

The `EMSSafetyEngine` acts as an unbypassable gatekeeper before hardware transmission:

1. **Human Approval Gate**: Decisions in `PENDING` or `REJECTED` states are strictly blocked from execution.
2. **Battery SOC Limits**:
   - `BATTERY_DISCHARGE` commands blocked if SOC $< 10.0\%$.
   - `BATTERY_CHARGE` commands blocked if SOC $\ge 100.0\%$.
3. **System Capacity Limit**: Commands blocked if aggregate load consumption exceeds $10.0\text{ kW}$.
4. **Critical Load Protection**: Shedding or shedding-adjacent commands targeting essential critical loads are forbidden.
5. **Action Whitelist**: Unrecognized actions are immediately blocked.

---

## ⚡ ESP32 Hardware Simulator

> **DISCLAIMER: SIMULATED HARDWARE ONLY**  
> There is no physical hardware attached. The `ESP32HardwareSimulator` simulates an ESP32 microcontroller receiving commands via Modbus RS485 / GPIO / PWM relay logic and returning a structured `HardwareResponse`.

Supported Command Types:
- `BATTERY_CHARGE`: Directs surplus solar power to charge storage inverter.
- `BATTERY_DISCHARGE`: Discharges battery storage to shave peak consumption grid draw.
- `GRID_EXPORT`: Exports excess solar power to utility grid when battery is full.
- `GRID_IMPORT`: Imports grid power while protecting depleted/low battery storage.
- `CRITICAL_LOAD_PROTECTION`: Sheds non-critical circuits to safeguard essential reserves.
- `OPTIMIZE_LOAD`: Optimizes consumption across circuits during balanced operation.

---

## 🌐 API Endpoints Overview

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/ems/scenarios` | Lists pre-packaged telemetry scenarios for quick testing |
| `POST` | `/api/ems/scenarios/{key}/decision` | Evaluates a pre-packaged scenario through the live AI decision engine |
| `POST` | `/api/ems/decision` | Evaluates telemetry and generates a dynamic `EMSDecision` (Pending approval) |
| `POST` | `/api/ems/confirm` | User approves or rejects a pending decision |
| `POST` | `/api/ems/execute` | Validates safety and dispatches approved decision to virtual ESP32 |
| `GET` | `/api/ems/status` | System metrics, active decision count, and execution history |

---

## 🎯 Demo Scenarios & Dynamic Logic

1. **Excess Solar Generation**:
   - *State*: High solar ($8.5\text{ kW}$), Load ($4.0\text{ kW}$), Moderate battery ($72\%$).
   - *Recommendation*: `BATTERY_CHARGE` (Surplus $4.50\text{ kW}$ directs to battery).
2. **Battery Full**:
   - *State*: High solar ($8.5\text{ kW}$), Load ($4.0\text{ kW}$), Full battery ($92\%$).
   - *Recommendation*: `GRID_EXPORT` (Battery full; export surplus green power to grid).
3. **Peak Consumption**:
   - *State*: Solar ($2.0\text{ kW}$), High load ($8.0\text{ kW}$), Battery ($65\%$).
   - *Recommendation*: `BATTERY_DISCHARGE` (Discharge battery storage to peak-shave deficit).
4. **Low Battery**:
   - *State*: Solar ($0.1\text{ kW}$), Load ($2.8\text{ kW}$), Battery ($18\%$).
   - *Recommendation*: `GRID_IMPORT` (Protect battery health, import power from grid).
5. **Critical Load Protection**:
   - *State*: Solar ($0.0\text{ kW}$), Load ($1.8\text{ kW}$), Emergency battery ($12\%$).
   - *Recommendation*: `CRITICAL_LOAD_PROTECTION` (Shed non-essential loads for essential reserve).
6. **Normal Operation**:
   - *State*: Balanced solar ($1.5\text{ kW}$), Load ($1.5\text{ kW}$), Healthy battery ($60\%$).
   - *Recommendation*: `OPTIMIZE_LOAD`.

---

## 🧪 Testing

Run pytest to test the full EMS pipeline:

```bash
python -m pytest tests/test_ems.py
```
