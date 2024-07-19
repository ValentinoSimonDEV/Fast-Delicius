from django.shortcuts import redirect, render, get_object_or_404
from Products.models import Products
from django.views.generic import View , UpdateView
from .cart import Cart

class add_to_cart(View):
    def post(self , request , product_id):
        if request.method == 'POST':
            cart = Cart(request)
            product = get_object_or_404(Products , id=product_id)
            cart.add(product=product)
        return redirect('index')
class cart_add(View):
    def post(self , request , product_id):
        cart = Cart(request)
        product = get_object_or_404(Products , id=product_id)
        cart.add(product=product)
        return redirect('cart_detail')

class cart_substract(View):
    def post(self , request , product_id):
        if request.method == 'POST':
            cart = Cart(request)
            product = get_object_or_404(Products , id=product_id)
            cart.substract(product=product)
        return redirect('cart_detail')
class clear_cart:
    def post(self , request):
        cart = Cart(request)
        cart.clear()
        return redirect('cart_detail')

class cart_detail(View):
    def get(self , request):
        cart = Cart(request)
        context = {
            'cart' : cart
        }
        return render(request , 'detail.html' , context)

