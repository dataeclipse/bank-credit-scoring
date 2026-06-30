from __future__ import annotations

from pd_scoring.scoring import RiskSegment, assign_segment, pd_to_score


def test_pd_to_score_monotonic() -> None:
    assert pd_to_score(0.01) > pd_to_score(0.1) > pd_to_score(0.5) > pd_to_score(0.9)


def test_pd_to_score_base_point() -> None:
    pd_at_base = 1.0 / (1.0 + 50.0)
    assert pd_to_score(pd_at_base, base_score=600, base_odds=50.0) == 600


def test_pd_to_score_clips_extremes() -> None:
    assert isinstance(pd_to_score(0.0), int)
    assert isinstance(pd_to_score(1.0), int)


def test_assign_segment_thresholds() -> None:
    assert assign_segment(0.01) is RiskSegment.LOW
    assert assign_segment(0.05) is RiskSegment.MEDIUM
    assert assign_segment(0.10) is RiskSegment.MEDIUM
    assert assign_segment(0.15) is RiskSegment.HIGH
    assert assign_segment(0.40) is RiskSegment.HIGH
