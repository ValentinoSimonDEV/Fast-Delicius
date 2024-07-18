from django.urls import path
from .views import add_to_cart, cart_detail, cart_substract , clear_cart , cart_add 

urlpatterns = [
    path('add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('remove/<int:product_id>/', cart_substract, name='cart_substract'),
    path('add/<int:product_id>' , cart_add , name='cart_add' ) ,
    path('clear/' , clear_cart , name='clear_cart') ,
    path('cart_detail/', cart_detail, name='cart_detail'),


]