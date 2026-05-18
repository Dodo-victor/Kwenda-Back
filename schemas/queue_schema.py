from pydantic import BaseModel
from uuid import UUID


class QueueEntrySchema(BaseModel):
    service_id: UUID
    client_name: str
    has_ticket: bool
    type_queue: str
