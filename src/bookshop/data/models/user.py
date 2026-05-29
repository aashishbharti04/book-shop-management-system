"""User account model."""

from __future__ import annotations

from sqlalchemy import Column, DateTime, String

from ..base import Base, id_type, utcnow


class User(Base):
    __tablename__ = "users"

    id = Column(id_type(), primary_key=True, autoincrement=True)
    username = Column(String(64), nullable=False, unique=True, index=True)
    password_hash = Column(String(128), nullable=False)
    role = Column(String(16), nullable=False, default="staff")
    created_at = Column(DateTime, nullable=False, default=utcnow)
    updated_at = Column(DateTime, nullable=False, default=utcnow, onupdate=utcnow)

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"<User id={self.id} username={self.username!r} role={self.role!r}>"
