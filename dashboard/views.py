from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, F
from django.core.paginator import Paginator
from django.http import JsonResponse
from products.models import Product, Category, ProductImage, ProductVideo
from sales.models import Sale, SaleItem
from users.models import Profile
from .forms import ProductForm, ProductImageFormSet, ProductVideoFormSet, CategoryForm


@login_required
def dashboard(request):
    """
    Main dashboard view with statistics.
    """
    # Statistics
    total_products = Product.objects.filter(is_active=True).count()
    low_stock_products = Product.objects.filter(quantity__lte=5, quantity__gt=0).count()
    out_of_stock_products = Product.objects.filter(quantity=0).count()
    
    # Sales statistics
    total_sales = Sale.objects.filter(status='completed').count()
    total_revenue = Sale.objects.filter(status='completed').aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    
    # Recent sales
    recent_sales = Sale.objects.all()[:5]
    
    # Low stock products
    low_stock = Product.objects.filter(quantity__lte=5).order_by('quantity')[:5]
    
    # Top selling products
    top_products = SaleItem.objects.filter(
        sale__status='completed'
    ).values('product__name').annotate(
        total_sold=Sum('quantity')
    ).order_by('-total_sold')[:5]
    
    context = {
        'total_products': total_products,
        'low_stock_products': low_stock_products,
        'out_of_stock_products': out_of_stock_products,
        'total_sales': total_sales,
        'total_revenue': total_revenue,
        'recent_sales': recent_sales,
        'low_stock': low_stock,
        'top_products': top_products,
        'title': 'Dashboard - Tobaz Autos',
    }
    return render(request, 'dashboard/dashboard.html', context)


@login_required
def add_category(request):
    if not request.user.profile.user_type in ['staff', 'admin']:
        messages.error(request, 'Access Denied.')
        return redirect('dashboard:dashboard')

    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save() # This triggers your model's save() and creates the slug
            messages.success(request, f'Category "{category.name}" created successfully!')
            return redirect('dashboard:product_management')
    else:
        form = CategoryForm()

    context = {
        'form': form,
        'title': 'Add Category - Tobaz Autos',
    }
    return render(request, 'dashboard/add_category.html', context)


@login_required
def product_management(request):
    """
    Product management view.
    """
    products = Product.objects.all()
    
    # Search
    search = request.GET.get('q', '')
    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(sku__icontains=search) |
            Q(description__icontains=search)
        )
    
    # Filter by category
    category = request.GET.get('category', '')
    if category:
        products = products.filter(category__slug=category)
    
    # Filter by stock status
    stock_status = request.GET.get('stock', '')
    if stock_status == 'in_stock':
        products = products.filter(quantity__gt=5)
    elif stock_status == 'low_stock':
        products = products.filter(quantity__lte=5, quantity__gt=0)
    elif stock_status == 'out_of_stock':
        products = products.filter(quantity=0)
    
    # Pagination
    paginator = Paginator(products, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = Category.objects.all()
    
    context = {
        'products': page_obj,
        'categories': categories,
        'search': search,
        'selected_category': category,
        'stock_status': stock_status,
        'title': 'Product Management - Tobaz Autos',
    }
    return render(request, 'dashboard/product_management.html', context)


@login_required
def add_product(request):
    """
    Add new product view.
    """
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save()
            
            # Handle images
            images = request.FILES.getlist('images')
            for i, image in enumerate(images):
                ProductImage.objects.create(
                    product=product,
                    image=image,
                    is_primary=(i == 0),
                    order=i
                )
            
            # Handle videos
            videos = request.FILES.getlist('videos')
            for i, video in enumerate(videos):
                ProductVideo.objects.create(
                    product=product,
                    video=video,
                    order=i
                )
            
            messages.success(request, f'Product "{product.name}" created successfully!')
            return redirect('dashboard:product_management')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProductForm()
    
    categories = Category.objects.all()
    
    context = {
        'form': form,
        'categories': categories,
        'title': 'Add Product - Tobaz Autos',
    }
    return render(request, 'dashboard/add_product.html', context)


@login_required
def edit_product(request, slug):
    """
    Edit product view.
    """
    product = get_object_or_404(Product, slug=slug)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            product = form.save()
            
            # Handle new images
            images = request.FILES.getlist('images')
            for i, image in enumerate(images):
                ProductImage.objects.create(
                    product=product,
                    image=image,
                    order=product.images.count() + i
                )
            
            # Handle new videos
            videos = request.FILES.getlist('videos')
            for i, video in enumerate(videos):
                ProductVideo.objects.create(
                    product=product,
                    video=video,
                    order=product.videos.count() + i
                )
            
            messages.success(request, f'Product "{product.name}" updated successfully!')
            return redirect('dashboard:product_management')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProductForm(instance=product)
    
    categories = Category.objects.all()
    images = product.images.all()
    videos = product.videos.all()
    
    context = {
        'form': form,
        'product': product,
        'categories': categories,
        'images': images,
        'videos': videos,
        'title': f'Edit {product.name} - Tobaz Autos',
    }
    return render(request, 'dashboard/edit_product.html', context)


@login_required
def delete_product(request, slug):
    """
    Delete product view.
    """
    product = get_object_or_404(Product, slug=slug)
    
    if request.method == 'POST':
        product_name = product.name
        product.delete()
        messages.success(request, f'Product "{product_name}" deleted successfully!')
        return redirect('dashboard:product_management')
    
    context = {
        'product': product,
        'title': f'Delete {product.name} - Tobaz Autos',
    }
    return render(request, 'dashboard/delete_product.html', context)


@login_required
def delete_product_image(request, image_id):
    """
    Delete product image.
    """
    image = get_object_or_404(ProductImage, id=image_id)
    product_slug = image.product.slug
    image.delete()
    messages.success(request, 'Image deleted successfully!')
    return redirect('dashboard:edit_product', slug=product_slug)


@login_required
def delete_product_video(request, video_id):
    """
    Delete product video.
    """
    video = get_object_or_404(ProductVideo, id=video_id)
    product_slug = video.product.slug
    video.delete()
    messages.success(request, 'Video deleted successfully!')
    return redirect('dashboard:edit_product', slug=product_slug)


@login_required
def set_primary_image(request, image_id):
    """
    Set image as primary.
    """
    image = get_object_or_404(ProductImage, id=image_id)
    product = image.product
    
    # Unset all other images as primary
    ProductImage.objects.filter(product=product).update(is_primary=False)
    
    # Set this image as primary
    image.is_primary = True
    image.save()
    
    messages.success(request, 'Primary image updated!')
    return redirect('dashboard:edit_product', slug=product.slug)


@login_required
def inventory(request):
    """
    Inventory management view.
    """
    products = Product.objects.all()
    
    # Filter by stock status
    stock_filter = request.GET.get('stock', '')
    if stock_filter == 'low':
        products = products.filter(quantity__lte=5, quantity__gt=0)
    elif stock_filter == 'out':
        products = products.filter(quantity=0)
    
    # Update stock
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        new_quantity = request.POST.get('quantity')
        
        if product_id and new_quantity is not None:
            try:
                product = Product.objects.get(id=product_id)
                product.quantity = int(new_quantity)
                product.save()
                messages.success(request, f'Stock for "{product.name}" updated to {new_quantity}!')
            except Product.DoesNotExist:
                messages.error(request, 'Product not found.')
        
        return redirect('dashboard:inventory')
    
    # Pagination
    paginator = Paginator(products, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistics
    total_value = sum(p.price * p.quantity for p in Product.objects.all())
    low_stock_count = Product.objects.filter(quantity__lte=5, quantity__gt=0).count()
    out_of_stock_count = Product.objects.filter(quantity=0).count()
    
    context = {
        'products': page_obj,
        'total_value': total_value,
        'low_stock_count': low_stock_count,
        'out_of_stock_count': out_of_stock_count,
        'stock_filter': stock_filter,
        'title': 'Inventory Management - Tobaz Autos',
    }
    return render(request, 'dashboard/inventory.html', context)


@login_required
def users_list(request):
    """
    Users list view (admin only).
    """
    if not request.user.profile.is_staff_user:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard:dashboard')
    
    users = Profile.objects.all()
    
    # Search
    search = request.GET.get('q', '')
    if search:
        users = users.filter(
            Q(user__username__icontains=search) |
            Q(user__email__icontains=search) |
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search)
        )
    
    # Filter by user type
    user_type = request.GET.get('type', '')
    if user_type:
        users = users.filter(user_type=user_type)
    
    # Pagination
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'users': page_obj,
        'search': search,
        'user_type': user_type,
        'title': 'Users - Tobaz Autos',
    }
    return render(request, 'dashboard/users_list.html', context)


@login_required
def update_user_type(request, user_id):
    """
    Update user type (admin only).
    """
    if not request.user.profile.is_admin_user:
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('dashboard:dashboard')
    
    profile = get_object_or_404(Profile, user__id=user_id)
    
    if request.method == 'POST':
        new_type = request.POST.get('user_type')
        if new_type in ['customer', 'staff', 'admin']:
            profile.user_type = new_type
            profile.save()
            messages.success(request, f'User type updated for {profile.user.username}!')
    
    return redirect('dashboard:users_list')
