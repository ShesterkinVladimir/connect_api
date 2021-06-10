from django.db import models


class Order(models.Model):
    # id = models.AutoField(auto_created=True, primary_key=True, serialize=True)
    NEW = 'N'
    ACCEPTED = 'A'
    FAILED = 'F'
    STATUS_CHOICES = [
        (NEW, 'new'),
        (ACCEPTED, 'accepted'),
        (FAILED, 'failed'),
    ]
    status = models.CharField(max_length=12, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    external_id = models.CharField(max_length=128)


class Product(models.Model):
    # id = models.AutoField(auto_created=True, primary_key=True, serialize=True)
    name = models.CharField(max_length=64)


class OrderDetail(models.Model):
    # id = models.AutoField(auto_created=True, primary_key=True, serialize=True)
    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    amount = models.IntegerField()  # мб добавить ограничение
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=3)


