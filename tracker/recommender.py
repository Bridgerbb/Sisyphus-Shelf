import os
import pickle
import numpy as np
from django.utils import timezone
from .models import MediaItem, RecommendationCache

class HybridRecommender:
    def __init__(self):
        self.svd_model = None
        self.text_embeddings = None
        # Load trained offline artifacts if they exist
        # self._load_artifacts()

    def _load_artifacts(self):
        svd_path = os.path.join(os.path.dirname(__file__), 'ml_models', 'svd_model.pkl')
        if os.path.exists(svd_path):
            with open(svd_path, 'rb') as f:
                self.svd_model = pickle.load(f)

    def compute_utility_score(self, s_content, s_collaborative, s_serendipity, age_in_days,
                               w1=0.4, w2=0.4, alpha=0.2, beta=0.001):
        """
        Composite Utility Function:
        Score = w1 * S_content + w2 * S_collaborative + alpha * S_serendipity - beta * t_watchlist_age
        """
        time_decay = beta * age_in_days
        score = (w1 * s_content) + (w2 * s_collaborative) + (alpha * s_serendipity) - time_decay
        return score

    def generate_recommendations_for_user(self, user, top_k=5, w1=0.4, w2=0.4, alpha=0.2, beta=0.01):
        """
        Scores all 'Backlog' media items for a user and returns top-K ranked recommendations.
        """
        backlog_items = MediaItem.objects.filter(user=user, status='Backlog')
        recommendations = []

        for item in backlog_items:
            # Placeholder signals until model pipeline files are serialized
            s_collaborative = (item.rating or 3.5) / 5.0
            s_content = 0.75
            s_serendipity = 0.5

            composite_score = self.compute_utility_score(
                s_content=s_content,
                s_collaborative=s_collaborative,
                s_serendipity=s_serendipity,
                age_in_days=item.backlog_age_days,
                w1=w1, w2=w2, alpha=alpha, beta=beta
            )

            # Update or create cached entry in SQLite
            RecommendationCache.objects.update_or_create(
                user=user,
                item=item,
                defaults={
                    'composite_score': composite_score,
                    's_content': s_content,
                    's_collaborative': s_collaborative,
                    's_serendipity': s_serendipity,
                }
            )

        # Retrieve top K items sorted by composite score
        cached_recs = RecommendationCache.objects.filter(user=user).order_by('-composite_score')[:top_k]
        return cached_recs

# Global engine instance
recommender_engine = HybridRecommender()