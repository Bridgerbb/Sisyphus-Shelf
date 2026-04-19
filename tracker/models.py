from django.db import models
from django.contrib.auth.models import User

class MediaItem(models.Model):
    # Link every item to a user
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True) 
    
    title = models.CharField(max_length=100)
    creator = models.CharField(max_length=100)
    genre = models.CharField(max_length=100, blank=True, null=True)
    
    MEDIA_TYPES = [
        ('Game', 'Game'),
        ('Book', 'Book'),
        ('Movie', 'Movie'),
        ('Other', 'Other'),
    ]
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES)
    
    STATUS_CHOICES = [
        ('Backlog', 'Backlog'),
        ('In-Progress', 'In-Progress'),
        ('Finished', 'Finished'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Backlog')
    
    priority_flag = models.BooleanField(default=False)
    rating = models.IntegerField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.title}'