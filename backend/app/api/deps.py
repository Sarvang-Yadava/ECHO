from typing import Annotated
from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.security import bearer_scheme, decode_access_token
from app.db.session import get_db
from app.models.digital_twin import User

DbSession = Annotated[Session, Depends(get_db)]


def get_current_user(db: DbSession, credentials=Depends(bearer_scheme)) -> User:
    if credentials is None:
        demo_email = "demo@echo.local"
        user = db.scalar(select(User).where(User.email == demo_email))
        if user is None:
            user = User(email=demo_email, password_hash="demo", display_name="Aria")
            db.add(user)
            db.commit()
            db.refresh(user)
        return user
    user_id = decode_access_token(credentials)
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User no longer exists")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
