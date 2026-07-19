from datetime import datetime
from enum import Enum
from uuid import uuid4
from sqlalchemy import Boolean, DateTime, Enum as SqlEnum, Float, ForeignKey, Integer, JSON, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


def uuid() -> str:
    return str(uuid4())


class Timestamped:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class DocumentStatus(str, Enum):
    uploaded = "uploaded"
    processing = "processing"
    ready = "ready"
    failed = "failed"


class TaskStatus(str, Enum):
    todo = "todo"
    complete = "complete"
    skipped = "skipped"


class User(Timestamped, Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(100))
    timezone: Mapped[str] = mapped_column(String(64), default="UTC", nullable=False)
    subjects: Mapped[list["Subject"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    documents: Mapped[list["Document"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    simulations: Mapped[list["Simulation"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Subject(Timestamped, Base):
    __tablename__ = "subjects"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    code: Mapped[str | None] = mapped_column(String(50))
    color: Mapped[str | None] = mapped_column(String(7))
    target_grade: Mapped[float | None] = mapped_column(Float)
    user: Mapped[User] = relationship(back_populates="subjects")
    topics: Mapped[list["Topic"]] = relationship(back_populates="subject", cascade="all, delete-orphan")
    study_sessions: Mapped[list["StudySession"]] = relationship(back_populates="subject")
    tasks: Mapped[list["Task"]] = relationship(back_populates="subject")
    __table_args__ = (UniqueConstraint("user_id", "name", name="uq_subject_user_name"),)


class Topic(Timestamped, Base):
    __tablename__ = "topics"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid)
    subject_id: Mapped[str] = mapped_column(ForeignKey("subjects.id"), index=True, nullable=False)
    parent_topic_id: Mapped[str | None] = mapped_column(ForeignKey("topics.id"))
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    importance: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)
    last_reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    subject: Mapped[Subject] = relationship(back_populates="topics")
    parent: Mapped["Topic | None"] = relationship(remote_side="Topic.id")


class Document(Timestamped, Base):
    __tablename__ = "documents"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    subject_id: Mapped[str | None] = mapped_column(ForeignKey("subjects.id"))
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_key: Mapped[str] = mapped_column(String(500), unique=True, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[DocumentStatus] = mapped_column(SqlEnum(DocumentStatus), default=DocumentStatus.uploaded, nullable=False)
    user: Mapped[User] = relationship(back_populates="documents")
    insight: Mapped["DocumentInsight | None"] = relationship(back_populates="document", uselist=False, cascade="all, delete-orphan")


class DocumentInsight(Timestamped, Base):
    __tablename__ = "document_insights"
    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id"), primary_key=True)
    course_name: Mapped[str | None] = mapped_column(String(150))
    page_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    extraction_method: Mapped[str] = mapped_column(String(50), nullable=False, default="text")
    extracted_text: Mapped[str] = mapped_column(Text, nullable=False)
    analysis_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False, default="heuristic-v1")
    document: Mapped[Document] = relationship(back_populates="insight")


class StudySession(Timestamped, Base):
    __tablename__ = "study_sessions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid)
    subject_id: Mapped[str] = mapped_column(ForeignKey("subjects.id"), index=True, nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    focus_score: Mapped[float | None] = mapped_column(Float)
    notes: Mapped[str | None] = mapped_column(Text)
    subject: Mapped[Subject] = relationship(back_populates="study_sessions")


class Revision(Timestamped, Base):
    __tablename__ = "revisions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid)
    topic_id: Mapped[str] = mapped_column(ForeignKey("topics.id"), index=True, nullable=False)
    revised_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    confidence_before: Mapped[float] = mapped_column(Float, nullable=False)
    confidence_after: Mapped[float] = mapped_column(Float, nullable=False)


class QuizAttempt(Timestamped, Base):
    __tablename__ = "quiz_attempts"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid)
    topic_id: Mapped[str] = mapped_column(ForeignKey("topics.id"), index=True, nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    max_score: Mapped[float] = mapped_column(Float, nullable=False)
    attempted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class Attendance(Timestamped, Base):
    __tablename__ = "attendance"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid)
    subject_id: Mapped[str] = mapped_column(ForeignKey("subjects.id"), index=True, nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    present: Mapped[bool] = mapped_column(Boolean, nullable=False)


class Task(Timestamped, Base):
    __tablename__ = "tasks"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid)
    subject_id: Mapped[str] = mapped_column(ForeignKey("subjects.id"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(250), nullable=False)
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    estimated_minutes: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[TaskStatus] = mapped_column(SqlEnum(TaskStatus), default=TaskStatus.todo, nullable=False)
    subject: Mapped[Subject] = relationship(back_populates="tasks")


class Simulation(Timestamped, Base):
    __tablename__ = "simulations"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    scenario: Mapped[dict] = mapped_column(JSON, nullable=False)
    prediction: Mapped[dict] = mapped_column(JSON, nullable=False)
    user: Mapped[User] = relationship(back_populates="simulations")


class MentorMessage(Timestamped, Base):
    __tablename__ = "mentor_messages"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    role: Mapped[str] = mapped_column(String(16), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    mode: Mapped[str] = mapped_column(String(50), nullable=False, default="Beginner")
    metadata_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
