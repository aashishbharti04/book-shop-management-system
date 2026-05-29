from __future__ import annotations

import pytest

from bookshop.core.exceptions import PasswordPolicyError
from bookshop.core.security import hash_password, validate_password, verify_password


def test_hash_is_not_plaintext_and_verifies():
    digest = hash_password("correct horse")
    assert digest != "correct horse"
    assert verify_password("correct horse", digest)
    assert not verify_password("wrong password", digest)


def test_two_hashes_of_same_password_differ_but_both_verify():
    a = hash_password("password123")
    b = hash_password("password123")
    assert a != b  # unique salts
    assert verify_password("password123", a)
    assert verify_password("password123", b)


def test_short_password_rejected():
    with pytest.raises(PasswordPolicyError):
        validate_password("short")


def test_overlong_password_rejected():
    with pytest.raises(PasswordPolicyError):
        validate_password("x" * 73)


def test_verify_with_garbage_hash_returns_false():
    assert verify_password("anything", "not-a-valid-bcrypt-hash") is False
    assert verify_password("", "") is False
