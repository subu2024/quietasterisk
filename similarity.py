"""
Content similarity analysis for related posts.
Uses TF-IDF vectorization and cosine similarity.
"""

from typing import List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from models import Post
from utils import clean_text
from config import SIMILARITY_THRESHOLD


def compute_similarity(posts: List[Post]):
    """
    Compute similarity matrix between all posts.
    
    Args:
        posts: List of Post objects
        
    Returns:
        2D array of similarity scores between posts
    """
    if not posts:
        return []
    
    # Clean and vectorize post content
    content = [clean_text(p.body) for p in posts]
    
    vectorizer = TfidfVectorizer(
        max_features=5000,
        stop_words='english',
        ngram_range=(1, 2)
    )
    
    vectors = vectorizer.fit_transform(content)
    return cosine_similarity(vectors)


def build_related_map(posts: List[Post], sim_matrix) -> Dict[str, List[str]]:
    """
    Build a mapping of posts to their related posts.
    
    Args:
        posts: List of Post objects
        sim_matrix: Similarity matrix from compute_similarity()
        
    Returns:
        Dictionary mapping post slugs to lists of related post slugs
    """
    related = {}
    
    for i, post in enumerate(posts):
        # Find posts with similarity above threshold
        scores = sorted(
            [
                (j, sim_matrix[i][j]) 
                for j in range(len(posts))
                if i != j and sim_matrix[i][j] >= SIMILARITY_THRESHOLD
            ],
            key=lambda x: x[1],
            reverse=True
        )[:3]  # Keep top 3 related posts
        
        # Store related post slugs
        related[post.slug] = [posts[j].slug for j, _ in scores]
    
    return related
