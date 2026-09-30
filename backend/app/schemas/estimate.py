from pydantic import BaseModel

class EstimateRequest(BaseModel):
    box_id: int
    overlap: float | None = None
    wrap_style: str = "cross"
    flap_m: float | None = None
    save: bool = False
    note: str = ""
