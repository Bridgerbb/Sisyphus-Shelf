from django import forms
from .models import MediaItem

class MediaItemForm(forms.ModelForm):
    class Meta:
        model = MediaItem
        fields = ['media_type','title', 'creator','genre', 'status', 'priority_flag', 'rating', 'notes', 'cover_image_url']
        
        # This tells Django to use Bootstrap CSS classes for the HTML inputs
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g.  The Lord of the Rings'}),
            'creator': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g.  J.R.R. Tolkien'}),
            'genre': forms.TextInput(attrs={'class': 'form-control bg-dark text-white border-secondary', 'placeholder': 'e.g.  Fantasy'}),
            'media_type': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'rating': forms.NumberInput(attrs={
                'class': 'form-control bg-dark text-white border-secondary', 
                'step': '0.1', 
                'min': '0', 
                'max': '10',
                'placeholder': 'e.g.  9.5/10'
            }),
            'priority_flag': forms.CheckboxInput(attrs={'class': 'form-check-input', 'role': 'switch'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Why do you want to play/read/watch this?'}),
            'cover_image_url': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Force Django to accept this form even if the hidden cover image input is completely empty
        self.fields['cover_image_url'].required = False