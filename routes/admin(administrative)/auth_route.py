from fastapi import APIRouter, Depends, status
from middleware import location_middlware

router = APIRouter()

@router.post("/register-user-organization", status_code=status.HTTP_201_CREATED)

def register_user_and_organization(current_location: Depends(location_middlware)):

    return {"message": "User created successfully"}


@router.post("login_user", status_code=status.HTTP_200_OK)
def login_user():
    pass


@router.get("confirm_email", status_code=status.HTTP_202_ACCEPTED)
def confirm_email():
    pass
