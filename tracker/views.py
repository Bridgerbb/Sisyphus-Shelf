from django.shortcuts import render

def dashboard(request):
    # Returns the main landing page
    return render(request, 'tracker/dashboard.html')

def pile(request):
    # Returns the archive list
    return render(request, 'tracker/pile.html')

def add_item(request):
    # Returns the form page
    return render(request, 'tracker/add_item.html')

def item_detail(request, pk):
    # Returns the detail page for a specific item using its Primary Key (pk)
    return render(request, 'tracker/item_detail.html')