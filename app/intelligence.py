"""
WattWise Module 2
Integrated renewable energy intelligence engine.
"""

import pandas as pd

from anomaly.hardware_detector import HardwareAnomalyDetector
from forecasting.solar_forecast import SolarForecaster
from digital_twin.performance import PerformanceAnalyzer
from anomaly.detector import AnomalyDetector
from anomaly.cause_classifier import CauseClassifier
from recommendations.engine import RecommendationEngine
from recommendations.control_engine import ControlRecommendationEngine
from app.health import HealthCalculator
from app.models import IntelligenceOutput
from app.output_models import (
    EnergyReadings,
    IntelligenceResult,
    FinalOutput,
)
from app.alerts import AlertGenerator
from app.raw_models import RawIoTData
from app.energy import EnergyCalculator
from app.generation import GenerationAnalyzer
from ml.anomaly_classifier import MLAnomalyClassifier
from ml.forecaster import MLSolarForecaster


class IntelligenceEngine:

    EXCESS_GENERATION_THRESHOLD = 1.20
    ML_CONFIDENCE_THRESHOLD = 0.75

    NORMAL_RECOMMENDATION = "System operating normally."

    ML_CAUSE_MAP = {
        "panel_soiling": "Panel shaded or dirty",
        "partial_shading": "Panel shaded or dirty",
        "inverter_inefficiency": "Inverter inefficiency",
        "cloudy_weather": "Cloudy weather",
        "high_energy_consumption": "High energy consumption",
    }

    SOLAR_PERFORMANCE_ANOMALY_THRESHOLD = 30.0

    # These scenarios describe operating conditions rather than faults.
    NON_FAULT_SCENARIOS = {
        "cloudy_weather",
        "high_energy_consumption",
    }

    def __init__(self):
        self.ml_anomaly_classifier = MLAnomalyClassifier()
        self.ml_forecaster = MLSolarForecaster()
        self.control_recommender = ControlRecommendationEngine()

    def analyze(
        self,
        dataframe,
        capacity,
        baseline_dataframe=None,
    ):
        """
        Analyze historical/dataframe-based solar intelligence.
        """

        forecaster = SolarForecaster(capacity)

        if baseline_dataframe is not None:
            result = forecaster.predict_from_baseline(
                baseline_dataframe,
                dataframe,
            )
        else:
            result = forecaster.predict(dataframe)

        result["actual_generation"] = result["solar_generation"]

        if "expected_generation" not in result.columns:
            result["expected_generation"] = result["predicted_generation"]

        analyzer = PerformanceAnalyzer()
        result = analyzer.compare(result)

        health = HealthCalculator()

        result["health_score"] = result["performance_loss"].apply(
            health.calculate
        )

        result["status"] = result["health_score"].apply(
            health.status
        )

        detector = AnomalyDetector()
        result = detector.detect(result)

        classifier = CauseClassifier()
        result = classifier.classify(result)

        recommender = RecommendationEngine()
        result = recommender.generate(
            result,
            baseline_dataframe=baseline_dataframe,
        )

        excess_generation = (
            (result["expected_generation"] > 0)
            & (
                result["actual_generation"]
                > result["expected_generation"]
                * self.EXCESS_GENERATION_THRESHOLD
            )
        )

        result.loc[excess_generation, "anomaly"] = True

        result.loc[excess_generation, "likely_cause"] = (
            "Unexpectedly high solar generation"
        )

        result.loc[excess_generation, "recommendation"] = (
            "Verify irradiance conditions, sensor readings, "
            "and solar system measurements."
        )

        return result

    def _apply_ml_anomaly_classification(
        self,
        result,
        raw_data: RawIoTData,
    ):
        """
        Apply the trained ML operating-scenario classifier.

        Fault scenarios are treated as anomalies.

        Operating conditions such as cloudy weather and high energy
        consumption are not automatically treated as anomalies.
        """

        prediction = self.ml_anomaly_classifier.predict(raw_data)

        result["ml_scenario"] = prediction["scenario"]
        result["ml_confidence"] = prediction["confidence"]

        scenario = prediction["scenario"]
        confidence = prediction["confidence"]

        if confidence < self.ML_CONFIDENCE_THRESHOLD:
            return result

        existing_anomaly = bool(
            result.iloc[0].get(
                "anomaly",
                False,
            )
        )

        existing_performance_loss = float(
            result.iloc[0].get(
                "performance_loss",
                0.0,
            )
        )

        solar_performance_anomaly = (
            existing_anomaly
            and existing_performance_loss
            >= self.SOLAR_PERFORMANCE_ANOMALY_THRESHOLD
        )

        # If the solar performance is genuinely poor, do not allow
        # high consumption to hide the solar-side fault.
        if (
            scenario == "high_energy_consumption"
            and solar_performance_anomaly
        ):
            return result

        # Cloudy weather is an operating condition, not automatically
        # a hardware/system fault.
        if scenario == "cloudy_weather":
            result["likely_cause"] = "Cloudy weather"

            if not solar_performance_anomaly:
                result["anomaly"] = False
                result["recommendation"] = (
                    "Reduced solar generation is consistent with "
                    "cloudy weather conditions."
                )

            return result

        # High energy consumption is an operating condition, not a fault.
        if scenario == "high_energy_consumption":

            if not solar_performance_anomaly:
                result["anomaly"] = False
                result["likely_cause"] = (
                    "High energy consumption"
                )
                result["recommendation"] = (
                    "Reduce unnecessary loads or shift high-energy "
                    "loads to periods of higher solar generation."
                )

            return result

        # Fault-related ML scenarios.
        if scenario in {
            "panel_soiling",
            "partial_shading",
            "inverter_inefficiency",
        }:

            result["anomaly"] = True

            result["likely_cause"] = (
                self.ML_CAUSE_MAP[scenario]
            )

            if scenario == "panel_soiling":
                result["recommendation"] = (
                    "Inspect and clean the solar panels."
                )

            elif scenario == "partial_shading":
                result["recommendation"] = (
                    "Inspect the installation for partial shading."
                )

            elif scenario == "inverter_inefficiency":
                result["recommendation"] = (
                    "Inspect the inverter and verify its electrical connections."
                )

        return result

    def analyze_raw(
        self,
        raw_data: RawIoTData,
        capacity: float,
        historical_dataframe=None,
    ):
        """
        Analyze a raw IoT telemetry payload.

        Production workflow:

        Raw Telemetry
            ↓
        Energy Calculation
            ↓
        Expected Generation
            ↓
        Predicted Generation
            ↓
        Performance Analysis
            ↓
        Health Score
            ↓
        Anomaly Detection
            ↓
        Likely Cause
            ↓
        Recommendation
            ↓
        9-field intelligence output
        """

        if not isinstance(raw_data, RawIoTData):
            raise TypeError(
                "raw_data must be a RawIoTData object."
            )

        # 1. Energy calculation
        energy_calculator = EnergyCalculator()

        energy = energy_calculator.calculate(
            raw_data
        )

        # 2. Physics-based expected generation
        generation_analyzer = GenerationAnalyzer(
            capacity
        )

        expected_generation = (
            generation_analyzer.expected_generation(
                raw_data
            )
        )

        # 3. Actual generation
        actual_generation = energy[
            "solar_generation"
        ]

        # 4. ML next-hour prediction
        predicted_generation = (
            self.ml_forecaster.predict(
                raw_data
            )
        )

        predicted_generation = min(
            max(
                predicted_generation,
                0.0,
            ),
            capacity,
        )

        # 5. Build analysis dataframe
        result = pd.DataFrame(
            [
                {
                    "timestamp": raw_data.timestamp,
                    "solar_generation": actual_generation,
                    "energy_consumption": energy[
                        "energy_consumption"
                    ],
                    "grid_import": energy[
                        "grid_import"
                    ],
                    "grid_export": energy[
                        "grid_export"
                    ],
                    "battery_charge": energy[
                        "battery_charge"
                    ],
                    "battery_discharge": energy[
                        "battery_discharge"
                    ],
                    "weather": "unknown",
                    "system_efficiency": 100.0,
                    "predicted_generation": predicted_generation,
                    "expected_generation": expected_generation,
                    "actual_generation": actual_generation,
                }
            ]
        )

        # 6. Performance analysis
        performance = PerformanceAnalyzer()

        result = performance.compare(
            result
        )

        # 7. Health score
        health = HealthCalculator()

        result["health_score"] = (
            result["performance_loss"].apply(
                health.calculate
            )
        )

        result["status"] = (
            result["health_score"].apply(
                health.status
            )
        )

        # 8. Mathematical anomaly detection
        detector = AnomalyDetector()

        result = detector.detect(
            result
        )

        # 9. Likely cause classification
        classifier = CauseClassifier()

        result = classifier.classify(
            result
        )

        # 10. Recommendation engine
        recommender = RecommendationEngine()

        result = recommender.generate(
            result
        )

        # 11. ML scenario classification
        result = (
            self._apply_ml_anomaly_classification(
                result,
                raw_data,
            )
        )

        # 12. Hardware anomaly detection
        hardware_detector = HardwareAnomalyDetector()

        hardware_anomalies = (
            hardware_detector.detect(
                raw_data,
                expected_generation=expected_generation,
                actual_generation=actual_generation,
            )
        )

        result["hardware_anomalies"] = [
            hardware_anomalies
        ]

        # 13. Hardware anomaly handling
        if hardware_anomalies:

            result["anomaly"] = True

            critical_anomalies = [
                anomaly
                for anomaly in hardware_anomalies
                if anomaly["severity"]
                == "critical"
            ]

            warning_anomalies = [
                anomaly
                for anomaly in hardware_anomalies
                if anomaly["severity"]
                == "warning"
            ]

            if critical_anomalies:

                selected_anomaly = (
                    critical_anomalies[0]
                )

                result["status"] = "critical"

                result["likely_cause"] = (
                    selected_anomaly[
                        "likely_cause"
                    ]
                )

                result["recommendation"] = (
                    selected_anomaly[
                        "recommendation"
                    ]
                )

            elif warning_anomalies:

                selected_anomaly = (
                    warning_anomalies[0]
                )

                result["status"] = "warning"

                result["likely_cause"] = (
                    selected_anomaly[
                        "likely_cause"
                    ]
                )

                result["recommendation"] = (
                    selected_anomaly[
                        "recommendation"
                    ]
                )

        # 14. Inverter status
        inverter_status = (
            hardware_detector.inverter_status(
                raw_data.inverter.status_code
            )
        )

        # 15. Control recommendation for non-fault operation
        if not hardware_anomalies:

            anomaly_present = bool(
                result.iloc[0]["anomaly"]
            )

            if not anomaly_present:

                ml_scenario = (
                    result.iloc[0].get(
                        "ml_scenario"
                    )
                )

                ml_confidence = float(
                    result.iloc[0].get(
                        "ml_confidence",
                        0.0,
                    )
                )

                if (
                    ml_confidence
                    < self.ML_CONFIDENCE_THRESHOLD
                ):
                    ml_scenario = None

                control = (
                    self.control_recommender.recommend(
                        raw_data,
                        predicted_generation=(
                            predicted_generation
                        ),
                        scenario=ml_scenario,
                        hardware_anomalies=[],
                    )
                )

                if (
                    control["recommendation"]
                    is not None
                ):

                    result["recommendation"] = (
                        control[
                            "recommendation"
                        ]
                    )

                    result["control_action"] = (
                        control[
                            "control_action"
                        ]
                    )

                    result[
                        "control_confidence"
                    ] = control[
                        "confidence"
                    ]

                    if (
                        control[
                            "control_action"
                        ]
                        == "MAINTAIN"
                    ):
                        result["recommendation"] = (
                            self.NORMAL_RECOMMENDATION
                        )

        # 16. Store internal values
        result["inverter_status"] = (
            inverter_status
        )

        result["installation_id"] = (
            raw_data.installation_id
        )

        return result

    def build_final_output(
        self,
        dataframe,
    ) -> FinalOutput:

        if dataframe.empty:
            raise ValueError(
                "Cannot create output from empty data."
            )

        row = dataframe.iloc[-1]

        energy_readings = EnergyReadings(
            solar_generation=float(
                row["solar_generation"]
            ),
            energy_consumption=float(
                row["energy_consumption"]
            ),
            grid_import=float(
                row["grid_import"]
            ),
            grid_export=float(
                row["grid_export"]
            ),
            battery_charge=float(
                row["battery_charge"]
            ),
            battery_discharge=float(
                row["battery_discharge"]
            ),
            inverter_status=str(
                row["inverter_status"]
            ),
        )

        intelligence_output = IntelligenceResult(
            predicted_generation=float(
                row["predicted_generation"]
            ),
            expected_generation=float(
                row["expected_generation"]
            ),
            actual_generation=float(
                row["actual_generation"]
            ),
            performance_loss=float(
                row["performance_loss"]
            ),
            health_score=float(
                row["health_score"]
            ),
            status=str(
                row["status"]
            ),
            anomaly=bool(
                row["anomaly"]
            ),
            likely_cause=(
                None
                if pd.isna(
                    row["likely_cause"]
                )
                else str(
                    row["likely_cause"]
                )
            ),
            recommendation=str(
                row["recommendation"]
            ),
        )

        hardware_anomalies = row.get(
            "hardware_anomalies",
            [],
        )

        if not isinstance(
            hardware_anomalies,
            list,
        ):
            hardware_anomalies = []

        return FinalOutput(
            energy_readings=energy_readings,
            intelligence_output=(
                intelligence_output
            ),
            hardware_anomalies=(
                hardware_anomalies
            ),
        )

    def api_output(
        self,
        dataframe,
    ):

        if dataframe.empty:
            raise ValueError(
                "Cannot create output from empty data."
            )

        row = dataframe.iloc[-1]

        return IntelligenceOutput(
            predicted_generation=float(
                row["predicted_generation"]
            ),
            expected_generation=float(
                row["expected_generation"]
            ),
            actual_generation=float(
                row["actual_generation"]
            ),
            performance_loss=float(
                row["performance_loss"]
            ),
            health_score=float(
                row["health_score"]
            ),
            status=str(
                row["status"]
            ),
            anomaly=bool(
                row["anomaly"]
            ),
            likely_cause=(
                None
                if pd.isna(
                    row["likely_cause"]
                )
                else str(
                    row["likely_cause"]
                )
            ),
            recommendation=str(
                row["recommendation"]
            ),
        )

    def generate_alerts(
        self,
        dataframe,
        installation_id: str,
    ):

        alert_generator = AlertGenerator()

        return alert_generator.generate(
            dataframe,
            installation_id,
        )

    def build_api_response(
        self,
        dataframe,
        installation_id: str,
    ):

        intelligence = self.api_output(
            dataframe
        )

        alerts = self.generate_alerts(
            dataframe,
            installation_id,
        )

        return {
            "intelligence": (
                intelligence.model_dump()
            ),
            "alerts": alerts,
        }

    def run_raw(
        self,
        raw_data: RawIoTData,
        capacity: float,
        historical_dataframe=None,
    ) -> FinalOutput:

        result = self.analyze_raw(
            raw_data,
            capacity=capacity,
            historical_dataframe=(
                historical_dataframe
            ),
        )

        return self.build_final_output(
            result
        )

    def run(
        self,
        dataframe,
        capacity: float,
        installation_id: str,
        baseline_dataframe=None,
    ):

        result = self.analyze(
            dataframe,
            capacity=capacity,
            baseline_dataframe=(
                baseline_dataframe
            ),
        )

        return self.build_api_response(
            result,
            installation_id,
        )