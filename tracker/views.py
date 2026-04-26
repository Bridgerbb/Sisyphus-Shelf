from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Case, When, Value, IntegerField, Q, F
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import MediaItemForm
from .models import MediaItem
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
import json
from django.http import JsonResponse
from django.core.paginator import Paginator
import os
import requests
import random  # Added for the "I'm Feeling Lucky" feature
from dotenv import load_dotenv

load_dotenv()

# --- HELPER FUNCTIONS ---

def get_igdb_token():
    """
    Automatically fetches a fresh OAuth token from Twitch.
    """
    client_id = os.getenv('TWITCH_CLIENT_ID')
    client_secret = os.getenv('TWITCH_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        return None

    url = "https://id.twitch.tv/oauth2/token"
    params = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }
    
    try:
        response = requests.post(url, params=params)
        if response.status_code == 200:
            return response.json().get('access_token')
    except Exception as e:
        print(f"Twitch Token Error: {e}")
    return None

# --- ENHANCED VIEWS ---

@login_required
def dashboard(request):
    """
    Dashboard with 'Shelf Weight' statistics for the demo.
    """
    items = MediaItem.objects.filter(user=request.user)
    
    # Enhanced Statistics
    stats = {
        'total': items.count(),
        'backlog': items.filter(status='Backlog').count(),
        'in_progress': items.filter(status='In-Progress').count(),
        'finished': items.filter(status='Finished').count(),
        # Specific breakdown for 'Currently Doing'
        'reading': items.filter(media_type='Book', status='In-Progress').count(),
        'playing': items.filter(media_type='Game', status='In-Progress').count(),
        'watching': items.filter(media_type='Movie', status='In-Progress').count(),
    }
    
    priority_items = items.filter(priority_flag=True).exclude(status='Finished').order_by('queue_order', '-created_at')
    
    context = {
        'stats': stats,
        'priority_items': priority_items,
    }
    return render(request, 'tracker/dashboard.html', context)

@login_required
def random_item(request):
    """
    'I'm Feeling Lucky' - Picks a random unfinished item.
    Great 'Demo Closer' feature.
    """
    backlog = MediaItem.objects.filter(user=request.user).exclude(status='Finished')
    
    if backlog.exists():
        selected = random.choice(list(backlog))
        messages.info(request, f"🎲 Sisyphus chose for you: {selected.title}")
        return redirect('item_detail', pk=selected.pk)
    
    messages.warning(request, "The hill is empty! Add something to the pile first.")
    return redirect('pile')

@login_required
def pile(request):
    filter_type = request.GET.get('type')
    filter_status = request.GET.get('status')
    search_query = request.GET.get('q')
    sort_by = request.GET.get('sort', '')
    
    all_items = MediaItem.objects.filter(user=request.user).annotate(
        custom_order=Case(
            When(status='In-Progress', then=Value(0)), 
            When(status='Backlog', then=Value(1)),     
            When(status='Finished', then=Value(2)),    
            output_field=IntegerField(),
        )
    )

    if search_query:
        all_items = all_items.filter(
            Q(title__icontains=search_query) | 
            Q(creator__icontains=search_query) |
            Q(genre__icontains=search_query) 
        )
    
    if filter_type:
        all_items = all_items.filter(media_type=filter_type)
        
    if filter_status == 'Finished':
        all_items = all_items.filter(status='Finished')
    elif filter_status == 'Unfinished':
        all_items = all_items.exclude(status='Finished')

    if sort_by == 'highest':
        all_items = all_items.order_by(F('rating').desc(nulls_last=True), 'custom_order', 'created_at')
    elif sort_by == 'lowest':
        all_items = all_items.order_by(F('rating').asc(nulls_last=True), 'custom_order', 'created_at')
    else:
        all_items = all_items.order_by('custom_order', 'created_at')
    
    paginator = Paginator(all_items, 15) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'items': page_obj, 
        'current_type': filter_type,
        'current_status': filter_status,
        'search_query': search_query,
        'current_sort': sort_by 
    }
    
    return render(request, 'tracker/pile.html', context)

@login_required
def add_item(request):
    if request.method == 'POST':
        form = MediaItemForm(request.POST)
        if 'cover_image_url' in form.fields:
            form.fields['cover_image_url'].required = False
            
        if form.is_valid():
            item = form.save(commit=False)
            item.user = request.user
            item.save()
            messages.success(request, f"'{item.title}' was added to your pile!")
            return redirect('pile') 
    else:
        form = MediaItemForm()
    return render(request, 'tracker/add_item.html', {'form': form})

@login_required
def item_detail(request, pk):
    item = get_object_or_404(MediaItem, pk=pk, user=request.user)
    if request.method == 'POST':
        form = MediaItemForm(request.POST, instance=item)
        if 'cover_image_url' in form.fields:
            form.fields['cover_image_url'].required = False

        if form.is_valid():
            item = form.save()
            messages.success(request, f"'{item.title}' was successfully updated!")
            
            if request.POST.get('action') == 'save_and_view':
                return redirect('item_detail', pk=item.pk)
            else:
                return redirect('pile') 
        else:
            messages.error(request, "There was an error saving your changes.")
    else:
        form = MediaItemForm(instance=item)
    return render(request, 'tracker/item_detail.html', {'form': form, 'item': item})

@login_required
def delete_item(request, pk):
    item = get_object_or_404(MediaItem, pk=pk, user=request.user)
    if request.method == 'POST':
        title = item.title 
        item.delete()
        messages.error(request, f"🗑️ '{title}' was permanently deleted.")
    return redirect('pile')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to The Pile, {user.username}!")
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'tracker/register.html', {'form': form})

@login_required
def update_queue_order(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        ordered_ids = data.get('ordered_ids', [])
        for index, item_id in enumerate(ordered_ids):
            MediaItem.objects.filter(id=item_id, user=request.user).update(queue_order=index)
        return JsonResponse({'status': 'success'})

def search_metadata(request):
    query = request.GET.get('q')
    media_type = request.GET.get('type', '').lower()
    
    if not query:
        return JsonResponse([], safe=False)

    results = []

    # 🎬 MOVIE SEARCH (TMDB)
    if media_type == 'movie':
        api_key = os.getenv('TMDB_API_KEY')
        url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={query}"
        response = requests.get(url)
        if response.status_code == 200:
            for item in response.json().get('results', [])[:5]:
                results.append({
                    'title': item.get('title'),
                    'creator': 'Movie', 
                    'genre': 'Film',
                    'image': f"https://image.tmdb.org/t/p/w500{item.get('poster_path')}" if item.get('poster_path') else "",
                    'description': item.get('overview', '')
                })

    # 📚 BOOK SEARCH (Google Books)
    elif media_type == 'book':
        api_key = os.getenv('GOOGLE_BOOKS_KEY')
        url = f"https://www.googleapis.com/books/v1/volumes?q={query}"
        if api_key and api_key != "your_key_here":
            url += f"&key={api_key}"
            
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            for item in data.get('items', [])[:5]:
                info = item.get('volumeInfo', {})
                image_links = info.get('imageLinks', {})
                image_url = image_links.get('thumbnail') or image_links.get('smallThumbnail') or ""
                image_url = image_url.replace('http://', 'https://')
                
                results.append({
                    'title': info.get('title', 'Unknown Title'),
                    'creator': ", ".join(info.get('authors', ['Unknown Author'])),
                    'genre': ", ".join(info.get('categories', ['Book'])),
                    'image': image_url,
                    'description': info.get('description', '')
                })

    # 🎮 GAME SEARCH (IGDB via Twitch)
    elif media_type == 'game':
        client_id = os.getenv('TWITCH_CLIENT_ID')
        token = get_igdb_token()
        
        if client_id and token:
            headers = {
                'Client-ID': client_id,
                'Authorization': f'Bearer {token}',
            }
            body = f'search "{query}"; fields name, cover.url, genres.name, summary; limit 5;'
            url = "https://api.igdb.com/v4/games"
            
            response = requests.post(url, headers=headers, data=body)
            if response.status_code == 200:
                for item in response.json():
                    cover_data = item.get('cover', {})
                    img_url = cover_data.get('url', '').replace('t_thumb', 't_cover_big')
                    if img_url:
                        img_url = "https:" + img_url

                    results.append({
                        'title': item.get('name'),
                        'creator': "Game Studio",
                        'genre': item.get('genres', [{}])[0].get('name', 'Game'),
                        'image': img_url,
                        'description': item.get('summary', '')
                    })

    return JsonResponse(results, safe=False)