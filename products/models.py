from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Category(models.Model):
    """
    Product category model.
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text='Font Awesome icon class')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('products:category_detail', kwargs={'slug': self.slug})


class Product(models.Model):
    """
    Product model with support for multiple images and videos.
    """
    CATEGORY_CHOICES = [
        ('small_cars', 'Small Cars'),
        ('auto_parts', 'Auto Parts'),
        ('tools', 'Tools'),
        ('oil', 'Oil'),
    ]

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    category_type = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='auto_parts')
    price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)
    description = models.TextField()
    specifications = models.TextField(blank=True, help_text='Technical specifications')
    sku = models.CharField(max_length=50, unique=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    # SEO fields
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.CharField(max_length=500, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if not self.sku:
            self.sku = f"TBZ-{self.id or 'NEW'}-{self.slug[:10].upper()}"
        super().save(*args, **kwargs)
        # Update SKU after first save if it was 'NEW'
        if 'NEW' in self.sku:
            self.sku = f"TBZ-{self.id}-{self.slug[:10].upper()}"
            super().save(update_fields=['sku'])

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('products:product_detail', kwargs={'slug': self.slug})

    @property
    def is_in_stock(self):
        return self.quantity > 0

    @property
    def stock_status(self):
        if self.quantity == 0:
            return 'out_of_stock'
        elif self.quantity <= 5:
            return 'low_stock'
        return 'in_stock'

    @property
    def primary_image(self):
        """Get the primary/first image of the product."""
        image = self.images.filter(is_primary=True).first()
        if not image:
            image = self.images.first()
        return image

    @property
    def total_sales(self):
        """Get total quantity sold for this product."""
        from sales.models import SaleItem
        total = SaleItem.objects.filter(product=self).aggregate(
            total=models.Sum('quantity')
        )['total']
        return total or 0


class ProductImage(models.Model):
    """
    Product image model supporting multiple images per product.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/images/%Y/%m/')
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"Image for {self.product.name}"

    def save(self, *args, **kwargs):
        # Ensure only one primary image per product
        if self.is_primary:
            ProductImage.objects.filter(product=self.product).update(is_primary=False)
        super().save(*args, **kwargs)


class ProductVideo(models.Model):
    """
    Product video model supporting multiple videos per product.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='videos')
    video = models.FileField(upload_to='products/videos/%Y/%m/')
    title = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    thumbnail = models.ImageField(upload_to='products/video_thumbnails/%Y/%m/', blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"Video for {self.product.name}"
