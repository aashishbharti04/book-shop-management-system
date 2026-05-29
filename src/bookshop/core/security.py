"""Password hashing and validation.

All bcrypt byte-handling lives here so the rest of the codebase only ever deals
with ``str``. bcrypt silently truncates inputs longer than 72 bytes, so the
password policy rejects them explicitly.
"""

from __future__ import annotations

import bcrypt

from .exceptions import PasswordPolicyError

MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_BYTES = 72  # bcrypt hard limit


def validate_password(password: str) -> None:
    """Validate a plaintext password against the policy.

    Raises :class:`PasswordPolicyError` if the password is too short or exceeds
    bcrypt's 72-byte limit.
    """

    if not isinstance(password, str) or len(password) < MIN_PASSWORD_LENGTH:
        raise PasswordPolicyError(
            f"Password must be at least {MIN_PASSWORD_LENGTH} characters long."
        )
    if len(password.encode("utf-8")) > MAX_PASSWORD_BYTES:
        raise PasswordPolicyError(
            f"Password must be at most {MAX_PASSWORD_BYTES} bytes long when encoded "
            "as UTF-8 (a bcrypt limit)."
        )


def hash_password(password: str) -> str:
    """Validate then hash a password, returning the bcrypt hash as text."""

    validate_password(password)
    digest = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return digest.decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """Return ``True`` if *password* matches *password_hash*.

    Never raises: malformed hashes or non-string input simply return ``False``.
    """

    if not password or not password_hash:
        return False
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except (ValueError, TypeError):
        return False
