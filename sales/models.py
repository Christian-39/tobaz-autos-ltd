from django.db import models
from django.contrib.auth.models import User
from products.models import Product


class Sale(models.Model):
    """
    Sale/Order model.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('transfer', 'Bank Transfer'),
        ('other', 'Other'),
    ]
    
    order_number = models.CharField(max_length=50, unique=True, blank=True)
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sales')
    customer_name = models.CharField(max_length=200, blank=True)
    customer_email = models.EmailField(blank=True)
    customer_phone = models.CharField(max_length=20, blank=True)
    
    # Sale details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='cash')
    
    # Financial fields
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.order_number:
            super().save(*args, **kwargs)
            self.order_number = f"SALE-{self.id:06d}"
            super().save(update_fields=['order_number'])
        else:
            super().save(*args, **kwargs)

    def __str__(self):
        return f"Sale {self.order_number}"

    def calculate_totals(self):
        """Calculate sale totals based on items."""
        items = self.items.all()
        self.subtotal = sum(item.total_price for item in items)
        self.total_amount = self.subtotal + self.tax_amount - self.discount_amount
        self.save(update_fields=['subtotal', 'total_amount'])

    @property
    def item_count(self):
        """Get total number of items in the sale."""
        return sum(item.quantity for item in self.items.all())


class SaleItem(models.Model):
    """
    Individual item in a sale.
    """
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        # Set unit price from product if not provided
        if not self.unit_price:
            self.unit_price = self.product.price
        
        # Calculate total price
        self.total_price = self.unit_price * self.quantity
        
        super().save(*args, **kwargs)
        
        # Update sale totals
        self.sale.calculate_totals()
        
        # Reduce product stock
        if self.sale.status == 'completed':
            self.product.quantity -= self.quantity
            self.product.save(update_fields=['quantity'])

    def __str__(self):
        return f"{self.quantity}x {self.product.name} in {self.sale.order_number}"

    def delete(self, *args, **kwargs):
        # Restore product stock if sale is completed
        if self.sale.status == 'completed':
            self.product.quantity += self.quantity
            self.product.save(update_fields=['quantity'])
        super().delete(*args, **kwargs)
        # Update sale totals after deletion
        self.sale.calculate_totals()
