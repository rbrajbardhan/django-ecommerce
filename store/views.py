import json
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView
from .models import Product, Category, Cart, CartItem, Order, OrderItem 
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q, Sum
from django.db.models.functions import TruncDate
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import transaction

# Storefront: Product listing with search and category filtering
class ProductListView(ListView):
    model = Product
    template_name = 'store/home.html'
    context_object_name = 'products'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_categories'] = Category.objects.all()
        return context

    def get_queryset(self):
        query = self.request.GET.get('q')
        category_slug = self.request.GET.get('category')
        queryset = Product.objects.all()
        if query:
            queryset = queryset.filter(Q(name__icontains=query) | Q(description__icontains=query))
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        return queryset

class ProductDetailView(DetailView):
    model = Product
    template_name = 'store/product_detail.html'
    context_object_name = 'product'

class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = 'store/register.html'
    success_url = '/login/'

@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = CartItem.objects.filter(cart=cart)
    total = sum(item.total_price() for item in items)
    return render(request, 'store/cart.html', {'items': items, 'total': total})

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    messages.success(request, f"{product.name} added to your bag.")
    return redirect('view_cart')

@login_required
def update_cart(request, item_id, action):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    if action == 'add':
        cart_item.quantity += 1
    elif action == 'remove':
        cart_item.quantity -= 1
    
    if cart_item.quantity <= 0:
        cart_item.delete()
    else:
        cart_item.save()
    return redirect('view_cart')

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.info(request, "Item removed from your bag.")
    return redirect('view_cart')

@login_required
def checkout(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = CartItem.objects.filter(cart=cart)
    
    if not items.exists():
        messages.warning(request, "Your shopping bag is empty.")
        return redirect('home')
        
    total = sum(item.total_price() for item in items)

    if request.method == 'POST':
        address = request.POST.get('address')
        try:
            with transaction.atomic():
                # Process order and inventory in a single secure block
                order = Order.objects.create(user=request.user, total_amount=total, address=address)
                for item in items:
                    if item.product.stock < item.quantity:
                        raise ValueError(f"Insufficient stock for {item.product.name}.")
                    OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity, price=item.product.price)
                    item.product.stock -= item.quantity
                    item.product.save()
                items.delete() 
                return render(request, 'store/checkout_success.html', {'order': order})
        except Exception as e:
            messages.error(request, str(e))
            return redirect('view_cart')

    return render(request, 'store/checkout.html', {'items': items, 'total': total})

@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items__product').order_by('-created_at')
    return render(request, 'store/my_orders.html', {'orders': orders})

@user_passes_test(lambda u: u.is_staff, login_url='login')
def admin_panel(request):
    # Only calculate revenue from non-cancelled orders
    sales_trend = Order.objects.exclude(status='Cancelled').annotate(date=TruncDate('created_at')).values('date').annotate(total=Sum('total_amount')).order_by('date')
    
    context = {
        'total_orders': Order.objects.count(),
        # Exclude Cancelled orders from revenue card
        'total_revenue': Order.objects.exclude(status='Cancelled').aggregate(Sum('total_amount'))['total_amount__sum'] or 0,
        'total_users': User.objects.count(),
        'total_products': Product.objects.count(),
        'recent_orders': Order.objects.all().order_by('-created_at')[:8],
        'low_stock_products': Product.objects.filter(stock__lt=10),
        'chart_dates': json.dumps([str(d['date']) for d in sales_trend]),
        'chart_amounts': json.dumps([float(d['total']) for d in sales_trend]),
    }
    return render(request, 'store/admin_panel.html', context)

@user_passes_test(lambda u: u.is_staff, login_url='login')
def update_order_status(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        new_status = request.POST.get('status')
        
        # If order is being cancelled, restore the stock
        if new_status == 'Cancelled' and order.status != 'Cancelled':
            with transaction.atomic():
                for item in order.items.all():
                    item.product.stock += item.quantity
                    item.product.save()
        
        # If a previously cancelled order is restored, re-deduct stock
        elif new_status != 'Cancelled' and order.status == 'Cancelled':
            with transaction.atomic():
                for item in order.items.all():
                    if item.product.stock < item.quantity:
                        messages.error(request, f"Cannot restore order. Insufficient stock for {item.product.name}.")
                        return redirect('admin_panel')
                    item.product.stock -= item.quantity
                    item.product.save()

        order.status = new_status
        order.save()
        messages.success(request, f"Order status updated for #{order_id}.")
    return redirect('admin_panel')

@user_passes_test(lambda u: u.is_staff, login_url='login')
def manage_products(request):
    return render(request, 'store/manage_products.html', {'products': Product.objects.all().order_by('name')})

@user_passes_test(lambda u: u.is_staff, login_url='login')
def delete_product(request, pk):
    get_object_or_404(Product, pk=pk).delete()
    messages.success(request, "Product deleted.")
    return redirect('manage_products')

@user_passes_test(lambda u: u.is_staff, login_url='login')
def manage_users(request):
    return render(request, 'store/manage_users.html', {'users': User.objects.all().order_by('-date_joined')})

def contact_us(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        messages.success(request, f"Thank you {name}, your message has been sent to our Gurugram HQ!")
        return redirect('contact_us')
        
    return render(request, 'store/contact.html')