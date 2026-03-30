from django.contrib import admin
from .models import Category, Product, ProductImage, ProductVideo


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'is_primary', 'order']


class ProductVideoInline(admin.TabularInline):
    model = ProductVideo
    extra = 1
    fields = ['video', 'title', 'description', 'thumbnail', 'order']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'category', 'price', 'quantity', 'stock_status', 'is_active', 'is_featured']
    list_filter = ['category', 'is_active', 'is_featured', 'category_type', 'created_at']
    search_fields = ['name', 'sku', 'description']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ProductVideoInline]
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'sku', 'category', 'category_type')
        }),
        ('Pricing & Inventory', {
            'fields': ('price', 'quantity')
        }),
        ('Description', {
            'fields': ('description', 'specifications')
        }),
        ('Status', {
            'fields': ('is_active', 'is_featured')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def stock_status(self, obj):
        status_colors = {
            'in_stock': 'green',
            'low_stock': 'orange',
            'out_of_stock': 'red'
        }
        color = status_colors.get(obj.stock_status, 'gray')
        return f'<span style="color: {color}; font-weight: bold;">{obj.stock_status.replace("_", " ").title()}</span>'
    stock_status.allow_tags = True
    stock_status.short_description = 'Stock Status'


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'alt_text', 'is_primary', 'order']
    list_filter = ['is_primary']
    search_fields = ['product__name', 'alt_text']


@admin.register(ProductVideo)
class ProductVideoAdmin(admin.ModelAdmin):
    list_display = ['product', 'title', 'order']
    search_fields = ['product__name', 'title']
