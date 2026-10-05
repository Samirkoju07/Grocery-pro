"""Pydantic schemas for Notification module."""
from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    title: str
    message: str
    notification_type: str
    is_read: bool
    read_at: datetime | None
    created_at: datetime
