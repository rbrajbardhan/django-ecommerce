from django.contrib import admin
from .models import Category, Product, Cart, CartItem, Order, OrderItem

admin.site.site_header = "NovaMarket | Admin Control"
admin.site.site_title = "NovaMarket Portal"
admin.site.index_title = "Inventory and Transaction Control"

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price') 

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock')
    list_filter = ('category', 'price')
    search_fields = ('name', 'description')
    list_editable = ('price', 'stock')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'created_at') 
    list_editable = ('status',)
    readonly_fields = ('created_at',)
    inlines = [OrderItemInline]

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)} 
    list_display = ('name', 'slug')


admin.site.register(Cart)
admin.site.register(CartItem)
