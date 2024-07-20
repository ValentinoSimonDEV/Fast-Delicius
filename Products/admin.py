from django.contrib import admin
from .models import Products , TypeProduct
from unfold.admin import ModelAdmin


# Define la clase CustomAdminClass heredando de ModelAdmin
class CustomAdminClass(ModelAdmin):
    pass

# Registra el modelo TypeProduct con la clase CustomAdminClass
@admin.register(TypeProduct)
class TypeProductAdmin(CustomAdminClass):
    pass

# Registra el modelo Products con la clase CustomAdminClass
@admin.register(Products)
class ProductsAdmin(CustomAdminClass):
    pass