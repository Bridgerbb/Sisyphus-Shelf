from django.db import models
from django.contrib.auth.models import User

class MediaItem(models.Model):
    # Link to the multi-user system
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Core Data
    title = models.CharField(max_length=255)
    creator = models.CharField(max_length=255)
    genre = models.CharField(max_length=100, blank=True, null=True)
    
    # Dropdown Choices
    MEDIA_TYPES = [
        ('Book', 'Book'),
        ('Movie', 'Movie'),
        ('Game', 'Game'),
        ('Other', 'Other'),
    ]
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPES)
    
    STATUS_CHOICES = [
        ('Backlog', 'Backlog'),
        ('In-Progress', 'In-Progress'),
        ('Finished', 'Finished'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Backlog')
    
    # The float field for our decimal ratings!
    rating = models.FloatField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    
    # Drag-and-drop & Priority trackers
    priority_flag = models.BooleanField(default=False)
    queue_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    # <-- OUR NEW BUSINESS LOGIC -->
    def save(self, *args, **kwargs):
        # If the item is finished, absolutely strip away its priority flag
        if self.status == 'Finished':
            self.priority_flag = False
            
        # Continue saving normally
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.title}'