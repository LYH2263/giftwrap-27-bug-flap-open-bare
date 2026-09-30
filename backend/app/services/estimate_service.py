from fastapi import HTTPException
from app.engines.wrap_math import paper_area, ribbon_estimate
from app.repositories import boxes, history, settings_repo

def run_estimate(box_id: int, overlap: float | None, wrap_style: str, save: bool, note: str, flap_m: float | None = None):
    box = boxes.get_box(box_id)
    if not box:
        raise HTTPException(404)
    if box.get("data_quality") == "dirty":
        raise HTTPException(422, "dirty box")
    # 折入深度：显式入参优先；未传时取盒主数据默认折入（老数据缺列按 0）
    if flap_m is None:
        flap_m = box.get("default_flap_m") or 0.0
    try:
        flap = float(flap_m)
    except (TypeError, ValueError):
        raise HTTPException(422, "flap_m must be a number in meters")
    if flap < 0:
        # 折入为负无意义：直接失败，且不得落任何用纸档行
        raise HTTPException(422, "flap_m must be non-negative")
    ov = float(overlap) if overlap is not None else settings_repo.get_overlap()
    calc = paper_area(box["length"], box["width"], box["height"], ov, flap)
    # 丝带只认未折入前的外形长宽高
    ribbon = ribbon_estimate(box["length"], box["width"], box["height"], wrap_style)
    # 落库即快照：flap_m / 有效表面积 / paper_m2 全部随当次计算固化
    payload = {**calc, "ribbon": ribbon, "box_id": box_id}
    run_id = history.insert_run(box_id, ov, payload, note) if save else None
    return {"box": box, "run_id": run_id, **calc, "ribbon": ribbon}
