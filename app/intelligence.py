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


class IntelligenceEngine:

    def analyze(
        self,
        dataframe,
        capacity,
        baseline_dataframe=None
    ):
        forecaster = SolarForecaster(capacity)

        if baseline_dataframe is not None:
            result = forecaster.predict_from_baseline(
                baseline_dataframe,
                dataframe
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
            baseline_dataframe=baseline_dataframe
        )

        return result

    def analyze_raw(
        self,
        raw_data: RawIoTData,
        capacity: float,
        historical_dataframe=None
    ):
        if not isinstance(raw_data, RawIoTData):
            raise TypeError(
                "raw_data must be a RawIoTData object."
            )

        energy_calculator = EnergyCalculator()
        energy = energy_calculator.calculate(raw_data)

        generation_analyzer = GenerationAnalyzer(capacity)

        expected_generation = (
            generation_analyzer.expected_generation(raw_data)
        )

        actual_generation = energy["solar_generation"]

        if (
            historical_dataframe is not None
            and not historical_dataframe.empty
        ):
            predicted_generation = (
                generation_analyzer.next_hour_prediction(
                    historical_dataframe,
                    raw_data.timestamp
                )
            )
        else:
            predicted_generation = expected_generation

        result = pd.DataFrame([{
            "timestamp": raw_data.timestamp,
            "solar_generation": actual_generation,
            "energy_consumption": energy["energy_consumption"],
            "grid_import": energy["grid_import"],
            "grid_export": energy["grid_export"],
            "battery_charge": energy["battery_charge"],
            "battery_discharge": energy["battery_discharge"],
            "weather": "unknown",
            "system_efficiency": 100.0,
            "predicted_generation": predicted_generation,
            "expected_generation": expected_generation,
            "actual_generation": actual_generation
        }])

        performance = PerformanceAnalyzer()
        result = performance.compare(result)

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
        result = recommender.generate(result)

        hardware_detector = HardwareAnomalyDetector()

        hardware_anomalies = hardware_detector.detect(
            raw_data,
            expected_generation=expected_generation,
            actual_generation=actual_generation
        )

        result["hardware_anomalies"] = [
            hardware_anomalies
        ]

        # ---------------------------------------------------------
        # Merge hardware safety anomalies into the main status.
        #
        # Priority:
        # critical > warning > existing performance status
        # ---------------------------------------------------------

        if hardware_anomalies:
            result["anomaly"] = True

            critical_anomalies = [
                anomaly
                for anomaly in hardware_anomalies
                if anomaly["severity"] == "critical"
            ]

            warning_anomalies = [
                anomaly
                for anomaly in hardware_anomalies
                if anomaly["severity"] == "warning"
            ]

            if critical_anomalies:
                selected_anomaly = critical_anomalies[0]

                result["status"] = "critical"
                result["likely_cause"] = (
                    selected_anomaly["likely_cause"]
                )
                result["recommendation"] = (
                    selected_anomaly["recommendation"]
                )

            elif warning_anomalies:
                selected_anomaly = warning_anomalies[0]

                result["status"] = "warning"
                result["likely_cause"] = (
                    selected_anomaly["likely_cause"]
                )
                result["recommendation"] = (
                    selected_anomaly["recommendation"]
                )

        inverter_status = hardware_detector.inverter_status(
            raw_data.inverter.status_code
        )

        result["inverter_status"] = inverter_status
        result["installation_id"] = raw_data.installation_id

        return result

    def build_final_output(self, dataframe) -> FinalOutput:
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
            )
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
                if pd.isna(row["likely_cause"])
                else str(row["likely_cause"])
            ),
            recommendation=str(
                row["recommendation"]
            )
        )

        hardware_anomalies = row.get(
            "hardware_anomalies",
            []
        )

        if not isinstance(
            hardware_anomalies,
            list
        ):
            hardware_anomalies = []

        return FinalOutput(
            energy_readings=energy_readings,
            intelligence_output=intelligence_output,
            hardware_anomalies=hardware_anomalies
        )

    def api_output(self, dataframe):
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
                if pd.isna(row["likely_cause"])
                else str(row["likely_cause"])
            ),
            recommendation=str(
                row["recommendation"]
            )
        )

    def generate_alerts(
        self,
        dataframe,
        installation_id: str
    ):
        alert_generator = AlertGenerator()

        return alert_generator.generate(
            dataframe,
            installation_id
        )

    def build_api_response(
        self,
        dataframe,
        installation_id: str
    ):
        intelligence = self.api_output(dataframe)

        alerts = self.generate_alerts(
            dataframe,
            installation_id
        )

        return {
            "intelligence": intelligence.model_dump(),
            "alerts": alerts
        }

    def run_raw(
        self,
        raw_data: RawIoTData,
        capacity: float,
        historical_dataframe=None
    ) -> FinalOutput:

        result = self.analyze_raw(
            raw_data,
            capacity=capacity,
            historical_dataframe=historical_dataframe
        )

        return self.build_final_output(
            result
        )

    def run(
        self,
        dataframe,
        capacity: float,
        installation_id: str,
        baseline_dataframe=None
    ):
        result = self.analyze(
            dataframe,
            capacity=capacity,
            baseline_dataframe=baseline_dataframe
        )

        return self.build_api_response(
            result,
            installation_id
        )