# Routing configuration for the NovaMarket platform encompassing inventory, transaction management, and administrative control
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.ProductListView.as_view(), name='home'),
    path('product/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    
    path('cart/', views.view_cart, name='view_cart'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('update_cart/<int:item_id>/<str:action>/', views.update_cart, name='update_cart'),
    path('remove_item/<int:item_id>/', views.remove_from_cart, name='remove_item'),
    
    path('checkout/', views.checkout, name='checkout'),
    path('my_orders/', views.my_orders, name='my_orders'),
    
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='store/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
    path('admin_panel/', views.admin_panel, name='admin_panel'),
    path('admin_panel/order_status/<int:order_id>/', views.update_order_status, name='update_order_status'),
    path('admin_panel/inventory/', views.manage_products, name='manage_products'),
    path('admin_panel/inventory/delete/<int:pk>/', views.delete_product, name='delete_product'),
    path('admin_panel/users/', views.manage_users, name='manage_users'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)