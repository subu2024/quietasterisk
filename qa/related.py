"""Related essays: TF-IDF cosine similarity over essay bodies."""

import re
from typing import Dict, List

from .models import Entry


def _clean(text: str) -> str:
    text = re.sub(r"[^a-z0-9\s]", "", text.lower())
    return re.sub(r"\s+", " ", text).strip()


def build_related_map(essays: List[Entry], threshold: float, count: int) -> Dict[str, List[Entry]]:
    """Map entry URL -> up to `count` related entries scoring at least `threshold`."""
    if len(essays) < 2:
        return {}
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    vectors = TfidfVectorizer(max_features=5000, stop_words="english", ngram_range=(1, 2)) \
        .fit_transform([_clean(e.body) for e in essays])
    sim = cosine_similarity(vectors)

    related: Dict[str, List[Entry]] = {}
    for i, entry in enumerate(essays):
        ranked = sorted(((j, sim[i][j]) for j in range(len(essays)) if i != j and sim[i][j] >= threshold),
                        key=lambda t: t[1], reverse=True)[:count]
        related[entry.url] = [essays[j] for j, _ in ranked]
    return related
