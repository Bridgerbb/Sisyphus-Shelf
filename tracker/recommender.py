import os
import pickle
import numpy as np
from django.utils import timezone
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .models import MediaItem, RecommendationCache


class HybridRecommender:
    def __init__(self):
        self.svd_model = None
        self._load_artifacts()

    def _load_artifacts(self):
        svd_path = os.path.join(os.path.dirname(__file__), 'ml_models', 'svd_model.pkl')
        if os.path.exists(svd_path):
            with open(svd_path, 'rb') as f:
                self.svd_model = pickle.load(f)

    def _calculate_content_similarity(self, target_item, user_completed_items):
        """
        Computes TF-IDF cosine similarity between a backlog item's synopsis/title
        and the user's highly-rated completed items.
        """
        if not user_completed_items.exists():
            return 0.5  # Neutral default score if user has no completed items yet

        # Combine titles and synopses into text representations
        corpus = [
            f"{item.title} {item.synopsis or ''} {item.creator or ''} {item.genre or ''}"
            for item in user_completed_items
        ]
        target_text = f"{target_item.title} {target_item.synopsis or ''} {target_item.creator or ''} {target_item.genre or ''}"
        
        corpus.append(target_text)

        # Vectorize corpus and compute average similarity to liked items
        vectorizer = TfidfVectorizer(stop_words='english')
        try:
            tfidf_matrix = vectorizer.fit_transform(corpus)
            target_vector = tfidf_matrix[-1]
            liked_vectors = tfidf_matrix[:-1]
            
            similarities = cosine_similarity(target_vector, liked_vectors)
            return float(np.mean(similarities))
        except ValueError:
            # Fallback if corpus contains only stop words
            return 0.5

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
        completed_items = MediaItem.objects.filter(user=user, status='Completed')
        
        # Highly rated items serve as the positive preference anchor
        liked_items = completed_items.filter(rating__gte=4.0) if completed_items.exists() else completed_items

        for item in backlog_items:
            # 1. Collaborative signal (User rating or global fallback)
            s_collaborative = (item.rating or 3.5) / 5.0

            # 2. Dynamic Content signal via TF-IDF similarity
            s_content = self._calculate_content_similarity(item, liked_items)

            # 3. Serendipity / Discovery signal (inverse of popularity/rating bias)
            s_serendipity = 1.0 - (s_collaborative * 0.5)

            composite_score = self.compute_utility_score(
                s_content=s_content,
                s_collaborative=s_collaborative,
                s_serendipity=s_serendipity,
                age_in_days=item.backlog_age_days,
                w1=w1, w2=w2, alpha=alpha, beta=beta
            )

            # Update or create cached entry
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