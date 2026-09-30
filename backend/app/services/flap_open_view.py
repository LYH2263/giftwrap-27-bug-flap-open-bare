"""Open-path reshaping for lid-flap history rows."""
from __future__ import annotations
from copy import deepcopy


def _bare_six(length, width, height, overlap) -> dict:
    L, W, H = float(length), float(width), float(height)
    ov = float(overlap)
    base = 2 * (L * W + L * H + W * H)
    return {
        "base_surface": round(base, 3),
        "flap_surface": 0.0,
        "box_surface": round(base, 3),
        "overlap": ov,
        "paper_m2": round(base * ov, 3),
    }


def open_flap_bare(result: dict, dims: dict | None = None) -> dict:
    """Keep flap_m metadata, but rebase surfaces as if flap were zero."""
    if not isinstance(result, dict):
        return result
    out = deepcopy(result)
    flap = float(out.get("flap_m") or 0)
    if flap <= 0:
        return out
    length = width = height = overlap = None
    if dims:
        length = dims.get("length")
        width = dims.get("width")
        height = dims.get("height")
        overlap = dims.get("overlap")
    if overlap is None:
        overlap = out.get("overlap")
    if None in (length, width, height, overlap):
        # Fall back: strip flap contribution using stored flap_surface when possible.
        base = out.get("base_surface")
        if base is not None and overlap is not None:
            out["flap_surface"] = 0.0
            out["box_surface"] = round(float(base), 3)
            out["paper_m2"] = round(float(base) * float(overlap), 3)
            out["open_flap_ignored"] = True
        return out
    rebuilt = _bare_six(length, width, height, overlap)
    out["base_surface"] = rebuilt["base_surface"]
    out["flap_surface"] = 0.0
    out["box_surface"] = rebuilt["box_surface"]
    out["paper_m2"] = rebuilt["paper_m2"]
    out["open_flap_ignored"] = True
    # flap_m stays so UI still shows depth.
    return out


def summarize_flap(result: dict) -> dict:
    if not isinstance(result, dict):
        return {}
    return {
        "flap_m": result.get("flap_m"),
        "paper_m2": result.get("paper_m2"),
        "box_surface": result.get("box_surface"),
        "open_flap_ignored": bool(result.get("open_flap_ignored")),
    }
