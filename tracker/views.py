from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Case, When, Value, IntegerField, Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required # <-- NEW: Import the security lock
from .forms import MediaItemForm
from .models import MediaItem
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

# <-- NEW: Slap this lock on every single view! -->
@login_required
def dashboard(request):
    # <-- NEW: Filter everything by request.user so they only see their own stats -->
    total_backlog = MediaItem.objects.filter(user=request.user, status='Backlog').count()
    in_progress = MediaItem.objects.filter(user=request.user, status='In-Progress').count()
    finished = MediaItem.objects.filter(user=request.user, status='Finished').count()
    
    priority_items = MediaItem.objects.filter(user=request.user, priority_flag=True).exclude(status='Finished').order_by('-created_at')[:5]
    
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
    
    # <-- NEW: Start the query by instantly filtering out everyone else's items -->
    all_items = MediaItem.objects.filter(user=request.user).annotate(
        custom_order=Case(
            When(status='In-Progress', then=Value(0)), 
            When(status='Backlog', then=Value(1)),     
            When(status='Finished', then=Value(2)),    
            output_field=IntegerField(),
        )
    ).order_by('custom_order', 'created_at') 

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
    
    context = {
        'items': all_items,
        'current_type': filter_type,
        'current_status': filter_status,
        'search_query': search_query 
    }
    
    return render(request, 'tracker/pile.html', context)

@login_required
def add_item(request):
    if request.method == 'POST':
        form = MediaItemForm(request.POST)
        if form.is_valid():
            # <-- NEW: Pause the save, attach the logged-in user, then save to DB! -->
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
    # <-- NEW: Make sure the item belongs to request.user so they can't hack the URL! -->
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
    # <-- Secure the delete route too -->
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
            login(request, user) # Automatically log them in after signing up
            messages.success(request, f"Welcome to The Pile, {user.username}!")
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    
    return render(request, 'tracker/register.html', {'form': form})