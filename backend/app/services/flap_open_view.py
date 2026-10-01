"""Snapshot summary helpers for lid-flap history rows."""
from __future__ import annotations


def summarize_flap(result: dict) -> dict:
    if not isinstance(result, dict):
        return {}
    return {
        "flap_m": result.get("flap_m"),
        "paper_m2": result.get("paper_m2"),
        "box_surface": result.get("box_surface"),
    }
