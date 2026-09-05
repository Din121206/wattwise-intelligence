import pytest

from app.health import HealthCalculator


def test_health_score():
    calculator = HealthCalculator()

    assert calculator.calculate(10) == 90


def test_zero_loss():
    calculator = HealthCalculator()

    assert calculator.calculate(0) == 100


def test_health_score_with_high_loss():
    calculator = HealthCalculator()

    assert calculator.calculate(50) == 50


def test_healthy_status():
    calculator = HealthCalculator()

    assert calculator.status(90) == "healthy"


def test_warning_status():
    calculator = HealthCalculator()

    assert calculator.status(70) == "warning"


def test_critical_status():
    calculator = HealthCalculator()

    assert calculator.status(40) == "critical"


def test_negative_loss():
    calculator = HealthCalculator()

    with pytest.raises(ValueError):
        calculator.calculate(-10)