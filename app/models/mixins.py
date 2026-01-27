from datetime import datetime
from sqlalchemy import func, UUID
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeMixin
from sqlalchemy.types import DateTime
import uuid

class TimestampMixin(DeclarativeMixin):
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

class UUIDMixin(DeclarativeMixin):
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )