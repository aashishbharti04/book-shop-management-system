"""Data access for :class:`~bookshop.data.models.user.User`."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import User


class UserRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, user_id: int) -> User | None:
        return self.session.get(User, user_id)

    def get_by_username(self, username: str) -> User | None:
        stmt = select(User).where(User.username == username)
        return self.session.execute(stmt).scalar_one_or_none()

    def exists(self, username: str) -> bool:
        return self.get_by_username(username) is not None

    def add(self, user: User) -> User:
        self.session.add(user)
        self.session.flush()
        return user
