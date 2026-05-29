"""Authentication: registration and login with bcrypt-hashed passwords."""

from __future__ import annotations

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from ..core.exceptions import UsernameTakenError, ValidationError
from ..core.security import hash_password, verify_password
from ..data.models import User
from ..data.repositories import UserRepository
from .base import BaseService, to_user_dto
from .dto import UserDTO

MAX_USERNAME_LENGTH = 64


class AuthService(BaseService):
    def __init__(self, session_factory: sessionmaker) -> None:
        super().__init__(session_factory)

    def register(self, username: str, password: str, confirm: str) -> UserDTO:
        """Create a new account. Raises on invalid input or a taken username."""

        username = (username or "").strip()
        if not username:
            raise ValidationError("Username is required.")
        if len(username) > MAX_USERNAME_LENGTH:
            raise ValidationError(
                f"Username must be at most {MAX_USERNAME_LENGTH} characters."
            )
        if password != confirm:
            raise ValidationError("Passwords do not match.")

        # hash_password validates the password policy (length / byte limit).
        password_hash = hash_password(password)

        with self._unit_of_work() as session:
            repo = UserRepository(session)
            if repo.exists(username):
                raise UsernameTakenError(f"The username '{username}' is already taken.")
            user = User(username=username, password_hash=password_hash, role="staff")
            try:
                repo.add(user)
            except IntegrityError as exc:  # pragma: no cover - race-condition guard
                raise UsernameTakenError(
                    f"The username '{username}' is already taken."
                ) from exc
            return to_user_dto(user)

    def login(self, username: str, password: str) -> UserDTO | None:
        """Return the user on success, or ``None`` on any failure.

        Deliberately does not reveal whether the username or the password was
        wrong.
        """

        username = (username or "").strip()
        if not username or not password:
            return None
        with self._unit_of_work() as session:
            user = UserRepository(session).get_by_username(username)
            if user is None or not verify_password(password, user.password_hash):
                return None
            return to_user_dto(user)
