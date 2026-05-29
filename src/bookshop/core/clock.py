"""Time helpers shared across all layers.

Lives in ``core`` so any layer (including presentation) can obtain the current
time without importing from the data layer.
"""

from __future__ import annotations

from datetime import UTC, datetime


def utcnow() -> datetime:
    """Naive UTC ``now``.

    We store *naive* datetimes that represent UTC: this keeps storage and
    comparisons consistent across SQLite (whose ``DATETIME`` does not round-trip
    timezone info) and MySQL, and avoids accidental naive/aware comparisons.
    """

    return datetime.now(UTC).replace(tzinfo=None)
