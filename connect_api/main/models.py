from django.db import models


class Order(models.Model):  # Заказ
    NEW = 'N'
    ACCEPTED = 'A'
    FAILED = 'F'
    STATUS_CHOICES = [
        (NEW, 'new'),
        (ACCEPTED, 'accepted'),
        (FAILED, 'failed'),
    ]
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=NEW)
    created_at = models.DateTimeField(auto_now_add=True)
    external_id = models.CharField(max_length=128)


class Product(models.Model):  # Продукт
    name = models.CharField(max_length=64)


class OrderDetail(models.Model):  # Детали заказа
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name="details")
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name="details")
    amount = models.IntegerField()  # мб добавить ограничение < 0
    price = models.DecimalField(max_digits=10, decimal_places=3)


