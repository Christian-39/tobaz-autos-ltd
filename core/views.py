from django.shortcuts import render
from django.db.models import Sum, Count
from products.models import Product, Category
from sales.models import Sale
from django.contrib.auth.decorators import login_required


def home(request):
    """
    Home page view displaying featured products and statistics.
    """
    featured_products = Product.objects.filter(is_active=True)[:8]
    categories = Category.objects.all()
    
    # Statistics
    total_products = Product.objects.filter(is_active=True).count()
    total_categories = categories.count()
    
    context = {
        'featured_products': featured_products,
        'categories': categories,
        'total_products': total_products,
        'total_categories': total_categories,
        'title': 'Tobaz Autos - Premium Auto Parts & Vehicles',
        'meta_description': 'Tobaz Autos - Your trusted source for quality auto parts, small cars, tools, and oil. Browse our extensive inventory today.',
    }
    return render(request, 'core/home.html', context)


def about(request):
    """
    About page view.
    """
    context = {
        'title': 'About Us - Tobaz Autos',
        'meta_description': 'Learn about Tobaz Autos, your trusted partner for quality automotive products and services.',
    }
    return render(request, 'core/about.html', context)


def contact(request):
    """
    Contact page view.
    """
    context = {
        'title': 'Contact Us - Tobaz Autos',
        'meta_description': 'Get in touch with Tobaz Autos for all your automotive needs. We are here to help!',
    }
    return render(request, 'core/contact.html', context)
