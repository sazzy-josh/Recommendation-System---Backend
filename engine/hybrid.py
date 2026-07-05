"""
Hybrid recommendation engine.

Blends Collaborative Filtering (CF) and Content-Based Filtering (CBF) scores
using a weighted linear combination:

    hybrid_score = w * cf_score_norm + (1 - w) * cbf_score_norm

where w (hybrid_weight) is dynamically set based on the student's interaction
history:
  - w = 0  → pure CBF  (cold-start: too few interactions)
  - w > 0  → hybrid    (enough signal for CF to contribute)
"""

from __future__ import annotations

import logging
from typing import List, Dict, Any

import numpy as np

logger = logging.getLogger(__name__)


# ── Score normalisation ───────────────────────────────────────────────────────

def normalize_scores(
    scores: List[Dict[str, Any]],
    score_key: str,
) -> List[Dict[str, Any]]:
    """
    Min-max normalise the values at `score_key` across all dicts in `scores`.
    Adds a new key ``<score_key>_norm`` to each dict (in-place copy).

    If all values are equal the normalised score is 0.0 for all entries.

    Returns the modified list.
    """
    values = np.array([s[score_key] for s in scores], dtype=float)
    min_val = values.min()
    max_val = values.max()
    denom = max_val - min_val

    normed_key = f"{score_key}_norm"
    result = []
    for s, v in zip(scores, values):
        entry = dict(s)
        entry[normed_key] = float((v - min_val) / denom) if denom > 0 else 0.0
        result.append(entry)
    return result


# ── Score blending ────────────────────────────────────────────────────────────

def blend_scores(
    cf_scores: List[Dict[str, Any]],
    cbf_scores: List[Dict[str, Any]],
    w: float,
    top_n: int,
) -> List[Dict[str, Any]]:
    """
    Blend normalised CF and CBF scores into a single ranked list.

    Parameters
    ----------
    cf_scores  : list of {'course_id': int, 'cf_score': float}
    cbf_scores : list of {'course_id': int, 'cbf_score': float}
    w          : hybrid weight in [0, 1]; 0 = pure CBF, 1 = pure CF
    top_n      : number of recommendations to return

    Returns
    -------
    list of dicts (length <= top_n), descending by hybrid_score:
        {
          'course_id': int,
          'hybrid_score': float,
          'cf_score': float,
          'cbf_score': float,
          'recommendation_type': 'CF' | 'CBF' | 'HYBRID',
        }
    """
    # Build lookup maps
    cf_map: Dict[int, float] = {s['course_id']: s['cf_score'] for s in cf_scores}
    cbf_map: Dict[int, float] = {s['course_id']: s['cbf_score'] for s in cbf_scores}

    # Union of all course IDs
    all_course_ids = set(cf_map.keys()) | set(cbf_map.keys())

    if not all_course_ids:
        return []

    # Build unified score lists for normalisation
    unified_cf = [{'course_id': cid, 'cf_score': cf_map.get(cid, 0.0)} for cid in all_course_ids]
    unified_cbf = [{'course_id': cid, 'cbf_score': cbf_map.get(cid, 0.0)} for cid in all_course_ids]

    norm_cf = normalize_scores(unified_cf, 'cf_score')
    norm_cbf = normalize_scores(unified_cbf, 'cbf_score')

    cf_norm_map = {s['course_id']: s['cf_score_norm'] for s in norm_cf}
    cbf_norm_map = {s['course_id']: s['cbf_score_norm'] for s in norm_cbf}

    blended = []
    for cid in all_course_ids:
        cf_n = cf_norm_map.get(cid, 0.0)
        cbf_n = cbf_norm_map.get(cid, 0.0)
        hybrid = w * cf_n + (1.0 - w) * cbf_n

        if w == 0.0:
            rec_type = 'CBF'
        elif w == 1.0:
            rec_type = 'CF'
        else:
            rec_type = 'HYBRID'

        blended.append({
            'course_id': cid,
            'hybrid_score': round(hybrid, 6),
            'cf_score': cf_map.get(cid, 0.0),
            'cbf_score': cbf_map.get(cid, 0.0),
            'recommendation_type': rec_type,
        })

    blended.sort(key=lambda x: x['hybrid_score'], reverse=True)
    return blended[:top_n]


# ── Rationale text ────────────────────────────────────────────────────────────

def generate_rationale(context: Dict[str, Any]) -> str:
    """
    Generate a human-readable explanation for a recommendation.

    Parameters
    ----------
    context : dict with at minimum 'recommendation_type' key
        ('CF', 'CBF', or 'HYBRID')

    Returns
    -------
    Explanation string.
    """
    rec_type = context.get('recommendation_type', 'HYBRID')

    rationales = {
        'CF': (
            "Recommended because students with similar academic histories and "
            "interaction patterns found this course valuable."
        ),
        'CBF': (
            "Recommended based on how well this course's content aligns with "
            "your stated interests and academic background."
        ),
        'HYBRID': (
            "Recommended using a combination of your content preferences and "
            "the experiences of students with similar profiles."
        ),
    }
    return rationales.get(rec_type, rationales['HYBRID'])
