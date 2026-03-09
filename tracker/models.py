from django.db import models

class MediaItem(models.Model):
    MEDIA_TYPES = [
        ('Book', 'Book'),
        ('Movie', 'Movie'),
        ('Game', 'Game'),
    ]
    STATUS_CHOICES = [
        ('Backlog', 'Backlog'),
        ('In-Progress', 'In-Progress'),
        ('Finished', 'Finished'),
    ]

    title = models.CharField(max_length=255)
    creator = models.CharField(max_length=255, help_text="Author, Director, or Studio")
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='Backlog')
    priority_flag = models.BooleanField(default=False, help_text="Highlight for Next Up")
    rating = models.IntegerField(null=True, blank=True, choices=[(i, i) for i in range(1, 6)])
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.media_type})"