from django.db import models
from Products.models import Products
from phone_field import PhoneField


class Order(models.Model):
    session_key = models.CharField(max_length=40, null=True, blank=True)
    first_name = models.CharField(max_length=50 , default='')
    last_name = models.CharField(max_length=50 , default='')
    email = models.EmailField(max_length=50 , default='')
    phone = PhoneField(blank=True, help_text='Contact phone number')
    postal_code = models.CharField(max_length=20 , default='')
    city = models.CharField(max_length=50 , default='')
    address = models.CharField(max_length=30 , default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=50 , choices=[('Cancelled' , 'Cancelled'), ('Pending' , 'Pending'), ('Completed' , 'Completed')] , default='Pending')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_id = models.CharField(max_length=100, unique=True, null=True, blank=True)  # Permitir nulo y vacío inicialmente
    type_payment = models.CharField(max_length=50 , default='')
    action = models.CharField(max_length=50 , default='')
    payment_state = models.BooleanField(default=False)


    def __str__(self):
        return f'{self.created_at} | {self.status}'
    

class OrderItem(models.Model):
    order = models.ForeignKey(Order , on_delete=models.CASCADE)
    product = models.ForeignKey(Products , on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.quantity} x {self.product.Tittle}'
