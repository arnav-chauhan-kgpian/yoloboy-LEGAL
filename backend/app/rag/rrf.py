"""Reciprocal rank fusion for graph + vector results."""


def reciprocal_rank_fusion(
    graph_results: list[dict],
    vector_results: list[dict],
    k: int = 60,
    graph_weight: float = 0.70,
) -> list[dict]:
    """
    Each result must have an `anchor` key uniquely identifying the unit.
    Returns merged list ordered by fused score.
    """
    scores: dict[str, float] = {}
    by_anchor: dict[str, dict] = {}

    for rank, item in enumerate(graph_results):
        anchor = item["anchor"]
        scores[anchor] = scores.get(anchor, 0.0) + graph_weight * (1.0 / (k + rank + 1))
        by_anchor[anchor] = item

    vector_weight = 1.0 - graph_weight
    for rank, item in enumerate(vector_results):
        anchor = item["anchor"]
        scores[anchor] = scores.get(anchor, 0.0) + vector_weight * (1.0 / (k + rank + 1))
        by_anchor.setdefault(anchor, item)

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [by_anchor[a] | {"_score": s} for a, s in ranked]
