from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from core.database.db import get_db
from core.database.tables import Plan, Subscription, Organization
from schemas.plan_schema import PlanOut, SubscriptionOut
from datetime import datetime, timedelta
from typing import Optional
import uuid


router = APIRouter()


def seed_plans(db: Session):
    """
    Seeds the default plans if they do not exist.
    """
    plans_to_seed = [
        {
            "name": "Free Trial",
            "price": 0.0,
            "duration_days": 30,
            "restrictions": {
                "max_users": 2,
                "max_queries": 50,
                "features": ["basic_analytics"],
            },
        },
        {
            "name": "Online Starter",
            "price": 1500.0,  # Example price in local currency or USD
            "duration_days": 30,
            "restrictions": {
                "max_users": 5,
                "max_queries": 500,
                "features": ["basic_analytics", "email_support"],
            },
        },
        {
            "name": "Pro",
            "price": 15000.0,  # Example annual price
            "duration_days": 365,
            "restrictions": {
                "max_users": 20,
                "max_queries": 5000,
                "features": ["advanced_analytics", "priority_support", "api_access"],
            },
        },
        {
            "name": "Custom",
            "price": 0.0,
            "duration_days": 0,  # Indeterminate
            "restrictions": {
                "features": ["all_features", "dedicated_support"],
                "contact_email": "kwendacorp@gmail.com",
            },
        },
    ]

    for plan_data in plans_to_seed:
        plan = db.query(Plan).filter(Plan.name == plan_data["name"]).first()
        if not plan:
            new_plan = Plan(
                id=uuid.uuid4(),
                name=plan_data["name"],
                price=plan_data["price"],
                duration_days=plan_data["duration_days"],
                restrictions=plan_data["restrictions"],
            )
            db.add(new_plan)
    db.commit()


@router.get("/", response_model=list[PlanOut], status_code=status.HTTP_200_OK)
def list_available_plans(db: Session = Depends(get_db)):
    """
    List all available plans. Seeds defaults if none are found.
    """
    plans = db.query(Plan).all()
    if not plans:
        seed_plans(db)
        plans = db.query(Plan).all()
    return plans


@router.post(
    "/activate-free-trial/{organization_id}",
    response_model=SubscriptionOut,
    status_code=status.HTTP_201_CREATED,
)
def activate_free_trial(organization_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Activates a 30-day free trial for an organization.
    """
    # 1. Check if organization exists
    organization = (
        db.query(Organization).filter(Organization.id == organization_id).first()
    )
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Organização não encontrada."
        )

    # 2. Check if organization already has an active subscription
    active_subscription = (
        db.query(Subscription)
        .filter(
            Subscription.organization_id == organization_id,
            Subscription.is_active == True,
            Subscription.expires_at > datetime.utcnow(),
        )
        .first()
    )

    if active_subscription:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A organização já possui uma subscrição ativa.",
        )

    # 3. Get the Free Trial plan
    free_plan = db.query(Plan).filter(Plan.name == "Free Trial").first()
    if not free_plan:
        seed_plans(db)
        free_plan = db.query(Plan).filter(Plan.name == "Free Trial").first()

    # 4. Create the subscription
    new_subscription = Subscription(
        id=uuid.uuid4(),
        organization_id=organization_id,
        plan_id=free_plan.id,
        start_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(days=free_plan.duration_days),
        is_active=True,
    )

    try:
        db.add(new_subscription)
        db.commit()
        db.refresh(new_subscription)
        return new_subscription
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao ativar o teste gratuito: {str(e)}",
        )


@router.get(
    "/my-subscription/{organization_id}", response_model=Optional[SubscriptionOut]
)
def get_organization_subscription(
    organization_id: uuid.UUID, db: Session = Depends(get_db)
):
    """
    Returns the current active subscription for an organization.
    """
    try:
        subscription = (
            db.query(Subscription)
            .filter(
                Subscription.organization_id == organization_id,
                Subscription.is_active == True,
                Subscription.expires_at > datetime.utcnow(),
            )
            .first()
        )
        return subscription
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar a subscrição: {str(e)}",
        )
