from __future__ import annotations
from typing import List, Tuple
import numpy as np

def cosine(a: np.ndarray, b: np.ndarray) -> float:
    na = np.linalg.norm(a)
    nb = np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))

def mmr_select(embeddings: List[List[float]], k: int = 6, lambda_param: float = 0.5) -> List[int]:
    """Maximal Marginal Relevance index selection.
    embeddings: list of vectors
    returns indices of selected items
    """
    X = np.array(embeddings, dtype=float)
    n = X.shape[0]
    if n <= k:
        return list(range(n))
    # similarity to centroid as relevance proxy
    centroid = X.mean(axis=0)
    rel = np.array([cosine(x, centroid) for x in X])
    selected = [int(np.argmax(rel))]
    candidates = set(range(n)) - set(selected)

    while len(selected) < k and candidates:
        best_idx = None
        best_score = -1e9
        for i in candidates:
            div = max(cosine(X[i], X[j]) for j in selected)
            score = lambda_param * rel[i] - (1 - lambda_param) * div
            if score > best_score:
                best_score = score
                best_idx = i
        selected.append(best_idx)
        candidates.remove(best_idx)
    return selected
