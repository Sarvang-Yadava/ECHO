from __future__ import annotations

from datetime import date, datetime
from math import isfinite

from app.models.digital_twin import Topic, User


def clamp(value: float, minimum: float = 0.0, maximum: float = 100.0) -> float:
    return max(minimum, min(maximum, value))


def _topic_baseline(user: User) -> float:
    topics = [topic.confidence for subject in user.subjects for topic in subject.topics]
    if not topics:
        return 42.0
    return sum(topics) / len(topics)


def predict_scenario(user: User, scenario: dict) -> dict:
    study_hours_per_day = float(scenario.get("study_hours_per_day", 0) or 0)
    days_skipped = int(scenario.get("days_skipped", 0) or 0)
    attendance = float(scenario.get("attendance", 0) or 0)
    sleep_hours = float(scenario.get("sleep_hours", 7) or 0)
    revision_frequency = float(scenario.get("revision_frequency", 3) or 0)
    exam_date_value = scenario.get("exam_date")
    exam_days = 14
    if isinstance(exam_date_value, str):
        try:
            exam_days = max(0, (date.fromisoformat(exam_date_value) - datetime.utcnow().date()).days)
        except ValueError:
            exam_days = 14

    topic_baseline = _topic_baseline(user)
    document_bonus = min(18.0, len(user.documents) * 3.0)
    attendance_component = attendance * 0.35
    study_component = study_hours_per_day * 8.5
    continuity_penalty = days_skipped * 3.2
    urgency_bonus = max(0.0, 18 - exam_days) * 1.35
    sleep_component = max(-12.0, 8 - abs(sleep_hours - 7.5) * 3.5)
    revision_component = min(14.0, revision_frequency * 2.3)

    knowledge_score = clamp(topic_baseline * 0.42 + attendance_component + study_component + document_bonus - continuity_penalty + urgency_bonus + revision_component * .35)
    confidence = clamp(knowledge_score * 0.9 + attendance * 0.08 - days_skipped * 1.6 + sleep_component * .25)
    memory_retention = clamp(topic_baseline + revision_component - days_skipped * 2.1 + sleep_component * .5)
    stress = clamp(38 + days_skipped * 5 + max(0, 7 - sleep_hours) * 7 + max(0, 10 - exam_days) * 3 - study_hours_per_day * 1.2)
    academic_health = clamp((knowledge_score + confidence + attendance + memory_retention + (100 - stress)) / 5)
    recommended_study_load = round(clamp((100 - knowledge_score) / 9 + days_skipped * 0.45 + max(0.0, 12 - exam_days) * 0.35, 0.0, 12.0), 1)

    return {
        "status": "ready" if user.subjects or user.documents else "insufficient_data",
        "knowledge_score": round(knowledge_score, 1),
        "confidence": round(confidence, 1),
        "academic_health": round(academic_health, 1),
        "recommended_study_load": recommended_study_load,
        "explanation": (
            f"Attendance contributes {attendance_component:.0f} points; {study_hours_per_day:g} study hours/day and "
            f"{revision_frequency:g} weekly revisions raise knowledge retention, while {days_skipped} skipped days "
            f"and sleep at {sleep_hours:g}h {'increase' if sleep_hours < 7 else 'reduce'} risk."
        ),
        "model_version": "twin-forecast-v3",
        "expected_exam_score": round(clamp(knowledge_score * .68 + confidence * .32), 1),
        "memory_retention": round(memory_retention, 1),
        "stress": round(stress, 1),
        "scenario_inputs": scenario,
    }
