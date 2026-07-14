"""
Collaborative Filtering engine using SVD matrix factorisation.

Builds a student-course interaction matrix from implicit signals, factorises
it with scipy's sparse SVD, and returns predicted scores for a target student.
"""

from __future__ import annotations

import logging
from typing import List, Dict, Any, Tuple

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import svds

from engine.utils import compute_implicit_score

logger = logging.getLogger(__name__)

# Number of latent factors for SVD
N_COMPONENTS = 20


# ── Matrix construction ───────────────────────────────────────────────────────

def build_interaction_matrix(
    interactions: List[Dict[str, Any]],
) -> Tuple[csr_matrix, List[int], List[int]]:
    """
    Build a sparse student-course interaction matrix.

    Parameters
    ----------
    interactions : list of dicts with keys:
        'student_id', 'course_id', 'clicks', 'time_spent_seconds'

    Returns
    -------
    matrix      : scipy sparse CSR matrix (n_students, n_courses)
    student_ids : ordered list of student IDs corresponding to rows
    course_ids  : ordered list of course IDs corresponding to columns
    """
    if not interactions:
        return csr_matrix((0, 0)), [], []

    df = pd.DataFrame(interactions)
    df['implicit_score'] = df.apply(
        lambda r: compute_implicit_score(
            int(r.get('clicks', 0)),
            int(r.get('time_spent_seconds', 0)),
        ),
        axis=1,
    )

    student_ids = sorted(df['student_id'].unique().tolist())
    course_ids = sorted(df['course_id'].unique().tolist())

    student_idx = {sid: i for i, sid in enumerate(student_ids)}
    course_idx = {cid: i for i, cid in enumerate(course_ids)}

    rows = df['student_id'].map(student_idx).values
    cols = df['course_id'].map(course_idx).values
    data = df['implicit_score'].values

    matrix = csr_matrix(
        (data, (rows, cols)),
        shape=(len(student_ids), len(course_ids)),
    )
    return matrix, student_ids, course_ids


# ── SVD factorisation ─────────────────────────────────────────────────────────

def compute_svd_predictions(
    matrix: csr_matrix,
    n_components: int = N_COMPONENTS,
) -> np.ndarray:
    """
    Factorise the interaction matrix with scipy's sparse SVD and reconstruct
    the full predicted matrix (U · Σ · Vt).

    Returns a dense (n_students, n_courses) numpy array of predicted scores.
    """
    if matrix.shape[0] == 0 or matrix.shape[1] == 0:
        return np.zeros(matrix.shape)

    # Number of factors capped at min(rows, cols) - 1
    k = min(n_components, min(matrix.shape) - 1)
    if k < 1:
        return matrix.toarray()

    U, sigma, Vt = svds(matrix.astype(float), k=k)

    predicted = np.dot(np.dot(U, np.diag(sigma)), Vt)
    return predicted


# ── CF scores for one student ─────────────────────────────────────────────────

def get_cf_scores_for_student(
    target_student_id: int,
    interactions: List[Dict[str, Any]],
    exclude_course_ids: List[int] | None = None,
) -> List[Dict[str, Any]]:
    """
    Return collaborative-filtering predicted scores for every course for
    a target student, sorted descending.

    Parameters
    ----------
    target_student_id  : the student we are generating recommendations for
    interactions       : full list of interaction dicts from the DB
    exclude_course_ids : courses already taken / enrolled — exclude from output

    Returns
    -------
    list of {'course_id': int, 'cf_score': float}, descending by cf_score
    """
    matrix, student_ids, course_ids = build_interaction_matrix(interactions)

    if not student_ids or target_student_id not in student_ids:
        # Cold-start: no CF signal; return zero scores for all known courses
        return [{'course_id': cid, 'cf_score': 0.0} for cid in course_ids]

    predicted = compute_svd_predictions(matrix)

    student_row = student_ids.index(target_student_id)
    scores = predicted[student_row]

    exclude_set = set(exclude_course_ids or [])

    results = [
        {'course_id': cid, 'cf_score': float(scores[i])}
        for i, cid in enumerate(course_ids)
        if cid not in exclude_set
    ]
    results.sort(key=lambda x: x['cf_score'], reverse=True)
    return results
