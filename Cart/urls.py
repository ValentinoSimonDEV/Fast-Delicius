from django.urls import path
from .views import add_to_cart, cart_detail, cart_substract , clear_cart , cart_add 

urlpatterns = [
    path('add/<int:product_id>/', add_to_cart.as_view() , name='add_to_cart'),
    path('remove/<int:product_id>/', cart_substract.as_view() , name='cart_substract'),
    path('add/<int:product_id>' , cart_add.as_view() , name='cart_add' ) ,
    path('clear/' , clear_cart , name='clear_cart') ,
    path('cart_detail/', cart_detail.as_view() , name='cart_detail'),


]