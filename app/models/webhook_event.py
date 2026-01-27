from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import String
from app.core.db import BaseModel
from app.models import UUIDMixin
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from sqlalchemy.types import DateTime

class WebhookEvent(BaseModel, UUIDMixin):
    __tablename__ = "webhook_events"

    provider: Mapped[str] = mapped_column(String(255), nullable=False)
    delivery_id: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    event_type: Mapped[str] = mapped_column(String(255), nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    signature_valid: Mapped[bool] = mapped_column(nullable=False, default=False)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=func.now())