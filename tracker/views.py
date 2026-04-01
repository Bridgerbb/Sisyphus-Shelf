from django.shortcuts import render, redirect
from .forms import MediaItemForm
from .models import MediaItem

def dashboard(request):
    return render(request, 'tracker/dashboard.html')

def pile(request):
    # 1. Grab all items from the database, sorting by newest first
    all_items = MediaItem.objects.all().order_by('-created_at')
    
    # 2. Package them up in a dictionary
    context = {'items': all_items}
    
    # 3. Send that dictionary to the HTML template
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