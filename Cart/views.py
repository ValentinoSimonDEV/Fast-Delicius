from django.shortcuts import redirect, render, get_object_or_404
from Products.models import Products
from .cart import Cart

def add_to_cart(request, product_id):
    if request.method == 'POST':
        cart = Cart(request)
        product = get_object_or_404(Products, id=product_id)
        cart.add(product=product)
    return redirect('index')


def cart_add(request , product_id):
    if request.method == 'POST':
        cart = Cart(request)
        product = get_object_or_404(Products , id=product_id)
        cart.add(product=product)
    return redirect('cart_detail')

def cart_substract(request, product_id):
    if request.method == 'POST':
        cart = Cart(request)
        product = get_object_or_404(Products, id=product_id)
        cart.substract(product)
    return redirect('cart_detail')


def clear_cart(request):
    cart = Cart(request)
    cart.clear()
    return redirect ('cart_detail')

def cart_detail(request):
    cart = Cart(request)
    return render(request, 'detail.html', {'cart': cart})


