from fastapi import APIRouter, HTTPException
from app.repositories import history as repo
from app.services.flap_open_view import summarize_flap

router = APIRouter()

@router.get("/runs")
def runs(limit: int = 50):
    return {"items": repo.list_runs(limit)}

@router.get("/runs/{run_id}")
def run_detail(run_id: int):
    r = repo.get_run(run_id)
    if not r:
        raise HTTPException(404)
    # Detail payload exposes a flat summary alongside result for open consumers.
    r["open_summary"] = summarize_flap(r.get("result") or {})
    return r
