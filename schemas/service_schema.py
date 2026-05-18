from pydantic import BaseModel
from typing import Optional, Dict, Any

class ServiceSchema(BaseModel):
    name: str
    restrictions: Optional[Dict[str, Any]] = None
