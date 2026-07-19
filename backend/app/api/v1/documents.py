from datetime import datetime
from pathlib import Path
from uuid import uuid4
import shutil

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.models.digital_twin import Document, DocumentInsight, DocumentStatus, Subject, Task, Topic
from app.schemas.twin import DocumentCreate, DocumentDetailResponse, DocumentListItem, DocumentResponse, DocumentUploadResponse, ManualTopicCreate, StructuredAnalysis
from app.services.analysis import analyze_academic_document
from app.services.digital_twin import initialize_from_analysis
from app.services.extraction import extract_document

router = APIRouter(prefix="/documents", tags=["documents"])

UPLOAD_ROOT = Path(__file__).resolve().parents[3] / "uploads"
SUPPORTED_SUFFIXES = {".pdf", ".docx", ".txt", ".png", ".jpg", ".jpeg"}


@router.get("", response_model=list[DocumentListItem])
def list_documents(current_user: CurrentUser, db: DbSession) -> list[DocumentListItem]:
    rows = (
        db.execute(
            select(Document, DocumentInsight, Subject)
            .outerjoin(DocumentInsight, DocumentInsight.document_id == Document.id)
            .outerjoin(Subject, Subject.id == Document.subject_id)
            .where(Document.user_id == current_user.id)
            .order_by(Document.created_at.desc())
        )
        .all()
    )
    return [_document_list_item(document, insight, subject) for document, insight, subject in rows]


@router.get("/{document_id}", response_model=DocumentDetailResponse)
def get_document(document_id: str, current_user: CurrentUser, db: DbSession) -> DocumentDetailResponse:
    document, insight, subject = _get_document_row(db, current_user.id, document_id)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return _document_detail(document, insight, subject)


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def register_document(payload: DocumentCreate, current_user: CurrentUser, db: DbSession) -> Document:
    if payload.subject_id:
        subject = db.get(Subject, payload.subject_id)
        if not subject or subject.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")
    document = Document(user_id=current_user.id, **payload.model_dump())
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    current_user: CurrentUser,
    db: DbSession,
    file: UploadFile = File(...),
    subject_id: str | None = Form(default=None),
) -> DocumentUploadResponse:
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A file is required")
    if Path(file.filename).suffix.lower() not in SUPPORTED_SUFFIXES:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Supported files: PDF, DOCX, TXT, PNG, JPG, JPEG")

    subject = _ensure_subject(db, current_user.id, subject_id, None) if subject_id else None

    UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
    storage_dir = UPLOAD_ROOT / current_user.id
    storage_dir.mkdir(parents=True, exist_ok=True)
    stored_name = f"{uuid4().hex}_{Path(file.filename).name}"
    storage_path = storage_dir / stored_name
    with storage_path.open("wb") as target:
        shutil.copyfileobj(file.file, target)

    document = Document(
        user_id=current_user.id,
        subject_id=subject.id if subject else subject_id,
        filename=file.filename,
        storage_key=str(storage_path.relative_to(UPLOAD_ROOT)),
        mime_type=file.content_type or "application/octet-stream",
        size_bytes=storage_path.stat().st_size,
        status=DocumentStatus.processing,
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    try:
        return _process_document(db, current_user.id, document, storage_path)
    except Exception as error:
        document.status = DocumentStatus.failed
        insight = db.get(DocumentInsight, document.id)
        if insight is None:
            insight = DocumentInsight(document_id=document.id, extracted_text="", analysis_json={})
            db.add(insight)
        insight.analysis_json = {"error": str(error), "pipeline_stage": "extraction_or_analysis"}
        db.commit()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Document processing failed: {error}") from error


@router.post("/{document_id}/reprocess", response_model=DocumentUploadResponse)
def reprocess_document(document_id: str, current_user: CurrentUser, db: DbSession) -> DocumentUploadResponse:
    document, insight, subject = _get_document_row(db, current_user.id, document_id)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    storage_path = UPLOAD_ROOT / document.storage_key
    if not storage_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stored file not found")
    document.status = DocumentStatus.processing
    db.commit()
    try:
        return _process_document(db, current_user.id, document, storage_path)
    except Exception as error:
        document.status = DocumentStatus.failed
        if insight:
            insight.analysis_json = {"error": str(error), "pipeline_stage": "extraction_or_analysis"}
        db.commit()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Document processing failed: {error}") from error


@router.post("/{document_id}/topics", response_model=DocumentDetailResponse)
def add_manual_topic(document_id: str, payload: ManualTopicCreate, current_user: CurrentUser, db: DbSession) -> DocumentDetailResponse:
    document, insight, subject = _get_document_row(db, current_user.id, document_id)
    if document is None or insight is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Processed document not found")
    analysis = dict(insight.analysis_json or {})
    topics = list(analysis.get("topics", []))
    if payload.name.casefold() not in {str(item).casefold() for item in topics}:
        topics.append(payload.name)
    analysis["topics"] = topics
    hierarchy = list(analysis.get("topic_hierarchy", []))
    if payload.module:
        target = next((item for item in hierarchy if str(item.get("name", "")).casefold() == payload.module.casefold()), None)
        if target is None:
            target = {"name": payload.module, "topics": []}; hierarchy.append(target)
        target["topics"] = list(dict.fromkeys([*target.get("topics", []), payload.name]))
    analysis["topic_hierarchy"] = hierarchy
    insight.analysis_json = analysis
    initialize_from_analysis(db, current_user.id, subject, analysis)
    db.commit()
    db.refresh(document)
    return _document_detail(document, insight, subject)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(document_id: str, current_user: CurrentUser, db: DbSession) -> None:
    document, insight, subject = _get_document_row(db, current_user.id, document_id)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    storage_path = UPLOAD_ROOT / document.storage_key
    db.delete(document)
    db.commit()
    if storage_path.exists():
        storage_path.unlink()


def _process_document(db, user_id: str, document: Document, storage_path: Path) -> DocumentUploadResponse:
    extracted_text, page_count, method = extract_document(storage_path)
    analysis = analyze_academic_document(extracted_text, document.filename)
    subject = _ensure_subject(db, user_id, document.subject_id, analysis.get("course_name"))
    if subject and document.subject_id != subject.id:
        document.subject_id = subject.id
    insight = db.get(DocumentInsight, document.id)
    if insight is None:
        insight = DocumentInsight(document_id=document.id)
        db.add(insight)
    insight.course_name = analysis.get("course_name")
    insight.page_count = page_count
    insight.extraction_method = method
    insight.extracted_text = extracted_text
    insight.analysis_json = analysis
    insight.model_version = "twin-pipeline-v2"
    initialize_from_analysis(db, user_id, subject, analysis)
    document.status = DocumentStatus.ready
    db.commit()
    db.refresh(document)
    return DocumentUploadResponse(
        filename=document.filename,
        page_count=page_count,
        extracted_text=extracted_text,
        analysis=StructuredAnalysis.model_validate(analysis),
        document_id=document.id,
        status=document.status,
    )


def _get_document_row(db, user_id: str, document_id: str):
    row = (
        db.execute(
            select(Document, DocumentInsight, Subject)
            .outerjoin(DocumentInsight, DocumentInsight.document_id == Document.id)
            .outerjoin(Subject, Subject.id == Document.subject_id)
            .where(Document.user_id == user_id, Document.id == document_id)
        )
        .first()
    )
    if row is None:
        return None, None, None
    return row


def _document_list_item(document: Document, insight: DocumentInsight | None, subject: Subject | None) -> DocumentListItem:
    return DocumentListItem(
        id=document.id,
        filename=document.filename,
        course=subject.name if subject else (insight.course_name if insight else None),
        status=document.status,
        uploaded_date=document.created_at,
        page_count=insight.page_count if insight else 0,
        size_bytes=document.size_bytes,
        error_message=(insight.analysis_json.get("error") if insight and document.status == DocumentStatus.failed else None),
    )


def _document_detail(document: Document, insight: DocumentInsight | None, subject: Subject | None) -> DocumentDetailResponse:
    analysis = StructuredAnalysis.model_validate(insight.analysis_json if insight else {})
    return DocumentDetailResponse(
        id=document.id,
        filename=document.filename,
        course=subject.name if subject else (insight.course_name if insight else None),
        status=document.status,
        uploaded_date=document.created_at,
        page_count=insight.page_count if insight else 0,
        error_message=(insight.analysis_json.get("error") if insight and document.status == DocumentStatus.failed else None),
        mime_type=document.mime_type,
        size_bytes=document.size_bytes,
        storage_key=document.storage_key,
        extracted_text=insight.extracted_text if insight else "",
        analysis=analysis,
        updated_at=document.updated_at,
    )


def _ensure_subject(db, user_id: str, subject_id: str | None, course_name: str | None) -> Subject | None:
    if subject_id:
        subject = db.get(Subject, subject_id)
        if not subject or subject.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")
        return subject
    if not course_name:
        return None
    subject = db.scalar(select(Subject).where(Subject.user_id == user_id, Subject.name == course_name))
    if subject:
        return subject
    subject = Subject(user_id=user_id, name=course_name)
    db.add(subject)
    db.flush()
    return subject


def _populate_subject_details(db, subject: Subject | None, analysis: dict) -> None:
    if subject is None:
        return
    existing_topics = {topic.name.casefold() for topic in subject.topics}
    ordered_topics = analysis.get("topics", []) + analysis.get("modules", []) + analysis.get("important_concepts", [])
    for index, topic_name in enumerate(ordered_topics):
        topic_text = str(topic_name).strip()
        if not topic_text or topic_text.casefold() in existing_topics:
            continue
        confidence = max(15.0, 72.0 - index * 4.0)
        importance = max(0.2, 0.95 - index * 0.08)
        db.add(Topic(subject_id=subject.id, name=topic_text, confidence=confidence, importance=importance))
    for exam_date in analysis.get("exam_dates", []):
        due_at = _parse_date(exam_date)
        db.add(Task(subject_id=subject.id, title=f"Prepare for {subject.name} exam", due_at=due_at, estimated_minutes=180 if due_at else None))
    for assignment in analysis.get("assignments_mentioned", []):
        db.add(Task(subject_id=subject.id, title=str(assignment).strip(), estimated_minutes=60))


def _parse_date(value: str):
    normalized = value.strip()
    for parser in (datetime.fromisoformat,):
        try:
            return parser(normalized)
        except ValueError:
            continue
    return None
