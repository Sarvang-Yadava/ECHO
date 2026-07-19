from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.digital_twin import Attendance, Document, DocumentInsight, DocumentStatus, Revision, Simulation, StudySession, Subject, Task, TaskStatus, Topic, User

UPLOAD_ROOT = Path(__file__).resolve().parents[2] / "uploads"


def seed_demo_data(db: Session) -> None:
    if db.scalar(select(User).limit(1)) is not None:
        return

    demo_user = User(email="demo@echo.local", password_hash="demo", display_name="Aria", timezone="UTC")
    db.add(demo_user)
    db.flush()

    subjects = [
        Subject(user_id=demo_user.id, name="Biology 101", code="BIO101", target_grade=88, color="#8b5cf6"),
        Subject(user_id=demo_user.id, name="Calculus II", code="MTH204", target_grade=84, color="#06b6d4"),
        Subject(user_id=demo_user.id, name="Computer Systems", code="CSE220", target_grade=86, color="#f97316"),
    ]
    db.add_all(subjects)
    db.flush()

    now = datetime.now(UTC)
    subject_topics: dict[str, list[tuple[str, float, float]]] = {
        "Biology 101": [("Cell structure", 86, 0.9), ("DNA replication", 74, 0.8), ("Genetics", 68, 0.85)],
        "Calculus II": [("Integration techniques", 64, 0.95), ("Series and sequences", 58, 0.92), ("Applications of integrals", 72, 0.88)],
        "Computer Systems": [("Instruction sets", 81, 0.82), ("Memory hierarchy", 69, 0.9), ("Process scheduling", 63, 0.87)],
    }
    for subject in subjects:
        for index, (name, confidence, importance) in enumerate(subject_topics[subject.name]):
            db.add(Topic(subject_id=subject.id, name=name, confidence=confidence, importance=importance, last_reviewed_at=now - timedelta(days=index + 1)))

    tasks = [
        Task(subject_id=subjects[0].id, title="Biology lab report", due_at=now + timedelta(days=4), estimated_minutes=90, status=TaskStatus.todo),
        Task(subject_id=subjects[1].id, title="Calculus problem set", due_at=now + timedelta(days=6), estimated_minutes=120, status=TaskStatus.todo),
        Task(subject_id=subjects[2].id, title="Systems quiz review", due_at=now + timedelta(days=3), estimated_minutes=75, status=TaskStatus.todo),
    ]
    db.add_all(tasks)

    study_sessions = [
        StudySession(subject_id=subjects[0].id, started_at=now - timedelta(days=1, hours=2), duration_minutes=70, focus_score=82, notes="Reviewed mitosis and meiosis."),
        StudySession(subject_id=subjects[1].id, started_at=now - timedelta(days=2, hours=1), duration_minutes=95, focus_score=76, notes="Integration practice."),
        StudySession(subject_id=subjects[2].id, started_at=now - timedelta(days=3), duration_minutes=60, focus_score=79, notes="Memory paging notes."),
    ]
    db.add_all(study_sessions)

    attendances = [
        Attendance(subject_id=subjects[0].id, occurred_at=now - timedelta(days=2), present=True),
        Attendance(subject_id=subjects[1].id, occurred_at=now - timedelta(days=2), present=True),
        Attendance(subject_id=subjects[2].id, occurred_at=now - timedelta(days=1), present=False),
    ]
    db.add_all(attendances)

    sample_documents = [
        {
            "subject": subjects[0],
            "filename": "biology-syllabus.txt",
            "course_name": "Biology 101",
            "content": "Biology 101 Syllabus\nModule 1: Cell structure and organelles\nModule 2: DNA replication and transcription\nAssignment: Lab report due March 18\nMidterm exam: April 12\nFinal exam: May 24\nTopics: genetics, evolution, ecology",
            "analysis": {
                "course_name": "Biology 101",
                "topics": ["Cell structure", "DNA replication", "Genetics", "Evolution"],
                "modules": ["Module 1: Cell structure and organelles", "Module 2: DNA replication and transcription"],
                "important_concepts": ["Organelle function", "Transcription", "Ecology"],
                "assignments_mentioned": ["Lab report due March 18"],
                "exam_dates": ["April 12", "May 24"],
                "recommended_study_priority": "High",
            },
        },
        {
            "subject": subjects[1],
            "filename": "calculus-syllabus.txt",
            "course_name": "Calculus II",
            "content": "Calculus II Syllabus\nUnit 1: Integration techniques\nUnit 2: Series and sequences\nHomework: Problem set due March 21\nQuiz dates: April 5 and April 19\nFinal exam: May 30\nImportant concepts: substitution, partial fractions, convergence tests",
            "analysis": {
                "course_name": "Calculus II",
                "topics": ["Integration techniques", "Series and sequences", "Convergence tests"],
                "modules": ["Unit 1: Integration techniques", "Unit 2: Series and sequences"],
                "important_concepts": ["Substitution", "Partial fractions", "Convergence"],
                "assignments_mentioned": ["Problem set due March 21"],
                "exam_dates": ["April 5", "April 19", "May 30"],
                "recommended_study_priority": "High",
            },
        },
    ]

    UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
    seed_user_root = UPLOAD_ROOT / demo_user.id
    seed_user_root.mkdir(parents=True, exist_ok=True)

    for item in sample_documents:
        storage_path = seed_user_root / f"{uuid4().hex}_{item['filename']}"
        storage_path.write_text(item["content"], encoding="utf-8")
        document = Document(
            user_id=demo_user.id,
            subject_id=item["subject"].id,
            filename=item["filename"],
            storage_key=str(storage_path.relative_to(UPLOAD_ROOT)),
            mime_type="text/plain",
            size_bytes=storage_path.stat().st_size,
            status=DocumentStatus.ready,
        )
        db.add(document)
        db.flush()
        db.add(
            DocumentInsight(
                document_id=document.id,
                course_name=item["course_name"],
                page_count=2,
                extraction_method="text",
                extracted_text=item["content"],
                analysis_json=item["analysis"],
                model_version="seed-v1",
            )
        )

    db.flush()
    biology_topic = db.scalar(select(Topic).where(Topic.subject_id == subjects[0].id).order_by(Topic.confidence.desc()))
    if biology_topic is not None:
        db.add(Revision(topic_id=biology_topic.id, revised_at=now - timedelta(days=1), confidence_before=71, confidence_after=86))

    db.add(Simulation(
        user_id=demo_user.id,
        scenario={"study_hours_per_day": 3.5, "days_skipped": 1, "attendance": 88, "exam_date": None},
        prediction={"knowledge_score": 78.2, "confidence": 81.5, "academic_health": 79.7, "recommended_study_load": 4.0, "explanation": "Seeded baseline"},
    ))

    db.commit()
