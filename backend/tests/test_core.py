"""Tests unitaires backend (sans DB externe)."""

from app.services.crisis_service import is_crisis_message
from app.services.encryption_service import decrypt_text
from app.services.encryption_service import encrypt_text
from app.services.i18n_service import crisis_text
from app.services.i18n_service import normalize_language


def test_normalize_language() -> None:
    assert normalize_language("FR") == "fr"
    assert normalize_language("xx") == "en"
    assert normalize_language(None) == "en"


def test_crisis_detection() -> None:
    assert is_crisis_message("I want to kill myself")
    assert not is_crisis_message("I feel a bit sad today")


def test_crisis_i18n() -> None:
    fr = crisis_text("fr")
    assert "3114" in fr
    en = crisis_text("en")
    assert "988" in en


def test_encryption_roundtrip(monkeypatch) -> None:
    from app.services import encryption_service as enc

    monkeypatch.setattr(
        enc.settings,
        "encryption_key",
        "test-secret-key",
    )
    token, encrypted = encrypt_text("hello world")
    assert encrypted is True
    assert decrypt_text(token, True) == "hello world"


def test_encryption_disabled(monkeypatch) -> None:
    from app.services import encryption_service as enc

    monkeypatch.setattr(enc.settings, "encryption_key", "")
    text, encrypted = encrypt_text("plain")
    assert encrypted is False
    assert text == "plain"
