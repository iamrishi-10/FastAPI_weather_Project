from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.db.orm_models.user_orm_models import User
from app.schemas.auth_schemas import SignUpRequest, LoginRequest
from app.services.user_services import get_user_by_email


def sign_up_new_user(db: Session, signup_data: SignUpRequest) -> User | None:
    if get_user_by_email(db, signup_data.email) is not None:
        return None

    new_user = User(
        first_name=signup_data.first_name,
        last_name=signup_data.last_name,
        email=signup_data.email,
        password_hash=hash_password(signup_data.password),
    )

    db.add(new_user)
    db.flush()
    db.refresh(new_user)
    return new_user



def authenticate_user(db: Session, login_data: LoginRequest) -> User | None:
    user = get_user_by_email(db, login_data.email)

    if user is None:
        return None

    if not verify_password(login_data.password, user.password_hash):
        return None

    return user