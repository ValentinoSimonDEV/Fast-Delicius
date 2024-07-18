from django.shortcuts import render
from .models import Products
from Cart.cart import Cart

def index(request):
    cart = Cart(request)
    session_key_exists = request.session.session_key is not None
    products = Products.objects.all()

    return render(request , 'index.html', {'products': products , 'cart' : cart , 'session_key_exists' : session_key_exists })