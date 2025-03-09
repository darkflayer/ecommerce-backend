from django.contrib import admin
from .models import Product,Order

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'stock', 'created_at']
    search_fields = ['name']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'customer_name', 'order_status', 'created_at']
    list_filter = ['order_status']
    search_fields = ['customer_name', 'customer_email']
