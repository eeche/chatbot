from datetime import datetime
from zoneinfo import ZoneInfo
from sqlalchemy.orm import Session
from models import User, IoC
from schema import UserSchema
from enum import Enum

class IoCType(Enum):
    EMAIL_MISMATCH = "Email Mismatch"
    # PASSWORD_ATTEMPT = "Password Attempt"
    # USERNAME_ATTEMPT = "Username Attempt"

def get_user(db: Session, user_identifier):
    if isinstance(user_identifier, int):
        return db.query(User).filter(User.id == user_identifier).first()
    elif hasattr(user_identifier, 'username'):
        return db.query(User).filter(User.username == user_identifier.username).first()
    else:
        raise ValueError("Invalid user identifier")

def get_iocs(db: Session, user: User):
    return db.query(IoC).filter(IoC.user_id == user.id).all()

# 다수의 ioc 생성 경우에 따라서 다르게 생성할 필요가 있음 ex) password, email, username 등
def create_ioc(db: Session, user: User, user_input: UserSchema, ioc_type: IoCType):

    if ioc_type == IoCType.EMAIL_MISMATCH:
        value = user_input.email
        description = f"Attempted access with incorrect email for user {user.username}"
        confidence = 0.6
    elif ioc_type == IoCType.PASSWORD_ATTEMPT:
        value = user_input.password
        description = f"Failed password attempt for user {user.username}"
        confidence = 0.7
    elif ioc_type == IoCType.USERNAME_ATTEMPT:
        value = user_input.username
        description = f"Attempted access with non-existent username"
        confidence = 0.8
    # 필요한 다른 IoC 타입들에 대한 로직을 여기에 추가

    new_ioc = IoC(
        type=ioc_type.value,
        value=value,
        description=description,
        confidence=confidence,
        user_id=user.id,
        created_at=datetime.now(ZoneInfo("Asia/Seoul"))
    )
    db.add(new_ioc)
    db.commit()
    return new_ioc