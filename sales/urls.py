from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    path('', views.sale_list, name='sale_list'),
    path('create/', views.create_sale, name='create_sale'),
    path('report/', views.sales_report, name='sales_report'),
    path('<str:order_number>/', views.sale_detail, name='sale_detail'),
    path('<str:order_number>/cancel/', views.cancel_sale, name='cancel_sale'),
    path('api/product-price/<int:product_id>/', views.get_product_price, name='get_product_price'),
]
