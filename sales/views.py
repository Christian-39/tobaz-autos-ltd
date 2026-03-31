from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import Sale, SaleItem
from products.models import Product


@login_required
def sale_list(request):
    """
    List all sales.
    """
    sales = Sale.objects.all()
    
    # Filter by status
    status = request.GET.get('status', '')
    if status:
        sales = sales.filter(status=status)
    
    # Search
    search = request.GET.get('q', '')
    if search:
        sales = sales.filter(
            models.Q(order_number__icontains=search) |
            models.Q(customer_name__icontains=search) |
            models.Q(customer_email__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(sales, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistics
    total_sales = Sale.objects.filter(status='completed').count()
    total_revenue = Sale.objects.filter(status='completed').aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    average_sale = total_revenue / total_sales if total_sales > 0 else 0
    
    
    context = {
        'sales': page_obj,
        'total_sales': total_sales,
        'total_revenue': total_revenue,
        'average_sale': average_sale,
        'status': status,
        'search': search,
        'title': 'Sales - Tobaz Autos',
    }
    return render(request, 'sales/sale_list.html', context)


@login_required
def sale_detail(request, order_number):
    """
    Sale detail view.
    """
    sale = get_object_or_404(Sale, order_number=order_number)
    items = sale.items.all()
    
    context = {
        'sale': sale,
        'items': items,
        'title': f'Sale {order_number} - Tobaz Autos',
    }
    return render(request, 'sales/sale_detail.html', context)


@login_required
def create_sale(request):
    """
    Create a new sale.
    """
    if request.method == 'POST':
        # Get form data
        customer_name = request.POST.get('customer_name', '')
        customer_email = request.POST.get('customer_email', '')
        customer_phone = request.POST.get('customer_phone', '')
        payment_method = request.POST.get('payment_method', 'cash')
        notes = request.POST.get('notes', '')
        
        # Create sale
        sale = Sale.objects.create(
            customer=request.user if request.user.is_authenticated else None,
            customer_name=customer_name,
            customer_email=customer_email,
            customer_phone=customer_phone,
            payment_method=payment_method,
            notes=notes,
            status='pending'
        )
        
        # Process items
        product_ids = request.POST.getlist('product_id[]')
        quantities = request.POST.getlist('quantity[]')
        
        for product_id, quantity in zip(product_ids, quantities):
            try:
                product = Product.objects.get(id=product_id)
                qty = int(quantity)
                
                # Check stock
                if product.quantity < qty:
                    messages.error(request, f'Insufficient stock for {product.name}')
                    sale.delete()
                    return redirect('sales:create_sale')
                
                SaleItem.objects.create(
                    sale=sale,
                    product=product,
                    quantity=qty,
                    unit_price=product.price
                )
                
                # Reduce stock immediately
                product.quantity -= qty
                product.save()
                
            except Product.DoesNotExist:
                continue
        
        # Update sale totals
        sale.calculate_totals()
        sale.status = 'completed'
        sale.save()
        
        messages.success(request, f'Sale {sale.order_number} created successfully!')
        return redirect('sales:sale_detail', order_number=sale.order_number)
    
    products = Product.objects.filter(is_active=True, quantity__gt=0)
    
    context = {
        'products': products,
        'title': 'Create Sale - Tobaz Autos',
    }
    return render(request, 'sales/create_sale.html', context)


@login_required
def cancel_sale(request, order_number):
    """
    Cancel a sale and restore stock.
    """
    sale = get_object_or_404(Sale, order_number=order_number)
    
    if sale.status == 'cancelled':
        messages.warning(request, 'This sale is already cancelled.')
        return redirect('sales:sale_detail', order_number=order_number)
    
    if request.method == 'POST':
        # Restore stock for all items
        for item in sale.items.all():
            item.product.quantity += item.quantity
            item.product.save()
        
        sale.status = 'cancelled'
        sale.save()
        
        messages.success(request, f'Sale {order_number} has been cancelled.')
        return redirect('sales:sale_list')
    
    context = {
        'sale': sale,
        'title': 'Cancel Sale - Tobaz Autos',
    }
    return render(request, 'sales/cancel_sale.html', context)


@login_required
def sales_report(request):
    """
    Sales report view with statistics.
    """
    from django.utils import timezone
    from datetime import timedelta
    
    # Date range
    days = int(request.GET.get('days', 30))
    start_date = timezone.now() - timedelta(days=days)
    
    # Sales statistics
    completed_sales = Sale.objects.filter(status='completed', created_at__gte=start_date)
    
    total_sales = completed_sales.count()
    total_revenue = completed_sales.aggregate(total=Sum('total_amount'))['total'] or 0
    total_items = SaleItem.objects.filter(sale__in=completed_sales).aggregate(
        total=Sum('quantity')
    )['total'] or 0

    average_sale = total_revenue / total_sales if total_sales > 0 else 0
    average_items = total_items / total_sales if total_sales > 0 else 0
    
    # Sales by product
    product_sales = SaleItem.objects.filter(
        sale__in=completed_sales
    ).values('product__name').annotate(
        total_quantity=Sum('quantity'),
        total_revenue=Sum('total_price')
    ).order_by('-total_quantity')[:10]
    
    # Sales by payment method
    payment_method_sales = completed_sales.values('payment_method').annotate(
        count=Count('id'),
        total=Sum('total_amount')
    )
    
    context = {
        'total_sales': total_sales,
        'total_revenue': total_revenue,
        'total_items': total_items,
        'average_sale': average_sale,
        'average_items': average_items,
        'product_sales': product_sales,
        'payment_method_sales': payment_method_sales,
        'days': days,
        'title': 'Sales Report - Tobaz Autos',
    }
    return render(request, 'sales/sales_report.html', context)


@login_required
def get_product_price(request, product_id):
    """
    AJAX endpoint to get product price.
    """
    try:
        product = Product.objects.get(id=product_id)
        return JsonResponse({
            'success': True,
            'price': float(product.price),
            'name': product.name,
            'stock': product.quantity
        })
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Product not found'})
