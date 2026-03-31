from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Product, Category, ProductImage, ProductVideo


def product_list(request):
    """
    Product list view with search and filter functionality.
    """
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.filter(is_active=True)
    
    # Search functionality
    search_query = request.GET.get('q', '')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(sku__icontains=search_query)
        )
    
    # Category filter
    category_slug = request.GET.get('category', '')
    if category_slug:
        products = products.filter(category__slug=category_slug)
    
    # Category type filter
    category_type = request.GET.get('type', '')
    if category_type:
        products = products.filter(category_type=category_type)
    
    # Sorting
    sort_by = request.GET.get('sort', '-created_at')
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'name':
        products = products.order_by('name')
    else:
        products = products.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'products': page_obj,
        'categories': categories,
        'search_query': search_query,
        'selected_category': category_slug,
        'selected_type': category_type,
        'sort_by': sort_by,
        'total_results': products.count(),
        'title': 'Products - Tobaz Autos',
        'meta_description': 'Browse our extensive collection of auto parts, small cars, tools, and oil products.',
    }
    return render(request, 'products/product_list.html', context)


def product_detail(request, slug):
    """
    Product detail view displaying all product information including images and videos.
    """
    product = get_object_or_404(Product, slug=slug, is_active=True)
    
    # Get related products
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id)[:4]
    
    # Get all images and videos
    images = product.images.all()
    videos = product.videos.all()
    
    context = {
        'product': product,
        'images': images,
        'videos': videos,
        'related_products': related_products,
        'title': f'{product.name} - Tobaz Autos',
        'meta_description': product.meta_description or product.description[:160],
    }
    return render(request, 'products/product_detail.html', context)


def category_list(request):
    """
    Category list view displaying all active product categories.
    """
    # Fetch all active categories
    categories = Category.objects.filter(is_active=True).order_by('name')
    
    # Search functionality within categories (optional, but helpful)
    search_query = request.GET.get('q', '')
    if search_query:
        categories = categories.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Pagination for categories (in case you have many)
    paginator = Paginator(categories, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'categories': page_obj,
        'search_query': search_query,
        'total_results': categories.count(),
        'title': 'Product Categories - Tobaz Autos',
        'meta_description': 'Explore our wide range of automotive categories including spare parts, oils, tools, and vehicles.',
    }
    return render(request, 'products/category_list.html', context)
    

def category_detail(request, slug):
    """
    Category detail view showing products in a specific category.
    """
    category = get_object_or_404(Category, slug=slug, is_active=True)
    products = Product.objects.filter(category=category, is_active=True)
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'products': page_obj,
        'title': f'{category.name} - Tobaz Autos',
        'meta_description': category.description or f'Browse {category.name} products at Tobaz Autos.',
    }
    return render(request, 'products/category_detail.html', context)
