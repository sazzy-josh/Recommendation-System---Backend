"""
Content-Based Filtering engine.

Builds a TF-IDF matrix from course text (title + description + syllabus + tags),
then cosines-similarity scores each course against a student query vector
constructed from the student's declared interests and completed course texts.
"""

from __future__ import annotations

import logging
from typing import List, Dict, Any

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


# ── TF-IDF matrix construction ───────────────────────────────────────────────

def build_tfidf_matrix(courses: List[Dict[str, Any]]):
    """
    Build a TF-IDF matrix for the given list of course dicts.

    Each dict must have at least an 'id' key and a 'combined_text' key
    (pre-concatenated title + description + syllabus + tags).

    Returns
    -------
    vectorizer : TfidfVectorizer (fitted)
    tfidf_matrix : sparse matrix (n_courses, n_features)
    course_ids : list[int]
    """
    if not courses:
        return None, None, []

    texts = [c.get('combined_text', '') for c in courses]
    course_ids = [c['id'] for c in courses]

    vectorizer = TfidfVectorizer(
        stop_words='english',
        ngram_range=(1, 2),
        max_features=10_000,
        sublinear_tf=True,
    )
    tfidf_matrix = vectorizer.fit_transform(texts)
    return vectorizer, tfidf_matrix, course_ids


# ── Student query vector ─────────────────────────────────────────────────────

def build_student_query_vector(
    interests: List[str],
    completed_course_texts: List[str],
    vectorizer: TfidfVectorizer,
) -> np.ndarray:
    """
    Construct a single query vector for the student.

    The query is built from:
      - the student's declared interest keywords (joined)
      - the combined text of courses they have already completed

    The resulting vector is the mean of all individual TF-IDF vectors,
    then L2-normalised to unit length.

    Returns a 1-D numpy array of shape (n_features,).
    Returns a zero vector if no usable text is available.
    """
    components = []

    # Interest keywords
    if interests:
        interest_text = ' '.join(interests)
        try:
            vec = vectorizer.transform([interest_text])
            components.append(vec.toarray()[0])
        except Exception:
            pass

    # Completed course texts
    for text in completed_course_texts:
        if text and text.strip():
            try:
                vec = vectorizer.transform([text])
                components.append(vec.toarray()[0])
            except Exception:
                pass

    if not components:
        n_features = len(vectorizer.get_feature_names_out())
        return np.zeros(n_features)

    query_vec = np.mean(components, axis=0)

    # L2 normalise
    norm = np.linalg.norm(query_vec)
    if norm > 0:
        query_vec = query_vec / norm

    return query_vec


# ── CBF scores ───────────────────────────────────────────────────────────────

def compute_cbf_scores(
    interests: List[str],
    courses: List[Dict[str, Any]],
    completed_course_texts: List[str],
) -> List[Dict[str, Any]]:
    """
    Return a list of CBF score dicts sorted descending by cbf_score.

    Each dict: {'course_id': int, 'cbf_score': float}

    Parameters
    ----------
    interests : list of interest keyword strings
    courses   : list of course dicts with 'id' and 'combined_text'
    completed_course_texts : texts of courses the student has already completed
                             (used to enrich the query vector)
    """
    if not courses:
        return []

    vectorizer, tfidf_matrix, course_ids = build_tfidf_matrix(courses)

    if vectorizer is None:
        return []

    query_vec = build_student_query_vector(interests, completed_course_texts, vectorizer)

    # Cosine similarity between query and all courses
    similarities = cosine_similarity(query_vec.reshape(1, -1), tfidf_matrix)[0]

    results = [
        {'course_id': cid, 'cbf_score': float(sim)}
        for cid, sim in zip(course_ids, similarities)
    ]

    results.sort(key=lambda x: x['cbf_score'], reverse=True)
    return results
