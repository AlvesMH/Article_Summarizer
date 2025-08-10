from __future__ import annotations
import requests
from typing import List, Sequence
from .settings import settings

def _normalize(v):
    import numpy as np
    v = np.array(v, dtype=float)
    n = (v**2).sum() ** 0.5
    return (v / max(n, 1e-12)).tolist()

def embed_texts(texts: Sequence[str]) -> List[List[float]]:
    """Call HF Router feature-extraction endpoint to get embeddings."""
    if not texts:
        return []
    url = settings.HF_EMBED_API
    headers = {
        "Authorization": f"Bearer {settings.HUGGINGFACE_API_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {"inputs": list(texts)}
    r = requests.post(url, headers=headers, json=payload, timeout=60)
    r.raise_for_status()
    data = r.json()
    # HF may return a single vector for one input or a list for many
    if isinstance(data[0], (int, float)):
        data = [data]
    # mean-pool if token embeddings returned
    outs = []
    for item in data:
        if item and isinstance(item[0], list):
            # [tokens, dims] -> mean over tokens
            dims = len(item[0])
            sums = [0.0]*dims
            for tok in item:
                for i, val in enumerate(tok):
                    sums[i] += float(val)
            vec = [v/len(item) for v in sums]
        else:
            vec = [float(x) for x in item]
        outs.append(_normalize(vec))
    return outs
