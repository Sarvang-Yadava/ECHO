from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from math import exp
from statistics import mean

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.digital_twin import Document, DocumentInsight, DocumentStatus, Subject, Task, Topic, User
from app.schemas.twin import DashboardResponse, DeadlineItem, GraphEdge, GraphNode, StudentProfile, TimelineItem, TopicSummary, TwinResponse, CourseSummary, DocumentListItem
from app.services.prediction import predict_scenario


def _document_rows(db: Session, user: User) -> list[tuple[Document, DocumentInsight | None, Subject | None]]:
    rows = (
        db.execute(
            select(Document, DocumentInsight, Subject)
            .outerjoin(DocumentInsight, DocumentInsight.document_id == Document.id)
            .outerjoin(Subject, Subject.id == Document.subject_id)
            .where(Document.user_id == user.id)
            .order_by(Document.created_at.desc())
        )
        .all()
    )
    return [(document, insight, subject) for document, insight, subject in rows]


def _topic_rows(db: Session, user: User) -> list[tuple[Subject, Topic]]:
    rows = (
        db.execute(select(Subject, Topic).join(Topic, Topic.subject_id == Subject.id).where(Subject.user_id == user.id)).all()
    )
    return [(subject, topic) for subject, topic in rows]


def build_twin_snapshot(db: Session, user: User) -> dict:
    documents = _document_rows(db, user)
    topics = _topic_rows(db, user)
    tasks = list(db.scalars(select(Task).join(Subject, Subject.id == Task.subject_id).where(Subject.user_id == user.id).order_by(Task.due_at.is_(None), Task.due_at)))
    documents_count = len(documents)
    active_courses = len({subject.id for subject, _topic in topics}) or len({subject.id for _doc, _insight, subject in documents if subject})

    course_map: dict[str, dict] = defaultdict(lambda: {"topic_count": 0, "assignment_count": 0, "exam_count": 0, "confidence": []})
    for subject, topic in topics:
        bucket = course_map[subject.id]
        bucket["id"] = subject.id
        bucket["name"] = subject.name
        bucket["code"] = subject.code
        bucket["topic_count"] += 1
        bucket["confidence"].append(topic.confidence)

    for document, insight, subject in documents:
        if insight and insight.analysis_json:
            target = subject.id if subject else insight.course_name or document.filename
            bucket = course_map[target]
            bucket["id"] = subject.id if subject else target
            bucket["name"] = subject.name if subject else (insight.course_name or document.filename)
            bucket["code"] = subject.code if subject else None
            bucket["assignment_count"] += len(insight.analysis_json.get("assignments_mentioned", []))
            bucket["exam_count"] += len(insight.analysis_json.get("exam_dates", []))

    detected_courses = []
    for bucket in course_map.values():
        confidence_values = bucket.pop("confidence", [])
        detected_courses.append(
            CourseSummary(
                id=str(bucket.get("id")),
                name=str(bucket.get("name")),
                code=bucket.get("code"),
                confidence=round(mean(confidence_values), 1) if confidence_values else 42.0,
                topic_count=int(bucket.get("topic_count", 0)),
                assignment_count=int(bucket.get("assignment_count", 0)),
                exam_count=int(bucket.get("exam_count", 0)),
            )
        )

    graph_nodes: list[GraphNode] = [GraphNode(id=user.id, label=user.display_name or user.email, type="student", value=None)]
    graph_edges: list[GraphEdge] = []
    for course in detected_courses:
        graph_nodes.append(GraphNode(id=course.id, label=course.name, type="course", value=course.confidence))
        graph_edges.append(GraphEdge(source=user.id, target=course.id, relation="studies"))
    for subject, topic in topics:
        node_id = f"topic:{topic.id}"
        graph_nodes.append(GraphNode(id=node_id, label=topic.name, type="topic", value=topic.confidence))
        graph_edges.append(GraphEdge(source=subject.id, target=node_id, relation="contains"))
        if topic.parent_topic_id:
            graph_edges.append(GraphEdge(source=f"topic:{topic.parent_topic_id}", target=node_id, relation="prerequisite"))

    topic_summaries = [TopicSummary(name=topic.name, course=subject.name, confidence=topic.confidence, importance=topic.importance) for subject, topic in topics]
    topic_summaries.sort(key=lambda item: item.confidence)
    weak_topics = topic_summaries[:5]
    strong_topics = sorted(topic_summaries, key=lambda item: item.confidence, reverse=True)[:5]

    now = datetime.now(timezone.utc)
    def retained(topic: Topic, days: int = 0) -> float:
        anchor = topic.last_reviewed_at or topic.updated_at or topic.created_at
        if anchor.tzinfo is None:
            anchor = anchor.replace(tzinfo=timezone.utc)
        elapsed = max(0, (now - anchor).total_seconds() / 86400) + days
        return round(max(0, topic.confidence * exp(-0.085 * elapsed)), 1)

    revision_timeline = [
        TimelineItem(label=topic.name, date=(topic.last_reviewed_at.isoformat() if topic.last_reviewed_at else "now"), detail=f"Confidence {topic.confidence:.0f}%", kind="revision")
        for subject, topic in sorted(topics, key=lambda row: row[1].confidence)
    ][:5]
    deadlines: list[DeadlineItem] = []
    for task in tasks:
        due_text = task.due_at.isoformat() if task.due_at else "TBD"
        deadlines.append(DeadlineItem(title=task.title, due_date=due_text, priority=task.status.value, source="task"))
    for document, insight, subject in documents:
        if insight:
            for exam_date in insight.analysis_json.get("exam_dates", []):
                deadlines.append(DeadlineItem(title=f"{insight.course_name or document.filename} exam", due_date=exam_date, priority="exam", source=document.filename))

    current_confidence = round(mean([retained(topic) for _subject, topic in topics]), 1) if topics else 42.0
    study_hours_default = max(1.5, len(topics) * 0.5 + len(documents) * 0.3)
    prediction = predict_scenario(user, {"study_hours_per_day": study_hours_default, "days_skipped": 0, "attendance": 85, "exam_date": None})
    academic_health = prediction["academic_health"] if isinstance(prediction, dict) else current_confidence
    memory_decay = []
    for subject, topic in sorted(topics, key=lambda row: retained(row[1]))[:6]:
        memory_decay.append({"topic": topic.name, "course": subject.name, "today": retained(topic), "tomorrow": retained(topic, 1), "three_days": retained(topic, 3), "one_week": retained(topic, 7), "two_weeks": retained(topic, 14)})
    future_timeline = []
    for item in sorted(deadlines, key=lambda x: x.due_date):
        future_timeline.append(TimelineItem(label=item.title, date=item.due_date, detail=f"{item.priority} priority · {item.source}", kind="deadline"))
    for subject, topic in topics:
        for day, label in ((1, "Tomorrow"), (3, "In 3 days"), (7, "In 1 week")):
            if retained(topic, day) < 60:
                future_timeline.append(TimelineItem(label=f"Review {topic.name}", date=label, detail=f"Memory projected to {retained(topic, day):.0f}%", kind="memory")); break
    future_timeline = future_timeline[:8]
    dna = {"memory_strength": round(mean([retained(topic) for _, topic in topics]), 1) if topics else 0, "confidence": current_confidence, "curiosity_score": round(min(100, 35 + len(documents) * 9 + len(topics) * 2.5), 1), "revision_momentum": round(min(100, 25 + sum(1 for _, topic in topics if topic.last_reviewed_at) * 12), 1), "burnout_risk": round(max(0, 62 - prediction["academic_health"] * .45 + len(deadlines) * 3), 1), "learning_velocity": round(min(100, 20 + len(topics) * 4 + len(documents) * 7), 1)}
    health_factors = [{"label": "Confidence", "value": current_confidence, "detail": "Decay-adjusted topic confidence"}, {"label": "Memory retention", "value": prediction.get("memory_retention", current_confidence), "detail": "Projected retention with current study habits"}, {"label": "Attendance", "value": 85.0, "detail": "Use the simulator to personalize this factor"}, {"label": "Deadline pressure", "value": max(0, 100 - len(deadlines) * 9), "detail": f"{len(deadlines)} extracted academic events"}]

    profile = StudentProfile(
        display_name=user.display_name or "Student",
        email=user.email,
        timezone=user.timezone,
        documents_uploaded=documents_count,
        active_courses=active_courses,
    )
    payload = {
        "has_data": bool(documents or topics),
        "student_profile": profile.model_dump(),
        "detected_courses": [course.model_dump() for course in detected_courses],
        "knowledge_graph": {"nodes": [node.model_dump() for node in graph_nodes], "edges": [edge.model_dump() for edge in graph_edges]},
        "current_confidence": current_confidence,
        "weak_topics": [topic.model_dump() for topic in weak_topics],
        "strong_topics": [topic.model_dump() for topic in strong_topics],
        "revision_timeline": [item.model_dump() for item in revision_timeline],
        "upcoming_deadlines": [item.model_dump() for item in deadlines[:6]],
        "academic_health": round(float(academic_health), 1),
        "recommended_study_load": float(prediction["recommended_study_load"]),
        "learning_dna": dna,
        "memory_decay": memory_decay,
        "future_timeline": [item.model_dump() for item in future_timeline],
        "academic_health_factors": health_factors,
    }
    return payload


def build_dashboard_snapshot(db: Session, user: User) -> dict:
    twin = build_twin_snapshot(db, user)
    documents = _document_rows(db, user)
    recent_documents = [
        DocumentListItem(
            id=document.id,
            filename=document.filename,
            course=(subject.name if subject else insight.course_name if insight else None),
            status=document.status,
            uploaded_date=document.created_at,
            page_count=insight.page_count if insight else 0,
            size_bytes=document.size_bytes,
            error_message=(insight.analysis_json.get("error") if insight and document.status == DocumentStatus.failed else None),
        ).model_dump()
        for document, insight, subject in documents
    ]
    onboarding_message = None if twin["has_data"] else "Upload your first syllabus to create your Digital Twin."
    return DashboardResponse(**twin, onboarding_message=onboarding_message, recent_documents=recent_documents).model_dump()
