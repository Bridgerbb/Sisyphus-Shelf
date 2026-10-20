from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class MediaItem(models.Model):
    # Link to the multi-user system
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Core Data
    title = models.CharField(max_length=255)
    creator = models.CharField(max_length=255)
    genre = models.CharField(max_length=100, blank=True, null=True)
    
    # --- AI Recommendation Metadata Fields ---
    tmdb_id = models.IntegerField(null=True, blank=True)
    synopsis = models.TextField(blank=True, null=True)
    
    # Dropdown Choices
    MEDIA_TYPES = [
        ('Book', 'Book'),
        ('Movie', 'Movie/TV'),
        ('Game', 'Game'),
        ('Other', 'Other'),
    ]
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPES)
    cover_image_url = models.URLField(max_length=500, blank=True, null=True)
    
    STATUS_CHOICES = [
        ('Backlog', 'Backlog'),
        ('In-Progress', 'In-Progress'),
        ('Finished', 'Finished'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Backlog')
    
    # Rating & Notes
    rating = models.FloatField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    
    # Drag-and-drop & Priority trackers
    priority_flag = models.BooleanField(default=False)
    queue_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def backlog_age_days(self):
        """Calculates days spent on the backlog for the beta time-decay penalty."""
        if self.status == 'Backlog' and self.created_at:
            return (timezone.now() - self.created_at).days
        return 0

    def save(self, *args, **kwargs):
        # If the item is finished, strip away its priority flag
        if self.status == 'Finished':
            self.priority_flag = False
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.title}'


class RecommendationCache(models.Model):
    """Stores generated recommendation utility scores to maintain low retrieval latency."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(MediaItem, on_delete=models.CASCADE)
    composite_score = models.FloatField()
    s_content = models.FloatField(default=0.0)
    s_collaborative = models.FloatField(default=0.0)
    s_serendipity = models.FloatField(default=0.0)
    calculated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'item')
        ordering = ['-composite_score']

    def __str__(self):
        return f"Rec for {self.user.username}: {self.item.title} ({self.composite_score:.2f})"