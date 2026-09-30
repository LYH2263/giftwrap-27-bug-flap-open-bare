from fastapi import APIRouter, HTTPException
from app.repositories import boxes as repo
from app.schemas.box import BoxUpdate
router = APIRouter()
@router.get("/boxes")
def list_boxes(): return {"items": repo.list_boxes()}
@router.get("/boxes/{bid}")
def get_box(bid: int):
    r = repo.get_box(bid)
    if not r: raise HTTPException(404)
    return r
@router.put("/boxes/{bid}")
def update_box(bid: int, body: BoxUpdate):
    if body.default_flap_m < 0:
        raise HTTPException(422, "default_flap_m must be non-negative")
    r = repo.set_default_flap(bid, body.default_flap_m)
    if not r: raise HTTPException(404)
    return r
