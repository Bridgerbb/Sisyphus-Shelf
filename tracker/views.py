from django.shortcuts import render, redirect
from django.db.models import Case, When, Value, IntegerField 
from .forms import MediaItemForm
from .models import MediaItem

def dashboard(request):
    total_backlog = MediaItem.objects.filter(status='Backlog').count()
    in_progress = MediaItem.objects.filter(status='In-Progress').count()
    finished = MediaItem.objects.filter(status='Finished').count()
    
    priority_items = MediaItem.objects.filter(priority_flag=True).exclude(status='Finished').order_by('-created_at')[:5]
    
    context = {
        'total_backlog': total_backlog,
        'in_progress': in_progress,
        'finished': finished,
        'priority_items': priority_items,
    }
    return render(request, 'tracker/dashboard.html', context)

def pile(request):
    filter_type = request.GET.get('type')
    filter_status = request.GET.get('status')
    
    # 3-Tier Sorting: 0 = In-Progress, 1 = Backlog, 2 = Finished
    all_items = MediaItem.objects.annotate(
        custom_order=Case(
            When(status='In-Progress', then=Value(0)), 
            When(status='Backlog', then=Value(1)),     
            When(status='Finished', then=Value(2)),    
            output_field=IntegerField(),
        )
    ).order_by('custom_order', 'created_at') 
    
    if filter_type:
        all_items = all_items.filter(media_type=filter_type)
        
    if filter_status == 'Finished':
        all_items = all_items.filter(status='Finished')
    elif filter_status == 'Unfinished':
        all_items = all_items.exclude(status='Finished')
    
    context = {
        'items': all_items,
        'current_type': filter_type,
        'current_status': filter_status 
    }
    
    return render(request, 'tracker/pile.html', context)

def add_item(request):
    if request.method == 'POST':
        form = MediaItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('pile') 
    else:
        form = MediaItemForm()
    return render(request, 'tracker/add_item.html', {'form': form})

def item_detail(request, pk):
    return render(request, 'tracker/item_detail.html')