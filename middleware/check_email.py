from core.utilis.security import verify_code
from fastapi import Depends, Header, HTTPException, status
from core.utilis.messages import Messages
from sqlalchemy.orm import Session
from core.database.db import get_db


def check_email(code: str = Header(), db: Session = Depends(get_db)):
    try:
        check_code = verify_code(code=code, db=db)

        if check_code == "expired":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=Messages.email_code_expired,
            )
        elif not check_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=Messages.email_code_invalid,
            )

        return check_code

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=Messages.error_internal_server,
        )
