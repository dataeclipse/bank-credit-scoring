from __future__ import annotations

import numpy as np
import pandas as pd

from pd_scoring.monitoring import population_stability_index
from pd_scoring.monitoring.drift import apply_demo_drift, drift_report


def test_psi_no_drift_low() -> None:
    rng = np.random.default_rng(0)
    expected = rng.normal(size=5000)
    actual = rng.normal(size=5000)
    assert population_stability_index(expected, actual) < 0.1


def test_psi_shift_high() -> None:
    rng = np.random.default_rng(0)
    expected = rng.normal(size=5000)
    actual = rng.normal(loc=1.5, size=5000)
    assert population_stability_index(expected, actual) > 0.2


def test_drift_report_flags_shifted_features() -> None:
    rng = np.random.default_rng(0)
    reference = pd.DataFrame(
        {"EXT_SOURCE_2": rng.random(4000), "AMT_CREDIT": rng.normal(500000, 50000, 4000)}
    )
    current = apply_demo_drift(reference)
    report = drift_report(reference, current, threshold=0.2)
    assert "EXT_SOURCE_2" in report.alerts
    assert report.feature_psi["EXT_SOURCE_2"] > 0.2


def test_drift_report_no_alert_when_stable() -> None:
    rng = np.random.default_rng(1)
    reference = pd.DataFrame({"f": rng.normal(size=3000)})
    current = pd.DataFrame({"f": rng.normal(size=3000)})
    report = drift_report(reference, current, threshold=0.2)
    assert report.alerts == []
