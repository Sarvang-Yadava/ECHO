"""Compatibility wrapper for the reusable prediction engine."""

from app.models.digital_twin import User
from app.services.prediction import predict_scenario


__all__ = ["predict_scenario", "User"]
