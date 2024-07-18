from django.contrib import admin
from django.urls import path, include
from .views import order_checkout, view_orders, delete_orders, update_order_status, my_orders, create_preference, payment_success, payment_failure, payment_pending , webhook

urlpatterns = [
    path('checkout/', order_checkout, name='order_checkout'),
    path('orders/', view_orders , name='view_orders'),
    path('order/', my_orders, name='my_orders'),
    path('update-order-status/<int:order_id>/', update_order_status, name='update_order_status'),
    path('delete_order/<int:order_id>/', delete_orders, name='delete_orders'),
    path('create_preference/<int:order_id>/', create_preference, name='create_preference'),
    path('success/', payment_success, name='payment_success'),
    path('failure/', payment_failure, name='payment_failure'),
    path('pending/', payment_pending, name='payment_pending'),
    path('webhook/', webhook, name='webhook'),
]