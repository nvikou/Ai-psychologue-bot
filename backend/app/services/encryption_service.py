"""Chiffrement au repos des contenus de messages."""

import base64
import hashlib
import logging

from cryptography.fernet import Fernet
from cryptography.fernet import InvalidToken

from app.config import settings

logger = logging.getLogger(__name__)


def _derive_fernet_key(raw: str) -> bytes:
    digest = hashlib.sha256(raw.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest)


def _get_fernet() -> Fernet | None:
    if not settings.encryption_key:
        return None
    return Fernet(_derive_fernet_key(settings.encryption_key))


def encrypt_text(plain: str) -> tuple[str, bool]:
    """
    Chiffre un texte si ENCRYPTION_KEY est défini.

    Retourne (contenu, is_encrypted).
    """
    fernet = _get_fernet()
    if fernet is None:
        return plain, False
    token = fernet.encrypt(plain.encode("utf-8")).decode("utf-8")
    return token, True


def decrypt_text(content: str, is_encrypted: bool) -> str:
    """Déchiffre un texte si nécessaire."""
    if not is_encrypted:
        return content
    fernet = _get_fernet()
    if fernet is None:
        logger.warning("Encrypted content but ENCRYPTION_KEY missing")
        return content
    try:
        return fernet.decrypt(content.encode("utf-8")).decode("utf-8")
    except InvalidToken:
        logger.error("Failed to decrypt message content")
        return "[encrypted]"
