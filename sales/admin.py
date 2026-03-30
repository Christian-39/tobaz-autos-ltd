from django.contrib import admin
from .models import Sale, SaleItem


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 1
    readonly_fields = ['total_price']
    autocomplete_fields = ['product']


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer', 'status', 'payment_method', 'total_amount', 'item_count', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['order_number', 'customer_name', 'customer_email', 'customer_phone']
    readonly_fields = ['order_number', 'subtotal', 'total_amount', 'created_at', 'updated_at', 'completed_at']
    inlines = [SaleItemInline]
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'status', 'payment_method')
        }),
        ('Customer Information', {
            'fields': ('customer', 'customer_name', 'customer_email', 'customer_phone')
        }),
        ('Financial Details', {
            'fields': ('subtotal', 'tax_amount', 'discount_amount', 'total_amount')
        }),
        ('Additional Information', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        form.instance.calculate_totals()


@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    list_display = ['sale', 'product', 'quantity', 'unit_price', 'total_price', 'created_at']
    list_filter = ['created_at']
    search_fields = ['sale__order_number', 'product__name']
    autocomplete_fields = ['sale', 'product']
