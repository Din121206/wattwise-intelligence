from app.output_models import (
    EnergyReadings,
    IntelligenceResult,
    FinalOutput,
)


def test_energy_readings():
    result = EnergyReadings(
        solar_generation=4.19,
        energy_consumption=3.2,
        grid_import=0.0,
        grid_export=0.0,
        battery_charge=0.2167,
        battery_discharge=0.0,
        inverter_status="normal",
    )

    assert result.solar_generation == 4.19
    assert result.energy_consumption == 3.2
    assert result.battery_charge == 0.2167
    assert result.inverter_status == "normal"


def test_intelligence_result():
    result = IntelligenceResult(
        predicted_generation=4.8,
        expected_generation=4.8,
        actual_generation=4.19,
        performance_loss=12.71,
        health_score=87.29,
        status="healthy",
        anomaly=True,
        likely_cause="Possible panel soiling",
        recommendation="Inspect and clean the solar panels.",
    )

    assert result.predicted_generation == 4.8
    assert result.health_score == 87.29
    assert result.anomaly is True
    assert result.likely_cause == "Possible panel soiling"


def test_final_output():
    result = FinalOutput(
        energy_readings=EnergyReadings(
            solar_generation=4.19,
            energy_consumption=3.2,
            grid_import=0.0,
            grid_export=0.0,
            battery_charge=0.2167,
            battery_discharge=0.0,
            inverter_status="normal",
        ),
        intelligence_output=IntelligenceResult(
            predicted_generation=4.8,
            expected_generation=4.8,
            actual_generation=4.19,
            performance_loss=12.71,
            health_score=87.29,
            status="healthy",
            anomaly=True,
            likely_cause="Possible panel soiling",
            recommendation="Inspect and clean the solar panels.",
        ),
    )

    output = result.model_dump()

    assert "energy_readings" in output
    assert "intelligence_output" in output


def test_battery_soc_is_not_in_output():
    result = FinalOutput(
        energy_readings=EnergyReadings(
            solar_generation=4.19,
            energy_consumption=3.2,
            grid_import=0.0,
            grid_export=0.0,
            battery_charge=0.2167,
            battery_discharge=0.0,
            inverter_status="normal",
        ),
        intelligence_output=IntelligenceResult(
            predicted_generation=4.8,
            expected_generation=4.8,
            actual_generation=4.19,
            performance_loss=12.71,
            health_score=87.29,
            status="healthy",
            anomaly=True,
            likely_cause="Possible panel soiling",
            recommendation="Inspect and clean the solar panels.",
        ),
    )

    output = result.model_dump()

    assert "battery_soc" not in output
    assert "battery_soc" not in output["energy_readings"]
    assert "battery_soc" not in output["intelligence_output"]