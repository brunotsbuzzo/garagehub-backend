from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class SessionResponse(BaseModel):
    id: UUID
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime
    expires_at: datetime

    model_config = {"from_attributes": True}
