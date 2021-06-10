from django.contrib import admin
from .models import Order, Product, OrderDetail

admin.site.register(Order)
admin.site.register(Product)
admin.site.register(OrderDetail)
