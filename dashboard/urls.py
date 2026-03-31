from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('products/', views.product_management, name='product_management'),
    path('categories/add/', views.add_category, name='add_category'),
    path('products/add/', views.add_product, name='add_product'),
    path('products/<slug:slug>/edit/', views.edit_product, name='edit_product'),
    path('products/<slug:slug>/delete/', views.delete_product, name='delete_product'),
    path('products/image/<int:image_id>/delete/', views.delete_product_image, name='delete_image'),
    path('products/video/<int:video_id>/delete/', views.delete_product_video, name='delete_video'),
    path('products/image/<int:image_id>/primary/', views.set_primary_image, name='set_primary_image'),
    path('inventory/', views.inventory, name='inventory'),
    path('users/', views.users_list, name='users_list'),
    path('users/<int:user_id>/update-type/', views.update_user_type, name='update_user_type'),
]
