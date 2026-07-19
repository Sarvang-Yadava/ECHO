from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from app.api.deps import CurrentUser, DbSession
from app.models.digital_twin import Subject
from app.schemas.twin import SubjectCreate, SubjectResponse

router = APIRouter(prefix="/subjects", tags=["subjects"])


@router.get("", response_model=list[SubjectResponse])
def list_subjects(current_user: CurrentUser, db: DbSession) -> list[Subject]:
    return list(db.scalars(select(Subject).where(Subject.user_id == current_user.id).order_by(Subject.name)))


@router.post("", response_model=SubjectResponse, status_code=status.HTTP_201_CREATED)
def create_subject(payload: SubjectCreate, current_user: CurrentUser, db: DbSession) -> Subject:
    subject = Subject(user_id=current_user.id, **payload.model_dump())
    db.add(subject)
    try:
        db.commit()
    except Exception as error:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A subject with that name already exists") from error
    db.refresh(subject)
    return subject
