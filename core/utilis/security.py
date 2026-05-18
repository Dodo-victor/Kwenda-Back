import random
from datetime import datetime
from sqlalchemy.orm import Session
from core.database.tables import VerificationCode, User
import bcrypt

ALGORITHM = "HS256"


def get_algorithm():
    return ALGORITHM


def hash_password(password: str) -> bytes:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt)


def verify_password(plain_password: str, hashed_password: bytes) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password)


def generate_code_verification(length: int = 6) -> str:
    return "".join(str(random.randint(0, 9)) for _ in range(length))


# end def


def verify_code(code: str, db: Session) -> dict | bool:

    check_code = (
        db.query(VerificationCode).filter(VerificationCode.code == code).first()
    )

    if not check_code:
        return False

    if check_code.expires_at < datetime.utcnow():
        db.delete(check_code)
        db.commit()
        return "expired"

    # Set user to verified
    user = db.query(User).filter(User.id == check_code.user_id).first()
    if user:
        user.is_verified = True

    paylod_data = {
        "user_id": str(check_code.user_id),
        "organization_id": str(check_code.organization_id),
    }
    db.delete(check_code)
    db.commit()
    return paylod_data


def verify_reset_code(code: str, db: Session) -> dict | bool:
    check_code = (
        db.query(VerificationCode).filter(VerificationCode.code == code).first()
    )

    if not check_code:
        return False

    if check_code.expires_at < datetime.utcnow():
        db.delete(check_code)
        db.commit()
        return "expired"

    paylod_data = {
        "user_id": str(check_code.user_id),
        "organization_id": str(check_code.organization_id),
    }
    db.delete(check_code)
    db.commit()
    return paylod_data
