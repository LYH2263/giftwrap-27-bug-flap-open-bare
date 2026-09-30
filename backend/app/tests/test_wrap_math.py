import pytest
from app.engines.wrap_math import paper_area, ribbon_estimate


def test_zero_flap_equals_legacy():
    """折入为 0：paper_m2 / box_surface 与改造前同盒同折边完全一致。"""
    legacy = paper_area(0.30, 0.20, 0.15, 1.15, 0.0)
    assert legacy["box_surface"] == 0.27
    assert legacy["paper_m2"] == 0.31
    assert legacy["flap_surface"] == 0.0
    assert legacy["flap_m"] == 0.0
    assert legacy["base_surface"] == 0.27
    # 不带 flap_m 旧调用方式仍然成立
    assert paper_area(1, 1, 1, 1.0)["paper_m2"] == 6.0


def test_positive_flap_adds_perimeter_surface():
    """折入贴面 = 口径周长 2(L+W) × flap；有效表面积叠加后再乘折边系数。"""
    L, W, H, ov, flap = 0.30, 0.20, 0.15, 1.15, 0.05
    r = paper_area(L, W, H, ov, flap)
    base = 2 * (L * W + L * H + W * H)
    flap_area = 2 * (L + W) * flap
    assert r["flap_surface"] == round(flap_area, 3)
    assert r["box_surface"] == round(base + flap_area, 3)
    assert r["paper_m2"] == round((base + flap_area) * ov, 3)
    assert r["flap_m"] == 0.05


def test_negative_flap_rejected():
    with pytest.raises(ValueError):
        paper_area(0.3, 0.2, 0.15, 1.15, -0.01)


def test_ribbon_ignores_flap():
    """丝带始终按未折入前长宽高，折入与否结果相同。"""
    a = ribbon_estimate(0.30, 0.20, 0.15, "cross")
    b = ribbon_estimate(0.30, 0.20, 0.15, "cross")
    assert a == b
    assert a["ribbon_m"] > 0.5
