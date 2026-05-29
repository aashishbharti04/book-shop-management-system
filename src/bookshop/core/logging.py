"""Centralized logging configuration."""

from __future__ import annotations

import logging

from .config import get_settings

_CONFIGURED = False


def configure_logging(level: str | None = None) -> None:
    """Configure root logging once, idempotently."""

    global _CONFIGURED
    if _CONFIGURED:
        return
    resolved = (level or get_settings().log_level or "INFO").upper()
    logging.basicConfig(
        level=getattr(logging, resolved, logging.INFO),
        format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    """Return a named logger, configuring logging on first use."""

    configure_logging()
    return logging.getLogger(name)
