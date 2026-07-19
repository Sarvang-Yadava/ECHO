from __future__ import annotations

from sqlalchemy import select

from app.models.digital_twin import Subject, Task, Topic
from app.services.timeline import parse_event_date


def initialize_from_analysis(db, user_id: str, subject: Subject | None, analysis: dict) -> None:
    """Materialize the analysis into the student's editable Digital Twin."""
    if subject is None:
        return
    if analysis.get("subject_code") and not subject.code:
        subject.code = analysis["subject_code"]
    existing = {topic.name.casefold(): topic for topic in subject.topics}
    hierarchy = analysis.get("topic_hierarchy", [])
    for module_index, module in enumerate(hierarchy):
        module_name = str(module.get("name", "")).strip()
        if not module_name:
            continue
        parent = existing.get(module_name.casefold())
        if not parent:
            parent = Topic(subject_id=subject.id, name=module_name, confidence=max(30, 64 - module_index * 3), importance=.9)
            db.add(parent); db.flush(); existing[module_name.casefold()] = parent
        for topic_index, name in enumerate(module.get("topics", [])):
            name = str(name).strip()
            if not name or name.casefold() in existing:
                continue
            child = Topic(subject_id=subject.id, parent_topic_id=parent.id, name=name, confidence=max(20, 56 - topic_index * 3), importance=.75)
            db.add(child); existing[name.casefold()] = child
    for name in analysis.get("topics", []):
        name = str(name).strip()
        if name and name.casefold() not in existing:
            db.add(Topic(subject_id=subject.id, name=name, confidence=52, importance=.65)); existing[name.casefold()] = True
    known_tasks = set(db.scalars(select(Task.title).where(Task.subject_id == subject.id)))
    for event in analysis.get("timeline_events", []):
        title = event.get("event", "Academic deadline")
        if title in known_tasks:
            continue
        db.add(Task(subject_id=subject.id, title=title, due_at=parse_event_date(event.get("date", "")), estimated_minutes=120))
