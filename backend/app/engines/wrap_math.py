def paper_area(length: float, width: float, height: float, overlap: float = 1.15, flap_m: float = 0.0) -> dict:
    """算纸核心。

    有效表面积 = 原六面表面积 + 盖口折入贴合面：
      - 六面：2(LW + LH + WH)
      - 折入贴面：盖口四周按口径周长 2(L+W) 折入深度 flap_m，
        口径由长宽自洽给出（2(L+W)·flap_m）。
    paper_m2 = 有效表面积 × 折边系数 overlap。
    flap_m 为 0 时与改造前完全一致；负数折入无意义，直接报错。
    """
    L, W, H = float(length), float(width), float(height)
    flap = float(flap_m)
    if min(L, W, H) <= 0:
        raise ValueError("box dimensions must be positive")
    if flap < 0:
        raise ValueError("flap_m must be non-negative")
    base_surface = 2 * (L * W + L * H + W * H)
    flap_surface = 2 * (L + W) * flap
    effective_surface = base_surface + flap_surface
    need = effective_surface * float(overlap)
    return {
        "base_surface": round(base_surface, 3),
        "flap_surface": round(flap_surface, 3),
        "box_surface": round(effective_surface, 3),
        "overlap": float(overlap),
        "flap_m": round(flap, 6),
        "paper_m2": round(need, 3),
    }


def ribbon_estimate(length: float, width: float, height: float, wrap_style: str = "cross") -> dict:
    """Helper: approximate ribbon length in meters (not stored as primary metric).

    丝带始终按未折入前的外形长宽高估算，与 flap_m 无关。
    """
    L, W, H = float(length), float(width), float(height)
    girth = 2 * (W + H)
    if wrap_style == "band":
        meters = girth + 0.3
    else:
        meters = girth * 2 + L + 0.5
    return {"wrap_style": wrap_style, "ribbon_m": round(meters, 2)}
