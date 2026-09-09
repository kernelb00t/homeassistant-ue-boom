"""Utility helpers for the UE Boom integration."""

from __future__ import annotations

import re

_MAC_RE = re.compile(r"^[0-9A-F]{12}$")


def normalize_mac(value: str) -> str:
    """Normalize a MAC address to 12 uppercase hex characters (no separators).

    Raises ValueError if the value does not look like a MAC address.
    """
    cleaned = re.sub(r"[^0-9a-fA-F]", "", value).upper()
    if not _MAC_RE.fullmatch(cleaned):
        raise ValueError(f"Invalid MAC address: {value}")
    return cleaned
