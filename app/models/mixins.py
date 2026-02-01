from datetime import datetime
from sqlalchemy import func, UUID
from sqlalchemy.orm import Mapped, mapped_column, declarative_mixin
from sqlalchemy.types import DateTime
import uuid

@declarative_mixin
class TimestampMixin():
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

@declarative_mixin
class UUIDMixin():
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )