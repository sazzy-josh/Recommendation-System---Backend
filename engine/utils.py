import numpy as np


# ── Implicit signal scoring ──────────────────────────────────────────────────

MAX_CLICKS = 50
MAX_TIME_SECONDS = 1800  # 30 minutes


def compute_implicit_score(clicks: int, time_spent_seconds: int) -> float:
    """
    Compute a normalised implicit interaction score in [0, 1].

    The score is the average of two min-max normalised signals:
      - click signal  = min(clicks, MAX_CLICKS) / MAX_CLICKS
      - time signal   = min(time_spent_seconds, MAX_TIME_SECONDS) / MAX_TIME_SECONDS

    Edge case: both signals 0 → 0.0; both at ceiling → 1.0.
    """
    click_score = min(clicks, MAX_CLICKS) / MAX_CLICKS
    time_score = min(time_spent_seconds, MAX_TIME_SECONDS) / MAX_TIME_SECONDS
    return round((click_score + time_score) / 2, 6)


# ── Evaluation metrics ───────────────────────────────────────────────────────

def compute_mae(y_true: list, y_pred: list) -> float:
    """Mean Absolute Error."""
    if not y_true:
        return 0.0
    arr_true = np.array(y_true, dtype=float)
    arr_pred = np.array(y_pred, dtype=float)
    return float(np.mean(np.abs(arr_true - arr_pred)))


def compute_rmse(y_true: list, y_pred: list) -> float:
    """Root Mean Squared Error."""
    if not y_true:
        return 0.0
    arr_true = np.array(y_true, dtype=float)
    arr_pred = np.array(y_pred, dtype=float)
    return float(np.sqrt(np.mean((arr_true - arr_pred) ** 2)))
