from fastapi import APIRouter, Query
from app.schemas.estimate import EstimateRequest
from app.services import estimate_service
router = APIRouter()
@router.get("/estimate")
def get_est(
    box_id: int = Query(...),
    overlap: float | None = None,
    wrap_style: str = "cross",
    flap_m: float | None = None,
    save: bool = False,
):
    return estimate_service.run_estimate(box_id, overlap, wrap_style, save, "", flap_m)
@router.post("/estimate")
def post_est(body: EstimateRequest):
    return estimate_service.run_estimate(body.box_id, body.overlap, body.wrap_style, body.save, body.note, body.flap_m)
