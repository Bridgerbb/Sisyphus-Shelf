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
from django.http import JsonResponse
from dotenv import load_dotenv
from django.shortcuts import render

load_dotenv()

@login_required
def dashboard(request):
    total_backlog = MediaItem.objects.filter(user=request.user, status='Backlog').count()
    in_progress = MediaItem.objects.filter(user=request.user, status='In-Progress').count()
    finished = MediaItem.objects.filter(user=request.user, status='Finished').count()
    
    priority_items = MediaItem.objects.filter(user=request.user, priority_flag=True).exclude(status='Finished').order_by('queue_order', '-created_at')
    
    context = {
        'total_backlog': total_backlog,
        'in_progress': in_progress,
        'finished': finished,
        'priority_items': priority_items,
    }
    return render(request, 'tracker/dashboard.html', context)

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
    
    # <-- NEW: Pagination Logic -->
    paginator = Paginator(all_items, 15) # Show 15 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'items': page_obj, # <-- Pass page_obj instead of all_items
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
        if form.is_valid():
            form.save()
            messages.success(request, f"'{item.title}' was successfully updated!")
            return redirect('pile') 
    else:
        form = MediaItemForm(instance=item)
        
    context = {
        'form': form,
        'item': item
    }
    return render(request, 'tracker/item_detail.html', context)

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
    
def search_tmdb(request):
    query = request.GET.get('q')
    api_key = os.getenv('TMDB_API_KEY')
    
    if not query:
        return JsonResponse({'error': 'No query provided'}, status=400)

    url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={query}"
    response = requests.get(url)
    data = response.json()

    # We just want the top 5 results to keep it simple
    results = data.get('results', [])[:5]
    
    # Format the data for our frontend
    formatted_results = []
    for item in results:
        formatted_results.append({
            'title': item.get('title'),
            'release_date': item.get('release_date', '')[:4], # Just the year
            'poster_path': f"https://image.tmdb.org/t/p/w200{item.get('poster_path')}",
            'overview': item.get('overview'),
        })

    return JsonResponse(formatted_results, safe=False)
def search_metadata(request):
    query = request.GET.get('q')
    media_type = request.GET.get('type') # 'movie' or 'book'
    
    if not query:
        return JsonResponse([], safe=False)

    results = []

    # MOVIE SEARCH (TMDB)
    if media_type == 'movie':
        api_key = os.getenv('TMDB_API_KEY')
        url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={query}"
        response = requests.get(url)
        if response.status_code == 200:
            for item in response.json().get('results', [])[:5]:
                results.append({
                    'title': item.get('title'),
                    'creator': 'Movie', # Defaulting for now
                    'genre': 'Film',
                    'image': f"https://image.tmdb.org/t/p/w200{item.get('poster_path')}" if item.get('poster_path') else "",
                    'description': item.get('overview', '')
                })

    # BOOK SEARCH (Google Books)
    elif media_type == 'book':
            api_key = os.getenv('GOOGLE_BOOKS_KEY')
            url = f"https://www.googleapis.com/books/v1/volumes?q={query}"
            
            # Only add the key if it's NOT the placeholder and NOT empty
            if api_key and api_key != "your_key_here":
                url += f"&key={api_key}"
                
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                for item in data.get('items', [])[:5]:
                    info = item.get('volumeInfo', {})
                    image_links = info.get('imageLinks', {})
                    # Ensuring we use HTTPS for images to avoid security warnings
                    image_url = image_links.get('thumbnail') or image_links.get('smallThumbnail') or ""
                    image_url = image_url.replace('http://', 'https://')

                    results.append({
                        'title': info.get('title', 'Unknown Title'),
                        'creator': ", ".join(info.get('authors', ['Unknown Author'])),
                        'genre': ", ".join(info.get('categories', ['Book'])),
                        'image': image_url,
                        'description': info.get('description', '')
                    })

    return JsonResponse(results, safe=False)