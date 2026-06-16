from app.rag.rrf import reciprocal_rank_fusion


def test_rrf_fuses_overlapping_anchors():
    g = [{"anchor": "a"}, {"anchor": "b"}, {"anchor": "c"}]
    v = [{"anchor": "b"}, {"anchor": "d"}]
    out = reciprocal_rank_fusion(g, v, k=60, graph_weight=0.7)
    anchors = [r["anchor"] for r in out]
    assert "b" in anchors
    assert anchors[0] in ("a", "b")
    assert len(out) == 4


def test_rrf_weight_favors_graph():
    g = [{"anchor": "x"}]
    v = [{"anchor": "y"}]
    out = reciprocal_rank_fusion(g, v, graph_weight=0.9)
    assert out[0]["anchor"] == "x"


def test_rrf_empty_inputs():
    assert reciprocal_rank_fusion([], []) == []
