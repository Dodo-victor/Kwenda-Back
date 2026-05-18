from core.utilis.messages import Messages
from fastapi import APIRouter, status, Depends, HTTPException
from core.database.db import get_db
from sqlalchemy.orm import Session
from core.database.tables import Services, Organization
from middleware.organization_middleware import organization_middleware
from schemas.service_schema import ServiceSchema
import uuid

router = APIRouter()


@router.get("get-admin-data")
def get_admin_data():
    pass


@router.post("register-costumer", status_code=status.HTTP_201_CREATED)
def register_costumer():
    pass


@router.put("block-costumer", status_code=status.HTTP_423_LOCKED)
def block_costumer():
    pass


@router.delete("delete-costumer", status_code=status.HTTP_200_OK)
def delete_costumer():

    pass


@router.post("/add-services", status_code=status.HTTP_201_CREATED)
def add_services(
    service_schema: ServiceSchema,
    db: Session = Depends(get_db),
    org_uid: dict = Depends(organization_middleware),
):
    try:
        # check if the user is admin
        if isinstance(org_uid, dict):
            if org_uid.get("organization_id") is None:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=Messages.permission_denied,
                )
        # check if the organization is active

        org = (
            db.query(Organization)
            .filter(Organization.id == org_uid.get("organization_id"))
            .first()
        )
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=Messages.organization_not_found,
            )

        # Check if service with same name already exists

        existing_service = (
            db.query(Services)
            .filter(
                Services.name == service_schema.name,
                Services.organizatio_id == org_uid.get("organization_id"),
            )
            .first()
        )
        if existing_service:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=Messages.service_name_exists,
            )

        # Create service
        new_service = Services(
            organizatio_id=org_uid.get("organization_id"),
            name=service_schema.name,
            restrictions=service_schema.restrictions,
        )
        db.add(new_service)
        db.commit()
        db.refresh(new_service)

        return {"message": Messages.service_registered, "service": new_service}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e) or Messages.error_internal_server,
        )


@router.patch("set-clock", status_code=status.HTTP_201_CREATED)
def set_clock():
    try:
         pass
    except Exception as e:
        raise e
    # end try
    pass


@router.get("generate-history", status_code=status.HTTP_201_CREATED)
def register_costumer():
    pass
