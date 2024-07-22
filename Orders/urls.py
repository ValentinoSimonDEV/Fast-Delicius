from django.contrib import admin
from django.urls import path, include
from .views import order_checkout, view_orders, delete_orders, update_order_status, my_order, create_preference, payment_success, payment_failure, payment_pending , webhook

urlpatterns = [
    path('checkout/', order_checkout.as_view(), name='order_checkout'),
    path('orders/', view_orders.as_view() , name='view_orders'),
    path('order/', my_order.as_view(), name='my_orders'),
    path('update-order-status/<int:order_id>/', update_order_status.as_view() , name='update_order_status'),
    path('delete_order/<int:order_id>/', delete_orders.as_view() , name='delete_orders'),
    path('create_preference/<int:order_id>/', create_preference.as_view() , name='create_preference'),
    path('delete_unpaid_orders/' , payment_success.as_view() , name='payment_success'),
    path('success/', payment_success.as_view() , name='payment_success'),
    path('failure/', payment_failure.as_view(), name='payment_failure'),
    path('pending/', payment_pending.as_view(), name='payment_pending'),
    path('webhook/', webhook.as_view() , name='webhook'),
]