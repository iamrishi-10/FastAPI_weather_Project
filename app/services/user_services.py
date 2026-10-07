from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.orm_models.user_orm_models import User


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalars(select(User).where(User.email == email)).one_or_none()



