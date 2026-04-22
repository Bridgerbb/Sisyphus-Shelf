from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('pile/', views.pile, name='pile'),
    path('add/', views.add_item, name='add_item'),
    path('item/<int:pk>/', views.item_detail, name='item_detail'),
    path('item/<int:pk>/delete/', views.delete_item, name='delete_item'),
    path('register/', views.register, name='register'),
    path('update-queue/', views.update_queue_order, name='update_queue_order'),
]