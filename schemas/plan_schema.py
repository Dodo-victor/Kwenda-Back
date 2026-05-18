from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional, Dict, Any


class PlanBase(BaseModel):
    name: str
    price: float
    duration_days: int
    restrictions: Optional[Dict[str, Any]] = None


class PlanCreate(PlanBase):
    pass


class PlanOut(PlanBase):
    id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class SubscriptionBase(BaseModel):
    organization_id: UUID
    plan_id: UUID


class SubscriptionCreate(SubscriptionBase):
    pass


class SubscriptionOut(SubscriptionBase):
    id: UUID
    start_at: datetime
    expires_at: datetime
    is_active: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
