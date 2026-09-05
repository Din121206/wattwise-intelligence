"""
WattWise Module 2
Solar system health score calculation.
"""


class HealthCalculator:

    def calculate(self, performance_loss: float) -> float:

        if performance_loss < 0:
            raise ValueError("Performance loss cannot be negative.")

        if performance_loss > 100:
            performance_loss = 100

        # Health is inversely related to performance loss
        health_score = 100 - performance_loss

        return round(health_score, 2)

    def status(self, health_score: float) -> str:

        if health_score >= 80:
            return "healthy"

        if health_score >= 60:
            return "warning"

        return "critical"