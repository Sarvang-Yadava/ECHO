from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field
from app.models.digital_twin import DocumentStatus


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    email: str
    display_name: str | None
    timezone: str


class SubjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    code: str | None = Field(default=None, max_length=50)
    color: str | None = Field(default=None, pattern=r"^#[0-9A-Fa-f]{6}$")
    target_grade: float | None = Field(default=None, ge=0, le=100)


class SubjectResponse(SubjectCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    created_at: datetime


class DocumentCreate(BaseModel):
    filename: str = Field(min_length=1, max_length=255)
    storage_key: str = Field(min_length=1, max_length=500)
    mime_type: str = Field(min_length=1, max_length=100)
    size_bytes: int = Field(ge=0)
    subject_id: str | None = None


class DocumentResponse(DocumentCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    status: DocumentStatus
    created_at: datetime


class DocumentListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    filename: str
    course: str | None
    status: DocumentStatus
    uploaded_date: datetime
    page_count: int
    size_bytes: int = 0
    error_message: str | None = None


class StructuredAnalysis(BaseModel):
    course_name: str | None = None
    topics: list[str] = Field(default_factory=list)
    modules: list[str] = Field(default_factory=list)
    important_concepts: list[str] = Field(default_factory=list)
    assignments_mentioned: list[str] = Field(default_factory=list)
    exam_dates: list[str] = Field(default_factory=list)
    recommended_study_priority: str = "Medium"
    subject_code: str | None = None
    instructor: str | None = None
    semester: str | None = None
    academic_year: str | None = None
    learning_outcomes: list[str] = Field(default_factory=list)
    references: list[str] = Field(default_factory=list)
    topic_hierarchy: list[dict] = Field(default_factory=list)
    timeline_events: list[dict] = Field(default_factory=list)


class DocumentDetailResponse(DocumentListItem):
    mime_type: str
    storage_key: str
    extracted_text: str
    analysis: StructuredAnalysis
    updated_at: datetime


class DocumentUploadResponse(BaseModel):
    filename: str
    page_count: int
    extracted_text: str
    analysis: StructuredAnalysis
    document_id: str
    status: DocumentStatus


class ManualTopicCreate(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    module: str | None = Field(default=None, max_length=200)


class CourseSummary(BaseModel):
    id: str
    name: str
    code: str | None = None
    confidence: float
    topic_count: int
    assignment_count: int
    exam_count: int


class TopicSummary(BaseModel):
    name: str
    course: str
    confidence: float
    importance: float


class GraphNode(BaseModel):
    id: str
    label: str
    type: str
    value: float | None = None


class GraphEdge(BaseModel):
    source: str
    target: str
    relation: str


class TimelineItem(BaseModel):
    label: str
    date: str
    detail: str
    kind: str = "revision"


class DeadlineItem(BaseModel):
    title: str
    due_date: str
    priority: str
    source: str


class StudentProfile(BaseModel):
    display_name: str
    email: str
    timezone: str
    documents_uploaded: int
    active_courses: int


class TwinResponse(BaseModel):
    has_data: bool
    student_profile: StudentProfile
    detected_courses: list[CourseSummary]
    knowledge_graph: dict[str, list[GraphNode | GraphEdge]]
    current_confidence: float
    weak_topics: list[TopicSummary]
    strong_topics: list[TopicSummary]
    revision_timeline: list[TimelineItem]
    upcoming_deadlines: list[DeadlineItem]
    academic_health: float
    recommended_study_load: float
    learning_dna: dict[str, float] = Field(default_factory=dict)
    memory_decay: list[dict] = Field(default_factory=list)
    future_timeline: list[TimelineItem] = Field(default_factory=list)
    academic_health_factors: list[dict] = Field(default_factory=list)


class DashboardResponse(TwinResponse):
    onboarding_message: str | None = None
    recent_documents: list[DocumentListItem]


class SimulationRequest(BaseModel):
    study_hours_per_day: float = Field(ge=0, le=24)
    days_skipped: int = Field(ge=0, le=365)
    attendance: float = Field(ge=0, le=100)
    exam_date: date | None = None
    sleep_hours: float = Field(default=7, ge=0, le=16)
    revision_frequency: float = Field(default=3, ge=0, le=14)


class SimulationPrediction(BaseModel):
    knowledge_score: float
    confidence: float
    academic_health: float
    recommended_study_load: float
    explanation: str
    model_version: str
    expected_exam_score: float = 0
    memory_retention: float = 0
    stress: float = 0


class MentorChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    mode: str = Field(default="Beginner", max_length=50)
    action: str | None = Field(default=None, max_length=50)


class MentorChatResponse(BaseModel):
    answer: str
    sources: list[str] = Field(default_factory=list)
    confidence: float
    citations: list[dict] = Field(default_factory=list)
    recommendations: dict = Field(default_factory=dict)
    reasoning: list[str] = Field(default_factory=list)
    follow_ups: list[str] = Field(default_factory=list)


class SimulationCreate(BaseModel):
    scenario: dict = Field(description="User-selected study-habit changes")


class SimulationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    scenario: dict
    prediction: dict
    created_at: datetime
