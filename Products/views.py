from django.shortcuts import render
from .models import Products
from Cart.cart import Cart
from django.views.generic import View , UpdateView


class index(View):
    def get(self , request):
        cart = Cart(request)
        session_key_exists = request.session.session_key is not None
        products = Products.objects.all()

        context = {
            'cart' : cart,
            'products' : products ,
            'session_key_exists' : session_key_exists
        }

        return render(request , 'index.html' , context)