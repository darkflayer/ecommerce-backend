from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('<int:pk>/', views.product_detail, name='product_detail'),

    # Order URLs
    path('orders/', views.order_list, name='order_list'),
    path('orders/create/', views.create_order, name='create_order'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),
    path('orders/<int:pk>/update/', views.update_order, name='update_order'),
    path('orders/<int:pk>/delete/', views.delete_order, name='delete_order'),
    path('payment/<int:order_id>/', views.create_payment, name='create_payment'),
    path('payment/success/', views.payment_success, name='payment_success'),

]
