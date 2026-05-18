
from core.utilis.messages import Messages
from fastapi import APIRouter, Depends, status, HTTPException
from core.database.db import get_db
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from core.database.tables import Services, ServiceCounter, Counter, Ticket
from middleware.organization_middleware import organization_middleware
from schemas.queue_schema import QueueEntrySchema
from core.utilis.generate_code import generate_type_queue
import uuid


router = APIRouter()


@router.post("/set-queue", status_code=status.HTTP_201_CREATED)
def set_queue(
    queue_entry: QueueEntrySchema,
    db: Session = Depends(get_db),
    org_uid: dict = Depends(organization_middleware),
):
    try:
        org_id = org_uid.get("organization_id")
        print("--------------->", org_id)
        if org_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=Messages.permission_denied,
            )

        # 1. Verify the service exists and belongs to this organization
        service = (
            db.query(Services)
            .filter(
                Services.id == queue_entry.service_id,
                Services.organizatio_id == org_id,
            )
            .first()
        )
        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=Messages.queue_service_not_found,
            )

        if queue_entry.has_ticket == True:
            print("--------------->", queue_entry.has_ticket)
            service_counter = (
                db.query(ServiceCounter)
                .filter(ServiceCounter.service_id == service.id)
                .first()
            )
            if not service_counter:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=Messages.queue_no_counter,
                )

            counter = (
                db.query(Counter)
                .filter(Counter.id == service_counter.counter_id)
                .first()
            )

            current_count = (
                db.query(Ticket)
                .filter(
                    Ticket.counter_id == counter.id,
                    Ticket.organization_id == org_id,
                    Ticket.status == True,
                )
                .count()
            )
            queue_position = current_count + 1

            # Verificar se já existe um ticket com esse nome
            existing_ticket = db.query(Ticket).filter(Ticket.name == queue_entry.client_name).first()
            if existing_ticket:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=Messages.client_already_in_queue,
                )

            # 4. Create the ticket (queue entry)
            new_ticket = Ticket(
                counter_id=counter.id,
                organization_id=org_id,
                name=queue_entry.client_name,
                count=generate_type_queue(queue_entry.type_queue, queue_position),
                status=True,
            )
            db.add(new_ticket)

            # Update the counter's total count
            counter.count = counter.count + 1
            db.commit()
            db.refresh(new_ticket)

            return {
                "message": Messages.queue_registered,
                "ticket": {
                    "id": str(new_ticket.id),
                    "client_name": new_ticket.name,
                    "queue_position": new_ticket.count,
                    "counter": counter.name,
                    "service": service.name,
                },
            }
        else:
            # Organização não tem balcão (Counter)
            # Pegar a posição do cliente com base no número de "Counters" (que estão sendo usados como fila)
            current_count = (
                db.query(Counter).filter(Counter.organization_id == org_id).count()
            )
            queue_position = current_count + 1

            # Verificar se já existe um counter com esse nome (usado como cliente)
            existing_counter = db.query(Counter).filter(Counter.name == queue_entry.client_name).first()
            if existing_counter:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=Messages.client_already_in_queue,
                )

            counter_data = Counter(
                name=queue_entry.client_name,
                organization_id=org_id,
                service_id=service.id,
                count=generate_type_queue(queue_entry.type_queue, queue_position),
            )

            db.add(counter_data)
            db.commit()
            db.refresh(counter_data)

            return {
                "message": Messages.queue_registered,
                "ticket": {
                    "id": str(counter_data.id),
                    "client_name": counter_data.name,
                    "queue_position": counter_data.count,
                    "service": service.name,
                },
            }

    except HTTPException:
        raise
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=Messages.client_already_in_queue,
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e) or Messages.error_internal_server,
        )


@router.get("/get-queue", status_code=status.HTTP_200_OK)
def get_queue(
    org_uid: dict = Depends(organization_middleware),
    db: Session = Depends(get_db),
):
    try:
        org_id = org_uid.get("organization_id")
        if org_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=Messages.permission_denied,
            )

        queue = db.query(Ticket).filter(Ticket.organization_id == org_id).all()
        return {
            "message": Messages.queue_registered,
            "queue": queue,
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e) or Messages.error_internal_server,
        )


@router.delete("/delete-queue", status_code=status.HTTP_200_OK)
def delete_queue(
    queue_id: uuid.UUID,
    org_uid: dict = Depends(organization_middleware),
    db: Session = Depends(get_db),
):
    try:
        org_id = org_uid.get("organization_id")
        if org_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=Messages.permission_denied,
            )

        # First, try to find and delete the client in the Ticket table
        ticket_to_delete = db.query(Ticket).filter(
            Ticket.id == queue_id, 
            Ticket.organization_id == org_id
        ).first()

        if ticket_to_delete:
            db.delete(ticket_to_delete)
            db.commit()
            return {"message": Messages.queue_deleted}

        # If not found in Ticket, check the Counter table (fallback queue)
        counter_to_delete = db.query(Counter).filter(
            Counter.id == queue_id, 
            Counter.organization_id == org_id
        ).first()

        if counter_to_delete:
            db.delete(counter_to_delete)
            db.commit()
            return {"message": Messages.queue_deleted}

        # If neither exists
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=Messages.queue_not_found,
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e) or Messages.error_internal_server,
        )