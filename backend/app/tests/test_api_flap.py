import pytest
from starlette.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    # 作为上下文管理器进入才会触发 startup（建表/种子）
    with TestClient(app) as c:
        yield c


def _run_count(client):
    return len(client.get("/api/runs").json()["items"])


def test_negative_flap_fails_without_inserting_row(client):
    """折入为负：整单失败（422），且用纸档不增行。"""
    before = _run_count(client)
    r_get = client.get("/api/estimate", params={"box_id": 1, "flap_m": -0.02})
    assert r_get.status_code == 422
    r_post = client.post("/api/estimate", json={"box_id": 1, "flap_m": -0.02, "save": True})
    assert r_post.status_code == 422
    assert _run_count(client) == before


def test_zero_flap_matches_legacy_and_dry_run_does_not_insert(client):
    """折入为 0 与改造前同盒同折边相等；save=false 只回算不增行。"""
    before = _run_count(client)
    r = client.post("/api/estimate", json={"box_id": 1, "flap_m": 0, "save": False})
    assert r.status_code == 200
    body = r.json()
    assert body["run_id"] is None
    assert body["flap_m"] == 0
    assert body["box_surface"] == 0.27
    assert body["paper_m2"] == 0.31
    assert body["flap_surface"] == 0.0
    assert _run_count(client) == before


def test_save_persists_flap_snapshot_and_survives_default_change(client):
    """save=true 落库 flap/有效表面积/paper；改主数据默认折入后，列表与详情两路钉住写入值。"""
    w = client.post("/api/estimate", json={"box_id": 1, "flap_m": 0.05, "save": True}).json()
    rid = w["run_id"]
    assert rid
    flap_at_write, paper_at_write, surface_at_write = w["flap_m"], w["paper_m2"], w["box_surface"]
    assert w["flap_surface"] > 0
    # 丝带不随折入变化：与 flap=0 干算一致
    dry0 = client.get("/api/estimate", params={"box_id": 1, "flap_m": 0}).json()
    assert dry0["ribbon"]["ribbon_m"] == w["ribbon"]["ribbon_m"]

    # 改盒主数据默认折入为另一个值
    assert client.put("/api/boxes/1", json={"default_flap_m": 0.08}).status_code == 200

    # 用纸档列表摘要：该编号 flap/paper 不按新默认回刷
    listed = next(x for x in client.get("/api/runs").json()["items"] if x["id"] == rid)
    assert listed["result"]["flap_m"] == flap_at_write
    assert listed["result"]["paper_m2"] == paper_at_write

    # 用纸档详情：同样钉住，且与列表彼此一致
    detail = client.get(f"/api/runs/{rid}").json()
    assert detail["result"]["flap_m"] == flap_at_write
    assert detail["result"]["paper_m2"] == paper_at_write
    assert detail["result"]["box_surface"] == surface_at_write
    assert detail["result"]["paper_m2"] == listed["result"]["paper_m2"]


def test_dry_calc_with_same_params_corroborates_saved_run(client):
    """算纸台用写入时同参再干算，须能与该编号回看互证。"""
    w = client.post("/api/estimate", json={"box_id": 2, "flap_m": 0.04, "save": True}).json()
    rid = w["run_id"]
    dry = client.get("/api/estimate", params={"box_id": 2, "flap_m": 0.04, "save": "false"}).json()
    saved = client.get(f"/api/runs/{rid}").json()["result"]
    assert dry["run_id"] is None
    for key in ("flap_m", "box_surface", "flap_surface", "base_surface", "paper_m2", "overlap"):
        assert dry[key] == saved[key]


def test_default_flap_used_when_param_omitted_and_negative_default_rejected(client):
    """未显式传 flap_m 时取盒主数据默认折入；负默认登记被拒。"""
    client.put("/api/boxes/1", json={"default_flap_m": 0.06})
    r = client.get("/api/estimate", params={"box_id": 1})
    assert r.json()["flap_m"] == 0.06
    assert client.put("/api/boxes/1", json={"default_flap_m": -1}).status_code == 422
